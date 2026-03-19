import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, date, time as t

# ─── Configuración de la página ───────────────────────────────────────────────
st.set_page_config(
    page_title="🎛️ Streamlit Interactions",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Space Mono', monospace !important;
    }

    /* Header principal */
    .hero {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1040 50%, #0d1f3c 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(120, 80, 255, 0.3);
        box-shadow: 0 0 40px rgba(100, 60, 255, 0.15);
    }
    .hero h1 {
        color: #c0aaff;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -1px;
    }
    .hero p {
        color: #8888aa;
        margin: 0.5rem 0 0 0;
        font-size: 1.05rem;
    }

    /* Tarjetas de sección */
    .section-card {
        background: #12121e;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .section-title {
        font-family: 'Space Mono', monospace;
        color: #7c5cfc;
        font-size: 0.75rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(124, 92, 252, 0.3);
        padding-bottom: 0.5rem;
    }

    /* Badges de resultado */
    .result-badge {
        background: rgba(124, 92, 252, 0.15);
        border: 1px solid rgba(124, 92, 252, 0.4);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        color: #c0aaff;
        display: inline-block;
        margin-top: 0.5rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0d0d1a;
        border-right: 1px solid rgba(120, 80, 255, 0.2);
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #aaaacc !important;
    }

    /* Stmetric overrides */
    [data-testid="stMetricValue"] {
        color: #c0aaff !important;
        font-family: 'Space Mono', monospace !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8888aa !important;
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #0d0d1a;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-size: 0.8rem;
        color: #8888aa;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(124, 92, 252, 0.25) !important;
        color: #c0aaff !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 10px !important;
        background: #12121e !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Navegación")
    seccion = st.radio(
        "Ir a sección:",
        [
            "🏠 Inicio",
            "🔘 Botones & Acciones",
            "📝 Texto & Números",
            "🔀 Selectores",
            "📅 Fecha & Hora",
            "🎚️ Sliders & Rangos",
            "📁 Archivos & Media",
            "📊 Datos & Gráficas",
            "💬 Mensajes & Estado",
            "🏗️ Layout & Estructura",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### ⚙️ Config global")
    tema = st.selectbox("Idioma de ejemplo", ["Español", "English", "Français"])
    modo_debug = st.toggle("Mostrar valores", value=True)

# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎛️ Streamlit · Galería de Interacciones</h1>
    <p>Explora todos los widgets y elementos interactivos que ofrece Streamlit en una sola página.</p>
</div>
""", unsafe_allow_html=True)

# ─── Métricas rápidas ─────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Widgets cubiertos", "30+", "interactivos")
c2.metric("Secciones", "9", "categorías")
c3.metric("Layouts", "5", "opciones")
c4.metric("Versión Streamlit", "≥ 1.30", "compatible")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: BOTONES & ACCIONES
# ══════════════════════════════════════════════════════════════════════════════
if "🔘 Botones & Acciones" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">🔘 Botones & Acciones</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### `st.button`")
        if st.button("Haz clic aquí", use_container_width=True):
            st.success("¡Botón presionado! 🎉")

        st.markdown("#### `st.download_button`")
        csv_data = "nombre,edad\nAna,30\nLuis,25"
        st.download_button("⬇️ Descargar CSV", csv_data, "datos.csv", "text/csv", use_container_width=True)

    with col2:
        st.markdown("#### `st.checkbox`")
        cb = st.checkbox("Acepto los términos")
        if modo_debug:
            st.markdown(f'<div class="result-badge">Valor: {cb}</div>', unsafe_allow_html=True)

        st.markdown("#### `st.toggle`")
        tog = st.toggle("Modo oscuro")
        if modo_debug:
            st.markdown(f'<div class="result-badge">Valor: {tog}</div>', unsafe_allow_html=True)

    with col3:
        st.markdown("#### `st.form` con submit")
        with st.form("mini_form"):
            nombre_form = st.text_input("Nombre")
            submitted = st.form_submit_button("Enviar formulario", use_container_width=True)
            if submitted:
                st.success(f"Hola, {nombre_form or 'anónimo'}! 👋")

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: TEXTO & NÚMEROS
# ══════════════════════════════════════════════════════════════════════════════
if "📝 Texto & Números" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">📝 Texto & Números</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### `st.text_input`")
        texto = st.text_input("Escribe algo", placeholder="Tu texto aquí…")
        if modo_debug and texto:
            st.markdown(f'<div class="result-badge">"{texto}"</div>', unsafe_allow_html=True)

        st.markdown("#### `st.text_area`")
        area = st.text_area("Mensaje largo", placeholder="Escribe varias líneas…", height=100)

        st.markdown("#### `st.number_input`")
        numero = st.number_input("Número", min_value=0, max_value=1000, value=42, step=5)
        if modo_debug:
            st.markdown(f'<div class="result-badge">Valor: {numero}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### `st.chat_input`")
        st.info("El chat input aparece fijo al fondo de la app. Ejemplo ilustrativo:")
        st.code('prompt = st.chat_input("Escribe un mensaje…")', language="python")

        st.markdown("#### `st.code` (display)")
        st.code("""
def saludo(nombre):
    return f"Hola, {nombre}!"

print(saludo("Streamlit"))
        """, language="python")

        st.markdown("#### `st.markdown` y formatos")
        st.markdown("Texto **negrita**, *cursiva*, `código`, [enlace](https://streamlit.io)")
        st.latex(r"E = mc^2 \quad \Rightarrow \quad \Delta E = \Delta m \cdot c^2")

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: SELECTORES
# ══════════════════════════════════════════════════════════════════════════════
if "🔀 Selectores" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">🔀 Selectores</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    opciones = ["Python", "JavaScript", "Rust", "Go", "TypeScript", "Julia"]

    with col1:
        st.markdown("#### `st.selectbox`")
        sel = st.selectbox("Lenguaje favorito", opciones)
        if modo_debug:
            st.markdown(f'<div class="result-badge">{sel}</div>', unsafe_allow_html=True)

        st.markdown("#### `st.radio`")
        rad = st.radio("Experiencia", ["Junior", "Mid", "Senior"], horizontal=True)
        if modo_debug:
            st.markdown(f'<div class="result-badge">{rad}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### `st.multiselect`")
        multi = st.multiselect("Tecnologías", opciones, default=["Python"])
        if modo_debug:
            st.markdown(f'<div class="result-badge">{multi}</div>', unsafe_allow_html=True)

        st.markdown("#### `st.pills` (≥1.35)")
        st.code('st.pills("Tags", ["🐍 Python","⚡ Fast","🔒 Seguro"])', language="python")

    with col3:
        st.markdown("#### `st.color_picker`")
        color = st.color_picker("Elige un color", "#7c5cfc")
        if modo_debug:
            st.markdown(f'<div class="result-badge" style="border-color:{color};color:{color}">{color}</div>', unsafe_allow_html=True)

        st.markdown("#### `st.segmented_control` (≥1.40)")
        st.code('st.segmented_control("Vista", ["Lista","Grid","Tabla"])', language="python")

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: FECHA & HORA
# ══════════════════════════════════════════════════════════════════════════════
if "📅 Fecha & Hora" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">📅 Fecha & Hora</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### `st.date_input`")
        fecha = st.date_input("Selecciona una fecha", value=date.today())
        if modo_debug:
            st.markdown(f'<div class="result-badge">{fecha.strftime("%d / %m / %Y")}</div>', unsafe_allow_html=True)

        st.markdown("#### Rango de fechas")
        rango = st.date_input("Rango", value=(date(2025, 1, 1), date.today()))
        if modo_debug and len(rango) == 2:
            st.markdown(f'<div class="result-badge">{rango[0]} → {rango[1]}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### `st.time_input`")
        hora = st.time_input("Selecciona hora", value=t(9, 0))
        if modo_debug:
            st.markdown(f'<div class="result-badge">{hora.strftime("%H:%M")}</div>', unsafe_allow_html=True)

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: SLIDERS & RANGOS
# ══════════════════════════════════════════════════════════════════════════════
if "🎚️ Sliders & Rangos" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">🎚️ Sliders & Rangos</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### `st.slider` — valor único")
        edad = st.slider("Edad", 0, 100, 25)
        if modo_debug:
            st.markdown(f'<div class="result-badge">Edad: {edad}</div>', unsafe_allow_html=True)

        st.markdown("#### `st.slider` — rango")
        rango_num = st.slider("Rango de precio (MXN)", 0, 10000, (1000, 5000), step=100)
        if modo_debug:
            st.markdown(f'<div class="result-badge">${rango_num[0]:,} — ${rango_num[1]:,}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### `st.slider` — flotante")
        confianza = st.slider("Nivel de confianza", 0.0, 1.0, 0.85, 0.01)
        st.progress(confianza)
        if modo_debug:
            st.markdown(f'<div class="result-badge">{confianza:.0%}</div>', unsafe_allow_html=True)

        st.markdown("#### `st.select_slider`")
        talla = st.select_slider("Talla", options=["XS", "S", "M", "L", "XL", "XXL"], value="M")
        if modo_debug:
            st.markdown(f'<div class="result-badge">{talla}</div>', unsafe_allow_html=True)

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: ARCHIVOS & MEDIA
# ══════════════════════════════════════════════════════════════════════════════
if "📁 Archivos & Media" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">📁 Archivos & Media</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### `st.file_uploader` — imagen")
        img = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg", "webp"])
        if img:
            st.image(img, caption="Imagen subida", use_container_width=True)

    with col2:
        st.markdown("#### `st.file_uploader` — CSV")
        csv_file = st.file_uploader("Sube un CSV", type=["csv"])
        if csv_file:
            df_up = pd.read_csv(csv_file)
            st.dataframe(df_up.head(5), use_container_width=True)
        else:
            st.info("Sube un CSV para ver una vista previa")

        st.markdown("#### `st.camera_input`")
        st.code("foto = st.camera_input('Toma una foto')", language="python")
        st.caption("Activa la cámara del dispositivo")

        st.markdown("#### `st.audio` / `st.video`")
        st.code("st.audio('audio.mp3')\nst.video('video.mp4')", language="python")

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: DATOS & GRÁFICAS
# ══════════════════════════════════════════════════════════════════════════════
if "📊 Datos & Gráficas" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">📊 Datos & Gráficas</div>', unsafe_allow_html=True)

    # Generar datos
    np.random.seed(42)
    df = pd.DataFrame({
        "Mes": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"],
        "Ventas": np.random.randint(5000, 15000, 12),
        "Gastos": np.random.randint(3000, 10000, 12),
        "Clientes": np.random.randint(100, 500, 12),
    })

    tab1, tab2, tab3 = st.tabs(["📋 Tabla", "📈 Líneas", "📊 Barras"])

    with tab1:
        st.markdown("#### `st.dataframe` y `st.data_editor`")
        col_a, col_b = st.columns(2)
        with col_a:
            st.caption("st.dataframe — sólo lectura")
            st.dataframe(df, use_container_width=True, height=260)
        with col_b:
            st.caption("st.data_editor — editable")
            df_edit = st.data_editor(df.head(5), use_container_width=True)

    with tab2:
        st.markdown("#### `st.line_chart`")
        st.line_chart(df.set_index("Mes")[["Ventas", "Gastos"]], use_container_width=True)

    with tab3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### `st.bar_chart`")
            st.bar_chart(df.set_index("Mes")["Clientes"], use_container_width=True)
        with col_b:
            st.markdown("#### `st.area_chart`")
            st.area_chart(df.set_index("Mes")[["Ventas", "Gastos"]], use_container_width=True)

    st.markdown("#### `st.map` — datos geográficos")
    mapa_df = pd.DataFrame({
        "lat": [20.97, 19.43, 25.68, 20.52],
        "lon": [-89.62, -99.13, -100.32, -87.31],
    })
    st.map(mapa_df, zoom=4)

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: MENSAJES & ESTADO
# ══════════════════════════════════════════════════════════════════════════════
if "💬 Mensajes & Estado" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">💬 Mensajes & Estado</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.success("✅ Operación exitosa — `st.success`")
        st.info("ℹ️ Información importante — `st.info`")
        st.warning("⚠️ Atención requerida — `st.warning`")
        st.error("❌ Ocurrió un error — `st.error`")
        st.exception(ValueError("Ejemplo de excepción"))

    with col2:
        st.markdown("#### `st.toast`")
        if st.button("Mostrar toast 🍞"):
            st.toast("¡Mensaje breve! 🎉", icon="✅")

        st.markdown("#### `st.progress` y `st.spinner`")
        if st.button("Simular carga ⏳"):
            barra = st.progress(0, text="Procesando…")
            for i in range(101):
                time.sleep(0.015)
                barra.progress(i, text=f"Procesando… {i}%")
            st.success("¡Completado!")

        st.markdown("#### `st.status`")
        with st.status("Ejecutando tarea…", expanded=False):
            st.write("Paso 1: Inicializando")
            st.write("Paso 2: Calculando")
            st.write("Paso 3: Finalizando")

        st.markdown("#### `st.balloons` / `st.snow`")
        c_a, c_b = st.columns(2)
        if c_a.button("🎈 Globos"):
            st.balloons()
        if c_b.button("❄️ Nieve"):
            st.snow()

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN: LAYOUT & ESTRUCTURA
# ══════════════════════════════════════════════════════════════════════════════
if "🏗️ Layout & Estructura" in seccion or "🏠 Inicio" in seccion:
    st.markdown('<div class="section-title">🏗️ Layout & Estructura</div>', unsafe_allow_html=True)

    st.markdown("#### `st.columns` — divisiones flexibles")
    cols = st.columns([2, 1, 1])
    cols[0].metric("Principal (2/4)", "70%", "+5%")
    cols[1].metric("Secundario (1/4)", "20%")
    cols[2].metric("Tercero (1/4)", "10%", "-2%")

    st.markdown("#### `st.expander`")
    with st.expander("📖 Ver detalles técnicos"):
        st.markdown("""
        - `st.columns(spec)` — divide la fila en columnas con proporciones personalizadas.
        - `st.tabs(labels)` — crea pestañas navegables.
        - `st.expander(label)` — sección plegable.
        - `st.sidebar` — panel lateral persistente.
        - `st.container()` — agrupa widgets con lógica.
        - `st.empty()` — placeholder dinámico que se puede sobreescribir.
        """)

    st.markdown("#### `st.container` y `st.empty`")
    contenedor = st.container(border=True)
    contenedor.markdown("Soy un **contenedor** con borde `border=True`")
    contenedor.caption("Los containers agrupan widgets visualmente.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### `st.popover` (≥1.31)")
        with st.popover("Abrir popover 🎯"):
            st.markdown("Contenido flotante dentro del popover")
            st.slider("Ajuste rápido", 0, 100, 50)

    with col2:
        st.markdown("#### `st.dialog` (≥1.37)")
        st.code("""
@st.dialog("Confirmar acción")
def confirmar():
    st.write("¿Estás seguro?")
    if st.button("Sí"):
        st.rerun()
        """, language="python")

    st.divider()

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem; color: #555577; font-family: 'Space Mono', monospace; font-size: 0.8rem;">
    Streamlit Interaction Gallery • Generado con ❤️ y Python
    <br><a href="https://docs.streamlit.io" style="color:#7c5cfc;">docs.streamlit.io</a>
</div>
""", unsafe_allow_html=True)
