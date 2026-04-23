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

# 3. ESTILOS CSS (Fondo Claro / Letras Negras)
st.markdown("""
    <style>
    /* Fondo claro global */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main { 
        background-color: #F0F2F6 !important; 
    }
    
    /* Sidebar Blanco */
    [data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E0E0E0; 
    }

    /* Forzar texto negro */
    html, body, [data-testid="stWidgetLabel"] p, p, span, li, label { 
        color: #000000 !important; 
    }
    h1, h2, h3 { color: #000000 !important; }

    /* Cabecera del Sidebar */
    .sidebar-header { 
        color: #B8860B !important; 
        font-size: 18px; 
        font-weight: bold; 
        text-align: center; 
        padding: 10px; 
        border: 2px solid #B8860B; 
        border-radius: 8px; 
        margin-bottom: 20px; 
        text-transform: uppercase; 
    }

    /* Inputs y Selects legibles */
    input, select, textarea { 
        color: #000000 !important; 
        background-color: #FFFFFF !important; 
        border: 1px solid #CCCCCC !important; 
        -webkit-text-fill-color: #000000 !important; 
    }

    /* Métricas Doradas */
    [data-testid="stMetricValue"] { 
        color: #B8860B !important; 
        font-size: 35px; 
        font-weight: bold; 
    }

    /* Botones Amarillos / Negros */
    .stButton>button { 
        background-color: #FACC15 !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        border-radius: 10px; 
        border: 1px solid #D4A017; 
        height: 45px; 
        width: 100%; 
    }
    
    /* Tarjetas de Turnos Urbanas */
    .turno-card { 
        background-color: #FFFFFF; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #D1D5DB; 
        margin-bottom: 10px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); 
    }

    /* Formularios */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 15px;
        border: 1px solid #D1D5DB;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #B8860B;'>💈 BARBER ADMIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Usuario (Email)")
        pw = st.text_input("Contraseña", type="password")
        
        if st.button("INGRESAR AL PANEL"):
            # REINTENTO AUTOMÁTICO (Fix para el error del primer intento)
            for intento in range(2):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                    st.session_state.user_id = res.user.id
                    
                    # Intentar traer nombre del local
                    try:
                        conf = supabase.table("Configuracion").select("nombre_negocio").eq("barber_id", res.user.id).single().execute()
                        st.session_state.nombre_local = conf.data['nombre_negocio']
                    except:
                        st.session_state.nombre_local = email.split('@')[0].upper()
                    
                    st.session_state.auth = True
                    st.rerun()
                    break 
                except Exception:
                    if intento == 0:
                        time.sleep(0.6) # Pequeña espera para estabilizar conexión
                        continue
                    else:
                        st.error("Credenciales incorrectas o problema de conexión.")

# --- PANEL PRINCIPAL (AUTENTICADO) ---
else:
    with st.sidebar:
        st.markdown(f'<div class="sidebar-header">💈 {st.session_state.nombre_local}</div>', unsafe_allow_html=True)
        menu = st.radio("GESTIÓN", ["🏠 Dashboard Hoy", "➕ Nueva Venta / Turno", "📅 Agenda Semanal", "💰 Historial de Caja", "👥 Mis Clientes"])
        st.write("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # Carga global de datos desde Supabase
    try:
        data_res = supabase.table("Turnos").select("*").eq("barber_id", st.session_state.user_id).execute()
        data = data_res.data
    except:
        data = []
        
    hoy_dt = datetime.now().date()
    hoy_iso = hoy_dt.isoformat()

    # PESTAÑA: DASHBOARD
    if menu == "🏠 Dashboard Hoy":
        st.title(f"Panel de {st.session_state.nombre_local}")
        pendientes = [t for t in data if str(t['fecha']) == hoy_iso and str(t['estado']).lower() == "pendiente"]
        caja_dia = sum(int(t.get('precio', 0) or 0) for t in data if str(t['fecha']) == hoy_iso and str(t['estado']).lower() == 'completado')
        
        m1, m2 = st.columns(2)
        m1.metric("Turnos Pendientes", len(pendientes))
        m2.metric("Caja Hoy", f"${caja_dia}")
        
        st.subheader("Próximos turnos de hoy")
        if not pendientes:
            st.info("No hay turnos pendientes para hoy.")
        else:
            for t in sorted(pendientes, key=lambda x: x['hora']):
                with st.container():
                    st.markdown(f'<div class="turno-card"><b style="color:#B8860B;">{t["nombre"]}</b><br>🕒 {t["hora"]} - {t["servicio"]}</div>', unsafe_allow_html=True)
                    monto = st.number_input(f"Cobrar a {t['nombre']}", min_value=0, key=f"c_{t['id']}", step=100)
                    if st.button(f"Finalizar Servicio", key=f"b_{t['id']}"):
                        if monto > 0:
                            supabase.table("Turnos").update({"estado": "Completado", "precio": monto}).eq("id", t['id']).execute()
                            st.toast(f"Venta de {t['nombre']} guardada.")
                            st.rerun()

    # PESTAÑA: NUEVA VENTA
    elif menu == "➕ Nueva Venta / Turno":
        st.title("Registrar Nuevo Servicio")
        with st.form("form_nuevo"):
            nom = st.text_input("Nombre del Cliente")
            serv = st.selectbox("Servicio", ["Corte", "Barba", "Combo", "Cejas", "Otro"])
            fec = st.date_input("Fecha", hoy_dt)
            hor = st.time_input("Hora", datetime.now().time())
            pre = st.number_input("Precio ($)", min_value=0, step=100)
            tipo_reg = st.radio("Estado inicial", ["Pendiente (Turno)", "Completado (Venta Directa)"], horizontal=True)
            if st.form_submit_button("GUARDAR EN BASE DE DATOS"):
                est = "Pendiente" if "Pendiente" in tipo_reg else "Completado"
                supabase.table("Turnos").insert({
                    "barber_id": st.session_state.user_id, 
                    "nombre": nom, "servicio": serv, 
                    "fecha": fec.isoformat(), 
                    "hora": hor.strftime("%H:%M"), 
                    "estado": est, "precio": pre
                }).execute()
                st.success("Registro guardado con éxito.")
                st.rerun()

    # PESTAÑA: AGENDA SEMANAL REPARADA
    elif menu == "📅 Agenda Semanal":
        st.title("Cronograma de la Semana")
        turnos_p = [t for t in data if str(t.get('estado', '')).lower() == "pendiente"]
        
        for i in range(7):
            dia_f = hoy_dt + timedelta(days=i)
            dia_iso = dia_f.isoformat()
            st.markdown(f"### 📅 {dia_f.strftime('%A %d/%m')}")
            
            t_del_dia = [t for t in turnos_p if str(t['fecha']) == dia_iso]
            if not t_del_dia:
                st.write("No hay turnos para este día.")
            else:
                for t in sorted(t_del_dia, key=lambda x: x['hora']):
                    st.markdown(f"""
                    <div class="turno-card">
                        <b>{t['hora']} hs</b> — {t['nombre']} <br>
                        <small style="color:#666;">✂️ {t['servicio']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            st.divider()

    # PESTAÑA: HISTORIAL
    elif menu == "💰 Historial de Caja":
        st.title("Historial de Ventas")
        completos = [t for t in data if str(t['estado']).lower() == "completado"]
        total_acum = sum(int(t.get('precio', 0) or 0) for t in completos)
        st.metric("Total Acumulado", f"${total_acum}")
        if completos:
            st.table([{"Fecha": t['fecha'], "Cliente": t['nombre'], "Monto": f"${t['precio']}"} for t in completos[::-1]])
        else:
            st.info("No hay ventas completadas aún.")

    # PESTAÑA: CLIENTES
    elif menu == "👥 Mis Clientes":
        st.title("Mis Clientes")
        # Agrupar clientes por nombre para ver recurrencia
        resumen_cli = {}
        for t in data:
            nombre = t.get('nombre', 'Anónimo')
            if nombre not in resumen_cli: resumen_cli[nombre] = 0
            resumen_cli[nombre] += 1
            
        for cli, visitas in sorted(resumen_cli.items()):
            st.markdown(f'<div class="turno-card"><b>👤 {cli}</b><br>Total de visitas: {visitas}</div>', unsafe_allow_html=True)
