import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="BarberFlow Admin", layout="wide")

URL = "https://vtqfhynmghxbpkrjdpwf.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0cWZoeW5tZ2h4YnBrcmpkcHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5MjQ2ODUsImV4cCI6MjA5MTUwMDY4NX0.OV14rdJs9sA079FUtL1N1pRtC0R2mHpmaoZ719cPn2E"
supabase = create_client(URL, KEY)

# 2. ESTILOS (Inspirado en la captura de pantalla)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 35px; color: #FACC15 !important; }
    .stButton>button { background-color: #FACC15; color: black; font-weight: bold; border-radius: 10px; border: none; }
    .turno-card { background-color: #16171D; padding: 15px; border-radius: 12px; border: 1px solid #2D2D35; margin-bottom: 10px; }
    .sidebar-header { color: #FACC15; font-size: 18px; font-weight: bold; text-align: center; padding: 10px; border: 1px solid #FACC15; border-radius: 8px; margin-bottom: 20px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("💈 LOGIN ADMIN")
    with st.form("login_form"):
        u = st.text_input("Email")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("INGRESAR"):
            try:
                res = supabase.auth.sign_in_with_password({"email": u, "password": p})
                st.session_state.user_id = res.user.id
                
                # --- OBTENER NOMBRE DEL NEGOCIO ---
                try:
                    # Buscamos en la tabla Configuracion la columna nombre_negocio
                    conf_res = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", res.user.id).single().execute()
                    st.session_state.nombre_local = conf_res.data['nombre_negocio']
                except:
                    # Si falla, usamos el email o un nombre por defecto
                    st.session_state.nombre_local = u.split('@')[0].upper()
                
                st.session_state.auth = True
                st.rerun()
            except: st.error("Acceso incorrecto.")
else:
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown(f'<div class="sidebar-header">💈 {st.session_state.nombre_local}</div>', unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "➕ Nueva Venta / Turno", "📅 Agenda Semanal", "💰 Historial de Caja", "👥 Clientes"])
        st.write("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # --- CARGA DE DATOS ---
    data_res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
    data = data_res.data
    hoy_dt = datetime.now().date()
    hoy_iso = hoy_dt.isoformat()

    # --- PESTAÑA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.title(f"Panel de {st.session_state.nombre_local}")
        pendientes_hoy = [t for t in data if str(t['fecha']).strip() == hoy_iso and str(t['estado']).lower() == "pendiente"]
        caja_hoy = sum(int(t.get('precio', 0) or 0) for t in data if t['fecha'] == hoy_iso and t['estado'].lower() == 'completado')

        col1, col2 = st.columns(2)
        col1.metric("Pendientes", len(pendientes_hoy))
        col2.metric("Caja Hoy", f"${caja_hoy}")

        st.subheader("Próximos en espera")
        if not pendientes_hoy:
            st.info("No hay turnos para hoy.")
        else:
            for t in sorted(pendientes_hoy, key=lambda x: x['hora']):
                with st.container():
                    st.markdown(f'<div class="turno-card"><b>{t["nombre"]}</b><br>🕒 {t["hora"]} hs - {t["servicio"]}</div>', unsafe_allow_html=True)
                    if st.button(f"✅ Finalizar y Cobrar", key=f"btn_{t['id']}"):
                        supabase.table("Turnos").update({"estado": "Completado", "precio": 2500}).eq("id", t['id']).execute()
                        st.rerun()

    # --- PESTAÑA: CARGAR VENTA / TURNO ---
    elif menu == "➕ Nueva Venta / Turno":
        st.title("➕ Registrar Venta Directa o Turno")
        with st.form("form_carga", clear_on_submit=True):
            nom = st.text_input("Nombre del Cliente")
            tel = st.text_input("WhatsApp")
            serv = st.selectbox("Servicio", ["Corte", "Barba", "Corte + Barba", "Cejas", "Otro"])
            fec = st.date_input("Fecha", hoy_dt)
            hor = st.time_input("Hora", datetime.now().time())
            pre = st.number_input("Monto ($)", value=2500)
            tipo_reg = st.radio("Tipo de entrada", ["Pendiente (Turno)", "Completado (Venta Directa)"], horizontal=True)
            
            if st.form_submit_button("GUARDAR EN REGISTRO"):
                est = "Pendiente" if "Pendiente" in tipo_reg else "Completado"
                supabase.table("Turnos").insert({
                    "barber_id": st.session_state.user_id, "nombre": nom, "telefono": tel,
                    "servicio": serv, "fecha": fec.isoformat(), "hora": hor.strftime("%H:%M"), 
                    "estado": est, "precio": pre
                }).execute()
                st.success("¡Registro guardado correctamente!")
                st.rerun()

    # --- RESTO DE PESTAÑAS (AGENDA, CAJA, CLIENTES) ---
    elif menu == "📅 Agenda Semanal":
        st.title("Agenda de Turnos")
        pends = [t for t in data if str(t.get('estado','')).lower() == "pendiente"]
        for i in range(7):
            d_ag = hoy_dt + timedelta(days=i)
            st.markdown(f"**{d_ag.strftime('%A %d/%m')}**")
            t_ag = [t for t in pends if t['fecha'] == d_ag.isoformat()]
            if not t_ag: st.caption("Sin turnos")
            for t in t_ag: st.text(f"• {t['hora']}hs: {t['nombre']}")
            st.divider()

    elif menu == "💰 Historial de Caja":
        st.title("Resumen de Cobros")
        completos = [t for t in data if t['estado'].lower() == "completado"]
        st.metric("Total Acumulado", f"${sum(int(t.get('precio', 0) or 0) for t in completos)}")
        st.table([{"Fecha": t['fecha'], "Cliente": t['nombre'], "Precio": t['precio']} for t in completos[::-1]])

    elif menu == "👥 Clientes":
        st.title("Base de Clientes")
        res_cli = {}
        for t in data:
            tel_cli = t.get('telefono', 'S/N')
            if tel_cli not in res_cli: res_cli[tel_cli] = {"nombre": t['nombre'], "servicios": 0}
            res_cli[tel_cli]["servicios"] += 1
        for tel, info in res_cli.items():
            st.write(f"👤 **{info['nombre']}** | 📞 {tel} | ⭐ {info['servicios']} visitas")