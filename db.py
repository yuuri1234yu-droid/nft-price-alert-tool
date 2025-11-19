# db.py

import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

# Render の環境変数から DB URL を取得
DATABASE_URL = os.environ.get("DATABASE_URL")

# Render の Postgres は SSL が必須
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    future=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# User テーブル
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

# DB初期化
def init_db():
    Base.metadata.create_all(bind=engine)
