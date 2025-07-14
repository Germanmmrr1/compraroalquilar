import streamlit as st
import numpy_financial as npf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

st.markdown("""
    <style>
    /* Oculta los anchor-link de los encabezados */
    h1 > a.anchor-link, h2 > a.anchor-link, h3 > a.anchor-link {
        display: none !important;
    }
    /* Streamlit v1.25+ usa esta clase: */
    .stMarkdown .css-1wvsk4q {
        display: none !important;
    }
    /* Algunos temas usan: */
    a[href^="#"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    .stButton > button {
        font-size: 1.25em !important;
        font-weight: bold;
        padding: 0.7em 2.8em !important;
        border-radius: 1.3em;
        background-color: #19A974 !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        min-width: 240px;
        max-width: 350px;
        width: 100%;
        white-space: nowrap;
        text-align: center;
        margin-top: 1.2em;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background-color: #146953 !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)


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

st.title("¿Comprar o alquilar casa?")

# Estado inicial de pasos
if "step" not in st.session_state:
    st.session_state.step = 1

# Barra de progreso visual mejorada
total_steps = 5
step_labels = ["Inicio", "Compra", "Alquiler", "Horizonte", "Revisión", "Resultados"]
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
    st.markdown(
        """
        <div class='big-text'>
        <b>Compara el coste total de comprar frente a alquilar</b> teniendo en cuenta precio, revalorización, gastos, impuestos y más.
        </div>
        <ul style='font-size: 1.3em; line-height: 1.7; margin-top: 20px;'>
            <li>📊 <b>Simula distintos escenarios</b> y visualiza cuál opción te conviene más.</li>
            <li>🛠️ <b>Ajusta los valores</b> según tu situación real.</li>
            <li>💡 <b>Toma la mejor decisión financiera</b> en segundos, gratis.</li>
        </ul>
        """, unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 ¡Empieza el análisis!", key="start"):
            cambiar_paso(2)

# Paso 2: Variables de Compra
elif st.session_state.step == 2:
    st.markdown("<div class='step-header'>🏠 Paso 1 de 4: Datos de Compra</div>", unsafe_allow_html=True)
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
        seguro_hogar_eur = st.number_input("Seguro hogar anual fijo (€)", 0.0, 5000.0, 0.0, step=50.0, help="Coste anual del seguro del hogar.")
    else:
        seguro_hogar_eur = 0.0

    incluir_seguro_vida = st.checkbox("Incluir seguro de vida", value=True)
    if incluir_seguro_vida:
        seguro_vida_eur = st.number_input("Seguro vida anual fijo (€)", 0.0, 5000.0, 0.0, step=50.0, help="Coste anual del seguro de vida.")
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
    st.markdown("<div class='step-header'>🏡 Paso 2 de 4: Datos de Alquiler</div>", unsafe_allow_html=True)
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

# Paso 4: Horizonte de comparación
elif st.session_state.step == 4:
    st.markdown("<div class='step-header'>⏳ Paso 3 de 4: Horizonte de comparación</div>", unsafe_allow_html=True)
    horizonte = st.number_input(
        "Horizonte de comparación (años)",
        1,
        50,
        st.session_state.get('horizonte', 25),
        step=1,
    )
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Volver", key="horizonte_back"):
        cambiar_paso(3)
    if col2.button("Siguiente ➡️", key="horizonte_next"):
        st.session_state.horizonte = horizonte
        cambiar_paso(5)

# Paso 5: Confirmación con resumen visual
elif st.session_state.step == 5:
    st.markdown("<div class='step-header'>📋 Paso 4 de 4: Resumen y Confirmación</div>", unsafe_allow_html=True)
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
        st.markdown(
            f"<div class='big-text'><span class='label'>{label}:</span> <span class='value'>{value}</span></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='big-text'><span class='label'>⏳ Horizonte de comparación (años):</span> <span class='value'>{st.session_state.get('horizonte', 25)}</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='big-text'>Si quieres cambiar algo, usa los botones para volver atrás.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Volver", key="confirm_back"):
        cambiar_paso(4)
    if col2.button("✅ Confirmar y Ver resultados", key="confirm_next"):
        cambiar_paso(6)

# Paso 6: Mostrar herramienta interactiva
elif st.session_state.step == 6:
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
@@ -243,117 +269,127 @@ elif st.session_state.step == 5:
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
                0.0,
                5000.0,
                c.get('seguro_hogar_eur', 0.0),
                step=50.0,
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
                0.0,
                5000.0,
                c.get('seguro_vida_eur', 0.0),
                step=50.0,
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

    with st.expander("🔧 Editar horizonte de comparación"):
        st.session_state.horizonte = st.number_input(
            "Horizonte de comparación (años)",
            1,
            50,
            st.session_state.get('horizonte', horizonte_anios),
            step=1,
            key="res_horizonte_anios",
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

    horizonte_anios = st.session_state.get('horizonte', c.get('plazo_hipoteca', 25))
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
