import logging
import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod

# ============================================================
# 1. CONFIGURACIÓN DE LOGS (RESTABLECIDA)
# ============================================================
logging.basicConfig(
    filename="logs_software_fj.txt", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================
class SoftwareFJError(Exception): pass
class ValidationError(SoftwareFJError): pass
class BusinessError(SoftwareFJError): pass

# ============================================================
# 3. ARQUITECTURA ORIENTADA A OBJETOS (POO)
# ============================================================
class Entidad(ABC):
    @abstractmethod
    def validar(self): pass

class Cliente(Entidad):
    def __init__(self, nombre, correo, telefono):
        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono
    @property
    def nombre(self): return self.__nombre
    @property
    def correo(self): return self.__correo
    @property
    def telefono(self): return self.__telefono
    def validar(self): return True

class Servicio(ABC):
    def __init__(self, nombre, precio_base):
        self.nombre = nombre
        self.precio_base = precio_base
    @abstractmethod
    def calcular_costo(self): pass
    @abstractmethod
    def obtener_detalle(self): pass

class ReservaSala(Servicio):
    def __init__(self, h): super().__init__("Sala", 50000); self.h = h
    def calcular_costo(self): return self.precio_base * self.h
    def obtener_detalle(self): return f"Sala por {self.h} hrs"

class AlquilerEquipo(Servicio):
    def __init__(self, d): super().__init__("Equipo", 30000); self.d = d
    def calcular_costo(self): return (self.precio_base * self.d) + 5000
    def obtener_detalle(self): return f"Equipo por {self.d} días"

class AsesoriaEspecializada(Servicio):
    def __init__(self): super().__init__("Asesoría", 120000)
    def calcular_costo(self): return self.precio_base * 1.5
    def obtener_detalle(self): return "Asesoría Senior"

class Reserva:
    def __init__(self, cliente, servicio):
        self.cliente, self.servicio = cliente, servicio
    def procesar(self):
        try:
            costo = self.servicio.calcular_costo()
            logging.info(f"PROCESADO: Cliente {self.cliente.nombre} - Total: ${costo}")
            return costo
        except Exception as e:
            logging.error(f"Error procesando costo: {e}")
            raise BusinessError("Error en cálculo de reserva")

# ============================================================
# 4. LÓGICA DE CONTROLADORES
# ============================================================
lista_clientes = []

def ejecutar_registro():
    try:
        n, c, t = entry_nombre.get(), entry_correo.get(), entry_telefono.get()
        if not (n and c and t): raise ValidationError("Campos obligatorios faltantes")
        nuevo = Cliente(n, c, t)
        lista_clientes.append(nuevo)
        tabla_clientes.insert("", tk.END, values=(nuevo.nombre, nuevo.correo, nuevo.telefono))
        combo_clientes["values"] = [cl.nombre for cl in lista_clientes]
        logging.info(f"REGISTRO: Nuevo cliente {n} añadido.")
        messagebox.showinfo("Éxito", "Cliente registrado")
    except ValidationError as e:
        logging.error(f"VALIDACIÓN: {e}")
        messagebox.showwarning("Atención", str(e))
    except Exception as e:
        logging.critical(f"SISTEMA: Error inesperado en registro: {e}")
        messagebox.showerror("Error", "Fallo crítico al registrar")
    finally:
        entry_nombre.delete(0, tk.END); entry_correo.delete(0, tk.END); entry_telefono.delete(0, tk.END)

def ejecutar_reserva():
    try:
        nom_c, tipo_s, cant = combo_clientes.get(), combo_servicio.get(), entry_cantidad.get()
        if not cant.isdigit(): raise BusinessError("La cantidad debe ser un número.")
        cli = next((c for c in lista_clientes if c.nombre == nom_c), None)
        if not cli: raise BusinessError("Seleccione un cliente válido.")
        
        if tipo_s == "Sala": s = ReservaSala(int(cant))
        elif tipo_s == "Equipo": s = AlquilerEquipo(int(cant))
        elif tipo_s == "Asesoría": s = AsesoriaEspecializada()
        else: raise BusinessError("Servicio no seleccionado.")

        res = Reserva(cli, s)
        total = res.procesar()
        tabla_reservas.insert("", tk.END, values=(cli.nombre, s.obtener_detalle(), f"${total}"))
    except BusinessError as e:
        logging.error(f"NEGOCIO: {e}")
        messagebox.showerror("Error de Reserva", str(e))
    except Exception as e:
        logging.error(f"ERROR: {e}")
        messagebox.showerror("Error", "No se pudo crear la reserva.")

def eliminar_reserva():
    selection = tabla_reservas.selection()
    if not selection:
        logging.warning("INTERFAZ: Intento de eliminación sin selección.")
        messagebox.showwarning("Aviso", "Seleccione una reserva")
        return
    if messagebox.askyesno("Confirmar", "¿Eliminar reserva?"):
        for item in selection:
            info = tabla_reservas.item(item)['values']
            logging.info(f"ELIMINACIÓN: Reserva de {info[0]} eliminada.")
            tabla_reservas.delete(item)

def deseleccionar(event):
    if not tabla_reservas.identify_row(event.y):
        tabla_reservas.selection_remove(tabla_reservas.selection())

# ============================================================
# 5. INTERFAZ GRÁFICA
# ============================================================
app = tk.Tk()
app.title("Software FJ - Gestión Integral")
app.geometry("800x700")

nb = ttk.Notebook(app)
nb.pack(fill="both", expand=True)

# Pestaña Clientes
p1 = ttk.Frame(nb, padding=10); nb.add(p1, text="Clientes")
ttk.Label(p1, text="Nombre:").pack(); entry_nombre = ttk.Entry(p1); entry_nombre.pack()
ttk.Label(p1, text="Email:").pack(); entry_correo = ttk.Entry(p1); entry_correo.pack()
ttk.Label(p1, text="Teléfono:").pack(); entry_telefono = ttk.Entry(p1); entry_telefono.pack()
ttk.Button(p1, text="Registrar", command=ejecutar_registro).pack(pady=10)
tabla_clientes = ttk.Treeview(p1, columns=("N", "C", "T"), show="headings"); tabla_clientes.pack(fill="x")
for c, h in zip(("N", "C", "T"), ("Nombre", "Email", "Teléfono")): tabla_clientes.heading(c, text=h)

# Pestaña Reservas
p2 = ttk.Frame(nb, padding=10); nb.add(p2, text="Reservas")
ttk.Label(p2, text="Cliente:").pack(); combo_clientes = ttk.Combobox(p2, state="readonly"); combo_clientes.pack()
ttk.Label(p2, text="Servicio:").pack(); combo_servicio = ttk.Combobox(p2, values=["Sala", "Equipo", "Asesoría"], state="readonly"); combo_servicio.pack()
ttk.Label(p2, text="Cantidad:").pack(); entry_cantidad = ttk.Entry(p2); entry_cantidad.pack()
ttk.Button(p2, text="Procesar Reserva", command=ejecutar_reserva).pack(pady=5)

tabla_reservas = ttk.Treeview(p2, columns=("C", "D", "T"), show="headings")
for c, h in zip(("C", "D", "T"), ("Cliente", "Detalle", "Total")): tabla_reservas.heading(c, text=h)
tabla_reservas.pack(fill="x", pady=10)
tabla_reservas.bind("<Button-1>", deseleccionar)

btn_el = tk.Button(p2, text="Eliminar Reserva Seleccionada", command=eliminar_reserva, bg="#ff4d4d", fg="white", font=("Arial", 9, "bold"))
btn_el.pack(pady=5)

app.mainloop()
