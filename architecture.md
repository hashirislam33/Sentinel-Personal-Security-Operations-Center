# Sentinel Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SENTINEL PLATFORM                                 │
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Sentinel   │    │   Syslog     │    │   File       │                   │
│  │    Agent     │    │   Collector  │    │   Upload     │                   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                            │
│         └───────────────────┼───────────────────┘                            │
│                             ▼                                                │
│                    ┌────────────────┐                                        │
│                    │  Ingestion API │                                        │
│                    │  (FastAPI)     │                                        │
│                    └───────┬────────┘                                        │
│                            │                                                 │
│                            ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EVENT PROCESSING PIPELINE                         │    │
│  │                                                                      │    │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                │    │
│  │  │ Validation  │ → │Normalization│ → │ Enrichment  │                │    │
│  │  └─────────────┘   └─────────────┘   └─────────────┘                │    │
│  │                                                                      │    │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                │    │
│  │  │  Detection  │ → │ Correlation │ → │ Risk Score  │                │    │
│  │  │   Engine    │   │   Engine    │   │   Engine    │                │    │
│  │  └─────────────┘   └─────────────┘   └─────────────┘                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                             │                                                │
│                             ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      DATA LAYER                                     │    │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                │    │
│  │  │   Events    │   │   Alerts    │   │  Incidents  │                │    │
│  │  │  (Time-     │   │             │   │             │                │    │
│  │  │  series)    │   │             │   │             │                │    │
│  │  └─────────────┘   └─────────────┘   └─────────────┘                │    │
│  │                                                                      │    │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                │    │
│  │  │   Assets    │   │    Users    │   │   Rules     │                │    │
│  │  │             │   │             │   │             │                │    │
│  │  └─────────────┘   └─────────────┘   └─────────────┘                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                             │                                                │
│                             ▼                                                │
│                    ┌────────────────┐                                        │
│                    │  PostgreSQL    │                                        │
│                    │   Database     │                                        │
│                    └───────┬────────┘                                        │
│                            │                                                 │
│  ┌─────────────────────────┼─────────────────────────┐                       │
│  │                         │                         │                       │
│  │                         ▼                         │                       │
│  │              ┌──────────────────┐                 │                       │
│  │              │   REST API       │                 │                       │
│  │              │   (FastAPI)      │                 │                       │
│  │              └────────┬─────────┘                 │                       │
│  │                       │                           │                       │
│  │         ┌─────────────┼─────────────┐             │                       │
│  │         │             │             │             │                       │
│  │         ▼             ▼             ▼             │                       │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │                       │
│  │  │ Dashboard│  │  Alerts  │  │Investiga-│        │                       │
│  │  │          │  │   &      │  │  tion    │        │                       │
│  │  │          │  │Incidents │  │Workspace │        │                       │
│  │  └──────────┘  └──────────┘  └──────────┘        │                       │
│  │                                                  │                       │
│  └──────────────────────────────────────────────────┘                       │
│                        React Frontend                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Collection Layer

**Sentinel Agent**
- Lightweight Python agent for host monitoring
- Collects: authentication events, process execution, file modifications, network connections
- Configurable collection policies (privacy-first design)
- Secure communication with Sentinel server
- Heartbeat and health monitoring

**Syslog Collector**
- UDP/TCP syslog listener
- Supports RFC 3164 and RFC 5424 formats
- Parses common log formats (auth.log, secure, syslog)

**File Upload**
- Web interface for log file uploads
- Supports compressed files (gzip, zip)
- Automatic format detection

**HTTP Event API**
- JSON-based event submission
- API key authentication
- Rate limiting and validation

### 2. Ingestion Service

**Responsibilities:**
- Authenticate event sources
- Validate event structure
- Attach metadata (source, timestamp, ingestion time)
- Assign unique event IDs
- Queue events for processing

**Event Schema (Raw):**
```json
{
  "event_id": "uuid",
  "source_type": "agent|syslog|file|api",
  "source_id": "string",
  "raw_event": "original log data",
  "ingested_at": "ISO8601 timestamp",
  "metadata": {}
}
```

### 3. Normalization Engine

**Purpose:** Convert diverse log formats into a common schema

**Normalized Event Schema:**
```json
{
  "event_id": "uuid",
  "timestamp": "ISO8601",
  "category": "authentication|network|process|file|config",
  "type": "specific event type",
  "severity": "info|low|medium|high|critical",
  "source": {
    "ip": "x.x.x.x",
    "port": 0,
    "hostname": "string",
    "mac": "xx:xx:xx:xx:xx:xx"
  },
  "destination": {
    "ip": "x.x.x.x",
    "port": 0,
    "hostname": "string"
  },
  "user": {
    "username": "string",
    "uid": "string"
  },
  "application": "string",
  "protocol": "string",
  "action": "allowed|denied|failed|success",
  "outcome": "string",
  "raw_event": "original data"
}
```

**Normalization Rules:**
- SSH authentication logs → `authentication` category
- Windows Event Logs → normalized fields
- Web server logs → `http_request` events
- Firewall logs → `network` category

### 4. Enrichment Service

**Enrichment Types:**
- **Asset Context**: Add hostname, OS, criticality from asset database
- **Geographic Information**: GeoIP lookup for external addresses
- **Threat Intelligence**: Check against known malicious indicators
- **Historical Context**: Previous activity from same source
- **User Context**: Role, department, privilege level

### 5. Detection Engine

**Rule-Based Detection:**
- Simple threshold rules (e.g., 5 failed logins in 1 minute)
- Pattern matching on event fields
- Time-window based aggregations
- Configurable severity levels

**Detection Rule Schema:**
```json
{
  "rule_id": "SSH-BRUTE-001",
  "name": "SSH Brute Force Attempt",
  "description": "Detects multiple failed SSH authentication attempts",
  "severity": "high",
  "category": "authentication",
  "conditions": [
    {
      "field": "event.type",
      "operator": "equals",
      "value": "authentication_failure"
    },
    {
      "field": "application",
      "operator": "equals",
      "value": "sshd"
    }
  ],
  "threshold": 5,
  "time_window": "1m",
  "group_by": ["source.ip"],
  "mitre_attack": ["T1110"],
  "response_recommendation": "Block source IP, investigate account"
}
```

### 6. Correlation Engine

**Purpose:** Connect related events that appear unrelated individually

**Correlation Strategies:**
- **Temporal Correlation**: Events within time windows
- **Entity Correlation**: Same IP, user, or host
- **Sequence Correlation**: Specific event sequences
- **Statistical Correlation**: Anomalous patterns

**Example Correlation:**
```
Event 1: Port scan detected from 192.168.1.100
Event 2: SSH brute force from 192.168.1.100
Event 3: Successful SSH login from 192.168.1.100
Event 4: Privilege escalation attempt

→ Correlated Incident: "Possible Account Compromise"
```

### 7. Risk & Severity Engine

**Risk Score Calculation:**
```
risk_score = base_severity ×
             asset_criticality ×
             threat_intel_factor ×
             confidence_score ×
             frequency_multiplier
```

**Severity Factors:**
- Detection rule base severity
- Asset criticality (production vs. test)
- Privileged account involvement
- Threat intelligence matches
- Number of affected assets
- Detection confidence
- Historical frequency

**Severity Levels:**
- **Informational**: No action required
- **Low**: Monitor, may indicate reconnaissance
- **Medium**: Investigation recommended
- **High**: Prompt investigation required
- **Critical**: Immediate response needed

### 8. Alert Management

**Alert Lifecycle:**
1. **Generated**: Alert created by detection engine
2. **New**: Awaiting analyst review
3. **Acknowledged**: Analyst assigned and investigating
4. **In Progress**: Active investigation
5. **Resolved**: Investigation complete
6. **Closed**: Final disposition documented

**Alert Fields:**
- Unique alert ID
- Title and description
- Severity and risk score
- Detection rule reference
- Timestamps (created, updated, resolved)
- Affected assets and users
- Source/destination information
- Supporting events
- Analyst notes
- Resolution details

### 9. Incident Management

**Incident Structure:**
- Incident ID and title
- Severity level
- Status (open, contained, resolved, closed)
- Timeline of events
- Related alerts (grouped)
- Affected assets
- Involved accounts
- Evidence attachments
- Analyst notes and actions
- Response actions taken

**Incident Workflow:**
```
Open → Triage → Containment → Eradication → Recovery → Closed
```

### 10. Investigation Workspace

**Features:**
- Event timeline visualization
- Entity relationship graph
- Search across all data
- Filter by entity (IP, user, host)
- Drill-down into raw events
- Export evidence packages

**Query Language:**
```
source.ip = "192.168.1.10" AND
event.type = "authentication_failure" AND
timestamp >= "2024-01-01T00:00:00Z"
```

### 11. Dashboard

**Key Metrics:**
- Events received (total, per second)
- Active alerts by severity
- Open incidents
- Failed authentication attempts
- Unique source IPs
- Monitored hosts
- Top detection rules triggered

**Visualizations:**
- Event volume over time
- Alert severity distribution
- Top source addresses
- Top affected hosts
- Authentication success/failure ratio
- Incident trends

## Data Flow

```
1. Event Generation
   ↓
2. Collection (Agent/Syslog/File/API)
   ↓
3. Ingestion (Validation, Authentication)
   ↓
4. Normalization (Common Schema)
   ↓
5. Enrichment (Context Addition)
   ↓
6. Storage (PostgreSQL)
   ↓
7. Detection (Rule Evaluation)
   ↓
8. Correlation (Relationship Analysis)
   ↓
9. Risk Scoring (Severity Calculation)
   ↓
10. Alert Generation
    ↓
11. Incident Creation (if correlated)
    ↓
12. Dashboard Notification
    ↓
13. Analyst Investigation
    ↓
14. Response Action (optional)
```

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **Task Queue**: Celery + Redis (for async processing)
- **Authentication**: JWT tokens, bcrypt password hashing
- **Validation**: Pydantic

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **State Management**: Redux Toolkit
- **UI Library**: Material-UI / Ant Design
- **Charts**: Recharts / Chart.js
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev), Kubernetes (future)
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana (future)

## Security Architecture

### Authentication
- Password-based authentication with bcrypt
- JWT tokens for session management
- API keys for agent authentication
- Token refresh mechanism
- Session timeout and invalidation

### Authorization
- Role-Based Access Control (RBAC)
- Roles: Admin, Analyst, Viewer, Agent
- Permission checks on all API endpoints
- Resource-level access control

### Data Protection
- TLS encryption for all communications
- Encrypted password storage
- Secrets management via environment variables
- Input validation and sanitization
- SQL injection prevention (parameterized queries)

### Audit Logging
- All authentication events
- All authorization decisions
- All configuration changes
- All incident state changes
- All API access (admin functions)

## Scalability Considerations

### Current (Modular Monolith)
- Single deployment unit
- Shared database
- Simple deployment and maintenance
- Suitable for personal/small lab use

### Future (Microservices)
- Separate services for:
  - Ingestion (high throughput)
  - Detection (CPU intensive)
  - Correlation (memory intensive)
  - API (user-facing)
- Message queue between services
- Independent scaling
- Event sourcing for resilience

## Performance Targets

- **Event Ingestion**: 1000 events/second (single node)
- **Detection Latency**: < 5 seconds from ingestion to alert
- **Query Response**: < 2 seconds for typical searches
- **Dashboard Load**: < 3 seconds initial load
- **Availability**: 99.5% (development target)
