import streamlit as st
import numpy_financial as npf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header [data-testid="stToolbar"] {visibility: hidden;}
    [data-testid="github-badge"] {display: none !important;}
    .viewerBadge_link__ {display: none !important;}
    .viewerBadge_container__ {display: none !important;}
    footer {visibility: hidden;}
    </style>
"""
import streamlit as st
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Set Streamlit page configuration
st.set_page_config(page_title="Alquiler vs Compra", layout="centered")

st.markdown("""
<style>
.big-text {font-size: 1.3em;}
.step-header {font-size: 1.5em; font-weight: bold; color: #4CAF50;}
.summary-box {border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; background-color: #f9f9f9;}
.label {font-weight: bold;}
.value {color: #2E86C1;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Análisis Interactivo: Alquiler vs Compra")

# Estado inicial de pasos
if "step" not in st.session_state:
    st.session_state.step = 1

# Barra de progreso visual mejorada
total_steps = 4
step_labels = ["Inicio", "Compra", "Alquiler", "Confirmación", "Resultados"]
progress_value = (st.session_state.step - 1) / total_steps
st.markdown(f"""
<div style='width: 100%; display: flex; justify-content: space-between; margin-bottom:10px;'>
    {''.join([f"<div style='flex:1; text-align:center; font-weight:bold; {'color:#4CAF50;' if i+1 <= st.session_state.step else 'color:#ccc;'}'>{i+1}. {label}</div>" for i, label in enumerate(step_labels[:-1])])}
</div>
<div style='height: 15px; background: #ddd; border-radius: 7px; overflow: hidden;'>
  <div style='height: 100%; width: {progress_value*100}%; background: #4CAF50;'></div>
</div>
""", unsafe_allow_html=True)

# Paso seguro para ir adelante o atrás
def cambiar_paso(siguiente):
    st.session_state.step = siguiente
    st.rerun()

# Paso 1: Introducción
if st.session_state.step == 1:
    st.markdown("<div class='step-header'>👋 Bienvenido</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-text'>Esta herramienta te ayudará a comparar si te conviene más comprar o alquilar una vivienda según tus datos. Te guiaremos paso a paso para que configures las variables.</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-text'>👉 <i>Ejemplo: Si estás considerando una vivienda de 250.000€ y actualmente pagas un alquiler de 800€, introduce esos valores cuando se te pidan.</i></div>", unsafe_allow_html=True)
    if st.button("👉 Empezar encuesta", key="start"):
        cambiar_paso(2)

# Paso 2: Variables de Compra
elif st.session_state.step == 2:
    st.markdown("<div class='step-header'>🏠 Paso 1 de 3: Datos de Compra</div>", unsafe_allow_html=True)
    st.markdown("<div class='big-text'>💡 Consejo: El precio de la vivienda incluye todos los gastos asociados como reformas y muebles iniciales.</div>", unsafe_allow_html=True)

    precio_vivienda = st.number_input("💰 Precio de la vivienda (€)", 50000, 1000000, 250000, step=10000, help="Precio total de la vivienda que deseas comprar.")
    entrada_pct = st.slider("Entrada (%)", 0, 50, 20, help="Porcentaje del precio total que pagarás como entrada.")
    gastos_compra_pct = st.slider("Gastos de compra (%)", 0, 15, 10, help="Costes adicionales como notaría, impuestos, registro.")
    tipo_interes_hipoteca = st.number_input("Interés hipoteca (%)", 0.1, 10.0, 2.5, help="Tipo de interés anual de la hipoteca.")
    plazo_hipoteca = st.slider("Plazo hipoteca (años)", 5, 40, 25, help="Duración de la hipoteca en años.")
    revalorizacion_vivienda_pct = st.number_input("Revalorización vivienda anual (%)", -5.0, 15.0, 5.5, help="Aumento esperado en el valor de la vivienda por año.")

    gasto_propietario_pct = st.number_input("Gastos propietario anuales (% valor vivienda)", 0.0, 5.0, 1.5, help="Mantenimiento, comunidad, IBI, etc.")

    incluir_seguro_hogar = st.checkbox("Incluir seguro de hogar", value=True)
    if incluir_seguro_hogar:
        seguro_hogar_eur = st.number_input("Seguro hogar anual fijo (€)", 0, 5000, 0, step=50, help="Coste anual del seguro del hogar.")
    else:
        seguro_hogar_eur = 0.0

    incluir_seguro_vida = st.checkbox("Incluir seguro de vida", value=True)
    if incluir_seguro_vida:
        seguro_vida_eur = st.number_input("Seguro vida anual fijo (€)", 0, 5000, 0, step=50, help="Coste anual del seguro de vida.")
    else:
        seguro_vida_eur = 0.0

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Volver", key="compra_back"):
        cambiar_paso(1)
    if col2.button("Siguiente ➡️", key="compra_next"):
        st.session_state.compra = {
            "precio_vivienda": precio_vivienda,
            "entrada_pct": entrada_pct,
            "gastos_compra_pct": gastos_compra_pct,
            "tipo_interes_hipoteca": tipo_interes_hipoteca,
            "plazo_hipoteca": plazo_hipoteca,
            "revalorizacion_vivienda_pct": revalorizacion_vivienda_pct,
            "gasto_propietario_pct": gasto_propietario_pct,
            "seguro_hogar_eur": seguro_hogar_eur,
            "seguro_vida_eur": seguro_vida_eur
        }
        cambiar_paso(3)

# Paso 3: Variables de Alquiler
elif st.session_state.step == 3:
    st.markdown("<div class='step-header'>🏡 Paso 2 de 3: Datos de Alquiler</div>", unsafe_allow_html=True)
    alquiler_inicial = st.number_input("💸 Alquiler mensual actual (€)", 300, 5000, 800, step=50, help="Cuánto pagas de alquiler actualmente.")
    subida_alquiler_anual_pct = st.number_input("Subida anual alquiler (%)", 0.0, 10.0, 2.0, help="Porcentaje esperado de incremento anual del alquiler.")
    rentabilidad_inversion_pct = st.number_input("Rentabilidad inversión anual (%)", 0.0, 20.0, 12.0, help="Rentabilidad media de invertir el dinero ahorrado.")

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Volver", key="alquiler_back"):
        cambiar_paso(2)
    if col2.button("Siguiente ➡️", key="alquiler_next"):
        st.session_state.alquiler = {
            "alquiler_inicial": alquiler_inicial,
            "subida_alquiler_anual_pct": subida_alquiler_anual_pct,
            "rentabilidad_inversion_pct": rentabilidad_inversion_pct
        }
        cambiar_paso(4)

# Paso 4: Confirmación con resumen visual
elif st.session_state.step == 4:
    st.markdown("<div class='step-header'>📋 Resumen y Confirmación</div>", unsafe_allow_html=True)
    st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>🏠 Datos de Compra:</div>", unsafe_allow_html=True)
    compra_labels = {
        "precio_vivienda": "Precio vivienda (€)",
        "entrada_pct": "Entrada (%)",
        "gastos_compra_pct": "Gastos compra (%)",
        "tipo_interes_hipoteca": "Interés hipoteca (%)",
        "plazo_hipoteca": "Plazo hipoteca (años)",
        "revalorizacion_vivienda_pct": "Revalorización vivienda anual (%)",
        "gasto_propietario_pct": "Gastos propietario anuales (%)",
        "seguro_hogar_eur": "Seguro hogar anual (€)",
        "seguro_vida_eur": "Seguro vida anual (€)"
    }
    for key, label in compra_labels.items():
        value = st.session_state.compra.get(key, "-")
        st.markdown(f"<div class='big-text'><span class='label'>{label}:</span> <span class='value'>{value}</span></div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='label'>🏡 Datos de Alquiler:</div>", unsafe_allow_html=True)
    alquiler_labels = {
        "alquiler_inicial": "Alquiler mensual (€)",
        "subida_alquiler_anual_pct": "Subida anual alquiler (%)",
        "rentabilidad_inversion_pct": "Rentabilidad inversión anual (%)"
    }
    for key, label in alquiler_labels.items():
        value = st.session_state.alquiler.get(key, "-")
        st.markdown(f"<div class='big-text'><span class='label'>{label}:</span> <span class='value'>{value}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='big-text'>Si quieres cambiar algo, usa los botones para volver atrás.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Volver", key="confirm_back"):
        cambiar_paso(3)
    if col2.button("✅ Confirmar y Ver resultados", key="confirm_next"):
        cambiar_paso(5)

# Paso 5: Mostrar herramienta interactiva
elif st.session_state.step == 5:
    st.success("✅ Datos completados. Ahora puedes ajustar variables y ver resultados interactivos.")

    # Cargar variables desde la sesión
    c = st.session_state.compra
    a = st.session_state.alquiler

    # Permitir modificar los datos directamente en esta pantalla
    with st.expander("🔧 Editar datos de compra"):
        c['precio_vivienda'] = st.number_input(
            "💰 Precio de la vivienda (€)",
            50000,
            1000000,
            c.get('precio_vivienda', 250000),
            step=10000,
            key="res_precio_vivienda",
        )
        c['entrada_pct'] = st.slider(
            "Entrada (%)", 0, 50, c.get('entrada_pct', 20), key="res_entrada_pct"
        )
        c['gastos_compra_pct'] = st.slider(
            "Gastos de compra (%)",
            0,
            15,
            c.get('gastos_compra_pct', 10),
            key="res_gastos_compra_pct",
        )
        c['tipo_interes_hipoteca'] = st.number_input(
            "Interés hipoteca (%)",
            0.1,
            10.0,
            c.get('tipo_interes_hipoteca', 2.5),
            key="res_tipo_interes_hipoteca",
        )
        c['plazo_hipoteca'] = st.slider(
            "Plazo hipoteca (años)",
            5,
            40,
            c.get('plazo_hipoteca', 25),
            key="res_plazo_hipoteca",
        )
        c['revalorizacion_vivienda_pct'] = st.number_input(
            "Revalorización vivienda anual (%)",
            -5.0,
            15.0,
            c.get('revalorizacion_vivienda_pct', 5.5),
            key="res_revalorizacion_vivienda_pct",
        )
        c['gasto_propietario_pct'] = st.number_input(
            "Gastos propietario anuales (% valor vivienda)",
            0.0,
            5.0,
            c.get('gasto_propietario_pct', 1.5),
            key="res_gasto_propietario_pct",
        )
        incluir_seguro_hogar = st.checkbox(
            "Incluir seguro de hogar",
            value=c.get('seguro_hogar_eur', 0.0) > 0,
            key="res_incluir_seguro_hogar",
        )
        if incluir_seguro_hogar:
            c['seguro_hogar_eur'] = st.number_input(
                "Seguro hogar anual fijo (€)",
                0,
                5000,
                c.get('seguro_hogar_eur', 0.0),
                step=50,
                key="res_seguro_hogar_eur",
            )
        else:
            c['seguro_hogar_eur'] = 0.0

        incluir_seguro_vida = st.checkbox(
            "Incluir seguro de vida",
            value=c.get('seguro_vida_eur', 0.0) > 0,
            key="res_incluir_seguro_vida",
        )
        if incluir_seguro_vida:
            c['seguro_vida_eur'] = st.number_input(
                "Seguro vida anual fijo (€)",
                0,
                5000,
                c.get('seguro_vida_eur', 0.0),
                step=50,
                key="res_seguro_vida_eur",
            )
        else:
            c['seguro_vida_eur'] = 0.0

    with st.expander("🔧 Editar datos de alquiler"):
        a['alquiler_inicial'] = st.number_input(
            "💸 Alquiler mensual actual (€)",
            300,
            5000,
            a.get('alquiler_inicial', 800),
            step=50,
            key="res_alquiler_inicial",
        )
        a['subida_alquiler_anual_pct'] = st.number_input(
            "Subida anual alquiler (%)",
            0.0,
            10.0,
            a.get('subida_alquiler_anual_pct', 2.0),
            key="res_subida_alquiler_anual_pct",
        )
        a['rentabilidad_inversion_pct'] = st.number_input(
            "Rentabilidad inversión anual (%)",
            0.0,
            20.0,
            a.get('rentabilidad_inversion_pct', 12.0),
            key="res_rentabilidad_inversion_pct",
        )

    # Guardar cambios
    st.session_state.compra = c
    st.session_state.alquiler = a

    # Variables actualizadas
    precio_vivienda = c['precio_vivienda']
    entrada_pct = c['entrada_pct']
    gastos_compra_pct = c['gastos_compra_pct']
    tipo_interes_hipoteca = c['tipo_interes_hipoteca']
    plazo_hipoteca = c['plazo_hipoteca']
    revalorizacion_vivienda_pct = c['revalorizacion_vivienda_pct']

    alquiler_inicial = a['alquiler_inicial']
    subida_alquiler_anual_pct = a['subida_alquiler_anual_pct']
    rentabilidad_inversion_pct = a['rentabilidad_inversion_pct']

    horizonte_anios = c.get('plazo_hipoteca', 25)
    gasto_propietario_pct = c.get('gasto_propietario_pct', 0.0)
    seguro_hogar_pct = 0.0
    seguro_hogar_eur = c.get('seguro_hogar_eur', 0.0)
    seguro_vida_pct = 0.0
    seguro_vida_eur = c.get('seguro_vida_eur', 0.0)

    # --- Cálculos ---
    entrada = precio_vivienda * entrada_pct / 100
    gastos_compra = precio_vivienda * gastos_compra_pct / 100
    capital_financiado = precio_vivienda * (100 - entrada_pct) / 100

    tipo_mensual = tipo_interes_hipoteca / 100 / 12
    n_meses = plazo_hipoteca * 12
    cuota_mensual = npf.pmt(tipo_mensual, n_meses, -capital_financiado)

    anios = list(range(1, horizonte_anios + 1))
    valor_vivienda = []
    deuda_pendiente = []
    patrimonio_compra = []
    inversion_alquiler = []
    coste_compra_acumulado = []
    coste_alquiler_acumulado = []

    inversion_inquilino = entrada + gastos_compra

    for year in anios:
        valor_actual_vivienda = precio_vivienda * (1 + revalorizacion_vivienda_pct / 100) ** year
        valor_vivienda.append(valor_actual_vivienda)
        amortizacion = min(1.0, year / plazo_hipoteca)
        deuda_actual = capital_financiado * (1 - amortizacion)
        deuda_pendiente.append(deuda_actual)
        patrimonio_actual = valor_actual_vivienda - deuda_actual
        patrimonio_compra.append(patrimonio_actual)

        inversion_inquilino *= (1 + rentabilidad_inversion_pct / 100)
        inversion_inquilino += (precio_vivienda * gasto_propietario_pct / 100 +
                                precio_vivienda * seguro_hogar_pct / 100 +
                                deuda_actual * seguro_vida_pct / 100 +
                                seguro_hogar_eur + seguro_vida_eur)
        inversion_alquiler.append(inversion_inquilino)

        coste_c = entrada + gastos_compra + cuota_mensual * 12 * min(year, plazo_hipoteca)
        coste_c += precio_vivienda * gasto_propietario_pct / 100 * year
        coste_c += (precio_vivienda * seguro_hogar_pct / 100 + seguro_hogar_eur) * year
        coste_c += (capital_financiado * seguro_vida_pct / 100 + seguro_vida_eur) * min(year, plazo_hipoteca)
        coste_compra_acumulado.append(coste_c)

        coste_a = sum(alquiler_inicial * (1 + subida_alquiler_anual_pct / 100) ** y * 12 for y in range(year))
        coste_alquiler_acumulado.append(coste_a)

    col1, col2 = st.columns(2)
    col1.metric("🏠 Patrimonio compra final (€)", f"{patrimonio_compra[-1]:,.0f}")
    col2.metric("🏡 Patrimonio alquiler final (€)", f"{inversion_alquiler[-1]:,.0f}")

    st.subheader("📈 Evolución del patrimonio")
    fig, ax = plt.subplots()
    ax.plot(anios, patrimonio_compra, label="Compra")
    ax.plot(anios, inversion_alquiler, label="Alquilar e invertir")
    ax.set_xlabel("Años")
    ax.set_ylabel("Patrimonio (€)")
    ax.legend()
    st.pyplot(fig)

    st.subheader("💸 Coste acumulado")
    fig2, ax2 = plt.subplots()
    ax2.plot(anios, coste_compra_acumulado, label="Coste Compra")
    ax2.plot(anios, coste_alquiler_acumulado, label="Coste Alquiler")
    ax2.set_xlabel("Años")
    ax2.set_ylabel("Coste acumulado (€)")
    ax2.legend()
    st.pyplot(fig2)

    df_resultados = pd.DataFrame({
        "Año": anios,
        "Valor Vivienda (€)": valor_vivienda,
        "Deuda Pendiente (€)": deuda_pendiente,
        "Patrimonio Compra (€)": patrimonio_compra,
        "Inversión Alquiler (€)": inversion_alquiler,
        "Coste Compra (€)": coste_compra_acumulado,
        "Coste Alquiler (€)": coste_alquiler_acumulado
    })

    st.download_button("📥 Descargar resultados como CSV", df_resultados.to_csv(index=False), "alquiler_vs_compra_resultados.csv", "text/csv")
