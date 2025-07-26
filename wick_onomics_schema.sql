-- Wick-onomics Enhanced Schema for Supabase
-- This schema extends the existing candle testing tables with advanced wick prediction features

-- Enhanced vessel table with heat dissipation properties
CREATE TABLE IF NOT EXISTS vessels (
    id VARCHAR(50) PRIMARY KEY, -- NetSuite internal ID
    itemid VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    shape VARCHAR(50), -- 'tumbler', 'jar', 'tin', 'votive'
    diameter_mm FLOAT,
    height_mm FLOAT,
    volume_ml FLOAT,
    material VARCHAR(50), -- 'glass', 'metal', 'ceramic'
    double_wick BOOLEAN DEFAULT FALSE,
    heat_dissipation_factor FLOAT DEFAULT 1.0, -- Multiplier for heat retention
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Enhanced wax type table with thermal properties
CREATE TABLE IF NOT EXISTS wax_types (
    id VARCHAR(50) PRIMARY KEY, -- NetSuite internal ID
    itemid VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    melt_point_celsius FLOAT,
    viscosity_index FLOAT,
    manufacturer VARCHAR(100),
    manufacturer_notes TEXT,
    base_type VARCHAR(50), -- 'soy', 'paraffin', 'coconut', 'beeswax', 'blend'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Enhanced fragrance oil table with heat index
CREATE TABLE IF NOT EXISTS fragrance_oils (
    id VARCHAR(50) PRIMARY KEY, -- NetSuite internal ID
    itemid VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    flash_point_celsius FLOAT,
    specific_gravity FLOAT,
    max_load_percentage FLOAT,
    heat_index FLOAT, -- Calculated based on historical burn data
    fragrance_category VARCHAR(50), -- 'vanilla', 'citrus', 'floral', 'woody', 'fresh'
    density_rating VARCHAR(20), -- 'light', 'medium', 'heavy'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Enhanced wick table with technical specifications
CREATE TABLE IF NOT EXISTS wicks (
    id VARCHAR(50) PRIMARY KEY, -- NetSuite internal ID
    itemid VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    series VARCHAR(20) NOT NULL, -- 'ECO', 'CD', 'LX', 'HTP'
    size_number INTEGER NOT NULL, -- 4, 6, 8, 10, etc.
    size_index INTEGER NOT NULL, -- Normalized size across series for arithmetic
    diameter_mm FLOAT,
    core_material VARCHAR(50), -- 'cotton', 'paper', 'zinc'
    coating VARCHAR(50), -- 'none', 'paraffin', 'soy'
    certified_for TEXT[], -- Array of wax types it's certified for
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Enhanced assembly table linking to new tables
CREATE TABLE IF NOT EXISTS assemblies (
    id VARCHAR(50) PRIMARY KEY, -- NetSuite internal ID
    itemid VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    vessel_id VARCHAR(50) REFERENCES vessels(id),
    wax_type_id VARCHAR(50) REFERENCES wax_types(id),
    fragrance_oil_id VARCHAR(50) REFERENCES fragrance_oils(id),
    fragrance_load_percentage FLOAT,
    wick_id_1 VARCHAR(50) REFERENCES wicks(id),
    wick_id_2 VARCHAR(50) REFERENCES wicks(id), -- For double wick candles
    approved_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'testing', 'approved', 'discontinued'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Enhanced test results table with comprehensive metrics
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    assembly_id VARCHAR(50) REFERENCES assemblies(id),
    test_date DATE NOT NULL,
    wax_type_id_tested VARCHAR(50) REFERENCES wax_types(id), -- May differ for wax conversion tests
    wick_id_tested VARCHAR(50) REFERENCES wicks(id),
    test_type VARCHAR(50) NOT NULL, -- 'initial', 'wax_conversion', 'quality_check'
    
    -- Test measurements
    flame_height_mm FLOAT,
    melt_pool_mm_at_1h FLOAT,
    melt_pool_mm_at_2h FLOAT,
    melt_pool_mm_at_4h FLOAT,
    container_temp_celsius FLOAT,
    mushrooming BOOLEAN DEFAULT FALSE,
    tunneling BOOLEAN DEFAULT FALSE,
    smoking BOOLEAN DEFAULT FALSE,
    extinguish_time_hours FLOAT,
    
    -- Results
    pass BOOLEAN NOT NULL,
    failure_reason VARCHAR(100),
    notes TEXT,
    tested_by VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Wax conversion delta tracking
CREATE TABLE IF NOT EXISTS wax_conversion_deltas (
    id SERIAL PRIMARY KEY,
    vessel_id VARCHAR(50) REFERENCES vessels(id),
    old_wax_type_id VARCHAR(50) REFERENCES wax_types(id),
    new_wax_type_id VARCHAR(50) REFERENCES wax_types(id),
    wick_size_delta INTEGER NOT NULL, -- +1, -1, etc. based on size_index
    confidence_score FLOAT DEFAULT 0.5, -- Increases with more test data
    sample_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(vessel_id, old_wax_type_id, new_wax_type_id)
);

-- ML model predictions and confidence tracking
CREATE TABLE IF NOT EXISTS wick_predictions (
    id SERIAL PRIMARY KEY,
    vessel_id VARCHAR(50) REFERENCES vessels(id),
    wax_type_id VARCHAR(50) REFERENCES wax_types(id),
    fragrance_oil_id VARCHAR(50) REFERENCES fragrance_oils(id),
    fragrance_load_percentage FLOAT,
    predicted_wick_id VARCHAR(50) REFERENCES wicks(id),
    confidence_score FLOAT NOT NULL, -- 0.0 to 1.0
    model_version VARCHAR(50) NOT NULL,
    features_used JSONB, -- Store feature vector for debugging
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP,
    actual_wick_id VARCHAR(50) REFERENCES wicks(id) -- Set when verified
);

-- Active learning queue for uncertainty sampling
CREATE TABLE IF NOT EXISTS test_priority_queue (
    id SERIAL PRIMARY KEY,
    assembly_id VARCHAR(50) REFERENCES assemblies(id),
    uncertainty_score FLOAT NOT NULL, -- Higher = less certain, test first
    information_gain_estimate FLOAT,
    priority VARCHAR(20) DEFAULT 'medium', -- 'urgent', 'high', 'medium', 'low'
    reason TEXT, -- Why this test is recommended
    queued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completed_date TIMESTAMP
);

-- Heat index calculation history
CREATE TABLE IF NOT EXISTS fragrance_heat_index_history (
    id SERIAL PRIMARY KEY,
    fragrance_oil_id VARCHAR(50) REFERENCES fragrance_oils(id),
    calculation_date DATE NOT NULL,
    heat_index_value FLOAT NOT NULL,
    sample_size INTEGER NOT NULL,
    avg_flame_height_mm FLOAT,
    avg_melt_pool_mm_2h FLOAT,
    std_deviation FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_vessels_shape ON vessels(shape);
CREATE INDEX IF NOT EXISTS idx_vessels_volume ON vessels(volume_ml);
CREATE INDEX IF NOT EXISTS idx_wax_types_base ON wax_types(base_type);
CREATE INDEX IF NOT EXISTS idx_fragrances_heat ON fragrance_oils(heat_index);
CREATE INDEX IF NOT EXISTS idx_fragrances_category ON fragrance_oils(fragrance_category);
CREATE INDEX IF NOT EXISTS idx_wicks_series_size ON wicks(series, size_number);
CREATE INDEX IF NOT EXISTS idx_wicks_size_index ON wicks(size_index);
CREATE INDEX IF NOT EXISTS idx_assemblies_components ON assemblies(vessel_id, wax_type_id, fragrance_oil_id);
CREATE INDEX IF NOT EXISTS idx_test_results_assembly ON test_results(assembly_id, test_date);
CREATE INDEX IF NOT EXISTS idx_test_results_pass ON test_results(pass);
CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON wick_predictions(confidence_score);
CREATE INDEX IF NOT EXISTS idx_predictions_unverified ON wick_predictions(verified) WHERE verified = FALSE;
CREATE INDEX IF NOT EXISTS idx_priority_queue_pending ON test_priority_queue(uncertainty_score DESC) WHERE completed = FALSE;

-- Create materialized view for majority vote baseline
CREATE MATERIALIZED VIEW IF NOT EXISTS wick_majority_baseline AS
SELECT 
    vessel_id,
    wax_type_id,
    mode() WITHIN GROUP (ORDER BY wick_id_1) AS recommended_wick,
    COUNT(*) as sample_size,
    COUNT(DISTINCT wick_id_1) as wick_variety
FROM assemblies
WHERE approved_date IS NOT NULL
GROUP BY vessel_id, wax_type_id
HAVING COUNT(*) >= 3; -- Need at least 3 samples for reliable baseline

-- Create function to calculate heat index
CREATE OR REPLACE FUNCTION calculate_fragrance_heat_index(fragrance_id VARCHAR(50))
RETURNS FLOAT AS $$
DECLARE
    heat_index FLOAT;
BEGIN
    WITH fragrance_tests AS (
        SELECT 
            tr.flame_height_mm,
            tr.melt_pool_mm_at_2h,
            (tr.flame_height_mm - tr.melt_pool_mm_at_2h) as flame_melt_diff
        FROM test_results tr
        JOIN assemblies a ON tr.assembly_id = a.id
        WHERE a.fragrance_oil_id = fragrance_id
        AND tr.pass = TRUE
        AND tr.flame_height_mm IS NOT NULL
        AND tr.melt_pool_mm_at_2h IS NOT NULL
    ),
    stats AS (
        SELECT 
            AVG(flame_melt_diff) as avg_diff,
            STDDEV(flame_melt_diff) as std_diff
        FROM fragrance_tests
    )
    SELECT 
        CASE 
            WHEN COUNT(*) < 5 THEN NULL -- Not enough data
            ELSE (AVG(ft.flame_melt_diff) - s.avg_diff) / NULLIF(s.std_diff, 0)
        END INTO heat_index
    FROM fragrance_tests ft, stats s
    GROUP BY s.avg_diff, s.std_diff;
    
    RETURN COALESCE(heat_index, 0);
END;
$$ LANGUAGE plpgsql;

-- Create function to get wick size delta for wax conversion
CREATE OR REPLACE FUNCTION get_wax_conversion_delta(
    p_vessel_id VARCHAR(50),
    p_old_wax_id VARCHAR(50),
    p_new_wax_id VARCHAR(50)
) RETURNS INTEGER AS $$
DECLARE
    delta INTEGER;
BEGIN
    SELECT wick_size_delta INTO delta
    FROM wax_conversion_deltas
    WHERE vessel_id = p_vessel_id
    AND old_wax_type_id = p_old_wax_id
    AND new_wax_type_id = p_new_wax_id;
    
    RETURN COALESCE(delta, 0);
END;
$$ LANGUAGE plpgsql;

-- Trigger to update heat index when new test results are added
CREATE OR REPLACE FUNCTION update_fragrance_heat_index()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE fragrance_oils
    SET heat_index = calculate_fragrance_heat_index(
        (SELECT fragrance_oil_id FROM assemblies WHERE id = NEW.assembly_id)
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = (SELECT fragrance_oil_id FROM assemblies WHERE id = NEW.assembly_id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_heat_index
AFTER INSERT ON test_results
FOR EACH ROW
EXECUTE FUNCTION update_fragrance_heat_index();

-- Trigger to update wax conversion deltas
CREATE OR REPLACE FUNCTION update_wax_conversion_delta()
RETURNS TRIGGER AS $$
DECLARE
    old_wick_size INTEGER;
    new_wick_size INTEGER;
    size_delta INTEGER;
BEGIN
    IF NEW.test_type = 'wax_conversion' AND NEW.pass = TRUE THEN
        -- Get the original wick size for this assembly
        SELECT w.size_index INTO old_wick_size
        FROM assemblies a
        JOIN wicks w ON a.wick_id_1 = w.id
        WHERE a.id = NEW.assembly_id;
        
        -- Get the tested wick size
        SELECT size_index INTO new_wick_size
        FROM wicks
        WHERE id = NEW.wick_id_tested;
        
        size_delta := new_wick_size - old_wick_size;
        
        -- Update or insert the delta
        INSERT INTO wax_conversion_deltas (
            vessel_id,
            old_wax_type_id,
            new_wax_type_id,
            wick_size_delta,
            sample_count
        )
        SELECT 
            a.vessel_id,
            a.wax_type_id,
            NEW.wax_type_id_tested,
            size_delta,
            1
        FROM assemblies a
        WHERE a.id = NEW.assembly_id
        ON CONFLICT (vessel_id, old_wax_type_id, new_wax_type_id) DO UPDATE
        SET 
            wick_size_delta = (
                wax_conversion_deltas.wick_size_delta * wax_conversion_deltas.sample_count + EXCLUDED.wick_size_delta
            ) / (wax_conversion_deltas.sample_count + 1),
            sample_count = wax_conversion_deltas.sample_count + 1,
            confidence_score = LEAST(0.95, 0.5 + (wax_conversion_deltas.sample_count * 0.1)),
            updated_at = CURRENT_TIMESTAMP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_wax_conversion
AFTER INSERT ON test_results
FOR EACH ROW
EXECUTE FUNCTION update_wax_conversion_delta();