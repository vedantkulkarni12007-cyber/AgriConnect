// =============================================================
// KrishiLink API Service
// Connects to FastAPI v1 / Flask backend with seamless DEMO fallback
// =============================================================

import {
  DEMO_PRICES,
  DEMO_PRICE_HISTORY,
  DEMO_BUYERS,
  DEMO_LOTS,
  DEMO_OFFERS,
  DEMO_TRANSACTIONS,
  DEMO_STORAGE,
  DEMO_GRIEVANCES,
  DEMO_NOTIFICATIONS,
  DEMO_MARKERS,
} from '../data/demoData';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms));

// Helper for safe fetch with timeout
async function apiCall(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);
    
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      signal: controller.signal,
      ...options,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    const json = await response.json();
    return json;
  } catch (error) {
    console.warn(`[KrishiLink API] ${endpoint} unavailable (${error.message}). Falling back to local data.`);
    return null;
  }
}

// 1. Market Prices
export async function getPrices(crop = null, market = null) {
  if (!DEMO_MODE) {
    const params = new URLSearchParams();
    if (crop && crop !== 'All') params.append('crop', crop);
    if (market && market !== 'All') params.append('market', market);
    
    // Try v1 first, then legacy /api/prices
    const res = (await apiCall(`/api/v1/prices?${params}`)) || (await apiCall(`/api/prices?${params}`));
    if (res && res.success && res.data) {
      return res;
    }
  }

  await delay(150);
  let prices = [...DEMO_PRICES];
  if (crop && crop !== 'All') prices = prices.filter(p => p.crop === crop);
  if (market && market !== 'All') prices = prices.filter(p => p.market === market);
  return { success: true, data: prices };
}

// 2. Price History
export async function getPriceHistory(crop, market = null, days = 15) {
  if (!DEMO_MODE) {
    const res = (await apiCall(`/api/v1/prices/${crop}/history?market=${market || ''}&days=${days}`)) ||
                (await apiCall(`/api/prices/${crop}/history?market=${market || ''}&days=${days}`));
    if (res && res.success && res.data) {
      return res;
    }
  }

  await delay(150);
  const marketKey = market || Object.keys(DEMO_PRICE_HISTORY[crop] || {})[0] || 'Lasalgaon';
  const history = DEMO_PRICE_HISTORY[crop]?.[marketKey] ||
                  DEMO_PRICE_HISTORY[crop]?.[Object.keys(DEMO_PRICE_HISTORY[crop] || {})[0]] ||
                  DEMO_PRICE_HISTORY['Onion']['Lasalgaon'] || [];
  return { success: true, data: history.slice(-days) };
}

// 3. Trend Analysis
export async function getTrend(crop, market = null) {
  if (!DEMO_MODE) {
    const res = (await apiCall(`/api/v1/prices/trends/${crop}${market ? `?market=${market}` : ''}`)) ||
                (await apiCall(`/api/trends/${crop}${market ? `?market=${market}` : ''}`));
    if (res && res.success && res.data) {
      return res;
    }
  }

  await delay(150);
  const priceData = DEMO_PRICES.find(p => p.crop === crop && (!market || p.market === market)) || DEMO_PRICES.find(p => p.crop === crop);
  if (!priceData) return { success: false, message: 'Crop not found' };
  
  const movingAvg = Math.round(priceData.modal_price / (1 + (priceData.change_pct || 0) / 100));
  return {
    success: true,
    data: {
      crop,
      market: priceData.market,
      current_price: priceData.modal_price,
      moving_average: movingAvg,
      percentage_change: priceData.change_pct || 0,
      trend: priceData.trend || 'STABLE',
      explanation: priceData.trend === 'RISING'
        ? `${crop} prices are currently ${priceData.change_pct}% above the 7-day average in ${priceData.market}.`
        : priceData.trend === 'FALLING'
        ? `${crop} prices have dropped ${Math.abs(priceData.change_pct)}% below the 7-day average.`
        : `${crop} prices are stable within 3% of the 7-day average.`,
      note: 'This trend signal is calculated from price arithmetic — not AI prediction.',
    }
  };
}

// 4. Produce Listings (Lots)
export async function getLots(farmerId = null) {
  if (!DEMO_MODE) {
    const params = farmerId ? `?farmer_id=${farmerId}` : '';
    const res = (await apiCall(`/api/v1/lots${params}`)) || (await apiCall(`/api/lots${params}`));
    if (res && res.success && res.data) return res;
  }

  await delay(150);
  return { success: true, data: DEMO_LOTS };
}

export async function createLot(lotData) {
  if (!DEMO_MODE) {
    const res = (await apiCall('/api/v1/lots', { method: 'POST', body: JSON.stringify(lotData) })) ||
                (await apiCall('/api/lots', { method: 'POST', body: JSON.stringify(lotData) }));
    if (res && res.success) return res;
  }

  await delay(300);
  const newLot = {
    id: `lot-${Date.now()}`,
    ...lotData,
    farmer: 'Ramesh Patil',
    status: 'active',
    created_at: new Date().toISOString()
  };
  return { success: true, data: newLot, message: 'Listing created successfully' };
}

// 5. Buyer Matches
export async function getMatches(lotData) {
  if (!DEMO_MODE) {
    const res = (await apiCall('/api/v1/matches/refresh', { method: 'POST', body: JSON.stringify({ lot_id: lotData?.id || lotData?.lot_id }) })) ||
                (await apiCall('/api/match', { method: 'POST', body: JSON.stringify(lotData) }));
    if (res && res.success && res.data) return res;
  }

  await delay(300);
  const buyers = DEMO_BUYERS.filter(b => b.crops.includes(lotData?.crop || 'Onion'));
  const pool = buyers.length > 0 ? buyers : DEMO_BUYERS;
  const scored = pool.map(buyer => {
    let score = 0;
    const reasons = [];
    if (buyer.crops.includes(lotData?.crop || 'Onion')) { score += 40; reasons.push('✓ Crop matches buyer preference'); }
    if (lotData?.grade === 'A') { score += 25; reasons.push('✓ Grade A preferred by buyer'); } else { score += 15; reasons.push('✓ Standard grade accepted'); }
    const qty = parseInt(lotData?.quantity) || 100;
    if (qty >= buyer.min_qty && qty <= buyer.max_qty) { score += 20; reasons.push('✓ Quantity within buyer range'); } else { score += 10; reasons.push('~ Partial volume fit'); }
    if (buyer.distance_km <= 20) { score += 15; reasons.push('✓ Buyer is nearby (< 20 km)'); } else { score += 8; reasons.push('~ Buyer within 100 km'); }
    const label = score >= 80 ? 'Excellent' : score >= 55 ? 'Good' : 'Fair';
    return { ...buyer, score, reasons, label };
  });
  return { success: true, data: scored.sort((a, b) => b.score - a.score) };
}

// 6. Offers
export async function getOffers(params = {}) {
  if (!DEMO_MODE) {
    const query = new URLSearchParams(params).toString();
    const res = (await apiCall(`/api/v1/offers${query ? `?${query}` : ''}`)) ||
                (await apiCall(`/api/offers${query ? `?${query}` : ''}`));
    if (res && res.success && res.data) return res;
  }

  await delay(150);
  return { success: true, data: DEMO_OFFERS };
}

export async function createOffer(offerData) {
  if (!DEMO_MODE) {
    const res = (await apiCall('/api/v1/offers', { method: 'POST', body: JSON.stringify(offerData) })) ||
                (await apiCall('/api/offers', { method: 'POST', body: JSON.stringify(offerData) }));
    if (res && res.success) return res;
  }

  await delay(200);
  const newOffer = { id: `demo-offer-${Date.now()}`, ...offerData, status: 'pending', created_at: new Date().toISOString() };
  return { success: true, data: newOffer, message: 'Offer submitted successfully' };
}

export async function updateOffer(offerId, status) {
  if (!DEMO_MODE) {
    const res = (await apiCall(`/api/v1/offers/${offerId}/${status}`, { method: 'POST' })) ||
                (await apiCall(`/api/offers/${offerId}`, { method: 'PUT', body: JSON.stringify({ status }) }));
    if (res && res.success) return res;
  }

  await delay(200);
  return { success: true, data: { id: offerId, status }, message: `Offer ${status}` };
}

// 7. Transactions
export async function getTransactions(params = {}) {
  if (!DEMO_MODE) {
    const query = new URLSearchParams(params).toString();
    const res = (await apiCall(`/api/v1/transactions${query ? `?${query}` : ''}`)) ||
                (await apiCall(`/api/transactions${query ? `?${query}` : ''}`));
    if (res && res.success && res.data) return res;
  }

  await delay(150);
  return { success: true, data: DEMO_TRANSACTIONS };
}

export async function getTransaction(id) {
  if (!DEMO_MODE) {
    const res = (await apiCall(`/api/v1/transactions/${id}`)) || (await apiCall(`/api/transactions/${id}`));
    if (res && res.success && res.data) return res;
  }

  await delay(150);
  const txn = DEMO_TRANSACTIONS.find(t => t.id === id);
  return txn ? { success: true, data: txn } : { success: false, message: 'Transaction not found' };
}

// 8. Map Data
export async function getMapMarkers(type = 'all') {
  if (!DEMO_MODE) {
    const res = (await apiCall(`/api/v1/markets`)) || (await apiCall(`/api/map/markers?type=${type}`));
    if (res && res.success && res.data?.length) return res;
  }

  await delay(150);
  const markers = type === 'all' ? DEMO_MARKERS : DEMO_MARKERS.filter(m => m.type === type);
  return { success: true, data: markers };
}

// 9. Storage
export async function getStorageFacilities() {
  if (!DEMO_MODE) {
    const res = (await apiCall('/api/v1/storage/facilities')) || (await apiCall('/api/storage'));
    if (res && res.success && res.data) return res;
  }

  await delay(150);
  return { success: true, data: DEMO_STORAGE };
}

// 10. Grievances
export async function getGrievances(farmerId = null) {
  if (!DEMO_MODE) {
    const res = (await apiCall(`/api/v1/disputes${farmerId ? `?farmer_id=${farmerId}` : ''}`)) ||
                (await apiCall(`/api/grievances${farmerId ? `?farmer_id=${farmerId}` : ''}`));
    if (res && res.success && res.data) return res;
  }

  await delay(150);
  return { success: true, data: DEMO_GRIEVANCES };
}

export async function createGrievance(data) {
  if (!DEMO_MODE) {
    const res = (await apiCall('/api/v1/disputes', { method: 'POST', body: JSON.stringify(data) })) ||
                (await apiCall('/api/grievances', { method: 'POST', body: JSON.stringify(data) }));
    if (res && res.success) return res;
  }

  await delay(300);
  return {
    success: true,
    data: { id: `g-${Date.now()}`, ...data, status: 'open', created_at: new Date().toISOString() },
    message: 'Grievance submitted successfully. Our team will review it.'
  };
}

// 11. Health
export async function checkHealth() {
  const res = (await apiCall('/api/v1/health')) || (await apiCall('/api/health'));
  if (res && res.success) return res;
  return { success: true, mode: 'demo', status: 'ready' };
}
