import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Dashboard Sauco Seguros", layout="wide")

# 🔒 DEFINE TU CONTRASEÑA CORPORATIVA AQUÍ
CONTRASEÑA_CORRECTA = "Sauco2026*"

# --- 2. SISTEMA DE SEGURIDAD (LOGIN) ---
# Verificamos si el usuario ya inició sesión
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

def mostrar_login():
    st.markdown("<br><br><h1 style='text-align: center;'>🔒 Acceso Restringido</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Dashboard de uso exclusivo para supervisión y Talento Humano de Sauco.</p>", unsafe_allow_html=True)
    
    # Centramos el formulario
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        pwd_input = st.text_input("Ingresa la contraseña:", type="password")
        
        if st.button("Ingresar al Dashboard", use_container_width=True):
            if pwd_input == CONTRASEÑA_CORRECTA:
                st.session_state["autenticado"] = True
                st.rerun() # Refresca la página para entrar
            else:
                st.error("❌ Contraseña incorrecta.")
        st.markdown("</div>", unsafe_allow_html=True)

# Si no está autenticado, mostramos el login y DETENEMOS el código aquí.
if not st.session_state["autenticado"]:
    mostrar_login()
    st.stop() # Esta línea es la barrera de seguridad. Nada debajo de ella se ejecuta.


# =====================================================================
# --- A PARTIR DE AQUÍ COMIENZA EL DASHBOARD (ZONA SEGURA) ---
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

# --- INTERFAZ SUPERIOR ---
col_l, col_t, col_btn = st.columns([1, 3, 1])
with col_l:
    if os.path.exists("logo_sauco.jpg"): st.image("logo_sauco.jpg", width=160)
with
