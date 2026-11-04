import os
from datetime import date, timedelta

import pytest

import heladera


@pytest.fixture(autouse=True)
def heladera_temporal(tmp_path, monkeypatch):
    """Apunta heladera.py a una base de datos SQLite temporal y vacía en cada test."""
    db_temporal = tmp_path / "heladera_test.db"
    monkeypatch.setattr(heladera, "DB_NAME", str(db_temporal))
    heladera.init_db()
    yield
    if db_temporal.exists():
        os.remove(db_temporal)


def _fecha(dias_desde_hoy: int) -> str:
    """Devuelve una fecha en formato YYYY-MM-DD, relativa a hoy."""
    return (date.today() + timedelta(days=dias_desde_hoy)).strftime("%Y-%m-%d")


# =====================================================================
# 1. PRUEBAS UNITARIAS: agregar_alimento
# =====================================================================

class TestAgregarAlimento:
    def test_agregar_alimento_devuelve_id_valido(self):
        # Arrange
        vencimiento = _fecha(5)

        # Act
        nuevo_id = heladera.agregar_alimento("Leche", 1, "litro", vencimiento)

        # Assert
        assert nuevo_id is not None
        assert nuevo_id > 0

    def test_agregar_alimento_con_fecha_invalida_lanza_valueerror(self):
        # Arrange: formato incorrecto, debería ser YYYY-MM-DD
        fecha_invalida = "31/12/2026"

        # Act / Assert
        with pytest.raises(ValueError):
            heladera.agregar_alimento("Pan", 1, "unidad", fecha_invalida)


# =====================================================================
# 2. PRUEBAS UNITARIAS: listar_alimentos
# =====================================================================

class TestListarAlimentos:
    def test_listar_alimentos_vacio_al_inicio(self):
        # Arrange / Act
        alimentos = heladera.listar_alimentos()

        # Assert
        assert alimentos == []

    def test_listar_alimentos_no_incluye_consumidos_por_defecto(self):
        # Arrange
        id_leche = heladera.agregar_alimento("Leche", 1, "litro", _fecha(5))
        heladera.marcar_consumido(id_leche)

        # Act
        alimentos = heladera.listar_alimentos()

        # Assert
        assert alimentos == []

    def test_listar_alimentos_incluir_consumidos_true_los_muestra(self):
        # Arrange
        id_leche = heladera.agregar_alimento("Leche", 1, "litro", _fecha(5))
        heladera.marcar_consumido(id_leche)

        # Act
        alimentos = heladera.listar_alimentos(incluir_consumidos=True)

        # Assert
        assert len(alimentos) == 1
        assert alimentos[0]["consumido"] == 1


# =====================================================================
# 3. PRUEBAS UNITARIAS: obtener_por_vencer (casos borde de fecha)
# =====================================================================

class TestObtenerPorVencer:
    def test_obtener_por_vencer_incluye_alimento_en_el_limite_exacto(self):
        # Arrange: vence en exactamente 3 días, igual al límite por defecto
        heladera.agregar_alimento("Yogur", 2, "unidades", _fecha(3))

        # Act
        resultado = heladera.obtener_por_vencer(dias=3)

        # Assert
        assert len(resultado) == 1
        assert resultado[0]["nombre"] == "Yogur"

    def test_obtener_por_vencer_excluye_alimento_fuera_del_rango(self):
        # Arrange: vence en 10 días, fuera del límite de 3
        heladera.agregar_alimento("Manzanas", 6, "unidades", _fecha(10))

        # Act
        resultado = heladera.obtener_por_vencer(dias=3)

        # Assert
        assert resultado == []

    def test_obtener_por_vencer_incluye_alimentos_ya_vencidos(self):
        # Arrange: venció hace 2 días
        heladera.agregar_alimento("Queso", 1, "unidad", _fecha(-2))

        # Act
        resultado = heladera.obtener_por_vencer(dias=3)

        # Assert
        assert len(resultado) == 1
        assert resultado[0]["dias_restantes"] == -2


# =====================================================================
# 4. PRUEBAS UNITARIAS: marcar_consumido
# =====================================================================

class TestMarcarConsumido:
    def test_marcar_consumido_con_id_existente_devuelve_true(self):
        # Arrange
        id_alimento = heladera.agregar_alimento("Huevos", 12, "unidades", _fecha(7))

        # Act
        resultado = heladera.marcar_consumido(id_alimento)

        # Assert
        assert resultado is True

    def test_marcar_consumido_con_id_inexistente_devuelve_false(self):
        # Arrange
        id_inexistente = 9999

        # Act
        resultado = heladera.marcar_consumido(id_inexistente)

        # Assert
        assert resultado is False


# =====================================================================
# 5. PRUEBAS UNITARIAS: obtener_alimentos_vencidos
# =====================================================================

class TestObtenerAlimentosVencidos:
    def test_obtener_alimentos_vencidos_vacio_si_nada_vencio(self):
        # Arrange
        heladera.agregar_alimento("Manzanas", 6, "unidades", _fecha(10))

        # Act
        vencidos = heladera.obtener_alimentos_vencidos()

        # Assert
        assert vencidos == []

    def test_obtener_alimentos_vencidos_detecta_fecha_pasada(self):
        # Arrange
        heladera.agregar_alimento("Leche", 1, "litro", _fecha(-1))

        # Act
        vencidos = heladera.obtener_alimentos_vencidos()

        # Assert
        assert len(vencidos) == 1
        assert vencidos[0]["nombre"] == "Leche"
        assert "dias_restantes" not in vencidos[0]
