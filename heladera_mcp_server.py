"""
Servidor MCP local que expone las tools de la heladera
para que el agente (Copilot en modo Agent) pueda invocarlas.
"""

from mcp.server.fastmcp import FastMCP
from heladera import agregar_alimento, listar_alimentos, obtener_por_vencer, marcar_consumido

mcp = FastMCP("heladera")


@mcp.tool()
def tool_agregar_alimento(nombre: str, cantidad: float, unidad: str, vencimiento: str) -> str:
    """Agrega un alimento a la heladera. vencimiento en formato YYYY-MM-DD."""
    nuevo_id = agregar_alimento(nombre, cantidad, unidad, vencimiento)
    return f"Alimento '{nombre}' agregado con id {nuevo_id}."


@mcp.tool()
def tool_listar_alimentos() -> list[dict]:
    """Lista todos los alimentos no consumidos en la heladera."""
    return listar_alimentos()


@mcp.tool()
def tool_obtener_por_vencer(dias: int = 3) -> list[dict]:
    """Devuelve los alimentos que vencen dentro de los próximos `dias` días."""
    return obtener_por_vencer(dias)


@mcp.tool()
def tool_marcar_consumido(alimento_id: int) -> str:
    """Marca un alimento como consumido, dado su id."""
    ok = marcar_consumido(alimento_id)
    return "Marcado como consumido." if ok else "No se encontró ese alimento."


if __name__ == "__main__":
    mcp.run()