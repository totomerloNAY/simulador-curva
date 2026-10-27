from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# Página NUEVA e independiente. No edita el simulador original ni el complemento v1.
st.set_page_config(
    page_title="Análisis local | Pérdida de control",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="expanded",
)

G = 9.81
FACTOR_DINAMICO = 0.75
RADIO_REFERENCIA_M = 60.0  # Hipótesis inicial; debe contrastarse con un relevamiento geométrico.
FECHA_CONSULTA = datetime.now().strftime("%d-%m-%Y")

# Fuentes que documentan hechos del sector concreto de la curva de Gascón.
URL_MAPA = "https://www.google.com/maps/search/?api=1&query=Boulevard+Maritimo+Gasc%C3%B3n+Mar+del+Plata"
URL_EVENTO_AGO_2021 = "https://www.pagina12.com.ar/361707-milagro-en-mar-del-plata-un-auto-cayo-desde-un-barranco-golp"
URL_EXPEDIENTE_HCD = "https://www.concejomdp.gov.ar/expedientes/ficha_expediente.php?anio=2021&numero=1790&tipo=E"
URL_EVENTO_SEP_2021 = "https://puntonoticias.com/perdio-el-control-del-auto-y-termino-atrapada-entre-las-piedras-de-cabo-corrientes/"
URL_FOTO_ALBERTI = "https://www.lacapitalmdp.com/habra-fotomultas-en-alberti-y-la-costa-ante-los-recurrentes-siniestros/"
URL_FOTO_PILOTES = "https://www.0223.com.ar/nota/2018-9-7-13-17-0-para-evitar-nuevas-tragedias-colocan-pilotes-donde-mataron-a-lucia-bernaola"

# ----------------------------------------------------------------------------
# Identidad visual: fondo claro, tipografía consistente y contraste alto.
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
      :root { --ink:#172033; --muted:#526176; --line:#d6e0eb; --paper:#ffffff; --canvas:#eef3f8; --navy:#10243a; --cyan:#0891b2; }
      html, body, [class*="css"], .stApp { font-family:'Inter','Segoe UI',Arial,sans-serif !important; }
      .stApp { background:linear-gradient(180deg,#f4f7fb 0%,#edf2f7 100%); color:var(--ink) !important; }
      .block-container { max-width:1500px; padding-top:1.25rem; padding-bottom:3rem; }
      .stApp p, .stApp li, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
      .stApp [data-testid="stMarkdownContainer"] { color:var(--ink); }
      .stApp p, .stApp li { line-height:1.62; }
      .hero { padding:2.1rem 2.25rem; border-radius:22px; margin:0 0 1.1rem 0;
        color:#f8fafc !important; background:linear-gradient(118deg,#0b1423 0%,#15334d 60%,#0e7490 100%);
        border:1px solid #233c55; box-shadow:0 16px 40px rgba(15,23,42,.14); }
      .hero * { color:#f8fafc !important; }
      .hero-eyebrow { font-size:.75rem; letter-spacing:.16em; text-transform:uppercase; color:#67e8f9 !important; font-weight:800; }
      .hero h1 { font-size:clamp(1.8rem,3vw,3rem); line-height:1.08; margin:.7rem 0; font-weight:800; }
      .hero p { font-size:1rem; max-width:980px; color:#dbeafe !important; margin:0; }
      .hero-meta { margin-top:1.1rem; font-size:.82rem; color:#bae6fd !important; letter-spacing:.04em; }
      .section-kicker { font-size:.73rem; text-transform:uppercase; letter-spacing:.15em; font-weight:800; color:#087f9f !important; margin-bottom:.25rem; }
      .muted { color:#526176 !important; font-size:.88rem; }
      .engineering-note { padding:1rem 1.15rem; border:1px solid #c8d7e5; border-left:4px solid #0891b2; background:#f8fbfe; color:#172033 !important; border-radius:12px; margin:.6rem 0 1rem; }
      .engineering-note * { color:#172033 !important; }
      .status-card { padding:1rem 1.15rem; border-radius:12px; margin:.6rem 0 1rem; border:1px solid #cbd5e1; background:#fff; color:#172033 !important; }
      .status-card.good { border-left:5px solid #059669; }
      .status-card.warn { border-left:5px solid #d97706; }
      .status-card.bad { border-left:5px solid #dc2626; }
      .status-card * { color:#172033 !important; }
      .event-card { padding:1.1rem 1.2rem; border:1px solid #d7e1ec; border-radius:14px; background:#fff; margin:.5rem 0 1rem; box-shadow:0 4px 14px rgba(15,23,42,.035); }
      .event-date { color:#087f9f !important; font-size:.78rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }
      .event-card h3 { margin:.35rem 0; color:#172033 !important; font-size:1.08rem; }
      .event-card p { color:#43536a !important; margin:.25rem 0; }
      .small-foot { font-size:.77rem; color:#526176 !important; }
      div[data-testid="stMetric"] { background:#fff; border:1px solid #d9e2ec; padding:14px 16px; border-radius:14px; box-shadow:0 3px 12px rgba(15,23,42,.035); }
      div[data-testid="stMetricLabel"] { color:#526176 !important; font-weight:650; }
      div[data-testid="stMetricValue"] { color:#10243a !important; font-weight:800; }
      div[data-testid="stMetricDelta"] { font-weight:600; }
      [data-testid="stTabs"] button { font-weight:700; color:#334155 !important; }
      [data-testid="stTabs"] button[aria-selected="true"] { color:#087f9f !important; }
      [data-testid="stSelectbox"] label, [data-testid="stSlider"] label, [data-testid="stNumberInput"] label,
      [data-testid="stCheckbox"] label, [data-testid="stRadio"] label { color:#172033 !important; font-weight:650 !important; }
      div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] { background:#fff !important; border-color:#b9c8d8 !important; }
      div[data-baseweb="select"] *, div[data-baseweb="input"] input, input, textarea { color:#172033 !important; -webkit-text-fill-color:#172033 !important; }
      div[role="listbox"] *, ul[role="listbox"] * { color:#172033 !important; background:#fff !important; }
      [data-testid="stDataFrame"] { border:1px solid #d9e2ec; border-radius:10px; overflow:hidden; }
      div[data-testid="stExpander"] { border:1px solid #d7e1ec; border-radius:12px; background:#fff; }
      a { color:#0369a1 !important; font-weight:600; }
      hr { border-color:#d7e1ec; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="hero-eyebrow">Ingeniería de transporte · Análisis localizado</div>
      <h1>Pérdida de control vehicular en curva</h1>
      <p>Estudio focalizado en la curva del Boulevard Marítimo a la altura de Gascón, con referencias al entorno de Alberti. Integra antecedentes documentados y un simulador físico interactivo para visualizar cómo cambian las fuerzas, la adherencia disponible y el factor de seguridad.</p>
      <div class="hero-meta">ZONA DE ESTUDIO · BOULEVARD MARÍTIMO · CURVA DE GASCÓN · MAR DEL PLATA</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Módulo adicional v2 · No modifica el simulador original ni el complemento anterior · Última ejecución: " + FECHA_CONSULTA)

# ----------------------------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------------------------
def fmt_num(x: float, dec: int = 1) -> str:
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def forces_for_speed(speed_kmh: float, mass_kg: float, radius_m: float, mu: float, brake_g: float) -> dict[str, float]:
    v_ms = speed_kmh / 3.6
    a_lat = v_ms * v_ms / radius_m
    demand_n = mass_kg * a_lat
    capacity_n = mass_kg * G * mu
    brake_n = mass_kg * G * brake_g
    available_n = math.sqrt(max(0.0, capacity_n**2 - brake_n**2)) if brake_n < capacity_n else 0.0
    dynamic_n = mass_kg * G * mu * FACTOR_DINAMICO
    fs_static = capacity_n / demand_n if demand_n > 0 else math.inf
    fs_combined = available_n / demand_n if demand_n > 0 else math.inf
    limit_kmh = math.sqrt(mu * G * radius_m) * 3.6
    margin_n = available_n - demand_n
    return {
        "v_ms": v_ms,
        "a_lat": a_lat,
        "a_lat_g": a_lat / G,
        "demand_n": demand_n,
        "capacity_n": capacity_n,
        "brake_n": brake_n,
        "available_n": available_n,
        "dynamic_n": dynamic_n,
        "fs_static": fs_static,
        "fs_combined": fs_combined,
        "limit_kmh": limit_kmh,
        "margin_n": margin_n,
    }


def chart_line_spec(x_title: str, y_title: str, series_order: list[str], colors: list[str], y_format: str = ",.0f") -> dict:
    return {
        "width": "container",
        "height": 360,
        "mark": {"type": "line", "strokeWidth": 3, "point": {"filled": True, "size": 28}},
        "encoding": {
            "x": {
                "field": "Velocidad (km/h)", "type": "quantitative",
                "title": x_title, "scale": {"zero": False},
                "axis": {"labelFontSize": 12, "titleFontSize": 13, "grid": False, "format": ".0f"},
            },
            "y": {
                "field": "Valor", "type": "quantitative", "title": y_title,
                "axis": {"labelFontSize": 12, "titleFontSize": 13, "grid": True, "gridColor": "#dbe4ee", "format": y_format},
            },
            "color": {
                "field": "Serie", "type": "nominal", "title": "Curva",
                "scale": {"domain": series_order, "range": colors},
                "legend": {"orient": "bottom", "labelFontSize": 12, "titleFontSize": 12, "symbolStrokeWidth": 4},
            },
            "tooltip": [
                {"field": "Serie", "type": "nominal", "title": "Magnitud"},
                {"field": "Velocidad (km/h)", "type": "quantitative", "title": "Velocidad", "format": ".0f"},
                {"field": "Valor", "type": "quantitative", "title": y_title, "format": y_format},
            ],
        },
        "config": {
            "background": "#ffffff",
            "view": {"stroke": "#dbe4ee", "strokeWidth": 1},
            "axis": {"labelColor": "#334155", "titleColor": "#172033", "domainColor": "#9fb0c3", "tickColor": "#9fb0c3"},
            "legend": {"labelColor": "#334155", "titleColor": "#172033"},
        },
    }

# ----------------------------------------------------------------------------
# Navegación principal
# ----------------------------------------------------------------------------
tab_resumen, tab_eventos, tab_practica, tab_teoria, tab_zona, tab_fuentes = st.tabs(
    ["Resumen local", "Registro de pérdida de control", "Simulador gráfico", "Fundamentos y FS", "Inspección de la curva", "Fuentes y metodología"]
)

# ----------------------------------------------------------------------------
# 1. Resumen centrado exclusivamente en el tramo
# ----------------------------------------------------------------------------
with tab_resumen:
    st.markdown('<div class="section-kicker">01 / Delimitación del estudio</div>', unsafe_allow_html=True)
    st.subheader("Curva del Boulevard Marítimo a la altura de Gascón")
    st.write("El análisis se concentra en la curva de la costa en las inmediaciones de Gascón, con referencias complementarias al cruce de Alberti y la costa. La prioridad es estudiar la secuencia de pérdida de control, salida de calzada y posible interacción con la vereda y el borde costero.")

    k1, k2, k3 = st.columns(3)
    k1.metric("Antecedentes específicos localizados", "2", help="Dos eventos publicados que describen pérdida de control en la curva de Gascón. No representa el total histórico del lugar.")
    k2.metric("Período de los casos documentados", "2021", help="Los dos eventos utilizados en este registro ocurrieron en agosto y septiembre de 2021.")
    k3.metric("Total histórico del tramo", "No verificado", help="No se encontró una serie pública completa y georreferenciada que permita afirmar el total histórico de siniestros de este segmento.")

    st.markdown(
        """
        <div class="engineering-note"><b>Alcance de la evidencia.</b> Se identificaron dos notas sobre vehículos que perdieron el control en la curva a la altura de Gascón, fechadas <b>15-08-2021</b> y <b>23-09-2021</b>. Son antecedentes documentales, no un padrón exhaustivo. No se calculan porcentajes por estación ni tasas anuales para la zona porque una muestra de dos casos no permite conclusiones temporales fiables.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Secuencia de riesgo que analiza el simulador")
    seq_cols = st.columns(4)
    sequence = [
        ("01", "Demanda lateral", "La trayectoria curva exige aceleración centrípeta, proporcional a v²/R."),
        ("02", "Reserva de adherencia", "El neumático tiene un límite de fuerza lateral condicionado por μ y la carga normal."),
        ("03", "Margen consumido", "Frenar mientras se gira utiliza parte de la capacidad disponible de fricción."),
        ("04", "Salida de trayectoria", "Si la demanda supera la capacidad disponible, aumenta el riesgo modelado de deslizamiento y despiste."),
    ]
    for col, (num, title, desc) in zip(seq_cols, sequence):
        with col:
            st.markdown(f'<div class="event-card"><div class="event-date">ETAPA {num}</div><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

    st.markdown("#### Referencia geográfica")
    st.markdown(f"[Abrir en el mapa: Boulevard Marítimo y Gascón ↗]({URL_MAPA})")
    st.caption("La geometría de 60 m usada inicialmente en la calculadora es una hipótesis de simulación basada en el escenario del proyecto. No debe tratarse como radio medido o certificado de esta curva.")

# ----------------------------------------------------------------------------
# 2. Incidentes específicos de pérdida de control; fechas en DD-MM-AAAA
# ----------------------------------------------------------------------------
with tab_eventos:
    st.markdown('<div class="section-kicker">02 / Antecedentes documentales locales</div>', unsafe_allow_html=True)
    st.subheader("Pérdida de control y salida de calzada en la curva de Gascón")
    st.warning("Registro no exhaustivo: se muestran únicamente dos casos localizados en fuentes públicas. No se puede inferir de esta lista el total de choques de la zona ni establecer causalidad definitiva.")

    st.markdown(
        f"""
        <div class="event-card">
          <div class="event-date">15-08-2021 · MADRUGADA</div>
          <h3>Despiste y caída hacia las rocas del sector costero</h3>
          <p><b>Ubicación publicada:</b> Boulevard Marítimo, curva a la altura de Gascón, sector Playa Chica.</p>
          <p><b>Secuencia informada:</b> el conductor perdió el control, el vehículo subió a la vereda, impactó contra el murallón y cayó sobre las rocas desde una altura informada de alrededor de 10 metros.</p>
          <p><b>Resultado informado:</b> el conductor resultó ileso. La noticia describe el resultado del hecho, pero no permite atribuir una causa única al siniestro.</p>
          <p><a href="{URL_EVENTO_AGO_2021}" target="_blank" rel="noopener noreferrer">Fuente periodística: Página/12 ↗</a> · <a href="{URL_EXPEDIENTE_HCD}" target="_blank" rel="noopener noreferrer">Expediente del HCD ↗</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="event-card">
          <div class="event-date">23-09-2021 · MAÑANA</div>
          <h3>Nuevo despiste en la curva con calzada reportada mojada</h3>
          <p><b>Ubicación publicada:</b> curva de la costa a la altura de Gascón, sector Cabo Corrientes.</p>
          <p><b>Secuencia informada:</b> la conductora perdió el control, rompió el paredón costero y el vehículo terminó entre las rocas. La nota menciona que la calzada estaba mojada por la lluvia; esa condición se registra como contexto reportado, no como causa demostrada.</p>
          <p><b>Resultado informado:</b> la conductora sufrió politraumatismos leves, según la publicación consultada.</p>
          <p><a href="{URL_EVENTO_SEP_2021}" target="_blank" rel="noopener noreferrer">Fuente periodística: Punto Noticias ↗</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Síntesis de trazabilidad")
    event_df = pd.DataFrame(
        [
            {"Fecha (DD-MM-AAAA)": "15-08-2021", "Lugar referido": "Boulevard Marítimo / Gascón", "Evento documentado": "Pérdida de control, impacto contra murallón y caída hacia rocas", "Resultado informado": "Conductor ileso", "Fuente": "Página/12"},
            {"Fecha (DD-MM-AAAA)": "23-09-2021", "Lugar referido": "Curva costera / Gascón", "Evento documentado": "Pérdida de control, rotura del paredón y caída hacia rocas", "Resultado informado": "Lesiones leves informadas", "Fuente": "Punto Noticias"},
        ]
    )
    st.dataframe(event_df, use_container_width=True, hide_index=True)
    st.markdown(
        """
        <div class="engineering-note"><b>Lectura temporal responsable.</b> Que las dos noticias encontradas sean de agosto y septiembre de 2021 no significa que esos sean los meses con mayor siniestralidad en el sitio. El registro depende de qué hechos se publicaron y localizaron; para estudiar estacionalidad real se necesita una serie completa con fechas, ubicación precisa y criterios uniformes de inclusión.</div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# 3. Simulador y panel de gráficos: controles conocidos y resultados claros
# ----------------------------------------------------------------------------
with tab_practica:
    st.markdown('<div class="section-kicker">03 / Laboratorio práctico</div>', unsafe_allow_html=True)
    st.subheader("Simulador gráfico de pérdida de adherencia")
    st.write("Elegí un vehículo, una condición de pavimento y la velocidad de circulación. Los gráficos se recalculan con esos parámetros para comparar la fuerza que exige la curva contra la adherencia estimada.")

    control_col, result_col = st.columns([0.82, 1.45], gap="large")
    with control_col:
        st.markdown("#### Parámetros del escenario")
        vehicle_type = st.selectbox(
            "Tipo de vehículo / masa",
            [
                "Personalizado",
                "Auto de ciudad (950 kg)",
                "Auto mediano / sedán (1.300 kg)",
                "SUV / camioneta (1.850 kg)",
            ],
            index=2,
            key="v2_vehicle_type",
        )
        if vehicle_type == "Personalizado":
            mass_kg = st.number_input("Masa del vehículo (kg)", min_value=500, max_value=4000, value=1200, step=50, key="v2_mass_custom")
        elif vehicle_type == "Auto de ciudad (950 kg)":
            mass_kg = 950
        elif vehicle_type == "Auto mediano / sedán (1.300 kg)":
            mass_kg = 1300
        else:
            mass_kg = 1850

        surface_options = {
            "Asfalto seco nuevo / rugoso · μ = 0,60": 0.60,
            "Asfalto seco estándar · μ = 0,50": 0.50,
            "Asfalto húmedo o desgastado · μ = 0,40": 0.40,
            "Lluvia intensa · μ = 0,30": 0.30,
            "Mojado / muy baja adherencia · μ = 0,20": 0.20,
        }
        surface_label = st.selectbox("Estado de la calzada", list(surface_options.keys()), index=1, key="v2_surface")
        mu = surface_options[surface_label]

        speed = st.slider("Velocidad de circulación (km/h)", min_value=10, max_value=120, value=55, step=1, key="v2_speed")
        radius_m = st.number_input("Radio de curva adoptado R (m)", min_value=10, max_value=200, value=int(RADIO_REFERENCIA_M), step=5, key="v2_radius", help="60 m es el supuesto inicial del proyecto; cambiarlo solo si se dispone de una medición o hipótesis de estudio explícita.")
        braking = st.checkbox("Evaluar también frenado mientras se gira", value=False, key="v2_braking")
        if braking:
            brake_g = st.slider("Desaceleración longitudinal (unidades de g)", min_value=0.05, max_value=0.80, value=0.30, step=0.05, key="v2_brake_g")
        else:
            brake_g = 0.0
        st.caption("Los valores de μ son supuestos didácticos, no mediciones del pavimento en tiempo real.")

    current = forces_for_speed(speed, float(mass_kg), float(radius_m), mu, brake_g)
    with result_col:
        st.markdown("#### Lectura inmediata del escenario")
        r1, r2, r3 = st.columns(3)
        r1.metric("Masa del vehículo", f"{fmt_num(float(mass_kg), 0)} kg")
        r2.metric("Demanda lateral Fc", f"{fmt_num(current['demand_n'])} N")
        r3.metric("Factor de seguridad lateral", f"{fmt_num(current['fs_combined'], 2)}")
        r4, r5, r6 = st.columns(3)
        r4.metric("Capacidad lateral disponible", f"{fmt_num(current['available_n'])} N")
        r5.metric("Velocidad límite idealizada", f"{fmt_num(current['limit_kmh'])} km/h")
        r6.metric("Margen de fuerza", f"{fmt_num(current['margin_n'])} N")
        st.caption(f"Aceleración lateral calculada para el escenario: {fmt_num(current['a_lat_g'], 2)} g.")

        if current["fs_combined"] > 1.20:
            status_class = "good"
            status_title = "Reserva de adherencia en el modelo"
            status_text = "La capacidad lateral estimada supera con margen la demanda calculada. Esto no garantiza la seguridad real: el modelo no incluye todas las condiciones del vehículo ni de la vía."
        elif current["fs_combined"] >= 1.0:
            status_class = "warn"
            status_title = "Margen lateral reducido"
            status_text = "La demanda aún no supera la capacidad estimada, pero la reserva es limitada. La incertidumbre en μ, el estado del neumático y las maniobras pueden cambiar el resultado."
        else:
            status_class = "bad"
            status_title = "Demanda superior a la adherencia estimada"
            status_text = "El escenario supera el límite lateral del modelo. Se identifica una condición de riesgo de deslizamiento o pérdida de trayectoria; no es una predicción exacta del resultado de un viaje real."
        st.markdown(f'<div class="status-card {status_class}"><b>{status_title}</b><br>{status_text}</div>', unsafe_allow_html=True)

        if braking:
            st.info("El frenado consume parte de la capacidad de fricción disponible. Por eso la reserva lateral se reduce aunque la velocidad y el radio permanezcan iguales.")
        else:
            st.caption("El cálculo principal se muestra sin frenado longitudinal simultáneo. Activá la opción de frenado para comparar el círculo de fricción combinado.")

    st.markdown("---")
    st.markdown('<div class="section-kicker">Panel gráfico interactivo</div>', unsafe_allow_html=True)
    st.subheader("1 · Fuerza lateral requerida frente a capacidad disponible")
    st.write("La línea de demanda crece con el cuadrado de la velocidad. Las líneas de capacidad representan el límite lateral estático, la reserva después de frenar (si se activó) y una referencia simplificada de fricción dinámica.")

    speeds = list(range(10, 121, 2))
    force_rows: list[dict[str, object]] = []
    fs_rows: list[dict[str, object]] = []
    margin_rows: list[dict[str, object]] = []
    for s in speeds:
        q = forces_for_speed(s, float(mass_kg), float(radius_m), mu, brake_g)
        force_series = [
            ("Demanda lateral", q["demand_n"]),
            ("Capacidad lateral estática", q["capacity_n"]),
            ("Referencia de roce dinámico", q["dynamic_n"]),
        ]
        if braking:
            force_series.append(("Capacidad lateral con frenado", q["available_n"]))
        for name, val in force_series:
            force_rows.append({"Velocidad (km/h)": s, "Serie": name, "Valor": val})
        fs_rows.append({"Velocidad (km/h)": s, "Serie": "FS lateral sin frenado", "Valor": q["fs_static"]})
        if braking:
            fs_rows.append({"Velocidad (km/h)": s, "Serie": "FS lateral con frenado", "Valor": q["fs_combined"]})
        fs_rows.append({"Velocidad (km/h)": s, "Serie": "Umbral físico FS = 1", "Valor": 1.0})
        margin_rows.append({"Velocidad (km/h)": s, "Margen (N)": q["margin_n"]})

    force_df = pd.DataFrame(force_rows)
    force_order = ["Demanda lateral", "Capacidad lateral estática", "Referencia de roce dinámico"]
    force_colors = ["#dc2626", "#0284c7", "#d97706"]
    if braking:
        force_order.insert(2, "Capacidad lateral con frenado")
        force_colors.insert(2, "#7c3aed")
    force_spec = chart_line_spec(
        "Velocidad de circulación (km/h)", "Fuerza (N)",
        force_order,
        force_colors,
        ",.0f",
    )
    st.vega_lite_chart(force_df, force_spec, use_container_width=True)
    st.caption(f"Vehículo: {vehicle_type}; masa: {fmt_num(float(mass_kg), 0)} kg; μ = {str(mu).replace('.', ',')}; radio adoptado: {fmt_num(float(radius_m), 0)} m. La masa modifica las fuerzas absolutas, aunque se cancela en el FS idealizado.")

    st.markdown("#### 2 · Factor de seguridad frente a velocidad")
    fs_df = pd.DataFrame(fs_rows)
    fs_order = ["FS lateral sin frenado"]
    fs_colors = ["#0284c7"]
    if braking:
        fs_order.append("FS lateral con frenado")
        fs_colors.append("#7c3aed")
    fs_order.append("Umbral físico FS = 1")
    fs_colors.append("#dc2626")
    fs_spec = chart_line_spec(
        "Velocidad de circulación (km/h)", "Factor de seguridad (adimensional)",
        fs_order,
        fs_colors,
        ".2f",
    )
    fs_spec["encoding"]["y"]["scale"] = {"zero": True, "domainMin": 0}
    st.vega_lite_chart(fs_df, fs_spec, use_container_width=True)
    st.caption("FS = capacidad lateral estimada / demanda lateral requerida. La línea FS = 1 marca igualdad física en este modelo; no es por sí sola un factor de diseño normativo.")

    st.markdown("#### 3 · Margen de adherencia que queda en cada velocidad")
    margin_df = pd.DataFrame(margin_rows)
    margin_spec = {
        "width": "container", "height": 300,
        "layer": [
            {
                "mark": {"type": "line", "color": "#0e7490", "strokeWidth": 3, "point": {"filled": True, "size": 25}},
                "encoding": {
                    "x": {"field": "Velocidad (km/h)", "type": "quantitative", "title": "Velocidad de circulación (km/h)", "axis": {"labelFontSize": 12, "titleFontSize": 13, "grid": False}},
                    "y": {"field": "Margen (N)", "type": "quantitative", "title": "Capacidad lateral − demanda (N)", "axis": {"labelFontSize": 12, "titleFontSize": 13, "grid": True, "gridColor": "#dbe4ee", "format": ",.0f"}},
                    "tooltip": [{"field": "Velocidad (km/h)", "type": "quantitative", "title": "Velocidad", "format": ".0f"}, {"field": "Margen (N)", "type": "quantitative", "title": "Margen", "format": ",.0f"}],
                },
            },
            {"data": {"values": [{"cero": 0}]}, "mark": {"type": "rule", "color": "#dc2626", "strokeDash": [6, 4], "strokeWidth": 2}, "encoding": {"y": {"field": "cero", "type": "quantitative"}}},
        ],
        "config": {"background": "#ffffff", "view": {"stroke": "#dbe4ee"}, "axis": {"labelColor": "#334155", "titleColor": "#172033", "domainColor": "#9fb0c3", "tickColor": "#9fb0c3"}},
    }
    st.vega_lite_chart(margin_df, margin_spec, use_container_width=True)
    st.caption("Margen positivo: la capacidad lateral calculada supera la demanda. Margen negativo: la demanda supera la capacidad disponible en el escenario simulado.")

    with st.expander("Ver tabla de puntos principales de la curva de respuesta"):
        selected_speeds = [20, 30, 40, 50, 55, 60, 70, 80, 90, 100, 110, 120]
        table_rows = []
        for s in selected_speeds:
            q = forces_for_speed(s, float(mass_kg), float(radius_m), mu, brake_g)
            table_rows.append({
                "Velocidad (km/h)": s,
                "Fuerza requerida (N)": fmt_num(q["demand_n"]),
                "Capacidad lateral disponible (N)": fmt_num(q["available_n"]),
                "FS combinado": fmt_num(q["fs_combined"], 2),
                "Margen (N)": fmt_num(q["margin_n"]),
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# 4. Teoría del FS y límites del modelo
# ----------------------------------------------------------------------------
with tab_teoria:
    st.markdown('<div class="section-kicker">04 / Fundamentos físico-matemáticos</div>', unsafe_allow_html=True)
    st.subheader("Factor de seguridad frente a la pérdida de control")
    st.write("El modelo compara la fuerza lateral que exige la curva con la fuerza que el contacto neumático–pavimento podría aportar bajo un coeficiente de fricción asumido.")

    t1, t2 = st.columns(2, gap="large")
    with t1:
        st.markdown("#### Demanda lateral")
        st.latex(r"a_y=\frac{v^2}{R}")
        st.latex(r"F_y=m\frac{v^2}{R}")
        st.markdown("La demanda aumenta con el cuadrado de la velocidad y disminuye cuando aumenta el radio. Por ejemplo, multiplicar la velocidad por 2 multiplica por 4 la demanda lateral, a radio constante.")
    with t2:
        st.markdown("#### Capacidad de adherencia idealizada")
        st.latex(r"F_{\mathrm{adh,max}}=\mu m g")
        st.latex(r"FS=\frac{F_{\mathrm{adh,disponible}}}{F_y}")
        st.markdown("Con frenado, una parte de la fricción se emplea longitudinalmente. En la aproximación de círculo de fricción, la reserva lateral se estima restando vectorialmente esa componente.")

    st.markdown("#### Cómo interpretar el factor de seguridad")
    fs_criteria = pd.DataFrame(
        [
            {"Resultado": "FS > 1", "Interpretación del modelo": "La capacidad estimada es mayor que la demanda calculada.", "Lectura de ingeniería": "Existe reserva matemática bajo las hipótesis ingresadas; no prueba seguridad real."},
            {"Resultado": "FS = 1", "Interpretación del modelo": "La demanda iguala el límite estimado de adherencia.", "Lectura de ingeniería": "Frontera teórica del modelo; margen nulo."},
            {"Resultado": "FS < 1", "Interpretación del modelo": "La demanda supera la capacidad estimada.", "Lectura de ingeniería": "El escenario presenta déficit de adherencia y mayor riesgo de deslizamiento."},
        ]
    )
    st.dataframe(fs_criteria, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="engineering-note"><b>Especificación y criterio de diseño.</b> En esta herramienta, FS = 1 es un umbral físico de comparación, no un factor mínimo de diseño establecido por una norma. Para especificar un factor objetivo en un proyecto real debe indicarse la norma aplicable, el nivel de confiabilidad, la incertidumbre de las variables, la geometría relevada, el peralte, las velocidades operativas y mediciones defendibles del estado superficial. No corresponde escoger un FS normativo arbitrario sin definir esas bases.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Hipótesis adoptadas por el complemento")
    assumptions = [
        "Curva horizontal de radio constante; el radio inicial de 60 m es un supuesto heredado del escenario, no un levantamiento topográfico certificado.",
        "Calzada tratada como sin peralte en las ecuaciones simplificadas. El peralte real puede modificar el balance de fuerzas.",
        "El coeficiente μ es elegible por el usuario y no se mide en tiempo real. No debe atribuirse automáticamente al pavimento de la curva.",
        "La masa modifica las fuerzas absolutas, pero se cancela del factor de seguridad y de la velocidad límite idealizada en este modelo.",
        "Se aproxima el efecto de la fricción dinámica como μd = 0,75·μ, por consistencia con el planteo académico original.",
        "No se simulan transferencia dinámica de carga, suspensión, desgaste/temperatura de neumáticos, maniobras transitorias, drenaje real ni errores del conductor.",
    ]
    for item in assumptions:
        st.markdown(f"- {item}")

# ----------------------------------------------------------------------------
# 5. Zona y checklist de inspección
# ----------------------------------------------------------------------------
with tab_zona:
    st.markdown('<div class="section-kicker">05 / Contexto físico del lugar</div>', unsafe_allow_html=True)
    st.subheader("Referencias visuales y puntos de inspección")
    st.markdown(f"[Abrir la curva en Google Maps ↗]({URL_MAPA})")
    st.write("Las imágenes son referencias periodísticas de la zona y de medidas de contención urbana. No reemplazan una inspección presencial actual, un relevamiento topográfico ni un inventario oficial de dispositivos de seguridad.")

    pic1, pic2 = st.columns(2, gap="large")
    with pic1:
        st.image(
            "https://storage.lacapitalmdp.com/2017/06/Alberti-La-Costa-1024x681.jpg",
            caption="Referencia del entorno de Alberti y la costa. Fuente periodística: La Capital. Imagen de archivo; no certifica condiciones actuales.",
            use_container_width=True,
        )
        st.markdown(f"[Abrir artículo y referencia visual ↗]({URL_FOTO_ALBERTI})")
    with pic2:
        st.image(
            "https://pxcdn.0223.com.ar/f/092018/1536333821808.webp?ch=780&cw=1280&extw=jpg",
            caption="Pilotes de contención informados para el sector Alberti–costa. Fuente periodística: 0223, 07-09-2018.",
            use_container_width=True,
        )
        st.markdown(f"[Abrir artículo y referencia visual ↗]({URL_FOTO_PILOTES})")

    st.markdown("#### Matriz propuesta para el relevamiento de campo")
    inspection = pd.DataFrame(
        [
            {"Variable": "Radio y transición de curva", "Método": "Levantamiento geométrico validado", "Registro esperado": "Radio en m, croquis y puntos de control"},
            {"Variable": "Peralte y pendiente transversal", "Método": "Nivelación o levantamiento topográfico", "Registro esperado": "Sección transversal y porcentaje"},
            {"Variable": "Velocidad operativa", "Método": "Medición de velocidades por franja horaria", "Registro esperado": "Distribución, V50 y V85 con protocolo"},
            {"Variable": "Fricción y textura", "Método": "Ensayo instrumental o método técnico documentado", "Registro esperado": "Coeficiente, método, equipo y clima"},
            {"Variable": "Agua y drenaje", "Método": "Inspección bajo lluvia y poslluvia", "Registro esperado": "Acumulaciones, desagües y fotografías"},
            {"Variable": "Contención y borde costero", "Método": "Inspección de barreras, bordillos y continuidad", "Registro esperado": "Estado, dimensiones y discontinuidades"},
            {"Variable": "Señalización e iluminación", "Método": "Auditoría diurna y nocturna", "Registro esperado": "Visibilidad, estado y ubicación"},
        ]
    )
    st.dataframe(inspection, use_container_width=True, hide_index=True)
    st.caption("La matriz enumera variables a medir; no afirma que la curva presente actualmente deficiencias específicas sin inspección de campo.")

# ----------------------------------------------------------------------------
# 6. Fuentes limitadas al área de estudio
# ----------------------------------------------------------------------------
with tab_fuentes:
    st.markdown('<div class="section-kicker">06 / Trazabilidad y límites</div>', unsafe_allow_html=True)
    st.subheader("Fuentes que describen la curva de Gascón o su entorno inmediato")
    sources = pd.DataFrame(
        [
            {"Fecha del hecho o referencia": "15-08-2021", "Fuente": "Página/12", "Aporte": "Relato de pérdida de control y caída hacia las rocas en la curva de Gascón.", "Enlace": URL_EVENTO_AGO_2021},
            {"Fecha del documento": "2021", "Fuente": "Honorable Concejo Deliberante de General Pueyrredon", "Aporte": "Expediente que menciona el despiste del 15-08-2021 en Boulevard Marítimo y Gascón.", "Enlace": URL_EXPEDIENTE_HCD},
            {"Fecha del hecho": "23-09-2021", "Fuente": "Punto Noticias", "Aporte": "Relato de pérdida de control en la curva costera a la altura de Gascón y mención de calzada mojada.", "Enlace": URL_EVENTO_SEP_2021},
            {"Fecha de publicación": "12-07-2019", "Fuente": "La Capital", "Aporte": "Referencia de contexto al cruce de Alberti y la costa y antecedentes de intervención vial.", "Enlace": URL_FOTO_ALBERTI},
            {"Fecha de publicación": "07-09-2018", "Fuente": "0223", "Aporte": "Referencia visual de pilotes y medidas de contención en el sector Alberti–costa.", "Enlace": URL_FOTO_PILOTES},
        ]
    )
    st.dataframe(sources, use_container_width=True, hide_index=True, column_config={"Enlace": st.column_config.LinkColumn("Documento", display_text="Abrir fuente")})

    st.markdown("#### Criterios metodológicos")
    st.markdown(
        """
        1. **Área estricta:** no se incorporan indicadores provinciales ni cifras del partido como si describieran la curva de estudio.
        2. **Registro no exhaustivo:** los dos casos son eventos hallados en publicaciones, no el número total de siniestros de la zona.
        3. **Fechas normalizadas:** las fechas visibles se presentan como DD-MM-AAAA. El formato no cambia la precisión ni el alcance de las fuentes originales.
        4. **No atribuir causalidad sin evidencia:** la mención de lluvia o de pérdida de control no basta por sí sola para establecer la causa técnica del siniestro.
        5. **Modelo educativo:** los resultados dependen de valores de entrada y simplificaciones; no sustituyen un estudio de seguridad vial, una pericia ni un dictamen de velocidad segura.
        """
    )
    st.caption("Las fotografías y los registros dependen de la disponibilidad en línea de las fuentes originales. Fecha de ejecución de la página: " + FECHA_CONSULTA + ".")

st.markdown("---")
st.caption("Análisis local de pérdida de control · complemento independiente v2 · sin carga de archivos externos")
