"""
Servidor MCP que consume una API externa (TheMealDB) para
buscar recetas según un ingrediente dado. Este es el MCP
"externo" que completa el patrón: MCP local (heladera) + MCP externo (recetas).
"""

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("recetas")

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# TheMealDB solo entiende ingredientes en inglés.
# Traducimos los alimentos más comunes de la heladera.
TRADUCCIONES = {
    "leche": "milk",
    "manzana": "apple",
    "manzanas": "apple",
    "yogur": "yogurt",
    "yogurt": "yogurt",
    "huevo": "egg",
    "huevos": "egg",
    "pollo": "chicken",
    "carne": "beef",
    "queso": "cheese",
    "tomate": "tomato",
    "tomates": "tomato",
    "papa": "potato",
    "papas": "potato",
    "patata": "potato",
    "arroz": "rice",
    "pan": "bread",
    "cebolla": "onion",
    "ajo": "garlic",
    "zanahoria": "carrot",
    "pescado": "fish",
    "banana": "banana",
    "naranja": "orange",
    "limon": "lemon",
    "limón": "lemon",
}


def _buscar(ingrediente: str) -> list[dict]:
    resp = requests.get(f"{BASE_URL}/filter.php", params={"i": ingrediente}, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("meals"):
        return []

    resultado = []
    for meal in data["meals"][:5]:
        resultado.append({
            "nombre": meal["strMeal"],
            "id": meal["idMeal"],
            "imagen": meal["strMealThumb"],
            "url": f"https://www.themealdb.com/meal/{meal['idMeal']}"
        })
    return resultado


@mcp.tool()
def buscar_recetas_por_ingrediente(ingrediente: str) -> list[dict]:
    """
    Busca recetas reales (vía TheMealDB) que usen el ingrediente dado.
    Acepta el nombre en español o inglés. Devuelve una lista con
    nombre, id y una URL a la receta completa.
    """
    ingrediente_normalizado = ingrediente.strip().lower()

    # 1° intento: tal cual como vino (por si ya está en inglés)
    resultado = _buscar(ingrediente_normalizado)
    if resultado:
        return resultado

    # 2° intento: traducido, si tenemos una traducción conocida
    traduccion = TRADUCCIONES.get(ingrediente_normalizado)
    if traduccion:
        return _buscar(traduccion)

    return []


@mcp.tool()
def obtener_detalle_receta(id_receta: str) -> dict:
    """Devuelve los ingredientes e instrucciones completas de una receta, dado su id."""
    resp = requests.get(f"{BASE_URL}/lookup.php", params={"i": id_receta}, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("meals"):
        return {"error": "Receta no encontrada"}

    meal = data["meals"][0]
    ingredientes = []
    for i in range(1, 21):
        nombre = meal.get(f"strIngredient{i}")
        medida = meal.get(f"strMeasure{i}")
        if nombre and nombre.strip():
            ingredientes.append(f"{medida.strip()} {nombre.strip()}".strip())

    return {
        "nombre": meal["strMeal"],
        "ingredientes": ingredientes,
        "instrucciones": meal["strInstructions"],
    }


if __name__ == "__main__":
    mcp.run()