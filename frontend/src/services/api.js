// KrishiLink API Service — FastAPI v1 + DEMO fallback
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
} from '../data/demoData';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
const API_V1 = import.meta.env.VITE_API_V1_BASE_URL || 'http://localhost:8001/api/v1';
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE !== 'false';
const delay = (ms = 400) => new Promise(resolve => setTimeout(resolve, ms));

async function apiCall(endpoint, options = {}) {
  const base = endpoint.startsWith('/api/v1') ? API_BASE : API_BASE;
  // Use V1 base for /api/v1 endpoints, else base
  const url = endpoint.startsWith('/api/v1') ? `${API_BASE}${endpoint}` : `${API_BASE}${endpoint}`;
  // If endpoint starts with /api/v1, use API_BASE (8001) + endpoint, else same
  // For V1 we could also use API_V1 directly: `${API_V1}${endpoint.replace('/api/v1','')}`
  const v1url = endpoint.startsWith('/api/v1') ? `${API_V1}${endpoint.replace('/api/v1','')}` : `${API_BASE}${endpoint}`;
  const target = endpoint.startsWith('/api/v1') ? v1url : `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(target, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.warn(`API call failed for ${endpoint}:`, error.message);
    throw error;
  }
}

export async function getPrices(crop = null, market = null) {
  if (DEMO_MODE) {
    await delay();
    let prices = [...DEMO_PRICES];
    if (crop) prices = prices.filter(p => p.crop === crop);
    if (market) prices = prices.filter(p => p.market === market);
    return { success: true, data: prices };
  }
  const params = new URLSearchParams();
  if (crop) params.append('crop', crop);
  if (market) params.append('market', market);
  return await apiCall(`/api/v1/prices?${params}`);
}

export async function getPriceHistory(crop, market = null, days = 15) {
  if (DEMO_MODE) {
    await delay();
    const marketKey = market || Object.keys(DEMO_PRICE_HISTORY[crop] || {})[0];
    const history = DEMO_PRICE_HISTORY[crop]?.[marketKey] || [];
    return { success: true, data: history.slice(-days) };
  }
  return await apiCall(`/api/v1/prices/${crop}/history?market=${market || ''}&days=${days}`);
}

export async function getTrend(crop, market = null) {
  if (DEMO_MODE) {
    await delay(300);
    const priceData = DEMO_PRICES.find(p => p.crop === crop && (!market || p.market === market)) || DEMO_PRICES.find(p => p.crop === crop);
    if (!priceData) return { success: false, message: 'Crop not found' };
    const movingAvg = Math.round(priceData.modal_price / (1 + priceData.change_pct / 100));
    return {
      success: true,
      data: {
        crop,
        market: priceData.market,
        current_price: priceData.modal_price,
        moving_average: movingAvg,
        percentage_change: priceData.change_pct,
        trend: priceData.trend,
        explanation: priceData.trend === 'RISING' ? `${crop} prices are currently ${priceData.change_pct}% above the 7-day average in ${priceData.market}.` : priceData.trend === 'FALLING' ? `${crop} prices have dropped ${Math.abs(priceData.change_pct)}% below the 7-day average.` : `${crop} prices are stable within 3% of the 7-day average.`,
        note: 'This trend signal is calculated from price arithmetic — not AI prediction.',
      }
    };
  }
  return await apiCall(`/api/v1/trends/${crop}${market ? `?market=${market}` : ''}`);
}

export async function getLots(farmerId = null) {
  if (DEMO_MODE) {
    await delay();
    return { success: true, data: DEMO_LOTS };
  }
  const params = farmerId ? `?farmer_id=${farmerId}` : '';
  return await apiCall(`/api/v1/lots${params}`);
}

export async function createLot(lotData) {
  if (DEMO_MODE) {
    await delay(600);
    const newLot = { id: `demo-lot-${Date.now()}`, ...lotData, farmer: 'Ramesh Patil', status: 'active', created_at: new Date().toISOString() };
    return { success: true, data: newLot, message: 'Lot created successfully' };
  }
  return await apiCall('/api/v1/lots', { method: 'POST', body: JSON.stringify(lotData) });
}

export async function getMatches(lotData) {
  if (DEMO_MODE) {
    await delay(800);
    const buyers = DEMO_BUYERS.filter(b => b.crops.includes(lotData.crop || 'Onion'));
    const scored = buyers.map(buyer => {
      let score = 0;
      const reasons = [];
      if (buyer.crops.includes(lotData.crop)) { score += 40; reasons.push('✓ Crop matches buyer preference'); }
      if (lotData.grade === 'A') { score += 25; reasons.push('✓ Grade A preferred by buyer'); } else if (lotData.grade === 'B') { score += 15; reasons.push('✓ Grade B accepted'); }
      const qty = parseInt(lotData.quantity) || 100;
      if (qty >= buyer.min_qty && qty <= buyer.max_qty) { score += 20; reasons.push('✓ Quantity within buyer range'); } else if (qty >= buyer.min_qty * 0.5) { score += 10; reasons.push('~ Quantity partially compatible'); }
      if (buyer.distance_km <= 20) { score += 15; reasons.push('✓ Buyer is nearby (< 20 km)'); } else if (buyer.distance_km <= 100) { score += 8; reasons.push('~ Buyer within 100 km'); }
      const label = score >= 80 ? 'Excellent' : score >= 55 ? 'Good' : 'Fair';
      return { ...buyer, score, reasons, label };
    });
    return { success: true, data: scored.sort((a, b) => b.score - a.score) };
  }
  return await apiCall('/api/v1/matches/refresh', { method: 'POST', body: JSON.stringify({ lot_id: lotData.id || lotData.lot_id }) });
}

export async function getOffers(params = {}) {
  if (DEMO_MODE) {
    await delay();
    return { success: true, data: DEMO_OFFERS };
  }
  const query = new URLSearchParams(params).toString();
  return await apiCall(`/api/v1/offers${query ? `?${query}` : ''}`);
}

export async function createOffer(offerData) {
  if (DEMO_MODE) {
    await delay(500);
    const newOffer = { id: `demo-offer-${Date.now()}`, ...offerData, status: 'pending', created_at: new Date().toISOString() };
    return { success: true, data: newOffer, message: 'Offer submitted successfully' };
  }
  return await apiCall('/api/v1/offers', { method: 'POST', body: JSON.stringify(offerData) });
}

export async function updateOffer(offerId, status) {
  if (DEMO_MODE) {
    await delay(400);
    return { success: true, data: { id: offerId, status }, message: `Offer ${status}` };
  }
  return await apiCall(`/api/v1/offers/${offerId}`, { method: 'PUT', body: JSON.stringify({ status }) });
}

export async function getTransactions(params = {}) {
  if (DEMO_MODE) {
    await delay();
    return { success: true, data: DEMO_TRANSACTIONS };
  }
  const query = new URLSearchParams(params).toString();
  return await apiCall(`/api/v1/transactions${query ? `?${query}` : ''}`);
}

export async function getTransaction(id) {
  if (DEMO_MODE) {
    await delay(300);
    const txn = DEMO_TRANSACTIONS.find(t => t.id === id);
    return txn ? { success: true, data: txn } : { success: false, message: 'Transaction not found' };
  }
  return await apiCall(`/api/v1/transactions/${id}`);
}

export async function getGrievances(farmerId = null) {
  if (DEMO_MODE) {
    await delay();
    return { success: true, data: DEMO_GRIEVANCES };
  }
  return await apiCall(`/api/v1/disputes${farmerId ? `?farmer_id=${farmerId}` : ''}`);
}

export async function createGrievance(data) {
  if (DEMO_MODE) {
    await delay(500);
    return { success: true, data: { id: `demo-g-${Date.now()}`, ...data, status: 'open', created_at: new Date().toISOString() }, message: 'Grievance filed successfully. We will review it shortly.' };
  }
  return await apiCall('/api/v1/disputes', { method: 'POST', body: JSON.stringify(data) });
}

export async function checkHealth() {
  try {
    return await apiCall('/api/v1/health');
  } catch {
    return { success: false, mode: 'demo', status: 'backend_offline' };
  }
}
