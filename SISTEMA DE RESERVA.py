import logging
import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from datetime import datetime

# ============================================================
# 1. CONFIGURACIÓN DE LOGS
# ============================================================
logging.basicConfig(
    filename="logs_software_fj.txt", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================
class SoftwareFJError(Exception): 
    pass

class ValidationError(SoftwareFJError): 
    pass

class BusinessError(SoftwareFJError): 
    pass

# ============================================================
# 3. ARQUITECTURA ORIENTADA A OBJETOS (POO)
# ============================================================
class Entidad(ABC):
    @abstractmethod
    def validar(self): 
        pass

class Cliente(Entidad):
    def __init__(self, nombre, correo, telefono):
        self.__nombre = self.__validar_nombre(nombre)
        self.__correo = self.__validar_correo(correo)
        self.__telefono = self.__validar_telefono(telefono)

    def __validar_nombre(self, nombre):
        if not nombre or len(nombre.strip()) < 3:
            raise ValidationError("Nombre inválido: debe tener al menos 3 caracteres.")
        return nombre.strip()

    def __validar_correo(self, correo):
        if "@" not in correo or "." not in correo:
            raise ValidationError(f"Correo electrónico inválido: {correo}")
        return correo.strip()

    def __validar_telefono(self, tel):
        # Validación estricta: solo números y longitud mínima
        if not tel or not tel.isdigit() or len(tel) < 7:
            raise ValidationError("Teléfono obligatorio: ingrese solo números (mínimo 7 dígitos).")
        return tel

    # Encapsulamiento
    @property
    def nombre(self): return self.__nombre
    @property
    def correo(self): return self.__correo
    @property
    def telefono(self): return self.__telefono

    def validar(self): return True

# --- Polimorfismo en Servicios ---
class Servicio(ABC):
    def __init__(self, nombre, precio_base):
        self.nombre = nombre
        self.precio_base = precio_base

    @abstractmethod
    def calcular_costo(self, descuento=0): pass

    @abstractmethod
    def obtener_detalle(self): pass

class ReservaSala(Servicio):
    def __init__(self, horas):
        super().__init__("Reserva de Sala", 50000)
        self.horas = horas

    def calcular_costo(self, descuento=0):
        total = self.precio_base * self.horas
        return total - (total * (descuento / 100))

    def obtener_detalle(self):
        return f"Sala de juntas por {self.horas} horas"

class AlquilerEquipo(Servicio):
    def __init__(self, dias):
        super().__init__("Alquiler de Equipo", 30000)
        self.dias = dias

    def calcular_costo(self, descuento=0):
        # Aplicamos un cargo fijo por mantenimiento en este servicio
        return (self.precio_base * self.dias) + 5000

    def obtener_detalle(self):
        return f"Equipo tecnológico por {self.dias} días"

class AsesoriaEspecializada(Servicio):
    def __init__(self, nivel="Senior"):
        super().__init__("Asesoría", 120000)
        self.nivel = nivel

    def calcular_costo(self, descuento=0):
        # Sobrecarga simulada: costo basado en nivel
        multiplicador = 1.5 if self.nivel == "Senior" else 1.0
        return (self.precio_base * multiplicador) - descuento

    def obtener_detalle(self):
        return f"Asesoría técnica especializada ({self.nivel})"

# --- Clase Reserva ---
class Reserva:
    def __init__(self, cliente, servicio):
        self.cliente = cliente
        self.servicio = servicio
        self.estado = "Iniciada"

    def procesar_pago(self):
        try:
            costo_final = self.servicio.calcular_costo()
            if costo_final <= 0:
                raise BusinessError("Cálculo de costo inconsistente.")
            self.estado = "Confirmada"
            logging.info(f"ÉXITO: Cliente {self.cliente.nombre} reservó {self.servicio.nombre}")
            return costo_final
        except BusinessError as e:
            # Encadenamiento de excepciones
            raise SoftwareFJError("Fallo en el flujo de procesamiento") from e
        finally:
            print(f"Log: Intento de procesamiento para {self.cliente.nombre}")

# ============================================================
# 4. LÓGICA DE CONTROLADORES E INTERFAZ
# ============================================================
lista_clientes = []

def ejecutar_registro():
    try:
        nom, corr, tel = entry_nombre.get(), entry_correo.get(), entry_telefono.get()
        nuevo_cliente = Cliente(nom, corr, tel)
        lista_clientes.append(nuevo_cliente)
    except ValidationError as e:
        logging.error(f"Error de Validación: {e}")
        messagebox.showwarning("Dato Obligatorio", str(e))
    except Exception as e:
        logging.critical(f"Error inesperado: {e}")
        messagebox.showerror("Error Crítico", "Consulte al administrador.")
    else:
        # Solo se ejecuta si el bloque try fue exitoso
        tabla_clientes.insert("", tk.END, values=(nuevo_cliente.nombre, nuevo_cliente.correo, nuevo_cliente.telefono))
        combo_clientes["values"] = [c.nombre for c in lista_clientes]
        messagebox.showinfo("Éxito", f"Cliente {nuevo_cliente.nombre} registrado correctamente.")
    finally:
        # Limpieza de campos siempre ocurre
        entry_nombre.delete(0, tk.END)
        entry_correo.delete(0, tk.END)
        entry_telefono.delete(0, tk.END)

def ejecutar_reserva():
    try:
        nom_c = combo_clientes.get()
        tipo_s = combo_servicio.get()
        cant_str = entry_cantidad.get()
        
        if not cant_str.isdigit():
            raise BusinessError("La cantidad de horas/días debe ser un número entero.")
        
        cliente = next((c for c in lista_clientes if c.nombre == nom_c), None)
        if not cliente:
            raise BusinessError("Debe seleccionar un cliente registrado.")

        cantidad = int(cant_str)
        if tipo_s == "Sala": s = ReservaSala(cantidad)
        elif tipo_s == "Equipo": s = AlquilerEquipo(cantidad)
        elif tipo_s == "Asesoría": s = AsesoriaEspecializada()
        else: raise BusinessError("Debe seleccionar un tipo de servicio.")

        reserva = Reserva(cliente, s)
        total = reserva.procesar_pago()
        
        tabla_reservas.insert("", tk.END, values=(cliente.nombre, s.obtener_detalle(), f"${total}"))
        messagebox.showinfo("Reserva Confirmada", f"Cliente: {cliente.nombre}\nServicio: {tipo_s}\nTotal: ${total}")
    except (BusinessError, SoftwareFJError) as e:
        logging.error(f"Error de Negocio: {e}")
        messagebox.showerror("No se pudo reservar", str(e))
    except Exception as e:
        logging.error(f"Fallo general: {e}")
        messagebox.showerror("Error", "Ocurrió un problema procesando la reserva.")

# ============================================================
# 5. CONSTRUCCIÓN DE LA UI (Tkinter + TTK)
# ============================================================
app = tk.Tk()
app.title("Software FJ - Gestión Integral v2.0")
app.geometry("800x650")

estilo = ttk.Style()
estilo.theme_use("clam")

nb = ttk.Notebook(app)
nb.pack(fill="both", expand=True)

# --- Pestaña de Clientes ---
p1 = ttk.Frame(nb, padding=20)
nb.add(p1, text="Registro de Clientes")

ttk.Label(p1, text="Nombre Completo:", font=("Arial", 10, "bold")).pack(pady=2)
entry_nombre = ttk.Entry(p1, width=40); entry_nombre.pack(pady=2)

ttk.Label(p1, text="Correo Electrónico:", font=("Arial", 10, "bold")).pack(pady=2)
entry_correo = ttk.Entry(p1, width=40); entry_correo.pack(pady=2)

ttk.Label(p1, text="Teléfono (Obligatorio):", font=("Arial", 10, "bold")).pack(pady=2)
entry_telefono = ttk.Entry(p1, width=40); entry_telefono.pack(pady=2)

ttk.Button(p1, text="Registrar Cliente", command=ejecutar_registro).pack(pady=15)

columnas_c = ("N", "C", "T")
tabla_clientes = ttk.Treeview(p1, columns=columnas_c, show="headings", height=8)
tabla_clientes.heading("N", text="Nombre"); tabla_clientes.heading("C", text="Email"); tabla_clientes.heading("T", text="Teléfono")
tabla_clientes.column("N", width=200); tabla_clientes.column("C", width=200); tabla_clientes.column("T", width=150)
tabla_clientes.pack(fill="x", pady=5)

# --- Pestaña de Reservas ---
p2 = ttk.Frame(nb, padding=20)
nb.add(p2, text="Módulo de Reservas")

ttk.Label(p2, text="Seleccionar Cliente:", font=("Arial", 10, "bold")).pack(pady=2)
combo_clientes = ttk.Combobox(p2, state="readonly", width=37); combo_clientes.pack(pady=2)

ttk.Label(p2, text="Tipo de Servicio:", font=("Arial", 10, "bold")).pack(pady=2)
combo_servicio = ttk.Combobox(p2, values=["Sala", "Equipo", "Asesoría"], state="readonly", width=37); combo_servicio.pack(pady=2)

ttk.Label(p2, text="Cantidad (Horas / Días):", font=("Arial", 10, "bold")).pack(pady=2)
entry_cantidad = ttk.Entry(p2, width=40); entry_cantidad.pack(pady=2)

ttk.Button(p2, text="Procesar Reserva", command=ejecutar_reserva).pack(pady=15)

columnas_r = ("Cl", "De", "To")
tabla_reservas = ttk.Treeview(p2, columns=columnas_r, show="headings", height=8)
tabla_reservas.heading("Cl", text="Cliente"); tabla_reservas.heading("De", text="Servicio / Detalle"); tabla_reservas.heading("To", text="Total Pago")
tabla_reservas.column("Cl", width=150); tabla_reservas.column("De", width=300); tabla_reservas.column("To", width=100)
tabla_reservas.pack(fill="x", pady=5)

app.mainloop()
