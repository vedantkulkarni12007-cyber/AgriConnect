// =============================================================
// KrishiLink API Service
// All communication between frontend and Flask backend goes here
// 
// HOW IT WORKS:
// - In DEMO MODE: returns local mock data (no backend needed)
// - In LIVE MODE: calls the Flask backend API
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
} from '../data/demoData';

// The base URL for the Flask backend
// In development: http://localhost:5000
// This is set in frontend/.env as VITE_API_BASE_URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// Are we using demo mode?
// Demo mode is ON by default unless explicitly set to false
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE !== 'false';

// Simulate a small delay to make demo feel realistic
const delay = (ms = 400) => new Promise(resolve => setTimeout(resolve, ms));

// Generic API call helper with error handling
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.warn(`API call failed for ${endpoint}:`, error.message);
    throw error;
  }
}

// =============================================================
// PRICES API
// =============================================================

/**
 * Get current prices for all crops or filter by crop/market
 * @param {string} crop - Optional crop name filter
 * @param {string} market - Optional market name filter
 */
export async function getPrices(crop = null, market = null) {
  if (DEMO_MODE) {
    await delay();
    let prices = [...DEMO_PRICES];
    if (crop) prices = prices.filter(p => p.crop === crop);
    if (market) prices = prices.filter(p => p.market === market);
    return { success: true, data: prices };
  }

  try {
    const params = new URLSearchParams();
    if (crop) params.append('crop', crop);
    if (market) params.append('market', market);
    return await apiCall(`/api/prices?${params}`);
  } catch {
    // Fallback to demo data if backend fails
    return { success: true, data: DEMO_PRICES, fallback: true };
  }
}

/**
 * Get price history for chart (last N days)
 * @param {string} crop
 * @param {string} market
 * @param {number} days
 */
export async function getPriceHistory(crop, market = null, days = 15) {
  if (DEMO_MODE) {
    await delay();
    const marketKey = market || Object.keys(DEMO_PRICE_HISTORY[crop] || {})[0];
    const history = DEMO_PRICE_HISTORY[crop]?.[marketKey] || [];
    return { success: true, data: history.slice(-days) };
  }

  try {
    return await apiCall(`/api/prices/${crop}/history?market=${market || ''}&days=${days}`);
  } catch {
    const marketKey = market || Object.keys(DEMO_PRICE_HISTORY[crop] || {})[0];
    const history = DEMO_PRICE_HISTORY[crop]?.[marketKey] || [];
    return { success: true, data: history, fallback: true };
  }
}

// =============================================================
// TRENDS API
// =============================================================

/**
 * Get trend analysis for a crop
 * Returns: current_price, moving_average, percentage_change, trend, explanation
 * TREND IS RULE-BASED (NOT AI): change > 3% = RISING, < -3% = FALLING, else STABLE
 */
export async function getTrend(crop, market = null) {
  if (DEMO_MODE) {
    await delay(300);
    // Find price data for this crop
    const priceData = DEMO_PRICES.find(p =>
      p.crop === crop && (!market || p.market === market)
    ) || DEMO_PRICES.find(p => p.crop === crop);

    if (!priceData) {
      return { success: false, message: 'Crop not found' };
    }

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
        // Human-readable explanation — NOT AI, just arithmetic
        explanation: priceData.trend === 'RISING'
          ? `${crop} prices are currently ${priceData.change_pct}% above the 7-day average in ${priceData.market}. This is based on recent market data.`
          : priceData.trend === 'FALLING'
          ? `${crop} prices have dropped ${Math.abs(priceData.change_pct)}% below the 7-day average. Consider market timing.`
          : `${crop} prices are stable within 3% of the 7-day average. Normal market conditions.`,
        note: 'This trend signal is calculated from price arithmetic — not AI prediction.',
      }
    };
  }

  try {
    return await apiCall(`/api/trends/${crop}${market ? `?market=${market}` : ''}`);
  } catch {
    return { success: false, message: 'Trend data unavailable' };
  }
}

// =============================================================
// LOTS API
// =============================================================

/**
 * Get all produce lots (listings)
 */
export async function getLots(farmerId = null) {
  if (DEMO_MODE) {
    await delay();
    return { success: true, data: DEMO_LOTS };
  }

  try {
    const params = farmerId ? `?farmer_id=${farmerId}` : '';
    return await apiCall(`/api/lots${params}`);
  } catch {
    return { success: true, data: DEMO_LOTS, fallback: true };
  }
}

/**
 * Create a new produce lot
 * @param {Object} lotData - { crop, quantity, unit, grade, location, expected_price, available_date, notes }
 */
export async function createLot(lotData) {
  if (DEMO_MODE) {
    await delay(600);
    // Simulate lot creation
    const newLot = {
      id: `demo-lot-${Date.now()}`,
      ...lotData,
      farmer: 'Ramesh Patil', // demo farmer
      status: 'active',
      created_at: new Date().toISOString(),
    };
    return { success: true, data: newLot, message: 'Lot created successfully' };
  }

  try {
    return await apiCall('/api/lots', {
      method: 'POST',
      body: JSON.stringify(lotData),
    });
  } catch {
    return { success: false, message: 'Failed to create lot. Please try again.' };
  }
}

// =============================================================
// MATCHING API
// =============================================================

/**
 * Get matching buyers for a lot
 * Matching is RULE-BASED (crop match, grade, quantity, distance)
 */
export async function getMatches(lotData) {
  if (DEMO_MODE) {
    await delay(800);
    // Rule-based demo matching: filter buyers by crop, score them
    const buyers = DEMO_BUYERS.filter(b =>
      b.crops.includes(lotData.crop || 'Onion')
    );

    const scored = buyers.map(buyer => {
      let score = 0;
      const reasons = [];

      // Crop match: 40 points
      if (buyer.crops.includes(lotData.crop)) {
        score += 40;
        reasons.push('✓ Crop matches buyer preference');
      }

      // Grade match: 25 points
      if (lotData.grade === 'A') {
        score += 25;
        reasons.push('✓ Grade A preferred by buyer');
      } else if (lotData.grade === 'B') {
        score += 15;
        reasons.push('✓ Grade B accepted');
      }

      // Quantity: 20 points
      const qty = parseInt(lotData.quantity) || 100;
      if (qty >= buyer.min_qty && qty <= buyer.max_qty) {
        score += 20;
        reasons.push('✓ Quantity within buyer range');
      } else if (qty >= buyer.min_qty * 0.5) {
        score += 10;
        reasons.push('~ Quantity partially compatible');
      }

      // Distance: 15 points
      if (buyer.distance_km <= 20) {
        score += 15;
        reasons.push('✓ Buyer is nearby (< 20 km)');
      } else if (buyer.distance_km <= 100) {
        score += 8;
        reasons.push('~ Buyer within 100 km');
      }

      const label = score >= 80 ? 'Excellent' : score >= 55 ? 'Good' : 'Fair';

      return { ...buyer, score, reasons, label };
    });

    return {
      success: true,
      data: scored.sort((a, b) => b.score - a.score),
    };
  }

  try {
    return await apiCall('/api/match', {
      method: 'POST',
      body: JSON.stringify(lotData),
    });
  } catch {
    return { success: false, message: 'Matching unavailable', data: [] };
  }
}

// =============================================================
// OFFERS API
// =============================================================

export async function getOffers(params = {}) {
  if (DEMO_MODE) {
    await delay();
    return { success: true, data: DEMO_OFFERS };
  }
  try {
    const query = new URLSearchParams(params).toString();
    return await apiCall(`/api/offers${query ? `?${query}` : ''}`);
  } catch {
    return { success: true, data: DEMO_OFFERS, fallback: true };
  }
}

export async function createOffer(offerData) {
  if (DEMO_MODE) {
    await delay(500);
    const newOffer = {
      id: `demo-offer-${Date.now()}`,
      ...offerData,
      status: 'pending',
      created_at: new Date().toISOString(),
    };
    return { success: true, data: newOffer, message: 'Offer submitted successfully' };
  }
  try {
    return await apiCall('/api/offers', {
      method: 'POST',
      body: JSON.stringify(offerData),
    });
  } catch {
    return { success: false, message: 'Failed to submit offer' };
  }
}

export async function updateOffer(offerId, status) {
  if (DEMO_MODE) {
    await delay(400);
    return { success: true, data: { id: offerId, status }, message: `Offer ${status}` };
  }
  try {
    return await apiCall(`/api/offers/${offerId}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  } catch {
    return { success: false, message: 'Failed to update offer' };
  }
}

// =============================================================
// TRANSACTIONS API
// =============================================================

export async function getTransactions(params = {}) {
  if (DEMO_MODE) {
    await delay();
    return { success: true, data: DEMO_TRANSACTIONS };
  }
  try {
    const query = new URLSearchParams(params).toString();
    return await apiCall(`/api/transactions${query ? `?${query}` : ''}`);
  } catch {
    return { success: true, data: DEMO_TRANSACTIONS, fallback: true };
  }
}

export async function getTransaction(id) {
  if (DEMO_MODE) {
    await delay(300);
    const txn = DEMO_TRANSACTIONS.find(t => t.id === id);
    return txn
      ? { success: true, data: txn }
      : { success: false, message: 'Transaction not found' };
  }
  try {
    return await apiCall(`/api/transactions/${id}`);
  } catch {
    return { success: false, message: 'Transaction unavailable' };
  }
}

// =============================================================
// GRIEVANCES API
// =============================================================

export async function getGrievances(farmerId = null) {
  if (DEMO_MODE) {
    await delay();
    return { success: true, data: DEMO_GRIEVANCES };
  }
  try {
    return await apiCall(`/api/grievances${farmerId ? `?farmer_id=${farmerId}` : ''}`);
  } catch {
    return { success: true, data: DEMO_GRIEVANCES, fallback: true };
  }
}

export async function createGrievance(data) {
  if (DEMO_MODE) {
    await delay(500);
    return {
      success: true,
      data: { id: `demo-g-${Date.now()}`, ...data, status: 'open', created_at: new Date().toISOString() },
      message: 'Grievance filed successfully. We will review it shortly.',
    };
  }
  try {
    return await apiCall('/api/grievances', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  } catch {
    return { success: false, message: 'Failed to file grievance' };
  }
}

// =============================================================
// HEALTH CHECK
// =============================================================
export async function checkHealth() {
  try {
    return await apiCall('/api/health');
  } catch {
    return { success: false, mode: 'demo', status: 'backend_offline' };
  }
}
