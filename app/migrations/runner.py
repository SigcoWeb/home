"""
Runner de migraciones SQL sin Alembic.

Splitter inteligente: reconoce comentarios de linea (--), comentarios de
bloque (/* */), strings con comilla simple y dollar-quoting de Postgres
para no partir por ';' dentro de ellos.
"""
import os
from pathlib import Path
from sqlalchemy import text
from app.database import engine

SQL_DIR = Path(__file__).parent / "sql"
TABLA_CONTROL = "sgc_sys_migraciones"


def _split_sql_statements(sql: str) -> list[str]:
    """
    Divide un bloque SQL en sentencias individuales, respetando:
    - Comentarios de linea: -- hasta fin de linea
    - Comentarios de bloque: /* ... */
    - Strings literales con comilla simple: '...' (incluyendo '' escapado)
    - Dollar-quoting de Postgres: $tag$ ... $tag$ (por ejemplo $$ o $body$)

    Retorna lista de sentencias no vacias, sin sentencias que sean solo comentarios.
    """
    statements = []
    buf = []
    i = 0
    n = len(sql)

    in_line_comment = False
    in_block_comment = False
    in_single_quote = False
    in_dollar_quote = False
    dollar_tag = ""

    while i < n:
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < n else ""

        if in_line_comment:
            buf.append(ch)
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            buf.append(ch)
            if ch == "*" and nxt == "/":
                buf.append(nxt)
                i += 2
                in_block_comment = False
                continue
            i += 1
            continue

        if in_single_quote:
            buf.append(ch)
            if ch == "'":
                # Escape: '' es comilla literal, NO cierre
                if nxt == "'":
                    buf.append(nxt)
                    i += 2
                    continue
                in_single_quote = False
            i += 1
            continue

        if in_dollar_quote:
            buf.append(ch)
            if ch == "$" and sql[i:i + len(dollar_tag)] == dollar_tag:
                buf.append(sql[i + 1:i + len(dollar_tag)])
                i += len(dollar_tag)
                in_dollar_quote = False
                continue
            i += 1
            continue

        # Aperturas de contexto
        if ch == "-" and nxt == "-":
            in_line_comment = True
            buf.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "*":
            in_block_comment = True
            buf.append(ch)
            buf.append(nxt)
            i += 2
            continue

        if ch == "'":
            in_single_quote = True
            buf.append(ch)
            i += 1
            continue

        if ch == "$":
            end_tag = sql.find("$", i + 1)
            if end_tag != -1 and end_tag - i < 30:
                candidate = sql[i:end_tag + 1]
                # Aceptar tags simples tipo $$, $body$, $func_1$
                if all(c.isalnum() or c == "_" for c in candidate[1:-1]):
                    dollar_tag = candidate
                    in_dollar_quote = True
                    buf.append(candidate)
                    i = end_tag + 1
                    continue

        if ch == ";":
            statement = "".join(buf).strip()
            if statement:
                statements.append(statement)
            buf = []
            i += 1
            continue

        buf.append(ch)
        i += 1

    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)

    # Filtrar sentencias que son solo comentarios
    result = []
    for stmt in statements:
        lines = [ln for ln in stmt.splitlines() if ln.strip()]
        if not lines:
            continue
        all_comments = True
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("--") or stripped.startswith("/*") or stripped.startswith("*"):
                continue
            all_comments = False
            break
        if all_comments:
            continue
        result.append(stmt)

    return result


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
            sentencias = _split_sql_statements(sql)

            for sentencia in sentencias:
                await conn.execute(text(sentencia))

            await conn.execute(text(
                f"INSERT INTO {TABLA_CONTROL} (version, nombre) VALUES (:v, :n)"
            ), {"v": version, "n": archivo})
            print(f"[migrations] OK {archivo} aplicado")
