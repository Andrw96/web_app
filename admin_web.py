import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="BarberFlow Admin", layout="wide")

# 2. CONEXIÓN A SUPABASE
URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase: Client = init_connection()

# 3. ESTILOS CSS REPLICANDO LA APP DE ESCRITORIO
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main { background-color: #0E1117 !important; }
    
    .header-text { font-size: 32px; font-weight: 800; color: #FFD700; margin-bottom: 20px; }
    
    .metric-card {
        background-color: #1A1C23;
        border: 1px solid #2D3139;
        border-radius: 20px;
        padding: 20px;
        transition: 0.3s;
    }
    .metric-val { font-size: 42px; font-weight: 700; color: #FFFFFF; line-height: 1; }
    .metric-lab { font-size: 14px; color: #888888; margin-top: 5px; }
    
    .section-title { color: #FFD700; font-size: 24px; font-weight: 700; margin: 30px 0 20px 0; }
    
    .item-card {
        background-color: #1A1C23;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #2D3139;
    }
    
    .stButton>button {
        background-color: #FFD700 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100%;
        height: 40px;
    }

    .recaudacion-box {
        background-color: #1A1C23;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #2D3139;
        margin-top: 10px;
    }
    .text-green { color: #4CAF50; font-weight: 700; font-size: 24px; }
    .text-blue { color: #2196F3; font-weight: 700; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

if 'tab_activa' not in st.session_state: st.session_state.tab_activa = "hoy"

# --- HEADER ---
st.markdown('<div class="header-text">💈 ANDRW96</div>', unsafe_allow_html=True)

# --- CARGA DE DATOS ---
res = supabase.table("Turnos").select("*").execute()
data = res.data if res.data else []

ahora = datetime.now().date()
hoy_iso = ahora.isoformat()
hace_7_dias = (ahora - timedelta(days=7)).isoformat()

# Totales para tarjetas
n_hoy = len([t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "pendiente"])
n_agenda = len([t for t in data if t['fecha'] >= hoy_iso and t['estado'].lower() == "pendiente"])
n_cobros = len([t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"])
n_clientes = len(set(t['nombre'] for t in data if t.get('nombre')))

# --- FILA DE TARJETAS ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card">🕒<div class="metric-val">{n_hoy}</div><div class="metric-lab">Hoy</div></div>', unsafe_allow_html=True)
    if st.button("Ver Hoy", key="btn_hoy"): st.session_state.tab_activa = "hoy"
with c2:
    st.markdown(f'<div class="metric-card">📅<div class="metric-val">{n_agenda}</div><div class="metric-lab">Agenda</div></div>', unsafe_allow_html=True)
    if st.button("Ver Agenda", key="btn_age"): st.session_state.tab_activa = "age"
with c3:
    st.markdown(f'<div class="metric-card">💰<div class="metric-val">{n_cobros}</div><div class="metric-lab">Cobros</div></div>', unsafe_allow_html=True)
    if st.button("Ver Cobros", key="btn_cob"): st.session_state.tab_activa = "cob"
with c4:
    st.markdown(f'<div class="metric-card">👥<div class="metric-val">{n_clientes}</div><div class="metric-lab">Clientes</div></div>', unsafe_allow_html=True)
    if st.button("Ver Clientes", key="btn_cli"): st.session_state.tab_activa = "cli"

# --- SECCIONES ---
if st.session_state.tab_activa == "hoy":
    st.markdown('<div class="section-title">Turnos de Hoy</div>', unsafe_allow_html=True)
    for t in [x for x in data if x['fecha'] == hoy_iso and x['estado'].lower() == "pendiente"]:
        st.markdown(f'<div class="item-card"><b>{t["nombre"]}</b><br><small>{t.get("hora", "")} | {t["servicio"]}</small></div>', unsafe_allow_html=True)
        if st.button(f"FINALIZAR {t['nombre']}", key=f"f_{t['id']}"):
            supabase.table("Turnos").update({"estado": "Completado"}).eq("id", t['id']).execute()
            st.rerun()

elif st.session_state.tab_activa == "cob":
    st.markdown('<div class="section-title">Recaudación y Cobros</div>', unsafe_allow_html=True)
    
    # Cálculos de dinero
    cobros_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
    cobros_sem = [t for t in data if hace_7_dias <= t['fecha'] <= hoy_iso and t['estado'].lower() == "completado"]
    
    suma_hoy = sum(int(t.get('precio', 0) or 0) for t in cobros_hoy)
    suma_sem = sum(int(t.get('precio', 0) or 0) for t in cobros_sem)

    # Bloques de Recaudación
    rec1, rec2 = st.columns(2)
    with rec1:
        st.markdown(f'<div class="recaudacion-box"><small>CAJA HOY</small><br><span class="text-green">$ {suma_hoy}</span></div>', unsafe_allow_html=True)
    with rec2:
        st.markdown(f'<div class="recaudacion-box"><small>ESTA SEMANA</small><br><span class="text-blue">$ {suma_sem}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ REGISTRAR VENTA RÁPIDA"): pass

    for t in cobros_hoy:
        st.markdown(f'''
            <div class="item-card">
                <div style="display: flex; justify-content: space-between;">
                    <span><b>{t["nombre"]}</b><br><small>{t["servicio"]}</small></span>
                    <span style="color: #4CAF50; font-weight: 700;">${t.get("precio", 0)}</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)

elif st.session_state.tab_activa == "age":
    st.markdown('<div class="section-title">Próximos Turnos</div>', unsafe_allow_html=True)
    proximos = sorted([t for t in data if t['fecha'] >= hoy_iso and t['estado'].lower() == "pendiente"], key=lambda x: x['fecha'])
    for t in proximos:
        st.markdown(f'<div class="item-card">📅 {t["fecha"]} | {t["hora"]} - <b>{t["nombre"]}</b></div>', unsafe_allow_html=True)

elif st.session_state.tab_activa == "cli":
    st.markdown('<div class="section-title">Fichas de Clientes</div>', unsafe_allow_html=True)
    clientes = sorted(list(set(t['nombre'] for t in data if t.get('nombre'))))
    for c in clientes:
        visitas = len([x for x in data if x['nombre'] == c])
        st.markdown(f'<div class="item-card">👤 <b>{c}</b><br><small>⭐ {visitas} visitas realizadas</small></div>', unsafe_allow_html=True)
