import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="BarberFlow Admin", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Esto hace la magia
)

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
    [data-testid="stAppViewContainer"], .main { background-color: #0E1117 !important; }
    .header-text { font-size: 32px; font-weight: 800; color: #FFD700; margin-bottom: 20px; text-transform: uppercase; }
    .metric-card { background-color: #1A1C23; border: 1px solid #2D3139; border-radius: 20px; padding: 20px; }
    .metric-val { font-size: 42px; font-weight: 700; color: #FFFFFF; }
    .metric-lab { font-size: 14px; color: #888888; margin-top: 5px; }
    .section-title { color: #FFD700; font-size: 24px; font-weight: 700; margin: 30px 0 20px 0; }
    .item-card { background-color: #1A1C23; border-radius: 15px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #2D3139; }
    .stButton>button { background-color: #FFD700 !important; color: #000000 !important; font-weight: 700 !important; border-radius: 12px !important; border: none !important; width: 100%; height: 40px; }
    input { background-color: #1A1C23 !important; color: white !important; border: 1px solid #2D3139 !important; border-radius: 8px !important; }
    .recaudacion-box { background-color: #1A1C23; padding: 15px; border-radius: 15px; border: 1px solid #2D3139; }
    .text-green { color: #4CAF50; font-weight: 700; font-size: 24px; }
    .text-blue { color: #2196F3; font-weight: 700; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

# 4. PERSISTENCIA DE SESIÓN
if "uid" in st.query_params and 'auth' not in st.session_state:
    st.session_state.auth = True
    st.session_state.user_id = st.query_params["uid"]

if 'auth' not in st.session_state: st.session_state.auth = False
if 'nombre_negocio' not in st.session_state: st.session_state.nombre_negocio = "BARBERÍA"
if 'tab_activa' not in st.session_state: st.session_state.tab_activa = "hoy"

# --- FUNCIÓN DE LOGIN (CORREGIDA) ---
def realizar_login(e, p):
    try:
        res = supabase.auth.sign_in_with_password({"email": e, "password": p})
        if res.user:
            st.session_state.user_id = res.user.id
            st.session_state.auth = True
            st.query_params["uid"] = res.user.id
            conf = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", res.user.id).execute()
            if conf.data:
                st.session_state.nombre_negocio = conf.data[0]['nombre_negocio']
            return True
    except:
        st.error("Credenciales incorrectas.")
    return False

# --- PANTALLA DE INICIO (ESTRUCTURA DE CLIC ÚNICO) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #FFD700; margin-top: 50px;'>BarberFlow</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        email_input = st.text_input("Correo")
        pass_input = st.text_input("Contraseña", type="password")
        if st.button("INICIAR SESIÓN"):
            if realizar_login(email_input, pass_input):
                st.rerun()
    st.stop() # Evita que se dibuje el dashboard si no hay auth

# --- APLICACIÓN COMPLETA (TODA TU LÓGICA ORIGINAL) ---
else:
    if st.session_state.nombre_negocio == "BARBERÍA":
        try:
            conf = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", st.session_state.user_id).execute()
            if conf.data: st.session_state.nombre_negocio = conf.data[0]['nombre_negocio']
        except: pass

    st.markdown(f'<div class="header-text">💈 {st.session_state.nombre_negocio}</div>', unsafe_allow_html=True)
    
    res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = res.data if res.data else []
    ahora = datetime.now().date()
    hoy_iso = ahora.isoformat()
    hace_7_dias = (ahora - timedelta(days=7)).isoformat()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card">🕒<div class="metric-val">{len([t for t in data if t["fecha"] == hoy_iso and t["estado"].lower() == "pendiente"])}</div><div class="metric-lab">Hoy</div></div>', unsafe_allow_html=True)
        if st.button("Ver Hoy", key="h"): st.session_state.tab_activa = "hoy"
    with c2:
        st.markdown(f'<div class="metric-card">📅<div class="metric-val">{len([t for t in data if t["fecha"] >= hoy_iso and t["estado"].lower() == "pendiente"])}</div><div class="metric-lab">Agenda</div></div>', unsafe_allow_html=True)
        if st.button("Ver Agenda", key="a"): st.session_state.tab_activa = "age"
    with c3:
        st.markdown(f'<div class="metric-card">💰<div class="metric-val">{len([t for t in data if t["fecha"] == hoy_iso and t["estado"].lower() == "completado"])}</div><div class="metric-lab">Cobros</div></div>', unsafe_allow_html=True)
        if st.button("Ver Cobros", key="c"): st.session_state.tab_activa = "cob"
    with c4:
        st.markdown(f'<div class="metric-card">👥<div class="metric-val">{len(set(t["nombre"] for t in data if t.get("nombre")))}</div><div class="metric-lab">Clientes</div></div>', unsafe_allow_html=True)
        if st.button("Ver Clientes", key="cl"): st.session_state.tab_activa = "cli"

    if st.session_state.tab_activa == "hoy":
        st.markdown('<div class="section-title">Turnos Pendientes</div>', unsafe_allow_html=True)
        pendientes = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "pendiente"]
        if not pendientes: st.info("No hay turnos pendientes para hoy.")
        for t in pendientes:
            with st.container():
                st.markdown(f'<div class="item-card"><b>{t["nombre"]}</b><br><small>{t["servicio"]}</small></div>', unsafe_allow_html=True)
                col1, col2 = st.columns([2, 1])
                m = col1.number_input("Cobrar $", min_value=0, key=f"m_{t['id']}", label_visibility="collapsed")
                if col2.button("FINALIZAR", key=f"btn_{t['id']}"):
                    supabase.table("Turnos").update({"estado": "Completado", "precio": m}).eq("id", t['id']).execute()
                    st.rerun()

    elif st.session_state.tab_activa == "age":
        st.markdown('<div class="section-title">Próximos Días</div>', unsafe_allow_html=True)
        proximos = sorted([t for t in data if t['fecha'] >= hoy_iso and t['estado'].lower() == "pendiente"], key=lambda x: x['fecha'])
        for t in proximos:
            st.markdown(f'<div class="item-card">📅 {t["fecha"]} | {t.get("hora","--:--")} - <b>{t["nombre"]}</b><br><small>{t["servicio"]}</small></div>', unsafe_allow_html=True)

    elif st.session_state.tab_activa == "cob":
        st.markdown('<div class="section-title">Caja y Recaudación</div>', unsafe_allow_html=True)
        c_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
        c_sem = [t for t in data if hace_7_dias <= t['fecha'] <= hoy_iso and t['estado'].lower() == "completado"]
        ca1, ca2 = st.columns(2)
        ca1.markdown(f'<div class="recaudacion-box"><small>HOY</small><br><span class="text-green">$ {sum(int(t.get("precio", 0) or 0) for t in c_hoy)}</span></div>', unsafe_allow_html=True)
        ca2.markdown(f'<div class="recaudacion-box"><small>SEMANA</small><br><span class="text-blue">$ {sum(int(t.get("precio", 0) or 0) for t in c_sem)}</span></div>', unsafe_allow_html=True)
        with st.expander("➕ REGISTRAR VENTA RÁPIDA"):
            with st.form("quick_sale"):
                n = st.text_input("Cliente")
                s = st.selectbox("Servicio", ["Corte", "Barba", "Combo", "Otro"])
                p = st.number_input("Precio $", min_value=0)
                if st.form_submit_button("GUARDAR VENTA"):
                    supabase.table("Turnos").insert({"nombre": n, "servicio": s, "precio": p, "fecha": hoy_iso, "estado": "Completado", "barber_id": st.session_state.user_id}).execute()
                    st.rerun()
        for t in reversed(c_hoy):
            st.markdown(f'<div class="item-card"><div style="display: flex; justify-content: space-between;"><span><b>{t["nombre"]}</b></span><span style="color: #4CAF50;">$ {t.get("precio", 0)}</span></div></div>', unsafe_allow_html=True)

    elif st.session_state.tab_activa == "cli":
        st.markdown('<div class="section-title">Directorio de Clientes</div>', unsafe_allow_html=True)
        clientes = sorted(list(set(t['nombre'] for t in data if t.get('nombre'))))
        for cl in clientes:
            st.markdown(f'<div class="item-card">👤 {cl}</div>', unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()
