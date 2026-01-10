-- Manual Database Migration Script
-- Run these commands in psql to fix the database

-- Step 1: Add SaaS subscription columns to users table (CRITICAL!)
ALTER TABLE users ADD COLUMN IF NOT EXISTS market VARCHAR(50) DEFAULT 'US';
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_expiry TIMESTAMP;

-- Step 2: Add missing columns to members table
ALTER TABLE members ADD COLUMN IF NOT EXISTS birthday DATE;
ALTER TABLE members ADD COLUMN IF NOT EXISTS last_check_in TIMESTAMP;

-- Step 2: Add missing columns to attendance table
ALTER TABLE attendance ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE attendance ADD COLUMN IF NOT EXISTS emotion VARCHAR(50);
ALTER TABLE attendance ADD COLUMN IF NOT EXISTS confidence FLOAT;

-- Step 3: Create body_measurements table
CREATE TABLE IF NOT EXISTS body_measurements (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id),
    weight FLOAT,
    body_fat FLOAT,
    chest FLOAT,
    waist FLOAT,
    arms FLOAT,
    notes TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Create member_notes table
CREATE TABLE IF NOT EXISTS member_notes (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verify tables exist
\dt

-- Show members table structure
\d members

-- Show new tables
\d body_measurements
\d member_notes
