"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config.settings import settings
from .models.database import Base


# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Enable connection health checks
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.

    Usage in FastAPI routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """

    """
Database models for Sentinel.

This module defines all SQLAlchemy models used by the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum
import uuid


Base = declarative_base()


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


# Enums
class AlertStatus(str, enum.Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Severity(str, enum.Enum):
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    AGENT = "agent"


class AssetType(str, enum.Enum):
    SERVER = "server"
    WORKSTATION = "workstation"
    CONTAINER = "container"
    NETWORK_DEVICE = "network_device"
    OTHER = "other"


class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


# Models
class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    alerts_assigned = relationship("Alert", back_populates="assigned_to_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Asset(Base):
    """Monitored asset (host/server/device) model."""
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=generate_uuid)
    hostname = Column(String(255), nullable=False, index=True)
    type = Column(SQLEnum(AssetType), default=AssetType.OTHER)
    os = Column(String(100), nullable=True)
    ip_addresses = Column(JSON, default=list)
    mac_addresses = Column(JSON, default=list)
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.INACTIVE)
    agent_version = Column(String(20), nullable=True)
    criticality = Column(String(20), default="medium")  # low, medium, high
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    events = relationship("Event", back_populates="asset")
    alerts = relationship("Alert", back_populates="asset")


class Event(Base):
    """Normalized security event model."""
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    # Event classification
    category = Column(String(50), nullable=False, index=True)  # authentication, network, process, file, config
    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(SQLEnum(Severity), default=Severity.INFORMATIONAL)

    # Source information
    source_ip = Column(String(45), nullable=True, index=True)
    source_port = Column(Integer, nullable=True)
    source_hostname = Column(String(255), nullable=True)
    source_mac = Column(String(17), nullable=True)

    # Destination information
    destination_ip = Column(String(45), nullable=True, index=True)
    destination_port = Column(Integer, nullable=True)
    destination_hostname = Column(String(255), nullable=True)

    # User information
    username = Column(String(255), nullable=True, index=True)
    user_uid = Column(String(20), nullable=True)

    # Application/protocol
    application = Column(String(100), nullable=True, index=True)
    protocol = Column(String(50), nullable=True)

    # Action and outcome
    action = Column(String(50), nullable=True)  # allowed, denied, failed, success
    outcome = Column(String(255), nullable=True)

    # Raw data
    raw_event = Column(Text, nullable=True)
    normalized_data = Column(JSON, default=dict)

    # Foreign keys
    asset_id = Column(String, ForeignKey("assets.id"), nullable=True, index=True)

    # Relationships
    asset = relationship("Asset", back_populates="events")
    alert_events = relationship("AlertEvent", back_populates="event")


class DetectionRule(Base):
    """Detection rule model."""
    __tablename__ = "detection_rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    rule_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., SSH-BRUTE-001
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    severity = Column(SQLEnum(Severity), default=Severity.MEDIUM)
    enabled = Column(Boolean, default=True)

    # Rule configuration
    conditions = Column(JSON, nullable=False, default=list)
    threshold = Column(Integer, default=1)
    time_window_seconds = Column(Integer, default=60)
    group_by_fields = Column(JSON, default=list)

    # MITRE ATT&CK mapping
    mitre_attack_ids = Column(JSON, default=list)

    # Response
    response_recommendation = Column(Text, nullable=True)

    # Metadata
    version = Column(Integer, default=1)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Statistics
    triggered_count = Column(Integer, default=0)
    last_triggered = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    alerts = relationship("Alert", back_populates="rule")


class Alert(Base):
    """Security alert model."""
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Classification
    severity = Column(SQLEnum(Severity), nullable=False)
    risk_score = Column(Integer, default=0)  # 0-100
    confidence = Column(Float, default=0.0)  # 0.0-1.0

    # Status
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.NEW)

    # Rule reference
    rule_id = Column(String, ForeignKey("detection_rules.rule_id"), nullable=True, index=True)

    # Context
    source_ip = Column(String(45), nullable=True, index=True)
    destination_ip = Column(String(45), nullable=True)
    username = Column(String(255), nullable=True)

    # Assignment
    assigned_to_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Foreign keys
    asset_id = Column(String, ForeignKey("assets.id"), nullable=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=True, index=True)

    # Relationships
    rule = relationship("DetectionRule", back_populates="alerts")
    assigned_to_user = relationship("User", back_populates="alerts_assigned")
    asset = relationship("Asset", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")
    alert_events = relationship("AlertEvent", back_populates="alert")
    notes = relationship("AlertNote", back_populates="alert", cascade="all, delete-orphan")


class AlertEvent(Base):
    """Association table linking alerts to supporting events."""
    __tablename__ = "alert_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False, index=True)
    correlation_reason = Column(String(255), nullable=True)

    # Relationships
    alert = relationship("Alert", back_populates="alert_events")
    event = relationship("Event", back_populates="alert_events")


class AlertNote(Base):
    """Investigation note on an alert."""
    __tablename__ = "alert_notes"

    id = Column(String, primary_key=True, default=generate_uuid)
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    alert = relationship("Alert", back_populates="notes")
    user = relationship("User")


class Incident(Base):
    """Security incident model (groups related alerts)."""
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(SQLEnum(Severity), nullable=False)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.OPEN)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    contained_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    affected_assets = Column(JSON, default=list)
    involved_accounts = Column(JSON, default=list)
    attacker_ips = Column(JSON, default=list)

    # Relationships
    alerts = relationship("Alert", back_populates="incident")
    timeline = relationship("IncidentTimeline", back_populates="incident", cascade="all, delete-orphan")
    response_actions = relationship("IncidentResponseAction", back_populates="incident", cascade="all, delete-orphan")


class IncidentTimeline(Base):
    """Timeline entry for an incident."""
    __tablename__ = "incident_timeline"

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON, default=dict)

    # Relationships
    incident = relationship("Incident", back_populates="timeline")
    user = relationship("User")


class IncidentResponseAction(Base):
    """Response action taken for an incident."""
    __tablename__ = "incident_response_actions"

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # containment, eradication, recovery
    description = Column(Text, nullable=False)
    automated = Column(Boolean, default=False)
    executed_by_id = Column(String, ForeignKey("users.id"), nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    result = Column(String(255), nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="response_actions")
    executed_by = relationship("User")


class AuditLog(Base):
    """Audit log for security-relevant actions."""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    success = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class APIKey(Base):
    """API key for agent authentication."""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    key_hash = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    permissions = Column(JSON, default=list)

    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=1000)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
