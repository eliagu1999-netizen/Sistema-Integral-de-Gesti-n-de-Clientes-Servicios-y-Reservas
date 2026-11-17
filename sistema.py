"""
SISTEMA INTEGRAL DE GESTION DE CLIENTES Y SERVICIOS - SOFTWARE FJ

Modulo integrado:
- Entidad y Cliente
- Servicio abstracto y servicios especializados
- Calculadora de costos con impuesto, descuento y recargo
- Registro de eventos y errores en sistema.log
- Gestion de reservas
- Pruebas automatizadas
"""

from abc import ABC, abstractmethod
import logging
import re
import unittest


# =========================================================
# 1. CONFIGURACION DEL REGISTRO DE EVENTOS (LOGS)
# =========================================================

logging.basicConfig(
    filename="sistema.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
    force=True
)

logger = logging.getLogger("SistemaSoftwareFJ")


def registrar_evento(mensaje):
    """Registra un evento informativo del sistema."""
    logger.info(mensaje)


def registrar_error(mensaje):
    """Registra un error de validacion."""
    logger.error(mensaje)


# =========================================================
# 2. EXCEPCION PERSONALIZADA COMPARTIDA
# =========================================================

class ErrorValidacion(Exception):
    """Controla los errores de validacion del sistema."""
    pass


# =========================================================
# 3. CALCULADORA DE COSTOS
# =========================================================

class CalculadoraCostos:
    """
    Calcula costos con opciones de impuesto, descuento y recargo.
    Los porcentajes se expresan entre 0 y 1.
    """

    @staticmethod
    def validar_porcentaje(valor, nombre):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            mensaje = f"{nombre} debe ser numerico."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if not 0 <= valor <= 1:
            mensaje = f"{nombre} debe estar entre 0 y 1."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

    @staticmethod
    def validar_subtotal(subtotal):
        if isinstance(subtotal, bool) or not isinstance(subtotal, (int, float)):
            mensaje = "El subtotal debe ser numerico."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if subtotal < 0:
            mensaje = "El subtotal no puede ser negativo."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

    @staticmethod
    def calcular(subtotal, impuesto=0, descuento=0, recargo=0):
        """Metodo general con parametros opcionales."""
        try:
            CalculadoraCostos.validar_subtotal(subtotal)
            CalculadoraCostos.validar_porcentaje(impuesto, "El impuesto")
            CalculadoraCostos.validar_porcentaje(descuento, "El descuento")
            CalculadoraCostos.validar_porcentaje(recargo, "El recargo")

            total = subtotal * (1 - descuento)
            total *= (1 + impuesto)
            total *= (1 + recargo)
            resultado = round(total, 2)

            logger.info(
                "Calculo exitoso | Subtotal: %.2f | Impuesto: %.2f | "
                "Descuento: %.2f | Recargo: %.2f | Total: %.2f",
                subtotal, impuesto, descuento, recargo, resultado
            )
            return resultado

        except ErrorValidacion:
            raise
        except Exception:
            logger.exception("Error inesperado en el calculo de costos.")
            raise

    @staticmethod
    def calcular_basico(subtotal):
        registrar_evento("Solicitud de calculo basico.")
        return CalculadoraCostos.calcular(subtotal)

    @staticmethod
    def calcular_con_impuesto(subtotal, impuesto):
        registrar_evento("Solicitud de calculo con impuesto.")
        return CalculadoraCostos.calcular(subtotal, impuesto=impuesto)

    @staticmethod
    def calcular_con_descuento(subtotal, descuento):
        registrar_evento("Solicitud de calculo con descuento.")
        return CalculadoraCostos.calcular(subtotal, descuento=descuento)

    @staticmethod
    def calcular_completo(subtotal, impuesto=0, descuento=0, recargo=0):
        registrar_evento("Solicitud de calculo completo.")
        return CalculadoraCostos.calcular(
            subtotal,
            impuesto=impuesto,
            descuento=descuento,
            recargo=recargo
        )


# =========================================================
# 4. CLASE ABSTRACTA ENTIDAD
# =========================================================

class Entidad(ABC):
    def __init__(self, identificacion, nombre):
        if not isinstance(identificacion, str) or not identificacion.strip():
            mensaje = "La identificacion es obligatoria."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if not isinstance(nombre, str) or not nombre.strip():
            mensaje = "El nombre es obligatorio."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self._identificacion = identificacion.strip()
        self._nombre = nombre.strip()
        registrar_evento(
            f"Entidad creada: {self._nombre} ({self._identificacion})."
        )

    @property
    def identificacion(self):
        return self._identificacion

    @property
    def nombre(self):
        return self._nombre

    @abstractmethod
    def describir(self):
        pass


# =========================================================
# 5. CLASE CLIENTE
# =========================================================

class Cliente(Entidad):
    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion, nombre)
        self.__correo = None
        self.__telefono = None
        self.correo = correo
        self.telefono = telefono
        registrar_evento(f"Cliente registrado: {self.nombre}.")

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, nuevo_correo):
        if not isinstance(nuevo_correo, str):
            mensaje = "El correo debe ser texto."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", nuevo_correo):
            mensaje = "El correo electronico no es valido."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self.__correo = nuevo_correo

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, nuevo_telefono):
        if not isinstance(nuevo_telefono, str):
            mensaje = "El telefono debe ser texto."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if not re.fullmatch(r"\d{7,15}", nuevo_telefono):
            mensaje = "El telefono debe tener entre 7 y 15 digitos."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self.__telefono = nuevo_telefono

    def describir(self):
        return (
            f"Cliente: {self.nombre}\n"
            f"Identificacion: {self.identificacion}\n"
            f"Correo: {self.correo}\n"
            f"Telefono: {self.telefono}"
        )


# =========================================================
# 6. CLASE ABSTRACTA SERVICIO
# =========================================================

class Servicio(Entidad, ABC):
    def __init__(self, identificacion, nombre, tarifa):
        super().__init__(identificacion, nombre)

        if isinstance(tarifa, bool) or not isinstance(tarifa, (int, float)):
            mensaje = "La tarifa debe ser numerica."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if tarifa <= 0:
            mensaje = "La tarifa debe ser mayor que cero."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self._tarifa = tarifa
        registrar_evento(f"Servicio creado: {self.nombre}.")

    @property
    def tarifa(self):
        return self._tarifa

    def validar_duracion(self, duracion):
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)):
            mensaje = "La duracion debe ser numerica."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if duracion <= 0:
            mensaje = "La duracion debe ser mayor que cero."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

    def validar_parametros(self, duracion, **kwargs):
        self.validar_duracion(duracion)

    def calcular_total(self, subtotal, impuesto=0, descuento=0, recargo=0):
        """Conecta los servicios con la calculadora compartida."""
        return CalculadoraCostos.calcular_completo(
            subtotal,
            impuesto=impuesto,
            descuento=descuento,
            recargo=recargo
        )

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0,
                       recargo=0, **kwargs):
        pass

    @abstractmethod
    def describir(self):
        pass


# =========================================================
# 7. SERVICIO DE RESERVA DE SALAS
# =========================================================

class ReservaSala(Servicio):
    def validar_parametros(self, duracion, **kwargs):
        self.validar_duracion(duracion)
        capacidad = kwargs.get("capacidad")

        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            mensaje = "La capacidad debe ser un numero entero."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if capacidad <= 0:
            mensaje = "La capacidad debe ser mayor que cero."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

    def calcular_costo(self, duracion, impuesto=0, descuento=0,
                       recargo=0, **kwargs):
        self.validar_parametros(duracion, **kwargs)
        subtotal = self.tarifa * duracion
        total = self.calcular_total(subtotal, impuesto, descuento, recargo)
        registrar_evento(
            f"Costo calculado para reserva de sala: {self.nombre}."
        )
        return total

    def describir(self):
        return (
            f"Reserva de sala: {self.nombre}\n"
            f"Tarifa por hora: ${self.tarifa}"
        )


# =========================================================
# 8. SERVICIO DE ALQUILER DE EQUIPOS
# =========================================================

class AlquilerEquipo(Servicio):
    def validar_parametros(self, duracion, **kwargs):
        self.validar_duracion(duracion)
        cantidad = kwargs.get("cantidad")

        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            mensaje = "La cantidad debe ser un numero entero."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if cantidad <= 0:
            mensaje = "La cantidad debe ser mayor que cero."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

    def calcular_costo(self, duracion, impuesto=0, descuento=0,
                       recargo=0, **kwargs):
        self.validar_parametros(duracion, **kwargs)
        cantidad = kwargs["cantidad"]
        subtotal = self.tarifa * duracion * cantidad
        total = self.calcular_total(subtotal, impuesto, descuento, recargo)
        registrar_evento(
            f"Costo calculado para alquiler de equipos: {self.nombre}."
        )
        return total

    def describir(self):
        return (
            f"Alquiler de equipos: {self.nombre}\n"
            f"Tarifa por hora y equipo: ${self.tarifa}"
        )


# =========================================================
# 9. SERVICIO DE ASESORIAS
# =========================================================

class Asesoria(Servicio):
    def validar_parametros(self, duracion, **kwargs):
        self.validar_duracion(duracion)
        modalidad = kwargs.get("modalidad")

        if not isinstance(modalidad, str) or modalidad not in (
            "virtual", "presencial"
        ):
            mensaje = "La modalidad debe ser virtual o presencial."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

    def calcular_costo(self, duracion, impuesto=0, descuento=0,
                       recargo=0, **kwargs):
        self.validar_parametros(duracion, **kwargs)
        modalidad = kwargs["modalidad"]
        subtotal = self.tarifa * duracion

        if modalidad == "presencial":
            subtotal *= 1.10

        total = self.calcular_total(subtotal, impuesto, descuento, recargo)
        registrar_evento(
            f"Costo calculado para asesoria: {self.nombre}."
        )
        return total

    def describir(self):
        return (
            f"Asesoria especializada: {self.nombre}\n"
            f"Tarifa por hora: ${self.tarifa}"
        )
    # =========================================================
# 10. CLASE PARA GESTIONAR LAS RESERVAS
# =========================================================

class Reserva:
    """Representa una reserva realizada por un cliente."""

    def __init__(self, identificacion, cliente, servicio,
                 fecha, duracion, **parametros):

        if not isinstance(identificacion, str) or not identificacion.strip():
            mensaje = "La identificacion de la reserva es obligatoria."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if not isinstance(cliente, Cliente):
            mensaje = "La reserva debe tener un cliente valido."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if not isinstance(servicio, Servicio):
            mensaje = "La reserva debe tener un servicio valido."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if not isinstance(fecha, str) or not fecha.strip():
            mensaje = "La fecha de la reserva es obligatoria."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        servicio.validar_duracion(duracion)

        self.identificacion = identificacion.strip()
        self.cliente = cliente
        self.servicio = servicio
        self.fecha = fecha.strip()
        self.duracion = duracion
        self.parametros = parametros
        self.estado = "Pendiente"
        self.costo = None

        registrar_evento(
            f"Reserva creada: {self.identificacion}."
        )

    def confirmar(self):
        if self.estado != "Pendiente":
            mensaje = "Solo se pueden confirmar reservas pendientes."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self.estado = "Confirmada"

        registrar_evento(
            f"Reserva confirmada: {self.identificacion}."
        )

        return self.estado

    def cancelar(self):
        if self.estado == "Cancelada":
            mensaje = "La reserva ya se encuentra cancelada."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self.estado = "Cancelada"

        registrar_evento(
            f"Reserva cancelada: {self.identificacion}."
        )

        return self.estado

    def procesar(self, impuesto=0, descuento=0, recargo=0):
        if self.estado != "Confirmada":
            mensaje = "La reserva debe estar confirmada para procesarse."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self.costo = self.servicio.calcular_costo(
            self.duracion,
            impuesto=impuesto,
            descuento=descuento,
            recargo=recargo,
            **self.parametros
        )

        registrar_evento(
            f"Reserva procesada: {self.identificacion}."
        )

        return self.costo

    def describir(self):
        return (
            f"Reserva: {self.identificacion}\n"
            f"Cliente: {self.cliente.nombre}\n"
            f"Servicio: {self.servicio.nombre}\n"
            f"Fecha: {self.fecha}\n"
            f"Duracion: {self.duracion}\n"
            f"Estado: {self.estado}\n"
            f"Costo: {self.costo}"
        )


# =========================================================
# 11. PRUEBAS AUTOMATIZADAS INTEGRADAS
# =========================================================

class PruebasSistemaSoftwareFJ(unittest.TestCase):

    def setUp(self):
        registrar_evento("Inicio de una prueba automatizada.")

    # PRUEBA 1: REGISTRO DE CLIENTE VALIDO

    def test_01_registro_cliente_valido(self):
        cliente = Cliente(
            "123456789",
            "Carlos Perez",
            "carlos@gmail.com",
            "3001234567"
        )

        self.assertEqual(cliente.nombre, "Carlos Perez")

    # PRUEBA 2: CORREO INVALIDO

    def test_02_correo_invalido(self):
        with self.assertRaises(ErrorValidacion):
            Cliente(
                "987654321",
                "Maria Lopez",
                "correoincorrecto",
                "3101234567"
            )

    # PRUEBA 3: TELEFONO INVALIDO

    def test_03_telefono_invalido(self):
        with self.assertRaises(ErrorValidacion):
            Cliente(
                "456789123",
                "Ana Torres",
                "ana@gmail.com",
                "123"
            )

    # PRUEBA 4: CREACION DE LOS TRES SERVICIOS

    def test_04_creacion_tres_servicios(self):
        servicios = [
            ReservaSala("S01", "Sala de reuniones", 50000),
            AlquilerEquipo("S02", "Computador", 15000),
            Asesoria("S03", "Asesoria de software", 80000)
        ]

        self.assertEqual(len(servicios), 3)

    # PRUEBA 5: CALCULO DE COSTOS DE LOS SERVICIOS

    def test_05_calculo_costos_de_servicios(self):
        sala = ReservaSala("S11", "Sala", 50000)
        equipo = AlquilerEquipo("S12", "Computador", 15000)
        asesoria = Asesoria("S13", "Asesoria", 80000)

        self.assertEqual(
            sala.calcular_costo(
                2,
                impuesto=0.19,
                descuento=0.10,
                capacidad=10
            ),
            107100
        )

        self.assertEqual(
            equipo.calcular_costo(
                3,
                impuesto=0.19,
                descuento=0.05,
                cantidad=2
            ),
            101745
        )

        self.assertEqual(
            asesoria.calcular_costo(
                2,
                impuesto=0.19,
                modalidad="presencial"
            ),
            209440
        )

    # PRUEBA 6: DURACION INCORRECTA

    def test_06_duracion_incorrecta(self):
        sala = ReservaSala("S21", "Sala", 50000)

        with self.assertRaises(ErrorValidacion):
            sala.calcular_costo(-2, capacidad=10)

    # PRUEBA 7: CANTIDAD INCORRECTA

    def test_07_cantidad_incorrecta(self):
        equipo = AlquilerEquipo("S22", "Computador", 15000)

        with self.assertRaises(ErrorValidacion):
            equipo.calcular_costo(2, cantidad=0)

    # PRUEBA 8: MODALIDAD INCORRECTA

    def test_08_modalidad_incorrecta(self):
        asesoria = Asesoria("S23", "Asesoria", 80000)

        with self.assertRaises(ErrorValidacion):
            asesoria.calcular_costo(2, modalidad="incorrecta")

    # PRUEBA 9: TARIFA INCORRECTA

    def test_09_tarifa_incorrecta(self):
        with self.assertRaises(ErrorValidacion):
            ReservaSala("S04", "Sala invalida", -5000)

    # PRUEBA 10: IMPUESTO INCORRECTO

    def test_10_impuesto_incorrecto(self):
        with self.assertRaises(ErrorValidacion):
            CalculadoraCostos.calcular(
                100000,
                impuesto=1.5
            )

    # PRUEBA 11: CALCULO BASICO

    def test_11_calculo_basico(self):
        self.assertEqual(
            CalculadoraCostos.calcular_basico(100000),
            100000
        )

    # PRUEBA 12: CALCULO CON IMPUESTO

    def test_12_calculo_con_impuesto(self):
        self.assertEqual(
            CalculadoraCostos.calcular_con_impuesto(100000, 0.19),
            119000
        )

    # PRUEBA 13: CALCULO CON DESCUENTO

    def test_13_calculo_con_descuento(self):
        self.assertEqual(
            CalculadoraCostos.calcular_con_descuento(100000, 0.10),
            90000
        )

    # PRUEBA 14: CALCULO CON IMPUESTO Y DESCUENTO

    def test_14_calculo_con_impuesto_y_descuento(self):
        self.assertEqual(
            CalculadoraCostos.calcular_completo(
                100000,
                impuesto=0.19,
                descuento=0.10
            ),
            107100
        )

    # PRUEBA 15: CALCULO CON RECARGO

    def test_15_calculo_con_recargo(self):
        self.assertEqual(
            CalculadoraCostos.calcular_completo(
                100000,
                recargo=0.10
            ),
            110000
        )

    # PRUEBA 16: CALCULO CON TODOS LOS PARAMETROS

    def test_16_calculo_con_todos_los_parametros(self):
        self.assertEqual(
            CalculadoraCostos.calcular_completo(
                200000,
                impuesto=0.19,
                descuento=0.10,
                recargo=0.05
            ),
            224910
        )

    # PRUEBA 17: DESCUENTO INCORRECTO

    def test_17_descuento_incorrecto(self):
        with self.assertRaises(ErrorValidacion):
            CalculadoraCostos.calcular(
                100000,
                descuento=-0.20
            )

    # PRUEBA 18: SUBTOTAL NEGATIVO

    def test_18_subtotal_negativo(self):
        with self.assertRaises(ErrorValidacion):
            CalculadoraCostos.calcular(-50000)

    # PRUEBA 19: PARAMETRO NO NUMERICO

    def test_19_parametro_no_numerico(self):
        with self.assertRaises(ErrorValidacion):
            CalculadoraCostos.calcular(
                100000,
                impuesto="incorrecto"
            )

    # PRUEBA 20: CAPACIDAD INCORRECTA

    def test_20_capacidad_incorrecta(self):
        sala = ReservaSala("S31", "Sala", 50000)

        with self.assertRaises(ErrorValidacion):
            sala.calcular_costo(2, capacidad=0)

           # PRUEBA 21: CREAR RESERVA

    def test_21_crear_reserva(self):
        cliente = Cliente(
            "1001",
            "Carlos Perez",
            "carlos@gmail.com",
            "3001234567"
        )

        servicio = ReservaSala("S41", "Sala", 50000)

        reserva = Reserva(
            "R01",
            cliente,
            servicio,
            "20/11/2026",
            2,
            capacidad=10
        )

        self.assertEqual(reserva.estado, "Pendiente")

    # PRUEBA 22: CONFIRMAR RESERVA

    def test_22_confirmar_reserva(self):
        cliente = Cliente(
            "1002",
            "Maria Lopez",
            "maria@gmail.com",
            "3101234567"
        )

        servicio = ReservaSala("S42", "Sala", 50000)

        reserva = Reserva(
            "R02",
            cliente,
            servicio,
            "21/11/2026",
            2,
            capacidad=10
        )

        reserva.confirmar()

        self.assertEqual(reserva.estado, "Confirmada")

    # PRUEBA 23: CANCELAR RESERVA

    def test_23_cancelar_reserva(self):
        cliente = Cliente(
            "1003",
            "Ana Torres",
            "ana@gmail.com",
            "3201234567"
        )

        servicio = ReservaSala("S43", "Sala", 50000)

        reserva = Reserva(
            "R03",
            cliente,
            servicio,
            "22/11/2026",
            2,
            capacidad=10
        )

        reserva.cancelar()

        self.assertEqual(reserva.estado, "Cancelada")

    # PRUEBA 24: PROCESAR RESERVA

    def test_24_procesar_reserva(self):
        cliente = Cliente(
            "1004",
            "Pedro Ruiz",
            "pedro@gmail.com",
            "3009876543"
        )

        servicio = ReservaSala("S44", "Sala", 50000)

        reserva = Reserva(
            "R04",
            cliente,
            servicio,
            "23/11/2026",
            2,
            capacidad=10
        )

        reserva.confirmar()

        total = reserva.procesar(impuesto=0.19)

        self.assertEqual(total, 119000)

    # PRUEBA 25: RESERVA SIN CONFIRMAR

    def test_25_reserva_sin_confirmar(self):
        cliente = Cliente(
            "1005",
            "Laura Diaz",
            "laura@gmail.com",
            "3011234567"
        )

        servicio = ReservaSala("S45", "Sala", 50000)

        reserva = Reserva(
            "R05",
            cliente,
            servicio,
            "24/11/2026",
            2,
            capacidad=10
        )

        with self.assertRaises(ErrorValidacion):
            reserva.procesar()


# =========================================================
# 12. EJECUCION DEL PROGRAMA Y LAS PRUEBAS
# =========================================================

if __name__ == "__main__":

    print("==============================================")
    print("       SISTEMA INTEGRAL SOFTWARE FJ")
    print("==============================================")

    registrar_evento(
        "Inicio de ejecucion del sistema integrado."
    )

    # SERVICIOS DISPONIBLES

    print("\nSERVICIOS DISPONIBLES:")

    servicios_demo = [
        ReservaSala(
            "D01",
            "Sala de reuniones",
            50000
        ),

        AlquilerEquipo(
            "D02",
            "Computador",
            15000
        ),

        Asesoria(
            "D03",
            "Asesoria de software",
            80000
        )
    ]

    for servicio in servicios_demo:
        print("\n" + servicio.describir())

    # EJEMPLO DE GESTION DE UNA RESERVA

    print("\nEJEMPLO DE GESTION DE UNA RESERVA:")

    cliente_demo = Cliente(
        "9001",
        "Cliente de prueba",
        "cliente@gmail.com",
        "3001112233"
    )

    reserva_demo = Reserva(
        "R-DEMO",
        cliente_demo,
        servicios_demo[0],
        "25/11/2026",
        2,
        capacidad=10
    )

    reserva_demo.confirmar()

    costo_reserva = reserva_demo.procesar(
        impuesto=0.19
    )

    print(reserva_demo.describir())

    print(
        f"Costo final de la reserva: ${costo_reserva:,.2f}"
    )

    # EJEMPLO DE CALCULO COMPLETO

    print(
        "\nEJEMPLO DE CALCULO CON IMPUESTO, "
        "DESCUENTO Y RECARGO:"
    )

    ejemplo = CalculadoraCostos.calcular_completo(
        200000,
        impuesto=0.19,
        descuento=0.10,
        recargo=0.05
    )

    print(f"Total calculado: ${ejemplo:,.2f}")

    # EJECUCION DE LAS PRUEBAS AUTOMATIZADAS

    print("\n==============================================")
    print("       EJECUCION DE PRUEBAS AUTOMATIZADAS")
    print("==============================================")

    resultado = unittest.TextTestRunner(
        verbosity=2
    ).run(
        unittest.TestLoader().loadTestsFromTestCase(
            PruebasSistemaSoftwareFJ
        )
    )

    if resultado.wasSuccessful():

        logger.info(
            "Todas las pruebas automatizadas fueron aprobadas."
        )

        print(
            "\nTodas las pruebas finalizaron correctamente."
        )

    else:

        logger.error(
            "Se presentaron fallos en las pruebas automatizadas."
        )

        print(
            "\nSe encontraron errores. Revise los resultados."
        )

    registrar_evento(
        "Fin de ejecucion del sistema integrado."
    )

    print("\nArchivo de registro generado: sistema.log")
    print("==============================================")     