import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="BarberFlow Admin", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXIÓN A SUPABASE
URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase: Client = init_connection()

# 3. ESTILOS CSS - DARK PREMIUM
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main { background-color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #0A0A0A !important; border-right: 1px solid #1A1A1A; }
    html, body, p, span, li, label, .stMarkdown { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Playfair Display', serif !important; }
    
    .metric-card-custom {
        background-color: #141414;
        border: 1px solid #222222;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: -40px; 
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
        font-weight: 600 !important;
        height: 32px !important;
        float: right;
    }
    .stButton>button:hover { border-color: #FFFFFF !important; background-color: rgba(255, 255, 255, 0.1) !important; }

    .detalle-container {
        background-color: #0D0D0D;
        border: 1px solid #222222;
        border-radius: 20px;
        padding: 25px;
        margin-top: 45px;
    }
    .item-lista { padding: 12px; border-bottom: 1px solid #1A1A1A; display: flex; justify-content: space-between; align-items: center; }
    </style>
    """, unsafe_allow_html=True)

# 4. ESTADO DE LA APP
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'tab_activa' not in st.session_state: st.session_state.tab_activa = None

# --- LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>BarberFlow</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        email = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user_id = res.user.id
                st.session_state.auth = True
                st.rerun()
            except Exception as e:
                st.error(f"Error de acceso: {e}")

# --- DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f'<h2 style="font-size: 24px;">Menu</h2>', unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "➕ Nueva Venta"])
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.session_state.user_id = None
            st.rerun()

    # Obtener Datos
    try:
        response = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
        data = response.data
    except Exception as e:
        st.error("Error al conectar con la base de datos.")
        data = []

    ahora = datetime.now()
    hoy_iso = ahora.date().isoformat()
    semana_iso = (ahora.date() + timedelta(days=7)).isoformat()

    if menu == "🏠 Dashboard":
        st.title("Panel de Control")
        
        # Lógica de Métricas
        p_hoy = [t for t in data if t.get('fecha') == hoy_iso and str(t.get('estado')).lower() == "pendiente"]
        f_hoy = [t for t in data if t.get('fecha') == hoy_iso and str(t.get('estado')).lower() == "completado"]
        a_sem = [t for t in data if hoy_iso <= str(t.get('fecha')) <= semana_iso and str(t.get('estado')).lower() == "pendiente"]
        clientes_cnt = len(set(t.get('nombre') for t in data if t.get('nombre')))

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box orange">🕒</div><div class="metric-value">{len(p_hoy)}</div><div class="metric-label">Turnos Hoy</div></div>', unsafe_allow_html=True)
            _, btn_col = st.columns([1, 1]); 
            if btn_col.button("Detalle", key="t1"): st.session_state.tab_activa = "hoy"
            
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box green">✅</div><div class="metric-value">{len(f_hoy)}</div><div class="metric-label">Finalizados Hoy</div></div>', unsafe_allow_html=True)
            _, btn_col = st.columns([1, 1]); 
            if btn_col.button("Historial", key="t2"): st.session_state.tab_activa = "hist"

        with col2:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box blue">📅</div><div class="metric-value">{len(a_sem)}</div><div class="metric-label">Agenda Semanal</div></div>', unsafe_allow_html=True)
            _, btn_col = st.columns([1, 1]); 
            if btn_col.button("Calendario", key="t3"): st.session_state.tab_activa = "sem"

            st.markdown(f'<div class="metric-card-custom"><div class="icon-box purple">👥</div><div class="metric-value">{clientes_cnt}</div><div class="metric-label">Mis Clientes</div></div>', unsafe_allow_html=True)
            _, btn_col = st.columns([1, 1]); 
            if btn_col.button("Ver Lista", key="t4"): st.session_state.tab_activa = "cli"

        # --- SECCIÓN DE PESTAÑAS (ABAJO) ---
        if st.session_state.tab_activa:
            st.markdown("---")
            st.markdown('<div class="detalle-container">', unsafe_allow_html=True)
            
            if st.session_state.tab_activa == "hoy":
                st.subheader("Pendientes de Cobro")
                for t in p_hoy:
                    c_a, c_b = st.columns([3, 1])
                    c_a.write(f"**{t['nombre']}** - {t['servicio']}")
                    m = c_b.number_input("$", min_value=0, key=f"p_{t['id']}", label_visibility="collapsed")
                    if st.button(f"Cobrar", key=f"btn_{t['id']}"):
                        supabase.table("Turnos").update({"estado": "Completado", "precio": m}).eq("id", t['id']).execute()
                        st.rerun()

            elif st.session_state.tab_activa == "sem":
                st.subheader("Próxima Semana")
                for t in a_sem: st.markdown(f'<div class="item-lista"><span>{t["fecha"]} | {t["nombre"]}</span><span>{t["servicio"]}</span></div>', unsafe_allow_html=True)

            elif st.session_state.tab_activa == "cli":
                st.subheader("Clientes")
                for n in sorted(list(set(t['nombre'] for t in data if t.get('nombre')))):
                    st.markdown(f'<div class="item-lista">👤 {n}</div>', unsafe_allow_html=True)

            if st.button("Cerrar ✕"):
                st.session_state.tab_activa = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ Nueva Venta":
        st.title("Nueva Venta")
        with st.form("venta"):
            n = st.text_input("Cliente")
            s = st.selectbox("Servicio", ["Corte", "Barba", "Combo"])
            p = st.number_input("Precio", min_value=0)
            if st.form_submit_button("GUARDAR"):
                supabase.table("Turnos").insert({
                    "barber_id": st.session_state.user_id, "nombre": n, "servicio": s,
                    "fecha": hoy_iso, "hora": ahora.strftime("%H:%M"), "estado": "Completado", "precio": p
                }).execute()
                st.success("Venta registrada")
                st.rerun()
