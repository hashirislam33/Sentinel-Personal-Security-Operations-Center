# Sentinel Threat Model

## Overview

This document describes the security threats, attack vectors, and mitigations for the Sentinel platform. As a security monitoring system, Sentinel must protect itself against the same types of attacks it is designed to detect.

## System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    TRUST BOUNDARY                           │
│                                                             │
│  ┌─────────────┐         ┌─────────────┐                   │
│  │   Agents    │────────▶│  Ingestion  │                   │
│  │  (Untrusted)│         │    API      │                   │
│  └─────────────┘         └──────┬──────┘                   │
│                                 │                           │
│  ┌─────────────┐         ┌──────▼──────┐                   │
│  │   Users     │────────▶│   Backend   │                   │
│  │  (Browser)  │         │  Services   │                   │
│  └─────────────┘         └──────┬──────┘                   │
│                                 │                           │
│                          ┌──────▼──────┐                   │
│                          │  PostgreSQL │                   │
│                          │  Database   │                   │
│                          └─────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Trust Levels

| Component | Trust Level | Description |
|-----------|-------------|-------------|
| Database | High | Trusted storage, internal network only |
| Backend Services | High | Application logic, authenticated access |
| Frontend | Medium | User-facing, potential XSS/CSRF |
| Agents | Low | External systems, potential compromise |
| External APIs | Low | Untrusted input sources |

## Threat Categories

### 1. Event Injection Attacks

**Threat**: Malicious actors inject false events to:
- Create false positives (noise injection)
- Hide real attacks (signal drowning)
- Trigger automated responses against innocent parties
- Corrupt investigation data

**Attack Vectors**:
- Compromised agent sending falsified telemetry
- Direct API abuse with crafted events
- Syslog spoofing from network
- Log file manipulation before upload

**Mitigations**:
- ✅ Agent authentication with API keys
- ✅ Event validation against schema
- ✅ Source IP verification
- ✅ Rate limiting per source
- ✅ Anomaly detection on event patterns
- ✅ Audit logging of all ingested events
- ⏳ Cryptographic signing of agent events (future)
- ⏳ Reputation scoring for event sources

### 2. Authentication & Authorization Attacks

**Threat**: Unauthorized access to Sentinel itself

**Attack Vectors**:
- Credential stuffing/brute force
- JWT token theft or forgery
- Session hijacking
- Privilege escalation
- API key leakage

**Mitigations**:
- ✅ Strong password hashing (bcrypt, cost factor 12+)
- ✅ Account lockout after failed attempts
- ✅ JWT tokens with short expiration
- ✅ Refresh token rotation
- ✅ HTTPS-only cookies
- ✅ Role-Based Access Control (RBAC)
- ✅ Permission checks on every endpoint
- ✅ Audit logging of auth events
- ⏳ Multi-factor authentication (future)
- ⏳ Hardware security key support (future)

### 3. Data Tampering

**Threat**: Modification of security data to hide attacks or frame innocents

**Attack Vectors**:
- SQL injection to modify records
- Direct database access
- Backup tampering
- Log deletion

**Mitigations**:
- ✅ Parameterized queries (no SQL injection)
- ✅ Database access restricted to backend
- ✅ Immutable audit logs (append-only)
- ✅ Regular backups with integrity checks
- ⏳ Write-once storage for critical events (future)
- ⏳ Blockchain-style hash chaining for audit trail (future)
- ⏳ External log shipping (future)

### 4. Denial of Service

**Threat**: Overwhelm Sentinel to blind monitoring

**Attack Vectors**:
- Flood ingestion API with events
- Exhaust database connections
- Consume disk space with events
- CPU exhaustion via complex queries

**Mitigations**:
- ✅ Rate limiting on all endpoints
- ✅ Event queue with backpressure
- ✅ Query timeout limits
- ✅ Resource quotas per user
- ✅ Disk space monitoring
- ⏳ Auto-scaling for ingestion (future)
- ⏳ Event sampling under load (future)

### 5. Information Disclosure

**Threat**: Exposure of sensitive security data

**Attack Vectors**:
- Unauthorized API access
- Insecure direct object references
- Excessive data in error messages
- Log leakage

**Mitigations**:
- ✅ Authentication required for all endpoints
- ✅ Object-level authorization checks
- ✅ Generic error messages
- ✅ Sensitive field masking
- ✅ Secure headers (no caching of sensitive data)
- ⏳ Field-level encryption for sensitive data (future)

### 6. Supply Chain Attacks

**Threat**: Compromise through dependencies

**Attack Vectors**:
- Malicious Python packages
- Compromised Docker images
- Dependency vulnerabilities

**Mitigations**:
- ✅ Dependency scanning in CI/CD
- ✅ Pin dependency versions
- ✅ Official base images only
- ✅ Regular security updates
- ⏳ Image signing verification (future)
- ⏳ Private package mirror (future)

### 7. Agent Compromise

**Threat**: Compromised agent used to attack Sentinel

**Attack Vectors**:
- Stolen agent API key
- Reverse-engineered agent binary
- Man-in-the-middle attack
- Agent vulnerability exploitation

**Mitigations**:
- ✅ Unique API key per agent
- ✅ TLS for all communications
- ✅ Agent health monitoring
- ✅ Certificate pinning (planned)
- ⏳ Agent attestation (future)
- ⏳ Behavioral analysis of agent traffic (future)

### 8. Insider Threats

**Threat**: Malicious action by authorized users

**Attack Vectors**:
- Admin credential abuse
- Evidence tampering
- Alert suppression
- Configuration changes

**Mitigations**:
- ✅ Comprehensive audit logging
- ✅ Separation of duties (roles)
- ✅ Alert on configuration changes
- ✅ Immutable audit trail
- ⏳ Four-eyes principle for critical actions (future)
- ⏳ Behavioral anomaly detection (future)

## STRIDE Analysis

| Threat | Security Property | Risk Level | Status |
|--------|------------------|------------|--------|
| Spoofing agent identity | Authentication | High | ✅ Mitigated |
| Tampering with events | Integrity | High | ✅ Mitigated |
| Repudiation of actions | Non-repudiation | Medium | ✅ Mitigated |
| Information disclosure | Confidentiality | Medium | ✅ Mitigated |
| Denial of service | Availability | Medium | ✅ Mitigated |
| Elevation of privilege | Authorization | High | ✅ Mitigated |

## Attack Surface

### External Interfaces

1. **Ingestion API** (`/api/v1/events`)
   - Authentication: API key required
   - Rate limit: 1000 events/minute per key
   - Validation: Schema enforcement
   - Logging: All requests logged

2. **User API** (`/api/v1/*`)
   - Authentication: JWT token required
   - Authorization: RBAC enforced
   - Rate limit: 100 requests/minute per user
   - Validation: Input sanitization

3. **Web Interface** (`/`)
   - Authentication: Session-based
   - CSRF protection: Token-based
   - XSS protection: CSP headers, output encoding

### Internal Interfaces

1. **Database Connection**
   - Network: Internal Docker network only
   - Authentication: Strong credentials
   - Encryption: TLS (production)

2. **Service-to-Service**
   - Network: Internal only
   - Authentication: Service tokens
   - Authorization: Least privilege

## Security Controls

### Preventive Controls

- Input validation on all external data
- Authentication before authorization
- Principle of least privilege
- Network segmentation
- Secrets management

### Detective Controls

- Comprehensive audit logging
- Anomaly detection on event volume
- Alert on security events
- Regular security scanning
- File integrity monitoring (planned)

### Corrective Controls

- Automated incident response (playbooks)
- Backup and recovery procedures
- Rollback capabilities
- Emergency shutdown procedures

## Security Assumptions

1. **Network Security**: Sentinel runs on a trusted internal network
2. **Physical Security**: Server hardware is physically secure
3. **Admin Trust**: System administrators are trusted
4. **TLS Termination**: TLS is terminated at reverse proxy or application
5. **External Dependencies**: Package repositories are trustworthy

## Known Limitations

1. **Single Point of Failure**: Current architecture has no redundancy
2. **Limited Scalability**: Not designed for enterprise-scale deployments
3. **No HSM Support**: Keys stored in software, not hardware
4. **Basic Anomaly Detection**: Rules-based, not ML-based
5. **Limited Forensics**: Basic evidence collection only

## Future Security Enhancements

### Short-term (v1.1)
- [ ] Multi-factor authentication
- [ ] Certificate pinning for agents
- [ ] Enhanced audit log search
- [ ] Security header hardening

### Medium-term (v1.5)
- [ ] Behavioral anomaly detection
- [ ] Encrypted event storage
- [ ] External SIEM integration
- [ ] Automated vulnerability scanning

### Long-term (v2.0)
- [ ] Hardware security module support
- [ ] Blockchain-style audit trail
- [ ] Zero-trust architecture
- [ ] Advanced threat hunting tools

## Incident Response

### Security Incident Types

1. **Authentication Failure Spike**: Possible brute force
2. **Unauthorized Access Attempt**: Privilege escalation attempt
3. **Data Tampering Detected**: Integrity violation
4. **Service Disruption**: Possible DoS
5. **Sensitive Data Exposure**: Information leak

### Response Procedures

```
Detection → Containment → Eradication → Recovery → Lessons Learned
```

### Contact Points

- **Security Team**: security@localhost (configured per deployment)
- **Emergency Shutdown**: Documented runbook
- **Escalation Path**: Defined in operations manual

## Compliance Considerations

While Sentinel is not certified for any compliance framework, its design considers:

- **NIST CSF**: Detect function alignment
- **PCI DSS**: Log management concepts
- **SOC 2**: Security control principles
- **GDPR**: Data minimization (for personal data in logs)

## Security Testing

### Automated Tests

- Unit tests for auth logic
- Integration tests for API security
- Dependency vulnerability scanning
- Static code analysis

### Manual Tests

- Penetration testing (periodic)
- Code review for security changes
- Threat model updates (quarterly)

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01 | Sentinel Team | Initial threat model |

---

**Note**: This threat model should be reviewed and updated whenever significant architectural changes are made to Sentinel.
