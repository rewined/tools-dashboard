-- Candle Testing Tables for Supabase

-- Main test table
CREATE TABLE IF NOT EXISTS candle_tests (
    id VARCHAR(50) PRIMARY KEY,
    vessel VARCHAR(200) NOT NULL,
    wax VARCHAR(200) NOT NULL,
    fragrance VARCHAR(200) NOT NULL,
    blend_percentage FLOAT NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Individual trials (wicks)
CREATE TABLE IF NOT EXISTS candle_trials (
    id VARCHAR(50) PRIMARY KEY,
    test_id VARCHAR(50) NOT NULL REFERENCES candle_tests(id) ON DELETE CASCADE,
    trial_number INTEGER NOT NULL,
    wick VARCHAR(200) NOT NULL
);

-- Evaluation data
CREATE TABLE IF NOT EXISTS candle_evaluations (
    id SERIAL PRIMARY KEY,
    trial_id VARCHAR(50) NOT NULL REFERENCES candle_trials(id) ON DELETE CASCADE,
    evaluation_type VARCHAR(20) NOT NULL, -- '1hr', '2hr', '4hr', 'post_extinguish'
    full_melt_pool BOOLEAN,
    melt_pool_depth FLOAT, -- in inches
    external_temp FLOAT, -- in Fahrenheit
    flame_height FLOAT, -- in inches
    after_glow INTEGER, -- in seconds
    after_smoke INTEGER, -- in seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(trial_id, evaluation_type)
);

-- Product cache table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    product_type VARCHAR(20) NOT NULL, -- 'vessel', 'wax', 'fragrance', 'wick'
    name VARCHAR(200) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Assembly analysis table
CREATE TABLE IF NOT EXISTS assembly_analysis (
    id SERIAL PRIMARY KEY,
    assembly_id VARCHAR(50) NOT NULL,
    assembly_itemid VARCHAR(100) NOT NULL,
    assembly_name VARCHAR(200) NOT NULL,
    oz_fill FLOAT,
    vessel_itemid VARCHAR(100),
    vessel_name VARCHAR(200),
    wax_itemid VARCHAR(100),
    wax_name VARCHAR(200),
    fragrance_itemid VARCHAR(100),
    fragrance_name VARCHAR(200),
    wick_itemid VARCHAR(100),
    wick_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Wick recommendations table
CREATE TABLE IF NOT EXISTS wick_recommendations (
    id SERIAL PRIMARY KEY,
    vessel_size_category VARCHAR(50) NOT NULL, -- 'small', 'medium', 'large', 'xl'
    oz_fill_min FLOAT NOT NULL,
    oz_fill_max FLOAT NOT NULL,
    diameter_min FLOAT, -- estimated inches
    diameter_max FLOAT, -- estimated inches
    wax_type VARCHAR(100), -- NULL for general, or specific like 'soy', 'paraffin', 'blend'
    fragrance_density VARCHAR(50), -- 'light', 'medium', 'heavy', NULL for general
    recommended_wicks TEXT[] NOT NULL, -- array of wick itemids
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_candle_tests_created_at ON candle_tests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_candle_trials_test_id ON candle_trials(test_id);
CREATE INDEX IF NOT EXISTS idx_candle_evaluations_trial_id ON candle_evaluations(trial_id);
CREATE INDEX IF NOT EXISTS idx_products_type ON products(product_type);
CREATE INDEX IF NOT EXISTS idx_assembly_analysis_oz_fill ON assembly_analysis(oz_fill);
CREATE INDEX IF NOT EXISTS idx_wick_recommendations_oz_fill ON wick_recommendations(oz_fill_min, oz_fill_max);