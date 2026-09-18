# Sentinel API Documentation

## Overview

Sentinel provides a RESTful API for all platform functionality. The API is designed to be intuitive, consistent, and well-documented.

**Base URL**: `http://localhost:8000/api/v1`

**OpenAPI/Swagger**: Available at `http://localhost:8000/docs`

## Authentication

### User Authentication

Most endpoints require authentication using JWT tokens.

**Login:**
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "sentinel-admin"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Token Refresh:**
```bash
POST /auth/refresh
Content-Type: application/json
Authorization: Bearer {refresh_token}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

### Agent Authentication

Agents use API keys for authentication:

```bash
POST /api/v1/events
X-API-Key: agent-api-key-here
Content-Type: application/json

{
  "events": [...]
}
```

## Endpoints

### Authentication

#### POST `/auth/login`
Authenticate user and receive access tokens.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST `/auth/refresh`
Refresh access token using refresh token.

#### POST `/auth/logout`
Invalidate current session.

#### GET `/auth/me`
Get current user information.

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "role": "admin|analyst|viewer",
  "created_at": "ISO8601",
  "last_login": "ISO8601"
}
```

### Events

#### POST `/events`
Submit security events (agent authentication required).

**Request:**
```json
{
  "events": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "source": {
        "ip": "192.168.1.100",
        "hostname": "web-server-01"
      },
      "event_type": "authentication_failure",
      "user": {
        "username": "admin"
      },
      "application": "sshd",
      "raw_event": "Failed password for admin from 192.168.1.100"
    }
  ]
}
```

**Response:**
```json
{
  "accepted": 1,
  "rejected": 0,
  "event_ids": ["uuid"]
}
```

#### GET `/events`
Query security events with filters.

**Query Parameters:**
- `start_time`: ISO8601 timestamp
- `end_time`: ISO8601 timestamp
- `source_ip`: Filter by source IP
- `event_type`: Filter by event type
- `severity`: Filter by severity
- `limit`: Max results (default: 100, max: 1000)
- `offset`: Pagination offset

**Response:**
```json
{
  "total": 1234,
  "limit": 100,
  "offset": 0,
  "events": [
    {
      "event_id": "uuid",
      "timestamp": "ISO8601",
      "category": "authentication",
      "type": "authentication_failure",
      "severity": "medium",
      "source": {...},
      "destination": {...},
      "user": {...},
      "raw_event": "string"
    }
  ]
}
```

#### GET `/events/{event_id}`
Get single event by ID.

### Alerts

#### GET `/alerts`
List alerts with filters.

**Query Parameters:**
- `status`: new|acknowledged|in_progress|resolved|closed
- `severity`: informational|low|medium|high|critical
- `rule_id`: Filter by detection rule
- `assigned_to`: Filter by assignee
- `start_time`: ISO8601 timestamp
- `end_time`: ISO8601 timestamp
- `limit`: Max results
- `offset`: Pagination offset

**Response:**
```json
{
  "total": 50,
  "alerts": [
    {
      "alert_id": "uuid",
      "title": "SSH Brute Force Attempt",
      "description": "Multiple failed SSH authentication attempts detected",
      "severity": "high",
      "risk_score": 75,
      "status": "new",
      "rule_id": "SSH-BRUTE-001",
      "created_at": "ISO8601",
      "updated_at": "ISO8601",
      "assigned_to": null,
      "affected_assets": ["uuid"],
      "source_ip": "192.168.1.100"
    }
  ]
}
```

#### GET `/alerts/{alert_id}`
Get alert details.

**Response:**
```json
{
  "alert_id": "uuid",
  "title": "string",
  "description": "string",
  "severity": "high",
  "risk_score": 75,
  "confidence": 0.85,
  "status": "new",
  "rule": {...},
  "supporting_events": [...],
  "timeline": [...],
  "notes": [],
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

#### PATCH `/alerts/{alert_id}`
Update alert status or assignment.

**Request:**
```json
{
  "status": "acknowledged",
  "assigned_to": "uuid"
}
```

#### POST `/alerts/{alert_id}/notes`
Add investigation note to alert.

**Request:**
```json
{
  "content": "Investigating suspicious activity",
  "is_private": false
}
```

### Incidents

#### GET `/incidents`
List incidents.

**Query Parameters:**
- `status`: open|contained|resolved|closed
- `severity`: low|medium|high|critical
- `limit`: Max results
- `offset`: Pagination offset

**Response:**
```json
{
  "total": 10,
  "incidents": [
    {
      "incident_id": "uuid",
      "title": "Possible Account Compromise",
      "severity": "critical",
      "status": "open",
      "created_at": "ISO8601",
      "alert_count": 5,
      "affected_assets": 2
    }
  ]
}
```

#### GET `/incidents/{incident_id}`
Get incident details.

**Response:**
```json
{
  "incident_id": "uuid",
  "title": "string",
  "description": "string",
  "severity": "critical",
  "status": "open",
  "timeline": [
    {
      "timestamp": "ISO8601",
      "event_type": "alert_created",
      "description": "Alert created",
      "user": "system"
    }
  ],
  "related_alerts": [...],
  "affected_assets": [...],
  "involved_accounts": [...],
  "evidence": [...],
  "notes": [],
  "response_actions": []
}
```

#### POST `/incidents`
Create new incident.

**Request:**
```json
{
  "title": "string",
  "description": "string",
  "severity": "high",
  "related_alerts": ["uuid", "uuid"]
}
```

#### PATCH `/incidents/{incident_id}`
Update incident.

#### POST `/incidents/{incident_id}/response-actions`
Record response action taken.

**Request:**
```json
{
  "action_type": "containment|eradication|recovery",
  "description": "Isolated affected host",
  "automated": false
}
```

### Assets

#### GET `/assets`
List monitored assets.

**Query Parameters:**
- `type`: server|workstation|container|network_device
- `status`: active|inactive|maintenance
- `tag`: Filter by tag
- `limit`: Max results

**Response:**
```json
{
  "total": 25,
  "assets": [
    {
      "asset_id": "uuid",
      "hostname": "web-server-01",
      "type": "server",
      "os": "Ubuntu 22.04",
      "ip_addresses": ["192.168.1.10"],
      "status": "active",
      "agent_version": "1.0.0",
      "last_seen": "ISO8601",
      "tags": ["production", "web"],
      "criticality": "high"
    }
  ]
}
```

#### GET `/assets/{asset_id}`
Get asset details.

#### POST `/assets`
Register new asset.

**Request:**
```json
{
  "hostname": "string",
  "type": "server",
  "os": "string",
  "ip_addresses": ["192.168.1.10"],
  "tags": ["production"],
  "criticality": "high"
}
```

#### PUT `/assets/{asset_id}`
Update asset information.

#### DELETE `/assets/{asset_id}`
Remove asset.

### Detection Rules

#### GET `/rules`
List detection rules.

**Query Parameters:**
- `category`: Filter by category
- `severity`: Filter by severity
- `enabled`: true|false
- `limit`: Max results

**Response:**
```json
{
  "total": 15,
  "rules": [
    {
      "rule_id": "SSH-BRUTE-001",
      "name": "SSH Brute Force Attempt",
      "description": "Detects multiple failed SSH authentication attempts",
      "category": "authentication",
      "severity": "high",
      "enabled": true,
      "threshold": 5,
      "time_window": "1m",
      "mitre_attack": ["T1110"],
      "triggered_count": 42
    }
  ]
}
```

#### GET `/rules/{rule_id}`
Get rule details.

#### POST `/rules`
Create new detection rule.

**Request:**
```json
{
  "rule_id": "CUSTOM-001",
  "name": "string",
  "description": "string",
  "category": "string",
  "severity": "high",
  "conditions": [
    {
      "field": "event.type",
      "operator": "equals",
      "value": "authentication_failure"
    }
  ],
  "threshold": 5,
  "time_window": "1m",
  "group_by": ["source.ip"]
}
```

#### PUT `/rules/{rule_id}`
Update rule.

#### DELETE `/rules/{rule_id}`
Delete rule.

#### POST `/rules/{rule_id}/test`
Test rule against historical data.

**Request:**
```json
{
  "start_time": "ISO8601",
  "end_time": "ISO8601"
}
```

**Response:**
```json
{
  "matches": 15,
  "sample_events": [...]
}
```

### Dashboard

#### GET `/dashboard/metrics`
Get dashboard metrics.

**Response:**
```json
{
  "events_total": 125000,
  "events_per_second": 45.2,
  "alerts_active": 23,
  "alerts_by_severity": {
    "critical": 2,
    "high": 5,
    "medium": 10,
    "low": 6
  },
  "incidents_open": 5,
  "failed_auth_24h": 150,
  "unique_sources_24h": 45,
  "monitored_assets": 25,
  "top_rules_triggered": [
    {
      "rule_id": "SSH-BRUTE-001",
      "count": 42
    }
  ]
}
```

#### GET `/dashboard/events-over-time`
Get event volume over time.

**Query Parameters:**
- `interval`: hour|day|week
- `duration`: Number of intervals

#### GET `/dashboard/alerts-over-time`
Get alert trends.

### Users (Admin Only)

#### GET `/users`
List all users.

#### GET `/users/{user_id}`
Get user details.

#### POST `/users`
Create new user.

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "analyst"
}
```

#### PUT `/users/{user_id}`
Update user.

#### DELETE `/users/{user_id}`
Delete user.

### Audit Logs (Admin Only)

#### GET `/audit`
Query audit logs.

**Query Parameters:**
- `user_id`: Filter by user
- `action`: Filter by action type
- `start_time`: ISO8601 timestamp
- `end_time`: ISO8601 timestamp
- `limit`: Max results

**Response:**
```json
{
  "total": 500,
  "logs": [
    {
      "audit_id": "uuid",
      "timestamp": "ISO8601",
      "user_id": "uuid",
      "action": "alert_status_change",
      "resource_type": "alert",
      "resource_id": "uuid",
      "details": {...},
      "ip_address": "192.168.1.50"
    }
  ]
}
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limiting

- **User endpoints**: 100 requests/minute per user
- **Agent endpoints**: 1000 events/minute per API key
- **Public endpoints**: 10 requests/minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

## Pagination

List endpoints support pagination:

**Request:**
```
GET /api/v1/alerts?limit=50&offset=0
```

**Response:**
```json
{
  "total": 250,
  "limit": 50,
  "offset": 0,
  "has_more": true,
  "data": [...]
}
```

## Versioning

API version is included in the URL path: `/api/v1/`

Future versions will be: `/api/v2/`, etc.

Deprecated endpoints will be marked in documentation for at least one version cycle before removal.

## Examples

### Complete Alert Investigation Workflow

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"sentinel-admin"}' \
  | jq -r '.access_token')

# 2. Get high severity alerts
curl -X GET "http://localhost:8000/api/v1/alerts?severity=high&status=new" \
  -H "Authorization: Bearer $TOKEN"

# 3. Get alert details
curl -X GET "http://localhost:8000/api/v1/alerts/{alert_id}" \
  -H "Authorization: Bearer $TOKEN"

# 4. Acknowledge alert
curl -X PATCH "http://localhost:8000/api/v1/alerts/{alert_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"acknowledged"}'

# 5. Add investigation note
curl -X POST "http://localhost:8000/api/v1/alerts/{alert_id}/notes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Investigating suspicious login pattern"}'

# 6. Query related events
curl -X GET "http://localhost:8000/api/v1/events?source_ip=192.168.1.100" \
  -H "Authorization: Bearer $TOKEN"

# 7. Create incident if warranted
curl -X POST "http://localhost:8000/api/v1/incidents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Possible Account Compromise",
    "severity": "critical",
    "related_alerts": ["alert-uuid-1", "alert-uuid-2"]
  }'
```

---

For interactive API testing, visit: `http://localhost:8000/docs`
