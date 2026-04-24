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
    
    /* Encabezado */
    .header-text { font-size: 32px; font-weight: 800; color: #FFD700; margin-bottom: 20px; display: flex; align-items: center; }
    
    /* Tarjetas Superiores */
    .metric-card {
        background-color: #1A1C23;
        border: 1px solid #2D3139;
        border-radius: 20px;
        padding: 20px;
        cursor: pointer;
        transition: 0.3s;
    }
    .metric-card:hover { border-color: #FFD700; }
    .metric-val { font-size: 42px; font-weight: 700; color: #FFFFFF; line-height: 1; }
    .metric-lab { font-size: 14px; color: #888888; margin-top: 5px; }
    
    /* Títulos de Sección en Amarillo */
    .section-title { color: #FFD700; font-size: 24px; font-weight: 700; margin: 30px 0 20px 0; }
    
    /* Tarjetas de Lista */
    .item-card {
        background-color: #1A1C23;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #2D3139;
    }
    
    /* Botones Amarillos */
    .stButton>button {
        background-color: #FFD700 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100%;
        height: 45px;
    }
    
    /* Recaudación en Verde */
    .recaudacion-text { color: #4CAF50; font-size: 28px; font-weight: 700; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

if 'tab_activa' not in st.session_state: st.session_state.tab_activa = "hoy"

# --- HEADER ---
st.markdown('<div class="header-text">💈 ANDRW96</div>', unsafe_allow_html=True)

# --- CARGA DE DATOS ---
res = supabase.table("Turnos").select("*").execute()
data = res.data if res.data else []
hoy = datetime.now().date().isoformat()

# Cálculos para los números de las tarjetas
n_hoy = len([t for t in data if t['fecha'] == hoy and t['estado'].lower() == "pendiente"])
n_agenda = len([t for t in data if t['fecha'] >= hoy and t['estado'].lower() == "pendiente"])
n_cobros = len([t for t in data if t['fecha'] == hoy and t['estado'].lower() == "completado"])
n_clientes = len(set(t['nombre'] for t in data if t.get('nombre')))

# --- FILA DE TARJETAS (Interactuables) ---
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

# --- SECCIÓN DINÁMICA INFERIOR ---

if st.session_state.tab_activa == "hoy":
    st.markdown('<div class="section-title">Turnos Pendientes</div>', unsafe_allow_html=True)
    pendientes = [t for t in data if t['fecha'] == hoy and t['estado'].lower() == "pendiente"]
    for t in pendientes:
        with st.container():
            st.markdown(f'<div class="item-card"><b>{t["nombre"]}</b><br><small>🕒 {t.get("hora", "S/H")} | {t["servicio"]}</small></div>', unsafe_allow_html=True)
            col_b1, col_b2 = st.columns([4, 1])
            if col_b1.button(f"FINALIZAR", key=f"fin_{t['id']}"):
                supabase.table("Turnos").update({"estado": "Completado"}).eq("id", t['id']).execute()
                st.rerun()
            col_b2.button("WA", key=f"wa_{t['id']}")

elif st.session_state.tab_activa == "age":
    st.markdown('<div class="section-title">Agenda Semanal</div>', unsafe_allow_html=True)
    # Lógica de agrupación por fecha similar a la captura
    fechas = sorted(list(set(t['fecha'] for t in data if t['fecha'] >= hoy)))
    for f in fechas:
        st.markdown(f"**{f}**")
        for t in [x for x in data if x['fecha'] == f]:
            st.markdown(f'<div class="item-card">• {t.get("hora", "")} - {t["nombre"]}</div>', unsafe_allow_html=True)

elif st.session_state.tab_activa == "cob":
    st.markdown('<div class="section-title">Historial de Cobros</div>', unsafe_allow_html=True)
    st.button("➕ REGISTRAR VENTA RÁPIDA")
    total_recaudado = 0
    cobros = [t for t in data if t['fecha'] == hoy and t['estado'].lower() == "completado"]
    for t in cobros:
        precio = int(t.get('precio', 0) or 0)
        total_recaudado += precio
        st.markdown(f'''
            <div class="item-card">
                <div style="display: flex; justify-content: space-between;">
                    <span><b>{t["nombre"]}</b><br><small>{t["fecha"]} | {t["servicio"]}</small></span>
                    <span style="color: #4CAF50; font-weight: 700;">${precio}</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f'<div style="display: flex; justify-content: space-between;"><span class="section-title">RECAUDACIÓN:</span><span class="recaudacion-text">${total_recaudado}</span></div>', unsafe_allow_html=True)

elif st.session_state.tab_activa == "cli":
    st.markdown('<div class="section-title">Mis Clientes</div>', unsafe_allow_html=True)
    clientes_unicos = sorted(list(set(t['nombre'] for t in data if t.get('nombre'))))
    for c in clientes_unicos:
        visitas = len([x for x in data if x['nombre'] == c])
        st.markdown(f'''
            <div class="item-card">
                👤 <b>{c}</b><br>
                <small>📞 1122334455 | ⭐ {visitas} visitas</small>
            </div>
        ''', unsafe_allow_html=True)
