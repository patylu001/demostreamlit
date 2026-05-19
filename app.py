import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────────────────────────────
#  CONFIGURACIÓN DEL SISTEMA
# ─────────────────────────────────────────────
ARCHIVEROS = 5        # Número de archiveros
FILAS = 7             # Filas por archivero
SECCIONES = list("ABCDEFG")  # Secciones por fila
DATA_FILE = "archivos_datos.json"

# ─────────────────────────────────────────────
#  CARGA / GUARDADO DE DATOS
# ─────────────────────────────────────────────

def cargar_datos():
    """Carga los datos desde el archivo JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_datos(datos):
    """Guarda los datos en el archivo JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def datos_a_dataframe(datos):
    """Convierte el diccionario de datos a un DataFrame de pandas."""
    if not datos:
        return pd.DataFrame(columns=["Nombre", "Archivero", "Fila", "Sección", "Descripción", "Fecha Registro"])
    rows = []
    for nombre, info in datos.items():
        rows.append({
            "Nombre": nombre,
            "Archivero": info.get("archivero", ""),
            "Fila": info.get("fila", ""),
            "Sección": info.get("seccion", ""),
            "Descripción": info.get("descripcion", ""),
            "Fecha Registro": info.get("fecha", ""),
        })
    return pd.DataFrame(rows)

def ubicacion_key(archivero, fila, seccion):
    return f"A{archivero}-F{fila}-{seccion}"

# ─────────────────────────────────────────────
#  MAPA VISUAL DE UN ARCHIVERO
# ─────────────────────────────────────────────

def crear_mapa_archivero(datos, archivero_sel, archivo_buscado=None):
    """Genera un mapa visual (Plotly) de un archivero con sus celdas."""
    # Construir matriz de ocupación y etiquetas
    z = []       # valor para colorear
    text = []    # texto en cada celda
    hover = []   # hover text

    for fila in range(1, FILAS + 1):
        z_row, text_row, hover_row = [], [], []
        for sec in SECCIONES:
            # Buscar archivos en esta celda
            archivos_aqui = [
                nombre for nombre, info in datos.items()
                if info.get("archivero") == archivero_sel
                and info.get("fila") == fila
                and info.get("seccion") == sec
            ]
            if archivos_aqui:
                if archivo_buscado and archivo_buscado in archivos_aqui:
                    z_row.append(3)       # Resaltado (resultado de búsqueda)
                else:
                    z_row.append(2)       # Ocupado
                label = f"<b>{len(archivos_aqui)}</b><br>archivo(s)"
                hover_text = "<br>".join(archivos_aqui)
            else:
                z_row.append(1)           # Vacío
                label = "—"
                hover_text = "Vacío"

            text_row.append(label)
            hover_row.append(
                f"<b>Archivero {archivero_sel} | Fila {fila} | Sec. {sec}</b><br>{hover_text}"
            )
        z.append(z_row)
        text.append(text_row)
        hover.append(hover_row)

    colorscale = [
        [0.0,  "#1e2030"],   # fondo (no usado)
        [0.33, "#243447"],   # vacío (1)
        [0.66, "#1a6b5a"],   # ocupado (2)
        [1.0,  "#f59e0b"],   # resaltado (3)
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z,
        text=text,
        hovertext=hover,
        hovertemplate="%{hovertext}<extra></extra>",
        texttemplate="%{text}",
        colorscale=colorscale,
        zmin=1, zmax=3,
        showscale=False,
        xgap=4,
        ygap=4,
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>Archivero {archivero_sel}</b>",
            font=dict(size=20, color="#e2e8f0"),
            x=0.5,
        ),
        xaxis=dict(
            tickvals=list(range(len(SECCIONES))),
            ticktext=[f"Sec. {s}" for s in SECCIONES],
            tickfont=dict(color="#94a3b8", size=13),
            showgrid=False,
            side="top",
        ),
        yaxis=dict(
            tickvals=list(range(FILAS)),
            ticktext=[f"Fila {f}" for f in range(1, FILAS + 1)],
            tickfont=dict(color="#94a3b8", size=13),
            showgrid=False,
            autorange="reversed",
        ),
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        margin=dict(l=80, r=20, t=80, b=20),
        height=380,
    )
    return fig


# ─────────────────────────────────────────────
#  VISTA GLOBAL — TODOS LOS ARCHIVEROS
# ─────────────────────────────────────────────

def crear_vista_global(datos):
    """Genera un mapa consolidado de ocupación de todos los archiveros."""
    # Contar archivos por archivero
    conteo = {a: 0 for a in range(1, ARCHIVEROS + 1)}
    for info in datos.values():
        a = info.get("archivero")
        if a in conteo:
            conteo[a] += 1

    capacidad_total = FILAS * len(SECCIONES)  # 49 slots por archivero

    archiveros_lista = list(range(1, ARCHIVEROS + 1))
    ocupados = [conteo[a] for a in archiveros_lista]
    libres = [capacidad_total - c for a, c in zip(archiveros_lista, ocupados)]
    pct = [round(c / capacidad_total * 100, 1) for c in ocupados]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Archivos registrados",
        x=[f"Archivero {a}" for a in archiveros_lista],
        y=ocupados,
        marker_color="#3b82f6",
        text=[f"{p}%" for p in pct],
        textposition="outside",
        textfont=dict(color="#e2e8f0"),
    ))
    fig.add_trace(go.Bar(
        name="Espacios libres",
        x=[f"Archivero {a}" for a in archiveros_lista],
        y=libres,
        marker_color="#243447",
    ))

    fig.update_layout(
        barmode="stack",
        title=dict(
            text="<b>Ocupación global de archiveros</b>",
            font=dict(size=18, color="#e2e8f0"),
            x=0.5,
        ),
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font=dict(color="#94a3b8"),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(color="#e2e8f0"),
        ),
        yaxis=dict(
            title="Cantidad de archivos",
            gridcolor="#1e2030",
        ),
        xaxis=dict(gridcolor="#1e2030"),
        margin=dict(l=60, r=20, t=80, b=40),
        height=350,
    )
    return fig


# ─────────────────────────────────────────────
#  CONFIGURACIÓN DE LA PÁGINA
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Localizador de Archivos",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown("""
<style>
    /* Fondo principal */
    .stApp { background-color: #0f1117; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #141824;
        border-right: 1px solid #1e2a3a;
    }

    /* Título principal */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .main-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Tarjetas de métricas */
    .metric-card {
        background: linear-gradient(145deg, #141824, #1a2035);
        border: 1px solid #1e2a3a;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #3b82f6;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Resultado de búsqueda */
    .result-card {
        background: linear-gradient(145deg, #1a2035, #162032);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 12px 0;
    }
    .result-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 8px;
    }
    .result-location {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f59e0b;
    }
    .coord-badge {
        display: inline-block;
        background: #1e3a5f;
        color: #93c5fd;
        border-radius: 8px;
        padding: 4px 12px;
        margin: 4px 4px 0 0;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Botones */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Divisor */
    hr { border-color: #1e2a3a; }

    /* Inputs */
    .stSelectbox>div>div, .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #141824 !important;
        border-color: #1e2a3a !important;
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ENCABEZADO
# ─────────────────────────────────────────────

st.markdown('<div class="main-title">🗂️ Localizador de Archivos Físicos</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Sistema de mapeo visual · 5 Archiveros · 7 Filas · Secciones A–G</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CARGAR DATOS
# ─────────────────────────────────────────────

if "datos" not in st.session_state:
    st.session_state.datos = cargar_datos()

datos = st.session_state.datos

# ─────────────────────────────────────────────
#  MÉTRICAS RÁPIDAS
# ─────────────────────────────────────────────

total_archivos = len(datos)
total_slots = ARCHIVEROS * FILAS * len(SECCIONES)
ocupacion_pct = round(total_archivos / total_slots * 100, 1) if total_slots > 0 else 0
archivero_mas_lleno = max(
    range(1, ARCHIVEROS + 1),
    key=lambda a: sum(1 for info in datos.values() if info.get("archivero") == a)
) if datos else "—"

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_archivos}</div>
        <div class="metric-label">Archivos registrados</div>
    </div>""", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_slots - total_archivos}</div>
        <div class="metric-label">Espacios disponibles</div>
    </div>""", unsafe_allow_html=True)
with col_m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{ocupacion_pct}%</div>
        <div class="metric-label">Ocupación total</div>
    </div>""", unsafe_allow_html=True)
with col_m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">#{archivero_mas_lleno}</div>
        <div class="metric-label">Archivero más lleno</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔍 Buscar Archivo")
    busqueda = st.text_input(
        "Nombre del archivo",
        placeholder="Ej: Contrato-2024-001",
        key="busqueda_input",
    )

    st.markdown("---")
    st.markdown("## ✏️ Registrar / Editar Archivo")

    with st.form("form_registro", clear_on_submit=True):
        nombre_archivo = st.text_input("Nombre del archivo *", placeholder="Ej: Factura-001")
        descripcion = st.text_area("Descripción", placeholder="Notas adicionales...", height=80)

        col_a, col_f = st.columns(2)
        with col_a:
            archivero_form = st.selectbox("Archivero", range(1, ARCHIVEROS + 1), key="arch_form")
        with col_f:
            fila_form = st.selectbox("Fila", range(1, FILAS + 1), key="fila_form")
        seccion_form = st.selectbox("Sección", SECCIONES, key="sec_form")

        submitted = st.form_submit_button("💾 Guardar", use_container_width=True, type="primary")
        if submitted:
            if not nombre_archivo.strip():
                st.error("⚠️ El nombre no puede estar vacío.")
            else:
                datos[nombre_archivo.strip()] = {
                    "archivero": archivero_form,
                    "fila": fila_form,
                    "seccion": seccion_form,
                    "descripcion": descripcion.strip(),
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                st.session_state.datos = datos
                guardar_datos(datos)
                st.success(f"✅ '{nombre_archivo}' guardado en A{archivero_form}-F{fila_form}-{seccion_form}")
                st.rerun()

    st.markdown("---")
    st.markdown("## 🗑️ Eliminar Archivo")
    if datos:
        archivo_eliminar = st.selectbox(
            "Selecciona archivo a eliminar",
            options=["— Seleccionar —"] + sorted(datos.keys()),
            key="eliminar_sel"
        )
        if archivo_eliminar != "— Seleccionar —":
            if st.button("🗑️ Eliminar", use_container_width=True, type="secondary"):
                del datos[archivo_eliminar]
                st.session_state.datos = datos
                guardar_datos(datos)
                st.success(f"Eliminado: {archivo_eliminar}")
                st.rerun()
    else:
        st.info("No hay archivos registrados.")

# ─────────────────────────────────────────────
#  RESULTADO DE BÚSQUEDA
# ─────────────────────────────────────────────

archivo_encontrado = None
if busqueda.strip():
    coincidencias = {
        nombre: info for nombre, info in datos.items()
        if busqueda.strip().lower() in nombre.lower()
    }
    if coincidencias:
        st.markdown("### 🎯 Resultado de búsqueda")
        for nombre, info in coincidencias.items():
            archivo_encontrado = nombre
            st.markdown(f"""
            <div class="result-card">
                <div class="result-title">📄 {nombre}</div>
                <div class="result-location">
                    Archivero {info['archivero']} · Fila {info['fila']} · Sección {info['seccion']}
                </div>
                <br>
                <span class="coord-badge">🗄️ Archivero {info['archivero']}</span>
                <span class="coord-badge">📏 Fila {info['fila']}</span>
                <span class="coord-badge">🔤 Sección {info['seccion']}</span>
                {"<br><small style='color:#64748b;margin-top:8px;display:block;'>📝 " + info['descripcion'] + "</small>" if info.get('descripcion') else ""}
                <small style='color:#475569;margin-top:6px;display:block;'>🕐 Registrado: {info.get('fecha','—')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning(f"No se encontró ningún archivo con: **{busqueda}**")

# ─────────────────────────────────────────────
#  TABS PRINCIPALES
# ─────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["🗺️ Mapa de Archiveros", "📊 Vista Global", "📋 Lista de Archivos"])

# ── TAB 1: MAPA INDIVIDUAL ──────────────────
with tab1:
    # Determinar qué archivero mostrar automáticamente si hay búsqueda
    default_arch = 1
    if archivo_encontrado and archivo_encontrado in datos:
        default_arch = datos[archivo_encontrado]["archivero"]

    col_sel, _ = st.columns([1, 3])
    with col_sel:
        archivero_sel = st.selectbox(
            "Selecciona archivero",
            range(1, ARCHIVEROS + 1),
            index=default_arch - 1,
            format_func=lambda x: f"Archivero {x}",
            key="arch_mapa"
        )

    fig_mapa = crear_mapa_archivero(datos, archivero_sel, archivo_encontrado)
    st.plotly_chart(fig_mapa, use_container_width=True)

    # Leyenda
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        st.markdown("🔵 **Vacío** — Sin archivos")
    with col_l2:
        st.markdown("🟢 **Ocupado** — Con archivo(s)")
    with col_l3:
        st.markdown("🟡 **Resaltado** — Resultado de búsqueda")

    st.markdown("---")
    # Detalle de celdas ocupadas en este archivero
    archivos_en_arch = {
        nombre: info for nombre, info in datos.items()
        if info.get("archivero") == archivero_sel
    }
    if archivos_en_arch:
        st.markdown(f"#### 📁 Archivos en Archivero {archivero_sel}")
        df_arch = pd.DataFrame([
            {
                "Archivo": nombre,
                "Fila": info["fila"],
                "Sección": info["seccion"],
                "Descripción": info.get("descripcion", ""),
                "Fecha": info.get("fecha", ""),
            }
            for nombre, info in sorted(
                archivos_en_arch.items(),
                key=lambda x: (x[1]["fila"], x[1]["seccion"])
            )
        ])
        st.dataframe(df_arch, use_container_width=True, hide_index=True)
    else:
        st.info(f"El Archivero {archivero_sel} no tiene archivos registrados.")

# ── TAB 2: VISTA GLOBAL ─────────────────────
with tab2:
    fig_global = crear_vista_global(datos)
    st.plotly_chart(fig_global, use_container_width=True)

    # Tabla de resumen por archivero
    st.markdown("#### 📋 Resumen por archivero")
    resumen_rows = []
    for a in range(1, ARCHIVEROS + 1):
        archivos_a = [info for info in datos.values() if info.get("archivero") == a]
        slots_usados = len(archivos_a)
        slots_libres = FILAS * len(SECCIONES) - slots_usados
        pct_a = round(slots_usados / (FILAS * len(SECCIONES)) * 100, 1)
        resumen_rows.append({
            "Archivero": f"Archivero {a}",
            "Archivos": slots_usados,
            "Espacios libres": slots_libres,
            "Ocupación (%)": pct_a,
        })
    df_resumen = pd.DataFrame(resumen_rows)
    st.dataframe(df_resumen, use_container_width=True, hide_index=True)

# ── TAB 3: LISTA COMPLETA ───────────────────
with tab3:
    if datos:
        df_todos = datos_a_dataframe(datos)
        df_todos = df_todos.sort_values(["Archivero", "Fila", "Sección"])

        # Filtros rápidos
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_arch = st.multiselect(
                "Filtrar por Archivero",
                options=list(range(1, ARCHIVEROS + 1)),
                default=list(range(1, ARCHIVEROS + 1)),
                format_func=lambda x: f"Archivero {x}",
            )
        with col_f2:
            filtro_fila = st.multiselect(
                "Filtrar por Fila",
                options=list(range(1, FILAS + 1)),
                default=list(range(1, FILAS + 1)),
                format_func=lambda x: f"Fila {x}",
            )
        with col_f3:
            filtro_sec = st.multiselect(
                "Filtrar por Sección",
                options=SECCIONES,
                default=SECCIONES,
            )

        df_filtrado = df_todos[
            df_todos["Archivero"].isin(filtro_arch) &
            df_todos["Fila"].isin(filtro_fila) &
            df_todos["Sección"].isin(filtro_sec)
        ]

        st.markdown(f"**{len(df_filtrado)}** archivo(s) encontrado(s)")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

        # Exportar
        csv_data = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Exportar a CSV",
            data=csv_data,
            file_name="archivos_localizador.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay archivos registrados aún. Usa el panel lateral para agregar el primero.")
