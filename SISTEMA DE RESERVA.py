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
# 2. EXCEPCIONES PERSONALIZADAS (Corregidas)
# ============================================================
class SoftwareFJError(Exception): 
    pass

class ValidationError(SoftwareFJError): 
    pass

class BusinessError(SoftwareFJError): 
    pass

# ============================================================
# 3. ARQUITECTURA ORIENTADA A OBJETOS
# ============================================================
class Entidad(ABC):
    @abstractmethod
    def validar(self): 
        pass

class Cliente(Entidad):
    def __init__(self, nombre, correo):
        self.__nombre = self.__validar_nombre(nombre)
        self.__correo = self.__validar_correo(correo)

    def __validar_nombre(self, nombre):
        if not nombre or len(nombre) < 3:
            raise ValidationError("Nombre de cliente demasiado corto o vacío.")
        return nombre

    def __validar_correo(self, correo):
        if "@" not in correo or "." not in correo:
            raise ValidationError(f"Estructura de correo inválida: {correo}")
        return correo

    @property
    def nombre(self): return self.__nombre
    
    @property
    def correo(self): return self.__correo

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
        return f"Sala por {self.horas} horas"

class AlquilerEquipo(Servicio):
    def __init__(self, dias):
        super().__init__("Alquiler de Equipo", 30000)
        self.dias = dias

    def calcular_costo(self, descuento=0):
        return (self.precio_base * self.dias) * 0.90 

    def obtener_detalle(self):
        return f"Equipo por {self.dias} días"

class AsesoriaEspecializada(Servicio):
    def __init__(self, nivel="Senior"):
        super().__init__("Asesoría", 100000)
        self.nivel = nivel

    def calcular_costo(self, descuento=0):
        multiplicador = 2 if self.nivel == "Senior" else 1
        return (self.precio_base * multiplicador) - descuento

    def obtener_detalle(self):
        return f"Asesoría nivel {self.nivel}"

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
                raise BusinessError("Costo de servicio inválido.")
            self.estado = "Confirmada"
            logging.info(f"Reserva: {self.cliente.nombre} | Total: {costo_final}")
            return costo_final
        except BusinessError as e:
            raise SoftwareFJError("Error en procesamiento") from e
        finally:
            print("Procesamiento de reserva finalizado.")

# ============================================================
# 4. GESTIÓN DE INTERFAZ Y LÓGICA
# ============================================================
lista_clientes = []

def ejecutar_registro():
    try:
        nombre, correo = entry_nombre.get(), entry_correo.get()
        nuevo_cliente = Cliente(nombre, correo)
        lista_clientes.append(nuevo_cliente)
    except ValidationError as e:
        logging.error(f"Validación: {e}")
        messagebox.showwarning("Error de Datos", str(e))
    else:
        tabla_clientes.insert("", tk.END, values=(nuevo_cliente.nombre, nuevo_cliente.correo))
        combo_clientes["values"] = [c.nombre for c in lista_clientes]
        messagebox.showinfo("Éxito", "Cliente registrado")
    finally:
        entry_nombre.delete(0, tk.END)
        entry_correo.delete(0, tk.END)

def ejecutar_reserva():
    try:
        nom_c, tipo_s, cant = combo_clientes.get(), combo_servicio.get(), entry_cantidad.get()
        if not cant.isdigit(): raise ValueError("La cantidad debe ser numérica.")
        
        cliente = next((c for c in lista_clientes if c.nombre == nom_c), None)
        if not cliente: raise BusinessError("Seleccione un cliente válido.")

        cant = int(cant)
        if tipo_s == "Sala": s = ReservaSala(cant)
        elif tipo_s == "Equipo": s = AlquilerEquipo(cant)
        elif tipo_s == "Asesoría": s = AsesoriaEspecializada()
        else: raise BusinessError("Seleccione un servicio.")

        reserva = Reserva(cliente, s)
        total = reserva.procesar_pago()
        
        tabla_reservas.insert("", tk.END, values=(cliente.nombre, s.obtener_detalle(), f"${total}"))
        messagebox.showinfo("Reserva", f"Confirmada. Total: ${total}")
    except Exception as e:
        logging.error(f"Error Reserva: {e}")
        messagebox.showerror("Error", str(e))

# ============================================================
# 5. UI PRINCIPAL
# ============================================================
app = tk.Tk()
app.title("Software FJ - Sistema Integral")
app.geometry("700x550")

nb = ttk.Notebook(app)
nb.pack(fill="both", expand=True)

# Pestaña Clientes
p1 = ttk.Frame(nb, padding=10)
nb.add(p1, text="Clientes")
ttk.Label(p1, text="Nombre:").pack()
entry_nombre = ttk.Entry(p1, width=30); entry_nombre.pack()
ttk.Label(p1, text="Email:").pack()
entry_correo = ttk.Entry(p1, width=30); entry_correo.pack()
ttk.Button(p1, text="Registrar", command=ejecutar_registro).pack(pady=5)
tabla_clientes = ttk.Treeview(p1, columns=("N", "E"), show="headings", height=5)
tabla_clientes.heading("N", text="Nombre"); tabla_clientes.heading("E", text="Email"); tabla_clientes.pack(fill="x")

# Pestaña Reservas
p2 = ttk.Frame(nb, padding=10)
nb.add(p2, text="Reservas")
ttk.Label(p2, text="Cliente:").pack()
combo_clientes = ttk.Combobox(p2, state="readonly"); combo_clientes.pack()
ttk.Label(p2, text="Servicio:").pack()
combo_servicio = ttk.Combobox(p2, values=["Sala", "Equipo", "Asesoría"], state="readonly"); combo_servicio.pack()
ttk.Label(p2, text="Cantidad:").pack()
entry_cantidad = ttk.Entry(p2); entry_cantidad.pack()
ttk.Button(p2, text="Reservar", command=ejecutar_reserva).pack(pady=5)
tabla_reservas = ttk.Treeview(p2, columns=("C", "D", "T"), show="headings")
tabla_reservas.heading("C", text="Cliente"); tabla_reservas.heading("D", text="Detalle"); tabla_reservas.heading("T", text="Total")
tabla_reservas.pack(fill="x")

app.mainloop()

