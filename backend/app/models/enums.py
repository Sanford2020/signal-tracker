import enum


class SourceType(str, enum.Enum):
    RSS = "rss"
    X = "x"
    REDDIT = "reddit"
    GITHUB = "github"
    CAREERS = "careers"
    NEWS = "news"
    SEARCH = "search"
    MANUAL = "manual"
    OTHER = "other"


class SignalType(str, enum.Enum):
    HIRING = "hiring"
    PRODUCT = "product"
    POLICY = "policy"
    FUNDING = "funding"
    GITHUB = "github"
    RUMOR = "rumor"
    RESEARCH = "research"
    MARKET = "market"
    OTHER = "other"


class LifecycleStatus(str, enum.Enum):
    NEW = "new"
    WATCHING = "watching"
    SPREADING = "spreading"
    VALIDATING = "validating"
    COOLING = "cooling"
    DORMANT = "dormant"
    RESURRECTED = "resurrected"
    VERIFIED = "verified"
    DEBUNKED = "debunked"
    NOISE = "noise"
    ARCHIVED = "archived"


class EvidenceType(str, enum.Enum):
    FIRST_SEEN = "first_seen"
    FOLLOW_UP = "follow_up"
    CORROBORATION = "corroboration"
    CONTRADICTION = "contradiction"
    CORRECTION = "correction"
    NOISE = "noise"


class AttachedBy(str, enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ADMIN = "admin"


class IntelEventType(str, enum.Enum):
    CREATED = "created"
    EVIDENCE_ADDED = "evidence_added"
    STATUS_CHANGED = "status_changed"
    SCORE_CHANGED = "score_changed"
    NOTE_ADDED = "note_added"


class AlertType(str, enum.Enum):
    RESURRECTED = "resurrected"
    HEAT_SPIKE = "heat_spike"
    CREDIBILITY_UP = "credibility_up"
    RISK_UP = "risk_up"
    OPPORTUNITY_UP = "opportunity_up"
    VERIFIED = "verified"
    DEBUNKED = "debunked"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WATCH = "watch"
    IMPORTANT = "important"
    URGENT = "urgent"


class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    DISMISSED = "dismissed"


class AlertChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"
    FEISHU = "feishu"
    TELEGRAM = "telegram"
