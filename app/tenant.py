from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import AsyncSessionLocal
import re

def schema_nombre(ruc: str) -> str:
    ruc_limpio = re.sub(r'[^0-9]', '', ruc)
    if len(ruc_limpio) not in (8, 11):
        raise ValueError(f"RUC/DNI inválido: {ruc}")
    return f"emp_{ruc_limpio}"

async def get_tenant_session(request: Request) -> AsyncSession:
    schema = getattr(request.state, "tenant_schema", None)
    if not schema:
        raise HTTPException(status_code=401, detail="Sesión sin tenant identificado")
    session = AsyncSessionLocal()
    try:
        await session.execute(text(f'SET search_path TO "{schema}", public'))
        yield session
    finally:
        await session.close()

def set_tenant(request: Request, schema: str):
    request.state.tenant_schema = schema
