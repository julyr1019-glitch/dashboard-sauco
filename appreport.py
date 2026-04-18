import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Dashboard Sauco v7", layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .user-card { background-color: white; border-radius: 20px; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #eee; }
    .time-circle { width: 110px; height: 110px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0 auto 10px; color: white; font-weight: bold; }
    .time-val { font-size: 1.5em; margin: 0; line-height: 1.2;}
    .status-val { font-size: 0.65em; text-transform: uppercase; margin: 0; }
    .name-val { color: #333; font-weight: bold; font-size: 1em; margin-top: 8px;}
    </style>
    """, unsafe_allow_html=True)

REEMPLAZOS = {"sthefanymoreno": "Nathalia Moreno", "gestor barranquilla av villas": "Armando Vega"}

def obtener_equipo(nombre):
    n = nombre.lower().strip()
    if n in ["ludy novoa", "viviana capera", "wendy garcia"]: return "Equipo Proyectos", "#1e40af"
    elif n in ["danna bernal", "angie hernandez", "britney sanchez", "britny sanchez", "ingrid mahecha", "nathalia moreno"]: return "Equipo Davivienda - Comfandi", "#991b1b"
    else: return "Equipo Avillas", "#5b21b6"

def calcular_puntos(nombre, hora_ini):
    n = nombre.lower().strip()
    if "luz pulido" in n: h_o, m_o = 8, 0
    elif "wendy olaya" in n: h_o, m_o = 8, 30
    else: h_o, m_o = 7, 30
    
    oficial = hora_ini.replace(hour=h_o, minute=m_o, second=0)
    margen = oficial + timedelta(minutes=10)
    
    if hora_ini <= oficial: return "#16a34a", "A TIEMPO"
    elif hora_ini <= margen: return "#d97706", "EN MARGEN"
    else: return "#dc2626", "RETARDO"

# --- INTERFAZ ---
col_l, col_t = st.columns([1, 4])
with col_l:
    if os.path.exists("logo_sauco.jpg"): st.image("logo_sauco.jpg", width=160)
with col_t:
    st.title("Dashboard Inicio Jornada")
    st.write("Control Operativo y Reporte para Talento Humano")

# --- BARRA LATERAL: NOVEDADES MANUALES ---
st.sidebar.header("📝 Registro de Novedades")
st.sidebar.write("Ingresa los nombres de los asesores con novedad (separados por coma):")
novedades_input = st.sidebar.text_area("Ejemplo: Juan Perez, Maria Gomez", "")

# Procesar novedades manuales
lista_novedades = [n.strip() for n in novedades_input.split(",") if n.strip()]

# --- PROCESAMIENTO DEL ARCHIVO ---
file = st.file_uploader("Cargar reporte de llamadas (.txt)", type=['txt'])

if file:
    df = pd.read_csv(file, sep='\t')
    df['full_name'] = df['full_name'].str.lower().str.strip().replace(REEMPLAZOS)
    df['call_date'] = pd.to_datetime(df['call_date'])
    
    resumen = df.sort_values('call_date').groupby('full_name').first().reset_index()
    
    # Lista para guardar todos los datos exportables
    datos_exportacion = []
    
    orden_equipos = ["Equipo Proyectos", "Equipo Davivienda - Comfandi", "Equipo Avillas", "Novedades Reportadas"]
    
    for eq in orden_equipos:
        m_equipo = []
        
        # Procesar personas que sí vinieron
        if eq != "Novedades Reportadas":
            for _, r in resumen.iterrows():
                eq_nom, eq_col = obtener_equipo(r['full_name'])
                if eq_nom == eq and r['full_name'].title() not in [n.title() for n in lista_novedades]:
                    c_est, t_est = calcular_puntos(r['full_name'], r['call_date'])
                    hora_str = r['call_date'].strftime('%H:%M')
                    m_equipo.append({"n": r['full_name'].title(), "h": hora_str, "c": c_est, "s": t_est, "ec": eq_col})
                    datos_exportacion.append({"Asesor": r['full_name'].title(), "Equipo": eq, "Hora Ingreso": hora_str, "Estado": t_est, "Fecha": r['call_date'].strftime('%Y-%m-%d')})
        
        # Procesar Novedades (Ausentes)
        else:
            eq_col = "#64748b" # Color Gris para novedades
            for nov in lista_novedades:
                 m_equipo.append({"n": nov.title(), "h": "--:--", "c": eq_col, "s": "NOVEDAD", "ec": eq_col})
                 # Determinar equipo aproximado para el reporte (opcional)
                 eq_aprox, _ = obtener_equipo(nov)
                 datos_exportacion.append({"Asesor": nov.title(), "Equipo": eq_aprox, "Hora Ingreso": "N/A", "Estado": "NOVEDAD", "Fecha": datetime.today().strftime('%Y-%m-%d')})

        # Dibujar Tarjetas
        if m_equipo:
            st.markdown(f"<h3 style='color:{m_equipo[0]['ec']}; border-bottom: 2px solid {m_equipo[0]['ec']}'>{eq}</h3>", unsafe_allow_html=True)
            cols = st.columns(5)
            for idx, p in enumerate(m_equipo):
                with cols[idx % 5]:
                    st.markdown(f"""
                        <div class="user-card">
                            <div class="time-circle" style="background-color: {p['c']}">
                                <div class="time-val">{p['h']}</div>
                                <div class="status-val">{p['s']}</div>
                            </div>
                            <div class="name-val">{p['n']}</div>
                        </div>
                    """, unsafe_allow_html=True)

    # --- ZONA DE EXPORTACIÓN ---
    st.markdown("---")
    st.subheader("📥 Exportar Reporte Diario para RRHH")
    df_export = pd.DataFrame(datos_exportacion)
    st.dataframe(df_export, use_container_width=True) # Mostrar vista previa
    
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Reporte en Excel (CSV)",
        data=csv,
        file_name=f"Reporte_Asistencia_{datetime.today().strftime('%Y_%m_%d')}.csv",
        mime="text/csv",
    )
else:
    st.info("Carga el archivo del día para generar el reporte.")
