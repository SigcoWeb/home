"""
Runner de migraciones SQL sin Alembic.
"""
import os
from pathlib import Path
from sqlalchemy import text
from app.database import engine

SQL_DIR = Path(__file__).parent / "sql"
TABLA_CONTROL = "sgc_sys_migraciones"

async def ejecutar_migraciones_pendientes():
    async with engine.begin() as conn:
        await conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {TABLA_CONTROL} (
                version VARCHAR(20) PRIMARY KEY,
                nombre VARCHAR(200),
                aplicada_en TIMESTAMP DEFAULT NOW()
            )
        """))

        result = await conn.execute(text(f"SELECT version FROM {TABLA_CONTROL}"))
        aplicadas = {row[0] for row in result.fetchall()}

        archivos = sorted([
            f for f in os.listdir(SQL_DIR)
            if f.endswith(".sql")
        ])

        for archivo in archivos:
            version = archivo.split("_")[0]
            if version in aplicadas:
                continue

            sql_path = SQL_DIR / archivo
            sql = sql_path.read_text(encoding="utf-8")

            print(f"[migrations] Aplicando {archivo}...")
            sentencias = [
                s.strip() for s in sql.split(";")
                if s.strip() and not all(
                    line.startswith("--") for line in s.strip().splitlines() if line.strip()
                )
            ]
            for sentencia in sentencias:
                await conn.execute(text(sentencia))

            await conn.execute(text(
                f"INSERT INTO {TABLA_CONTROL} (version, nombre) VALUES (:v, :n)"
            ), {"v": version, "n": archivo})
            print(f"[migrations] OK {archivo} aplicado")
