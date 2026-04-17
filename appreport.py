import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. Estilos de Interfaz (Tarjetas XL y Círculos Informativos)
st.set_page_config(page_title="Dashboard Sauco v6", layout="wide")

st.markdown("""
    <style>
    .user-card {
        background-color: white;
        border-radius: 25px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        margin-bottom: 25px;
        border: 1px solid #f0f0f0;
    }
    .time-circle {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0 auto 15px;
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .time-val { font-size: 1.7em; font-weight: 800; margin: 0; line-height: 1; }
    .status-val { font-size: 0.7em; font-weight: 600; text-transform: uppercase; margin-top: 5px; }
    .name-val { color: #1a202c; font-weight: 700; font-size: 1.1em; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Lógica de Organización
REEMPLAZOS = {
    "sthefanymoreno": "Nathalia Moreno",
    "gestor barranquilla av villas": "Armando Vega"
}

def obtener_equipo(nombre):
    n = nombre.lower().strip()
    
    # Wendy Garcia movida a Proyectos
    proyectos = ["ludy novoa", "viviana capera", "wendy garcia"]
    
    davivienda = [
        "danna bernal", "angie hernandez", "britney sanchez", 
        "britny sanchez", "ingrid mahecha", "nathalia moreno"
    ]
    
    if n in proyectos:
        return "Equipo Proyectos", "#1e40af" # Azul
    elif n in davivienda:
        return "Equipo Davivienda - Comfandi", "#991b1b" # Rojo
    else:
        return "Equipo Avillas", "#5b21b6" # Morado

def calcular_puntos(nombre, hora_ini):
    n = nombre.lower().strip()
    # Luz Pulido: 8:00 AM / Wendy Olaya: 8:30 AM / Otros: 7:30 AM
    if "luz pulido" in n:
        h_o, m_o = 8, 0
    elif "wendy olaya" in n:
        h_o, m_o = 8, 30
    else:
        h_o, m_o = 7, 30
    
    oficial = hora_ini.replace(hour=h_o, minute=m_o, second=0)
    margen = oficial + timedelta(minutes=10)
    
    if hora_ini <= oficial:
        return "#16a34a", "A TIEMPO"
    elif hora_ini <= margen:
        return "#d97706", "EN MARGEN"
    else:
        return "#dc2626", "RETARDO"

# 3. Encabezado y Gestión de Logo
col_l, col_t = st.columns([1, 4])
with col_l:
    # Nombres posibles del logo
    posibles_logos = [
        "01_Curvas_Logos versiones_marca interna SAUCO_Mesa de trabajo 1 copia 14.jpg",
        "logo_sauco.jpg"
    ]
    logo_encontrado = False
    for p in posibles_logos:
        if os.path.exists(p):
            st.image(p, width=180)
            logo_encontrado = True
            break
    
    if not logo_encontrado:
        st.info("📌 Logo no detectado. Verifica el nombre del archivo.")

with col_t:
    st.title("Dashboard Inicio Jornada")
    st.write("Configuración Actualizada: Wendy Garcia en Equipo Proyectos.")

# 4. Procesamiento de Reporte
file = st.file_uploader("Cargar reporte (.txt)", type=['txt'])

if file:
    df = pd.read_csv(file, sep='\t')
    df['full_name'] = df['full_name'].str.lower().str.strip().replace(REEMPLAZOS)
    df['call_date'] = pd.to_datetime(df['call_date'])
    
    resumen = df.sort_values('call_date').groupby('full_name').first().reset_index()
    
    orden_equipos = ["Equipo Proyectos", "Equipo Davivienda - Comfandi", "Equipo Avillas"]
    
    for eq in orden_equipos:
        m_equipo = []
        for _, r in resumen.iterrows():
            eq_nom, eq_col = obtener_equipo(r['full_name'])
            if eq_nom == eq:
                c_est, t_est = calcular_puntos(r['full_name'], r['call_date'])
                m_equipo.append({
                    "n": r['full_name'].title(), "h": r['call_date'].strftime('%H:%M'),
                    "c": c_est, "s": t_est, "ec": eq_col
                })
        
        if m_equipo:
            st.markdown(f"<h2 style='color:{m_equipo[0]['ec']}; border-bottom: 3px solid {m_equipo[0]['ec']}'>{eq}</h2>", unsafe_allow_html=True)
            cols = st.columns(4)
            for idx, p in enumerate(m_equipo):
                with cols[idx % 4]:
                    st.markdown(f"""
                        <div class="user-card">
                            <div class="time-circle" style="background-color: {p['c']}">
                                <div class="time-val">{p['h']}</div>
                                <div class="status-val">{p['s']}</div>
                            </div>
                            <div class="name-val">{p['n']}</div>
                        </div>
                    """, unsafe_allow_html=True)
else:
    st.warning("Por favor, sube el reporte para generar la visualización.")
