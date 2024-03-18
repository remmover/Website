from datetime import date

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy import Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connect import Base


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(10000), nullable=False, unique=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    """user_id always must be present because post is created by specific user"""
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", backref="posts", lazy="joined")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """username must be case insensitive unique because comments
       must always be uniquely identified without an email address.
       Cannot start with digit and cannot contain "/" in aim
       to avoid conflicts with some requests"""
    username: Mapped[str] = mapped_column(String(50))
    """email must be case insensitive unique to avoid spoofing"""
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    """about is users description about self"""
    about: Mapped[str] = mapped_column(Text, nullable=True)
    """refresh_token must be deleted after logout"""
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    """is_active=False if user is banned"""
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
