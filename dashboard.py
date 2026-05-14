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

CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CSV = os.path.join(CARPETA, "csv_camaras_2.csv")
ARCHIVO_USUARIOS = os.path.join(CARPETA, "usuarios.txt")

# Apariencia general: fondo blanco/gris claro, tema azul simple
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Colores usados en la app
COLOR_FONDO        = "#f0f0f0"
COLOR_SIDEBAR      = "#dce6f0"
COLOR_BARRA_TOP    = "#4a7db5"
COLOR_BOTON        = "#4a7db5"
COLOR_BOTON_HOVER  = "#3a6a9a"
COLOR_TEXTO_CLARO  = "#ffffff"
COLOR_TEXTO_GRIS   = "#555555"
COLOR_RESULTADO    = "#ffffff"


def leer_usuarios():
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
    df["marca"] = df["modelo"].str.split().str[0]
    return df


# -------------------------------------------------------
# VENTANA DE LOGIN
# -------------------------------------------------------

class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Iniciar sesion")
        self.geometry("380x400")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO)
        self.usuarios = leer_usuarios()
        self.construir_interfaz()

    def construir_interfaz(self):
        # Titulo principal
        marco_titulo = ctk.CTkFrame(self, fg_color=COLOR_BARRA_TOP, corner_radius=0)
        marco_titulo.pack(fill="x")
        ctk.CTkLabel(
            marco_titulo,
            text="Dashboard de Camaras",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXTO_CLARO
        ).pack(pady=18)

        # Formulario
        marco_form = ctk.CTkFrame(self, fg_color=COLOR_FONDO, corner_radius=0)
        marco_form.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(marco_form, text="Usuario:", anchor="w",
                     text_color=COLOR_TEXTO_GRIS).pack(fill="x", pady=(10, 2))
        self.campo_usuario = ctk.CTkEntry(marco_form, width=300,
                                          border_color="#aaaaaa",
                                          fg_color="white")
        self.campo_usuario.pack(fill="x")

        ctk.CTkLabel(marco_form, text="Contrasena:", anchor="w",
                     text_color=COLOR_TEXTO_GRIS).pack(fill="x", pady=(12, 2))
        self.campo_contrasena = ctk.CTkEntry(marco_form, width=300,
                                              show="*",
                                              border_color="#aaaaaa",
                                              fg_color="white")
        self.campo_contrasena.pack(fill="x")

        self.etiqueta_error = ctk.CTkLabel(marco_form, text="",
                                           text_color="red",
                                           font=ctk.CTkFont(size=11))
        self.etiqueta_error.pack(pady=(6, 0))

        ctk.CTkButton(
            marco_form,
            text="Entrar",
            fg_color=COLOR_BOTON,
            hover_color=COLOR_BOTON_HOVER,
            text_color="white",
            corner_radius=4,
            command=self.intentar_login
        ).pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(
            marco_form,
            text="Prueba: admin / admin123",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(pady=(10, 0))

        self.campo_contrasena.bind("<Return>", lambda e: self.intentar_login())

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
        usuario = self.campo_usuario.get().strip()
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
        self.configure(fg_color=COLOR_FONDO)
        self.nombre = nombre
        self.rol = rol
        self.df = leer_csv()
        self.construir_interfaz()

    def construir_interfaz(self):
        # Barra superior
        barra_top = ctk.CTkFrame(self, height=48, corner_radius=0,
                                 fg_color=COLOR_BARRA_TOP)
        barra_top.pack(fill="x", side="top")
        barra_top.pack_propagate(False)

        ctk.CTkLabel(
            barra_top,
            text="Dashboard de Camaras Fotograficas",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXTO_CLARO
        ).pack(side="left", padx=16, pady=12)

        ctk.CTkLabel(
            barra_top,
            text=f"Usuario: {self.nombre}  |  Rol: {self.rol}",
            font=ctk.CTkFont(size=11),
            text_color="#d0e4f7"
        ).pack(side="right", padx=16)

        # Contenedor principal
        contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkScrollableFrame(
            contenedor, width=200, corner_radius=0,
            fg_color=COLOR_SIDEBAR,
            scrollbar_button_color="#aabbcc"
        )
        self.sidebar.pack(fill="y", side="left")

        ctk.CTkLabel(
            self.sidebar,
            text="Consultas disponibles",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(pady=(14, 8), padx=8)

        # Separador visual simple
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#aaaaaa").pack(fill="x", padx=8, pady=(0, 8))

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
            ctk.CTkButton(
                self.sidebar,
                text=texto,
                anchor="w",
                width=184,
                fg_color=COLOR_BOTON,
                hover_color=COLOR_BOTON_HOVER,
                text_color="white",
                corner_radius=3,
                font=ctk.CTkFont(size=12),
                command=funcion
            ).pack(pady=3, padx=8)

        # Area de resultados
        frame_derecha = ctk.CTkFrame(contenedor, corner_radius=0, fg_color=COLOR_FONDO)
        frame_derecha.pack(fill="both", expand=True, side="left")

        scrollbar = ctk.CTkScrollbar(frame_derecha)
        scrollbar.pack(fill="y", side="right")

        self.canvas_scroll = tk.Canvas(
            frame_derecha,
            highlightthickness=0,
            bg=COLOR_FONDO,
            yscrollcommand=scrollbar.set
        )
        self.canvas_scroll.pack(fill="both", expand=True, side="left")
        scrollbar.configure(command=self.canvas_scroll.yview)

        self.frame_resultados = ctk.CTkFrame(
            self.canvas_scroll, corner_radius=0, fg_color=COLOR_FONDO
        )
        self.ventana_canvas = self.canvas_scroll.create_window(
            (0, 0), window=self.frame_resultados, anchor="nw"
        )

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
        # Franja de titulo con fondo azul suave
        marco_titulo = ctk.CTkFrame(
            self.frame_resultados,
            fg_color="#d0e4f7",
            corner_radius=4
        )
        marco_titulo.pack(fill="x", padx=20, pady=(18, 4))

        ctk.CTkLabel(
            marco_titulo,
            text=titulo,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1a3a5c"
        ).pack(anchor="w", padx=12, pady=(8, 2))

        if subtitulo:
            ctk.CTkLabel(
                marco_titulo,
                text=subtitulo,
                font=ctk.CTkFont(size=11),
                text_color=COLOR_TEXTO_GRIS
            ).pack(anchor="w", padx=12, pady=(0, 8))

    def mostrar_grafica(self, fig):
        # Fondo blanco para la grafica
        fig.patch.set_facecolor("#ffffff")
        marco_grafica = ctk.CTkFrame(
            self.frame_resultados, fg_color=COLOR_RESULTADO,
            corner_radius=4, border_width=1, border_color="#cccccc"
        )
        marco_grafica.pack(padx=20, pady=6, fill="x")

        canvas = FigureCanvasTkAgg(fig, master=marco_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=8, pady=8, fill="x")
        plt.close(fig)

    def mostrar_tabla(self, dataframe):
        marco_tabla = ctk.CTkFrame(
            self.frame_resultados, fg_color=COLOR_RESULTADO,
            corner_radius=4, border_width=1, border_color="#cccccc"
        )
        marco_tabla.pack(padx=20, pady=(0, 14), fill="x")

        columnas = list(dataframe.columns)

        # Encabezados con fondo azul suave
        for j, col in enumerate(columnas):
            celda = ctk.CTkFrame(marco_tabla, fg_color="#4a7db5", corner_radius=0)
            celda.grid(row=0, column=j, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(
                celda, text=str(col),
                font=ctk.CTkFont(weight="bold"),
                text_color="white",
                width=150
            ).pack(padx=6, pady=4)
            marco_tabla.grid_columnconfigure(j, weight=1)

        # Filas de datos alternando color
        for i, fila in enumerate(dataframe.itertuples(index=False), start=1):
            color_fila = "#f7faff" if i % 2 == 0 else "#ffffff"
            for j, valor in enumerate(fila):
                celda = ctk.CTkFrame(marco_tabla, fg_color=color_fila, corner_radius=0)
                celda.grid(row=i, column=j, padx=1, pady=1, sticky="nsew")
                ctk.CTkLabel(
                    celda, text=str(valor),
                    text_color="#222222",
                    width=150
                ).pack(padx=6, pady=3)

    def mostrar_bienvenida(self):
        self.limpiar_resultados()

        # Tarjeta de bienvenida simple
        marco = ctk.CTkFrame(
            self.frame_resultados,
            fg_color=COLOR_RESULTADO,
            corner_radius=6,
            border_width=1,
            border_color="#cccccc"
        )
        marco.pack(padx=40, pady=60, fill="x")

        ctk.CTkLabel(
            marco,
            text=f"Bienvenido, {self.nombre}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1a3a5c"
        ).pack(pady=(30, 8))

        ctk.CTkFrame(marco, height=1, fg_color="#dddddd").pack(fill="x", padx=20)

        ctk.CTkLabel(
            marco,
            text=f"Dataset cargado: {len(self.df)} camaras de {self.df['marca'].nunique()} marcas.",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXTO_GRIS
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            marco,
            text="Selecciona una consulta del menu de la izquierda.",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(0, 30))

    # ---------------------------------------------------
    # CONSULTAS
    # ---------------------------------------------------

    def consulta_1(self):
        self.limpiar_resultados()
        self.mostrar_titulo("Camaras por marca",
                            "Top 15 marcas con mas modelos en el dataset")
        conteo = self.df["marca"].value_counts().head(15).reset_index()
        conteo.columns = ["marca", "cantidad"]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(conteo["marca"][::-1], conteo["cantidad"][::-1], color="#4a7db5")
        ax.set_xlabel("Numero de modelos")
        ax.set_title("Top 15 marcas con mas modelos")
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()
        self.mostrar_grafica(fig)
        self.mostrar_tabla(conteo)

    def consulta_2(self):
        self.limpiar_resultados()
        self.mostrar_titulo("Distribucion de precios",
                            "Como se distribuyen los precios de todas las camaras")
        precios = self.df["precio"].dropna()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(precios, bins=30, color="#4a7db5", edgecolor="white")
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
        self.limpiar_resultados()
        self.mostrar_titulo("Top 10 camaras mas caras",
                            "Los modelos con el precio mas alto en el dataset")
        top = self.df.nlargest(10, "precio")[["modelo", "marca", "precio"]].reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(top["modelo"][::-1], top["precio"][::-1], color="#c0392b")
        ax.set_xlabel("Precio (USD)")
        ax.set_title("Top 10 camaras mas caras")
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()
        self.mostrar_grafica(fig)
        self.mostrar_tabla(top)

    def consulta_4(self):
        self.limpiar_resultados()
        self.mostrar_titulo("Top 10 camaras mas baratas",
                            "Los modelos con el precio mas bajo (excluyendo precio cero)")
        baratas = self.df[self.df["precio"] > 0].nsmallest(10, "precio")[
            ["modelo", "marca", "precio"]].reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(baratas["modelo"][::-1], baratas["precio"][::-1], color="#27ae60")
        ax.set_xlabel("Precio (USD)")
        ax.set_title("Top 10 camaras mas baratas")
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()
        self.mostrar_grafica(fig)
        self.mostrar_tabla(baratas)

    def consulta_5(self):
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
        ax.bar(precio_marca["marca"], precio_marca["precio_promedio"], color="#4a7db5")
        ax.set_ylabel("Precio promedio (USD)")
        ax.set_title("Precio promedio por marca")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()
        self.mostrar_grafica(fig)
        self.mostrar_tabla(precio_marca)

    def consulta_6(self):
        self.limpiar_resultados()
        self.mostrar_titulo("Zoom promedio por marca",
                            "Alcance de zoom promedio de cada marca")
        marcas_validas = self.df["marca"].value_counts()
        marcas_validas = marcas_validas[marcas_validas >= 5].index
        zoom_marca = (self.df[self.df["marca"].isin(marcas_validas)]
                      .groupby("marca")["zoom"]
                      .mean().round(1)
                      .sort_values(ascending=False)
                      .reset_index())
        zoom_marca.columns = ["marca", "zoom_promedio"]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(zoom_marca["marca"], zoom_marca["zoom_promedio"], color="#e67e22")
        ax.set_ylabel("Zoom promedio (mm)")
        ax.set_title("Zoom promedio por marca")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()
        self.mostrar_grafica(fig)
        self.mostrar_tabla(zoom_marca)

    def consulta_7(self):
        self.limpiar_resultados()
        self.mostrar_titulo("Peso vs Precio",
                            "Hay relacion entre el peso de la camara y su precio?")
        datos = self.df[["peso", "precio"]].dropna()
        datos = datos[(datos["peso"] > 0) & (datos["precio"] > 0)]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(datos["peso"], datos["precio"], alpha=0.4, color="#4a7db5", s=20)
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
        self.limpiar_resultados()
        self.mostrar_titulo("Almacenamiento incluido",
                            "Cuantas camaras incluyen cada cantidad de almacenamiento (MB)")
        almacenamiento = self.df["almacenamiento"].dropna()
        almacenamiento = almacenamiento[almacenamiento > 0]
        conteo = almacenamiento.value_counts().sort_index().reset_index()
        conteo.columns = ["almacenamiento_mb", "cantidad"]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(conteo["almacenamiento_mb"].astype(str), conteo["cantidad"], color="#8e44ad")
        ax.set_xlabel("Almacenamiento incluido (MB)")
        ax.set_ylabel("Numero de camaras")
        ax.set_title("Camaras por almacenamiento incluido")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()
        self.mostrar_grafica(fig)
        self.mostrar_tabla(conteo)

    def consulta_9(self):
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
        ax.bar([i - ancho / 2 for i in x], resumen["enfoque_normal"],
               ancho, label="Enfoque normal", color="#4a7db5")
        ax.bar([i + ancho / 2 for i in x], resumen["enfoque_macro"],
               ancho, label="Enfoque macro", color="#c0392b")
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
        self.limpiar_resultados()
        self.mostrar_titulo("Camaras por rango de precio",
                            "Cuantos modelos hay en cada rango de precio")
        rangos = [0, 100, 200, 300, 500, 800, 1500, 8000]
        etiquetas = ["0-100", "100-200", "200-300",
                     "300-500", "500-800", "800-1500", "1500+"]
        df_valido = self.df[self.df["precio"] > 0].copy()
        df_valido["rango"] = pd.cut(df_valido["precio"], bins=rangos, labels=etiquetas)
        conteo = df_valido["rango"].value_counts().sort_index().reset_index()
        conteo.columns = ["rango_precio", "cantidad"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        ax1.bar(conteo["rango_precio"], conteo["cantidad"], color="#4a7db5")
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