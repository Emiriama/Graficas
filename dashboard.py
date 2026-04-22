# dashboard.py
# Proyecto: Dashboard de Camaras Fotograficas
# Materia: Fundamentos de Inteligencia Artificial
# Herramientas: CustomTkinter, Pandas, Matplotlib

import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import os
import sys



CARPETA          = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CSV      = os.path.join(CARPETA, "csv_camaras_2.csv")
ARCHIVO_USUARIOS = os.path.join(CARPETA, "usuarios.txt")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")



def leer_usuarios():
    """
    Lee usuarios.txt y devuelve un diccionario.
    Formato de cada linea: usuario:contrasena:nombre:rol
    """
    usuarios = {}
    try:
        with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                partes = linea.split(":")
                if len(partes) == 4:
                    usuario, contrasena, nombre, rol = partes
                    usuarios[usuario] = {
                        "contrasena": contrasena,
                        "nombre": nombre,
                        "rol": rol
                    }
    except FileNotFoundError:
        print("No se encontro el archivo usuarios.txt")
    return usuarios


def leer_csv():
    """
    Lee camaras.csv y devuelve un DataFrame de pandas.
    Limpia y convierte las columnas al tipo correcto.
    """
    df = pd.read_csv(ARCHIVO_CSV, encoding="utf-8")


    df.columns = [
        "modelo", "zoom", "enfoque_normal",
        "enfoque_macro", "almacenamiento",
        "peso", "dimensiones", "precio"
    ]


    columnas_numericas = [
        "zoom", "enfoque_normal", "enfoque_macro",
        "almacenamiento", "peso", "dimensiones", "precio"
    ]
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Extraer la marca del nombre del modelo (primera palabra)
    df["marca"] = df["modelo"].str.split().str[0]

    return df


class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Iniciar sesion")
        self.geometry("400x420")
        self.resizable(False, False)

        self.usuarios = leer_usuarios()
        self.construir_interfaz()

    def construir_interfaz(self):

        ctk.CTkLabel(self, text="Dashboard de Camaras",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(30, 5))

        ctk.CTkLabel(self, text="Usuario:").pack(anchor="w", padx=60)
        self.campo_usuario = ctk.CTkEntry(self, width=280,
                                          placeholder_text="")
        self.campo_usuario.pack(pady=(2, 12))

        ctk.CTkLabel(self, text="Contrasena:").pack(anchor="w", padx=60)
        self.campo_contrasena = ctk.CTkEntry(self, width=280,
                                              placeholder_text="",
                                              show="*")
        self.campo_contrasena.pack(pady=(2, 8))


        self.etiqueta_error = ctk.CTkLabel(self, text="", text_color="red",
                                           font=ctk.CTkFont(size=12))
        self.etiqueta_error.pack(pady=(0, 8))

        ctk.CTkButton(self, text="Entrar", width=280,
                      command=self.intentar_login).pack()

        self.campo_contrasena.bind("<Return>", lambda e: self.intentar_login())

        ctk.CTkLabel(self, text="Prueba: admin / admin123",
                     font=ctk.CTkFont(size=10),
                     text_color="gray").pack(pady=(16, 0))

    def toggle_contrasena(self):
        if self.mostrar_pwd.get():
            self.campo_contrasena.configure(show="")
        else:
            self.campo_contrasena.configure(show="*")

    def validar_campos(self, usuario, contrasena):
        if not usuario:
            return "El usuario no puede estar vacio."
        if not contrasena:
            return "La contrasena no puede estar vacia."
        if len(usuario) < 3:
            return "El usuario debe tener al menos 3 caracteres."
        if len(contrasena) < 4:
            return "La contrasena debe tener al menos 4 caracteres."
        return ""

    def intentar_login(self):
        usuario    = self.campo_usuario.get().strip()
        contrasena = self.campo_contrasena.get()

        error = self.validar_campos(usuario, contrasena)
        if error:
            self.etiqueta_error.configure(text=error)
            return

        if usuario not in self.usuarios:
            self.etiqueta_error.configure(text="Usuario no encontrado.")
            return

        datos_usuario = self.usuarios[usuario]
        if contrasena != datos_usuario["contrasena"]:
            self.etiqueta_error.configure(text="Contrasena incorrecta.")
            return

        self.destroy()
        ventana_principal = VentanaDashboard(
            nombre=datos_usuario["nombre"],
            rol=datos_usuario["rol"]
        )
        ventana_principal.mainloop()


# -------------------------------------------------------
# VENTANA PRINCIPAL (DASHBOARD)
# -------------------------------------------------------

class VentanaDashboard(ctk.CTk):
    def __init__(self, nombre, rol):
        super().__init__()

        self.title("Dashboard de Camaras Fotograficas")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.nombre = nombre
        self.rol    = rol
        self.df     = leer_csv()

        self.construir_interfaz()

    def construir_interfaz(self):

        # Barra superior
        barra_top = ctk.CTkFrame(self, height=45, corner_radius=0)
        barra_top.pack(fill="x", side="top")
        barra_top.pack_propagate(False)

        ctk.CTkLabel(barra_top,
                     text="Dashboard de Camaras Fotograficas",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=20)

        ctk.CTkLabel(barra_top,
                     text=f"Usuario: {self.nombre} ({self.rol})",
                     font=ctk.CTkFont(size=12),
                     text_color="gray").pack(side="right", padx=20)

        # Contenedor principal
        contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        contenedor.pack(fill="both", expand=True)

        # Sidebar con botones
        self.sidebar = ctk.CTkScrollableFrame(contenedor, width=210, corner_radius=0)
        self.sidebar.pack(fill="y", side="left")

        ctk.CTkLabel(self.sidebar, text="Consultas",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(15, 10))

        consultas = [
            ("1. Camaras por marca",           self.consulta_1),
            ("2. Distribucion de precios",      self.consulta_2),
            ("3. Top 10 mas caras",             self.consulta_3),
            ("4. Top 10 mas baratas",           self.consulta_4),
            ("5. Precio por marca",             self.consulta_5),
            ("6. Zoom por marca",               self.consulta_6),
            ("7. Peso vs Precio",               self.consulta_7),
            ("8. Almacenamiento incluido",      self.consulta_8),
            ("9. Enfoque normal vs macro",      self.consulta_9),
            ("10. Camaras por rango de precio", self.consulta_10),
        ]

        for texto, funcion in consultas:
            ctk.CTkButton(self.sidebar, text=texto,
                          anchor="w", width=190,
                          command=funcion).pack(pady=3, padx=8)

        # Area de resultados con scroll manual (compatible con matplotlib)
        frame_derecha = ctk.CTkFrame(contenedor, corner_radius=0, fg_color="transparent")
        frame_derecha.pack(fill="both", expand=True, side="left")

        scrollbar = ctk.CTkScrollbar(frame_derecha)
        scrollbar.pack(fill="y", side="right")

        self.canvas_scroll = tk.Canvas(frame_derecha,
                                       highlightthickness=0,
                                       yscrollcommand=scrollbar.set)
        self.canvas_scroll.pack(fill="both", expand=True, side="left")
        scrollbar.configure(command=self.canvas_scroll.yview)

        self.frame_resultados = ctk.CTkFrame(self.canvas_scroll,
                                              corner_radius=0, fg_color="transparent")
        self.ventana_canvas = self.canvas_scroll.create_window(
            (0, 0), window=self.frame_resultados, anchor="nw")

        def actualizar_scroll(event=None):
            self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))

        def ajustar_ancho(event=None):
            self.canvas_scroll.itemconfig(self.ventana_canvas, width=event.width)

        self.frame_resultados.bind("<Configure>", actualizar_scroll)
        self.canvas_scroll.bind("<Configure>", ajustar_ancho)

        def scroll_mouse(event):
            self.canvas_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas_scroll.bind_all("<MouseWheel>", scroll_mouse)

        self.mostrar_bienvenida()

    # ---------------------------------------------------
    # METODOS DE AYUDA
    # ---------------------------------------------------

    def limpiar_resultados(self):
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()
        self.canvas_scroll.yview_moveto(0)

    def mostrar_titulo(self, titulo, subtitulo=""):
        ctk.CTkLabel(self.frame_resultados,
                     text=titulo,
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 2))
        if subtitulo:
            ctk.CTkLabel(self.frame_resultados,
                         text=subtitulo,
                         font=ctk.CTkFont(size=12),
                         text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))

    def mostrar_grafica(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.frame_resultados)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=20, pady=10, fill="x")
        plt.close(fig)

    def mostrar_tabla(self, dataframe):
        frame_tabla = ctk.CTkFrame(self.frame_resultados)
        frame_tabla.pack(padx=20, pady=10, fill="x")

        columnas = list(dataframe.columns)

        for j, col in enumerate(columnas):
            ctk.CTkLabel(frame_tabla, text=str(col),
                         font=ctk.CTkFont(weight="bold"),
                         width=160).grid(row=0, column=j, padx=4, pady=4)
            frame_tabla.grid_columnconfigure(j, weight=1)

        for i, fila in enumerate(dataframe.itertuples(index=False), start=1):
            for j, valor in enumerate(fila):
                ctk.CTkLabel(frame_tabla, text=str(valor),
                             width=160).grid(row=i, column=j, padx=4, pady=2)

    def mostrar_bienvenida(self):
        self.limpiar_resultados()
        ctk.CTkLabel(self.frame_resultados,
                     text=f"Bienvenido, {self.nombre}",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(80, 10))
        ctk.CTkLabel(self.frame_resultados,
                     text=f"Dataset cargado: {len(self.df)} camaras de {self.df['marca'].nunique()} marcas.\n"
                          "Selecciona una consulta del menu izquierdo.",
                     font=ctk.CTkFont(size=13),
                     text_color="gray",
                     justify="center").pack()

    # ---------------------------------------------------
    # CONSULTAS
    # ---------------------------------------------------

    def consulta_1(self):
        """Cuantas camaras hay por marca — Top 15 marcas"""
        self.limpiar_resultados()
        self.mostrar_titulo("Camaras por marca",
                            "Top 15 marcas con mas modelos en el dataset")

        conteo = self.df["marca"].value_counts().head(15).reset_index()
        conteo.columns = ["marca", "cantidad"]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(conteo["marca"][::-1], conteo["cantidad"][::-1], color="steelblue")
        ax.set_xlabel("Numero de modelos")
        ax.set_title("Top 15 marcas con mas modelos")
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(conteo)

    def consulta_2(self):
        """Distribucion de precios — histograma"""
        self.limpiar_resultados()
        self.mostrar_titulo("Distribucion de precios",
                            "Como se distribuyen los precios de todas las camaras")

        precios = self.df["precio"].dropna()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(precios, bins=30, color="steelblue", edgecolor="white")
        ax.set_xlabel("Precio (USD)")
        ax.set_ylabel("Numero de camaras")
        ax.set_title("Distribucion de precios")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)

        resumen = precios.describe().round(2).reset_index()
        resumen.columns = ["estadistica", "valor"]
        self.mostrar_tabla(resumen)

    def consulta_3(self):
        """Top 10 camaras mas caras"""
        self.limpiar_resultados()
        self.mostrar_titulo("Top 10 camaras mas caras",
                            "Los modelos con el precio mas alto en el dataset")

        top = self.df.nlargest(10, "precio")[["modelo", "marca", "precio"]].reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(top["modelo"][::-1], top["precio"][::-1], color="tomato")
        ax.set_xlabel("Precio (USD)")
        ax.set_title("Top 10 camaras mas caras")
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(top)

    def consulta_4(self):
        """Top 10 camaras mas baratas (precio > 0)"""
        self.limpiar_resultados()
        self.mostrar_titulo("Top 10 camaras mas baratas",
                            "Los modelos con el precio mas bajo (excluyendo precio cero)")

        baratas = self.df[self.df["precio"] > 0].nsmallest(10, "precio")[
            ["modelo", "marca", "precio"]].reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(baratas["modelo"][::-1], baratas["precio"][::-1], color="seagreen")
        ax.set_xlabel("Precio (USD)")
        ax.set_title("Top 10 camaras mas baratas")
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(baratas)

    def consulta_5(self):
        """Precio promedio por marca"""
        self.limpiar_resultados()
        self.mostrar_titulo("Precio promedio por marca",
                            "Promedio de precio de las marcas con al menos 5 modelos")

        marcas_validas = self.df["marca"].value_counts()
        marcas_validas = marcas_validas[marcas_validas >= 5].index

        precio_marca = (self.df[self.df["marca"].isin(marcas_validas)]
                        .groupby("marca")["precio"]
                        .mean().round(2)
                        .sort_values(ascending=False)
                        .reset_index())
        precio_marca.columns = ["marca", "precio_promedio"]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(precio_marca["marca"], precio_marca["precio_promedio"], color="steelblue")
        ax.set_ylabel("Precio promedio (USD)")
        ax.set_title("Precio promedio por marca")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(precio_marca)

    def consulta_6(self):
        """Zoom promedio por marca"""
        self.limpiar_resultados()
        self.mostrar_titulo("Zoom promedio por marca",
                            "Alcance de zoom promedio (tele) de cada marca")

        marcas_validas = self.df["marca"].value_counts()
        marcas_validas = marcas_validas[marcas_validas >= 5].index

        zoom_marca = (self.df[self.df["marca"].isin(marcas_validas)]
                      .groupby("marca")["zoom"]
                      .mean().round(1)
                      .sort_values(ascending=False)
                      .reset_index())
        zoom_marca.columns = ["marca", "zoom_promedio"]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(zoom_marca["marca"], zoom_marca["zoom_promedio"], color="orange")
        ax.set_ylabel("Zoom promedio (mm)")
        ax.set_title("Zoom promedio por marca")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(zoom_marca)

    def consulta_7(self):
        """Relacion entre peso y precio"""
        self.limpiar_resultados()
        self.mostrar_titulo("Peso vs Precio",
                            "Hay relacion entre el peso de la camara y su precio?")

        datos = self.df[["peso", "precio"]].dropna()
        datos = datos[(datos["peso"] > 0) & (datos["precio"] > 0)]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(datos["peso"], datos["precio"],
                   alpha=0.4, color="steelblue", s=20)
        ax.set_xlabel("Peso (gramos)")
        ax.set_ylabel("Precio (USD)")
        ax.set_title("Peso vs Precio de la camara")
        ax.grid(alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)

        resumen = datos.describe().round(2).reset_index()
        resumen.columns = ["estadistica", "peso", "precio"]
        self.mostrar_tabla(resumen)

    def consulta_8(self):
        """Distribucion de almacenamiento incluido"""
        self.limpiar_resultados()
        self.mostrar_titulo("Almacenamiento incluido",
                            "Cuantas camaras incluyen cada cantidad de almacenamiento (MB)")

        almacenamiento = self.df["almacenamiento"].dropna()
        almacenamiento = almacenamiento[almacenamiento > 0]
        conteo = almacenamiento.value_counts().sort_index().reset_index()
        conteo.columns = ["almacenamiento_mb", "cantidad"]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(conteo["almacenamiento_mb"].astype(str),
               conteo["cantidad"], color="purple")
        ax.set_xlabel("Almacenamiento incluido (MB)")
        ax.set_ylabel("Numero de camaras")
        ax.set_title("Camaras por almacenamiento incluido")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(conteo)

    def consulta_9(self):
        """Comparacion enfoque normal vs enfoque macro por marca"""
        self.limpiar_resultados()
        self.mostrar_titulo("Enfoque normal vs Enfoque macro",
                            "Comparacion del rango de enfoque entre los dos modos por marca")

        marcas_validas = self.df["marca"].value_counts()
        marcas_validas = marcas_validas[marcas_validas >= 5].index

        resumen = (self.df[self.df["marca"].isin(marcas_validas)]
                   .groupby("marca")[["enfoque_normal", "enfoque_macro"]]
                   .mean().round(1)
                   .sort_values("enfoque_normal", ascending=False)
                   .reset_index())

        fig, ax = plt.subplots(figsize=(9, 5))
        x = range(len(resumen))
        ancho = 0.35
        ax.bar([i - ancho/2 for i in x], resumen["enfoque_normal"],
               ancho, label="Enfoque normal", color="steelblue")
        ax.bar([i + ancho/2 for i in x], resumen["enfoque_macro"],
               ancho, label="Enfoque macro", color="tomato")
        ax.set_xticks(list(x))
        ax.set_xticklabels(resumen["marca"], rotation=30, ha="right")
        ax.set_ylabel("Rango de enfoque (cm)")
        ax.set_title("Enfoque normal vs macro por marca")
        ax.legend()
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(resumen)

    def consulta_10(self):
        """Cantidad de camaras por rango de precio"""
        self.limpiar_resultados()
        self.mostrar_titulo("Camaras por rango de precio",
                            "Cuantos modelos hay en cada rango de precio")

        rangos    = [0, 100, 200, 300, 500, 800, 1500, 8000]
        etiquetas = ["0-100", "100-200", "200-300",
                     "300-500", "500-800", "800-1500", "1500+"]

        df_valido = self.df[self.df["precio"] > 0].copy()
        df_valido["rango"] = pd.cut(df_valido["precio"],
                                     bins=rangos, labels=etiquetas)

        conteo = df_valido["rango"].value_counts().sort_index().reset_index()
        conteo.columns = ["rango_precio", "cantidad"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        ax1.bar(conteo["rango_precio"], conteo["cantidad"], color="steelblue")
        ax1.set_xlabel("Rango de precio (USD)")
        ax1.set_ylabel("Cantidad de camaras")
        ax1.set_title("Camaras por rango de precio")
        plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")
        ax1.grid(axis="y", alpha=0.4)

        ax2.pie(conteo["cantidad"], labels=conteo["rango_precio"],
                autopct="%1.0f%%", startangle=90)
        ax2.set_title("Proporcion (%)")

        fig.tight_layout()
        self.mostrar_grafica(fig)
        self.mostrar_tabla(conteo)


# -------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------

if __name__ == "__main__":
    app = VentanaLogin()
    app.mainloop()
