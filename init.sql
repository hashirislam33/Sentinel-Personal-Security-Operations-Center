-- Sentinel Database Initialization Script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types (if not created by SQLAlchemy)
DO $$ BEGIN
    CREATE TYPE alert_status AS ENUM ('new', 'acknowledged', 'in_progress', 'resolved', 'closed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE incident_status AS ENUM ('open', 'contained', 'resolved', 'closed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM ('informational', 'low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'analyst', 'viewer', 'agent');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create default admin user (password: sentinel-admin)
-- Password hash is for 'sentinel-admin' using bcrypt
INSERT INTO users (id, username, email, password_hash, role, is_active)
VALUES (
    uuid_generate_v4(),
    'admin',
    'admin@localhost',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu',
    'admin',
    true
)
ON CONFLICT (username) DO NOTHING;

-- Create sample detection rules
INSERT INTO detection_rules (
    id, rule_id, name, description, category, severity, enabled,
    conditions, threshold, time_window_seconds, group_by_fields,
    mitre_attack_ids, response_recommendation
) VALUES
(
    uuid_generate_v4(),
    'SSH-BRUTE-001',
    'SSH Brute Force Attempt',
    'Detects multiple failed SSH authentication attempts from a single source',
    'authentication',
    'high',
    true,
    '[{"field": "event_type", "operator": "equals", "value": "authentication_failure"}, {"field": "application", "operator": "equals", "value": "sshd"}]',
    5,
    60,
    '["source_ip"]',
    '["T1110"]',
    'Block source IP at firewall, investigate affected accounts'
),
(
    uuid_generate_v4(),
    'AUTH-MULTI-001',
    'Multiple Authentication Failures',
    'Detects authentication failures across multiple services',
    'authentication',
    'medium',
    true,
    '[{"field": "event_type", "operator": "equals", "value": "authentication_failure"}]',
    10,
    300,
    '["source_ip", "username"]',
    '["T1110.001"]',
    'Review authentication logs and verify user activity'
),
(
    uuid_generate_v4(),
    'PRIV-ESC-001',
    'Privilege Escalation Attempt',
    'Detects potential privilege escalation activities',
    'process',
    'critical',
    true,
    '[{"field": "category", "operator": "equals", "value": "process"}, {"field": "outcome", "operator": "contains", "value": "privilege"}]',
    1,
    60,
    '["username", "source_hostname"]',
    '["T1068"]',
    'Immediately investigate host and user activity'
),
(
    uuid_generate_v4(),
    'WEB-SCAN-001',
    'Web Application Scanning',
    'Detects web application scanning or reconnaissance',
    'network',
    'medium',
    true,
    '[{"field": "category", "operator": "equals", "value": "http_request"}, {"field": "action", "operator": "equals", "value": "denied"}]',
    20,
    60,
    '["source_ip"]',
    '["T1190"]',
    'Review web server logs and consider blocking source IP'
);

-- Create sample assets
INSERT INTO assets (
    id, hostname, type, os, ip_addresses, status, criticality, tags
) VALUES
(
    uuid_generate_v4(),
    'web-server-01',
    'server',
    'Ubuntu 22.04',
    '["192.168.1.10"]',
    'active',
    'high',
    '["production", "web"]'
),
(
    uuid_generate_v4(),
    'db-server-01',
    'server',
    'Ubuntu 22.04',
    '["192.168.1.20"]',
    'active',
    'critical',
    '["production", "database"]'
),
(
    uuid_generate_v4(),
    'dev-workstation-01',
    'workstation',
    'Windows 11',
    '["192.168.1.100"]',
    'active',
    'low',
    '["development"]'
)
ON CONFLICT DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_source_ip ON events(source_ip);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sentinel;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sentinel;
