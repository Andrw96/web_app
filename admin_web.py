import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN E INSTANCIA
st.set_page_config(page_title="BarberFlow Admin", layout="wide")

URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase: Client = init_connection()

# 2. ESTILOS CSS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0E1117; }
    .header-text { font-size: 32px; font-weight: 800; color: #FFD700; margin-bottom: 20px; text-transform: uppercase; }
    .metric-card { background-color: #1A1C23; border: 1px solid #2D3139; border-radius: 20px; padding: 20px; text-align: center; }
    .metric-val { font-size: 42px; font-weight: 700; color: #FFFFFF; }
    .metric-lab { font-size: 14px; color: #888888; }
    .section-title { color: #FFD700; font-size: 24px; font-weight: 700; margin: 30px 0 15px 0; }
    .item-card { background-color: #1A1C23; border-radius: 15px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #2D3139; }
    .stButton>button { background-color: #FFD700 !important; color: #000000 !important; font-weight: 700 !important; border-radius: 12px !important; width: 100%; border: none !important; }
    .recaudacion-box { background-color: #1A1C23; padding: 15px; border-radius: 15px; border: 1px solid #2D3139; text-align: center; }
    input { background-color: #1A1C23 !important; color: white !important; border: 1px solid #2D3139 !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. MANEJO DE SESIÓN Y PERSISTENCIA
if "uid" in st.query_params and 'auth' not in st.session_state:
    st.session_state.auth = True
    st.session_state.user_id = st.query_params["uid"]

if 'auth' not in st.session_state: st.session_state.auth = False
if 'nombre_negocio' not in st.session_state: st.session_state.nombre_negocio = "BARBERÍA"
if 'tab_activa' not in st.session_state: st.session_state.tab_activa = "hoy"

# --- LÓGICA DE LOGIN ---
def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            st.session_state.user_id = res.user.id
            st.session_state.auth = True
            st.query_params["uid"] = res.user.id
            conf = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", res.user.id).execute()
            if conf.data:
                st.session_state.nombre_negocio = conf.data[0]['nombre_negocio']
            st.rerun()
    except:
        st.error("Credenciales incorrectas.")

# --- INTERFAZ ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #FFD700; margin-top: 50px;'>BarberFlow</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        e = st.text_input("Correo")
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            login_user(e, p)
else:
    # Recuperar nombre si se refresca la página
    if st.session_state.nombre_negocio == "BARBERÍA":
        try:
            conf = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", st.session_state.user_id).execute()
            if conf.data: st.session_state.nombre_negocio = conf.data[0]['nombre_negocio']
        except: pass

    st.markdown(f'<div class="header-text">💈 {st.session_state.nombre_negocio}</div>', unsafe_allow_html=True)
    
    # Datos
    res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = res.data if res.data else []
    hoy_iso = datetime.now().date().isoformat()
    hace_7_dias = (datetime.now().date() - timedelta(days=7)).isoformat()

    # Dashboard
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len([t for t in data if t["fecha"] == hoy_iso and t["estado"].lower() == "pendiente"])}</div><div class="metric-lab">Hoy</div></div>', unsafe_allow_html=True)
        if st.button("Ver Hoy", key="bh"): st.session_state.tab_activa = "hoy"
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len([t for t in data if t["fecha"] >= hoy_iso and t["estado"].lower() == "pendiente"])}</div><div class="metric-lab">Agenda</div></div>', unsafe_allow_html=True)
        if st.button("Ver Agenda", key="ba"): st.session_state.tab_activa = "age"
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len([t for t in data if t["fecha"] == hoy_iso and t["estado"].lower() == "completado"])}</div><div class="metric-lab">Cobros</div></div>', unsafe_allow_html=True)
        if st.button("Ver Cobros", key="bc"): st.session_state.tab_activa = "cob"
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(set(t["nombre"] for t in data if t.get("nombre")))}</div><div class="metric-lab">Clientes</div></div>', unsafe_allow_html=True)
        if st.button("Ver Clientes", key="bl"): st.session_state.tab_activa = "cli"

    # --- CONTENIDO ---
    if st.session_state.tab_activa == "hoy":
        st.markdown('<div class="section-title">Turnos Pendientes</div>', unsafe_allow_html=True)
        pendientes = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "pendiente"]
        for t in pendientes:
            with st.container():
                st.markdown(f'<div class="item-card"><b>{t["nombre"]}</b> - {t["servicio"]}</div>', unsafe_allow_html=True)
                cm, cb = st.columns([2, 1])
                monto = cm.number_input("Precio $", min_value=0, key=f"p_{t['id']}", label_visibility="collapsed")
                if cb.button("COBRAR", key=f"b_{t['id']}"):
                    supabase.table("Turnos").update({"estado": "Completado", "precio": monto}).eq("id", t['id']).execute()
                    st.rerun()

    elif st.session_state.tab_activa == "age":
        st.markdown('<div class="section-title">Agenda Próxima</div>', unsafe_allow_html=True)
        age = sorted([t for t in data if t['fecha'] >= hoy_iso and t['estado'].lower() == "pendiente"], key=lambda x: x['fecha'])
        for t in age:
            st.markdown(f'<div class="item-card">📅 {t["fecha"]} | {t.get("hora", "00:00")} - <b>{t["nombre"]}</b></div>', unsafe_allow_html=True)

    elif st.session_state.tab_activa == "cob":
        st.markdown('<div class="section-title">Caja y Recaudación</div>', unsafe_allow_html=True)
        c_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
        c_sem = [t for t in data if hace_7_dias <= t['fecha'] <= hoy_iso and t['estado'].lower() == "completado"]
        
        ca1, ca2 = st.columns(2)
        ca1.markdown(f'<div class="recaudacion-box">HOY<br><b style="color:#4CAF50; font-size:24px;">$ {sum(int(t.get("precio", 0) or 0) for t in c_hoy)}</b></div>', unsafe_allow_html=True)
        ca2.markdown(f'<div class="recaudacion-box">SEMANA<br><b style="color:#2196F3; font-size:24px;">$ {sum(int(t.get("precio", 0) or 0) for t in c_sem)}</b></div>', unsafe_allow_html=True)
        
        with st.expander("➕ VENTA RÁPIDA"):
            with st.form("vr"):
                cn = st.text_input("Nombre")
                cs = st.selectbox("Servicio", ["Corte", "Barba", "Combo", "Otros"])
                cp = st.number_input("Precio", min_value=0)
                if st.form_submit_button("REGISTRAR"):
                    supabase.table("Turnos").insert({"nombre": cn, "servicio": cs, "precio": cp, "fecha": hoy_iso, "estado": "Completado", "barber_id": st.session_state.user_id}).execute()
                    st.rerun()

    elif st.session_state.tab_activa == "cli":
        st.markdown('<div class="section-title">Historial de Clientes</div>', unsafe_allow_html=True)
        nombres = sorted(list(set(t['nombre'] for t in data if t.get('nombre'))))
        for n in nombres:
            visitas = len([x for x in data if x['nombre'] == n and x['estado'].lower() == "completado"])
            st.markdown(f'<div class="item-card">👤 <b>{n}</b><br><small>Visitas completadas: {visitas}</small></div>', unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()
