import math
import streamlit as st

# Configuración inicial de la página web
st.set_page_config(
    page_title="Simulador de Curva - Blvd. Marítimo",
    page_icon="🚗",
    layout="wide",
)

# Parámetros fijos del escenario
RADIO_CURVA = 60.0  # m (curva Alberti - Gascón)
GRAVEDAD = 9.81  # m/s²
MU_E_MIN = 0.4
MU_E_MAX = 0.6
FACTOR_DINAMICO = 0.75  # mu_c = mu_e * 0.75


# Funciones de cálculo físico
def kmh_a_ms(v_kmh):
  return v_kmh / 3.6


def calcular_fuerza_centrifuga(masa, v_ms, radio):
  return masa * v_ms**2 / radio


def calcular_roce_estatico_max(mu_e, masa, g):
  return mu_e * masa * g


def calcular_roce_dinamico(mu_c, masa, g):
  return mu_c * masa * g


def calcular_velocidad_limite(mu_e, g, radio):
  return math.sqrt(mu_e * g * radio)


# -----------------------------------------------------------------------------
# BARRA LATERAL (ENTRADAS Y NAVEGACIÓN)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Parámetros de Simulación")
st.sidebar.markdown("**Ubicación:** Blvd. Marítimo (Alberti a Gascón)")
st.sidebar.markdown(f"**Radio fijo (R):** {RADIO_CURVA:.1f} m")
st.sidebar.markdown(f"**Gravedad (g):** {GRAVEDAD} m/s²")

st.sidebar.markdown("---")

# Controles interactivos (reemplazan los input de consola)
masa = st.sidebar.number_input(
    "Masa del auto (kg)",
    min_value=100.0,
    max_value=5000.0,
    value=1200.0,
    step=50.0,
)
v_kmh = st.sidebar.number_input(
    "Velocidad de circulación (km/h)",
    min_value=1.0,
    max_value=200.0,
    value=60.0,
    step=5.0,
)
mu_e = st.sidebar.slider(
    "Coeficiente de rozamiento estático (mu_e)",
    min_value=MU_E_MIN,
    max_value=MU_E_MAX,
    value=0.5,
    step=0.01,
    help="0.4: Húmedo / gastado | 0.6: Seco estándar",
)

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegación", ["Simular paso por la curva", "Marco teórico"]
)

# -----------------------------------------------------------------------------
# CUERPO PRINCIPAL DE LA APLICACIÓN
# -----------------------------------------------------------------------------
if menu == "Simular paso por la curva":
  st.title("🚗 Simulador de Estabilidad en Curva")
  st.markdown(
      "Modelo dinámico para analizar si un vehículo logra superar la curva sin"
      " derrapar."
  )

  # Cálculos internos
  v_ms = kmh_a_ms(v_kmh)
  fc = calcular_fuerza_centrifuga(masa, v_ms, RADIO_CURVA)
  fr_max = calcular_roce_estatico_max(mu_e, masa, GRAVEDAD)
  mu_c = mu_e * FACTOR_DINAMICO
  fr_din = calcular_roce_dinamico(mu_c, masa, GRAVEDAD)
  v_lim_ms = calcular_velocidad_limite(mu_e, GRAVEDAD, RADIO_CURVA)
  v_lim_kmh = v_lim_ms * 3.6

  # Tarjetas métricas visuales superiores
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Fuerza Centrífuga (Fc)", f"{fc:,.1f} N")
  col2.metric("Roce Estático Máx (Fr_max)", f"{fr_max:,.1f} N")
  col3.metric("Velocidad Límite", f"{v_lim_kmh:.1f} km/h")
  col4.metric("Velocidad Actual", f"{v_kmh:.1f} km/h")

  st.markdown("---")

  # Criterio de estabilidad con alertas visuales de Streamlit
  if fc <= fr_max:
    margen = fr_max - fc
    margen_pct = margen / fr_max * 100
    st.success(
        "### 🎉 ¡CURVA SUPERADA CON ÉXITO!\nEl auto transitó de forma segura y"
        " estable."
    )

    col_a, col_b = st.columns(2)
    with col_a:
      st.markdown(f"**Fuerza de roce utilizada (= Fc):** `{fc:,.1f} N`")
      st.markdown(f"**Fuerza de roce disponible:** `{fr_max:,.1f} N`")
    with col_b:
      st.markdown(
          f"**Margen de seguridad restante:** `{margen:,.1f} N`"
          f" (`{margen_pct:.1f}%` del agarre disponible)"
      )

    st.info(
        "**Explicación:** El roce estático (reacción del asfalto, 3ª Ley)"
        " alcanzó para proveer la fuerza centrípeta que exige la 2ª Ley. El"
        " neumático rueda sin deslizar y el conductor conserva el control."
    )
  else:
    exceso = fc - fr_max
    st.error(
        "### ⚠️ ¡EL AUTO DERRAPÓ!\nLa fuerza centrífuga superó la fricción"
        " estática máxima."
    )

    col_a, col_b = st.columns(2)
    with col_a:
      st.markdown(f"**Fc necesaria:** `{fc:,.1f} N`")
      st.markdown(f"**Fr_max (estático):** `{fr_max:,.1f} N`")
    with col_b:
      st.markdown(f"**Exceso sobre el límite:** `{exceso:,.1f} N`")

    st.warning("### --- QUÉ PASA DESPUÉS DEL DESLIZAMIENTO ---")
    st.markdown(
        f"- **Caída de agarre:** La fuerza de agarre cayó al roce dinámico: "
        f"`{fr_din:,.1f} N` (antes era `{fr_max:,.1f} N`, una pérdida de "
        f"`{fr_max - fr_din:,.1f} N`).\n"
        f"- **Déficit de fuerza centrípeta:** `Fc - Fr_dinamica = {fc - fr_din:,.1f} N`.\n\n"
        "**Por qué el conductor pierde el control total:**\n"
        "1. Al deslizar, el roce pasa de estático a dinámico, que es menor"
        " (mu_c < mu_e): justo cuando más fuerza se necesita, el piso"
        " entrega menos.\n"
        f"2. La fuerza disponible (`{fr_din:,.0f} N`) es inferior a la"
        f" requerida (`{fc:,.0f} N`): la fuerza neta ya no puede producir la"
        " aceleración centrípeta.\n"
        "3. Por inercia (1ª Ley), el auto tiende a seguir en línea recta"
        " tangente a la curva hacia el exterior.\n"
        "4. Girar más el volante o frenar no ayuda, ya que el mismo roce"
        " limitado se reparte entre frenar y doblar.\n"
        f"5. Recién recuperaría el control si la velocidad baja por debajo de"
        f" `{v_lim_kmh:.1f} km/h`."
    )

elif menu == "Marco teórico":
  st.title("📚 Marco Teórico y Leyes de Newton")
  st.markdown("""
    Este simulador modela el comportamiento dinámico de un vehículo al tomar una curva horizontal sin peralte:
    
    * **Movimiento Circular Uniforme (MCU):** $a_c = v^2 / R$, dirigida permanentemente hacia el centro.
    * **2ª Ley de Newton:** La fuerza centrípeta requerida es $F_c = m \cdot v^2 / R$.
    * **3ª Ley de Newton:** El neumático empuja al asfalto hacia afuera y el asfalto reacciona empujando al neumático hacia adentro mediante la fuerza de rozamiento estático.
    * **1ª Ley de Newton:** Sin una fuerza neta transversal suficiente, el vehículo continúa su marcha en línea recta (inercia).
    * **Límites de Fricción:** 
      - Roce estático máximo: $F_{r\\_max} = \mu_e \cdot m \cdot g$
      - Roce dinámico: $F_{r\\_din} = \mu_c \cdot m \cdot g$ (con $\mu_c = 0.75 \cdot \mu_e$)
    * **Velocidad Límite:** Igualando $F_c = F_{r\\_max}$, se obtiene $v_{max} = \sqrt{\mu_e \cdot g \cdot R}$. **La masa del vehículo se cancela**, por lo que el límite no depende del peso del auto.
    """)