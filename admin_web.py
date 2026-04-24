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

# 3. ESTILOS CSS - FOCO EN ALINEACIÓN DERECHA
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main { background-color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #0A0A0A !important; border-right: 1px solid #1A1A1A; }
    html, body, p, span, label { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    
    /* Tarjetas */
    .metric-card-custom {
        background-color: #141414;
        border: 1px solid #222222;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: -42px; /* Superposición controlada para integrar el botón */
    }
    .metric-value { font-size: 34px; font-weight: 700; color: #FFFFFF; line-height: 1; }
    .metric-label { font-size: 10px; color: #888888; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }
    
    .icon-box { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; font-size: 18px; }
    .orange { background: rgba(255, 152, 0, 0.1); color: #ff9800; }
    .blue { background: rgba(33, 150, 243, 0.1); color: #2196f3; }
    .green { background: rgba(76, 175, 80, 0.1); color: #4caf50; }
    .purple { background: rgba(156, 39, 176, 0.1); color: #9c27b0; }

    /* BOTÓN ALINEADO A LA DERECHA */
    .stButton>button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #BBBBBB !important;
        border: 1px solid #333333 !important;
        border-radius: 10px !important;
        font-size: 10px !important;
        height: 28px !important;
        width: 100% !important; /* Ocupa el ancho de su columna pequeña */
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #FFFFFF !important;
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    .detalle-container {
        background-color: #0D0D0D;
        border: 1px solid #222222;
        border-radius: 20px;
        padding: 25px;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'tab_activa' not in st.session_state: st.session_state.tab_activa = None

# --- LÓGICA DE LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>BarberFlow</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR"):
            try:
                res = supabase.auth.sign_in_with_password({"email": u, "password": p})
                st.session_state.user_id = res.user.id
                st.session_state.auth = True
                st.rerun()
            except: st.error("Error")

# --- DASHBOARD ---
else:
    # Sidebar
    with st.sidebar:
        menu = st.radio("MENÚ", ["🏠 Dashboard", "➕ Venta Directa"])
        if st.button("Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # Carga de datos
    res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = res.data if res.data else []
    hoy = datetime.now().date().isoformat()
    sem = (datetime.now().date() + timedelta(days=7)).isoformat()

    if menu == "🏠 Dashboard":
        st.title("Panel de Control")
        
        # Filtros
        p_hoy = [t for t in data if t['fecha'] == hoy and t['estado'].lower() == "pendiente"]
        f_hoy = [t for t in data if t['fecha'] == hoy and t['estado'].lower() == "completado"]
        a_sem = [t for t in data if hoy <= t['fecha'] <= sem and t['estado'].lower() == "pendiente"]
        c_tot = len(set(t['nombre'] for t in data if t.get('nombre')))

        # FILA 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box orange">🕒</div><div class="metric-value">{len(p_hoy)}</div><div class="metric-label">Turnos Hoy</div></div>', unsafe_allow_html=True)
            # El truco: 3 columnas, el botón va en la última (derecha)
            _, _, btn_col = st.columns([1, 1, 0.8])
            if btn_col.button("DETALLE", key="k1"): st.session_state.tab_activa = "hoy"
            
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box green">✅</div><div class="metric-value">{len(f_hoy)}</div><div class="metric-label">Finalizados</div></div>', unsafe_allow_html=True)
            _, _, btn_col = st.columns([1, 1, 0.8])
            if btn_col.button("VER", key="k2"): st.session_state.tab_activa = "hist"

        with col2:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box blue">📅</div><div class="metric-value">{len(a_sem)}</div><div class="metric-label">Agenda Semanal</div></div>', unsafe_allow_html=True)
            _, _, btn_col = st.columns([1, 1, 0.8])
            if btn_col.button("CALENDARIO", key="k3"): st.session_state.tab_activa = "sem"

            st.markdown(f'<div class="metric-card-custom"><div class="icon-box purple">👥</div><div class="metric-value">{c_tot}</div><div class="metric-label">Clientes</div></div>', unsafe_allow_html=True)
            _, _, btn_col = st.columns([1, 1, 0.8])
            if btn_col.button("LISTA", key="k4"): st.session_state.tab_activa = "cli"

        # SECCIÓN DESPLEGABLE ABAJO
        if st.session_state.tab_activa:
            st.markdown('<div class="detalle-container">', unsafe_allow_html=True)
            
            if st.session_state.tab_activa == "hoy":
                st.subheader("Turnos de Hoy")
                for t in p_hoy:
                    c_x, c_y = st.columns([4, 1])
                    c_x.write(f"• {t['nombre']} ({t['servicio']})")
                    if c_y.button("Cobrar", key=f"cob_{t['id']}"):
                        supabase.table("Turnos").update({"estado": "Completado"}).eq("id", t['id']).execute()
                        st.rerun()
            
            elif st.session_state.tab_activa == "sem":
                st.subheader("Próximos Turnos")
                for t in a_sem: st.write(f"📅 {t['fecha']} - {t['nombre']}")
            
            elif st.session_state.tab_activa == "cli":
                st.subheader("Mis Clientes")
                for c in sorted(list(set(t['nombre'] for t in data))): st.write(f"👤 {c}")

            if st.button("Cerrar ✕"):
                st.session_state.tab_activa = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ Venta Directa":
        st.title("Nueva Venta")
        with st.form("v"):
            nom = st.text_input("Nombre")
            serv = st.selectbox("Servicio", ["Corte", "Barba", "Combo"])
            if st.form_submit_button("Guardar"):
                supabase.table("Turnos").insert({"barber_id": st.session_state.user_id, "nombre": nom, "servicio": serv, "fecha": hoy, "estado": "Completado"}).execute()
                st.success("Guardado")
                st.rerun()
