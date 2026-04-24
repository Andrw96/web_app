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
    .stButton>button { background-color: #FFD700 !important; color: #000000 !important; font-weight: 700 !important; border-radius: 12px !important; width: 100%; }
    .recaudacion-box { background-color: #1A1C23; padding: 15px; border-radius: 15px; border: 1px solid #2D3139; text-align: center; }
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
            # Cargar nombre inmediatamente
            conf = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", res.user.id).execute()
            if conf.data:
                st.session_state.nombre_negocio = conf.data[0]['nombre_negocio']
            st.rerun()
    except:
        st.error("Credenciales incorrectas.")

# --- INTERFAZ: LOGIN O APP ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #FFD700; margin-top: 50px;'>BarberFlow</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        e = st.text_input("Correo")
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            login_user(e, p)
else:
    # Asegurar nombre del negocio
    if st.session_state.nombre_negocio == "BARBERÍA":
        try:
            conf = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", st.session_state.user_id).execute()
            if conf.data: st.session_state.nombre_negocio = conf.data[0]['nombre_negocio']
        except: pass

    st.markdown(f'<div class="header-text">💈 {st.session_state.nombre_negocio}</div>', unsafe_allow_html=True)
    
    # 4. CARGA DE DATOS
    res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = res.data if res.data else []
    ahora = datetime.now().date()
    hoy_iso = ahora.isoformat()
    hace_7_dias = (ahora - timedelta(days=7)).isoformat()

    # 5. DASHBOARD
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len([t for t in data if t["fecha"] == hoy_iso and t["estado"].lower() == "pendiente"])}</div><div class="metric-lab">Hoy</div></div>', unsafe_allow_html=True)
        if st.button("Ver Hoy", key="btn_h"): st.session_state.tab_activa = "hoy"
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len([t for t in data if t["fecha"] >= hoy_iso and t["estado"].lower() == "pendiente"])}</div><div class="metric-lab">Agenda</div></div>', unsafe_allow_html=True)
        if st.button("Ver Agenda", key="btn_a"): st.session_state.tab_activa = "age"
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len([t for t in data if t["fecha"] == hoy_iso and t["estado"].lower() == "completado"])}</div><div class="metric-lab">Cobros</div></div>', unsafe_allow_html=True)
        if st.button("Ver Cobros", key="btn_c"): st.session_state.tab_activa = "cob"
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(set(t["nombre"] for t in data if t.get("nombre")))}</div><div class="metric-lab">Clientes</div></div>', unsafe_allow_html=True)
        if st.button("Ver Clientes", key="btn_cl"): st.session_state.tab_activa = "cli"

    # --- PESTAÑAS ---
    if st.session_state.tab_activa == "hoy":
        st.markdown('<div class="section-title">Turnos de Hoy</div>', unsafe_allow_html=True)
        pendientes = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "pendiente"]
        for t in pendientes:
            with st.container():
                st.markdown(f'<div class="item-card"><b>{t["nombre"]}</b> - {t["servicio"]}</div>', unsafe_allow_html=True)
                col_m, col_b = st.columns([2,1])
                m = col_m.number_input("Monto $", min_value=0, key=f"p_{t['id']}", label_visibility="collapsed")
                if col_b.button("COBRAR", key=f"b_{t['id']}"):
                    supabase.table("Turnos").update({"estado": "Completado", "precio": m}).eq("id", t['id']).execute()
                    st.rerun()

    elif st.session_state.tab_activa == "age":
        st.markdown('<div class="section-title">Agenda</div>', unsafe_allow_html=True)
        for t in sorted([x for x in data if x['fecha'] >= hoy_iso and x['estado'].lower() == "pendiente"], key=lambda x: x['fecha']):
            st.markdown(f'<div class="item-card">📅 {t["fecha"]} | <b>{t["nombre"]}</b> ({t["servicio"]})</div>', unsafe_allow_html=True)

    elif st.session_state.tab_activa == "cob":
        st.markdown('<div class="section-title">Caja y Ventas</div>', unsafe_allow_html=True)
        c_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
        c_sem = [t for t in data if hace_7_dias <= t['fecha'] <= hoy_iso and t['estado'].lower() == "completado"]
        
        ca1, ca2 = st.columns(2)
        ca1.markdown(f'<div class="recaudacion-box">HOY<br><b style="color:#4CAF50; font-size:24px;">$ {sum(int(t.get("precio", 0) or 0) for t in c_hoy)}</b></div>', unsafe_allow_html=True)
        ca2.markdown(f'<div class="recaudacion-box">SEMANA<br><b style="color:#2196F3; font-size:24px;">$ {sum(int(t.get("precio", 0) or 0) for t in c_sem)}</b></div>', unsafe_allow_html=True)
        
        with st.expander("➕ VENTA RÁPIDA"):
            with st.form("venta"):
                n = st.text_input("Cliente")
                s = st.selectbox("Servicio", ["Corte", "Barba", "Combo", "Otro"])
                p = st.number_input("Monto $", min_value=0)
                if st.form_submit_button("REGISTRAR"):
                    supabase.table("Turnos").insert({"nombre": n, "servicio": s, "precio": p, "fecha": hoy_iso, "estado": "Completado", "barber_id": st.session_state.user_id}).execute()
                    st.rerun()

    elif st.session_state.tab_activa == "cli":
        st.markdown('<div class="section-title">Mis Clientes</div>', unsafe_allow_html=True)
        for cl in sorted(list(set(t['nombre'] for t in data if t.get('nombre')))):
            st.markdown(f'<div class="item-card">👤 {cl}</div>', unsafe_allow_html=True)

    if st.sidebar.button("Salir"):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()
