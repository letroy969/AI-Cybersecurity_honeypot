-- AI Cybersecurity Honeypot Database Initialization
-- This script sets up the database schema and initial data

-- Create database if it doesn't exist (handled by Docker)
-- CREATE DATABASE IF NOT EXISTS honeypot_db;

-- Use the database
\c honeypot_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE attack_type AS ENUM (
        'sql_injection', 'xss', 'csrf', 'brute_force', 'ddos', 
        'port_scan', 'vulnerability_scan', 'malware', 'phishing',
        'privilege_escalation', 'data_exfiltration', 'unknown'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE alert_status AS ENUM ('open', 'investigating', 'resolved', 'false_positive');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for performance (will be created by SQLAlchemy models)
-- These are here for reference and can be used for manual optimization

-- Function to update last_seen timestamp
CREATE OR REPLACE FUNCTION update_last_seen()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_seen = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to generate request IDs
CREATE OR REPLACE FUNCTION generate_request_id()
RETURNS TEXT AS $$
BEGIN
    RETURN 'req_' || extract(epoch from now())::text || '_' || substring(md5(random()::text) from 1 for 8);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate risk score
CREATE OR REPLACE FUNCTION calculate_risk_score(
    attack_count INTEGER,
    unique_endpoints INTEGER,
    session_duration FLOAT,
    severity_weights JSONB
) RETURNS FLOAT AS $$
DECLARE
    base_score FLOAT := 0.0;
    severity_multiplier FLOAT := 1.0;
BEGIN
    -- Base score from attack count
    base_score := LEAST(attack_count * 10, 50);
    
    -- Endpoint diversity bonus
    base_score := base_score + (unique_endpoints * 2);
    
    -- Session duration factor
    IF session_duration > 3600 THEN  -- More than 1 hour
        base_score := base_score * 1.2;
    END IF;
    
    -- Apply severity weights if provided
    IF severity_weights IS NOT NULL THEN
        IF (severity_weights->>'high')::FLOAT > 0 THEN
            severity_multiplier := severity_multiplier * 1.5;
        END IF;
        IF (severity_weights->>'critical')::FLOAT > 0 THEN
            severity_multiplier := severity_multiplier * 2.0;
        END IF;
    END IF;
    
    RETURN LEAST(base_score * severity_multiplier, 100.0);
END;
$$ LANGUAGE plpgsql;

-- Create a view for attack statistics
CREATE OR REPLACE VIEW attack_statistics AS
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    source_ip,
    COUNT(*) as attack_count,
    COUNT(DISTINCT endpoint) as unique_endpoints,
    COUNT(DISTINCT attack_type) as attack_types,
    AVG(anomaly_score) as avg_anomaly_score,
    MAX(severity) as max_severity,
    array_agg(DISTINCT attack_type) as attack_types_list
FROM attack_events 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp), source_ip
ORDER BY hour DESC, attack_count DESC;

-- Create a view for threat intelligence
CREATE OR REPLACE VIEW threat_intelligence AS
SELECT 
    af.source_ip,
    af.first_seen,
    af.last_seen,
    af.total_requests,
    af.unique_endpoints,
    af.risk_score,
    af.threat_level,
    af.is_bot,
    array_agg(DISTINCT ae.attack_type) as attack_types,
    array_agg(DISTINCT ae.country) as countries,
    COUNT(CASE WHEN ae.severity = 'critical' THEN 1 END) as critical_attacks,
    COUNT(CASE WHEN ae.severity = 'high' THEN 1 END) as high_attacks,
    MAX(ae.timestamp) as last_attack_time
FROM attacker_fingerprints af
LEFT JOIN attack_events ae ON af.source_ip = ae.source_ip
GROUP BY af.id, af.source_ip, af.first_seen, af.last_seen, 
         af.total_requests, af.unique_endpoints, af.risk_score, 
         af.threat_level, af.is_bot
ORDER BY af.risk_score DESC, af.last_seen DESC;

-- Create a view for real-time alerts
CREATE OR REPLACE VIEW real_time_alerts AS
SELECT 
    sa.id,
    sa.alert_id,
    sa.timestamp,
    sa.alert_type,
    sa.severity,
    sa.title,
    sa.description,
    sa.source_ip,
    sa.affected_endpoint,
    sa.confidence,
    sa.status,
    ae.attack_type,
    ae.anomaly_score
FROM security_alerts sa
LEFT JOIN attack_events ae ON ae.id = ANY(sa.attack_event_ids)
WHERE sa.status IN ('open', 'investigating')
ORDER BY sa.timestamp DESC;

-- Insert initial system configuration
INSERT INTO system_metrics (
    timestamp,
    cpu_usage,
    memory_usage,
    disk_usage,
    requests_per_second,
    average_response_time,
    error_rate,
    active_connections,
    attacks_detected,
    anomalies_found,
    false_positives,
    model_predictions,
    model_accuracy
) VALUES (
    NOW(),
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0,
    0,
    0,
    0,
    0,
    0.0
) ON CONFLICT DO NOTHING;

-- Create audit log entry for database initialization
INSERT INTO audit_logs (
    timestamp,
    action,
    resource,
    success,
    metadata
) VALUES (
    NOW(),
    'database_init',
    'honeypot_db',
    true,
    '{"version": "1.0.0", "initialized_by": "system"}'
) ON CONFLICT DO NOTHING;

-- Grant permissions (adjust as needed for your security requirements)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO honeypot_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO honeypot_user;

COMMENT ON DATABASE honeypot_db IS 'AI Cybersecurity Honeypot Database - Educational Use Only';
COMMENT ON SCHEMA public IS 'Main schema for honeypot application data';
