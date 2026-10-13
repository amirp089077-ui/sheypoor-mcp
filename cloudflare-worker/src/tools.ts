import {
  searchSheypoor,
  getSheypoorListing,
  getSheypoorContact,
  getSimilarListings,
  resolveCity,
} from './sheypoor';

export const WORKER_TOOLS = [
  {
    name: 'sheypoor_search',
    description: 'جستجوی آگهی‌های شیپور با پشتیبانی از چند شهر همزمان و فیلتر قیمت',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'عبارت جستجو' },
        cities: { type: 'string', description: 'نام شهرها (مثلا شیراز یا شیراز,شاهرود)' },
        page: { type: 'integer', description: 'شماره صفحه', default: 1 },
        min_price: { type: 'integer', description: 'حداقل قیمت به تومان' },
        max_price: { type: 'integer', description: 'حداکثر قیمت به تومان' },
      },
    },
  },
  {
    name: 'sheypoor_get_listing',
    description: 'دریافت جزییات کامل یک آگهی شیپور',
    inputSchema: {
      type: 'object',
      properties: {
        listing_id: { type: 'string', description: 'شناسه آگهی' },
      },
      required: ['listing_id'],
    },
  },
  {
    name: 'sheypoor_get_contact',
    description: 'دریافت مستقیم شماره تماس فروشنده در شیپور',
    inputSchema: {
      type: 'object',
      properties: {
        listing_id: { type: 'string', description: 'شناسه آگهی' },
        contact_type: { type: 'string', description: 'call یا sms', default: 'call' },
      },
      required: ['listing_id'],
    },
  },
  {
    name: 'sheypoor_similar_listings',
    description: 'آگهی‌های مشابه برای یک آگهی مشخص در شیپور',
    inputSchema: {
      type: 'object',
      properties: {
        listing_id: { type: 'string', description: 'شناسه آگهی' },
      },
      required: ['listing_id'],
    },
  },
  {
    name: 'sheypoor_price_analysis',
    description: 'تحلیل آماری قیمت بازار در شیپور (میانگین، میانه، کمترین و بیشترین)',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'عبارت جستجو' },
        cities: { type: 'string', description: 'شهرها' },
      },
      required: ['query'],
    },
  },
  {
    name: 'sheypoor_find_deals',
    description: 'یافتن آگهی‌های زیر قیمت بازار در شیپور (معاملات عالی)',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'عبارت جستجو' },
        cities: { type: 'string', description: 'شهرها' },
        discount_percentage: { type: 'number', description: 'حداقل درصد تخفیف', default: 15 },
      },
      required: ['query'],
    },
  },
  {
    name: 'sheypoor_status',
    description: 'وضعیت سلامت سرور ابری Sheypoor MCP',
    inputSchema: { type: 'object', properties: {} },
  },
];

export async function executeWorkerTool(name: string, args: Record<string, any>) {
  if (name === 'sheypoor_search') {
    return await searchSheypoor({
      query: args.query,
      cities: args.cities,
      page: args.page,
      min_price: args.min_price,
      max_price: args.max_price,
    });
  } else if (name === 'sheypoor_get_listing') {
    return await getSheypoorListing(args.listing_id);
  } else if (name === 'sheypoor_get_contact') {
    return await getSheypoorContact(args.listing_id, args.contact_type || 'call');
  } else if (name === 'sheypoor_similar_listings') {
    return await getSimilarListings(args.listing_id);
  } else if (name === 'sheypoor_price_analysis') {
    const res = await searchSheypoor({ query: args.query, cities: args.cities });
    const prices = res.listings
      .map((l: any) => l.price)
      .filter((p: any) => typeof p === 'number' && p > 0)
      .sort((a: number, b: number) => a - b);

    if (!prices.length) {
      return { query: args.query, total_listings: res.listings.length, analysis: null };
    }
    const sum = prices.reduce((a: number, b: number) => a + b, 0);
    const avg = Math.round(sum / prices.length);
    const med = prices[Math.floor(prices.length / 2)];
    return {
      query: args.query,
      total_listings: res.listings.length,
      priced_listings: prices.length,
      analysis: {
        min_price: prices[0],
        max_price: prices[prices.length - 1],
        avg_price: avg,
        median_price: med,
      },
    };
  } else if (name === 'sheypoor_find_deals') {
    const res = await searchSheypoor({ query: args.query, cities: args.cities });
    const prices = res.listings
      .map((l: any) => l.price)
      .filter((p: any) => typeof p === 'number' && p > 0)
      .sort((a: number, b: number) => a - b);

    if (!prices.length) return { deals_count: 0, deals: [] };
    const med = prices[Math.floor(prices.length / 2)];
    const thresh = (Number(args.discount_percentage) || 15) / 100;
    const deals = res.listings.filter((l: any) => l.price && l.price <= med * (1 - thresh));
    return {
      query: args.query,
      market_median: med,
      deals_count: deals.length,
      deals,
    };
  } else if (name === 'sheypoor_status') {
    return {
      server: 'Sheypoor Cloudflare Remote MCP',
      version: '1.0.0',
      sheypoor_api: 'v7.0.7',
      edge: 'Cloudflare Workers (V8 Isolate)',
      healthy: true,
    };
  }

  throw new Error(`Unknown tool: ${name}`);
}
