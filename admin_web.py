import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="BarberFlow Admin", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXIÓN A SUPABASE
URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
# Tu clave anon (ya integrada)
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"
supabase = create_client(URL, KEY)

# 3. ESTILOS CSS - ADN BARBERFLOW (DARK & PREMIUM)
st.markdown("""
    <style>
    /* Fondo General */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main { 
        background-color: #000000 !important; 
    }
    
    /* Sidebar Dark */
    [data-testid="stSidebar"] { 
        background-color: #0A0A0A !important; 
        border-right: 1px solid #1A1A1A; 
    }
    
    /* Textos Globales */
    html, body, [data-testid="stWidgetLabel"] p, p, span, li, label, .stMarkdown { 
        color: #FFFFFF !important; 
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 { 
        color: #FFFFFF !important; 
        font-family: 'Playfair Display', serif !important;
    }

    /* Tarjetas de Métricas */
    .metric-card-custom {
        background-color: #141414;
        border: 1px solid #222222;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: -45px; /* Para que el botón parezca estar dentro */
    }
    .metric-value { font-size: 32px; font-weight: 700; color: #FFFFFF; }
    .metric-label { font-size: 10px; color: #888888; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    
    .icon-box { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; font-size: 18px; }
    .orange { background: rgba(255, 152, 0, 0.1); color: #ff9800; }
    .blue { background: rgba(33, 150, 243, 0.1); color: #2196f3; }
    .green { background: rgba(76, 175, 80, 0.1); color: #4caf50; }
    .purple { background: rgba(156, 39, 176, 0.1); color: #9c27b0; }

    /* BOTONES MODERNOS ALINEADOS A LA DERECHA */
    .stButton>button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        height: 32px !important;
        width: auto !important;
        padding: 0 15px !important;
        float: right;
    }
    .stButton>button:hover {
        border-color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Contenedor de Detalles Desplegable */
    .detalle-container {
        background-color: #0D0D0D;
        border: 1px solid #222222;
        border-radius: 20px;
        padding: 25px;
        margin-top: 50px;
    }

    .item-lista {
        padding: 15px;
        border-bottom: 1px solid #1A1A1A;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Inputs de formulario */
    input, [data-testid="stNumberInput"] div div input, select { 
        background-color: #141414 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. MANEJO DE ESTADO
if 'auth' not in st.session_state: st.session_state.auth = False
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
            except: st.error("Acceso incorrecto")

# --- PANEL PRINCIPAL ---
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f'<h2 style="font-size: 24px;">Menu</h2>', unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard Hoy", "➕ Nueva Venta"])
        st.divider()
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # Carga de Datos Real
    try:
        res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
        data = res.data if res.data else []
    except: data = []

    ahora = datetime.now()
    hoy_iso = ahora.date().isoformat()
    semana_limite = (ahora.date() + timedelta(days=7)).isoformat()

    if menu == "🏠 Dashboard Hoy":
        st.title("Panel de Control")
        
        # Procesamiento de métricas
        p_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "pendiente"]
        f_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
        a_sem = [t for t in data if hoy_iso <= t['fecha'] <= semana_limite and t['estado'].lower() == "pendiente"]
        c_total = len(set(t['nombre'] for t in data if t.get('nombre')))

        # Grid de Tarjetas (2 columnas)
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box orange">🕒</div><div class="metric-value">{len(p_hoy)}</div><div class="metric-label">Turnos Hoy</div></div>', unsafe_allow_html=True)
            sc1, sc2 = st.columns([1, 1])
            with sc2: 
                if st.button("Detalle", key="t1"): st.session_state.tab_activa = "hoy"
            
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box green">✅</div><div class="metric-value">{len(f_hoy)}</div><div class="metric-label">Finalizados Hoy</div></div>', unsafe_allow_html=True)
            sc1, sc2 = st.columns([1, 1])
            with sc2:
                if st.button("Historial", key="t2"): st.session_state.tab_activa = "hist"

        with c2:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box blue">📅</div><div class="metric-value">{len(a_sem)}</div><div class="metric-label">Agenda Semanal</div></div>', unsafe_allow_html=True)
            sc1, sc2 = st.columns([1, 1])
            with sc2:
                if st.button("Calendario", key="t3"): st.session_state.tab_activa = "sem"

            st.markdown(f'<div class="metric-card-custom"><div class="icon-box purple">👥</div><div class="metric-value">{c_total}</div><div class="metric-label">Mis Clientes</div></div>', unsafe_allow_html=True)
            sc1, sc2 = st.columns([1, 1])
            with sc2:
                if st.button("Ver Lista", key="t4"): st.session_state.tab_activa = "cli"

        # --- SECCIÓN DINÁMICA (DESPLEGABLE ABAJO) ---
        if st.session_state.tab_activa:
            st.markdown("---")
            with st.container():
                st.markdown('<div class="detalle-container">', unsafe_allow_html=True)
                
                if st.session_state.tab_activa == "hoy":
                    st.subheader("📋 Pendientes de Cobro")
                    if not p_hoy: st.caption("No hay turnos pendientes.")
                    for t in p_hoy:
                        col_a, col_b = st.columns([3, 1])
                        col_a.write(f"**{t['nombre']}** - {t['servicio']}")
                        m = col_b.number_input("$", min_value=0, key=f"p_{t['id']}", label_visibility="collapsed")
                        if st.button(f"Cobrar {t['nombre']}", key=f"btn_{t['id']}"):
                            supabase.table("Turnos").update({"estado": "Completado", "precio": m}).eq("id", t['id']).execute()
                            st.success("Cobrado")
                            time.sleep(0.5)
                            st.rerun()

                elif st.session_state.tab_activa == "sem":
                    st.subheader("📅 Próximos 7 días")
                    for i in range(7):
                        dia = ahora.date() + timedelta(days=i)
                        st.markdown(f"<p style='color:#2196f3; font-weight:bold;'>{dia.strftime('%A %d/%m')}</p>", unsafe_allow_html=True)
                        t_dia = [t for t in a_sem if t['fecha'] == dia.isoformat()]
                        if not t_dia: st.caption("Libre")
                        for t in t_dia: st.markdown(f'<div class="item-lista"><span>{t["hora"]}hs - {t["nombre"]}</span></div>', unsafe_allow_html=True)

                elif st.session_state.tab_activa == "cli":
                    st.subheader("👥 Mis Clientes")
                    for n in sorted(list(set(t['nombre'] for t in data if t.get('nombre')))):
                        st.markdown(f'<div class="
