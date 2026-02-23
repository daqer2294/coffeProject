from datetime import datetime, date

from sqlalchemy import (
    Integer,
    BigInteger,
    String,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# =========================================================
# 👤 USERS
# =========================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    visits = relationship(
        "Visit",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    admin_messages = relationship(
        "AdminMessage",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# =========================================================
# ☕ COFFEE SHOPS
# =========================================================

class CoffeeShop(Base):
    __tablename__ = "coffee_shops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    visits = relationship(
        "Visit",
        back_populates="shop",
        cascade="all, delete-orphan"
    )


# =========================================================
# 🧾 VISITS
# =========================================================

class Visit(Base):
    __tablename__ = "visits"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "shop_id",
            "visit_date",
            name="unique_user_shop_date"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    shop_id: Mapped[int] = mapped_column(
        ForeignKey("coffee_shops.id"),
        nullable=False
    )

    visit_date: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
        nullable=False
    )

    user = relationship("User", back_populates="visits")
    shop = relationship("CoffeeShop", back_populates="visits")

    ratings = relationship(
        "ReviewRating",
        back_populates="visit",
        cascade="all, delete-orphan"
    )

    text = relationship(
        "ReviewText",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan"
    )

    admin_messages = relationship(
        "AdminMessage",
        back_populates="visit"
    )


# =========================================================
# ⭐ RATINGS
# =========================================================

class ReviewRating(Base):
    __tablename__ = "review_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    visit_id: Mapped[int] = mapped_column(
        ForeignKey("visits.id"),
        nullable=False
    )

    criterion_key: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    visit = relationship("Visit", back_populates="ratings")


# =========================================================
# 💬 REVIEW TEXT
# =========================================================

class ReviewText(Base):
    __tablename__ = "review_texts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    visit_id: Mapped[int] = mapped_column(
        ForeignKey("visits.id"),
        unique=True,
        nullable=False
    )

    comment: Mapped[str] = mapped_column(String, nullable=True)
    improvement_suggestion: Mapped[str] = mapped_column(String, nullable=True)

    visit = relationship("Visit", back_populates="text")


# =========================================================
# 📩 ADMIN MESSAGES
# =========================================================

class AdminMessage(Base):
    __tablename__ = "admin_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    admin_telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    visit_id: Mapped[int | None] = mapped_column(
        ForeignKey("visits.id"),
        nullable=True
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="sent",
        nullable=False
    )

    user = relationship("User", back_populates="admin_messages")
    visit = relationship("Visit", back_populates="admin_messages")