# dashboard.py
# Proyecto: Dashboard de Camaras Fotograficas
# Materia: Fundamentos de Inteligencia Artificial

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Dashboard Camaras", layout="wide")

# --------------------------------------------------
# LEER DATOS
# --------------------------------------------------

CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CSV = os.path.join(CARPETA, "csv_camaras_2.csv")
ARCHIVO_USUARIOS = os.path.join(CARPETA, "usuarios.txt")


def leer_usuarios():
    usuarios = {}
    try:
        with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
            for linea in f:
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
        st.error("No se encontro el archivo usuarios.txt")
    return usuarios


@st.cache_data
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



if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.nombre = ""
    st.session_state.rol = ""

if not st.session_state.autenticado:
    st.title("Dashboard de Camaras Fotograficas")
    st.write("Inicia sesion para continuar.")

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contrasena", type="password")
    boton = st.button("Entrar")

    if boton:
        if not usuario or not contrasena:
            st.error("Por favor llena todos los campos.")
        elif len(usuario) < 3:
            st.error("El usuario debe tener al menos 3 caracteres.")
        elif len(contrasena) < 4:
            st.error("La contrasena debe tener al menos 4 caracteres.")
        else:
            usuarios = leer_usuarios()
            if usuario not in usuarios:
                st.error("Usuario no encontrado.")
            elif contrasena != usuarios[usuario]["contrasena"]:
                st.error("Contrasena incorrecta.")
            else:
                st.session_state.autenticado = True
                st.session_state.nombre = usuarios[usuario]["nombre"]
                st.session_state.rol = usuarios[usuario]["rol"]
                st.rerun()

    st.caption("Prueba: admin / admin123")
    st.stop()



df = leer_csv()

st.title("Dashboard de Camaras Fotograficas")
st.write(f"Bienvenido, **{st.session_state.nombre}** | Rol: {st.session_state.rol}")
st.write(f"Dataset cargado: {len(df)} camaras de {df['marca'].nunique()} marcas.")
st.divider()

consulta = st.sidebar.selectbox("Selecciona una consulta", [
    "1. Camaras por marca",
    "2. Distribucion de precios",
    "3. Top 10 mas caras",
    "4. Top 10 mas baratas",
    "5. Precio promedio por marca",
    "6. Zoom promedio por marca",
    "7. Peso vs Precio",
    "8. Almacenamiento incluido",
    "9. Enfoque normal vs macro",
    "10. Camaras por rango de precio",
])

if st.sidebar.button("Cerrar sesion"):
    st.session_state.autenticado = False
    st.rerun()

# --------------------------------------------------
# CONSULTAS
# --------------------------------------------------

if consulta == "1. Camaras por marca":
    st.subheader("Camaras por marca")
    st.caption("Top 15 marcas con mas modelos en el dataset")

    conteo = df["marca"].value_counts().head(15).reset_index()
    conteo.columns = ["marca", "cantidad"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(conteo["marca"][::-1], conteo["cantidad"][::-1], color="#4a7db5")
    ax.set_xlabel("Numero de modelos")
    ax.set_title("Top 15 marcas con mas modelos")
    ax.grid(axis="x", alpha=0.4)
    fig.tight_layout()
    st.pyplot(fig)
    st.dataframe(conteo, use_container_width=True)

elif consulta == "2. Distribucion de precios":
    st.subheader("Distribucion de precios")
    st.caption("Como se distribuyen los precios de todas las camaras")

    precios = df["precio"].dropna()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(precios, bins=30, color="#4a7db5", edgecolor="white")
    ax.set_xlabel("Precio (USD)")
    ax.set_ylabel("Numero de camaras")
    ax.set_title("Distribucion de precios")
    ax.grid(axis="y", alpha=0.4)
    fig.tight_layout()
    st.pyplot(fig)

    resumen = precios.describe().round(2).reset_index()
    resumen.columns = ["estadistica", "valor"]
    st.dataframe(resumen, use_container_width=True)

elif consulta == "3. Top 10 mas caras":
    st.subheader("Top 10 camaras mas caras")
    st.caption("Los modelos con el precio mas alto en el dataset")

    top = df.nlargest(10, "precio")[["modelo", "marca", "precio"]].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top["modelo"][::-1], top["precio"][::-1], color="#c0392b")
    ax.set_xlabel("Precio (USD)")
    ax.set_title("Top 10 camaras mas caras")
    ax.grid(axis="x", alpha=0.4)
    fig.tight_layout()
    st.pyplot(fig)
    st.dataframe(top, use_container_width=True)

elif consulta == "4. Top 10 mas baratas":
    st.subheader("Top 10 camaras mas baratas")
    st.caption("Los modelos con el precio mas bajo (excluyendo precio cero)")

    baratas = df[df["precio"] > 0].nsmallest(10, "precio")[
        ["modelo", "marca", "precio"]].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(baratas["modelo"][::-1], baratas["precio"][::-1], color="#27ae60")
    ax.set_xlabel("Precio (USD)")
    ax.set_title("Top 10 camaras mas baratas")
    ax.grid(axis="x", alpha=0.4)
    fig.tight_layout()
    st.pyplot(fig)
    st.dataframe(baratas, use_container_width=True)

elif consulta == "5. Precio promedio por marca":
    st.subheader("Precio promedio por marca")
    st.caption("Promedio de precio de las marcas con al menos 5 modelos")

    marcas_validas = df["marca"].value_counts()
    marcas_validas = marcas_validas[marcas_validas >= 5].index
    precio_marca = (df[df["marca"].isin(marcas_validas)]
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
    st.pyplot(fig)
    st.dataframe(precio_marca, use_container_width=True)

elif consulta == "6. Zoom promedio por marca":
    st.subheader("Zoom promedio por marca")
    st.caption("Alcance de zoom promedio de cada marca")

    marcas_validas = df["marca"].value_counts()
    marcas_validas = marcas_validas[marcas_validas >= 5].index
    zoom_marca = (df[df["marca"].isin(marcas_validas)]
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
    st.pyplot(fig)
    st.dataframe(zoom_marca, use_container_width=True)

elif consulta == "7. Peso vs Precio":
    st.subheader("Peso vs Precio")
    st.caption("Hay relacion entre el peso de la camara y su precio?")

    datos = df[["peso", "precio"]].dropna()
    datos = datos[(datos["peso"] > 0) & (datos["precio"] > 0)]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(datos["peso"], datos["precio"], alpha=0.4, color="#4a7db5", s=20)
    ax.set_xlabel("Peso (gramos)")
    ax.set_ylabel("Precio (USD)")
    ax.set_title("Peso vs Precio de la camara")
    ax.grid(alpha=0.4)
    fig.tight_layout()
    st.pyplot(fig)

    resumen = datos.describe().round(2).reset_index()
    resumen.columns = ["estadistica", "peso", "precio"]
    st.dataframe(resumen, use_container_width=True)

elif consulta == "8. Almacenamiento incluido":
    st.subheader("Almacenamiento incluido")
    st.caption("Cuantas camaras incluyen cada cantidad de almacenamiento (MB)")

    almacenamiento = df["almacenamiento"].dropna()
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
    st.pyplot(fig)
    st.dataframe(conteo, use_container_width=True)

elif consulta == "9. Enfoque normal vs macro":
    st.subheader("Enfoque normal vs Enfoque macro")
    st.caption("Comparacion del rango de enfoque entre los dos modos por marca")

    marcas_validas = df["marca"].value_counts()
    marcas_validas = marcas_validas[marcas_validas >= 5].index
    resumen = (df[df["marca"].isin(marcas_validas)]
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
    st.pyplot(fig)
    st.dataframe(resumen, use_container_width=True)

elif consulta == "10. Camaras por rango de precio":
    st.subheader("Camaras por rango de precio")
    st.caption("Cuantos modelos hay en cada rango de precio")

    rangos = [0, 100, 200, 300, 500, 800, 1500, 8000]
    etiquetas = ["0-100", "100-200", "200-300",
                 "300-500", "500-800", "800-1500", "1500+"]
    df_valido = df[df["precio"] > 0].copy()
    df_valido["rango"] = pd.cut(df_valido["precio"], bins=rangos, labels=etiquetas)
    conteo = df_valido["rango"].value_counts().sort_index().reset_index()
    conteo.columns = ["rango_precio", "cantidad"]

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(conteo["rango_precio"], conteo["cantidad"], color="#4a7db5")
        ax.set_xlabel("Rango de precio (USD)")
        ax.set_ylabel("Cantidad de camaras")
        ax.set_title("Camaras por rango de precio")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        ax.grid(axis="y", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.pie(conteo["cantidad"], labels=conteo["rango_precio"],
                autopct="%1.0f%%", startangle=90)
        ax2.set_title("Proporcion (%)")
        fig2.tight_layout()
        st.pyplot(fig2)

    st.dataframe(conteo, use_container_width=True)

    # streamlit run dashboard.py
    # http://localhost:8501