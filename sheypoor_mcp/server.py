"""
Model Context Protocol (MCP) standard JSON-RPC 2.0 server over stdin/stdout.
"""

import sys
import json
import traceback
from typing import Dict, Any
from .tools import TOOLS, execute_tool

SERVER_NAME = "sheypoor-mcp"
SERVER_VERSION = "1.0.0"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")



def send_response(response: Dict[str, Any]):
    line = json.dumps(response, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def handle_request(req: Dict[str, Any]):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        send_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                }
            }
        })

    elif method == "notifications/initialized":
        # Client notification, no response required
        pass

    elif method == "tools/list":
        send_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        })

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            res = execute_tool(tool_name, arguments)
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(res, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            })
        except Exception as e:
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "isError": True,
                "error": {
                    "code": -32603,
                    "message": str(e),
                    "data": traceback.format_exc()
                }
            })

    elif method == "ping":
        send_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        })

    else:
        if req_id is not None:
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })


def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            handle_request(req)
        except Exception as e:
            sys.stderr.write(f"Error handling line: {e}\n")
            sys.stderr.flush()



if __name__ == "__main__":
    main()
