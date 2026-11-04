# Documentación técnica: la Skill `sugerir_receta_antivencimiento`

## La idea, en una analogía

Pensá en la heladera como un local de comida con un cartel de "¡Oferta por vencer hoy!". El agente no ordena los alimentos por orden alfabético ni por cuáles llegaron primero: ordena por **urgencia**, igual que un verdulero que acomoda la fruta más madura adelante del mostrador para que se venda antes de que se pudra. `obtener_por_vencer` es ese cartel: calcula, para cada alimento, cuántos días le quedan (`dias_restantes`) y filtra solo los urgentes.

## Por qué `dias_restantes <= dias` y no `dias_restantes >= 0`

Un alimento vencido ayer tiene `dias_restantes = -1`. Si filtráramos con `dias_restantes >= 0`, ese alimento directamente **desaparecería** de la lista de "por vencer" apenas cruzara la fecha — justo cuando más necesita atención. Por eso el filtro es `dias_restantes <= dias`: un número cada vez más negativo sigue siendo "menor o igual" al límite, así que un alimento vencido nunca se pierde de la lista hasta que alguien lo marca como consumido (o se borra explícitamente). Es la misma lógica que separa `obtener_por_vencer` (incluye vencidos) de `obtener_alimentos_vencidos` (sólo vencidos): la primera es una alerta temprana, la segunda es la lista de "esto ya hay que tirarlo o usarlo ya".

## Contrato de la Skill (resumen de `agente_heladera.agent.md`)

| | |
|---|---|
| **Entrada** | Ninguna obligatoria (opcional: días de margen) |
| **Herramientas que usa** | `tool_obtener_alimentos_vencidos`, `tool_obtener_por_vencer` (MCP heladera) → `buscar_recetas_por_ingrediente`, `obtener_detalle_receta` (MCP recetas) |
| **Salida** | Alerta de vencidos + alimento priorizado + receta real con ingredientes e instrucciones |
| **Restricción clave** | Nunca inventa una receta: si `buscar_recetas_por_ingrediente` no devuelve nada, prueba con el siguiente alimento en vez de alucinar una |

## Por qué el orden de las llamadas importa

El flujo obligatorio pide revisar primero `tool_obtener_alimentos_vencidos` y recién después `tool_obtener_por_vencer`. Si se invirtiera el orden, el agente podría terminar recomendando una receta para un alimento que vence en 2 días sin haber avisado antes que ya hay otro vencido desde ayer — técnicamente "no es un error", pero contradice el objetivo real del agente (evitar desperdicio), que es lo que esta Skill está documentando como regla explícita y no dejando a criterio del modelo en cada corrida.
