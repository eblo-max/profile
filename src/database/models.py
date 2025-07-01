"""
Модели данных для базы данных
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    BigInteger, String, Text, DateTime, JSON, Boolean, 
    Float, Integer, ForeignKey, func
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    language_code: Mapped[Optional[str]] = mapped_column(String(10))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Связи
    analyses: Mapped[List["Analysis"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )


class Analysis(Base):
    """Модель анализа"""
    __tablename__ = "analyses"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.id", ondelete="CASCADE")
    )
    
    # Статус анализа
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Входные данные
    input_text: Mapped[Optional[str]] = mapped_column(Text)
    input_images: Mapped[Optional[List[str]]] = mapped_column(JSON)  # URLs изображений
    input_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Результаты AI анализа
    watson_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    azure_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    google_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    aws_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    crystal_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    receptiviti_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    lexalytics_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    monkeylearn_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Финальный синтез от Claude
    claude_synthesis: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Метрики валидации
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    bias_warnings: Mapped[Optional[List[str]]] = mapped_column(JSON)
    source_breakdown: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Финальный отчет
    final_report: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="analyses")
    errors: Mapped[List["AnalysisError"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan"
    )


class AnalysisError(Base):
    """Модель ошибок анализа"""
    __tablename__ = "analysis_errors"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("analyses.id", ondelete="CASCADE")
    )
    
    service_name: Mapped[str] = mapped_column(String(100))  # watson, azure, etc.
    error_type: Mapped[str] = mapped_column(String(100))    # api_error, timeout, etc.
    error_message: Mapped[str] = mapped_column(Text)
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Связи
    analysis: Mapped["Analysis"] = relationship(back_populates="errors")


class ApiUsage(Base):
    """Модель учета использования API"""
    __tablename__ = "api_usage"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE")
    )
    
    service_name: Mapped[str] = mapped_column(String(100))
    requests_count: Mapped[int] = mapped_column(Integer, default=1)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float)
    
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )


class UserSession(Base):
    """Модель пользовательской сессии для FSM"""
    __tablename__ = "user_sessions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    
    current_state: Mapped[Optional[str]] = mapped_column(String(100))
    session_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    ) 