import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="BarberFlow Admin", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXIÓN A SUPABASE
URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"
supabase = create_client(URL, KEY)

# 3. ESTILOS CSS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main { background-color: #F0F2F6 !important; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E0E0E0; }
    html, body, [data-testid="stWidgetLabel"] p, p, span, li, label { color: #000000 !important; }
    h1, h2, h3 { color: #000000 !important; }
    .sidebar-header { color: #B8860B !important; font-size: 18px; font-weight: bold; text-align: center; padding: 10px; border: 2px solid #B8860B; border-radius: 8px; margin-bottom: 20px; text-transform: uppercase; }
    input, select, textarea { color: #000000 !important; background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; }
    [data-testid="stMetricValue"] { color: #B8860B !important; font-size: 35px; font-weight: bold; }
    .stButton>button { background-color: #FACC15 !important; color: #000000 !important; font-weight: bold !important; border-radius: 10px; border: 1px solid #D4A017; height: 45px; width: 100%; }
    .turno-card { background-color: #FFFFFF; padding: 15px; border-radius: 12px; border: 1px solid #D1D5DB; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #B8860B;'>💈 BARBER ADMIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR AL PANEL"):
            for intento in range(2):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                    st.session_state.user_id = res.user.id
                    st.session_state.auth = True
                    st.rerun()
                    break
                except:
                    if intento == 0: time.sleep(0.6); continue
                    else: st.error("Error de acceso.")

# --- PANEL ---
else:
    with st.sidebar:
        st.markdown(f'<div class="sidebar-header">GESTIÓN BARBERÍA</div>', unsafe_allow_html=True)
        menu = st.radio("MENÚ", ["🏠 Dashboard Hoy", "➕ Registrar Entrada", "📅 Agenda Semanal", "💰 Historial de Caja", "👥 Mis Clientes"])
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # CARGA DE DATOS: Aseguramos que se descarguen todos los turnos del usuario
    try:
        data_res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
        data = data_res.data if data_res.data else []
    except:
        data = []

    ahora = datetime.now()
    hoy_iso = ahora.date().isoformat()

    if menu == "🏠 Dashboard Hoy":
        st.title("Resumen de Hoy")
        # Filtro estricto para caja de hoy
        pendientes = [t for t in data if str(t.get('fecha')) == hoy_iso and str(t.get('estado', '')).lower() == "pendiente"]
        
        # FIX: Convertimos a int y manejamos nulos para que la suma no falle
        caja_hoy = 0
        for t in data:
            if str(t.get('fecha')) == hoy_iso and str(t.get('estado', '')).lower() == 'completado':
                try:
                    caja_hoy += int(t.get('precio', 0) or 0)
                except:
                    pass

        m1, m2 = st.columns(2)
        m1.metric("Pendientes", len(pendientes))
        m2.metric("Caja Hoy", f"${caja_hoy}")

        st.subheader("Pendientes de cobrar")
        for t in pendientes:
            with st.container():
                st.markdown(f'<div class="turno-card"><b>{t["nombre"]}</b> - {t["servicio"]}</div>', unsafe_allow_html=True)
                monto = st.number_input(f"Monto final para {t['nombre']}", min_value=0, key=f"p_{t['id']}")
                if st.button(f"Confirmar Cobro", key=f"b_{t['id']}"):
                    supabase.table("Turnos").update({"estado": "Completado", "precio": monto}).eq("id", t['id']).execute()
                    st.rerun()

    elif menu == "➕ Registrar Entrada":
        st.title("Nueva Venta")
        with st.form("venta_rapida", clear_on_submit=True):
            nom = st.text_input("Nombre")
            serv = st.selectbox("Servicio", ["Corte", "Barba", "Combo", "Otro"])
            pre = st.number_input("Precio ($)", min_value=0)
            if st.form_submit_button("GUARDAR ENTRADA"):
                supabase.table("Turnos").insert({
                    "barber_id": st.session_state.user_id,
                    "nombre": nom,
                    "servicio": serv,
                    "fecha": hoy_iso,
                    "hora": ahora.strftime("%H:%M"),
                    "estado": "Completado",
                    "precio": pre
                }).execute()
                st.success("¡Venta guardada!")
                time.sleep(1)
                st.rerun()

    elif menu == "💰 Historial de Caja":
        st.title("Historial Completo")
        # Filtramos todos los completados de la historia
        ventas = [t for t in data if str(t.get('estado', '')).lower() == "completado"]
        
        if ventas:
            # Calculamos total histórico
            total_historico = sum(int(v.get('precio', 0) or 0) for v in ventas)
            st.subheader(f"Recaudación Total: ${total_historico}")
            
            # Tabla detallada
            st.table([{"Fecha": v['fecha'], "Cliente": v['nombre'], "Monto": f"${v['precio']}"} for v in ventas[::-1]])
        else:
            st.info("No hay ventas registradas todavía.")

    elif menu == "📅 Agenda Semanal":
        st.title("Próximos Turnos")
        futuros = [t for t in data if str(t.get('estado', '')).lower() == "pendiente"]
        for i in range(7):
            f = ahora.date() + timedelta(days=i)
            st.markdown(f"**{f.strftime('%A %d/%m')}**")
            t_dia = [t for t in futuros if str(t['fecha']) == f.isoformat()]
            if not t_dia: st.caption("Sin turnos")
            for t in t_dia:
                st.markdown(f'<div class="turno-card">{t["hora"]} - {t["nombre"]}</div>', unsafe_allow_html=True)

    elif menu == "👥 Mis Clientes":
        st.title("Clientes")
        nombres = sorted({t['nombre'] for t in data if t.get('nombre')})
        for n in nombres:
            st.markdown(f'<div class="turno-card">👤 {n}</div>', unsafe_allow_html=True)
