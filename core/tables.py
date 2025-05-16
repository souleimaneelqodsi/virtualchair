import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    DateTime,
    Boolean,
    Integer,
    Date,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import Enum as SQLAlchemyEnum

from flask_login import UserMixin

from .database import Base



class PaperStatusEnum(enum.Enum):
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    NEEDS_REVISION = "Needs Revision"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class ConferenceRoleEnum(enum.Enum):
    CHAIR = "Chair"
    REVIEWER = "Reviewer"
    AUTHOR = "Author"


class EvaluationRecommendationEnum(enum.Enum):
    STRONG_ACCEPT = "Strong Accept"
    ACCEPT = "Accept"
    WEAK_ACCEPT = "Weak Accept"
    BORDERLINE_PAPER = "Borderline Paper"
    WEAK_REJECT = "Weak Reject"
    REJECT = "Reject"
    STRONG_REJECT = "Strong Reject"


class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_conferences = relationship("Conference", back_populates="creator", foreign_keys="Conference.creator_id")
    papers_authored = relationship("Paper", back_populates="author", foreign_keys="Paper.author_id")
    evaluations_given = relationship("Evaluation", back_populates="reviewer", foreign_keys="Evaluation.reviewer_id")
    conference_roles = relationship("ConferenceRole", back_populates="user", cascade="all, delete-orphan")
    def __repr__(self): return f"<User {self.username} ({self.email})>"


class Conference(Base):
    __tablename__ = "conferences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    location = Column(String(100), nullable=True)
    submission_deadline = Column(DateTime, nullable=True)
    current_phase = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    creator = relationship("User", back_populates="created_conferences", foreign_keys=[creator_id])
    papers = relationship("Paper", back_populates="conference", cascade="all, delete-orphan")
    conference_roles = relationship("ConferenceRole", back_populates="conference", cascade="all, delete-orphan")
    def __repr__(self): return f"<Conference {self.name}>"


class Paper(Base):
    __tablename__ = "papers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(300), nullable=False)
    abstract = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    s3_file_url = Column(String(500), nullable=True)
    status = Column(
        SQLAlchemyEnum(
            PaperStatusEnum,
            name='paperstatusenum',
            native_enum=True,
            create_type=False,


        ),
        default=PaperStatusEnum.SUBMITTED,
        nullable=False,
    )
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    conference_id = Column(UUID(as_uuid=True), ForeignKey("conferences.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    conference = relationship("Conference", back_populates="papers")
    author = relationship("User", back_populates="papers_authored")
    evaluations = relationship("Evaluation", back_populates="paper", cascade="all, delete-orphan")
    def __repr__(self): return f"<Paper '{self.title}'>"


class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    score = Column(Integer, nullable=True)
    comments_to_author = Column(Text, nullable=True)
    comments_to_committee = Column(Text, nullable=True)
    recommendation = Column(
        SQLAlchemyEnum(
            EvaluationRecommendationEnum,
            name='evaluationrecommendationenum',
            native_enum=True,
            create_type=False
        ),
        nullable=True
    )
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    deadline = Column(DateTime, nullable=True)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    paper = relationship("Paper", back_populates="evaluations")
    reviewer = relationship("User", back_populates="evaluations_given")
    __table_args__ = (UniqueConstraint("paper_id", "reviewer_id", name="uq_evaluation_paper_reviewer"),)
    def __repr__(self): return f"<Evaluation for Paper ID {self.paper_id} by Reviewer ID {self.reviewer_id}>"


class ConferenceRole(Base):
    __tablename__ = "conference_roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(
        SQLAlchemyEnum(
            ConferenceRoleEnum,
            name='conferenceroleenum',
            native_enum=True,
            create_type=False
        ),
        nullable=False
    )
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conference_id = Column(UUID(as_uuid=True), ForeignKey("conferences.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="conference_roles")
    conference = relationship("Conference", back_populates="conference_roles")
    __table_args__ = (UniqueConstraint("user_id", "conference_id", "role_name", name="uq_conference_user_role"),)

    def __repr__(self): return f"<ConferenceRole: User {self.user_id} as {self.role_name.value if isinstance(self.role_name, enum.Enum) else self.role_name} in Conf {self.conference_id}>"
