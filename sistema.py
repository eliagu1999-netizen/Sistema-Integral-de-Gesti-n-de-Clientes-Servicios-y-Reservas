"""
SISTEMA INTEGRAL DE GESTION DE CLIENTES Y SERVICIOS - SOFTWARE FJ
"""

from abc import ABC, abstractmethod
import logging
import re
import unittest
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# =========================================================
# 1. CONFIGURACION DE REGISTROS
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
    logger.info(mensaje)


def registrar_error(mensaje):
    logger.error(mensaje)


# =========================================================
# 2. EXCEPCION PERSONALIZADA
# =========================================================

class ErrorValidacion(Exception):
    pass


# =========================================================
# 3. CALCULADORA DE COSTOS
# =========================================================

class CalculadoraCostos:

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
        try:
            CalculadoraCostos.validar_subtotal(subtotal)
            CalculadoraCostos.validar_porcentaje(impuesto, "El impuesto")
            CalculadoraCostos.validar_porcentaje(descuento, "El descuento")
            CalculadoraCostos.validar_porcentaje(recargo, "El recargo")

            total = subtotal * (1 - descuento)
            total *= (1 + impuesto)
            total *= (1 + recargo)

            resultado = round(total, 2)

            registrar_evento(
                f"Calculo exitoso. Total: {resultado}"
            )

            return resultado

        except ErrorValidacion:
            raise

        except Exception:
            logger.exception("Error inesperado en el calculo.")
            raise

    @staticmethod
    def calcular_basico(subtotal):
        registrar_evento("Solicitud de calculo basico.")
        return CalculadoraCostos.calcular(subtotal)

    @staticmethod
    def calcular_con_impuesto(subtotal, impuesto):
        registrar_evento("Solicitud de calculo con impuesto.")
        return CalculadoraCostos.calcular(
            subtotal, impuesto=impuesto
        )

    @staticmethod
    def calcular_con_descuento(subtotal, descuento):
        registrar_evento("Solicitud de calculo con descuento.")
        return CalculadoraCostos.calcular(
            subtotal, descuento=descuento
        )

    @staticmethod
    def calcular_completo(
        subtotal, impuesto=0, descuento=0, recargo=0
    ):
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

        self._tarifa = float(tarifa)

    @property
    def tarifa(self):
        return self._tarifa

    def validar_duracion(self, duracion):
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)):
            raise ErrorValidacion("La duracion debe ser numerica.")

        if duracion <= 0:
            raise ErrorValidacion("La duracion debe ser mayor que cero.")

    @abstractmethod
    def validar_parametros(self, duracion, **parametros):
        pass

    @abstractmethod
    def calcular_costo(self, duracion, **parametros):
        pass

    @abstractmethod
    def describir(self):
        pass

# =========================================================
# 7. SERVICIO ESPECIALIZADO: RESERVA DE SALA
# =========================================================

class ReservaSala(Servicio):

    def validar_parametros(self, duracion, **parametros):
        self.validar_duracion(duracion)

        capacidad = parametros.get("capacidad")

        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ErrorValidacion("La capacidad debe ser un numero entero.")

        if capacidad <= 0:
            raise ErrorValidacion("La capacidad debe ser mayor que cero.")

        return True

    def calcular_costo(
        self, duracion, impuesto=0, descuento=0, recargo=0, **parametros
    ):
        self.validar_parametros(duracion, **parametros)

        subtotal = self.tarifa * duracion

        return CalculadoraCostos.calcular(
            subtotal, impuesto, descuento, recargo
        )

    def describir(self):
        return (
            f"Servicio: Reserva de sala\n"
            f"Nombre: {self.nombre}\n"
            f"Tarifa por hora: ${self.tarifa:,.2f}"
        )


# =========================================================
# 8. SERVICIO ESPECIALIZADO: ALQUILER DE EQUIPOS
# =========================================================

class AlquilerEquipo(Servicio):

    def validar_parametros(self, duracion, **parametros):
        self.validar_duracion(duracion)

        cantidad = parametros.get("cantidad")

        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise ErrorValidacion("La cantidad debe ser un numero entero.")

        if cantidad <= 0:
            raise ErrorValidacion("La cantidad debe ser mayor que cero.")

        return True

    def calcular_costo(
        self, duracion, impuesto=0, descuento=0, recargo=0, **parametros
    ):
        self.validar_parametros(duracion, **parametros)

        cantidad = parametros["cantidad"]
        subtotal = self.tarifa * duracion * cantidad

        return CalculadoraCostos.calcular(
            subtotal, impuesto, descuento, recargo
        )

    def describir(self):
        return (
            f"Servicio: Alquiler de equipos\n"
            f"Equipo: {self.nombre}\n"
            f"Tarifa por unidad y hora: ${self.tarifa:,.2f}"
        )


# =========================================================
# 9. SERVICIO ESPECIALIZADO: ASESORIA
# =========================================================

class Asesoria(Servicio):

    def validar_parametros(self, duracion, **parametros):
        self.validar_duracion(duracion)

        modalidad = parametros.get("modalidad")

        if modalidad not in ("virtual", "presencial"):
            raise ErrorValidacion(
                "La modalidad debe ser virtual o presencial."
            )

        return True

    def calcular_costo(
        self, duracion, impuesto=0, descuento=0, recargo=0, **parametros
    ):
        self.validar_parametros(duracion, **parametros)

        modalidad = parametros["modalidad"]

        subtotal = self.tarifa * duracion

        if modalidad == "presencial":
            subtotal += 15000

        return CalculadoraCostos.calcular(
            subtotal, impuesto, descuento, recargo
        )

    def describir(self):
        return (
            f"Servicio: Asesoria especializada\n"
            f"Nombre: {self.nombre}\n"
            f"Tarifa por hora: ${self.tarifa:,.2f}"
        )


# =========================================================
# 10. CLASE RESERVA
# =========================================================

class Reserva:

    def __init__(
        self, identificacion, cliente, servicio,
        fecha, duracion, **parametros
    ):

        if not isinstance(identificacion, str) or not identificacion.strip():
            raise ErrorValidacion(
                "La identificacion de la reserva es obligatoria."
            )

        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("La reserva necesita un cliente valido.")

        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("La reserva necesita un servicio valido.")

        if not isinstance(fecha, str) or not fecha.strip():
            raise ErrorValidacion("La fecha de la reserva es obligatoria.")

        try:
            datetime.strptime(fecha, "%d/%m/%Y")
        except ValueError as error:
            registrar_error(f"Fecha incorrecta: {error}")
            raise ErrorValidacion(
                "La fecha debe tener el formato DD/MM/AAAA."
            ) from error

        servicio.validar_parametros(duracion, **parametros)

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

        if self.estado in ("Cancelada", "Procesada"):
            mensaje = "No se puede cancelar esta reserva."
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

        try:
            self.costo = self.servicio.calcular_costo(
                self.duracion,
                impuesto=impuesto,
                descuento=descuento,
                recargo=recargo,
                **self.parametros
            )

        except ErrorValidacion as error:
            registrar_error(
                f"Error al procesar reserva {self.identificacion}: {error}"
            )
            raise

        else:
            self.estado = "Procesada"

            registrar_evento(
                f"Reserva procesada: {self.identificacion}."
            )

            return self.costo

        finally:
            registrar_evento(
                f"Finalizo intento de procesamiento: {self.identificacion}."
            )

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
# 11. GESTOR DEL SISTEMA Y LISTAS INTERNAS
# =========================================================

class SistemaGestion:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

        registrar_evento("Sistema de gestion inicializado.")

    # -----------------------------------------------------
    # REGISTRAR CLIENTES
    # -----------------------------------------------------

    def registrar_cliente(self, cliente):

        try:
            if not isinstance(cliente, Cliente):
                raise ErrorValidacion(
                    "Solo se pueden registrar objetos Cliente."
                )

            if any(
                c.identificacion == cliente.identificacion
                for c in self.clientes
            ):
                raise ErrorValidacion(
                    "Ya existe un cliente con esa identificacion."
                )

            self.clientes.append(cliente)

        except ErrorValidacion as error:
            registrar_error(
                f"Error al registrar cliente: {error}"
            )

            raise ErrorValidacion(
                "No fue posible registrar el cliente."
            ) from error

        else:
            registrar_evento(
                f"Cliente agregado: {cliente.nombre}."
            )
            return cliente

        finally:
            registrar_evento(
                "Finalizo el intento de registro de cliente."
            )

    # -----------------------------------------------------
    # REGISTRAR SERVICIOS
    # -----------------------------------------------------

    def registrar_servicio(self, servicio):

        if not isinstance(servicio, Servicio):
            mensaje = "Solo se pueden registrar objetos Servicio."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if any(
            s.identificacion == servicio.identificacion
            for s in self.servicios
        ):
            mensaje = "Ya existe un servicio con esa identificacion."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self.servicios.append(servicio)

        registrar_evento(
            f"Servicio agregado: {servicio.nombre}."
        )

        return servicio

    # -----------------------------------------------------
    # REGISTRAR RESERVAS
    # -----------------------------------------------------

    def registrar_reserva(self, reserva):

        if not isinstance(reserva, Reserva):
            mensaje = "Solo se pueden registrar objetos Reserva."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        if any(
            r.identificacion == reserva.identificacion
            for r in self.reservas
        ):
            mensaje = "Ya existe una reserva con esa identificacion."
            registrar_error(mensaje)
            raise ErrorValidacion(mensaje)

        self.reservas.append(reserva)

        registrar_evento(
            f"Reserva agregada: {reserva.identificacion}."
        )

        return reserva

    # -----------------------------------------------------
    # CONSULTAR CLIENTES
    # -----------------------------------------------------

    def consultar_clientes(self):
        return self.clientes.copy()

    # -----------------------------------------------------
    # CONSULTAR SERVICIOS
    # -----------------------------------------------------

    def consultar_servicios(self):
        return self.servicios.copy()

    # -----------------------------------------------------
    # CONSULTAR RESERVAS
    # -----------------------------------------------------

    def consultar_reservas(self):
        return self.reservas.copy()

    # -----------------------------------------------------
    # BUSCAR CLIENTE
    # -----------------------------------------------------

    def buscar_cliente(self, identificacion):

        for cliente in self.clientes:
            if cliente.identificacion == identificacion:
                return cliente

        raise ErrorValidacion(
            "No se encontro el cliente solicitado."
        )

    # -----------------------------------------------------
    # BUSCAR SERVICIO
    # -----------------------------------------------------

    def buscar_servicio(self, identificacion):

        for servicio in self.servicios:
            if servicio.identificacion == identificacion:
                return servicio

        raise ErrorValidacion(
            "No se encontro el servicio solicitado."
        )

    # -----------------------------------------------------
    # BUSCAR RESERVA
    # -----------------------------------------------------

    def buscar_reserva(self, identificacion):

        for reserva in self.reservas:
            if reserva.identificacion == identificacion:
                return reserva

        raise ErrorValidacion(
            "No se encontro la reserva solicitada."
        )

    # -----------------------------------------------------
    # MOSTRAR RESUMEN
    # -----------------------------------------------------

    def mostrar_resumen(self):

        return (
            f"Clientes registrados: {len(self.clientes)}\n"
            f"Servicios registrados: {len(self.servicios)}\n"
            f"Reservas registradas: {len(self.reservas)}"
        )

    # -----------------------------------------------------
    # REGISTRAR ERROR CON ENCADENAMIENTO
    # -----------------------------------------------------

    def registrar_cliente_seguro(self, cliente):

        try:
            return self.registrar_cliente(cliente)

        except ErrorValidacion as error:
            registrar_error(
                "Se produjo un error al intentar registrar un cliente."
            )

            raise ErrorValidacion(
                "Error controlado durante el registro del cliente."
            ) from error
            # =========================================================
# 12. FUNCION PARA EJECUTAR OPERACIONES
# =========================================================

def ejecutar_operacion(numero, descripcion, funcion):

    print(f"\nOperacion {numero}: {descripcion}")

    try:
        resultado = funcion()

    except ErrorValidacion as error:
        print(f"  Resultado controlado: {error}")
        registrar_error(
            f"Operacion {numero}: {error}"
        )

    except Exception as error:
        print(f"  Error inesperado: {error}")
        logger.exception(
            f"Error inesperado en operacion {numero}."
        )

    else:
        print(f"  Resultado: {resultado}")

    finally:
        registrar_evento(
            f"Finalizo la operacion {numero}: {descripcion}."
        )


# =========================================================
# 13. PRUEBAS AUTOMATIZADAS
# =========================================================

class PruebasSistemaSoftwareFJ(unittest.TestCase):

    def crear_cliente(self):
        return Cliente(
            "1001",
            "Carlos Perez",
            "carlos@gmail.com",
            "3001234567"
        )

    def crear_sala(self):
        return ReservaSala(
            "S01",
            "Sala de reuniones",
            50000
        )

    def crear_equipo(self):
        return AlquilerEquipo(
            "S02",
            "Computador portatil",
            15000
        )

    def crear_asesoria(self):
        return Asesoria(
            "S03",
            "Asesoria de software",
            80000
        )

    # PRUEBA 1

    def test_01_registro_cliente_valido(self):
        cliente = self.crear_cliente()
        self.assertEqual(cliente.nombre, "Carlos Perez")

    # PRUEBA 2

    def test_02_correo_invalido(self):
        with self.assertRaises(ErrorValidacion):
            Cliente(
                "1002", "Ana Ruiz",
                "correo_invalido", "3001234567"
            )

    # PRUEBA 3

    def test_03_telefono_invalido(self):
        with self.assertRaises(ErrorValidacion):
            Cliente(
                "1003", "Ana Ruiz",
                "ana@gmail.com", "abc123"
            )

    # PRUEBA 4

    def test_04_creacion_tres_servicios(self):
        self.assertIsInstance(self.crear_sala(), ReservaSala)
        self.assertIsInstance(self.crear_equipo(), AlquilerEquipo)
        self.assertIsInstance(self.crear_asesoria(), Asesoria)

    # PRUEBA 5

    def test_05_calculo_costos_de_servicios(self):
        sala = self.crear_sala()
        equipo = self.crear_equipo()
        asesoria = self.crear_asesoria()

        self.assertEqual(
            sala.calcular_costo(2, capacidad=10), 100000
        )

        self.assertEqual(
            equipo.calcular_costo(2, cantidad=2), 60000
        )

        self.assertEqual(
            asesoria.calcular_costo(2, modalidad="virtual"), 160000
        )

    # PRUEBA 6

    def test_06_duracion_incorrecta(self):
        with self.assertRaises(ErrorValidacion):
            self.crear_sala().calcular_costo(
                -2, capacidad=10
            )

    # PRUEBA 7

    def test_07_cantidad_incorrecta(self):
        with self.assertRaises(ErrorValidacion):
            self.crear_equipo().calcular_costo(
                2, cantidad=0
            )

    # PRUEBA 8

    def test_08_modalidad_incorrecta(self):
        with self.assertRaises(ErrorValidacion):
            self.crear_asesoria().calcular_costo(
                2, modalidad="incorrecta"
            )

    # PRUEBA 9

    def test_09_tarifa_incorrecta(self):
        with self.assertRaises(ErrorValidacion):
            ReservaSala("S10", "Sala", -5000)

    # PRUEBA 10

    def test_10_impuesto_incorrecto(self):
        with self.assertRaises(ErrorValidacion):
            CalculadoraCostos.calcular(
                100000, impuesto=1.5
            )

    # PRUEBA 11

    def test_11_calculo_basico(self):
        self.assertEqual(
            CalculadoraCostos.calcular_basico(100000),
            100000
        )

    # PRUEBA 12

    def test_12_calculo_con_impuesto(self):
        self.assertEqual(
            CalculadoraCostos.calcular_con_impuesto(
                100000, 0.19
            ),
            119000
        )

    # PRUEBA 13

    def test_13_calculo_con_descuento(self):
        self.assertEqual(
            CalculadoraCostos.calcular_con_descuento(
                100000, 0.10
            ),
            90000
        )

    # PRUEBA 14

    def test_14_calculo_con_impuesto_y_descuento(self):
        resultado = CalculadoraCostos.calcular(
            100000, impuesto=0.19, descuento=0.10
        )

        self.assertEqual(resultado, 107100)

    # PRUEBA 15

    def test_15_calculo_con_recargo(self):
        resultado = CalculadoraCostos.calcular(
            100000, recargo=0.05
        )

        self.assertEqual(resultado, 105000)

    # PRUEBA 16

    def test_16_calculo_con_todos_los_parametros(self):
        resultado = CalculadoraCostos.calcular_completo(
            200000,
            impuesto=0.19,
            descuento=0.10,
            recargo=0.05
        )

        self.assertEqual(resultado, 224910)

    # PRUEBA 17

    def test_17_descuento_incorrecto(self):
        with self.assertRaises(ErrorValidacion):
            CalculadoraCostos.calcular(
                100000, descuento=2
            )

    # PRUEBA 18

    def test_18_subtotal_negativo(self):
        with self.assertRaises(ErrorValidacion):
            CalculadoraCostos.calcular(-1000)

    # PRUEBA 19

    def test_19_parametro_no_numerico(self):
        with self.assertRaises(ErrorValidacion):
            CalculadoraCostos.calcular("incorrecto")

    # PRUEBA 20

    def test_20_capacidad_incorrecta(self):
        with self.assertRaises(ErrorValidacion):
            self.crear_sala().calcular_costo(
                2, capacidad=0
            )

    # PRUEBA 21

    def test_21_crear_reserva(self):
        reserva = Reserva(
            "R01",
            self.crear_cliente(),
            self.crear_sala(),
            "20/11/2026",
            2,
            capacidad=10
        )

        self.assertEqual(reserva.estado, "Pendiente")

    # PRUEBA 22

    def test_22_confirmar_reserva(self):
        reserva = Reserva(
            "R02",
            self.crear_cliente(),
            self.crear_sala(),
            "20/11/2026",
            2,
            capacidad=10
        )

        reserva.confirmar()

        self.assertEqual(reserva.estado, "Confirmada")

    # PRUEBA 23

    def test_23_cancelar_reserva(self):
        reserva = Reserva(
            "R03",
            self.crear_cliente(),
            self.crear_sala(),
            "20/11/2026",
            2,
            capacidad=10
        )

        reserva.cancelar()

        self.assertEqual(reserva.estado, "Cancelada")

    # PRUEBA 24

    def test_24_procesar_reserva(self):
        reserva = Reserva(
            "R04",
            self.crear_cliente(),
            self.crear_sala(),
            "20/11/2026",
            2,
            capacidad=10
        )

        reserva.confirmar()
        total = reserva.procesar(impuesto=0.19)

        self.assertEqual(total, 119000)
        self.assertEqual(reserva.estado, "Procesada")

    # PRUEBA 25

    def test_25_reserva_sin_confirmar(self):
        reserva = Reserva(
            "R05",
            self.crear_cliente(),
            self.crear_sala(),
            "20/11/2026",
            2,
            capacidad=10
        )

        with self.assertRaises(ErrorValidacion):
            reserva.procesar()
            # =========================================================
# 14. INTERFAZ GRAFICA DEL SISTEMA
# =========================================================

class AplicacionSoftwareFJ:

    def __init__(self, ventana, sistema):

        self.ventana = ventana
        self.sistema = sistema

        self.ventana.title(
            "Sistema Integral de Gestion - Software FJ"
        )

        self.ventana.geometry("950x650")
        self.ventana.minsize(800, 550)

        titulo = tk.Label(
            self.ventana,
            text="SISTEMA INTEGRAL DE GESTION",
            font=("Arial", 18, "bold"),
            bg="#17365D",
            fg="white",
            pady=15
        )

        titulo.pack(fill="x")

        subtitulo = tk.Label(
            self.ventana,
            text="Clientes, servicios y reservas - Software FJ",
            font=("Arial", 11)
        )

        subtitulo.pack(pady=8)

        self.pestanas = ttk.Notebook(self.ventana)
        self.pestanas.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=10
        )

        self.pestana_clientes = ttk.Frame(self.pestanas)
        self.pestana_servicios = ttk.Frame(self.pestanas)
        self.pestana_reservas = ttk.Frame(self.pestanas)
        self.pestana_consultas = ttk.Frame(self.pestanas)

        self.pestanas.add(
            self.pestana_clientes,
            text="Clientes"
        )

        self.pestanas.add(
            self.pestana_servicios,
            text="Servicios"
        )

        self.pestanas.add(
            self.pestana_reservas,
            text="Reservas"
        )

        self.pestanas.add(
            self.pestana_consultas,
            text="Consultas"
        )

        self.crear_pestana_clientes()
        self.crear_pestana_servicios()
        self.crear_pestana_reservas()
        self.crear_pestana_consultas()

    # -----------------------------------------------------
    # PESTAÑA DE CLIENTES
    # -----------------------------------------------------

    def crear_pestana_clientes(self):

        marco = ttk.LabelFrame(
            self.pestana_clientes,
            text="Registro de clientes",
            padding=15
        )

        marco.pack(fill="x", padx=15, pady=15)

        ttk.Label(marco, text="Identificacion:").grid(
            row=0, column=0, sticky="w", pady=5
        )

        self.id_cliente = ttk.Entry(marco, width=35)
        self.id_cliente.grid(row=0, column=1, pady=5)

        ttk.Label(marco, text="Nombre completo:").grid(
            row=1, column=0, sticky="w", pady=5
        )

        self.nombre_cliente = ttk.Entry(marco, width=35)
        self.nombre_cliente.grid(row=1, column=1, pady=5)

        ttk.Label(marco, text="Correo electronico:").grid(
            row=2, column=0, sticky="w", pady=5
        )

        self.correo_cliente = ttk.Entry(marco, width=35)
        self.correo_cliente.grid(row=2, column=1, pady=5)

        ttk.Label(marco, text="Telefono:").grid(
            row=3, column=0, sticky="w", pady=5
        )

        self.telefono_cliente = ttk.Entry(marco, width=35)
        self.telefono_cliente.grid(row=3, column=1, pady=5)

        ttk.Button(
            marco,
            text="Registrar cliente",
            command=self.registrar_cliente
        ).grid(row=4, column=1, pady=12, sticky="w")

        self.lista_clientes = ttk.Treeview(
            self.pestana_clientes,
            columns=("id", "nombre", "correo", "telefono"),
            show="headings",
            height=10
        )

        self.lista_clientes.heading("id", text="Identificacion")
        self.lista_clientes.heading("nombre", text="Nombre")
        self.lista_clientes.heading("correo", text="Correo")
        self.lista_clientes.heading("telefono", text="Telefono")

        self.lista_clientes.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.actualizar_clientes()

    def registrar_cliente(self):

        try:

            cliente = Cliente(
                self.id_cliente.get(),
                self.nombre_cliente.get(),
                self.correo_cliente.get(),
                self.telefono_cliente.get()
            )

            self.sistema.registrar_cliente(cliente)

            messagebox.showinfo(
                "Registro exitoso",
                "El cliente fue registrado correctamente."
            )

            self.id_cliente.delete(0, tk.END)
            self.nombre_cliente.delete(0, tk.END)
            self.correo_cliente.delete(0, tk.END)
            self.telefono_cliente.delete(0, tk.END)

            self.actualizar_clientes()

        except Exception as error:

            messagebox.showerror(
                "Error de registro",
                str(error)
            )

    def actualizar_clientes(self):

        for elemento in self.lista_clientes.get_children():
            self.lista_clientes.delete(elemento)

        for cliente in self.sistema.consultar_clientes():

            self.lista_clientes.insert(
                "",
                tk.END,
                values=(
                    cliente.identificacion,
                    cliente.nombre,
                    cliente.correo,
                    cliente.telefono
                )
            )

    # -----------------------------------------------------
    # PESTAÑA DE SERVICIOS
    # -----------------------------------------------------

    def crear_pestana_servicios(self):

        marco = ttk.LabelFrame(
            self.pestana_servicios,
            text="Registro de servicios",
            padding=15
        )

        marco.pack(fill="x", padx=15, pady=15)

        ttk.Label(marco, text="Codigo:").grid(
            row=0, column=0, sticky="w", pady=5
        )

        self.id_servicio = ttk.Entry(marco, width=30)
        self.id_servicio.grid(row=0, column=1, pady=5)

        ttk.Label(marco, text="Nombre:").grid(
            row=1, column=0, sticky="w", pady=5
        )

        self.nombre_servicio = ttk.Entry(marco, width=30)
        self.nombre_servicio.grid(row=1, column=1, pady=5)

        ttk.Label(marco, text="Tarifa:").grid(
            row=2, column=0, sticky="w", pady=5
        )

        self.tarifa_servicio = ttk.Entry(marco, width=30)
        self.tarifa_servicio.grid(row=2, column=1, pady=5)

        ttk.Label(marco, text="Tipo de servicio:").grid(
            row=3, column=0, sticky="w", pady=5
        )

        self.tipo_servicio = ttk.Combobox(
            marco,
            values=[
                "Sala de reuniones",
                "Alquiler de equipo",
                "Asesoria"
            ],
            state="readonly",
            width=27
        )

        self.tipo_servicio.grid(row=3, column=1, pady=5)
        self.tipo_servicio.current(0)

        ttk.Button(
            marco,
            text="Registrar servicio",
            command=self.registrar_servicio
        ).grid(row=4, column=1, pady=12, sticky="w")

        self.lista_servicios = ttk.Treeview(
            self.pestana_servicios,
            columns=("id", "nombre", "tarifa", "tipo"),
            show="headings",
            height=10
        )

        self.lista_servicios.heading("id", text="Codigo")
        self.lista_servicios.heading("nombre", text="Servicio")
        self.lista_servicios.heading("tarifa", text="Tarifa")
        self.lista_servicios.heading("tipo", text="Tipo")

        self.lista_servicios.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.actualizar_servicios()

    def registrar_servicio(self):

        try:

            identificacion = self.id_servicio.get()
            nombre = self.nombre_servicio.get()
            tarifa = float(self.tarifa_servicio.get())

            tipo = self.tipo_servicio.get()

            if tipo == "Sala de reuniones":

                servicio = ReservaSala(
                    identificacion,
                    nombre,
                    tarifa
                )

            elif tipo == "Alquiler de equipo":

                servicio = AlquilerEquipo(
                    identificacion,
                    nombre,
                    tarifa
                )

            else:

                servicio = Asesoria(
                    identificacion,
                    nombre,
                    tarifa
                )

            self.sistema.registrar_servicio(servicio)

            messagebox.showinfo(
                "Registro exitoso",
                "El servicio fue registrado correctamente."
            )

            self.id_servicio.delete(0, tk.END)
            self.nombre_servicio.delete(0, tk.END)
            self.tarifa_servicio.delete(0, tk.END)

            self.actualizar_servicios()
            self.actualizar_listas_reservas()

        except Exception as error:

            messagebox.showerror(
                "Error de registro",
                str(error)
            )

    def actualizar_servicios(self):

        for elemento in self.lista_servicios.get_children():
            self.lista_servicios.delete(elemento)

        for servicio in self.sistema.consultar_servicios():

            self.lista_servicios.insert(
                "",
                tk.END,
                values=(
                    servicio.identificacion,
                    servicio.nombre,
                    servicio.tarifa,
                    type(servicio).__name__
                )
            )

    # -----------------------------------------------------
    # PESTAÑA DE RESERVAS
    # -----------------------------------------------------

    def crear_pestana_reservas(self):

        marco = ttk.LabelFrame(
            self.pestana_reservas,
            text="Registro de reservas",
            padding=15
        )

        marco.pack(fill="x", padx=15, pady=15)

        ttk.Label(marco, text="Codigo de reserva:").grid(
            row=0, column=0, sticky="w", pady=5
        )

        self.id_reserva = ttk.Entry(marco, width=30)
        self.id_reserva.grid(row=0, column=1, pady=5)

        ttk.Label(marco, text="Cliente:").grid(
            row=1, column=0, sticky="w", pady=5
        )

        self.cliente_reserva = ttk.Combobox(
            marco,
            state="readonly",
            width=27
        )

        self.cliente_reserva.grid(row=1, column=1, pady=5)

        ttk.Label(marco, text="Servicio:").grid(
            row=2, column=0, sticky="w", pady=5
        )

        self.servicio_reserva = ttk.Combobox(
            marco,
            state="readonly",
            width=27
        )

        self.servicio_reserva.grid(row=2, column=1, pady=5)

        ttk.Label(marco, text="Fecha (DD/MM/AAAA):").grid(
            row=3, column=0, sticky="w", pady=5
        )

        self.fecha_reserva = ttk.Entry(marco, width=30)
        self.fecha_reserva.grid(row=3, column=1, pady=5)

        ttk.Label(marco, text="Duracion:").grid(
            row=4, column=0, sticky="w", pady=5
        )

        self.duracion_reserva = ttk.Entry(marco, width=30)
        self.duracion_reserva.grid(row=4, column=1, pady=5)

        ttk.Label(marco, text="Capacidad de sala:").grid(
            row=5, column=0, sticky="w", pady=5
        )

        self.capacidad_reserva = ttk.Entry(marco, width=30)
        self.capacidad_reserva.grid(row=5, column=1, pady=5)

        ttk.Label(marco, text="Cantidad de equipos:").grid(
            row=6, column=0, sticky="w", pady=5
        )

        self.cantidad_reserva = ttk.Entry(marco, width=30)
        self.cantidad_reserva.grid(row=6, column=1, pady=5)

        ttk.Label(marco, text="Modalidad de asesoria:").grid(
            row=7, column=0, sticky="w", pady=5
        )

        self.modalidad_reserva = ttk.Combobox(
            marco,
            values=["virtual", "presencial"],
            state="readonly",
            width=27
        )

        self.modalidad_reserva.grid(row=7, column=1, pady=5)

        ttk.Button(
            marco,
            text="Registrar reserva",
            command=self.registrar_reserva
        ).grid(row=8, column=1, pady=12, sticky="w")

        botones = ttk.Frame(self.pestana_reservas)
        botones.pack(pady=5)

        ttk.Button(
            botones,
            text="Confirmar reserva",
            command=self.confirmar_reserva
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Cancelar reserva",
            command=self.cancelar_reserva
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Procesar reserva",
            command=self.procesar_reserva
        ).pack(side="left", padx=5)

        self.lista_reservas = ttk.Treeview(
            self.pestana_reservas,
            columns=("id", "cliente", "servicio", "fecha", "estado"),
            show="headings",
            height=8
        )

        self.lista_reservas.heading("id", text="Codigo")
        self.lista_reservas.heading("cliente", text="Cliente")
        self.lista_reservas.heading("servicio", text="Servicio")
        self.lista_reservas.heading("fecha", text="Fecha")
        self.lista_reservas.heading("estado", text="Estado")

        self.lista_reservas.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.actualizar_listas_reservas()
        self.actualizar_reservas()

    def actualizar_listas_reservas(self):

        clientes = self.sistema.consultar_clientes()
        servicios = self.sistema.consultar_servicios()

        self.cliente_reserva["values"] = [
            f"{cliente.identificacion} - {cliente.nombre}"
            for cliente in clientes
        ]

        self.servicio_reserva["values"] = [
            f"{servicio.identificacion} - {servicio.nombre}"
            for servicio in servicios
        ]

    def registrar_reserva(self):

        try:

            clientes = self.sistema.consultar_clientes()
            servicios = self.sistema.consultar_servicios()

            cliente_seleccionado = self.cliente_reserva.get()
            servicio_seleccionado = self.servicio_reserva.get()

            if not cliente_seleccionado or not servicio_seleccionado:
                raise ErrorValidacion(
                    "Debe seleccionar un cliente y un servicio."
                )

            id_cliente = cliente_seleccionado.split(" - ")[0]
            id_servicio = servicio_seleccionado.split(" - ")[0]

            cliente = self.sistema.buscar_cliente(id_cliente)
            servicio = self.sistema.buscar_servicio(id_servicio)

            if cliente is None or servicio is None:
                raise ErrorValidacion(
                    "No se encontro el cliente o el servicio."
                )

            duracion = float(self.duracion_reserva.get())

            parametros = {}

            if isinstance(servicio, ReservaSala):

                parametros["capacidad"] = int(
                    self.capacidad_reserva.get()
                )

            elif isinstance(servicio, AlquilerEquipo):

                parametros["cantidad"] = int(
                    self.cantidad_reserva.get()
                )

            elif isinstance(servicio, Asesoria):

                parametros["modalidad"] = (
                    self.modalidad_reserva.get()
                )

            reserva = Reserva(
                self.id_reserva.get(),
                cliente,
                servicio,
                self.fecha_reserva.get(),
                duracion,
                **parametros
            )

            self.sistema.registrar_reserva(reserva)

            messagebox.showinfo(
                "Reserva registrada",
                "La reserva fue creada correctamente."
            )

            self.id_reserva.delete(0, tk.END)
            self.fecha_reserva.delete(0, tk.END)
            self.duracion_reserva.delete(0, tk.END)
            self.capacidad_reserva.delete(0, tk.END)
            self.cantidad_reserva.delete(0, tk.END)
            self.modalidad_reserva.set("")

            self.actualizar_reservas()

        except Exception as error:

            messagebox.showerror(
                "Error en la reserva",
                str(error)
            )

    def obtener_reserva_seleccionada(self):

        seleccion = self.lista_reservas.selection()

        if not seleccion:
            raise ErrorValidacion(
                "Seleccione una reserva de la lista."
            )

        valores = self.lista_reservas.item(
            seleccion[0], "values"
        )

        return self.sistema.buscar_reserva(valores[0])

    def confirmar_reserva(self):

        try:

            reserva = self.obtener_reserva_seleccionada()
            reserva.confirmar()

            messagebox.showinfo(
                "Reserva confirmada",
                "La reserva fue confirmada."
            )

            self.actualizar_reservas()

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

    def cancelar_reserva(self):

        try:

            reserva = self.obtener_reserva_seleccionada()
            reserva.cancelar()

            messagebox.showinfo(
                "Reserva cancelada",
                "La reserva fue cancelada."
            )

            self.actualizar_reservas()

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

    def procesar_reserva(self):

        try:

            reserva = self.obtener_reserva_seleccionada()

            total = reserva.procesar(
                impuesto=0.19
            )

            messagebox.showinfo(
                "Reserva procesada",
                f"El valor total de la reserva es: ${total:,.2f}"
            )

            self.actualizar_reservas()

        except Exception as error:

            messagebox.showerror(
                "Error al procesar",
                str(error)
            )

    def actualizar_reservas(self):

        for elemento in self.lista_reservas.get_children():
            self.lista_reservas.delete(elemento)

        for reserva in self.sistema.consultar_reservas():

            self.lista_reservas.insert(
                "",
                tk.END,
                values=(
                    reserva.identificacion,
                    reserva.cliente.nombre,
                    reserva.servicio.nombre,
                    reserva.fecha,
                    reserva.estado
                )
            )

    # -----------------------------------------------------
    # PESTAÑA DE CONSULTAS
    # -----------------------------------------------------

    def crear_pestana_consultas(self):

        marco = ttk.LabelFrame(
            self.pestana_consultas,
            text="Resumen del sistema",
            padding=20
        )

        marco.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Button(
            marco,
            text="Consultar resumen",
            command=self.mostrar_resumen
        ).pack(pady=10)

        self.texto_resumen = tk.Text(
            marco,
            height=18,
            width=90,
            font=("Arial", 11)
        )

        self.texto_resumen.pack(
            fill="both",
            expand=True,
            pady=10
        )

    def mostrar_resumen(self):

        resumen = self.sistema.mostrar_resumen()

        self.texto_resumen.delete("1.0", tk.END)

        self.texto_resumen.insert(
            tk.END,
            str(resumen)
        )


# =========================================================
# 15. EJECUCION DE LAS OPERACIONES DE DEMOSTRACION
# =========================================================

def ejecutar_demostracion():

    sistema = SistemaGestion()

    print("\n")
    print("=" * 60)
    print("SISTEMA INTEGRAL DE GESTION - SOFTWARE FJ")
    print("=" * 60)

    ejecutar_operacion(
        1,
        "Registro de cliente valido",
        lambda: sistema.registrar_cliente(
            Cliente(
                "1001",
                "Carlos Perez",
                "carlos@gmail.com",
                "3001234567"
            )
        )
    )

    ejecutar_operacion(
        2,
        "Registro de cliente con correo invalido",
        lambda: Cliente(
            "1002",
            "Ana Ruiz",
            "correo_invalido",
            "3001234567"
        )
    )

    ejecutar_operacion(
        3,
        "Creacion de sala de reuniones",
        lambda: sistema.registrar_servicio(
            ReservaSala(
                "S01",
                "Sala de reuniones",
                50000
            )
        )
    )

    ejecutar_operacion(
        4,
        "Creacion de alquiler de equipo",
        lambda: sistema.registrar_servicio(
            AlquilerEquipo(
                "S02",
                "Computador portatil",
                15000
            )
        )
    )

    ejecutar_operacion(
        5,
        "Creacion de asesoria",
        lambda: sistema.registrar_servicio(
            Asesoria(
                "S03",
                "Asesoria de software",
                80000
            )
        )
    )

    ejecutar_operacion(
        6,
        "Intento de crear servicio con tarifa incorrecta",
        lambda: ReservaSala(
            "S04",
            "Sala incorrecta",
            -5000
        )
    )

    ejecutar_operacion(
        7,
        "Registro de una reserva",
        lambda: sistema.registrar_reserva(
            Reserva(
                "R01",
                sistema.buscar_cliente("1001"),
                sistema.buscar_servicio("S01"),
                "25/11/2026",
                2,
                capacidad=10
            )
        )
    )

    ejecutar_operacion(
        8,
        "Confirmacion de reserva",
        lambda: sistema.buscar_reserva("R01").confirmar()
    )

    ejecutar_operacion(
        9,
        "Procesamiento de reserva",
        lambda: sistema.buscar_reserva("R01").procesar(
            impuesto=0.19
        )
    )

    ejecutar_operacion(
        10,
        "Creacion y cancelacion de otra reserva",
        lambda: sistema.registrar_reserva(
            Reserva(
                "R02",
                sistema.buscar_cliente("1001"),
                sistema.buscar_servicio("S02"),
                "26/11/2026",
                2,
                cantidad=2
            )
        )
    )

    ejecutar_operacion(
        11,
        "Intento de procesar una reserva sin confirmar",
        lambda: sistema.buscar_reserva("R02").procesar()
    )

    ejecutar_operacion(
        12,
        "Validacion de error y excepcion encadenada",
        lambda: sistema.registrar_cliente_seguro(
            "dato incorrecto"
        )
    )

    print("\nRESUMEN DE LA DEMOSTRACION")
    print(sistema.mostrar_resumen())

    return sistema


# =========================================================
# 16. INICIO DEL PROGRAMA
# =========================================================

def iniciar_programa():

    sistema = ejecutar_demostracion()

    print("\n")
    print("=" * 60)
    print("EJECUCION DE LAS PRUEBAS AUTOMATIZADAS")
    print("=" * 60)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        PruebasSistemaSoftwareFJ
    )

    resultado = unittest.TextTestRunner(
        verbosity=2
    ).run(suite)

    if resultado.wasSuccessful():
        print("\nTodas las pruebas finalizaron correctamente.")
    else:
        print("\nSe encontraron pruebas con errores.")

    print("\nIniciando la ventana del sistema...")

    try:

        ventana = tk.Tk()

        aplicacion = AplicacionSoftwareFJ(
            ventana,
            sistema
        )

        ventana.mainloop()

    except tk.TclError as error:

        print("\nNo fue posible abrir la ventana grafica.")
        print("Ejecute el programa en un computador con escritorio.")
        print(f"Detalle: {error}")


if __name__ == "__main__":
    iniciar_programa()

