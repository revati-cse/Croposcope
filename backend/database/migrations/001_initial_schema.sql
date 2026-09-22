-- Initial database schema migration
-- Run this after creating the database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar VARCHAR(200),
    preferences TEXT, -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0
);

-- Trigger for updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Crop analyses table
CREATE TABLE IF NOT EXISTS crop_analyses (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    image_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255),
    crop_type VARCHAR(100) NOT NULL,
    disease_detected VARCHAR(200) NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    severity_level VARCHAR(10) CHECK (severity_level IN ('low', 'medium', 'high')) NOT NULL,
    field_location VARCHAR(200),
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    treatment_applied BOOLEAN DEFAULT FALSE,
    notes TEXT,
    model_version VARCHAR(50) DEFAULT 'efficientnetv2-1.0',
    processing_time FLOAT,
    image_width INTEGER,
    image_height INTEGER,
    file_size_bytes INTEGER,
    weather_conditions TEXT, -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_crop_analyses_updated_at 
    BEFORE UPDATE ON crop_analyses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Analysis metadata table for additional information
CREATE TABLE IF NOT EXISTS analysis_metadata (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES crop_analyses(id) ON DELETE CASCADE,
    camera_info TEXT, -- JSON string with camera details
    preprocessing_applied TEXT, -- JSON array of preprocessing steps
    alternative_predictions TEXT, -- JSON array of alternative predictions
    environmental_data TEXT, -- JSON object with environmental conditions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Treatments table
CREATE TABLE IF NOT EXISTS treatments (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    disease_target VARCHAR(200) NOT NULL,
    crop_target VARCHAR(200) NOT NULL,
    treatment_type VARCHAR(20) CHECK (treatment_type IN ('organic', 'biological', 'cultural', 'preventive')) NOT NULL,
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 0 AND effectiveness_rating <= 100),
    duration VARCHAR(100),
    difficulty_level VARCHAR(10) CHECK (difficulty_level IN ('easy', 'medium', 'hard')) NOT NULL,
    ingredients TEXT, -- JSON array
    instructions TEXT, -- JSON array
    benefits TEXT, -- JSON array
    precautions TEXT, -- JSON array
    cost_level VARCHAR(10) CHECK (cost_level IN ('low', 'medium', 'high')) NOT NULL,
    seasonal_info TEXT, -- JSON array
    success_rate FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TRIGGER update_treatments_updated_at 
    BEFORE UPDATE ON treatments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Treatment applications table (tracks when treatments are applied)
CREATE TABLE IF NOT EXISTS treatment_applications (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES crop_analyses(id) ON DELETE CASCADE,
    treatment_id INTEGER REFERENCES treatments(id) ON DELETE CASCADE,
    application_date DATE NOT NULL,
    dosage_amount VARCHAR(100),
    application_method VARCHAR(100),
    weather_conditions VARCHAR(200),
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 5),
    notes TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    cost_incurred DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_treatment_applications_updated_at 
    BEFORE UPDATE ON treatment_applications 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Voice interactions table
CREATE TABLE IF NOT EXISTS voice_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID DEFAULT uuid_generate_v4(),
    transcript TEXT NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    command_type VARCHAR(100),
    response_text TEXT,
    confidence_score FLOAT,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fields table (farm/field management)
CREATE TABLE IF NOT EXISTS fields (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    location VARCHAR(500),
    gps_coordinates POINT, -- PostGIS point type for precise coordinates
    size_acres DECIMAL(10, 3),
    soil_type VARCHAR(100),
    irrigation_type VARCHAR(100),
    current_crop VARCHAR(100),
    planting_date DATE,
    expected_harvest DATE,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_fields_updated_at 
    BEFORE UPDATE ON fields 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Crop history table (track crop rotation and history)
CREATE TABLE IF NOT EXISTS crop_history (
    id SERIAL PRIMARY KEY,
    field_id INTEGER REFERENCES fields(id) ON DELETE CASCADE,
    crop_name VARCHAR(100) NOT NULL,
    variety VARCHAR(100),
    planting_date DATE NOT NULL,
    harvest_date DATE,
    yield_amount DECIMAL(10, 3),
    yield_unit VARCHAR(20),
    notes TEXT,
    season VARCHAR(20),
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Disease library table (comprehensive disease information)
CREATE TABLE IF NOT EXISTS diseases (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    name VARCHAR(200) NOT NULL UNIQUE,
    common_names TEXT, -- JSON array of common names
    scientific_name VARCHAR(200),
    disease_type VARCHAR(20) CHECK (disease_type IN ('fungal', 'bacterial', 'viral', 'pest', 'nutritional', 'environmental')) NOT NULL,
    pathogen_name VARCHAR(200),
    affected_crops TEXT, -- JSON array
    symptoms TEXT, -- JSON array
    causes TEXT, -- JSON array
    organic_treatments TEXT, -- JSON array of treatment IDs
    prevention_methods TEXT, -- JSON array
    environmental_conditions TEXT, -- JSON object
    severity_factors TEXT, -- JSON array
    economic_impact VARCHAR(50),
    geographical_distribution TEXT, -- JSON array of regions
    images TEXT, -- JSON array of image URLs
    research_links TEXT, -- JSON array of research paper URLs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TRIGGER update_diseases_updated_at 
    BEFORE UPDATE ON diseases 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Weather data table (for correlation with disease outbreaks)
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    location VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    temperature_max DECIMAL(5, 2),
    temperature_min DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    rainfall DECIMAL(8, 2),
    wind_speed DECIMAL(6, 2),
    pressure DECIMAL(7, 2),
    conditions VARCHAR(100),
    data_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(location, date)
);

-- User sessions table (track user activity)
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info', -- info, warning, success, error
    category VARCHAR(50), -- treatment_reminder, disease_alert, etc.
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(500),
    metadata TEXT, -- JSON object for additional data
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System logs table