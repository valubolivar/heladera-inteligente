"""Capa de datos y lógica de negocio de la heladera inteligente.

Persiste los alimentos cargados en SQLite y expone las funciones que
luego `heladera_mcp_server.py` publica como herramientas MCP para el
agente (ver `agente_heladera.agent.md`).
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
    """Abre una conexión nueva a la base de datos de la heladera.

    Returns:
        sqlite3.Connection: conexión con row_factory configurado para
        devolver filas accesibles por nombre de columna (sqlite3.Row).
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crea la tabla `alimentos` si todavía no existe.

    Es idempotente: puede llamarse varias veces sin duplicar ni
    romper la estructura ya creada.
    """
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
    """Agrega un alimento nuevo a la heladera.

    Args:
        nombre: nombre del alimento (ej. "Leche").
        cantidad: cantidad numérica cargada.
        unidad: unidad de esa cantidad (ej. "litro", "unidades").
        vencimiento: fecha de vencimiento en formato 'YYYY-MM-DD'.

    Returns:
        int: id autogenerado del alimento recién creado.

    Raises:
        ValueError: si `vencimiento` no tiene el formato 'YYYY-MM-DD'.
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
    """Lista los alimentos cargados, ordenados por fecha de vencimiento.

    Args:
        incluir_consumidos: si es True, también devuelve los alimentos
            ya marcados como consumidos. Por defecto False.

    Returns:
        list[dict]: una entrada por alimento, ordenadas de la fecha de
        vencimiento más próxima a la más lejana.
    """
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


def _alimentos_con_dias_restantes() -> list[dict]:
    """Adjunta a cada alimento no consumido cuántos días faltan para su vencimiento.

    Returns:
        list[dict]: los mismos campos de `listar_alimentos()` más la
        clave `dias_restantes` (negativa si ya venció).
    """
    hoy = date.today()
    alimentos = listar_alimentos()
    return [
        {
            **alimento,
            "dias_restantes": (
                datetime.strptime(alimento["vencimiento"], "%Y-%m-%d").date()
                - hoy
            ).days,
        }
        for alimento in alimentos
    ]


def obtener_por_vencer(dias: int = 3) -> list[dict]:
    """Devuelve los alimentos no consumidos que vencen pronto.

    Incluye tanto los que vencen dentro del rango pedido como los que
    ya vencieron (días restantes negativos), porque ambos casos
    requieren atención inmediata.

    Args:
        dias: tope de días restantes a considerar "por vencer".
            Por defecto 3.

    Returns:
        list[dict]: alimentos con `dias_restantes <= dias`.
    """
    return [
        alimento
        for alimento in _alimentos_con_dias_restantes()
        if alimento["dias_restantes"] <= dias
    ]


def marcar_consumido(alimento_id: int) -> bool:
    """Marca un alimento como consumido.

    Args:
        alimento_id: id del alimento a marcar.

    Returns:
        bool: True si el id existía y se actualizó una fila; False si
        no existía ningún alimento con ese id.
    """
    conn = get_connection()
    conn.execute("UPDATE alimentos SET consumido = 1 WHERE id = ?", (alimento_id,))
    conn.commit()
    actualizado = conn.total_changes > 0
    conn.close()
    return actualizado


def obtener_alimentos_vencidos() -> list[dict]:
    """Devuelve los alimentos no consumidos cuya fecha de vencimiento ya pasó.

    Returns:
        list[dict]: igual que `listar_alimentos()`, sin la clave
        `dias_restantes` (se descarta porque acá siempre es negativa).
    """
    return [
        {clave: valor for clave, valor in alimento.items() if clave != "dias_restantes"}
        for alimento in _alimentos_con_dias_restantes()
        if alimento["dias_restantes"] < 0
    ]


init_db()
