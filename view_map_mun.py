import streamlit as st
import os
import pandas as pd
from PIL import Image

st.set_page_config(layout="wide")
st.title("Mapas de población")

# -----------------------------
# CONFIG
# -----------------------------
BASE_PATH = "output"

# -----------------------------
# FUNC: leer metadata desde filenames
# -----------------------------
def load_maps(tipo):
    base_dir = os.path.join(BASE_PATH, tipo + "_ae", "mapas", "mun")
    
    data = []
    
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".jpg"):
                
                parts = f.replace(".jpg","").split("_")
                
                # mapa_ENT_SEXO_EDAD_AÑO(_vc)
                if len(parts) < 5:
                    continue
                
                ent = parts[1]
                sexo = parts[2]
                edad = parts[3]
                ano = parts[4]
                
                data.append({
                    "ent": ent,
                    "sexo": sexo,
                    "edad": edad,
                    "ano": int(ano),
                    "path": os.path.join(root, f)
                })
    
    return pd.DataFrame(data)

# -----------------------------
# SELECTORES
# -----------------------------
tipo = st.sidebar.selectbox("Tipo", ["VP", "VC"])

df_maps = load_maps(tipo)

if df_maps.empty:
    st.warning("No hay mapas disponibles")
    st.stop()

# limpieza por si acaso
df_maps["sexo"] = df_maps["sexo"].str.strip()
df_maps["ent"] = df_maps["ent"].str.strip()

# filtros dinámicos
sexo_sel = st.sidebar.multiselect("Sexo", sorted(df_maps["sexo"].unique()))

anio_sel = st.sidebar.multiselect("Año", sorted(df_maps["ano"].unique()))

df_base = df_maps[
    (df_maps["sexo"].isin(sexo_sel) &
    (df_maps["ano"].isin(anio_sel))
]

# entidades dinámicas
entidades = sorted(df_base["ent"].unique())

ent_sel = st.sidebar.multiselect(
    "Entidad",
    entidades,
    default=entidades
)

# edades dinámicas
edades = sorted(df_base["edad"].unique())

edad_sel = st.sidebar.multiselect(
    "Edad",
    edades,
    default=edades
)

# -----------------------------
# FILTRO FINAL
# -----------------------------
df_final = df_base[
    (df_base["ent"].isin(ent_sel)) &
    (df_base["edad"].isin(edad_sel))
]

# ordenar edades correctamente
orden_edades = ["95-99","100-104","105-109","110-114","115+"]
df_final["edad"] = pd.Categorical(df_final["edad"], categories=orden_edades, ordered=True)
df_final = df_final.sort_values(["ent","edad"])

# -----------------------------
# VISUALIZACIÓN
# -----------------------------
st.subheader(f"{sexo_sel} - {anio_sel}")

if df_final.empty:
    st.warning("No hay mapas para estos filtros")
else:
    st.write(f"Mapas mostrados: {len(df_final)}")

    for i in range(0, len(df_final), 2):
        cols = st.columns(2)
        
        subset = df_final.iloc[i:i+2]
        
        for j, (_, row) in enumerate(subset.iterrows()):
            with cols[j]:
                st.caption(f"{row['ent']} | {row['edad']}")
                st.image(row["path"], use_container_width=True)
