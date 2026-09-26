from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class Integration(Base):
    __tablename__ = "integrations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    integration_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    existing_module: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    proposed_module: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    contract_address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    network: Mapped[str] = mapped_column(
        String(100),
        default="local",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="CREATED",
        nullable=False,
    )

    start_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    end_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )



class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    integration_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    phase: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    cpu_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    memory_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    error_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


class ModuleProfile(Base):
    __tablename__ = "module_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    integration_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    module_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_file: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    source_lines: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    function_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    state_variable_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    external_call_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    event_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    modifier_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    payable_function_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    interface_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    dependency_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

class IntegrationEvent(Base):
    __tablename__ = "integration_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    integration_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    component: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="INFO",
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

class PerformanceAnalysis(Base):
    __tablename__ = "performance_analysis"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    integration_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    baseline_cpu: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    baseline_memory: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    runtime_sample_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    average_runtime_cpu: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    average_runtime_memory: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    cpu_change: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    memory_change: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    total_runtime_errors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

class SecurityFinding(Base):
    __tablename__ = "security_findings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    integration_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    finding_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    component: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    evidence: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    integration_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    transaction_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    from_address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    to_address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    block_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    gas_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    gas_used: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )