// =============================================================
// KrishiLink Demo Data (Frontend)
// All realistic Indian agricultural data used when backend is unavailable
// =============================================================

// Helper to get a date string N days ago
const daysAgo = (n) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().split('T')[0];
};

// =============================================================
// PRICE DATA
// Realistic prices in INR per quintal
// =============================================================
export const DEMO_PRICES = [
  // Onion - Nashik
  { id: 1, crop: 'Onion',   market: 'Nashik',      modal_price: 1850, min_price: 1650, max_price: 2100, change_pct: 5.2,  trend: 'RISING',  volume: 420 },
  { id: 2, crop: 'Onion',   market: 'Lasalgaon',   modal_price: 1920, min_price: 1700, max_price: 2200, change_pct: 8.1,  trend: 'RISING',  volume: 680 },
  { id: 3, crop: 'Onion',   market: 'Pune',        modal_price: 1780, min_price: 1600, max_price: 1950, change_pct: 2.1,  trend: 'STABLE',  volume: 310 },
  { id: 4, crop: 'Onion',   market: 'Ahmednagar',  modal_price: 1690, min_price: 1500, max_price: 1850, change_pct: -4.5, trend: 'FALLING', volume: 190 },
  // Tomato - various
  { id: 5, crop: 'Tomato',  market: 'Nashik',      modal_price: 1200, min_price: 950,  max_price: 1450, change_pct: -12.3,trend: 'FALLING', volume: 280 },
  { id: 6, crop: 'Tomato',  market: 'Pune',        modal_price: 1380, min_price: 1100, max_price: 1600, change_pct: -8.2, trend: 'FALLING', volume: 350 },
  { id: 7, crop: 'Tomato',  market: 'Ahmednagar',  modal_price: 1050, min_price: 850,  max_price: 1250, change_pct: -15.1,trend: 'FALLING', volume: 165 },
  // Soybean
  { id: 8, crop: 'Soybean', market: 'Nashik',      modal_price: 4850, min_price: 4600, max_price: 5100, change_pct: 1.2,  trend: 'STABLE',  volume: 520 },
  { id: 9, crop: 'Soybean', market: 'Aurangabad',  modal_price: 4920, min_price: 4700, max_price: 5200, change_pct: 2.8,  trend: 'STABLE',  volume: 780 },
  // Cotton
  { id: 10, crop: 'Cotton', market: 'Nashik',      modal_price: 6800, min_price: 6500, max_price: 7100, change_pct: 3.5,  trend: 'RISING',  volume: 310 },
  { id: 11, crop: 'Cotton', market: 'Aurangabad',  modal_price: 7100, min_price: 6800, max_price: 7400, change_pct: 4.2,  trend: 'RISING',  volume: 450 },
  // Wheat
  { id: 12, crop: 'Wheat',  market: 'Pune',        modal_price: 2150, min_price: 2050, max_price: 2250, change_pct: 0.5,  trend: 'STABLE',  volume: 890 },
  { id: 13, crop: 'Potato', market: 'Pune',        modal_price: 900,  min_price: 800,  max_price: 1050, change_pct: -2.1, trend: 'STABLE',  volume: 410 },
];

// =============================================================
// PRICE HISTORY (15 days, for chart)
// =============================================================
export const DEMO_PRICE_HISTORY = {
  Onion: {
    Lasalgaon: Array.from({ length: 15 }, (_, i) => ({
      date: daysAgo(14 - i),
      price: Math.round(1600 + (i * 22) + (Math.random() * 80 - 40)),
    })),
    Nashik: Array.from({ length: 15 }, (_, i) => ({
      date: daysAgo(14 - i),
      price: Math.round(1550 + (i * 20) + (Math.random() * 70 - 35)),
    })),
  },
  Tomato: {
    Nashik: Array.from({ length: 15 }, (_, i) => ({
      date: daysAgo(14 - i),
      price: Math.round(2100 - (i * 60) + (Math.random() * 100 - 50)),
    })),
  },
  Soybean: {
    Nashik: Array.from({ length: 15 }, (_, i) => ({
      date: daysAgo(14 - i),
      price: Math.round(4750 + (i * 7) + (Math.random() * 60 - 30)),
    })),
  },
  Cotton: {
    Nashik: Array.from({ length: 15 }, (_, i) => ({
      date: daysAgo(14 - i),
      price: Math.round(6500 + (i * 20) + (Math.random() * 80 - 40)),
    })),
  },
};

// =============================================================
// BUYERS
// =============================================================
export const DEMO_BUYERS = [
  {
    id: 'b1',
    name: 'Mehta Traders Pvt Ltd',
    type: 'Trader',
    crops: ['Onion', 'Tomato'],
    min_qty: 50,
    max_qty: 500,
    location: 'Nashik',
    distance_km: 12,
    verified: true,
    rating: 4.5,
    reviews: 48,
    offer_price: 1800,
  },
  {
    id: 'b2',
    name: 'Pune Agro Exports',
    type: 'Exporter',
    crops: ['Onion', 'Soybean'],
    min_qty: 200,
    max_qty: 2000,
    location: 'Pune',
    distance_km: 45,
    verified: true,
    rating: 4.8,
    reviews: 112,
    offer_price: 1870,
  },
  {
    id: 'b3',
    name: 'FreshMart Retail Chain',
    type: 'Retailer',
    crops: ['Tomato', 'Potato', 'Onion'],
    min_qty: 10,
    max_qty: 100,
    location: 'Mumbai',
    distance_km: 165,
    verified: true,
    rating: 4.2,
    reviews: 31,
    offer_price: 1750,
  },
  {
    id: 'b4',
    name: 'Maharashtra Cotton Corp',
    type: 'Processor',
    crops: ['Cotton'],
    min_qty: 100,
    max_qty: 1000,
    location: 'Aurangabad',
    distance_km: 120,
    verified: false,
    rating: 3.9,
    reviews: 17,
    offer_price: 6900,
  },
];

// =============================================================
// LOTS (produce listings)
// =============================================================
export const DEMO_LOTS = [
  {
    id: 'l1',
    farmer: 'Ramesh Patil',
    crop: 'Onion',
    quantity: 500,
    unit: 'quintal',
    grade: 'A',
    location: 'Lasalgaon',
    expected_price: 1800,
    available_date: daysAgo(-4),
    status: 'active',
    created_at: daysAgo(1),
  },
  {
    id: 'l2',
    farmer: 'Sunita Deshpande',
    crop: 'Tomato',
    quantity: 200,
    unit: 'quintal',
    grade: 'A',
    location: 'Pune',
    expected_price: 1200,
    available_date: daysAgo(-2),
    status: 'matched',
    created_at: daysAgo(3),
  },
  {
    id: 'l3',
    farmer: 'Nashik Farmer Collective FPO',
    crop: 'Onion',
    quantity: 1200,
    unit: 'quintal',
    grade: 'A',
    location: 'Nashik',
    expected_price: 1850,
    available_date: daysAgo(-5),
    status: 'active',
    created_at: daysAgo(2),
  },
];

// =============================================================
// OFFERS
// =============================================================
export const DEMO_OFFERS = [
  {
    id: 'o1',
    buyer: 'Mehta Traders Pvt Ltd',
    crop: 'Onion',
    quantity: 300,
    offered_price: 1780,
    total_value: 534000,
    status: 'pending',
    created_at: daysAgo(1),
    valid_until: daysAgo(-2),
    lot_id: 'l1',
  },
  {
    id: 'o2',
    buyer: 'Pune Agro Exports',
    crop: 'Onion',
    quantity: 150,
    offered_price: 1720,
    total_value: 258000,
    status: 'accepted',
    created_at: daysAgo(5),
    valid_until: daysAgo(-1),
    lot_id: 'l1',
  },
  {
    id: 'o3',
    buyer: 'FreshMart Retail Chain',
    crop: 'Tomato',
    quantity: 200,
    offered_price: 1150,
    total_value: 230000,
    status: 'pending',
    created_at: daysAgo(2),
    valid_until: daysAgo(-3),
    lot_id: 'l2',
  },
  {
    id: 'o4',
    buyer: 'Maharashtra Cotton Corp',
    crop: 'Soybean',
    quantity: 300,
    offered_price: 4450,
    total_value: 1335000,
    status: 'rejected',
    created_at: daysAgo(7),
    valid_until: daysAgo(-1),
    lot_id: 'l3',
  },
];

// =============================================================
// TRANSACTIONS
// =============================================================
export const DEMO_TRANSACTIONS = [
  {
    id: 'txn001',
    buyer: 'Pune Agro Exports',
    crop: 'Onion',
    quantity: 150,
    agreed_price: 1720,
    total_amount: 258000,
    current_stage: 'payment_received',
    payment_status: 'received',
    stages_completed: ['offer_created', 'offer_accepted', 'produce_dispatched', 'payment_pending', 'payment_received'],
    created_at: daysAgo(8),
    payment_date: daysAgo(2),
  },
  {
    id: 'txn002',
    buyer: 'FreshMart Retail Chain',
    crop: 'Tomato',
    quantity: 200,
    agreed_price: 1150,
    total_amount: 230000,
    current_stage: 'produce_dispatched',
    payment_status: 'pending',
    stages_completed: ['offer_created', 'offer_accepted', 'produce_dispatched'],
    created_at: daysAgo(4),
    dispatch_date: daysAgo(1),
  },
];

// =============================================================
// STORAGE LOCATIONS
// =============================================================
export const DEMO_STORAGE = [
  {
    id: 's1',
    name: 'Nashik Cold Storage',
    type: 'Cold Storage',
    location: 'Nashik',
    distance_km: 8,
    capacity: 500,
    available: 200,
    price_per_day: 2.50,
    lat: 19.9975,
    lng: 73.7898,
  },
  {
    id: 's2',
    name: 'Lasalgaon Agri Warehouse',
    type: 'Warehouse',
    location: 'Lasalgaon',
    distance_km: 3,
    capacity: 1000,
    available: 650,
    price_per_day: 1.20,
    lat: 20.1224,
    lng: 73.9698,
  },
  {
    id: 's3',
    name: 'Pune Agri Godown',
    type: 'Godown',
    location: 'Pune',
    distance_km: 45,
    capacity: 300,
    available: 50,
    price_per_day: 1.80,
    lat: 18.5204,
    lng: 73.8567,
  },
  {
    id: 's4',
    name: 'Ahmednagar Silo',
    type: 'Silo',
    location: 'Ahmednagar',
    distance_km: 78,
    capacity: 2000,
    available: 1200,
    price_per_day: 0.90,
    lat: 19.0948,
    lng: 74.7480,
  },
];

// =============================================================
// GRIEVANCES
// =============================================================
export const DEMO_GRIEVANCES = [
  {
    id: 'g1',
    transaction_id: 'txn002',
    issue_type: 'Payment Delay',
    description: 'Payment was expected within 3 days but has not been received after 5 days.',
    status: 'under_review',
    created_at: daysAgo(3),
  },
  {
    id: 'g2',
    transaction_id: 'txn001',
    issue_type: 'Quality Dispute',
    description: 'Buyer claims quantity received was 140 quintals. Dispatch record shows 150 quintals.',
    status: 'resolved',
    created_at: daysAgo(10),
    resolution: 'Verified with transport bill. Payment adjusted.',
  },
];

// =============================================================
// NOTIFICATIONS
// =============================================================
export const DEMO_NOTIFICATIONS = [
  {
    id: 'n1',
    type: 'price_alert',
    title: 'Onion Prices Rising',
    message: 'Onion prices in Lasalgaon are up 8.1% today. Current modal price: ₹1,920/quintal.',
    is_read: false,
    created_at: daysAgo(0),
    icon: 'TrendingUp',
  },
  {
    id: 'n2',
    type: 'new_offer',
    title: 'New Buyer Offer Received',
    message: 'Mehta Traders has made an offer of ₹1,780/quintal for your Onion lot.',
    is_read: false,
    created_at: daysAgo(1),
    icon: 'HandShake',
  },
  {
    id: 'n3',
    type: 'offer_accepted',
    title: 'Offer Accepted',
    message: 'Your offer to Pune Agro Exports for 150 quintals of Onion has been accepted.',
    is_read: true,
    created_at: daysAgo(5),
    icon: 'CheckCircle',
  },
  {
    id: 'n4',
    type: 'payment',
    title: 'Payment Received',
    message: '₹2,58,000 received from Pune Agro Exports for Transaction #txn001.',
    is_read: true,
    created_at: daysAgo(2),
    icon: 'IndianRupee',
  },
  {
    id: 'n5',
    type: 'price_alert',
    title: 'Tomato Prices Falling',
    message: 'Tomato prices in Nashik have dropped 12.3%. Consider selling soon.',
    is_read: true,
    created_at: daysAgo(1),
    icon: 'TrendingDown',
  },
];

// =============================================================
// MAP MARKERS
// =============================================================
export const DEMO_MARKERS = [
  // Mandis
  { id: 'm1', type: 'mandi', name: 'Nashik APMC',     lat: 19.9975, lng: 73.7898, info: 'Major APMC market. 40+ crops traded daily.' },
  { id: 'm2', type: 'mandi', name: 'Lasalgaon APMC',  lat: 20.1224, lng: 73.9698, info: 'Asia\'s largest onion market.' },
  { id: 'm3', type: 'mandi', name: 'Pune APMC',       lat: 18.5204, lng: 73.8567, info: 'Regional APMC market.' },
  { id: 'm4', type: 'mandi', name: 'Ahmednagar APMC', lat: 19.0948, lng: 74.7480, info: 'Local APMC market.' },
  // Buyers
  { id: 'b1', type: 'buyer', name: 'Mehta Traders',   lat: 20.0032, lng: 73.7814, info: 'Verified Trader. Onion & Tomato.' },
  { id: 'b2', type: 'buyer', name: 'Pune Agro Exports',lat: 18.5280, lng: 73.8620, info: 'Verified Exporter. Onion & Soybean.' },
  // Storage
  { id: 's1', type: 'storage', name: 'Nashik Cold Storage',    lat: 19.9840, lng: 73.7960, info: '200 tonnes available. ₹2.50/tonne/day.' },
  { id: 's2', type: 'storage', name: 'Lasalgaon Agri Warehouse',lat: 20.1180, lng: 73.9650, info: '650 tonnes available. ₹1.20/tonne/day.' },
];

// =============================================================
// DEMO USERS (for demo login)
// =============================================================
export const DEMO_USERS = {
  farmer: {
    id: 'demo-farmer',
    name: 'Ramesh Patil',
    role: 'farmer',
    location: 'Lasalgaon, Nashik',
    phone: '9876543210',
    email: 'ramesh@demo.com',
  },
  buyer: {
    id: 'demo-buyer',
    name: 'Mehta Traders',
    role: 'buyer',
    location: 'Nashik, Maharashtra',
    phone: '9987654321',
    email: 'mehta@demo.com',
  },
  fpo: {
    id: 'demo-fpo',
    name: 'Nashik Farmer Collective FPO',
    role: 'fpo',
    location: 'Nashik, Maharashtra',
    phone: '9900112233',
    email: 'fpo1@demo.com',
  },
};
