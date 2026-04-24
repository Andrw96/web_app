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

# 3. ESTILOS CSS - ADN BARBERFLOW (DARK & INTERACTIVO)
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
    
    /* Textos y Fuentes */
    html, body, [data-testid="stWidgetLabel"] p, p, span, li, label, .stMarkdown { 
        color: #FFFFFF !important; 
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 { 
        color: #FFFFFF !important; 
        font-family: 'Playfair Display', serif !important;
    }

    /* Métrica Estilo PC */
    .metric-card-custom {
        background-color: #141414;
        border: 1px solid #222222;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 5px;
        display: flex;
        flex-direction: column;
    }
    .metric-value { font-size: 32px; font-weight: 700; color: #FFFFFF; }
    .metric-label { font-size: 11px; color: #888888; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    
    .icon-box { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; font-size: 20px; }
    .orange { background: rgba(255, 152, 0, 0.15); color: #ff9800; }
    .blue { background: rgba(33, 150, 243, 0.15); color: #2196f3; }
    .green { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
    .purple { background: rgba(156, 39, 176, 0.15); color: #9c27b0; }

    /* Botones que actúan como pestañas */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        height: 45px;
        width: 100%;
        margin-bottom: 20px;
    }

    /* Contenedor de Detalles (Pestaña abierta) */
    .detalle-container {
        background-color: #0D0D0D;
        border: 1px solid #222222;
        border-radius: 20px;
        padding: 25px;
        margin-top: 10px;
    }
    
    .item-lista {
        padding: 15px;
        border-bottom: 1px solid #1A1A1A;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Inputs Modernos */
    input, [data-testid="stNumberInput"] div div input { 
        background-color: #141414 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. MANEJO DE SESIÓN
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
    with st.sidebar:
        st.markdown(f'<h2 style="font-size: 24px;">Menú</h2>', unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "➕ Nueva Venta", "📅 Agenda"])
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # Carga de Datos
    res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = res.data if res.data else []
    ahora = datetime.now()
    hoy_iso = ahora.date().isoformat()

    if menu == "🏠 Dashboard":
        st.markdown(f"<p style='color: #888888; margin:0;'>{ahora.strftime('%A, %d de %B')}</p>", unsafe_allow_html=True)
        st.title("Panel de Control")

        # Procesar métricas
        pendientes = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "pendiente"]
        completados = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
        caja_hoy = sum(int(t.get('precio', 0) or 0) for t in completados)
        clientes_num = len(set(t['nombre'] for t in data if t.get('nombre')))

        # Grid 2x2
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box orange">🕒</div><div class="metric-value">{len(pendientes)}</div><div class="metric-label">Turnos Hoy</div></div>', unsafe_allow_html=True)
            if st.button("Ver Pendientes", key="btn1"): st.session_state.tab_activa = "pendientes"
            
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box green">✅</div><div class="metric-value">{len(completados)}</div><div class="metric-label">Finalizados</div></div>', unsafe_allow_html=True)
            if st.button("Ver Historial Hoy", key="btn2"): st.session_state.tab_activa = "finalizados"

        with c2:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box blue">💵</div><div class="metric-value">${caja_hoy}</div><div class="metric-label">Caja Hoy</div></div>', unsafe_allow_html=True)
            if st.button("Detalle de Caja", key="btn3"): st.session_state.tab_activa = "caja"
            
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box purple">👥</div><div class="metric-value">{clientes_num}</div><div class="metric-label">Mis Clientes</div></div>', unsafe_allow_html=True)
            if st.button("Lista Clientes", key="btn4"): st.session_state.tab_activa = "clientes"

        # --- SECCIÓN DINÁMICA (Pestañas Abajo) ---
        if st.session_state.tab_activa:
            st.markdown("---")
            with st.container():
                st.markdown('<div class="detalle-container">', unsafe_allow_html=True)
                
                if st.session_state.tab_activa == "pendientes":
                    st.subheader("🕒 Cobros Pendientes")
                    if not pendientes: st.caption("No hay turnos para cobrar.")
                    for t in pendientes:
                        col_a, col_b = st.columns([3, 1])
                        col_a.markdown(f"**{t['nombre']}** - {t['servicio']}")
                        monto = col_b.number_input("$", min_value=0, key=f"v_{t['id']}", label_visibility="collapsed")
                        if st.button(f"Cobrar {t['nombre']}", key=f"cb_{t['id']}"):
                            supabase.table("Turnos").update({"estado": "Completado", "precio": monto}).eq("id", t['id']).execute()
                            st.success("¡Cobro exitoso!")
                            time.sleep(0.5)
                            st.rerun()

                elif st.session_state.tab_activa == "finalizados":
                    st.subheader("✅ Servicios de Hoy")
                    for t in completados:
                        st.markdown(f'<div class="item-lista"><span>{t["nombre"]}</span><span style="color:#4caf50;">+${t["precio"]}</span></div>', unsafe_allow_html=True)

                elif st.session_state.tab_activa == "caja":
                    st.subheader("💰 Resumen Financiero")
                    st.metric("Total Diario", f"${caja_hoy}")
                    st.caption("Basado en servicios completados hoy.")

                elif st.session_state.tab_activa == "clientes":
                    st.subheader("👥 Mis Clientes")
                    nombres = sorted(list(set(t['nombre'] for t in data if t.get('nombre'))))
                    for n in nombres:
                        st.markdown(f'<div class="item-lista">👤 {n}</div>', unsafe_allow_html=True)

                if st.button("Cerrar Detalle ✕"):
                    st.session_state.tab_activa = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ Nueva Venta":
        st.title("Registro Rápido")
        with st.form("venta"):
            nom = st.text_input("Nombre del Cliente")
            serv = st.selectbox("Servicio", ["Corte", "Barba", "Combo", "Otro"])
            pre = st.number_input("Precio ($)", min_value=0)
            if st.form_submit_button("GUARDAR"):
                supabase.table("Turnos").insert({
                    "barber_id": st.session_state.user_id, "nombre": nom, "servicio": serv,
                    "fecha": hoy_iso, "hora": ahora.strftime("%H:%M"), "estado": "Completado", "precio": pre
                }).execute()
                st.success("Venta registrada")
                time.sleep(1)
                st.rerun()

    elif menu == "📅 Agenda":
        st.title("Próximos Turnos")
        futuros = [t for t in data if t['estado'].lower() == "pendiente"]
        for i in range(7):
            f = ahora.date() + timedelta(days=i)
            st.markdown(f"<p style='color:#ff9800; font-weight:bold; margin-top:20px;'>{f.strftime('%A %d/%m')}</p>", unsafe_allow_html=True)
            t_dia = [t for t in futuros if t['fecha'] == f.isoformat()]
            if not t_dia: st.caption("Libre")
            for t in t_dia:
                st.markdown(f'<div class="item-lista" style="background:#141414; border-radius:10px; margin-bottom:5px;"><span>{t["hora"]}hs - {t["nombre"]}</span></div>', unsafe_allow_html=True)
