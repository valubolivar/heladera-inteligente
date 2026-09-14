"""
Capa de datos y lógica de negocio del organizador de heladera.
Persistencia en SQLite. Cada función de acá abajo es una "tool"
que después el agente (vía MCP o directamente) va a poder invocar.
"""

import sqlite3
from datetime import date, datetime
from dataclasses import dataclass

DB_NAME = "heladera.db"


@dataclass
class Alimento:
    id: int
    nombre: str
    cantidad: float
    unidad: str
    vencimiento: str  # formato YYYY-MM-DD


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crea la tabla de alimentos si no existe."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad REAL NOT NULL,
            unidad TEXT NOT NULL,
            vencimiento TEXT NOT NULL,
            consumido INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def agregar_alimento(nombre: str, cantidad: float, unidad: str, vencimiento: str) -> int:
    """
    Agrega un alimento a la heladera.
    vencimiento debe tener formato 'YYYY-MM-DD'.
    Devuelve el id del alimento creado.
    """
    datetime.strptime(vencimiento, "%Y-%m-%d")  # valida el formato de fecha

    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO alimentos (nombre, cantidad, unidad, vencimiento) VALUES (?, ?, ?, ?)",
        (nombre, cantidad, unidad, vencimiento)
    )
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return nuevo_id


def listar_alimentos(incluir_consumidos: bool = False) -> list[dict]:
    """Devuelve todos los alimentos cargados, ordenados por fecha de vencimiento."""
    conn = get_connection()
    if incluir_consumidos:
        rows = conn.execute(
            "SELECT * FROM alimentos ORDER BY vencimiento ASC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM alimentos WHERE consumido = 0 ORDER BY vencimiento ASC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtener_por_vencer(dias: int = 3) -> list[dict]:
    """
    Devuelve los alimentos no consumidos que vencen dentro de los
    próximos `dias` días (incluye los ya vencidos).
    """
    hoy = date.today()
    alimentos = listar_alimentos()
    resultado = []
    for a in alimentos:
        vencimiento = datetime.strptime(a["vencimiento"], "%Y-%m-%d").date()
        diferencia = (vencimiento - hoy).days
        if diferencia <= dias:
            resultado.append({**a, "dias_restantes": diferencia})
    return resultado


def marcar_consumido(alimento_id: int) -> bool:
    """Marca un alimento como consumido. Devuelve True si existía y se actualizó."""
    conn = get_connection()
    conn.execute("UPDATE alimentos SET consumido = 1 WHERE id = ?", (alimento_id,))
    conn.commit()
    actualizado = conn.total_changes > 0
    conn.close()
    return actualizado


init_db()