import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow())  # .utcnow   tz=timezone.utc  now()

    role_id = Column(ForeignKey('roles.id'), default=1)

    history = relationship('UserHistory', back_populates='user')
    role = relationship('Role', lazy='selectin')

    def __init__(self, login: str, email: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.email = email
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class UserHistory(Base):
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete="CASCADE"), default=uuid.uuid4, unique=False, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow())  # .utcnow   tz=timezone.utc  now()

    user = relationship('User', back_populates='history')


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    role = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())  # .utcnow   tz=timezone.utc  now()

    def __repr__(self) -> str:
        return f'<User {self.role}>'