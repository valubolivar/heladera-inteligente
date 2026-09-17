from heladera import agregar_alimento, listar_alimentos, obtener_por_vencer, marcar_consumido, obtener_alimentos_vencidos

if __name__ == "__main__":
    agregar_alimento("Leche", 1, "litro", "2026-09-16")
    agregar_alimento("Manzanas", 6, "unidades", "2026-09-30")
    agregar_alimento("Yogur", 4, "unidades", "2026-09-15")

    print("Todos los alimentos:")
    for a in listar_alimentos():
        print(a)

    print("\nPor vencer en 3 días:")
    for a in obtener_por_vencer(dias=3):
        print(a)