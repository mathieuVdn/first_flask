from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    firstname: so.Mapped[str] = so.mapped_column(sa.String(256))
    lastname: so.Mapped[str] = so.mapped_column(sa.String(256))
    gender: so.Mapped[int] = so.mapped_column(sa.Boolean)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    profile_picture: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class MarketRequest(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    symbol: so.Mapped[str] = so.mapped_column(sa.String(140))
    company_name: so.Mapped[str] = so.mapped_column(sa.String(140))
    price: so.Mapped[str] = so.mapped_column(sa.String(140))
    net_change: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    def __repr__(self):
        return f'<MarketRequest {self.symbol}>'


class UploadFile(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    filename: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    upload_at: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    def __repr__(self):
        return f'<UploadFile {self.title}>'


@login.user_loader
def load_user(id):
    return db.session .get(User, int(id))
