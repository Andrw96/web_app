import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="BarberFlow Admin", layout="wide")

# 2. CONEXIÓN A SUPABASE
URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase: Client = init_connection()

# 3. ESTILOS CSS REPLICANDO LA APP
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main { background-color: #0E1117 !important; }
    .header-text { font-size: 32px; font-weight: 800; color: #FFD700; margin-bottom: 20px; text-transform: uppercase; }
    .metric-card { background-color: #1A1C23; border: 1px solid #2D3139; border-radius: 20px; padding: 20px; min-height: 140px; }
    .metric-val { font-size: 42px; font-weight: 700; color: #FFFFFF; line-height: 1; }
    .metric-lab { font-size: 14px; color: #888888; margin-top: 5px; }
    .section-title { color: #FFD700; font-size: 24px; font-weight: 700; margin: 30px 0 20px 0; }
    .item-card { background-color: #1A1C23; border-radius: 15px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #2D3139; }
    .stButton>button { background-color: #FFD700 !important; color: #000000 !important; font-weight: 700 !important; border-radius: 12px !important; border: none !important; width: 100%; height: 40px; }
    .recaudacion-box { background-color: #1A1C23; padding: 15px; border-radius: 15px; border: 1px solid #2D3139; }
    .text-green { color: #4CAF50; font-weight: 700; font-size: 24px; }
    .text-blue { color: #2196F3; font-weight: 700; font-size: 24px; }
    input { background-color: #1A1C23 !important; color: white !important; border: 1px solid #2D3139 !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. MANEJO DE SESIÓN
if 'auth' not in st.session_state: st.session_state.auth = False
if 'nombre_negocio' not in st.session_state: st.session_state.nombre_negocio = "BARBERÍA"
if 'tab_activa' not in st.session_state: st.session_state.tab_activa = "hoy"

# --- LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #FFD700; margin-top: 50px;'>BarberFlow</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("ENTRAR"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": u, "password": p})
                    st.session_state.user_id = res.user.id
                    
                    # BUSCAR NOMBRE DEL NEGOCIO DINÁMICO
                    try:
                        # Buscamos en la tabla 'Usuarios' el campo 'nombre_negocio'
                        userData = supabase.table("configuracion").select("nombre_negocio").eq("id", res.user.id).single().execute()
                        st.session_state.nombre_negocio = userData.data['nombre_negocio']
                    except:
                        # Si falla, usamos el mail como respaldo
                        st.session_state.nombre_negocio = u.split('@')[0].upper()
                    
                    st.session_state.auth = True
                    st.rerun()
                except: st.error("Credenciales incorrectas")

# --- APP ---
else:
    # Encabezado con Nombre de Negocio dinámico de la DB
    st.markdown(f'<div class="header-text">💈 {st.session_state.nombre_negocio}</div>', unsafe_allow_html=True)
    
    # Carga de datos
    res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = res.data if res.data else []
    ahora = datetime.now().date()
    hoy_iso = ahora.isoformat()
    hace_7_dias = (ahora - timedelta(days=7)).isoformat()

    # Tarjetas Superiores
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

    # Secciones
    if st.session_state.tab_activa == "hoy":
        st.markdown('<div class="section-title">Turnos de Hoy</div>', unsafe_allow_html=True)
        for t in [x for x in data if x['fecha'] == hoy_iso and x['estado'].lower() == "pendiente"]:
            with st.container():
                st.markdown(f'<div class="item-card"><b>{t["nombre"]}</b><br><small>{t["servicio"]}</small></div>', unsafe_allow_html=True)
                col1, col2 = st.columns([2, 1])
                m = col1.number_input("Cobrar $", min_value=0, key=f"m_{t['id']}", label_visibility="collapsed")
                if col2.button("FINALIZAR", key=f"b_{t['id']}"):
                    supabase.table("Turnos").update({"estado": "Completado", "precio": m}).eq("id", t['id']).execute()
                    st.rerun()

    elif st.session_state.tab_activa == "cob":
        st.markdown('<div class="section-title">Recaudación</div>', unsafe_allow_html=True)
        c_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
        c_sem = [t for t in data if hace_7_dias <= t['fecha'] <= hoy_iso and t['estado'].lower() == "completado"]
        
        ca1, ca2 = st.columns(2)
        ca1.markdown(f'<div class="recaudacion-box"><small>HOY</small><br><span class="text-green">$ {sum(int(t.get("precio", 0) or 0) for t in c_hoy)}</span></div>', unsafe_allow_html=True)
        ca2.markdown(f'<div class="recaudacion-box"><small>ESTA SEMANA</small><br><span class="text-blue">$ {sum(int(t.get("precio", 0) or 0) for t in c_sem)}</span></div>', unsafe_allow_html=True)
        
        if st.button("➕ REGISTRAR VENTA RÁPIDA"):
            st.session_state.quick_active = True
        
        if st.session_state.get('quick_active'):
            with st.form("quick_form"):
                n = st.text_input("Nombre del Cliente")
                p = st.number_input("Monto a cobrar $", min_value=0)
                if st.form_submit_button("CONFIRMAR VENTA"):
                    supabase.table("Turnos").insert({"nombre": n, "precio": p, "fecha": hoy_iso, "estado": "Completado", "barber_id": st.session_state.user_id}).execute()
                    st.session_state.quick_active = False
                    st.rerun()

    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.clear())
