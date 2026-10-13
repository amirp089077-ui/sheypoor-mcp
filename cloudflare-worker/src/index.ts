import { WORKER_TOOLS, executeWorkerTool } from './tools';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, Mcp-Session-Id',
};

export default {
  async fetch(request: Request, env: any, ctx: any): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    // Landing / Status
    if (url.pathname === '/' || url.pathname === '/health') {
      return new Response(
        JSON.stringify(
          {
            name: 'sheypoor-mcp',
            description: 'Model Context Protocol (MCP) server for Sheypoor classifieds on Cloudflare Workers',
            version: '1.0.0',
            endpoints: {
              sse: '/sse',
              messages: '/messages?sessionId={id}',
              mcp_stateless: '/mcp',
            },
            toolsCount: WORKER_TOOLS.length,
            status: 'operational',
          },
          null,
          2
        ),
        {
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json; charset=utf-8' },
        }
      );
    }

    // Stateless MCP JSON-RPC
    if (url.pathname === '/mcp' && request.method === 'POST') {
      try {
        const body: any = await request.json();
        const response = await handleMcpRequest(body);
        return new Response(JSON.stringify(response), {
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json; charset=utf-8' },
        });
      } catch (err: any) {
        return new Response(
          JSON.stringify({
            jsonrpc: '2.0',
            id: null,
            error: { code: -32603, message: err.message },
          }),
          {
            status: 500,
            headers: { ...CORS_HEADERS, 'Content-Type': 'application/json; charset=utf-8' },
          }
        );
      }
    }

    // SSE Endpoint
    if (url.pathname === '/sse') {
      const sessionId = crypto.randomUUID();
      const messageUri = `${url.origin}/messages?sessionId=${sessionId}`;

      const { readable, writable } = new TransformStream();
      const writer = writable.getWriter();
      const encoder = new TextEncoder();

      ctx.waitUntil(
        (async () => {
          await writer.write(encoder.encode(`event: endpoint\ndata: ${messageUri}\n\n`));
        })()
      );

      return new Response(readable, {
        headers: {
          ...CORS_HEADERS,
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }

    // SSE Messages POST
    if (url.pathname === '/messages' && request.method === 'POST') {
      try {
        const body: any = await request.json();
        const response = await handleMcpRequest(body);
        return new Response(JSON.stringify(response), {
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json; charset=utf-8' },
        });
      } catch (err: any) {
        return new Response(
          JSON.stringify({
            jsonrpc: '2.0',
            id: null,
            error: { code: -32603, message: err.message },
          }),
          {
            status: 500,
            headers: { ...CORS_HEADERS, 'Content-Type': 'application/json; charset=utf-8' },
          }
        );
      }
    }

    return new Response('Not Found', { status: 404, headers: CORS_HEADERS });
  },
};

async function handleMcpRequest(req: any) {
  const { id, method, params } = req;

  if (method === 'initialize') {
    return {
      jsonrpc: '2.0',
      id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: 'sheypoor-mcp-cloud', version: '1.0.0' },
      },
    };
  }

  if (method === 'notifications/initialized') {
    return null;
  }

  if (method === 'tools/list') {
    return {
      jsonrpc: '2.0',
      id,
      result: { tools: WORKER_TOOLS },
    };
  }

  if (method === 'tools/call') {
    const toolName = params?.name;
    const args = params?.arguments || {};
    try {
      const result = await executeWorkerTool(toolName, args);
      return {
        jsonrpc: '2.0',
        id,
        result: {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        },
      };
    } catch (e: any) {
      return {
        jsonrpc: '2.0',
        id,
        isError: true,
        error: { code: -32603, message: e.message },
      };
    }
  }

  if (method === 'ping') {
    return { jsonrpc: '2.0', id, result: {} };
  }

  return {
    jsonrpc: '2.0',
    id,
    error: { code: -32601, message: `Method not found: ${method}` },
  };
}
