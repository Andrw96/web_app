import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN DE PÁGINA (Estilo Dark)
st.set_page_config(page_title="BarberFlow Admin", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXIÓN A SUPABASE
URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
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

    /* Títulos Elegantes (Playfair Display) */
    h1, h2, h3 { 
        color: #FFFFFF !important; 
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
    }

    /* Inputs Modernos */
    input, select, textarea, [data-testid="stNumberInput"] div div input { 
        color: #FFFFFF !important; 
        background-color: #141414 !important; 
        border: 1px solid #222222 !important;
        border-radius: 12px !important;
    }

    /* Métrica Custom (Cards Estilo Base44) */
    .metric-card-custom {
        background-color: #141414;
        border: 1px solid #222222;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .metric-value { font-size: 32px; font-weight: 700; color: #FFFFFF; }
    .metric-label { font-size: 12px; color: #888888; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Colores de Iconos */
    .icon-box { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 5px; }
    .orange { background: rgba(255, 152, 0, 0.15); color: #ff9800; }
    .blue { background: rgba(33, 150, 243, 0.15); color: #2196f3; }
    .green { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
    .purple { background: rgba(156, 39, 176, 0.15); color: #9c27b0; }

    /* Botón Principal Blanco */
    .stButton>button { 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        font-weight: 700 !important; 
        border-radius: 14px !important; 
        border: none !important; 
        height: 50px; 
        width: 100%;
        transition: transform 0.2s;
    }
    .stButton>button:active { transform: scale(0.96); }

    /* Tarjetas de Turnos */
    .turno-card { 
        background-color: #141414; 
        padding: 18px; 
        border-radius: 18px; 
        border: 1px solid #222222; 
        margin-bottom: 12px; 
    }
    </style>
    """, unsafe_allow_html=True)

# Helper para métricas estilo BarberFlow
def barber_metric(label, value, color_class, icon):
    st.markdown(f"""
        <div class="metric-card-custom">
            <div class="icon-box {color_class}">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>BarberFlow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888;'>Panel de Administración</p>", unsafe_allow_html=True)
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
            except:
                st.error("Credenciales incorrectas")

# --- PANEL ---
else:
    with st.sidebar:
        st.markdown(f'<h2 style="font-size: 24px; padding: 10px 0;">Menu</h2>', unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard Hoy", "➕ Nueva Venta", "📅 Agenda", "💰 Finanzas", "👥 Clientes"])
        st.divider()
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # CARGA DE DATOS
    try:
        data_res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
        data = data_res.data if data_res.data else []
    except:
        data = []

    ahora = datetime.now()
    hoy_iso = ahora.date().isoformat()

    if menu == "🏠 Dashboard Hoy":
        st.markdown(f"<p style='color: #888888; margin:0;'>{ahora.strftime('%A, %d de %B')}</p>", unsafe_allow_html=True)
        st.title("Panel de Control")
        
        pendientes = [t for t in data if str(t.get('fecha')) == hoy_iso and str(t.get('estado', '')).lower() == "pendiente"]
        
        caja_hoy = 0
        for t in data:
            if str(t.get('fecha')) == hoy_iso and str(t.get('estado', '')).lower() == 'completado':
                caja_hoy += int(t.get('precio', 0) or 0)

        # Grid de métricas 2x2
        col1, col2 = st.columns(2)
        with col1:
            barber_metric("Turnos Hoy", len(pendientes), "orange", "🕒")
            barber_metric("Completados", len([t for t in data if str(t.get('fecha')) == hoy_iso and t.get('estado') == 'Completado']), "green", "✅")
        with col2:
            barber_metric("Caja Hoy", f"${caja_hoy}", "blue", "💵")
            barber_metric("Clientes", len(set(t.get('nombre') for t in data)), "purple", "👥")

        st.subheader("Pendientes de cobrar")
        if not pendientes:
            st.caption("No hay turnos pendientes para hoy.")
        for t in pendientes:
            with st.container():
                st.markdown(f'<div class="turno-card"><b>{t["nombre"]}</b><br><span style="color:#888888; font-size:13px;">{t["servicio"]}</span></div>', unsafe_allow_html=True)
                monto = st.number_input(f"Monto final ({t['nombre']})", min_value=0, key=f"p_{t['id']}", label_visibility="collapsed")
                if st.button(f"Confirmar Cobro", key=f"b_{t['id']}"):
                    supabase.table("Turnos").update({"estado": "Completado", "precio": monto}).eq("id", t['id']).execute()
                    st.success("¡Cobro registrado!")
                    time.sleep(0.5)
                    st.rerun()

    elif menu == "➕ Nueva Venta":
        st.title("Registrar Venta")
        with st.form("venta_rapida"):
            nom = st.text_input("Nombre del Cliente")
            serv = st.selectbox("Servicio", ["Corte", "Barba", "Combo", "Otro"])
            pre = st.number_input("Precio ($)", min_value=0)
            if st.form_submit_button("GUARDAR ENTRADA"):
                supabase.table("Turnos").insert({
                    "barber_id": st.session_state.user_id,
                    "nombre": nom, "servicio": serv, "fecha": hoy_iso,
                    "hora": ahora.strftime("%H:%M"), "estado": "Completado", "precio": pre
                }).execute()
                st.success("¡Venta guardada!")
                time.sleep(1)
                st.rerun()

    elif menu == "💰 Finanzas":
        st.title("Historial de Caja")
        ventas = [t for t in data if str(t.get('estado', '')).lower() == "completado"]
        if ventas:
            total = sum(int(v.get('precio', 0) or 0) for v in ventas)
            barber_metric("Recaudación Total", f"${total}", "green", "💰")
            st.markdown("---")
            for v in ventas[::-1]:
                st.markdown(f"""
                <div class="turno-card" style="display:flex; justify-content:space-between; align-items:center;">
                    <div><b>{v['nombre']}</b><br><small style="color:#888888;">{v['fecha']}</small></div>
                    <div style="color:#4caf50; font-weight:700;">+ ${v['precio']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Sin registros.")

    elif menu == "📅 Agenda":
        st.title("Agenda")
        futuros = [t for t in data if str(t.get('estado', '')).lower() == "pendiente"]
        for i in range(7):
            f = ahora.date() + timedelta(days=i)
            st.markdown(f"<h3 style='font-size:18px; color:#ff9800 !important;'>{f.strftime('%A %d/%m')}</h3>", unsafe_allow_html=True)
            t_dia = [t for t in futuros if str(t['fecha']) == f.isoformat()]
            if not t_dia: st.caption("Sin compromisos")
            for t in t_dia:
                st.markdown(f'<div class="turno-card"><b>{t["hora"]}hs</b> - {t["nombre"]}</div>', unsafe_allow_html=True)

    elif menu == "👥 Clientes":
        st.title("Mis Clientes")
        nombres = sorted({t['nombre'] for t in data if t.get('nombre')})
        for n in nombres:
            st.markdown(f'<div class="turno-card">👤 {n}</div>', unsafe_allow_html=True)
