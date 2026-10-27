import math
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Simulador y Teoría - Dinámica Vehicular",
    page_icon="🚗",
    layout="wide",
)

# Parámetros fijos del escenario (Blvd. Marítimo - Mar del Plata)
RADIO_CURVA = 60.0  # metros
GRAVEDAD = 9.81  # m/s²
FACTOR_DINAMICO = 0.75  # mu_c = mu_e * 0.75

# -----------------------------------------------------------------------------
# NAVEGACIÓN PRINCIPAL (Barra lateral)
# -----------------------------------------------------------------------------
st.sidebar.title("🎛️ Panel de Control")
menu_principal = st.sidebar.radio(
    "Selecciona una sección:",
    ["🚗 Simulador Dinámico Interactivo", "📚 Marco Teórico y Fundamentos"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Escenario:** Blvd. Marítimo (Alberti - Gascón)")
st.sidebar.markdown(f"**Radio fijo ($R$):** {RADIO_CURVA} m")
st.sidebar.markdown(f"**Gravedad ($g$):** {GRAVEDAD} m/s²")


# =============================================================================
# SECCIÓN 1: SIMULADOR DINÁMICO INTERACTIVO
# =============================================================================
if menu_principal == "🚗 Simulador Dinámico Interactivo":
  st.title("🏎️ Simulador de Estabilidad en Curva (Sin Peralte)")
  st.markdown(
      "Herramienta analítica para evaluar las fuerzas en juego durante el"
      " tránsito vehicular por una curva horizontal."
  )

  # Controles en la barra lateral específicos para la simulación
  st.sidebar.subheader("Configuración del Vehículo")
  tipo_vehiculo = st.sidebar.selectbox(
      "Categoría",
      [
          "Personalizado",
          "Auto Compacto (City Car - 950 kg)",
          "Sedán / Familiar (1,300 kg)",
          "SUV / Camioneta (1,850 kg)",
      ],
  )

  if tipo_vehiculo == "Personalizado":
    masa = st.sidebar.number_input(
        "Masa del vehículo (kg)",
        min_value=500.0,
        max_value=4000.0,
        value=1200.0,
        step=50.0,
    )
  elif tipo_vehiculo == "Auto Compacto (City Car - 950 kg)":
    masa = 950.0
  elif tipo_vehiculo == "Sedán / Familiar (1,300 kg)":
    masa = 1300.0
  else:
    masa = 1850.0

  st.sidebar.subheader("Condiciones del Asfalto")
  estado_calzada = st.sidebar.selectbox(
      "Estado de la calzada",
      [
          "Seco óptimo (Asfalto rugoso) [mu = 0.60]",
          "Seco estándar [mu = 0.50]",
          "Húmedo / Desgastado [mu = 0.40]",
          "Lluvia intensa / Acuaplaning [mu = 0.30]",
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

  st.sidebar.subheader("Cinemática")
  v_kmh = st.sidebar.slider(
      "Velocidad de circulación ($v$)",
      min_value=10.0,
      max_value=120.0,
      value=55.0,
      step=1.0,
  )

  # Opción avanzada de frenado (Círculo de Fricción)
  with st.sidebar.expander("⚙️ Análisis Avanzado (Frenado en Curva)"):
    aplicar_frenado = st.checkbox("Simular frenado simultáneo")
    if aplicar_frenado:
      deceleracion_g = st.slider(
          "Desaceleración longitudinal ($a_x / g$)", 0.1, 0.8, 0.3, 0.05
      )
    else:
      deceleracion_g = 0.0

  # Cálculos físicos
  v_ms = v_kmh / 3.6
  fc = masa * v_ms**2 / RADIO_CURVA
  fr_max = mu_e * masa * GRAVEDAD
  mu_c = mu_e * FACTOR_DINAMICO
  fr_din = mu_c * masa * GRAVEDAD
  v_lim_ms = math.sqrt(mu_e * GRAVEDAD * RADIO_CURVA)
  v_lim_kmh = v_lim_ms * 3.6

  # Aceleración lateral en ges y Factor de Seguridad
  acel_lat_ms2 = v_ms**2 / RADIO_CURVA
  acel_lat_g = acel_lat_ms2 / GRAVEDAD
  factor_seguridad = fr_max / fc if fc > 0 else 99.9

  # Lógica del Círculo de Fricción
  if aplicar_frenado:
    fuerza_freno = masa * (deceleracion_g * GRAVEDAD)
    fr_lateral_disponible = (
        math.sqrt(max(0.0, fr_max**2 - fuerza_freno**2))
        if fuerza_freno < fr_max
        else 0.0
    )
  else:
    fr_lateral_disponible = fr_max

  # Tarjetas de Métricas Principales
  col1, col2, col3, col4, col5 = st.columns(5)
  col1.metric("Fuerza Centrífuga ($F_c$)", f"{fc:,.1f} N")
  col2.metric("Roce Estático Máx", f"{fr_max:,.1f} N")
  col3.metric("Velocidad Límite", f"{v_lim_kmh:.1f} km/h")
  col4.metric("Factor de Seguridad (FS)", f"{factor_seguridad:.2f}")
  col5.metric("Aceleración Lateral", f"{acel_lat_g:.2f} g")

  st.markdown("---")

  # Diagnóstico de Estabilidad
  estable = fc <= fr_lateral_disponible

  if estable:
    st.success(
        "### ✅ CURVA SUPERADA CON ÉXITO\nEl vehículo mantiene adherencia y"
        " control direccional estable."
    )
    st.markdown(
        f"- **Margen de seguridad:** El sistema cuenta con un reaseguro de"
        f" **{(fr_lateral_disponible - fc):,.1f} N** de adherencia remanente.\n"
        f"- **Sensación física:** La aceleración lateral de `{acel_lat_g:.2f} g`"
        " genera una inclinación moderada perceptible en el habitáculo, sin"
        " compromiso de trayectoria."
    )
  else:
    st.error(
        "### 🚨 PÉRDIDA DE CONTROL / DERRAPE (SPIN-OUT)\nLa demanda de fuerza"
        " centrífuga supera la fricción disponible."
    )
    st.markdown(
        f"- **Déficit de fuerza:** Faltan **{(fc - fr_lateral_disponible):,.1f} N**"
        " de agarre transversal para sostener la trayectoria.\n"
        f"- **Transición a roce dinámico:** Al deslizar, el agarre cae a"
        f" `{fr_din:,.1f} N`, agravando la pérdida de control.\n"
        "- **Consecuencia inercial:** Por la 1ª Ley de Newton, el vehículo"
        " abandona la curva en trayectoria rectilínea tangente hacia el"
        " exterior."
    )

  st.markdown("---")

  # Gráfico de Líneas ($F_c$ vs Velocidad)
  st.subheader("📈 Comportamiento de la Fuerza Centrífuga vs. Velocidad")
  st.markdown(
      "Curva teórica de crecimiento de $F_c$ para un radio de"
      f" `{RADIO_CURVA} m`. La línea marca la transición hacia el derrape."
  )

  velocidades_range = range(10, 131, 2)
  datos_grafico = [
      {
          "Velocidad (km/h)": v,
          "Fuerza Centrífuga (N)": masa * (v / 3.6) ** 2 / RADIO_CURVA,
      }
      for v in velocidades_range
  ]
  df_chart = pd.DataFrame(datos_grafico).set_index("Velocidad (km/h)")
  st.line_chart(df_chart)


# =============================================================================
# SECCIÓN 2: MARCO TEÓRICO (Fundamentos Físicos)
# =============================================================================
elif menu_principal == "📚 Marco Teórico y Fundamentos":
  st.title("📚 Marco Teórico: Dinámica de Vehículos en Curvas")
  st.markdown(
      "Fundamentos físicos, leyes de conservación y modelado matemático"
      " aplicados al tránsito vehicular."
  )

  st.markdown("---")

  st.subheader("1. Movimiento Circular Uniforme (MCU)")
  st.markdown(
      "Cuando un vehículo recorre una curva horizontal de radio constante $R$"
      " a rapidez constante $v$, describe un **MCU**. Aunque la rapidez no"
      " varía, el vector velocidad cambia continuamente de dirección, lo que"
      " implica la existencia de una aceleración dirigida permanentemente hacia"
      " el centro de curvatura: la **Aceleración Centrífuga/Centrípeta**:\n\n"
      "$$a_c = \\frac{v^2}{R}$$"
  )

  st.subheader("2. Leyes de Newton Aplicadas")
  st.markdown(
      "- **1ª Ley (Inercia):** Un cuerpo tiende a mantener su estado de"
      " movimiento rectilíneo uniforme. El vehículo 'quiere' continuar en"
      " línea recta (tangente a la trayectoria); para forzarlo a doblar,"
      " es indispensable una fuerza neta transversal.\n"
      "- **2ª Ley ($F = m \\cdot a$):** La fuerza centrípeta requerida para"
      " mantener el vehículo en la trayectoria circular es:\n\n"
      "  $$F_c = m \\cdot a_c = m \\cdot \\frac{v^2}{R}$$\n\n"
      "- **3ª Ley (Acción y Reacción):** El neumático empuja al asfalto hacia"
      " el exterior de la curva mediante fricción, y el asfalto reacciona"
      " empujando al neumático hacia el centro. Esa fuerza de reacción es el"
      " **rozamiento estático**."
  )

  st.subheader("3. Modelado del Rozamiento")
  st.markdown(
      "- **Roce Estático Máximo ($F_{r\\_max}$):** Ocurre mientras el"
      " neumático rueda sin deslizar sobre el pavimento.\n\n"
      "  $$F_{r\\_max} = \\mu_e \\cdot N = \\mu_e \\cdot m \\cdot g$$\n\n"
      "- **Roce Dinámico ($F_{r\\_din}$):** Si se supera el límite estático,"
      " el neumático comienza a deslizar y el coeficiente cae abruptamente"
      " (por enunciado, $\\mu_c = 0.75 \\cdot \\mu_e$), reduciendo drásticamente"
      " la capacidad de control."
  )

  st.subheader("4. Deducción de la Velocidad Límite")
  st.markdown(
      "Igualando la demanda de fuerza centrífuga con la capacidad de agarre"
      " máximo ($F_c = F_{r\\_max}$):\n\n"
      "$$\\frac{m \\cdot v^2}{R} = \\mu_e \\cdot m \\cdot g$$\n\n"
      "Notar que **la masa ($m$) se cancela en ambos miembros**. Esto demuestra"
      " un principio físico fundamental: **el límite de velocidad en una curva"
      " no depende del peso del vehículo**, sino exclusivamente del radio de la"
      " curva, la gravedad y el coeficiente de rozamiento:\n\n"
      "$$v_{max} = \\sqrt{\\mu_e \\cdot g \\cdot R}$$"
  )

  st.subheader("5. Círculo de Fricción (Circulo de Kamm.)")
  st.markdown(
      "La adherencia máxima de un neumático es un vector limitado en un círculo"
      " de radio $\\mu \\cdot N$. Si el conductor acciona los frenos mientras"
      " dobla, una parte de esa capacidad se consume longitudinalmente"
      " (frenado), reduciendo el remanente disponible para la fuerza lateral"
      " de giro. Es la razón técnica por la cual **frenar bruscamente en plena"
      " curva mojada induce la pérdida de control**."
  )