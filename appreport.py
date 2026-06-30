import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Dashboard Sauco BPO", layout="wide")

# Contraseña definida
CONTRASEÑA_CORRECTA = "Sauco2026*"
NOMBRE_LOGO = "logo_sauco.jpg"

# --- 2. SISTEMA DE SEGURIDAD (LOGIN) ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

def mostrar_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        if os.path.exists(NOMBRE_LOGO):
            st.image(NOMBRE_LOGO, use_container_width=True)
        
        st.markdown("<h1 style='text-align: center;'>🔒 Acceso Restringido</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-weight: bold;'>Dashboard de uso exclusivo Lideres Negociación y Calidad.</p>", unsafe_allow_html=True)
        
        st.markdown("<div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        pwd_input = st.text_input("Ingresa la contraseña corporativa:", type="password")
        
        if st.button("Ingresar al Sistema", use_container_width=True):
            if pwd_input == CONTRASEÑA_CORRECTA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state["autenticado"]:
    mostrar_login()
    st.stop()


# =====================================================================
# --- ZONA SEGURA (DASHBOARD) ---
# =====================================================================

# --- 3. ESTILOS VISUALES ---
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

# --- LÓGICA DE ASIGNACIÓN DE EQUIPOS ---
def obtener_equipo(nombre):
    n = nombre.lower().strip()
    
    # Se retiró a Maria Marin de esta lista
    if n in ["ludy novoa", "viviana capera", "wendy garcia"]: 
        return "Equipo Proyectos", "#1e40af"
        
    # Corrección: Se agregó a Maria Marin a la lista de Comfandi
    elif n in ["angie hernandez", "ingrid mahecha", "nathalia moreno", "maria marin"]: 
        return "Equipo Davivienda - Comfandi", "#991b1b"
        
    else: 
        return "Equipo Avillas", "#5b21b6"

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

# --- INTERFAZ SUPERIOR ---
col_l, col_t, col_btn = st.columns([1, 3, 1])
with col_l:
    if os.path.exists(NOMBRE_LOGO): st.image(NOMBRE_LOGO, width=150)
with col_t:
    st.title("Dashboard Inicio Jornada")
    st.write("Gestión de Líderes Negociación y Calidad")
with col_btn:
    st.write("") 
    if st.button("🔒 Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

# --- BARRA LATERAL: NOVEDADES ---
st.sidebar.header("📝 Registro de Novedades")
novedades_input = st.sidebar.text_area("Nombres de ausentes (separados por coma):", "")
lista_novedades = [n.strip() for n in novedades_input.split(",") if n.strip()]

# --- PROCESAMIENTO ---
file = st.file_uploader("Cargar reporte diario (.txt)", type=['txt'])

if file:
    df = pd.read_csv(file, sep='\t')
    df['full_name'] = df['full_name'].str.lower().str.strip().replace(REEMPLAZOS)
    df['call_date'] = pd.to_datetime(df['call_date'])
    
    resumen = df.sort_values('call_date').groupby('full_name').first().reset_index()
    datos_exportacion = []
    orden_equipos = ["Equipo Proyectos", "Equipo Davivienda - Comfandi", "Equipo Avillas", "Novedades Reportadas"]
    
    for eq in orden_equipos:
        m_equipo = []
        
        if eq != "Novedades Reportadas":
            for _, r in resumen.iterrows():
                eq_nom, eq_col = obtener_equipo(r['full_name'])
                if eq_nom == eq and r['full_name'].title() not in [n.title() for n in lista_novedades]:
                    c_est, t_est = calcular_puntos(r['full_name'], r['call_date'])
                    hora_str = r['call_date'].strftime('%H:%M')
                    m_equipo.append({"n": r['full_name'].title(), "h": hora_str, "c": c_est, "s": t_est, "ec": eq_col})
                    datos_exportacion.append({"Asesor": r['full_name'].title(), "Equipo": eq, "Hora Ingreso": hora_str, "Estado": t_est, "Fecha": r['call_date'].strftime('%Y-%m-%d')})
        else:
            eq_col = "#64748b" 
            for nov in lista_novedades:
                 m_equipo.append({"n": nov.title(), "h": "--:--", "c": eq_col, "s": "NOVEDAD", "ec": eq_col})
                 eq_aprox, _ = obtener_equipo(nov)
                 datos_exportacion.append({"Asesor": nov.title(), "Equipo": eq_aprox, "Hora Ingreso": "N/A", "Estado": "NOVEDAD", "Fecha": datetime.today().strftime('%Y-%m-%d')})

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

    # --- EXPORTACIÓN ---
    st.markdown("---")
    st.subheader("📥 Reporte Consolidado")
    df_export = pd.DataFrame(datos_exportacion)
    st.dataframe(df_export, use_container_width=True) 
    
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Reporte para Gestión Humana",
        data=csv,
        file_name=f"Reporte_Negociacion_Calidad_{datetime.today().strftime('%Y_%m_%d')}.csv",
        mime="text/csv",
    )
else:
    st.info("Sube el archivo del día para activar el panel visual.")
