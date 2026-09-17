# Heladera Inteligente

Organizador de alimentos que ayuda a decidir qué cocinar antes de que algo se venza. Permite cargar alimentos con su fecha de vencimiento, consultar cuáles están por vencer o ya vencidos, y — usando un agente de IA con MCP — buscar recetas reales que aprovechen esos ingredientes.

Proyecto realizado para el Parcial 1 de "Programación con IA Generativa" (UP).

## Arquitectura

El proyecto sigue el patrón MCP local + datos propios + MCP externo:

GitHub Copilot (Agent) se conecta a `heladera_mcp_server.py` (MCP local), que usa `heladera.py` para leer y escribir en `heladera.db` (SQLite). También se conecta a `recetas_mcp_server.py` (MCP externo), que consulta la API pública TheMealDB (https://www.themealdb.com).

- `heladera.py` — capa de datos y lógica de negocio. Persistencia en SQLite.
- `heladera_mcp_server.py` — servidor MCP que expone las funciones de `heladera.py` como herramientas para el agente.
- `recetas_mcp_server.py` — servidor MCP que consulta la API pública TheMealDB para buscar recetas reales según un ingrediente.
- `main.py` — script de prueba manual de las funciones de `heladera.py`.
- `.vscode/mcp.json` — configuración de ambos servidores MCP para VS Code / GitHub Copilot.

## Funcionalidades

- Agregar alimentos con nombre, cantidad, unidad y fecha de vencimiento.
- Listar todos los alimentos cargados.
- Consultar qué alimentos están por vencer dentro de N días.
- Consultar qué alimentos ya vencieron.
- Marcar un alimento como consumido.
- Buscar recetas reales (vía TheMealDB) que usen un ingrediente dado.
- Ver el detalle completo (ingredientes e instrucciones) de una receta.

## Requisitos

- Python 3.11 o superior
- Visual Studio Code
- Extensión GitHub Copilot / GitHub Copilot Chat

## Instalación

Clonar el repositorio:

    git clone https://github.com/valubolivar/heladera-inteligente.git
    cd heladera-inteligente

Crear y activar entorno virtual:

    python -m venv .venv
    .venv\Scripts\Activate.ps1

Instalar dependencias:

    pip install -r requirements.txt

## Cómo correrlo

**1. Probar las funciones de la heladera directamente:**

    python main.py

**2. Usarlo con el agente de IA (recomendado):**

1. Abrir la carpeta del proyecto en VS Code.
2. VS Code detecta automáticamente los servidores definidos en `.vscode/mcp.json` (`heladera` y `recetas`).
3. Abrir el panel de Copilot Chat y seleccionar el modo Agent.
4. Pedirle, por ejemplo:

   > Fijate qué alimentos están por vencer en mi heladera y buscame una receta real que use el que vence antes

El agente va a consultar primero el MCP de la heladera (qué vence antes) y después el MCP de recetas (qué se puede cocinar con eso), devolviendo una respuesta que combina ambas fuentes.

## Estructura del proyecto

- primer parcial/
  - .vscode/mcp.json — Configuración de los servidores MCP
  - heladera.py — Capa de datos (SQLite)
  - heladera_mcp_server.py — Servidor MCP local (tools de la heladera)
  - recetas_mcp_server.py — Servidor MCP externo (TheMealDB API)
  - main.py — Script de prueba manual
  - requirements.txt
  - README.md

## Tecnologías

- Python 3
- SQLite
- MCP Python SDK (mcp<2)
- Requests (consumo de API externa)
- TheMealDB (API pública de recetas)
- GitHub Copilot (modo Agent)