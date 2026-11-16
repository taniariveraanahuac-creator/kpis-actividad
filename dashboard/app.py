# KPIs en acción · Tablero docente con Streamlit
# Basado en el patrón de Sven-Bo/streamlit-sales-dashboard:
# Excel → filtros en la barra lateral → KPIs principales → gráficas.
#
# Ejecutar en tu computadora:   pip install -r requirements.txt
#                               streamlit run app.py

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="KPIs en acción · Tablero", page_icon="🚦", layout="wide")

COLORES = {"VERDE": "#15803d", "AMARILLO": "#ca8a04", "ROJO": "#b91c1c"}
ORDEN = ["VERDE", "AMARILLO", "ROJO"]


# ---- LEER EXCEL ----
@st.cache_data
def leer_datos():
    df = pd.read_excel("kpis_casos.xlsx", sheet_name="KPIs", engine="openpyxl")
    df["Equipo_txt"] = df["Grupo"] + " · E" + df["Equipo"].astype(str) + " · " + df["Caso"]
    return df


df = leer_datos()

# ---- BARRA LATERAL: FILTROS ----
st.sidebar.header("🔎 Filtra aquí")
grupo = st.sidebar.multiselect("Grupo:", options=sorted(df["Grupo"].unique()), default=sorted(df["Grupo"].unique()))
equipos_disp = sorted(df[df["Grupo"].isin(grupo)]["Equipo_txt"].unique())
equipo = st.sidebar.multiselect("Equipo y caso:", options=equipos_disp, default=equipos_disp)
semaforo = st.sidebar.multiselect("Semáforo:", options=ORDEN, default=ORDEN)
mes = st.sidebar.slider("Mes a evaluar:", 1, 6, 6)

base = df.query("Grupo == @grupo & Equipo_txt == @equipo")
corte = base[base["Mes"] == mes]
corte = corte[corte["Semaforo"].isin(semaforo)]
if corte.empty:
    st.warning("No hay datos con estos filtros.")
    st.stop()

# ---- PÁGINA PRINCIPAL ----
st.title("🚦 KPIs en acción · Tablero docente")
st.caption(f"Liderazgo y Administración · semáforo calculado con el tabulador de la clase · mes {mes} de 6")
st.markdown("##")

# KPIs PRINCIPALES
total = len(corte)
verdes = int((corte["Semaforo"] == "VERDE").sum())
rojos = int((corte["Semaforo"] == "ROJO").sum())
eq_rojo = corte[corte["Semaforo"] == "ROJO"]["Equipo_txt"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("KPIs evaluados", total)
c2.metric("En verde", f"{verdes}  ({verdes / total:.0%})")
c3.metric("En rojo", rojos)
c4.metric("Equipos con al menos un rojo", eq_rojo)

st.markdown("---")

# SEMÁFORO POR CASO [BARRAS APILADAS]
por_caso = corte.groupby(["Equipo_txt", "Semaforo"]).size().reset_index(name="KPIs")
fig_caso = px.bar(
    por_caso, x="KPIs", y="Equipo_txt", color="Semaforo", orientation="h",
    color_discrete_map=COLORES, category_orders={"Semaforo": ORDEN},
    title="<b>Semáforo por caso</b>", template="plotly_white",
)
fig_caso.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis_title=None, xaxis=dict(showgrid=False, dtick=1), legend_title=None)

# CUMPLIMIENTO VS META [BARRAS]
corte = corte.assign(Etiqueta=corte["Caso"] + " · " + corte["KPI"])
fig_cump = px.bar(
    corte.sort_values("Cumplimiento"), x="Cumplimiento", y="Etiqueta", color="Semaforo", orientation="h",
    color_discrete_map=COLORES, category_orders={"Semaforo": ORDEN},
    title="<b>Real ÷ meta × 100</b> (en ↓ máximo, menos es mejor)", template="plotly_white",
)
fig_cump.add_vline(x=100, line_dash="dash", line_color="#4c5d6d")
fig_cump.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis_title=None, xaxis_title="% de la meta", legend_title=None, height=max(380, 26 * len(corte)))

st.plotly_chart(fig_caso, width="stretch")
st.plotly_chart(fig_cump, width="stretch")

# EVOLUCIÓN DE 6 MESES [LÍNEAS]
st.markdown("---")
caso_sel = st.selectbox("Evolución de un caso:", options=sorted(base["Equipo_txt"].unique()))
evo = base[base["Equipo_txt"] == caso_sel]
cols = st.columns(3)
for i, (kpi, d) in enumerate(evo.groupby("KPI_num")):
    fig = px.line(d, x="Mes", y="Valor", markers=True, title=f"<b>{d['KPI'].iloc[0]}</b> · {d['Tipo'].iloc[0]}", template="plotly_white")
    fig.add_hline(y=d["Meta"].iloc[0], line_dash="dash", line_color="#4c5d6d", annotation_text="meta")
    fig.update_traces(line_color=COLORES[d["Semaforo"].iloc[-1]])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(dtick=1), yaxis_title=d["Unidad"].iloc[0] or None)
    cols[i].plotly_chart(fig, width="stretch")

with st.expander("Ver tabla de datos"):
    st.dataframe(corte.drop(columns=["Equipo_txt", "Etiqueta"]), width="stretch", hide_index=True)

# ---- OCULTAR MENÚ DE STREAMLIT ----
st.markdown("<style>#MainMenu{visibility:hidden}footer{visibility:hidden}</style>", unsafe_allow_html=True)
