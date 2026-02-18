-- Marine Safety Incidents Database - SQLite Schema
-- Version: 1.0.0
-- Date: 2025-10-03
-- Purpose: Development and testing environment database schema

-- Enable foreign key support (must be enabled for each connection)
PRAGMA foreign_keys = ON;

-- ============================================================================
-- REFERENCE TABLES
-- ============================================================================

-- Incident Types Reference Table
CREATE TABLE incident_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT UNIQUE NOT NULL,
    category TEXT,
    severity_weight REAL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data Sources Reference Table
CREATE TABLE data_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    source_agency TEXT,
    source_url TEXT,
    data_format TEXT,
    update_frequency TEXT,
    last_scraped TIMESTAMP,
    records_count INTEGER DEFAULT 0,
    active_status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Geographic Locations Reference Table
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT,
    location_type TEXT, -- 'port', 'waterway', 'offshore_field', 'region'
    country_code TEXT,
    latitude REAL,
    longitude REAL,
    water_body TEXT,
    jurisdiction TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on coordinates for location lookups
CREATE INDEX idx_locations_coords ON locations(latitude, longitude);
CREATE INDEX idx_locations_type ON locations(location_type);

-- ============================================================================
-- ENTITY TABLES
-- ============================================================================

-- Companies (Vessel owners, operators, facility operators)
CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    company_type TEXT, -- 'operator', 'owner', 'charterer', 'manager'
    country_code TEXT,
    industry_sector TEXT,
    active_status INTEGER DEFAULT 1,
    safety_record_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for companies
CREATE INDEX idx_companies_name ON companies(company_name);
CREATE INDEX idx_companies_type ON companies(company_type);
CREATE INDEX idx_companies_country ON companies(country_code);

-- Vessels
CREATE TABLE vessels (
    vessel_id TEXT PRIMARY KEY,
    vessel_name TEXT,
    imo_number TEXT UNIQUE,
    vessel_type TEXT,
    vessel_subtype TEXT,
    flag_country TEXT,
    built_year INTEGER,
    gross_tonnage INTEGER,
    length_meters REAL,
    beam_meters REAL,
    engine_type TEXT,
    classification_society TEXT,
    owner_name TEXT,
    operator_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for vessels
CREATE INDEX idx_vessels_type ON vessels(vessel_type);
CREATE INDEX idx_vessels_flag ON vessels(flag_country);
CREATE INDEX idx_vessels_imo ON vessels(imo_number);
CREATE INDEX idx_vessels_name ON vessels(vessel_name);

-- ============================================================================
-- INCIDENTS TABLE (Primary Table)
-- ============================================================================

CREATE TABLE incidents (
    -- Primary Key
    incident_id TEXT PRIMARY KEY,

    -- Temporal Data
    incident_date TEXT NOT NULL, -- ISO 8601 format: YYYY-MM-DD
    incident_time TEXT, -- ISO 8601 format: HH:MM:SS
    report_date TEXT, -- ISO 8601 format: YYYY-MM-DD

    -- Location Data
    latitude REAL,
    longitude REAL,
    location_description TEXT,
    country_code TEXT,
    state_province TEXT,
    water_body TEXT,
    port_name TEXT,

    -- Incident Classification
    incident_type TEXT NOT NULL,
    incident_subtype TEXT,
    severity_level TEXT,
    incident_category TEXT,

    -- Outcomes
    fatalities INTEGER DEFAULT 0,
    injuries INTEGER DEFAULT 0,
    missing_persons INTEGER DEFAULT 0,
    property_damage_usd REAL,
    vessel_total_loss INTEGER DEFAULT 0, -- 0 = false, 1 = true

    -- Environmental Impact
    environmental_impact INTEGER DEFAULT 0, -- 0 = false, 1 = true
    oil_spill_volume_gallons REAL,
    chemical_spill INTEGER DEFAULT 0, -- 0 = false, 1 = true
    wildlife_impact TEXT,

    -- Weather & Conditions
    weather_conditions TEXT,
    sea_state TEXT,
    visibility TEXT,
    wind_speed_knots INTEGER,

    -- Investigation & Analysis
    root_cause TEXT,
    contributing_factors TEXT,
    investigation_status TEXT,
    regulatory_violations TEXT,
    corrective_actions TEXT,
    lessons_learned TEXT,

    -- Administrative
    reporting_agency TEXT,
    source_url TEXT,
    source_document_id TEXT,
    data_source_id INTEGER,
    data_quality_score REAL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (data_source_id) REFERENCES data_sources(source_id)
);

-- Create indexes for common queries on incidents
CREATE INDEX idx_incidents_date ON incidents(incident_date);
CREATE INDEX idx_incidents_location ON incidents(latitude, longitude);
CREATE INDEX idx_incidents_type ON incidents(incident_type);
CREATE INDEX idx_incidents_severity ON incidents(severity_level);
CREATE INDEX idx_incidents_country ON incidents(country_code);
CREATE INDEX idx_incidents_agency ON incidents(reporting_agency);
CREATE INDEX idx_incidents_fatalities ON incidents(fatalities);
CREATE INDEX idx_incidents_environmental ON incidents(environmental_impact);

-- ============================================================================
-- JUNCTION TABLES (Many-to-Many Relationships)
-- ============================================================================

-- Incident-Vessel Relationship
CREATE TABLE incident_vessels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL,
    vessel_id TEXT NOT NULL,
    vessel_role TEXT, -- 'primary', 'collision_partner', 'assisting', 'damaged'
    vessel_damage_level TEXT,
    vessel_position TEXT, -- 'at_fault', 'victim', 'neutral'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE,
    FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
);

-- Create indexes for junction table
CREATE INDEX idx_incident_vessels_incident ON incident_vessels(incident_id);
CREATE INDEX idx_incident_vessels_vessel ON incident_vessels(vessel_id);
CREATE UNIQUE INDEX idx_incident_vessels_unique ON incident_vessels(incident_id, vessel_id, vessel_role);

-- Incident-Company Relationship
CREATE TABLE incident_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL,
    company_id TEXT NOT NULL,
    company_role TEXT, -- 'vessel_owner', 'operator', 'charterer', 'facility_owner'
    responsibility_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- Create indexes for incident-companies junction
CREATE INDEX idx_incident_companies_incident ON incident_companies(incident_id);
CREATE INDEX idx_incident_companies_company ON incident_companies(company_id);
CREATE UNIQUE INDEX idx_incident_companies_unique ON incident_companies(incident_id, company_id, company_role);

-- ============================================================================
-- INVESTIGATION TABLES
-- ============================================================================

-- Investigations (Related to incidents)
CREATE TABLE investigations (
    investigation_id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    investigating_agency TEXT,
    investigation_type TEXT, -- 'preliminary', 'full', 'formal', 'criminal'
    start_date TEXT, -- ISO 8601 format
    completion_date TEXT, -- ISO 8601 format
    report_url TEXT,
    final_report_available INTEGER DEFAULT 0, -- 0 = false, 1 = true
    findings_summary TEXT,
    recommendations TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE
);

-- Create indexes for investigations
CREATE INDEX idx_investigations_incident ON investigations(incident_id);
CREATE INDEX idx_investigations_agency ON investigations(investigating_agency);
CREATE INDEX idx_investigations_status ON investigations(status);

-- ============================================================================
-- PERSONNEL TABLES
-- ============================================================================

-- Personnel (Crew, passengers, shore workers involved in incidents)
CREATE TABLE personnel (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL,
    person_role TEXT, -- 'captain', 'crew', 'passenger', 'pilot', 'shore_worker'
    outcome TEXT, -- 'uninjured', 'injured', 'fatal', 'missing'
    injury_severity TEXT,
    age_range TEXT,
    experience_years INTEGER,
    certification_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE
);

-- Create indexes for personnel
CREATE INDEX idx_personnel_incident ON personnel(incident_id);
CREATE INDEX idx_personnel_outcome ON personnel(outcome);
CREATE INDEX idx_personnel_role ON personnel(person_role);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Summary statistics view
CREATE VIEW IF NOT EXISTS incident_summary_stats AS
SELECT
    COUNT(*) as total_incidents,
    SUM(fatalities) as total_fatalities,
    SUM(injuries) as total_injuries,
    SUM(missing_persons) as total_missing,
    SUM(property_damage_usd) as total_property_damage,
    COUNT(CASE WHEN environmental_impact = 1 THEN 1 END) as environmental_incidents,
    COUNT(CASE WHEN vessel_total_loss = 1 THEN 1 END) as total_loss_incidents,
    MIN(incident_date) as earliest_incident,
    MAX(incident_date) as latest_incident
FROM incidents;

-- Incidents by type view
CREATE VIEW IF NOT EXISTS incidents_by_type AS
SELECT
    incident_type,
    incident_category,
    COUNT(*) as incident_count,
    SUM(fatalities) as total_fatalities,
    SUM(injuries) as total_injuries,
    AVG(data_quality_score) as avg_quality_score
FROM incidents
GROUP BY incident_type, incident_category
ORDER BY incident_count DESC;

-- Incidents by year view
CREATE VIEW IF NOT EXISTS incidents_by_year AS
SELECT
    SUBSTR(incident_date, 1, 4) as year,
    COUNT(*) as incident_count,
    SUM(fatalities) as total_fatalities,
    SUM(injuries) as total_injuries,
    SUM(property_damage_usd) as total_damage
FROM incidents
GROUP BY year
ORDER BY year;

-- High severity incidents view
CREATE VIEW IF NOT EXISTS high_severity_incidents AS
SELECT
    i.incident_id,
    i.incident_date,
    i.incident_type,
    i.severity_level,
    i.location_description,
    i.fatalities,
    i.injuries,
    i.property_damage_usd,
    i.environmental_impact
FROM incidents i
WHERE i.fatalities > 0
   OR i.injuries > 5
   OR i.environmental_impact = 1
   OR i.vessel_total_loss = 1
   OR i.severity_level IN ('Major', 'Catastrophic')
ORDER BY i.incident_date DESC;

-- Vessel incident history view
CREATE VIEW IF NOT EXISTS vessel_incident_history AS
SELECT
    v.vessel_id,
    v.vessel_name,
    v.imo_number,
    v.vessel_type,
    COUNT(iv.incident_id) as incident_count,
    SUM(CASE WHEN i.fatalities > 0 THEN 1 ELSE 0 END) as fatal_incidents,
    MIN(i.incident_date) as first_incident,
    MAX(i.incident_date) as latest_incident
FROM vessels v
LEFT JOIN incident_vessels iv ON v.vessel_id = iv.vessel_id
LEFT JOIN incidents i ON iv.incident_id = i.incident_id
GROUP BY v.vessel_id, v.vessel_name, v.imo_number, v.vessel_type;

-- Company safety record view
CREATE VIEW IF NOT EXISTS company_safety_records AS
SELECT
    c.company_id,
    c.company_name,
    c.company_type,
    COUNT(ic.incident_id) as incident_count,
    SUM(CASE WHEN i.fatalities > 0 THEN 1 ELSE 0 END) as fatal_incidents,
    SUM(i.fatalities) as total_fatalities,
    SUM(i.injuries) as total_injuries,
    AVG(i.data_quality_score) as avg_incident_quality
FROM companies c
LEFT JOIN incident_companies ic ON c.company_id = ic.company_id
LEFT JOIN incidents i ON ic.incident_id = i.incident_id
GROUP BY c.company_id, c.company_name, c.company_type;

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Update timestamp trigger for incidents
CREATE TRIGGER update_incidents_timestamp
AFTER UPDATE ON incidents
BEGIN
    UPDATE incidents SET last_updated = CURRENT_TIMESTAMP
    WHERE incident_id = NEW.incident_id;
END;

-- Update timestamp trigger for companies
CREATE TRIGGER update_companies_timestamp
AFTER UPDATE ON companies
BEGIN
    UPDATE companies SET updated_at = CURRENT_TIMESTAMP
    WHERE company_id = NEW.company_id;
END;

-- Update timestamp trigger for vessels
CREATE TRIGGER update_vessels_timestamp
AFTER UPDATE ON vessels
BEGIN
    UPDATE vessels SET updated_at = CURRENT_TIMESTAMP
    WHERE vessel_id = NEW.vessel_id;
END;

-- Update timestamp trigger for locations
CREATE TRIGGER update_locations_timestamp
AFTER UPDATE ON locations
BEGIN
    UPDATE locations SET updated_at = CURRENT_TIMESTAMP
    WHERE location_id = NEW.location_id;
END;

-- Update timestamp trigger for investigations
CREATE TRIGGER update_investigations_timestamp
AFTER UPDATE ON investigations
BEGIN
    UPDATE investigations SET updated_at = CURRENT_TIMESTAMP
    WHERE investigation_id = NEW.investigation_id;
END;

-- Update timestamp trigger for data_sources
CREATE TRIGGER update_data_sources_timestamp
AFTER UPDATE ON data_sources
BEGIN
    UPDATE data_sources SET updated_at = CURRENT_TIMESTAMP
    WHERE source_id = NEW.source_id;
END;

-- ============================================================================
-- SEED DATA FOR INCIDENT TYPES
-- ============================================================================

-- Insert common incident type categories
INSERT INTO incident_types (type_name, category, severity_weight, description) VALUES
-- Collision types
('Ship-to-Ship Collision', 'Collision', 0.85, 'Collision between two vessels'),
('Ship-to-Structure Collision', 'Collision', 0.80, 'Vessel collision with fixed structure'),
('Allision', 'Collision', 0.75, 'Moving vessel collision with stationary object'),

-- Grounding types
('Hard Grounding', 'Grounding', 0.75, 'Vessel runs aground with significant impact'),
('Soft Grounding', 'Grounding', 0.60, 'Vessel touches bottom in shallow water'),
('Stranding', 'Grounding', 0.70, 'Vessel becomes stuck on shore or reef'),

-- Fire/Explosion types
('Engine Room Fire', 'Fire/Explosion', 0.80, 'Fire originating in engine room'),
('Cargo Fire', 'Fire/Explosion', 0.85, 'Fire in cargo holds or deck cargo'),
('Accommodation Fire', 'Fire/Explosion', 0.75, 'Fire in crew/passenger accommodations'),
('Explosion', 'Fire/Explosion', 0.95, 'Explosive event on vessel or platform'),
('Blowout', 'Fire/Explosion', 0.95, 'Uncontrolled release from oil/gas well'),

-- Capsizing/Sinking types
('Capsizing', 'Capsizing/Sinking', 0.90, 'Vessel overturns'),
('Sinking', 'Capsizing/Sinking', 0.92, 'Vessel founders and sinks'),
('Flooding', 'Capsizing/Sinking', 0.75, 'Uncontrolled water ingress'),
('Stability Loss', 'Capsizing/Sinking', 0.80, 'Loss of vessel stability'),

-- Personnel Injury/Fatality types
('Fall Overboard', 'Personnel Injury/Fatality', 0.85, 'Person falls from vessel into water'),
('Slip/Trip/Fall', 'Personnel Injury/Fatality', 0.50, 'Fall on deck or in vessel'),
('Struck by Object', 'Personnel Injury/Fatality', 0.60, 'Person struck by moving or falling object'),
('Caught in Machinery', 'Personnel Injury/Fatality', 0.75, 'Person caught in mechanical equipment'),
('Exposure', 'Personnel Injury/Fatality', 0.70, 'Exposure to hazardous conditions or substances'),

-- Environmental types
('Oil Spill', 'Environmental', 0.80, 'Release of petroleum products into water'),
('Chemical Spill', 'Environmental', 0.85, 'Release of hazardous chemicals'),
('Hazmat Release', 'Environmental', 0.85, 'Release of hazardous materials'),
('Wildlife Impact', 'Environmental', 0.65, 'Collision or impact with marine wildlife'),

-- Equipment Failure types
('Main Engine Failure', 'Equipment Failure', 0.70, 'Failure of primary propulsion'),
('Auxiliary Systems Failure', 'Equipment Failure', 0.55, 'Failure of supporting systems'),
('Navigation Equipment Failure', 'Equipment Failure', 0.65, 'Failure of navigation systems'),
('Safety Equipment Failure', 'Equipment Failure', 0.75, 'Failure of safety systems'),
('Structural Failure', 'Equipment Failure', 0.85, 'Failure of vessel structure'),

-- Navigation Error types
('Wrong Course', 'Navigation Error', 0.60, 'Vessel on incorrect course'),
('Improper Lookout', 'Navigation Error', 0.65, 'Inadequate watch keeping'),
('Chart/GPS Error', 'Navigation Error', 0.70, 'Error in chart or GPS navigation'),

-- Weather-Related types
('Storm Damage', 'Weather-Related', 0.75, 'Damage from severe weather'),
('Hurricane/Typhoon', 'Weather-Related', 0.90, 'Damage from tropical cyclone'),
('Ice Damage', 'Weather-Related', 0.70, 'Damage from ice conditions'),
('Fog-Related', 'Weather-Related', 0.60, 'Incident in reduced visibility'),

-- Security/Piracy types
('Piracy Attack', 'Security/Piracy', 0.85, 'Armed attack on vessel'),
('Armed Robbery', 'Security/Piracy', 0.80, 'Robbery while in port or anchorage'),
('Terrorism', 'Security/Piracy', 0.95, 'Terrorist attack on vessel'),
('Stowaway', 'Security/Piracy', 0.30, 'Unauthorized person on board'),

-- Pollution types
('Illegal Discharge', 'Pollution', 0.60, 'Unauthorized discharge of pollutants'),
('Ballast Water Violation', 'Pollution', 0.50, 'Improper ballast water management'),
('Air Emissions', 'Pollution', 0.45, 'Excessive air emissions'),

-- Other types
('Towing Casualty', 'Other', 0.60, 'Incident during towing operations'),
('Mooring Failure', 'Other', 0.55, 'Failure of mooring system'),
('Loading/Unloading Incident', 'Other', 0.60, 'Incident during cargo operations'),
('Bunkering Incident', 'Other', 0.65, 'Incident during fuel transfer');

-- ============================================================================
-- SEED DATA FOR DATA SOURCES
-- ============================================================================

-- Insert primary data sources
INSERT INTO data_sources (source_name, source_agency, source_url, data_format, update_frequency, active_status) VALUES
('USCG Marine Casualty Reports', 'U.S. Coast Guard', 'https://www.dco.uscg.mil', 'PDF/Web', 'Daily', 1),
('NTSB Investigation Database', 'National Transportation Safety Board', 'https://www.ntsb.gov', 'API/Database', 'Daily', 1),
('BTS Waterborne Statistics', 'Bureau of Transportation Statistics', 'https://www.bts.gov', 'CSV/Excel', 'Annual', 1),
('USCG Boating Statistics', 'U.S. Coast Guard', 'https://uscgboating.org', 'PDF/Excel', 'Annual', 1),
('IMCA Safety Statistics', 'International Marine Contractors Association', 'https://www.imca-int.com', 'PDF/Web', 'Annual', 1),
('IMO Casualty Database', 'International Maritime Organization', 'https://www.imo.org', 'Database', 'Ongoing', 1),
('III Insurance Statistics', 'Insurance Information Institute', 'https://www.iii.org', 'Web/Reports', 'Annual', 1);

-- ============================================================================
-- OPTIMIZATION TIPS
-- ============================================================================

-- For better performance in SQLite:
-- 1. Use ANALYZE command periodically to update query optimizer statistics:
--    ANALYZE;
--
-- 2. Consider VACUUM to rebuild database and reclaim space:
--    VACUUM;
--
-- 3. Adjust cache size for large datasets (in KB):
--    PRAGMA cache_size = -64000; -- 64MB cache
--
-- 4. Use WAL mode for better concurrent read performance:
--    PRAGMA journal_mode = WAL;
--
-- 5. Disable synchronous for faster writes (less safe):
--    PRAGMA synchronous = NORMAL;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
