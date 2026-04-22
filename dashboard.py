# dashboard.py
# Proyecto: Dashboard de Ciudades Mundiales
# Materia: Fundamentos de Inteligencia Artificial
# Herramientas: CustomTkinter, Pandas, Matplotlib

import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys


# Rutas de los archivos
CARPETA    = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CSV     = os.path.join(CARPETA, "ciudades.csv")
ARCHIVO_USUARIOS = os.path.join(CARPETA, "usuarios.txt")


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")



def leer_usuarios():
    """
    Lee el archivo usuarios.txt y devuelve un diccionario.
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
    Lee el archivo ciudades.csv y devuelve un DataFrame de pandas.
    Convierte las columnas numericas al tipo correcto.
    """
    df = pd.read_csv(ARCHIVO_CSV, encoding="utf-8")
    columnas_numericas = [
        "poblacion", "area_km2", "densidad", "pib_per_capita",
        "temperatura_media", "precipitacion_anual", "esperanza_vida",
        "alfabetizacion", "año_fundacion"
    ]
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Iniciar sesion")
        self.geometry("400x420")
        self.resizable(False, False)

        # Leer usuarios del archivo
        self.usuarios = leer_usuarios()

        self.construir_interfaz()

    def construir_interfaz(self):


        ctk.CTkLabel(self, text="Dashboard de Ciudades",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(30, 5))


        # Campo usuario
        ctk.CTkLabel(self, text="Usuario:").pack(anchor="w", padx=60)
        self.campo_usuario = ctk.CTkEntry(self, width=280,
                                          placeholder_text="")
        self.campo_usuario.pack(pady=(2, 12))

        # Campo contrasena
        ctk.CTkLabel(self, text="Contrasena:").pack(anchor="w", padx=60)
        self.campo_contrasena = ctk.CTkEntry(self, width=280,
                                              placeholder_text="",
                                              show="*")
        self.campo_contrasena.pack(pady=(2, 8))

        # Etiqueta de error (empieza vacia)
        self.etiqueta_error = ctk.CTkLabel(self, text="", text_color="red",
                                           font=ctk.CTkFont(size=12))
        self.etiqueta_error.pack(pady=(0, 8))

        # Boton entrar
        ctk.CTkButton(self, text="Entrar", width=280,
                      command=self.intentar_login).pack()

        # Presionar Enter tambien inicia sesion
        self.campo_contrasena.bind("<Return>", lambda e: self.intentar_login())

        # Nota con credenciales de prueba
        ctk.CTkLabel(self, text="Prueba: admin / admin123",
                     font=ctk.CTkFont(size=10),
                     text_color="gray").pack(pady=(16, 0))

    def toggle_contrasena(self):
        if self.mostrar_pwd.get():
            self.campo_contrasena.configure(show="")
        else:
            self.campo_contrasena.configure(show="*")

    def validar_campos(self, usuario, contrasena):
        """
        Revisa que los campos tengan datos validos.
        Devuelve un mensaje de error, o cadena vacia si todo esta bien.
        """
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

        # Paso 1: validar formato
        error = self.validar_campos(usuario, contrasena)
        if error:
            self.etiqueta_error.configure(text=error)
            return

        # Paso 2: verificar contra el archivo
        if usuario not in self.usuarios:
            self.etiqueta_error.configure(text="Usuario no encontrado.")
            return

        datos_usuario = self.usuarios[usuario]
        if contrasena != datos_usuario["contrasena"]:
            self.etiqueta_error.configure(text="Contrasena incorrecta.")
            return

        # Paso 3: acceso correcto, abrir dashboard
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

        self.title("Dashboard de Ciudades Mundiales")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.nombre = nombre
        self.rol    = rol
        self.df     = leer_csv()

        self.construir_interfaz()

    def construir_interfaz(self):

        # --- Barra superior ---
        barra_top = ctk.CTkFrame(self, height=45, corner_radius=0)
        barra_top.pack(fill="x", side="top")
        barra_top.pack_propagate(False)

        ctk.CTkLabel(barra_top,
                     text="Dashboard de Ciudades Mundiales",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=20)

        ctk.CTkLabel(barra_top,
                     text=f"Usuario: {self.nombre} ({self.rol})",
                     font=ctk.CTkFont(size=12),
                     text_color="gray").pack(side="right", padx=20)

        # --- Contenedor principal ---
        contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        contenedor.pack(fill="both", expand=True)

        # --- Sidebar izquierdo con los botones de consulta ---
        self.sidebar = ctk.CTkScrollableFrame(contenedor, width=200, corner_radius=0)
        self.sidebar.pack(fill="y", side="left", padx=(0, 0))

        ctk.CTkLabel(self.sidebar, text="Consultas",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(15, 10))

        # Lista de consultas: (texto del boton, funcion)
        consultas = [
            ("1. Top 10 pobladas",         self.consulta_1),
            ("2. Ciudades por continente",  self.consulta_2),
            ("3. PIB por continente",       self.consulta_3),
            ("4. Temperatura vs vida",      self.consulta_4),
            ("5. Densidad poblacional",     self.consulta_5),
            ("6. Precipitacion anual",      self.consulta_6),
            ("7. Alfabetizacion",           self.consulta_7),
            ("8. Antiguas vs modernas",     self.consulta_8),
            ("9. PIB vs esperanza vida",    self.consulta_9),
            ("10. Poblacion mundial",       self.consulta_10),
        ]

        for texto, funcion in consultas:
            ctk.CTkButton(self.sidebar, text=texto,
                          anchor="w", width=180,
                          command=funcion).pack(pady=3, padx=8)

        # --- Frame de resultados (derecha) ---
        # Usamos un Canvas de tkinter con scrollbar para que las graficas
        # de matplotlib se rendericen correctamente
        import tkinter as tk

        # Contenedor externo del area de resultados
        frame_derecha = ctk.CTkFrame(contenedor, corner_radius=0, fg_color="transparent")
        frame_derecha.pack(fill="both", expand=True, side="left")

        # Scrollbar vertical
        scrollbar = ctk.CTkScrollbar(frame_derecha)
        scrollbar.pack(fill="y", side="right")

        # Canvas que permite el scroll
        self.canvas_scroll = tk.Canvas(frame_derecha, bg="#2b2b2b",
                                       highlightthickness=0,
                                       yscrollcommand=scrollbar.set)
        self.canvas_scroll.pack(fill="both", expand=True, side="left")
        scrollbar.configure(command=self.canvas_scroll.yview)

        # Frame interno donde van los widgets reales
        self.frame_resultados = ctk.CTkFrame(self.canvas_scroll,
                                              corner_radius=0, fg_color="transparent")
        self.ventana_canvas = self.canvas_scroll.create_window(
            (0, 0), window=self.frame_resultados, anchor="nw")

        # Actualizar el area de scroll cuando cambia el contenido
        def actualizar_scroll(event=None):
            self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))

        def ajustar_ancho(event=None):
            self.canvas_scroll.itemconfig(self.ventana_canvas, width=event.width)

        self.frame_resultados.bind("<Configure>", actualizar_scroll)
        self.canvas_scroll.bind("<Configure>", ajustar_ancho)

        # Scroll con rueda del mouse
        def scroll_mouse(event):
            self.canvas_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas_scroll.bind_all("<MouseWheel>", scroll_mouse)

        # Mostrar mensaje de bienvenida al inicio
        self.mostrar_bienvenida()

    # ---------------------------------------------------
    # METODOS DE AYUDA
    # ---------------------------------------------------

    def limpiar_resultados(self):
        """Elimina todo lo que hay en el frame de resultados."""
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

    def mostrar_titulo(self, titulo, subtitulo=""):
        """Muestra un titulo y subtitulo en el frame de resultados."""
        ctk.CTkLabel(self.frame_resultados,
                     text=titulo,
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 2))
        if subtitulo:
            ctk.CTkLabel(self.frame_resultados,
                         text=subtitulo,
                         font=ctk.CTkFont(size=12),
                         text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))

    def mostrar_grafica(self, fig):
        """Incrusta una figura de matplotlib en el frame de resultados."""
        canvas = FigureCanvasTkAgg(fig, master=self.frame_resultados)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=20, pady=10, fill="both", expand=True)
        plt.close(fig)

    def mostrar_tabla(self, dataframe):
        """Muestra un DataFrame como tabla en el frame de resultados."""
        frame_tabla = ctk.CTkFrame(self.frame_resultados)
        frame_tabla.pack(padx=20, pady=10, fill="x")

        columnas = list(dataframe.columns)

        # Encabezados
        for j, col in enumerate(columnas):
            ctk.CTkLabel(frame_tabla, text=str(col),
                         font=ctk.CTkFont(weight="bold"),
                         width=160).grid(row=0, column=j, padx=4, pady=4)
            frame_tabla.grid_columnconfigure(j, weight=1)

        # Filas de datos
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
                     text=f"Dataset cargado: {len(self.df)} ciudades en {self.df['continente'].nunique()} continentes.\nSelecciona una consulta del menu izquierdo.",
                     font=ctk.CTkFont(size=13),
                     text_color="gray",
                     justify="center").pack()

    # ---------------------------------------------------
    # CONSULTAS (10 en total)
    # ---------------------------------------------------

    def consulta_1(self):
        """Top 10 ciudades mas pobladas — grafica de barras horizontales"""
        self.limpiar_resultados()
        self.mostrar_titulo("Top 10 ciudades mas pobladas",
                            "Las 10 ciudades con mayor numero de habitantes")

        # Obtener los datos
        top10 = self.df.nlargest(10, "poblacion")[["ciudad", "pais", "poblacion"]].copy()
        top10["poblacion_millones"] = (top10["poblacion"] / 1_000_000).round(2)

        # Crear la grafica
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(top10["ciudad"][::-1], top10["poblacion_millones"][::-1], color="steelblue")
        ax.set_xlabel("Poblacion (millones)")
        ax.set_title("Top 10 ciudades mas pobladas")
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(top10[["ciudad", "pais", "poblacion_millones"]].reset_index(drop=True))

    def consulta_2(self):
        """Numero de ciudades por continente — grafica de pastel y barras"""
        self.limpiar_resultados()
        self.mostrar_titulo("Ciudades por continente",
                            "Cuantas ciudades del dataset hay en cada continente")

        conteo = self.df["continente"].value_counts().reset_index()
        conteo.columns = ["continente", "cantidad"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

        ax1.pie(conteo["cantidad"], labels=conteo["continente"],
                autopct="%1.0f%%", startangle=90)
        ax1.set_title("Proporcion (%)")

        ax2.bar(conteo["continente"], conteo["cantidad"], color="steelblue")
        ax2.set_ylabel("Cantidad de ciudades")
        ax2.set_title("Total por continente")
        plt.setp(ax2.get_xticklabels(), rotation=25, ha="right")
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(conteo)

    def consulta_3(self):
        """PIB per capita promedio por continente — barras verticales"""
        self.limpiar_resultados()
        self.mostrar_titulo("PIB per capita por continente",
                            "Promedio del PIB per capita en dolares (USD)")

        pib = self.df.groupby("continente")["pib_per_capita"].mean().round(0).reset_index()
        pib.columns = ["continente", "pib_promedio"]
        pib = pib.sort_values("pib_promedio", ascending=False)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(pib["continente"], pib["pib_promedio"], color="steelblue")
        ax.set_ylabel("PIB per capita (USD)")
        ax.set_title("PIB per capita promedio por continente")
        plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(pib)

    def consulta_4(self):
        """Temperatura media vs esperanza de vida — grafica de dispersion"""
        self.limpiar_resultados()
        self.mostrar_titulo("Temperatura vs Esperanza de vida",
                            "Relacion entre el clima y cuanto viven las personas")

        fig, ax = plt.subplots(figsize=(8, 5))

        colores = ["steelblue", "tomato", "seagreen", "orange", "purple", "brown", "teal"]
        for i, continente in enumerate(self.df["continente"].unique()):
            sub = self.df[self.df["continente"] == continente]
            ax.scatter(sub["temperatura_media"], sub["esperanza_vida"],
                       label=continente, color=colores[i % len(colores)], alpha=0.7)

        ax.set_xlabel("Temperatura media (C)")
        ax.set_ylabel("Esperanza de vida (anos)")
        ax.set_title("Temperatura media vs Esperanza de vida")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)

        resumen = self.df.groupby("continente")[["temperatura_media", "esperanza_vida"]].mean().round(1).reset_index()
        self.mostrar_tabla(resumen)

    def consulta_5(self):
        """Top 15 ciudades con mayor densidad poblacional"""
        self.limpiar_resultados()
        self.mostrar_titulo("Densidad poblacional - Top 15",
                            "Ciudades con mas habitantes por km2")

        top = self.df.nlargest(15, "densidad")[["ciudad", "pais", "densidad"]].reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(top["ciudad"][::-1], top["densidad"][::-1], color="tomato")
        ax.set_xlabel("Habitantes por km2")
        ax.set_title("Top 15 ciudades mas densas")
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(top)

    def consulta_6(self):
        """Precipitacion anual por continente — min, promedio y max"""
        self.limpiar_resultados()
        self.mostrar_titulo("Precipitacion anual por continente",
                            "Minima, promedio y maxima precipitacion en mm por ano")

        prec = self.df.groupby("continente")["precipitacion_anual"].agg(
            minimo="min", promedio="mean", maximo="max").round(0).reset_index()

        fig, ax = plt.subplots(figsize=(9, 4))
        x = range(len(prec))
        ancho = 0.25

        ax.bar([i - ancho for i in x], prec["minimo"],   ancho * 1.8, label="Minimo",   color="skyblue")
        ax.bar([i           for i in x], prec["promedio"], ancho * 1.8, label="Promedio", color="steelblue")
        ax.bar([i + ancho for i in x], prec["maximo"],   ancho * 1.8, label="Maximo",   color="navy")

        ax.set_xticks(list(x))
        ax.set_xticklabels(prec["continente"], rotation=20, ha="right")
        ax.set_ylabel("mm / ano")
        ax.set_title("Precipitacion anual por continente")
        ax.legend()
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(prec)

    def consulta_7(self):
        """Tasa de alfabetizacion promedio por continente"""
        self.limpiar_resultados()
        self.mostrar_titulo("Alfabetizacion por continente",
                            "Porcentaje promedio de personas que saben leer y escribir")

        alfa = self.df.groupby("continente")["alfabetizacion"].mean().round(1).sort_values().reset_index()
        alfa.columns = ["continente", "alfabetizacion"]

        fig, ax = plt.subplots(figsize=(8, 4))
        colores = ["tomato" if v < 90 else "seagreen" for v in alfa["alfabetizacion"]]
        ax.barh(alfa["continente"], alfa["alfabetizacion"], color=colores)
        ax.axvline(90, color="gray", linestyle="--", linewidth=1, label="90%")
        ax.set_xlabel("Alfabetizacion (%)")
        ax.set_title("Tasa de alfabetizacion por continente")
        ax.set_xlim(0, 105)
        ax.legend()
        ax.grid(axis="x", alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)
        self.mostrar_tabla(alfa)

    def consulta_8(self):
        """Ciudades mas antiguas y mas modernas segun ano de fundacion"""
        self.limpiar_resultados()
        self.mostrar_titulo("Ciudades mas antiguas y mas modernas",
                            "Las 5 ciudades mas antiguas y las 5 mas recientes")

        antiguas = self.df.nsmallest(5, "año_fundacion")[["ciudad", "pais", "año_fundacion"]]
        modernas = self.df.nlargest(5, "año_fundacion")[["ciudad", "pais", "año_fundacion"]]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        ax1.barh(antiguas["ciudad"], antiguas["año_fundacion"], color="purple")
        ax1.set_title("Las 5 mas antiguas")
        ax1.set_xlabel("Ano de fundacion")

        ax2.barh(modernas["ciudad"][::-1], modernas["año_fundacion"][::-1], color="orange")
        ax2.set_title("Las 5 mas modernas")
        ax2.set_xlabel("Ano de fundacion")

        fig.tight_layout()
        self.mostrar_grafica(fig)

        combinado = pd.concat([antiguas, modernas]).reset_index(drop=True)
        self.mostrar_tabla(combinado)

    def consulta_9(self):
        """Correlacion entre PIB per capita y esperanza de vida"""
        self.limpiar_resultados()
        self.mostrar_titulo("Correlacion: PIB vs Esperanza de vida",
                            "A mayor PIB per capita, mayor esperanza de vida?")

        fig, ax = plt.subplots(figsize=(8, 5))

        colores = ["steelblue", "tomato", "seagreen", "orange", "purple", "brown", "teal"]
        for i, continente in enumerate(self.df["continente"].unique()):
            sub = self.df[self.df["continente"] == continente]
            ax.scatter(sub["pib_per_capita"], sub["esperanza_vida"],
                       label=continente, color=colores[i % len(colores)], alpha=0.8)

        # Linea de tendencia simple (regresion lineal manual)
        x = self.df["pib_per_capita"].dropna()
        y = self.df["esperanza_vida"].dropna()
        mask = self.df["pib_per_capita"].notna() & self.df["esperanza_vida"].notna()
        x_vals = self.df.loc[mask, "pib_per_capita"]
        y_vals = self.df.loc[mask, "esperanza_vida"]
        pendiente = x_vals.cov(y_vals) / x_vals.var()
        intercepto = y_vals.mean() - pendiente * x_vals.mean()
        ax.plot([x_vals.min(), x_vals.max()],
                [pendiente * x_vals.min() + intercepto, pendiente * x_vals.max() + intercepto],
                color="black", linewidth=1.5, linestyle="--", label="Tendencia")

        ax.set_xlabel("PIB per capita (USD)")
        ax.set_ylabel("Esperanza de vida (anos)")
        ax.set_title("PIB per capita vs Esperanza de vida")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.4)
        fig.tight_layout()

        self.mostrar_grafica(fig)

        # Tabla de correlacion entre variables numericas clave
        corr = self.df[["pib_per_capita", "esperanza_vida", "alfabetizacion"]].corr().round(3)
        self.mostrar_tabla(corr.reset_index().rename(columns={"index": "variable"}))

    def consulta_10(self):
        """Distribucion de la poblacion total por continente"""
        self.limpiar_resultados()
        self.mostrar_titulo("Distribucion de poblacion mundial",
                            "Suma total de habitantes por continente en el dataset")

        pob = self.df.groupby("continente")["poblacion"].sum().sort_values(ascending=False).reset_index()
        pob.columns = ["continente", "poblacion_total"]
        pob["porcentaje"] = (pob["poblacion_total"] / pob["poblacion_total"].sum() * 100).round(1)
        pob["millones"] = (pob["poblacion_total"] / 1_000_000).round(1)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

        ax1.pie(pob["poblacion_total"], labels=pob["continente"],
                autopct="%1.1f%%", startangle=90)
        ax1.set_title("Proporcion de poblacion (%)")

        ax2.barh(pob["continente"][::-1], pob["millones"][::-1], color="steelblue")
        ax2.set_xlabel("Millones de habitantes")
        ax2.set_title("Poblacion total por continente")
        ax2.grid(axis="x", alpha=0.4)

        fig.tight_layout()
        self.mostrar_grafica(fig)
        self.mostrar_tabla(pob[["continente", "millones", "porcentaje"]])




if __name__ == "__main__":
    app = VentanaLogin()
    app.mainloop()