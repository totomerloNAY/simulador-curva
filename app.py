import math
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Simulador Avanzado - Dinámica Vehicular en Curva",
    page_icon="🏎️",
    layout="wide",
)

# Parámetros fijos del escenario (Blvd. Marítimo - Mar del Plata)
RADIO_CURVA = 60.0  # metros
GRAVEDAD = 9.81  # m/s²
FACTOR_DINAMICO = 0.75  # mu_c = mu_e * 0.75


# -----------------------------------------------------------------------------
# BARRA LATERAL: CONFIGURACIÓN DE ESCENARIO Y VEHÍCULO
# -----------------------------------------------------------------------------
st.sidebar.header("🛠️ Panel de Control de Ingeniería")

st.sidebar.subheader("1. Ubicación y Geometría")
st.sidebar.text(f"📍 Curva: Blvd. Marítimo (Alberti-Gascón)")
st.sidebar.text(f"📏 Radio de curvatura (R): {RADIO_CURVA} m")

st.sidebar.subheader("2. Selección de Vehículo")
tipo_vehiculo = st.sidebar.selectbox(
    "Categoría de vehículo",
    [
        "Personalizado",
        "Auto Compacto (City Car - 950 kg)",
        "Sedán / Familiar (1,300 kg)",
        "SUV / Camioneta (1,850 kg)",
    ],
)

if tipo_vehiculo == "Personalizado":
  masa = st.sidebar.number_input(
      "Masa del vehículo (kg)", min_value=500.0, max_value=4000.0, value=1200.0, step=50.0
  )
elif tipo_vehiculo == "Auto Compacto (City Car - 950 kg)":
  masa = 950.0
elif tipo_vehiculo == "Sedán / Familiar (1,300 kg)":
  masa = 1300.0
else:
  masa = 1850.0

st.sidebar.subheader("3. Condiciones del Asfalto y Neumáticos")
estado_calzada = st.sidebar.selectbox(
    "Estado de la calzada",
    [
        "Seco óptimo (Asfalto rugoso) [mu = 0.60]",
        "Seco estándar [mu = 0.50]",
        "Húmedo / Desgastado [mu = 0.40]",
        "Lluvia intensa / Acuaplaning leve [mu = 0.30]",
    ],
)

if "0.60" in estado_calzada:
  mu_e = 0.60
elif "0.50" in estado_calzada:
  mu_e = 0.50
elif "0.40" in estado_calzada:
  mu_e = 0.40
else:
  mu_e = 0.30

st.sidebar.subheader("4. Cinemática del Movimiento")
v_kmh = st.sidebar.slider(
    "Velocidad de circulación ($v$)", min_value=10.0, max_value=120.0, value=55.0, step=1.0
)

# -----------------------------------------------------------------------------
# PANEL AVANZADO: EFECTO DE FRENADO (CÍRCULO DE FRICCIÓN)
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Análisis Avanzado (Círculo de Fricción)"):
  st.markdown(
      "El **Círculo de Kamm** establece que la fuerza de adherencia total de"
      " un neumático es un límite circular ($F_{max} = \\mu \cdot N$). Si usas"
      " parte de esa adherencia para frenar, el agarre para doblar disminuye."
  )
  aplicar_frenado = st.checkbox(
      "Simular frenado simultáneo en la curva"
  )
  if aplicar_frenado:
    deceleracion_g = st.slider(
        "Desaceleración longitudinal ($a_x / g$)", 0.1, 0.8, 0.3, 0.05
    )
  else:
    deceleracion_g = 0.0

# -----------------------------------------------------------------------------
# CÁLCULOS FÍSICOS PRINCIPALES
# -----------------------------------------------------------------------------
v_ms = v_kmh / 3.6
fc = masa * v_ms**2 / RADIO_CURVA
fr_max = mu_e * masa * GRAVEDAD
mu_c = mu_e * FACTOR_DINAMICO
fr_din = mu_c * masa * GRAVEDAD
v_lim_ms = math.sqrt(mu_e * GRAVEDAD * RADIO_CURVA)
v_lim_kmh = v_lim_ms * 3.6

# Lógica del Círculo de Fricción
if aplicar_frenado:
  fuerza_freno = masa * (deceleracion_g * GRAVEDAD)
  if fuerza_freno >= fr_max:
    fr_lateral_disponible = 0.0
  else:
    fr_lateral_disponible = math.sqrt(
        max(0.0, fr_max**2 - fuerza_freno**2)
    )
else:
  fuerza_freno = 0.0
  fr_lateral_disponible = fr_max

# -----------------------------------------------------------------------------
# CUERPO PRINCIPAL DE LA APLICACIÓN
# -----------------------------------------------------------------------------
st.title("🏎️ Simulador Dinámico de Estabilidad Vehicular")
st.markdown(
    "Modelo analítico de fuerzas aplicado al tránsito vehicular en curvas"
    " horizontales sin peralte."
)

# Tarjetas de Métricas Principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Fuerza Centrífuga ($F_c$)", f"{fc:,.1f} N")
col2.metric(
    "Roce Estático Máx ($F_{r\\_max}$)",
    f"{fr_max:,.1f} N",
    help="Límite absoluto de adherencia lateral",
)
col3.metric("Velocidad Límite Teórica", f"{v_lim_kmh:.1f} km/h")
col4.metric("Velocidad Actual", f"{v_kmh:.1f} km/h")

st.markdown("---")

# -----------------------------------------------------------------------------
# DIAGNÓSTICO DE ESTABILIDAD
# -----------------------------------------------------------------------------
estable = fc <= fr_lateral_disponible

if estable:
  margen = fr_lateral_disponible - fc
  margen_pct = (
      (margen / fr_max * 100) if fr_max > 0 else 0
  )
  st.success(
      "### ✅ CURVA SUPERADA CON ÉXITO\nEl vehículo mantiene adherencia y control"
      " direccional."
  )

  c1, c2 = st.columns(2)
  with c1:
    st.markdown(
        f"**Fuerza lateral requerida ($F_c$):** `{fc:,.1f} N`\n"
        f"**Adherencia lateral efectiva:** `{fr_lateral_disponible:,.1f} N`"
    )
  with c2:
    st.markdown(
        f"**Margen de seguridad restante:** `{margen:,.1f} N` (`{margen_pct:.1f}%`"
        " del límite)"
    )

  if aplicar_frenado:
    st.info(
        f"⚠️ **Nota sobre frenado:** Al aplicar una desaceleración de"
        f" `{deceleracion_g}g`, parte de la fricción se consumió en frenar,"
        f" reduciendo el margen de giro disponible a"
        f" `{fr_lateral_disponible:,.1f} N`."
    )
else:
  exceso = fc - fr_lateral_disponible
  st.error(
      "### 🚨 PÉRDIDA DE CONTROL / DERRAPE (SPIN-OUT)\nLa demanda de fuerza"
      " centrífuga supera la adherencia disponible de los neumáticos."
  )

  c1, c2 = st.columns(2)
  with c1:
    st.markdown(
        f"**Demanda ($F_c$):** `{fc:,.1f} N`\n"
        f"**Capacidad de agarre:** `{fr_lateral_disponible:,.1f} N`"
    )
  with c2:
    st.markdown(f"**Déficit de fuerza:** `{exceso:,.1f} N`")

  st.warning(
      "### 📉 Dinámica posterior al colapso de adherencia:\n"
      f"1. **Transición a Roce Dinámico:** La fricción cae abruptamente a"
      f" `{fr_din:,.1f} N` (pérdida de `{fr_max - fr_din:,.1f} N`).\n"
      "2. **Inercia (1ª Ley de Newton):** El vehículo deja de describir la"
      " trayectoria circular y tiende a escapar tangencialmente hacia el"
      " exterior de la calzada.\n"
      f"3. **Recuperación:** Solo será posible si la velocidad desciende"
      f" nuevamente por debajo de los **{v_lim_kmh:.1f} km/h** y cesan las"
      " fuerzas longitudinales bruscas."
  )

st.markdown("---")

# -----------------------------------------------------------------------------
# GRÁFICO TÉCNICO INTERACTIVO ($F_c$ vs Velocidad)
# -----------------------------------------------------------------------------
st.subheader("📈 Análisis Gráfico: Fuerza Centrífuga vs. Velocidad")
st.markdown(
    "La curva representa cómo crece exponencialmente la fuerza centrífuga"
    " ($F_c$) a medida que aumenta la velocidad para el radio fijo de"
    f" `{RADIO_CURVA} m`. La línea horizontal roja marca el límite estático"
    f" máximo (`{fr_max:,.0f} N`)."
)

# Generar datos para el gráfico
velocidades_range = range(10, 131, 2)
datos_grafico = []
for v in velocidades_range:
  v_m = v / 3.6
  f_cent = masa * v_m**2 / RADIO_CURVA
  datos_grafico.append({"Velocidad (km/h)": v, "Fuerza Centrífuga (N)": f_cent})

df_chart = pd.DataFrame(datos_grafico).set_index("Velocidad (km/h)")

# Mostrar gráfico de líneas con Streamlit
st.line_chart(df_chart)
st.caption(
    "Nota: El punto donde la línea azul cruza el límite de adherencia de tus"
    " neumáticos representa la velocidad máxima absoluta de diseño."
)