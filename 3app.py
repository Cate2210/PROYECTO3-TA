
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt


# Configuración de la página
st.set_page_config(page_title="Análisis de Homicidios en Colombia", layout="wide")
st.title("Análisis de Homicidios en Colombia — 2024")
gdf= gpd.read_parquet("mapatasa.parquet")
# --- Cargar y limpiar datos ---
@st.cache_data
def load_data():
    """Carga y limpia los datos del archivo CSV."""
    df = pd.read_csv("tasamunicipal.csv")
    df.rename(columns={
        'HOMICIDIO TOTAL': 'homicidio_total',
        'TASA MUNICIPAL': 'tasa_municipal',
        'MUNICIPIO': 'municipio',
        'DEPARTAMENTO': 'departamento'
    }, inplace=True)

    # Asegurar que las columnas numéricas sean válidas
    df['homicidio_total'] = pd.to_numeric(df['homicidio_total'], errors='coerce')
    df['tasa_municipal'] = pd.to_numeric(df['tasa_municipal'], errors='coerce')
    df.dropna(subset=['homicidio_total', 'tasa_municipal'], inplace=True)
    return df

df = load_data()

#Tasa de homicidios por municipio ---
st.subheader("Tasa de homicidios por municipio (por 100.000 hab.)")
fig_tasa = px.bar(
    df.sort_values("tasa_municipal", ascending=False).head(30), # Mostrar solo los 20 principales
    x="municipio",
    y="tasa_municipal",
    color="tasa_municipal",
    color_continuous_scale="RdPu", # Cambiado a una escala rojo-púrpura
    labels={
        "tasa_municipal": "Tasa de Homicidios",
        "municipio": "Municipio"
    },
    title="Tasa de Homicidios por Municipio"
)
st.plotly_chart(fig_tasa, use_container_width=True)

#Top municipios con más y menos homicidios (con histogramas) ---
st.subheader("Top municipios según número absoluto de homicidios")
col1, col2 = st.columns(2)

with col1:
    st.write("10 con más homicidios")
    top_10 = df.sort_values("homicidio_total", ascending=False).head(10)
    fig_top_10 = px.bar(
        top_10,
        x="homicidio_total",
        y="municipio",
        orientation='h',
        title="Top 10 Municipios con Más Homicidios",
        labels={"homicidio_total": "Número de Homicidios", "municipio": "Municipio"},
        color_discrete_sequence=px.colors.sequential.Magenta # Paleta de magentas
    )
    fig_top_10.update_yaxes(categoryorder='total ascending')
    st.plotly_chart(fig_top_10, use_container_width=True)

with col2:
    st.write("10 con menos homicidios")
    bottom_10 = df.sort_values("homicidio_total", ascending=True).head(10)
    fig_bottom_10 = px.bar(
        bottom_10,
        x="homicidio_total",
        y="municipio",
        orientation='h',
        title="Top 10 Municipios con Menos Homicidios",
        labels={"homicidio_total": "Número de Homicidios", "municipio": "Municipio"},
        color_discrete_sequence=px.colors.sequential.Purp # Paleta de púrpuras
    )
    fig_bottom_10.update_yaxes(categoryorder='total ascending')
    st.plotly_chart(fig_bottom_10, use_container_width=True)

#Distribución por departamento ---
st.subheader("Distribución de homicidios por departamento")
dept = df.groupby("departamento")["homicidio_total"].sum().reset_index()

fig_dept = px.bar(
    dept.sort_values("homicidio_total", ascending=False),
    x="departamento",
    y="homicidio_total",
    color="homicidio_total",
    color_continuous_scale="Purpor", # Paleta púrpura-naranja
    labels={
        "homicidio_total": "Homicidios Totales",
        "departamento": "Departamento"
    },
    title="Distribución de Homicidios por Departamento"
)
st.plotly_chart(fig_dept, use_container_width=True)


import matplotlib.colors as mcolors

# Definir paleta personalizada (rosado → fucsia → morado fuerte)
colors = ["#e7cfe2", "#E081A6", "#a53a93", "#EE22EE"]
cmap_fucsia_morado = mcolors.LinearSegmentedColormap.from_list("fucsia_morado", colors)

# Limitar el rango para contraste
vmax = gdf["TASA MUNICIPAL"].quantile(0.95)

# Graficar
fig, ax = plt.subplots(1, 1, figsize=(8, 8), facecolor="none")
gdf_plot = gdf.plot(
    column="TASA MUNICIPAL",
    ax=ax,
    cmap=cmap_fucsia_morado,
    vmin=0,
    vmax=vmax,
    legend=False,   # quitamos la leyenda automática
    missing_kwds={
        "color": "white",
        "edgecolor": "grey",
        "hatch": "///",
        "label": "Sin datos"
    }
)

# Añadir barra de colores más pequeña
sm = plt.cm.ScalarMappable(cmap=cmap_fucsia_morado, 
                           norm=plt.Normalize(vmin=0, vmax=vmax))
sm._A = []
cbar = fig.colorbar(sm, ax=ax, shrink=0.5)  # <-- shrink controla el tamaño
cbar.ax.tick_params(labelsize=8)            # etiquetas más pequeñas

# Título y fondo
ax.axis("off")
fig.patch.set_alpha(0)
ax.set_facecolor("none")

st.pyplot(fig)
