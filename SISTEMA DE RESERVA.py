import logging
import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod

# Configuración básica de Logs
logging.basicConfig(filename="logs.txt", level=logging.ERROR, format="%(asctime)s - %(message)s")

# Excepciones
class AppError(Exception): pass

# Clases de Lógica
class Entidad(ABC):
    @abstractmethod
    def mostrar_info(self): pass

class Cliente(Entidad):
    def __init__(self, nombre, correo):
        self.__nombre = nombre
        self.__correo = correo
    def get_nombre(self): return self.__nombre
    def get_correo(self): return self.__correo
    def mostrar_info(self): return f"Cliente: {self.__nombre} | Correo: {self.__correo}"

class Servicio(ABC):
    def __init__(self, nombre, precio_base):
        self.nombre, self.precio_base = nombre, precio_base
    @abstractmethod
    def calcular_costo(self): pass
    @abstractmethod
    def descripcion(self): pass

class ReservaSala(Servicio):
    def __init__(self, horas):
        super().__init__("Sala", 50000)
        self.horas = horas
    def calcular_costo(self): return self.precio_base * self.horas
    def descripcion(self): return f"Sala por {self.horas} hrs"

class AlquilerEquipo(Servicio):
    def __init__(self, dias):
        super().__init__("Equipo", 30000)
        self.dias = dias
    def calcular_costo(self): return self.precio_base * self.dias
    def descripcion(self): return f"Equipo por {self.dias} días"

class Reserva:
    def __init__(self, cliente, servicio):
        self.cliente, self.servicio, self.estado = cliente, servicio, "Confirmada"
    def procesar(self):
        costo = self.servicio.calcular_costo()
        return f"Total: ${costo}"

# Listas de datos
clientes, reservas = [], []

# Funciones de Interfaz
def registrar_cliente():
    nom, corr = entry_nombre.get(), entry_correo.get()
    if nom and corr:
        c = Cliente(nom, corr)
        clientes.append(c)
        tabla_clientes.insert("", tk.END, values=(c.get_nombre(), c.get_correo()))
        combo_clientes["values"] = [cl.get_nombre() for cl in clientes]
        entry_nombre.delete(0, tk.END); entry_correo.delete(0, tk.END)
        messagebox.showinfo("Éxito", "Cliente registrado")
    else:
        messagebox.showwarning("Atención", "Llene todos los campos")

def crear_reserva():
    try:
        nom_c, serv_t, cant = combo_clientes.get(), combo_servicio.get(), int(entry_cantidad.get())
        cliente = next((c for c in clientes if c.get_nombre() == nom_c), None)
        
        if not cliente: raise AppError("Seleccione un cliente")
        
        if serv_t == "Reserva Sala": s = ReservaSala(cant)
        elif serv_t == "Alquiler Equipo": s = AlquilerEquipo(cant)
        else: raise AppError("Seleccione servicio")
        
        res = Reserva(cliente, s)
        tabla_reservas.insert("", tk.END, values=(cliente.get_nombre(), s.descripcion(), res.estado))
        messagebox.showinfo("Reserva", res.procesar())
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- INTERFAZ GRÁFICA ---
root = tk.Tk()
root.title("Software FJ - Gestión")
root.geometry("800x500")

nb = ttk.Notebook(root)
nb.pack(fill="both", expand=True)

# Pestaña Clientes
f1 = ttk.Frame(nb, padding=10)
nb.add(f1, text="Clientes")
ttk.Label(f1, text="Nombre:").grid(row=0, column=0)
entry_nombre = ttk.Entry(f1)
entry_nombre.grid(row=0, column=1)
ttk.Label(f1, text="Correo:").grid(row=1, column=0)
entry_correo = ttk.Entry(f1)
entry_correo.grid(row=1, column=1)
ttk.Button(f1, text="Registrar", command=registrar_cliente).grid(row=2, columnspan=2)
tabla_clientes = ttk.Treeview(f1, columns=("Nom", "Corr"), show="headings")
tabla_clientes.heading("Nom", text="Nombre"); tabla_clientes.heading("Corr", text="Correo")
tabla_clientes.grid(row=3, columnspan=2)

# Pestaña Reservas
f2 = ttk.Frame(nb, padding=10)
nb.add(f2, text="Reservas")
ttk.Label(f2, text="Cliente:").grid(row=0, column=0)
combo_clientes = ttk.Combobox(f2)
combo_clientes.grid(row=0, column=1)
ttk.Label(f2, text="Servicio:").grid(row=1, column=0)
combo_servicio = ttk.Combobox(f2, values=["Reserva Sala", "Alquiler Equipo"])
combo_servicio.grid(row=1, column=1)
ttk.Label(f2, text="Cantidad (Hrs/Días):").grid(row=2, column=0)
entry_cantidad = ttk.Entry(f2)
entry_cantidad.grid(row=2, column=1)
ttk.Button(f2, text="Reservar", command=crear_reserva).grid(row=3, columnspan=2)
tabla_reservas = ttk.Treeview(f2, columns=("C", "S", "E"), show="headings")
tabla_reservas.heading("C", text="Cliente"); tabla_reservas.heading("S", text="Servicio"); tabla_reservas.heading("E", text="Estado")
tabla_reservas.grid(row=4, columnspan=2)

root.mainloop()
