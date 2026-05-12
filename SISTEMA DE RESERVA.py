# ================================
# SOFTWARE FJ
# Sistema de Clientes, Servicios y Reservas
# Interfaz con Tkinter + TTK
# ================================

from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import ttk, messagebox


# ================================
# CONFIGURACIÓN LOGS
# ================================

logging.basicConfig(
    filename="logs.txt",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ================================
# EXCEPCIONES PERSONALIZADAS
# ================================

class ClienteError(Exception):
    pass


class ServicioError(Exception):
    pass


class ReservaError(Exception):
    pass


# ================================
# CLASE ABSTRACTA ENTIDAD
# ================================

class Entidad(ABC):

    @abstractmethod
    def mostrar_info(self):
        pass


# ================================
# CLASE CLIENTE
# ================================

class Cliente(Entidad):

    def __init__(self, nombre, correo):
        self.__nombre = nombre
        self.__correo = correo

    def get_nombre(self):
        return self.__nombre

    def get_correo(self):
        return self.__correo

    def set_nombre(self, nombre):

        if not nombre.strip():
            raise ClienteError(
                "El nombre no puede estar vacío"
            )

        self.__nombre = nombre

    def set_correo(self, correo):

        if "@" not in correo:
            raise ClienteError(
                "Correo inválido"
            )

        self.__correo = correo

    def mostrar_info(self):

        return (
            f"Cliente: {self.__nombre} "
            f"| Correo: {self.__correo}"
        )


# ================================
# CLASE ABSTRACTA SERVICIO
# ================================

class Servicio(ABC):

    def __init__(self, nombre, precio_base):

        self.nombre = nombre
        self.precio_base = precio_base

    @abstractmethod
    def calcular_costo(self):
        pass

    @abstractmethod
    def descripcion(self):
        pass


# ================================
# SERVICIO: RESERVA SALA
# ================================

class ReservaSala(Servicio):

    def __init__(self, nombre, precio_base, horas):

        super().__init__(nombre, precio_base)
        self.horas = horas

    def calcular_costo(self):

        return self.precio_base * self.horas

    def descripcion(self):

        return (
            f"Reserva de sala "
            f"por {self.horas} horas"
        )


# ================================
# SERVICIO: ALQUILER EQUIPO
# ================================

class AlquilerEquipo(Servicio):

    def __init__(self, nombre, precio_base, dias):

        super().__init__(nombre, precio_base)
        self.dias = dias

    def calcular_costo(self):

        return self.precio_base * self.dias

    def descripcion(self):

        return (
            f"Alquiler por "
            f"{self.dias} días"
        )


# ================================
# SERVICIO: ASESORÍA
# ================================

class Asesoria(Servicio):

    def __init__(self, nombre, precio_base, nivel):

        super().__init__(nombre, precio_base)
        self.nivel = nivel

    def calcular_costo(self):

        if self.nivel.lower() == "avanzada":
            return self.precio_base * 2

        return self.precio_base

    def descripcion(self):

        return (
            f"Asesoría nivel "
            f"{self.nivel}"
        )


# ================================
# CLASE RESERVA
# ================================

class Reserva:

    def __init__(self, cliente, servicio, duracion):

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"

    def confirmar(self):

        self.estado = "Confirmada"

    def cancelar(self):

        self.estado = "Cancelada"

    def procesar(self):

        try:

            if self.estado == "Cancelada":

                raise ReservaError(
                    "No se puede procesar "
                    "una reserva cancelada"
                )

            costo = self.servicio.calcular_costo()

            if costo <= 0:

                raise ReservaError(
                    "Costo inválido"
                )

            self.confirmar()

            return (
                f"Reserva confirmada\n"
                f"Cliente: "
                f"{self.cliente.get_nombre()}\n"
                f"Servicio: "
                f"{self.servicio.descripcion()}\n"
                f"Costo: ${costo}"
            )

        except Exception as e:

            logging.error(e)

            return f"Error: {e}"


# ================================
# LISTAS DEL SISTEMA
# ================================

clientes = []
servicios = []
reservas = []


# ================================
# FUNCIONES INTERFAZ
# ================================

def registrar_cliente():

    try:

        nombre = entry_nombre.get()
        correo = entry_correo.get()

        cliente = Cliente(nombre, correo)

        clientes.append(cliente)

        tabla_clientes.insert(
            "",
            tk.END,
            values=(
                cliente.get_nombre(),
                cliente.get_correo()
            )
        )

        messagebox.showinfo(
            "Éxito",
            "Cliente registrado correctamente"
        )

        entry_nombre.delete(0, tk.END)
        entry_correo.delete(0, tk.END)

    except Exception as e:

        logging.error(e)

        messagebox.showerror(
            "Error",
            str(e)
        )


# ================================
# VENTANA PRINCIPAL
# ================================

ventana = tk.Tk()

ventana.title("Software FJ")
ventana.geometry("700x500")
ventana.resizable(False, False)


# ================================
# ESTILO TTK
# ================================

style = ttk.Style()
style.theme_use("clam")


# ================================
# FRAME PRINCIPAL
# ================================

frame = ttk.Frame(
    ventana,
    padding=20
)

frame.pack(
    fill="both",
    expand=True
)


# ================================
# TÍTULO
# ================================

titulo = ttk.Label(
    frame,
    text="SOFTWARE FJ",
    font=("Arial", 20, "bold")
)

titulo.pack(pady=10)


# ================================
# FORMULARIO CLIENTES
# ================================

label_nombre = ttk.Label(
    frame,
    text="Nombre"
)

label_nombre.pack()

entry_nombre = ttk.Entry(
    frame,
    width=40
)

entry_nombre.pack(pady=5)


label_correo = ttk.Label(
    frame,
    text="Correo"
)

label_correo.pack()

entry_correo = ttk.Entry(
    frame,
    width=40
)

entry_correo.pack(pady=5)


# ================================
# BOTÓN REGISTRO
# ================================

btn_registrar = ttk.Button(
    frame,
    text="Registrar Cliente",
    command=registrar_cliente
)

btn_registrar.pack(pady=10)


# ================================
# TABLA CLIENTES
# ================================

columnas = (
    "Nombre",
    "Correo"
)

tabla_clientes = ttk.Treeview(
    frame,
    columns=columnas,
    show="headings",
    height=10
)

for col in columnas:

    tabla_clientes.heading(
        col,
        text=col
    )

    tabla_clientes.column(
        col,
        width=250
    )

tabla_clientes.pack(pady=20)


# ================================
# EJECUCIÓN
# ================================

ventana.mainloop()
