from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Trend(Base):
    __tablename__ = "trends"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    summary = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Script(Base):
    __tablename__ = "scripts"
    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(Integer, index=True)
    script = Column(Text)
    critique = Column(Text)
    score = Column(Float)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, index=True)
    path = Column(String)
    engagement_score = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, index=True)
    status = Column(String, default='processing')
    result = Column(Text, nullable=True)
    progress = Column(Integer, default=0)  # Progress percentage 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())