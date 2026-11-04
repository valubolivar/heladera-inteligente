from datetime import date, timedelta

from heladera import agregar_alimento, listar_alimentos, obtener_por_vencer, marcar_consumido, obtener_alimentos_vencidos


def _fecha(dias_desde_hoy: int) -> str:
    """Devuelve una fecha en formato YYYY-MM-DD, relativa a hoy."""
    return (date.today() + timedelta(days=dias_desde_hoy)).strftime("%Y-%m-%d")


if __name__ == "__main__":
    # Un alimento ya vencido (para mostrar la alerta del agente)
    agregar_alimento("Yogur", 2, "unidades", _fecha(-2))
    # Un alimento por vencer pronto (el que el agente debería priorizar)
    agregar_alimento("Leche", 1, "litro", _fecha(1))
    # Un alimento con margen, lejos de vencer
    agregar_alimento("Manzanas", 6, "unidades", _fecha(15))

    print("Todos los alimentos:")
    for a in listar_alimentos():
        print(a)

    print("\nPor vencer en 3 días:")
    for a in obtener_por_vencer(dias=3):
        print(a)

    print("\nYa vencidos:")
    for a in obtener_alimentos_vencidos():
        print(a)