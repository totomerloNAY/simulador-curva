from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import streamlit as st

# Página complementaria e independiente. No modifica el simulador original.
ROOT = Path(__file__).resolve().parent.parent
G = 9.81

# -----------------------------------------------------------------------------
# Identidad visual
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
      .block-container {max-width: 1480px; padding-top: 1.45rem; padding-bottom: 3rem;}
      .hero {
        padding: 2rem 2.15rem; border-radius: 22px; margin: .25rem 0 1.25rem 0;
        color: #f8fafc; background: linear-gradient(118deg, #0b1220 0%, #152b45 62%, #0e7490 100%);
        border: 1px solid rgba(148,163,184,.28); box-shadow: 0 16px 40px rgba(2,8,23,.16);
      }
      .hero-eyebrow {font-size:.76rem; letter-spacing:.16em; text-transform:uppercase; color:#67e8f9; font-weight:800;}
      .hero h1 {font-size:clamp(1.8rem,3.4vw,3rem); line-height:1.08; margin:.65rem 0 .65rem 0; color:#f8fafc;}
      .hero p {font-size:1rem; max-width:900px; color:#dbeafe; margin:0; line-height:1.6;}
      .hero-meta {margin-top:1.1rem; font-size:.82rem; color:#bae6fd; letter-spacing:.02em;}
      .section-kicker {font-size:.75rem; text-transform:uppercase; letter-spacing:.13em; font-weight:800; color:#0891b2; margin-bottom:.25rem;}
      .subtle {color:#64748b; font-size:.88rem;}
      .engineering-note {padding:1rem 1.15rem; border:1px solid #cbd5e1; border-left:4px solid #0891b2; background:rgba(241,245,249,.72); border-radius:10px; margin:.5rem 0 1rem 0;}
      .source-chip {display:inline-block; padding:.25rem .55rem; border-radius:999px; border:1px solid #cbd5e1; font-size:.75rem; color:#334155; margin:.15rem .2rem .15rem 0; background:#f8fafc;}
      div[data-testid="stMetric"] {background:rgba(248,250,252,.88); border:1px solid #dbe4ee; padding:15px 17px; border-radius:15px; box-shadow:0 3px 12px rgba(15,23,42,.035);}
      div[data-testid="stMetricLabel"] {color:#475569; font-weight:650;}
      div[data-testid="stMetricValue"] {color:#0f172a;}
      .photo-card {border:1px solid #dbe4ee; border-radius:16px; padding:10px; background:rgba(248,250,252,.8); height:100%;}
      .photo-card img {width:100%; height:260px; object-fit:cover; border-radius:10px; display:block;}
      .photo-caption {font-size:.82rem; line-height:1.45; color:#475569; padding:.55rem .2rem .15rem .2rem;}
      .mini-label {font-size:.7rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:#64748b;}
      .small-foot {font-size:.78rem; color:#64748b;}
      [data-testid="stTabs"] button {font-weight:650;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="hero-eyebrow">Ingeniería de transporte · Seguridad vial · Mar del Plata</div>
      <h1>Observatorio vial y análisis de estabilidad</h1>
      <p>Extensión técnica independiente para contextualizar el simulador: evidencia documental, estadística estacional, registro trazable de eventos y criterios de evaluación de adherencia.</p>
      <div class="hero-meta">TRAMO DE ESTUDIO · BOULEVARD MARÍTIMO · REFERENCIAS ALBERTI — GASCÓN</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("MÓDULO COMPLEMENTARIO · No sobrescribe ni altera el simulador ni el marco teórico existentes.")

# -----------------------------------------------------------------------------
# Fuentes y conjuntos de datos de referencia
# -----------------------------------------------------------------------------
URL_MGP_2023 = "https://www.mardelplata.gob.ar/documentos/transporte_y_transito/osv%202023%20informe%20anual_vc.pdf"
URL_QUE_2023 = "https://quedigital.com.ar/policiales/en-2023-hubo-40-muertes-y-1411-personas-heridas-en-siniestros-viales-mar-del-plata/"
URL_PBA_2024 = "https://publicaciones.transporte.gba.gob.ar/prensa/Informe-siniestralidad-vial-personas-lesionadasPBA-2024.pptx.pdf"
URL_PBA_OBS = "https://www.gba.gob.ar/seguridadvial/observatorio_vial"
URL_HCD_GASCON = "https://concejo.mdp.gob.ar/expedientes/ficha_expediente.php?anio=2021&numero=1790&tipo=E"
URL_LACAPITAL = "https://www.lacapitalmdp.com/habra-fotomultas-en-alberti-y-la-costa-ante-los-recurrentes-siniestros/"
URL_0223 = "https://www.0223.com.ar/nota/2018-9-7-13-17-0-para-evitar-nuevas-tragedias-colocan-pilotes-donde-mataron-a-lucia-bernaola"
URL_MAPA = "https://www.google.com/maps/search/?api=1&query=Boulevard+Maritimo+Alberti+Gascon+Mar+del+Plata"

pba_monthly = pd.DataFrame(
    {
        "Mes": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        "Siniestros con personas lesionadas": [2623, 2363, 2800, 2808, 2986, 2938, 2859, 2894, 3152, 3311, 3307, 3261],
    }
)

pba_season_order = ["Verano", "Otoño", "Invierno", "Primavera"]
month_season = {
    "Diciembre": "Verano", "Enero": "Verano", "Febrero": "Verano",
    "Marzo": "Otoño", "Abril": "Otoño", "Mayo": "Otoño",
    "Junio": "Invierno", "Julio": "Invierno", "Agosto": "Invierno",
    "Septiembre": "Primavera", "Octubre": "Primavera", "Noviembre": "Primavera",
}
seasonal = pba_monthly.assign(Estación=pba_monthly["Mes"].map(month_season)).groupby("Estación", as_index=False)["Siniestros con personas lesionadas"].sum()
seasonal["Estación"] = pd.Categorical(seasonal["Estación"], categories=pba_season_order, ordered=True)
seasonal = seasonal.sort_values("Estación")
seasonal["Porcentaje"] = seasonal["Siniestros con personas lesionadas"] / seasonal["Siniestros con personas lesionadas"].sum() * 100

# En 2023, General Pueyrredon registró 40 fallecimientos; la distribución mensual
# que se muestra a continuación corresponde a fallecidos, NO a todos los siniestros.
mdp_fatal_month = pd.DataFrame(
    {
        "Mes": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        "Personas fallecidas": [2, 8, 1, 4, 1, 6, 8, 4, 1, 1, 1, 3],
    }
)

fatality_history = pd.DataFrame(
    {
        "Año": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "Personas fallecidas": [25, 42, 33, 72, 44, 30, 50, 37, 40],
    }
)

incidents = pd.DataFrame(
    [
        {
            "Fecha del hecho": "2017-07-04",
            "Punto referido": "Alberti / avenida costera (Playa Chica)",
            "Hecho documentado": "Atropello de peatón; antecedente fatal",
            "Fallecidos informados": "1",
            "Lesionados informados": "No especificado en la fuente consultada",
            "Tipo de fuente": "Nota periodística retrospectiva",
            "Fuente": URL_0223,
            "Alcance": "Evento individual; no implica que sea el único del tramo.",
        },
        {
            "Fecha del hecho": "2021-08-15",
            "Punto referido": "Boulevard Marítimo / Gascón",
            "Hecho documentado": "Despiste y salida de calzada hacia el sector rocoso",
            "Fallecidos informados": "No especificado para este evento en el expediente",
            "Lesionados informados": "No especificado para este evento en el expediente",
            "Tipo de fuente": "Antecedente citado en expediente del HCD",
            "Fuente": URL_HCD_GASCON,
            "Alcance": "Evento individual; no implica que sea el único del tramo.",
        },
    ]
)

interventions = pd.DataFrame(
    [
        {"Fecha de publicación": "2018-09-07", "Punto": "Alberti / costa", "Medida o antecedente": "Instalación informada de 16 pilotes de granito; separación aproximada de 1,30 m", "Fuente": URL_0223},
        {"Fecha de publicación": "2019-07-12", "Punto": "Alberti / costa", "Medida o antecedente": "Aprobación de la colocación de un cinemómetro ante siniestros recurrentes y preocupación por la velocidad", "Fuente": URL_LACAPITAL},
    ]
)

# -----------------------------------------------------------------------------
# Tabs principales del complemento
# -----------------------------------------------------------------------------
tab_overview, tab_events, tab_stats, tab_engineering, tab_site, tab_sources = st.tabs(
    ["Resumen ejecutivo", "Registro documental", "Estadística estacional", "Modelo y FS", "Zona evaluada", "Fuentes y método"]
)

# 1. Resumen ejecutivo
with tab_overview:
    st.markdown('<div class="section-kicker">01 / Contexto cuantitativo</div>', unsafe_allow_html=True)
    st.subheader("Panorama de siniestralidad · General Pueyrredon")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Siniestros con lesionados · 2023", "1.178", help="Total municipal informado para todo General Pueyrredon; no es un recuento del tramo Alberti–Gascón.")
    k2.metric("Personas lesionadas · 2023", "1.411", help="Personas lesionadas en los siniestros con lesiones informados en el partido.")
    k3.metric("Personas fallecidas · 2023", "40", help="Total anual informado para el partido, no para el tramo de estudio.")
    k4.metric("Siniestros fatales · 2023", "37", help="La fuente informa 40 personas fallecidas distribuidas en 37 siniestros fatales.")

    st.markdown(
        f"**Fuentes:** [Informe del Observatorio de Seguridad Vial de Mar del Plata (2023)]({URL_MGP_2023}) · [Síntesis estadística de Qué digital (26/05/2024)]({URL_QUE_2023})."
    )
    st.markdown(
        """
        <div class="engineering-note"><b>Lectura correcta de los datos.</b> Las cifras anteriores pertenecen al partido de General Pueyrredon. No permiten afirmar cuántos siniestros ocurrieron en el segmento exacto del Boulevard Marítimo comprendido entre Alberti y Gascón. En las fuentes públicas revisadas se encontraron antecedentes puntuales, pero no una serie completa, georreferenciada y verificable para ese tramo.</div>
        """,
        unsafe_allow_html=True,
    )

    a, b, c = st.columns(3)
    with a:
        st.markdown("#### Alcance")
        st.write("Separar el análisis dinámico de vehículo de la evidencia histórica de siniestros. Son capas de información complementarias, no intercambiables.")
    with b:
        st.markdown("#### Trazabilidad")
        st.write("Cada estadística debe acompañarse por fuente, fecha, geografía, unidad de conteo y definición de lesión o fatalidad.")
    with c:
        st.markdown("#### Prioridad de ingeniería")
        st.write("Completar inventario georreferenciado, geometría real, medición de velocidades, estado superficial y demanda de usuarios vulnerables antes de emitir conclusiones de diseño.")

    st.markdown("#### Indicadores de calidad de la evidencia")
    quality = pd.DataFrame(
        [
            {"Indicador": "Estadística municipal anual", "Estado": "Disponible para 2023", "Uso": "Contexto del partido"},
            {"Indicador": "Serie mensual provincial", "Estado": "Disponible para 2024", "Uso": "Estacionalidad de contexto"},
            {"Indicador": "Eventos del tramo con fuente trazable", "Estado": "2 antecedentes individuales identificados", "Uso": "Documentación no exhaustiva"},
            {"Indicador": "Inventario total georreferenciado Alberti–Gascón", "Estado": "No verificado en las fuentes revisadas", "Uso": "No calcular un total local todavía"},
        ]
    )
    st.dataframe(quality, use_container_width=True, hide_index=True)

# 2. Registro de incidentes documentados
with tab_events:
    st.markdown('<div class="section-kicker">02 / Evidencia local trazable</div>', unsafe_allow_html=True)
    st.subheader("Eventos puntuales identificados en fuentes públicas")
    st.warning(
        "Este registro es documental y no exhaustivo. Contiene eventos individuales que aparecen en fuentes periodísticas o en un expediente legislativo; no es una base oficial completa ni debe interpretarse como el total de siniestros del tramo."
    )
    st.metric("Eventos individuales localizados en las fuentes revisadas", "2", help="Cuenta los dos antecedentes individuales listados en esta tabla, no el universo histórico de siniestros.")
    st.dataframe(
        incidents,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fuente": st.column_config.LinkColumn("Fuente primaria / nota", display_text="Abrir documento"),
        },
    )

    st.markdown("#### Intervenciones de seguridad vial documentadas")
    st.caption("Las siguientes filas registran medidas o decisiones públicas; no son siniestros adicionales y no se suman al recuento de eventos.")
    st.dataframe(
        interventions,
        use_container_width=True,
        hide_index=True,
        column_config={"Fuente": st.column_config.LinkColumn("Fuente", display_text="Abrir fuente")},
    )

    st.markdown("#### Incorporar una base local para actualizar los indicadores")
    st.write("El archivo CSV debe contener una fila por siniestro y la columna `fecha` en formato ISO `AAAA-MM-DD`. La plantilla descargable no incluye eventos ficticios.")
    template_path = ROOT / "data" / "registro_siniestros_template.csv"
    if template_path.exists():
        template_bytes = template_path.read_bytes()
    else:
        template_bytes = b"fecha,hora,ubicacion,tipo_siniestro,vehiculos_involucrados,lesionados,fallecidos,estado_calzada,iluminacion,fuente,observaciones\n"
    st.download_button(
        "Descargar plantilla CSV",
        data=template_bytes,
        file_name="registro_siniestros_template.csv",
        mime="text/csv",
        use_container_width=False,
    )

    uploaded = st.file_uploader("Cargar registro local (CSV)", type=["csv"], key="incidents_csv")
    if uploaded is not None:
        try:
            user_df = pd.read_csv(uploaded)
            required = {"fecha", "ubicacion", "tipo_siniestro", "lesionados", "fallecidos"}
            # Normalizar etiquetas sin modificar los valores aportados.
            user_df.columns = user_df.columns.str.strip().str.lower()
            missing = required - set(user_df.columns)
            if missing:
                st.error("Faltan columnas obligatorias: " + ", ".join(sorted(missing)))
                st.caption("Usá la plantilla descargable para respetar los nombres de las columnas.")
            else:
                user_df["fecha"] = pd.to_datetime(user_df["fecha"], errors="coerce", dayfirst=False)
                user_df["lesionados"] = pd.to_numeric(user_df["lesionados"], errors="coerce").fillna(0)
                user_df["fallecidos"] = pd.to_numeric(user_df["fallecidos"], errors="coerce").fillna(0)
                user_df = user_df.dropna(subset=["fecha"])
                u1, u2, u3 = st.columns(3)
                u1.metric("Registros válidos con fecha", f"{len(user_df):,}".replace(",", "."))
                u2.metric("Personas lesionadas cargadas", f"{int(user_df['lesionados'].sum()):,}".replace(",", "."))
                u3.metric("Personas fallecidas cargadas", f"{int(user_df['fallecidos'].sum()):,}".replace(",", "."))
                if not user_df.empty:
                    user_df["Mes"] = user_df["fecha"].dt.month
                    month_counts = user_df.groupby("Mes").size().reindex(range(1, 13), fill_value=0)
                    month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                    local_month_chart = pd.DataFrame({"Mes": month_names, "Siniestros registrados": month_counts.values}).set_index("Mes")
                    st.markdown("##### Distribución mensual de la base cargada")
                    st.bar_chart(local_month_chart, use_container_width=True)
                    st.dataframe(user_df, use_container_width=True, hide_index=True)
                else:
                    st.info("El archivo se leyó, pero no contiene fechas válidas para graficar.")
        except Exception as exc:
            st.error(f"No se pudo leer el CSV: {exc}")

# 3. Estadísticas estacionales
with tab_stats:
    st.markdown('<div class="section-kicker">03 / Análisis temporal</div>', unsafe_allow_html=True)
    st.subheader("Estacionalidad observada en la Provincia de Buenos Aires · 2024")
    p1, p2, p3 = st.columns(3)
    p1.metric("Siniestros con lesionados", "35.302")
    p2.metric("Personas lesionadas", "45.527")
    p3.metric("Promedio mensual", "2.942", help="Cálculo directo: 35.302 / 12 ≈ 2.942. El informe de PBA lo presenta como un promedio aproximado de 2.941.")
    st.caption(f"Fuente: [Informe preliminar de Siniestralidad Vial y Personas Lesionadas, PBA 2024]({URL_PBA_2024}). Ámbito provincial; no es una estadística propia de Mar del Plata ni del tramo estudiado.")

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("#### Siniestros con personas lesionadas por mes")
        monthly_plot = pba_monthly.set_index("Mes")
        st.bar_chart(monthly_plot, use_container_width=True)
        peak_row = pba_monthly.loc[pba_monthly["Siniestros con personas lesionadas"].idxmax()]
        low_row = pba_monthly.loc[pba_monthly["Siniestros con personas lesionadas"].idxmin()]
        st.caption(f"Máximo mensual publicado: {peak_row['Mes']} ({peak_row['Siniestros con personas lesionadas']:,}). Mínimo: {low_row['Mes']} ({low_row['Siniestros con personas lesionadas']:,}).".replace(",", "."))
    with right:
        st.markdown("#### Proporción por estación")
        season_spec = {
            "mark": {"type": "arc", "innerRadius": 62, "outerRadius": 122, "stroke": "white", "strokeWidth": 2},
            "encoding": {
                "theta": {"field": "Siniestros con personas lesionadas", "type": "quantitative"},
                "color": {"field": "Estación", "type": "nominal", "sort": pba_season_order, "scale": {"scheme": "tealblues"}},
                "tooltip": [
                    {"field": "Estación", "type": "nominal", "title": "Estación"},
                    {"field": "Siniestros con personas lesionadas", "type": "quantitative", "title": "Siniestros", "format": ","},
                    {"field": "Porcentaje", "type": "quantitative", "title": "Porcentaje", "format": ".1f"},
                ],
            },
            "view": {"stroke": None},
        }
        st.vega_lite_chart(seasonal, season_spec, use_container_width=True)
        st.dataframe(
            seasonal.assign(**{"Siniestros con personas lesionadas": seasonal["Siniestros con personas lesionadas"].map(lambda x: f"{int(x):,}".replace(",", ".")), "Porcentaje": seasonal["Porcentaje"].map(lambda x: f"{x:.1f}%")})[["Estación", "Siniestros con personas lesionadas", "Porcentaje"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("#### Personas fallecidas por mes · General Pueyrredon · 2023")
    st.caption("Esta serie representa personas fallecidas, no todos los siniestros ocurridos en el mes. No debe compararse directamente con la serie provincial de siniestros con personas lesionadas de 2024.")
    st.bar_chart(mdp_fatal_month.set_index("Mes"), use_container_width=True)

    st.markdown("#### Evolución anual de personas fallecidas · General Pueyrredon")
    st.line_chart(fatality_history.set_index("Año"), use_container_width=True)
    st.caption(f"Serie reproducida a partir de [Qué digital, informe estadístico municipal 2023]({URL_QUE_2023}). Los años y la cobertura geográfica se mantienen explícitos para evitar mezclar unidades.")

    st.markdown(
        """
        <div class="engineering-note"><b>Interpretación.</b> La primavera concentra la mayor fracción de los siniestros provinciales con lesionados en esta agregación por estación (septiembre–noviembre). Esto no prueba que el tramo Alberti–Gascón tenga el mismo patrón. Para estudiar estacionalidad local hace falta una serie de varios años, georreferenciada y con cobertura homogénea, idealmente junto con aforos de tránsito y exposición (vehículos-kilómetro).</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### Tabla mensual usada en el gráfico provincial")
    st.dataframe(pba_monthly, use_container_width=True, hide_index=True)
    st.download_button(
        "Descargar serie mensual PBA 2024",
        pba_monthly.to_csv(index=False).encode("utf-8-sig"),
        file_name="pba_siniestros_con_lesionados_por_mes_2024.csv",
        mime="text/csv",
    )

# 4. Teoría ingenieril y FS independiente
with tab_engineering:
    st.markdown('<div class="section-kicker">04 / Verificación físico-matemática</div>', unsafe_allow_html=True)
    st.subheader("Factor de seguridad frente a pérdida de adherencia")
    st.markdown("El factor de seguridad compara la capacidad lateral disponible con la demanda que exige la trayectoria. En este módulo se presenta primero el caso sin frenado y después la reserva lateral cuando se aplica fuerza longitudinal.")

    eq1, eq2 = st.columns(2)
    with eq1:
        st.latex(r"F_c = m\frac{v^2}{R}\qquad F_{r,\max}=\mu m g")
        st.latex(r"FS_{\mathrm{lateral}}=\frac{F_{r,\max}}{F_c}=\frac{\mu g R}{v^2}")
        st.markdown("**Lectura:** `FS > 1` indica reserva en el modelo idealizado; `FS = 1` representa igualdad entre demanda y límite; `FS < 1` indica que la demanda supera la adherencia disponible asumida.")
    with eq2:
        st.latex(r"F_{y,\max}=\sqrt{(\mu N)^2-F_x^2}")
        st.latex(r"FS_{\mathrm{con\ frenado}}=\frac{F_{y,\max}}{m v^2/R}")
        st.markdown("El frenado consume parte de la capacidad total de fricción. El margen lateral puede caer aunque la velocidad y el radio no cambien.")

    st.markdown("#### Calculadora de reserva lateral")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        speed = st.slider("Velocidad (km/h)", min_value=10, max_value=120, value=55, step=1, key="fs_speed")
    with c2:
        radius = st.number_input("Radio de curva R (m)", min_value=10.0, max_value=300.0, value=60.0, step=5.0, key="fs_radius")
    with c3:
        mu = st.select_slider("Coeficiente μ asumido", options=[0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70], value=0.50, key="fs_mu")
    with c4:
        ax_g = st.slider("Desaceleración longitudinal (g)", min_value=0.0, max_value=0.8, value=0.30, step=0.05, key="fs_ax")

    v_ms = speed / 3.6
    a_lat = v_ms**2 / radius
    fs_static = (mu * G) / a_lat if a_lat > 0 else math.inf
    lateral_accel_available = G * math.sqrt(max(0.0, mu**2 - ax_g**2)) if ax_g < mu else 0.0
    fs_braking = lateral_accel_available / a_lat if a_lat > 0 else math.inf
    v_limit = math.sqrt(mu * G * radius) * 3.6
    lateral_capacity_force_per_mass = lateral_accel_available

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Aceleración lateral", f"{a_lat:.2f} m/s²", f"{a_lat / G:.2f} g")
    m2.metric("FS sin frenado", f"{fs_static:.2f}")
    m3.metric("FS con frenado", f"{fs_braking:.2f}")
    m4.metric("Velocidad límite idealizada", f"{v_limit:.1f} km/h")

    reserve_df = pd.DataFrame(
        {
            "Magnitud": ["Demanda lateral", "Capacidad lateral sin frenar", "Capacidad lateral con frenado"],
            "Aceleración equivalente (m/s²)": [a_lat, mu * G, lateral_capacity_force_per_mass],
        }
    ).set_index("Magnitud")
    st.bar_chart(reserve_df, use_container_width=True)
    if fs_braking >= 1.0:
        st.success("Con los parámetros seleccionados, la demanda lateral no supera la capacidad lateral restante del modelo combinado.")
    else:
        st.error("Con los parámetros seleccionados, la demanda lateral supera la capacidad restante estimada; el modelo predice margen insuficiente.")

    st.markdown(
        """
        <div class="engineering-note"><b>Importante: no confundir umbral físico con factor de diseño normativo.</b> El valor 1 es la frontera matemática de este modelo, no una declaración automática de seguridad vial ni un factor de diseño legal. Para fijar un FS de proyecto se requiere definir norma, combinación de acciones, incertidumbre, estado de neumáticos, medición del coeficiente de fricción, geometría real y nivel de confiabilidad requerido.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Hipótesis y límites del modelo"):
        st.markdown(
            """
            - Curva horizontal, radio constante y calzada sin peralte en el cálculo simplificado.
            - La adherencia se representa mediante un único coeficiente efectivo μ; no es un valor medido in situ.
            - No se modelan transferencia dinámica de cargas, suspensión, estado y temperatura de neumáticos, reparto de frenado, textura/microtextura, espesor de película de agua, drenaje, pendiente longitudinal ni maniobras transitorias.
            - La masa se cancela en la velocidad límite bajo las hipótesis básicas, pero la masa sí afecta las fuerzas absolutas calculadas.
            - El círculo de fricción es una aproximación; una evaluación de seguridad vial requiere contrastarlo con mediciones y normas técnicas aplicables.
            """
        )

# 5. Zona evaluada y fotografías
with tab_site:
    st.markdown('<div class="section-kicker">05 / Inspección visual y contexto geométrico</div>', unsafe_allow_html=True)
    st.subheader("Boulevard Marítimo · referencias Alberti y Gascón")
    st.markdown(f"[Abrir la zona en Google Maps ↗]({URL_MAPA})")
    st.write("Las siguientes imágenes publicadas muestran el entorno costero y las intervenciones de seguridad documentadas en las referencias citadas. Son antecedentes visuales periodísticos, no un relevamiento topográfico ni una inspección actual certificada.")

    image1 = "https://storage.lacapitalmdp.com/2017/06/Alberti-La-Costa-1024x681.jpg"
    image2 = "https://pxcdn.0223.com.ar/f/092018/1536333821808.webp?ch=780&cw=1280&extw=jpg"
    photo_a, photo_b = st.columns(2)
    with photo_a:
        st.markdown(
            f"""
            <div class="photo-card">
              <a href="{URL_LACAPITAL}" target="_blank" rel="noopener noreferrer">
                <img src="{image1}" alt="Intersección de Alberti con la avenida costera en Mar del Plata" loading="lazy" />
              </a>
              <div class="mini-label">Registro visual A</div>
              <div class="photo-caption">Entorno de Alberti y la costa, utilizado como referencia periodística sobre controles de velocidad y siniestros recurrentes. <a href="{URL_LACAPITAL}" target="_blank" rel="noopener noreferrer">Fuente: La Capital, 12/07/2019.</a></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with photo_b:
        st.markdown(
            f"""
            <div class="photo-card">
              <a href="{URL_0223}" target="_blank" rel="noopener noreferrer">
                <img src="{image2}" alt="Pilotes instalados como medida de contención en el sector costero" loading="lazy" />
              </a>
              <div class="mini-label">Registro visual B</div>
              <div class="photo-caption">Intervención de contención peatonal informada en 2018: pilotes junto a la vereda en el sector Alberti–costa. <a href="{URL_0223}" target="_blank" rel="noopener noreferrer">Fuente: 0223, 07/09/2018.</a></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Matriz de inspección propuesta")
    checklist = pd.DataFrame(
        [
            {"Variable a relevar": "Radio horizontal real", "Método recomendado": "Levantamiento geométrico / cartografía validada", "Unidad o evidencia": "m; plano con puntos de control"},
            {"Variable a relevar": "Peralte y pendiente transversal", "Método recomendado": "Nivelación o estación total", "Unidad o evidencia": "%; sección transversal"},
            {"Variable a relevar": "Velocidad operativa", "Método recomendado": "Aforo y medición de velocidad con protocolo", "Unidad o evidencia": "V50, V85, distribución por horario"},
            {"Variable a relevar": "Fricción / condición de superficie", "Método recomendado": "Ensayo instrumental y ficha de pavimento", "Unidad o evidencia": "Método, equipo y condición climática"},
            {"Variable a relevar": "Visibilidad e iluminación", "Método recomendado": "Inspección diurna/nocturna", "Unidad o evidencia": "distancia, lux, obstáculos"},
            {"Variable a relevar": "Usuarios vulnerables y cruces", "Método recomendado": "Conteo de peatones, ciclistas y cruces", "Unidad o evidencia": "flujo por franja horaria"},
            {"Variable a relevar": "Drenaje y agua sobre calzada", "Método recomendado": "Inspección después de lluvia y revisión de desagües", "Unidad o evidencia": "zonas de acumulación y registro fotográfico"},
        ]
    )
    st.dataframe(checklist, use_container_width=True, hide_index=True)
    st.caption("Los factores anteriores son variables a inspeccionar; no se afirma que exista una deficiencia concreta sin medición de campo.")

# 6. Fuentes, metodología y limitaciones
with tab_sources:
    st.markdown('<div class="section-kicker">06 / Auditoría de datos</div>', unsafe_allow_html=True)
    st.subheader("Fuentes utilizadas y límites de inferencia")
    sources = pd.DataFrame(
        [
            {"Fuente": "Observatorio de Seguridad Vial de Mar del Plata · Informe 2023", "Tipo": "Informe municipal", "Aporta": "Serie anual local y estadísticas de siniestralidad", "Enlace": URL_MGP_2023},
            {"Fuente": "Qué digital · balance de siniestralidad 2023", "Tipo": "Nota basada en informe del Observatorio", "Aporta": "1.178 siniestros con lesionados, 1.411 personas lesionadas y 40 fallecidas en General Pueyrredon; detalle mensual de fallecidos", "Enlace": URL_QUE_2023},
            {"Fuente": "Honorable Concejo Deliberante · expediente E-1790/2021", "Tipo": "Documento legislativo", "Aporta": "Antecedente de despiste el 15/08/2021 en Boulevard Marítimo y Gascón", "Enlace": URL_HCD_GASCON},
            {"Fuente": "La Capital · 12/07/2019", "Tipo": "Nota periodística", "Aporta": "Antecedentes de siniestros recurrentes y aprobación de cinemómetro en Alberti y la costa", "Enlace": URL_LACAPITAL},
            {"Fuente": "0223 · 07/09/2018", "Tipo": "Nota periodística", "Aporta": "Intervención con pilotes y señalización en Alberti y la costa", "Enlace": URL_0223},
            {"Fuente": "Observatorio Vial de la Provincia de Buenos Aires · Informe 2024", "Tipo": "Estadística provincial preliminar", "Aporta": "Siniestros con lesionados por mes y día de la semana", "Enlace": URL_PBA_2024},
            {"Fuente": "Observatorio Vial PBA · portal institucional", "Tipo": "Portal oficial", "Aporta": "Metodología y acceso a estadísticas oficiales/preliminares", "Enlace": URL_PBA_OBS},
        ]
    )
    st.dataframe(sources, use_container_width=True, hide_index=True, column_config={"Enlace": st.column_config.LinkColumn("Documento", display_text="Abrir fuente")})

    st.markdown("#### Reglas de integridad aplicadas")
    st.markdown(
        """
        1. **No extrapolar el partido al tramo.** Las series de General Pueyrredon y de toda la provincia se muestran como contexto, no como conteo de Alberti–Gascón.
        2. **Separar unidades.** Siniestros, personas lesionadas y personas fallecidas son indicadores diferentes; una persona fallecida no equivale a un siniestro.
        3. **No completar vacíos por inferencia.** Si una fuente no detalla lesionados o fallecidos de un evento concreto, el panel lo indica como no especificado.
        4. **Evitar causalidad no probada.** Una concentración temporal provincial no demuestra que la época del año cause el siniestro ni que el tramo tenga la misma distribución.
        5. **Documentar incertidumbre.** Los valores de adherencia introducidos en el simulador son hipótesis; para un informe de ingeniería deben medirse o justificarse con una fuente técnica válida.
        """
    )
    st.markdown("#### Referencia de cálculo estacional")
    st.write("Las estaciones se agregan por meses del hemisferio sur: verano = diciembre–febrero; otoño = marzo–mayo; invierno = junio–agosto; primavera = septiembre–noviembre. Cada porcentaje se calcula sobre los 35.302 siniestros provinciales con personas lesionadas informados para 2024.")
    st.caption("Complemento técnico de carácter educativo. No constituye auditoría pericial, estudio de seguridad vial certificado ni recomendación de velocidad operativa para circular.")

st.markdown("---")
st.caption("Observatorio vial y análisis de estabilidad · módulo adicional e independiente · versión 1.0")
