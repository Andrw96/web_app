import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="BarberFlow Admin", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXIÓN A SUPABASE
URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase: Client = init_connection()

# 3. ESTILOS CSS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main { background-color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #0A0A0A !important; border-right: 1px solid #1A1A1A; }
    html, body, p, span, label, .stMarkdown { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    .metric-card-custom {
        background-color: #141414;
        border: 1px solid #222222;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: -45px;
    }
    .metric-value { font-size: 32px; font-weight: 700; color: #FFFFFF; }
    .metric-label { font-size: 10px; color: #888888; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    
    .icon-box { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; font-size: 18px; }
    .orange { background: rgba(255, 152, 0, 0.1); color: #ff9800; }
    .blue { background: rgba(33, 150, 243, 0.1); color: #2196f3; }
    .green { background: rgba(76, 175, 80, 0.1); color: #4caf50; }
    .purple { background: rgba(156, 39, 176, 0.1); color: #9c27b0; }

    .stButton>button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        font-size: 11px !important;
        height: 32px !important;
    }
    
    .detalle-container {
        background-color: #0D0D0D;
        border: 1px solid #222222;
        border-radius: 20px;
        padding: 25px;
        margin-top: 50px;
    }

    .recaudacion-box {
        background: linear-gradient(90deg, #141414 0%, #1a1a1a 100%);
        padding: 15px;
        border-radius: 15px;
        border-left: 4px solid #2196f3;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'tab_activa' not in st.session_state: st.session_state.tab_activa = None

# --- AUTH ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>BarberFlow</h1>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1.5, 1])
    with c2:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            try:
                res = supabase.auth.sign_in_with_password({"email": u, "password": p})
                st.session_state.user_id = res.user.id
                st.session_state.auth = True
                st.rerun()
            except: st.error("Error")
else:
    # Carga de Datos
    res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = res.data if res.data else []
    
    hoy_dt = datetime.now().date()
    hoy_iso = hoy_dt.isoformat()
    hace_una_semana = (hoy_dt - timedelta(days=7)).isoformat()
    proxima_semana = (hoy_dt + timedelta(days=7)).isoformat()

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    st.title("Panel de Control")
    
    # Cálculos
    p_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "pendiente"]
    f_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
    
    # Turnos futuros (Agenda)
    a_sem = [t for t in data if hoy_iso <= t['fecha'] <= proxima_semana and t['estado'].lower() == "pendiente"]
    
    # Recaudación de los últimos 7 días (Lo que ya se cobró)
    completados_semana = [t for t in data if hace_una_semana <= t['fecha'] <= hoy_iso and t['estado'].lower() == "completado"]
    total_recaudado_semana = sum(int(t.get('precio', 0) or 0) for t in completados_semana)

    # Métricas principales
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card-custom"><div class="icon-box orange">🕒</div><div class="metric-value">{len(p_hoy)}</div><div class="metric-label">Turnos Hoy</div></div>', unsafe_allow_html=True)
        _, bc = st.columns([1, 1]); 
        if bc.button("Detalle", key="b1"): st.session_state.tab_activa = "hoy"

        st.markdown(f'<div class="metric-card-custom"><div class="icon-box green">✅</div><div class="metric-value">{len(f_hoy)}</div><div class="metric-label">Finalizados Hoy</div></div>', unsafe_allow_html=True)
        _, bc = st.columns([1, 1]); 
        if bc.button("Ver Historial", key="b2"): st.session_state.tab_activa = "hist"

    with col2:
        st.markdown(f'<div class="metric-card-custom"><div class="icon-box blue">📅</div><div class="metric-value">{len(a_sem)}</div><div class="metric-label">Agenda Semanal</div></div>', unsafe_allow_html=True)
        _, bc = st.columns([1, 1]); 
        if bc.button("Ver Agenda/Caja", key="b3"): st.session_state.tab_activa = "sem"

        st.markdown(f'<div class="metric-card-custom"><div class="icon-box purple">👥</div><div class="metric-value">{len(set(t["nombre"] for t in data if t.get("nombre")))}</div><div class="metric-label">Clientes</div></div>', unsafe_allow_html=True)
        _, bc = st.columns([1, 1]); 
        if bc.button("Ver Lista", key="b4"): st.session_state.tab_activa = "cli"

    # --- DESPLEGABLE CON RECAUDACIÓN ---
    if st.session_state.tab_activa:
        st.markdown('<div class="detalle-container">', unsafe_allow_html=True)
        
        if st.session_state.tab_activa == "sem":
            st.subheader("📊 Resumen Semanal")
            
            # Caja de recaudación destacada
            st.markdown(f"""
                <div class="recaudacion-box">
                    <span style="color: #888888; font-size: 12px;">RECAUDACIÓN ÚLTIMOS 7 DÍAS</span><br>
                    <span style="font-size: 24px; font-weight: 700; color: #2196f3;">$ {total_recaudado_semana}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Próximos turnos:**")
            if not a_sem: st.caption("No hay turnos programados.")
            for t in a_sem:
                st.write(f"📅 {t['fecha']} | {t['nombre']} - {t['servicio']}")

        elif st.session_state.tab_activa == "hoy":
            st.subheader("Pendientes de Hoy")
            for t in p_hoy: st.write(f"• {t['nombre']} ({t['servicio']})")

        elif st.session_state.tab_activa == "cli":
            st.subheader("Mis Clientes")
            for n in sorted(list(set(t['nombre'] for t in data if t.get('nombre')))): st.write(f"👤 {n}")

        if st.button("Cerrar ✕"):
            st.session_state.tab_activa = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
