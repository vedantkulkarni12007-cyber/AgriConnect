-- =============================================================
-- KrishiLink Seed Data
-- Run this AFTER schema.sql to populate demo data
-- =============================================================
-- INSTRUCTIONS:
-- 1. First run schema.sql in Supabase SQL Editor
-- 2. Then run this file in Supabase SQL Editor
-- =============================================================

-- -------------------------
-- MARKETS
-- -------------------------
INSERT INTO markets (id, name, name_marathi, district, state, latitude, longitude, market_type) VALUES
  ('11111111-0000-0000-0000-000000000001', 'Nashik', 'नाशिक', 'Nashik', 'Maharashtra', 19.9975, 73.7898, 'APMC'),
  ('11111111-0000-0000-0000-000000000002', 'Lasalgaon', 'लासलगाव', 'Nashik', 'Maharashtra', 20.1224, 73.9698, 'APMC'),
  ('11111111-0000-0000-0000-000000000003', 'Pune', 'पुणे', 'Pune', 'Maharashtra', 18.5204, 73.8567, 'APMC'),
  ('11111111-0000-0000-0000-000000000004', 'Ahmednagar', 'अहमदनगर', 'Ahmednagar', 'Maharashtra', 19.0948, 74.7480, 'APMC'),
  ('11111111-0000-0000-0000-000000000005', 'Solapur', 'सोलापूर', 'Solapur', 'Maharashtra', 17.6868, 75.9064, 'APMC'),
  ('11111111-0000-0000-0000-000000000006', 'Aurangabad', 'औरंगाबाद', 'Aurangabad', 'Maharashtra', 19.8762, 75.3433, 'APMC')
ON CONFLICT DO NOTHING;

-- -------------------------
-- CROPS
-- -------------------------
INSERT INTO crops (id, name, name_marathi, name_hindi, category, unit) VALUES
  ('22222222-0000-0000-0000-000000000001', 'Onion',   'कांदा',   'प्याज',    'vegetable',  'quintal'),
  ('22222222-0000-0000-0000-000000000002', 'Tomato',  'टोमॅटो',  'टमाटर',   'vegetable',  'quintal'),
  ('22222222-0000-0000-0000-000000000003', 'Soybean', 'सोयाबीन', 'सोयाबीन', 'cash_crop',  'quintal'),
  ('22222222-0000-0000-0000-000000000004', 'Cotton',  'कापूस',   'कपास',    'cash_crop',  'quintal'),
  ('22222222-0000-0000-0000-000000000005', 'Wheat',   'गहू',     'गेहूँ',    'grain',      'quintal'),
  ('22222222-0000-0000-0000-000000000006', 'Potato',  'बटाटा',   'आलू',     'vegetable',  'quintal'),
  ('22222222-0000-0000-0000-000000000007', 'Chilli',  'मिर्ची',   'मिर्च',    'spice',      'quintal'),
  ('22222222-0000-0000-0000-000000000008', 'Rice',    'तांदूळ',  'चावल',    'grain',      'quintal')
ON CONFLICT DO NOTHING;

-- -------------------------
-- USERS (farmers, buyers, fpos)
-- -------------------------
INSERT INTO users (id, email, phone, full_name, role, location, district, state) VALUES
  -- Farmers
  ('33333333-0000-0000-0000-000000000001', 'ramesh@demo.com',  '9876543210', 'Ramesh Patil',    'farmer', 'Lasalgaon', 'Nashik',    'Maharashtra'),
  ('33333333-0000-0000-0000-000000000002', 'sunita@demo.com',  '9876543211', 'Sunita Deshpande','farmer', 'Pune',      'Pune',      'Maharashtra'),
  ('33333333-0000-0000-0000-000000000003', 'ganesh@demo.com',  '9876543212', 'Ganesh Shinde',   'farmer', 'Solapur',   'Solapur',   'Maharashtra'),
  ('33333333-0000-0000-0000-000000000004', 'laxmi@demo.com',   '9876543213', 'Laxmi Jadhav',    'farmer', 'Nashik',    'Nashik',    'Maharashtra'),
  -- Buyers
  ('33333333-0000-0000-0000-000000000005', 'mehta@demo.com',   '9987654321', 'Mehta Traders Pvt Ltd',  'buyer',  'Nashik', 'Nashik', 'Maharashtra'),
  ('33333333-0000-0000-0000-000000000006', 'agro@demo.com',    '9987654322', 'Pune Agro Exports',      'buyer',  'Pune',   'Pune',   'Maharashtra'),
  ('33333333-0000-0000-0000-000000000007', 'fresh@demo.com',   '9987654323', 'FreshMart Retail Chain',  'buyer', 'Mumbai', 'Mumbai', 'Maharashtra'),
  -- FPO
  ('33333333-0000-0000-0000-000000000008', 'fpo1@demo.com',    '9900112233', 'Nashik Farmer Collective FPO', 'fpo', 'Nashik', 'Nashik', 'Maharashtra'),
  ('33333333-0000-0000-0000-000000000009', 'fpo2@demo.com',    '9900112234', 'Marathwada Agri FPO',          'fpo', 'Aurangabad', 'Aurangabad', 'Maharashtra')
ON CONFLICT DO NOTHING;

-- Farmer profiles
INSERT INTO farmer_profiles (user_id, land_area_acres, primary_crops) VALUES
  ('33333333-0000-0000-0000-000000000001', 5.5,  ARRAY['Onion', 'Tomato']),
  ('33333333-0000-0000-0000-000000000002', 3.0,  ARRAY['Tomato', 'Chilli']),
  ('33333333-0000-0000-0000-000000000003', 8.0,  ARRAY['Soybean', 'Cotton']),
  ('33333333-0000-0000-0000-000000000004', 4.5,  ARRAY['Onion', 'Wheat'])
ON CONFLICT DO NOTHING;

-- Buyer profiles
INSERT INTO buyer_profiles (user_id, business_name, business_type, crops_interested, min_quantity_quintals, max_quantity_quintals, is_verified, rating) VALUES
  ('33333333-0000-0000-0000-000000000005', 'Mehta Traders Pvt Ltd', 'trader',    ARRAY['Onion', 'Tomato'],      50,   500,  TRUE, 4.5),
  ('33333333-0000-0000-0000-000000000006', 'Pune Agro Exports',     'exporter',  ARRAY['Onion', 'Soybean'],     200,  2000, TRUE, 4.8),
  ('33333333-0000-0000-0000-000000000007', 'FreshMart Retail Chain','retailer',  ARRAY['Tomato', 'Potato'],     10,   100,  TRUE, 4.2)
ON CONFLICT DO NOTHING;

-- FPO profiles
INSERT INTO fpo_profiles (user_id, organization_name, member_count, primary_crops) VALUES
  ('33333333-0000-0000-0000-000000000008', 'Nashik Farmer Collective FPO', 120, ARRAY['Onion', 'Tomato', 'Wheat']),
  ('33333333-0000-0000-0000-000000000009', 'Marathwada Agri FPO',           85,  ARRAY['Soybean', 'Cotton'])
ON CONFLICT DO NOTHING;

-- -------------------------
-- LOTS
-- -------------------------
INSERT INTO lots (id, seller_id, crop, quantity, unit, grade, location, district, expected_price, available_date, status) VALUES
  ('44444444-0000-0000-0000-000000000001', '33333333-0000-0000-0000-000000000001', 'Onion',   500,  'quintal', 'A', 'Lasalgaon', 'Nashik',    1800, '2026-09-01', 'active'),
  ('44444444-0000-0000-0000-000000000002', '33333333-0000-0000-0000-000000000002', 'Tomato',  200,  'quintal', 'A', 'Pune',      'Pune',      1200, '2026-08-30', 'matched'),
  ('44444444-0000-0000-0000-000000000003', '33333333-0000-0000-0000-000000000003', 'Soybean', 300,  'quintal', 'B', 'Solapur',   'Solapur',   4500, '2026-09-05', 'active'),
  ('44444444-0000-0000-0000-000000000004', '33333333-0000-0000-0000-000000000004', 'Onion',   150,  'quintal', 'A', 'Nashik',    'Nashik',    1750, '2026-08-28', 'sold'),
  ('44444444-0000-0000-0000-000000000005', '33333333-0000-0000-0000-000000000001', 'Tomato',  80,   'quintal', 'B', 'Lasalgaon', 'Nashik',    900,  '2026-09-10', 'active')
ON CONFLICT DO NOTHING;

-- -------------------------
-- OFFERS
-- -------------------------
INSERT INTO offers (id, lot_id, buyer_id, farmer_id, crop, quantity, offered_price, total_value, status) VALUES
  ('55555555-0000-0000-0000-000000000001', '44444444-0000-0000-0000-000000000002', '33333333-0000-0000-0000-000000000005', '33333333-0000-0000-0000-000000000002', 'Tomato',  200, 1150, 230000, 'pending'),
  ('55555555-0000-0000-0000-000000000002', '44444444-0000-0000-0000-000000000004', '33333333-0000-0000-0000-000000000006', '33333333-0000-0000-0000-000000000004', 'Onion',   150, 1720, 258000, 'accepted'),
  ('55555555-0000-0000-0000-000000000003', '44444444-0000-0000-0000-000000000001', '33333333-0000-0000-0000-000000000005', '33333333-0000-0000-0000-000000000001', 'Onion',   300, 1780, 534000, 'pending'),
  ('55555555-0000-0000-0000-000000000004', '44444444-0000-0000-0000-000000000003', '33333333-0000-0000-0000-000000000006', '33333333-0000-0000-0000-000000000003', 'Soybean', 300, 4450, 1335000,'rejected')
ON CONFLICT DO NOTHING;

-- -------------------------
-- TRANSACTIONS
-- -------------------------
INSERT INTO transactions (id, offer_id, lot_id, farmer_id, buyer_id, crop, quantity, agreed_price, total_amount, current_stage, payment_status) VALUES
  ('66666666-0000-0000-0000-000000000001', '55555555-0000-0000-0000-000000000002', '44444444-0000-0000-0000-000000000004', '33333333-0000-0000-0000-000000000004', '33333333-0000-0000-0000-000000000006', 'Onion', 150, 1720, 258000, 'payment_received', 'received'),
  ('66666666-0000-0000-0000-000000000002', '55555555-0000-0000-0000-000000000001', '44444444-0000-0000-0000-000000000002', '33333333-0000-0000-0000-000000000002', '33333333-0000-0000-0000-000000000005', 'Tomato',200, 1150, 230000, 'produce_dispatched','pending')
ON CONFLICT DO NOTHING;

-- -------------------------
-- STORAGE LOCATIONS
-- -------------------------
INSERT INTO storage_locations (id, name, type, location, district, latitude, longitude, capacity_tonnes, available_capacity_tonnes, price_per_tonne_per_day) VALUES
  ('77777777-0000-0000-0000-000000000001', 'Nashik Cold Storage',      'cold_storage', 'Nashik',    'Nashik',    19.9975, 73.7898, 500,  200,  2.50),
  ('77777777-0000-0000-0000-000000000002', 'Lasalgaon Agri Warehouse', 'warehouse',    'Lasalgaon', 'Nashik',    20.1224, 73.9698, 1000, 650,  1.20),
  ('77777777-0000-0000-0000-000000000003', 'Pune Agri Godown',         'godown',       'Pune',      'Pune',      18.5204, 73.8567, 300,  50,   1.80),
  ('77777777-0000-0000-0000-000000000004', 'Ahmednagar Silo',          'silo',         'Ahmednagar','Ahmednagar',19.0948, 74.7480, 2000, 1200, 0.90)
ON CONFLICT DO NOTHING;

-- -------------------------
-- GRIEVANCES
-- -------------------------
INSERT INTO grievances (id, transaction_id, filed_by, issue_type, description, status) VALUES
  ('88888888-0000-0000-0000-000000000001', '66666666-0000-0000-0000-000000000002', '33333333-0000-0000-0000-000000000002', 'payment_delay',   'Payment was expected within 3 days but has not been received after 5 days.', 'under_review'),
  ('88888888-0000-0000-0000-000000000002', '66666666-0000-0000-0000-000000000001', '33333333-0000-0000-0000-000000000004', 'quality_dispute', 'Buyer claims quantity was 140 quintals but farmer has dispatch record for 150 quintals.', 'resolved')
ON CONFLICT DO NOTHING;

-- =============================================================
-- SUCCESS MESSAGE
-- =============================================================
-- After running this, you should see data in:
-- SELECT * FROM markets;   -- 6 markets
-- SELECT * FROM crops;     -- 8 crops
-- SELECT * FROM users;     -- 9 users
-- SELECT * FROM lots;      -- 5 lots
-- SELECT * FROM offers;    -- 4 offers
-- =============================================================
