Sentinel is a self-hosted, modular Security Operations Center (SOC) platform designed to provide centralized security monitoring, threat detection, investigation, alert management, and incident analysis for computers, servers, applications, and small networks.

The goal is to recreate the core concepts of professional SIEM and SOC platforms on a personal or small-lab scale while keeping the system understandable, deployable, extensible, and suitable for a software engineering and cybersecurity portfolio.

Core features include:

Security event collection from operating systems, authentication systems, web servers, applications, network services, firewalls, and endpoints.
Log normalization into a standardized event format.
Rule-based and correlation-based threat detection.
Risk scoring and severity classification.
Alert and incident management.
Investigation tools and security timelines.
Threat intelligence enrichment.
Asset management and log exploration.
Security reporting and analytics.

Technology stack:

Backend: Python and FastAPI
Frontend: React and TypeScript
Database: PostgreSQL
Deployment: Docker Compose
API: REST with OpenAPI documentation
Authentication: JWT with role-based access control
Testing: Unit, integration, and end-to-end tests
CI/CD: GitHub Actions

Typical workflow:

A monitored system generates a security event.
Sentinel collects and validates the event.
The event is normalized into a common format.
The event is stored and indexed.
Detection rules analyze the event.
Related activity is correlated.
Risk and severity are calculated.
An alert is generated.
Related alerts are grouped into an incident.
The analyst investigates the activity through the dashboard.
An approved response action can be executed.

Security features include secure password storage, authentication and authorization, JWT sessions, input validation, API rate limiting, audit logging, TLS/HTTPS, secrets management, and protection against common OWASP vulnerabilities.

The project follows concepts from the NIST Cybersecurity Framework, MITRE ATT&CK, and established SOC practices. These mappings are design references and do not represent certification or official framework implementations.

Version 1.0 focuses on the core backend, detection engine, alert and incident management, dashboard, and Docker deployment.

Version 1.1 will add a Sentinel Agent, advanced event correlation, investigation graphs, threat intelligence integration, and reporting.

Version 2.0 will introduce machine-learning-based anomaly detection, automated response playbooks, cloud integrations, scalable event processing, and Kubernetes deployment.

Sentinel is designed as an educational and portfolio project demonstrating practical software engineering, cybersecurity, system architecture, security monitoring, and SOC concepts.

License: MIT

Sentinel — Your Personal Security Operations Center
