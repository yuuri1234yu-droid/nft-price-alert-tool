import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# Render の環境変数から DB URL を取得
DATABASE_URL = os.environ.get("DATABASE_URL")

# Render の Postgres を使う場合は SSL 必須
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    future=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User モデル
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)   # ← 必須！

# DB初期化（テーブル作成）
def init_db():
    Base.metadata.create_all(bind=engine)
