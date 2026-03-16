"""Company content and asset models."""
from datetime import datetime
import enum
import uuid

from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.db.session import Base


class AssetTypeEnum(str, enum.Enum):
    """Company asset types."""
    LOGO = "LOGO"
    AWARD_BADGE = "AWARD_BADGE"
    CERTIFICATION = "CERTIFICATION"
    REVIEW_IMAGE = "REVIEW_IMAGE"
    DEFAULT_IMAGE = "DEFAULT_IMAGE"


class CompanyContent(Base):
    """Company content for global templates."""
    __tablename__ = "company_content"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique key like 'intro_letter_template', 'about_company', 'cta_message'"
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    placeholders: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        comment="Available placeholders for template"
    )

    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    updated_by: Mapped["User"] = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "key": self.key,
            "content": self.content,
            "placeholders": self.placeholders,
            "updated_at": self.updated_at.isoformat(),
        }


class CompanyAsset(Base):
    """Company assets like logos, badges, certifications."""
    __tablename__ = "company_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    asset_type: Mapped[AssetTypeEnum] = mapped_column(
        SQLEnum(AssetTypeEnum, name="asset_type_enum"),
        nullable=False,
        index=True
    )

    asset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_url: Mapped[str] = mapped_column(String(500), nullable=False, comment="Azure Blob Storage URL")

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_company_assets_type_active", "asset_type", "is_active"),
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "asset_type": self.asset_type.value,
            "asset_name": self.asset_name,
            "asset_url": self.asset_url,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
        }
