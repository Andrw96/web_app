import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="BarberFlow Admin", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXIÓN A SUPABASE
URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"
supabase = create_client(URL, KEY)

# 3. ESTILOS CSS (Modo Claro / Letras Negras)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main { background-color: #F0F2F6 !important; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E0E0E0; }
    html, body, [data-testid="stWidgetLabel"] p, p, span, li, label { color: #000000 !important; }
    h1, h2, h3 { color: #000000 !important; }
    .sidebar-header { color: #B8860B !important; font-size: 18px; font-weight: bold; text-align: center; padding: 10px; border: 2px solid #B8860B; border-radius: 8px; margin-bottom: 20px; text-transform: uppercase; }
    input, select, textarea { color: #000000 !important; background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; -webkit-text-fill-color: #000000 !important; }
    [data-testid="stMetricValue"] { color: #B8860B !important; font-size: 35px; font-weight: bold; }
    .stButton>button { background-color: #FACC15 !important; color: #000000 !important; font-weight: bold !important; border-radius: 10px; border: 1px solid #D4A017; height: 45px; width: 100%; }
    .turno-card { background-color: #FFFFFF; padding: 15px; border-radius: 12px; border: 1px solid #D1D5DB; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    div[data-testid="stForm"] { background-color: #FFFFFF; border-radius: 15px; border: 1px solid #D1D5DB; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

# Función para manejar el login y evitar el doble clic
def login():
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
        st.session_state.user_id = res.user.id
        try:
            conf_res = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", res.user.id).single().execute()
            st.session_state.nombre_local = conf_res.data['nombre_negocio']
        except:
            st.session_state.nombre_local = email.split('@')[0].upper()
        st.session_state.auth = True
        st.rerun() # Fuerza el reinicio inmediato una vez autenticado
    except Exception as e:
        st.error("Credenciales incorrectas")

# --- INTERFAZ ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #B8860B;'>💈 BARBER ADMIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Usuario (Email)")
            pw = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("INGRESAR AL PANEL")
            if submit:
                login()
else:
    # --- PANEL DE CONTROL (CUANDO YA ESTÁ LOGUEADO) ---
    with st.sidebar:
        st.markdown(f'<div class="sidebar-header">💈 {st.session_state.nombre_local}</div>', unsafe_allow_html=True)
        menu = st.radio("GESTIÓN", ["🏠 Dashboard Hoy", "➕ Nueva Venta / Turno", "📅 Agenda Semanal", "💰 Historial de Caja", "👥 Mis Clientes"])
        st.write("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # Carga de datos
    data_res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = data_res.data
    hoy_dt = datetime.now().date()
    hoy_iso = hoy_dt.isoformat()

    if menu == "🏠 Dashboard Hoy":
        st.title(f"Panel de {st.session_state.nombre_local}")
        pendientes = [t for t in data if str(t['fecha']) == hoy_iso and str(t['estado']).lower() == "pendiente"]
        caja = sum(int(t.get('precio', 0) or 0) for t in data if str(t['fecha']) == hoy_iso and str(t['estado']).lower() == 'completado')
        
        m1, m2 = st.columns(2)
        m1.metric("Turnos Pendientes", len(pendientes))
        m2.metric("Caja Hoy", f"${caja}")
        
        st.subheader("Pendientes de hoy")
        if not pendientes:
            st.info("No hay turnos pendientes para hoy.")
        else:
            for t in sorted(pendientes, key=lambda x: x['hora']):
                with st.container():
                    st.markdown(f'<div class="turno-card"><b style="color:#B8860B;">{t["nombre"]}</b><br>🕒 {t["hora"]} - {t["servicio"]}</div>', unsafe_allow_html=True)
                    monto = st.number_input(f"Cobrar a {t['nombre']}", min_value=0, key=f"c_{t['id']}")
                    if st.button(f"Finalizar {t['nombre']}", key=f"b_{t['id']}"):
                        if monto > 0:
                            supabase.table("Turnos").update({"estado": "Completado", "precio": monto}).eq("id", t['id']).execute()
                            st.rerun()

    elif menu == "➕ Nueva Venta / Turno":
        st.title("Registrar Entrada")
        with st.form("carga"):
            nom = st.text_input("Nombre del Cliente")
            serv = st.selectbox("Servicio", ["Corte", "Barba", "Combo", "Otro"])
            fec = st.date_input("Fecha", hoy_dt)
            hor = st.time_input("Hora", datetime.now().time())
            pre = st.number_input("Precio ($)", min_value=0)
            tipo = st.radio("Estado", ["Pendiente (Turno)", "Completado (Venta Directa)"], horizontal=True)
            if st.form_submit_button("GUARDAR"):
                est = "Pendiente" if "Pendiente" in tipo else "Completado"
                supabase.table("Turnos").insert({"barber_id": st.session_state.user_id, "nombre": nom, "servicio": serv, "fecha": fec.isoformat(), "hora": hor.strftime("%H:%M"), "estado": est, "precio": pre}).execute()
                st.rerun()

    elif menu == "📅 Agenda Semanal":
        st.title("Próximos 7 días")
        turnos_pendientes = [t for t in data if str(t.get('estado', '')).lower() == "pendiente"]
        for i in range(7):
            fecha_dia = hoy_dt + timedelta(days=i)
            fecha_iso = fecha_dia.isoformat()
            st.markdown(f"### 📅 {fecha_dia.strftime('%A %d/%m')}")
            turnos_del_dia = [t for t in turnos_pendientes if str(t['fecha']) == fecha_iso]
            if not turnos_del_dia:
                st.write("No hay turnos.")
            else:
                for t in sorted(turnos_del_dia, key=lambda x: x['hora']):
                    st.markdown(f'<div class="turno-card"><b>{t["hora"]} hs</b> — {t["nombre"]} <br><small>✂️ {t["servicio"]}</small></div>', unsafe_allow_html=True)
            st.divider()

    elif menu == "💰 Historial de Caja":
        st.title("Historial")
        completos = [t for t in data if str(t['estado']).lower() == "completado"]
        if completos:
            st.table([{"Fecha": t['fecha'], "Cliente": t['nombre'], "Monto": f"${t['precio']}"} for t in completos[::-1]])

    elif menu == "👥 Mis Clientes":
        st.title("Directorio")
        nombres_unicos = sorted({t['nombre'] for t in data if t.get('nombre')})
        for cli in nombres_unicos:
            st.markdown(f'<div class="turno-card">👤 {cli}</div>', unsafe_allow_html=True)
