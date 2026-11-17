"""
SISTEMA INTEGRAL DE GESTION DE CLIENTES Y SERVICIOS - SOFTWARE FJ

Modulo integrado:
- Entidad y Cliente
- Servicio abstracto y servicios especializados
- Calculadora de costos con impuesto, descuento y recargo
- Registro de eventos y errores en sistema.log
- Gestion de reservas
- Listas internas para clientes, servicios y reservas
- Manejo avanzado de excepciones
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
