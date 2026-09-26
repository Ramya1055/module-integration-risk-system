from pydantic import BaseModel


class IntegrationCreate(BaseModel):
    existing_module: str
    proposed_module: str
    contract_address: str | None = None
    network: str = "local"


class IntegrationResponse(BaseModel):
    integration_id: str
    existing_module: str
    proposed_module: str
    contract_address: str | None
    network: str
    status: str

    class Config:
        from_attributes = True