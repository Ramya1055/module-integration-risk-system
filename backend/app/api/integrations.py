from fastapi import APIRouter, Depends, HTTPException


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import SessionLocal
from backend.app.schemas.integration import (
    IntegrationCreate,
    IntegrationResponse,
)
from reports.integration_report import (
    generate_integration_report,
)

from backend.app.services.integration_service import (
    create_integration,
    start_integration,
    begin_integration_monitoring,
    collect_integration_runtime_metric,
    collect_integration_runtime_samples,
    complete_integration,
    analyze_completed_integration,
    analyze_integration_security,
    finalize_integration,
    record_blockchain_transaction,
)


router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=IntegrationResponse,
)
def create_new_integration(
    data: IntegrationCreate,
    db: Session = Depends(get_db),
):
    return create_integration(
        db=db,
        existing_module=data.existing_module,
        proposed_module=data.proposed_module,
        contract_address=data.contract_address,
        network=data.network,
    )


@router.post(
    "/{integration_id}/start",
    response_model=IntegrationResponse,
)
def start_existing_integration(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        return start_integration(
            db=db,
            integration_id=integration_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/{integration_id}/begin-monitoring",
    response_model=IntegrationResponse,
)
def begin_monitoring(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        return begin_integration_monitoring(
            db=db,
            integration_id=integration_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/{integration_id}/runtime-metric",
)
def collect_runtime_observation(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        metric = collect_integration_runtime_metric(
            db=db,
            integration_id=integration_id,
        )

        return {
            "integration_id": metric.integration_id,
            "phase": metric.phase,
            "cpu_percent": metric.cpu_percent,
            "memory_percent": metric.memory_percent,
            "error_count": metric.error_count,
            "timestamp": metric.timestamp,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/{integration_id}/runtime-samples",
)
def collect_runtime_samples_endpoint(
    integration_id: str,
    sample_count: int = 5,
    interval_seconds: int = 2,
    db: Session = Depends(get_db),
):
    try:
        metrics = collect_integration_runtime_samples(
            db=db,
            integration_id=integration_id,
            sample_count=sample_count,
            interval_seconds=interval_seconds,
        )

        return {
            "integration_id": integration_id,
            "samples_collected": len(metrics),
            "metrics": [
                {
                    "phase": metric.phase,
                    "cpu_percent": metric.cpu_percent,
                    "memory_percent": metric.memory_percent,
                    "error_count": metric.error_count,
                    "timestamp": metric.timestamp,
                }
                for metric in metrics
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.post(
    "/{integration_id}/complete",
    response_model=IntegrationResponse,
)
def complete_existing_integration(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        return complete_integration(
            db=db,
            integration_id=integration_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.post(
    "/{integration_id}/analyze",
)
def analyze_integration(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        return analyze_completed_integration(
            db=db,
            integration_id=integration_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.post(
    "/{integration_id}/security-analysis",
)
def security_analysis(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        return analyze_integration_security(
            db=db,
            integration_id=integration_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.post(
    "/{integration_id}/finalize",
    response_model=IntegrationResponse,
)
def finalize_existing_integration(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        return finalize_integration(
            db=db,
            integration_id=integration_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )   

@router.get(
    "/{integration_id}/report",
)
def get_integration_report(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        return generate_integration_report(
            db=db,
            integration_id=integration_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

@router.post(
    "/{integration_id}/blockchain-transaction"
)
def record_integration_blockchain_transaction(
    integration_id: str,
    transaction_hash: str,
    db: Session = Depends(get_db),
):
    try:
        transaction = record_blockchain_transaction(
            db=db,
            integration_id=integration_id,
            transaction_hash=transaction_hash,
        )

        return {
            "integration_id": transaction.integration_id,
            "transaction_hash": transaction.transaction_hash,
            "block_number": transaction.block_number,
            "gas_limit": transaction.gas_limit,
            "gas_used": transaction.gas_used,
            "status": transaction.status,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )