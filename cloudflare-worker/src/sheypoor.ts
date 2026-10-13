import citiesMap from './data/cities.json';

export const SHEYPOOR_BASE_URL = 'https://www.sheypoor.com/api/v7.0.7';

export const SHEYPOOR_HEADERS = {
  'User-Agent': 'Sheypoor/7.0.7 (Android; Mobile; fa)',
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'X-AGENT-TYPE': 'Android App',
  'X-BUILD-MODE': 'Release',
  'X-FLAVOR': 'direct',
};

export function normalizePersian(text: string): string {
  if (!text) return '';
  return text
    .trim()
    .replace(/\u064a/g, '\u06cc')
    .replace(/\u0649/g, '\u06cc')
    .replace(/\u0643/g, '\u06a9')
    .replace(/\u200c/g, ' ')
    .replace(/\s+/g, ' ')
    .toLowerCase();
}

export function resolveCity(nameOrSlug: string): { id: number; name: string; slug: string; province: string } | null {
  if (!nameOrSlug) return null;
  const raw = nameOrSlug.trim().toLowerCase();
  const norm = normalizePersian(nameOrSlug);
  const map = citiesMap as Record<string, any>;

  if (map[raw]) return map[raw];
  if (map[norm]) return map[norm];

  const aliases: Record<string, string> = {
    'تهران': 'tehran',
    'مشهد': 'mashhad',
    'اصفهان': 'isfahan',
    'شیراز': 'shiraz',
    'تبریز': 'tabriz',
    'کرج': 'karaj',
    'قم': 'qom',
    'اهواز': 'ahvaz',
    'شاهرود': 'shahroud',
    'سبزوار': 'sabzevar',
    'سمنان': 'semnan',
  };

  if (aliases[norm] && map[aliases[norm]]) return map[aliases[norm]];
  if (aliases[raw] && map[aliases[raw]]) return map[aliases[raw]];

  for (const [k, v] of Object.entries(map)) {
    if (k.includes(norm) || norm.includes(k)) {
      return v;
    }
  }

  return null;
}

export function parsePrice(priceStr?: string): number | null {
  if (!priceStr) return null;
  if (/توافقی|رایگان|مجانی/.test(priceStr)) return null;
  const persianDigits: Record<string, string> = {
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
  };
  const converted = priceStr.replace(/[۰-۹٠-٩]/g, d => persianDigits[d] || d);
  const digits = converted.replace(/[^\d]/g, '');
  return digits ? parseInt(digits, 10) : null;
}

export function normalizeListing(item: any): any {
  const listingId = item.listingID || item.id;
  const loc = item.location || {};
  const cat = item.category || {};

  const images: string[] = [];
  if (Array.isArray(item.images)) {
    for (const img of item.images) {
      if (typeof img === 'string') images.push(img);
      else if (img && (img.imageURL || img.originalURL || img.thumbnailURL)) {
        images.push(img.imageURL || img.originalURL || img.thumbnailURL);
      }
    }
  } else if (item.thumbImageURL) {
    images.push(item.thumbImageURL);
  }

  const attributes: Record<string, string> = {};
  if (Array.isArray(item.attributes)) {
    for (const attr of item.attributes) {
      const k = attr.attributeTitle || attr.title;
      const v = attr.attributeValue || attr.value;
      if (k && v) attributes[k] = v;
    }
  }

  return {
    id: String(listingId),
    title: item.title || '',
    price: parsePrice(item.priceString),
    price_string: item.priceString || '',
    city: loc.city || '',
    city_id: loc.cityId || loc.cityID,
    province: loc.region || loc.province || '',
    neighbourhood: loc.neighbourhood || '',
    category: cat.c3 || cat.c2 || cat.c1 || cat.categoryTitle || '',
    category_id: cat.categoryID || cat.id,
    time: item.sortInfo || item.date || '',
    description: item.description || '',
    images,
    attributes,
    url: listingId ? `https://www.sheypoor.com/v/${listingId}.html` : '',
  };
}

export async function searchSheypoor(options: {
  query?: string;
  cities?: string;
  page?: number;
  min_price?: number;
  max_price?: number;
}) {
  const url = new URL(`${SHEYPOOR_BASE_URL}/listings`);
  if (options.query) url.searchParams.set('q', options.query.trim());
  if (options.page && options.page > 1) url.searchParams.set('p', String(options.page));

  if (options.cities) {
    const list = options.cities.split(',').map(s => s.trim()).filter(Boolean);
    for (const c of list) {
      const resolved = resolveCity(c);
      if (resolved && resolved.id) {
        url.searchParams.append('cities[]', String(resolved.id));
      }
    }
  }

  if (options.min_price) url.searchParams.set('pr[from]', String(options.min_price));
  if (options.max_price) url.searchParams.set('pr[to]', String(options.max_price));

  const resp = await fetch(url.toString(), { headers: SHEYPOOR_HEADERS });
  if (!resp.ok) {
    throw new Error(`Sheypoor API HTTP ${resp.status}`);
  }

  const data: any = await resp.json();
  const rawListings: any[] = [];
  for (const block of data.data || []) {
    if (block.type === 'serp') {
      const sub = block.data;
      if (sub && Array.isArray(sub.listings)) {
        rawListings.push(...sub.listings);
      } else if (Array.isArray(sub)) {
        rawListings.push(...sub);
      }
    }
  }

  const normalized = rawListings.map(normalizeListing);
  return {
    success: true,
    totalCount: data.totalCount || normalized.length,
    count: normalized.length,
    page: options.page || 1,
    listings: normalized,
  };
}

export async function getSheypoorListing(id: string | number) {
  const resp = await fetch(`${SHEYPOOR_BASE_URL}/listings/${id}`, { headers: SHEYPOOR_HEADERS });
  if (!resp.ok) {
    throw new Error(`Listing not found (${resp.status})`);
  }
  const data = await resp.json();
  return { success: true, listing: normalizeListing(data) };
}

export async function getSheypoorContact(id: string | number, contactType = 'call') {
  const resp = await fetch(`${SHEYPOOR_BASE_URL}/listings/${id}/contact/${contactType}?referrer=listing`, {
    headers: SHEYPOOR_HEADERS,
  });
  const data: any = await resp.json();
  if (resp.ok && data.contactInfo) {
    return { success: true, phone: data.contactInfo, listing_id: String(id) };
  }
  return { success: false, error: data?.error?.errorMessage || `HTTP ${resp.status}` };
}

export async function getSimilarListings(id: string | number) {
  const resp = await fetch(`${SHEYPOOR_BASE_URL}/listings/${id}/relateds`, { headers: SHEYPOOR_HEADERS });
  if (!resp.ok) {
    throw new Error(`Similar listings error (${resp.status})`);
  }
  const data: any = await resp.json();
  const items = Array.isArray(data) ? data : data.listings || [];
  return { success: true, listings: items.map(normalizeListing) };
}
