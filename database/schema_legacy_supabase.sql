-- =============================================================
-- KrishiLink Database Schema
-- Run this in your Supabase SQL Editor to create all tables
-- =============================================================
-- INSTRUCTIONS:
-- 1. Go to https://supabase.com and create a project
-- 2. Click "SQL Editor" in the left sidebar
-- 3. Paste this entire file and click "Run"
-- =============================================================

-- Enable UUID extension (already available in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================
-- USERS TABLE
-- Stores all users: farmers, buyers, FPOs
-- =============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('farmer', 'buyer', 'fpo', 'admin')),
    location TEXT,
    district TEXT,
    state TEXT DEFAULT 'Maharashtra',
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- FARMER PROFILES TABLE
-- Extra details specific to farmers
-- =============================================================
CREATE TABLE IF NOT EXISTS farmer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    aadhaar_number TEXT,
    land_area_acres DECIMAL(10,2),
    primary_crops TEXT[],          -- Array of crops they grow
    bank_account TEXT,
    ifsc_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- BUYER PROFILES TABLE
-- Extra details specific to buyers (traders, processors, exporters)
-- =============================================================
CREATE TABLE IF NOT EXISTS buyer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_name TEXT NOT NULL,
    business_type TEXT CHECK (business_type IN ('trader', 'processor', 'exporter', 'retailer')),
    license_number TEXT,
    crops_interested TEXT[],        -- Array of crops they want to buy
    min_quantity_quintals DECIMAL(10,2),
    max_quantity_quintals DECIMAL(10,2),
    preferred_grade TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3,2) DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- FPO PROFILES TABLE
-- Farmer Producer Organization details
-- =============================================================
CREATE TABLE IF NOT EXISTS fpo_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_name TEXT NOT NULL,
    registration_number TEXT,
    member_count INTEGER DEFAULT 0,
    total_land_acres DECIMAL(12,2),
    primary_crops TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- CROPS TABLE
-- Master list of crops with metadata
-- =============================================================
CREATE TABLE IF NOT EXISTS crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    name_marathi TEXT,
    name_hindi TEXT,
    category TEXT,                  -- vegetable, grain, cash_crop, spice
    unit TEXT DEFAULT 'quintal',    -- quintal, kg, tonne
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- MARKETS TABLE
-- Agricultural markets / mandis
-- =============================================================
CREATE TABLE IF NOT EXISTS markets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    name_marathi TEXT,
    district TEXT NOT NULL,
    state TEXT DEFAULT 'Maharashtra',
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    market_type TEXT DEFAULT 'APMC',   -- APMC, private, eNAM
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- PRICES TABLE
-- Daily price data from mandis
-- =============================================================
CREATE TABLE IF NOT EXISTS prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_id UUID REFERENCES crops(id),
    market_id UUID REFERENCES markets(id),
    price_date DATE NOT NULL,
    min_price DECIMAL(10,2) NOT NULL,        -- Lowest price seen that day
    max_price DECIMAL(10,2) NOT NULL,        -- Highest price seen that day
    modal_price DECIMAL(10,2) NOT NULL,      -- Most common / average price
    volume_tonnes DECIMAL(10,2),             -- How much was traded
    source TEXT DEFAULT 'demo',              -- 'demo', 'agmarknet', 'enam'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(crop_id, market_id, price_date)   -- One record per crop per market per day
);

-- =============================================================
-- LOTS TABLE
-- Produce listings created by farmers/FPOs
-- =============================================================
CREATE TABLE IF NOT EXISTS lots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL REFERENCES users(id),
    crop TEXT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit TEXT DEFAULT 'quintal',
    grade TEXT CHECK (grade IN ('A', 'B', 'C')),
    location TEXT NOT NULL,
    district TEXT,
    expected_price DECIMAL(10,2),            -- Price per quintal farmer expects
    available_date DATE,
    notes TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'matched', 'sold', 'expired', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- BUYER REQUIREMENTS TABLE
-- What buyers are looking for
-- =============================================================
CREATE TABLE IF NOT EXISTS buyer_requirements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id UUID NOT NULL REFERENCES users(id),
    crop TEXT NOT NULL,
    min_quantity DECIMAL(10,2),
    max_quantity DECIMAL(10,2),
    preferred_grade TEXT,
    max_price DECIMAL(10,2),                 -- Maximum price they'll pay
    preferred_location TEXT,
    valid_until DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- OFFERS TABLE
-- Offers made by buyers to farmers for their lots
-- =============================================================
CREATE TABLE IF NOT EXISTS offers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lot_id UUID NOT NULL REFERENCES lots(id),
    buyer_id UUID NOT NULL REFERENCES users(id),
    farmer_id UUID NOT NULL REFERENCES users(id),
    crop TEXT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    offered_price DECIMAL(10,2) NOT NULL,    -- Price per quintal
    total_value DECIMAL(12,2),               -- quantity * offered_price
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'expired', 'completed')),
    valid_until TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- TRANSACTIONS TABLE
-- Tracks the complete lifecycle of a sale
-- =============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    offer_id UUID NOT NULL REFERENCES offers(id),
    lot_id UUID NOT NULL REFERENCES lots(id),
    farmer_id UUID NOT NULL REFERENCES users(id),
    buyer_id UUID NOT NULL REFERENCES users(id),
    crop TEXT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    agreed_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    current_stage TEXT DEFAULT 'offer_accepted',
    -- Stages: offer_created → offer_accepted → produce_dispatched
    --         → payment_pending → payment_received → completed
    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'processing', 'received', 'failed')),
    payment_reference TEXT,                  -- UPI/bank reference
    dispatch_date TIMESTAMP WITH TIME ZONE,
    payment_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- GRIEVANCES TABLE
-- Dispute/issue records for transparency
-- =============================================================
CREATE TABLE IF NOT EXISTS grievances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID REFERENCES transactions(id),
    filed_by UUID NOT NULL REFERENCES users(id),
    issue_type TEXT NOT NULL CHECK (issue_type IN ('price_dispute', 'quality_dispute', 'payment_delay', 'delivery_issue', 'fraud', 'other')),
    description TEXT NOT NULL,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'under_review', 'resolved', 'closed')),
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- STORAGE LOCATIONS TABLE
-- Nearby warehouses / cold storage facilities
-- =============================================================
CREATE TABLE IF NOT EXISTS storage_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    type TEXT CHECK (type IN ('warehouse', 'cold_storage', 'silo', 'godown')),
    location TEXT NOT NULL,
    district TEXT,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    capacity_tonnes DECIMAL(10,2),
    available_capacity_tonnes DECIMAL(10,2),
    price_per_tonne_per_day DECIMAL(10,2),
    contact_phone TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- NOTIFICATIONS TABLE
-- In-app notifications for users
-- =============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,         -- 'price_alert', 'new_offer', 'offer_accepted', 'payment'
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_id UUID,            -- ID of related lot/offer/transaction
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================
-- INDEXES for better query performance
-- =============================================================
CREATE INDEX IF NOT EXISTS idx_prices_crop_date ON prices(crop_id, price_date DESC);
CREATE INDEX IF NOT EXISTS idx_lots_seller ON lots(seller_id);
CREATE INDEX IF NOT EXISTS idx_lots_status ON lots(status);
CREATE INDEX IF NOT EXISTS idx_offers_lot ON offers(lot_id);
CREATE INDEX IF NOT EXISTS idx_offers_buyer ON offers(buyer_id);
CREATE INDEX IF NOT EXISTS idx_offers_farmer ON offers(farmer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_farmer ON transactions(farmer_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);

-- =============================================================
-- ROW LEVEL SECURITY (RLS) - Enable when using Supabase Auth
-- Uncomment these after setting up Supabase Auth
-- =============================================================
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE lots ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE offers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Example RLS policy (farmers can only see their own lots):
-- CREATE POLICY "Farmers see own lots" ON lots
--     FOR SELECT USING (auth.uid() = seller_id);
