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

# 3. ESTILOS CSS - ADN BARBERFLOW
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main { background-color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #0A0A0A !important; border-right: 1px solid #1A1A1A; }
    html, body, p, span, label, .stMarkdown { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Playfair Display', serif !important; }
    
    .metric-card-custom {
        background-color: #141414;
        border: 1px solid #222222;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 5px;
    }
    .metric-value { font-size: 32px; font-weight: 700; color: #FFFFFF; }
    .metric-label { font-size: 11px; color: #888888; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    
    .icon-box { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; font-size: 20px; }
    .orange { background: rgba(255, 152, 0, 0.15); color: #ff9800; }
    .blue { background: rgba(33, 150, 243, 0.15); color: #2196f3; }
    .green { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
    .purple { background: rgba(156, 39, 176, 0.15); color: #9c27b0; }

    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        height: 40px;
        width: 100%;
        margin-bottom: 20px;
    }

    .detalle-container {
        background-color: #0D0D0D;
        border: 1px solid #222222;
        border-radius: 20px;
        padding: 25px;
        margin-top: 10px;
    }
    
    .item-lista {
        padding: 12px;
        border-bottom: 1px solid #1A1A1A;
        display: flex;
        justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

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
            except: st.error("Error de acceso")

# --- PANEL ---
else:
    with st.sidebar:
        st.markdown(f'<h2 style="font-size: 24px;">Menú</h2>', unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "➕ Nueva Venta"])
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # Datos
    res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = res.data if res.data else []
    ahora = datetime.now()
    hoy_iso = ahora.date().isoformat()
    fin_semana = (ahora.date() + timedelta(days=7)).isoformat()

    if menu == "🏠 Dashboard":
        st.title("Panel de Control")

        # Procesamiento para métricas
        pendientes_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "pendiente"]
        completados_hoy = [t for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == "completado"]
        
        # Agenda Semanal (próximos 7 días)
        semanales = [t for t in data if hoy_iso <= t['fecha'] <= fin_semana and t['estado'].lower() == "pendiente"]
        clientes_total = len(set(t['nombre'] for t in data if t.get('nombre')))

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box orange">🕒</div><div class="metric-value">{len(pendientes_hoy)}</div><div class="metric-label">Turnos Hoy</div></div>', unsafe_allow_html=True)
            if st.button("Cobrar Ahora", key="btn_h"): st.session_state.tab_activa = "hoy"
            
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box green">✅</div><div class="metric-value">{len(completados_hoy)}</div><div class="metric-label">Finalizados Hoy</div></div>', unsafe_allow_html=True)
            if st.button("Ver Historial", key="btn_f"): st.session_state.tab_activa = "historial"

        with c2:
            # Reemplazo de Caja por Agenda Semanal
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box blue">📅</div><div class="metric-value">{len(semanales)}</div><div class="metric-label">Agenda Semanal</div></div>', unsafe_allow_html=True)
            if st.button("Ver Calendario", key="btn_s"): st.session_state.tab_activa = "semanal"
            
            st.markdown(f'<div class="metric-card-custom"><div class="icon-box purple">👥</div><div class="metric-value">{clientes_total}</div><div class="metric-label">Mis Clientes</div></div>', unsafe_allow_html=True)
            if st.button("Ver Lista", key="btn_c"): st.session_state.tab_activa = "clientes"

        # --- SECCIÓN DESPLEGABLE ---
        if st.session_state.tab_activa:
            st.markdown("---")
            with st.container():
                st.markdown('<div class="detalle-container">', unsafe_allow_html=True)
                
                if st.session_state.tab_activa == "hoy":
                    st.subheader("🕒 Pendientes de Cobro")
                    for t in pendientes_hoy:
                        col_a, col_b = st.columns([3, 1])
                        col_a.write(f"**{t['nombre']}** ({t['servicio']})")
                        monto = col_b.number_input("$", min_value=0, key=f"v_{t['id']}", label_visibility="collapsed")
                        if st.button(f"Confirmar", key=f"b_{t['id']}"):
                            supabase.table("Turnos").update({"estado": "Completado", "precio": monto}).eq("id", t['id']).execute()
                            st.rerun()

                elif st.session_state.tab_activa == "semanal":
                    st.subheader("📅 Próximos 7 días")
                    for i in range(7):
                        dia = ahora.date() + timedelta(days=i)
                        st.markdown(f"<p style='color:#2196f3; font-weight:bold; margin-top:10px;'>{dia.strftime('%A %d/%m')}</p>", unsafe_allow_html=True)
                        t_dia = [t for t in semanales if t['fecha'] == dia.isoformat()]
                        if not t_dia: st.caption("Sin turnos")
                        for t in t_dia:
                            st.markdown(f'<div class="item-lista"><span>{t["hora"]}hs - {t["nombre"]}</span><span>{t["servicio"]}</span></div>', unsafe_allow_html=True)

                elif st.session_state.tab_activa == "historial":
                    st.subheader("✅ Completados hoy")
                    for t in completados_hoy:
                        st.markdown(f'<div class="item-lista"><span>{t["nombre"]}</span><span style="color:#4caf50;">${t["precio"]}</span></div>', unsafe_allow_html=True)

                elif st.session_state.tab_activa == "clientes":
                    st.subheader("👥 Base de Clientes")
                    nombres = sorted(list(set(t['nombre'] for t in data if t.get('nombre'))))
                    for n in nombres:
                        st.write(f"👤 {n}")

                if st.button("Cerrar ✕"):
                    st.session_state.tab_activa = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ Nueva Venta":
        st.title("Nueva Entrada")
        with st.form("f1"):
            n = st.text_input("Cliente")
            s = st.selectbox("Servicio", ["Corte", "Barba", "Combo"])
            p = st.number_input("Precio", min_value=0)
            if st.form_submit_button("Guardar"):
                supabase.table("Turnos").insert({"barber_id": st.session_state.user_id, "nombre": n, "servicio": s, "fecha": hoy_iso, "hora": ahora.strftime("%H:%M"), "estado": "Completado", "precio": p}).execute()
                st.success("Guardado")
                time.sleep(1)
                st.rerun()
