import streamlit as st
import numpy_financial as npf
import pandas as pd
import matplotlib.pyplot as plt
import os


def amortizacion_hipoteca(capital: float, tasa_mensual: float, meses: int,
                          horizonte: int):
    """Devuelve la amortización y la deuda pendiente por año considerando
    capital e intereses."""

    cuota = npf.pmt(tasa_mensual, meses, -capital)

    saldo_capital = capital
    pagos_realizados = 0.0
    deuda_total = cuota * meses

    amort_anual = [0.0]
    deuda_anual = [deuda_total]

    for mes in range(1, min(meses, horizonte * 12) + 1):
        interes = saldo_capital * tasa_mensual
        principal = cuota - interes
        saldo_capital -= principal
        pagos_realizados += cuota
        deuda_total -= cuota
        if mes % 12 == 0:
            amort_anual.append(pagos_realizados)
            deuda_anual.append(max(deuda_total, 0.0))

    while len(amort_anual) < horizonte + 1:
        amort_anual.append(pagos_realizados)
        deuda_anual.append(max(deuda_total, 0.0))

    return amort_anual, deuda_anual


def calcular_resultados(c, a):
    """Realiza todos los cálculos y devuelve un DataFrame y métricas."""
    precio_vivienda = c['precio_vivienda']
    entrada_pct = c['entrada_pct']
    gastos_compra_pct = c['gastos_compra_pct']
    tipo_interes_hipoteca = c['tipo_interes_hipoteca']
    plazo_hipoteca = c['plazo_hipoteca']
    revalorizacion_vivienda_pct = c['revalorizacion_vivienda_pct']
    gasto_propietario_pct = c.get('gasto_propietario_pct', 0.0)
    seguro_hogar_eur = c.get('seguro_hogar_eur', 0.0)
    seguro_vida_eur = c.get('seguro_vida_eur', 0.0)

    alquiler_inicial = a['alquiler_inicial']
    subida_alquiler_anual_pct = a['subida_alquiler_anual_pct']
    rentabilidad_inversion_pct = a['rentabilidad_inversion_pct']
    horizonte_anios = a.get('horizonte_anios', plazo_hipoteca)

    entrada = precio_vivienda * entrada_pct / 100
    gastos_compra = precio_vivienda * gastos_compra_pct / 100
    capital_financiado = precio_vivienda - entrada

    tasa_mensual = tipo_interes_hipoteca / 100 / 12
    meses_totales = plazo_hipoteca * 12
    cuota_mensual = npf.pmt(tasa_mensual, meses_totales, -capital_financiado)
    cuota_anual = cuota_mensual * 12

    amort_acum, deuda_anual = amortizacion_hipoteca(
        capital_financiado, tasa_mensual, meses_totales, horizonte_anios
    )

    gastos_iniciales = 0
    years = [0]
    precio_vivienda_lst = [precio_vivienda]
    gastos_iniciales_lst = [entrada + gastos_compra]
    hipoteca_amortizada_lst = [0.0]
    deuda_pendiente_lst = [capital_financiado]
    gastos_anuales_lst = [0.0]
    gastos_acumulados_lst = [entrada + gastos_compra]
    patrimonio_neto_lst = [-(entrada + gastos_compra)]
    gasto_alquiler_anual_lst = [0.0]
    gasto_alq_acum_lst = [0.0]
    disponible_inv_lst = [entrada + gastos_compra]
    total_invertido_lst = [entrada + gastos_compra]
    inversion_acumulada_lst = [entrada + gastos_compra]
    patrimonio_alq_lst = [entrada + gastos_compra]

    inversion_inquilino = entrada + gastos_compra
    capital_invertido = entrada + gastos_compra
    gasto_acumulado = entrada + gastos_compra
    gasto_alquiler_acum = 0.0

    for year in range(1, horizonte_anios + 1):
        valor_actual_vivienda = precio_vivienda * (1 + revalorizacion_vivienda_pct / 100) ** year
        hipoteca_amortizada = amort_acum[year]
        deuda_actual = deuda_anual[year]
        patrimonio_actual = valor_actual_vivienda - deuda_actual

        gastos_propietario = precio_vivienda * gasto_propietario_pct / 100 + seguro_hogar_eur + seguro_vida_eur
        cuota_ano = cuota_anual if year <= plazo_hipoteca else 0.0
        gasto_acumulado += gastos_propietario + cuota_ano

        alquiler_anual = alquiler_inicial * (1 + subida_alquiler_anual_pct / 100) ** (year - 1) * 12
        gasto_alquiler_acum += alquiler_anual

        aportacion = max(cuota_ano + gastos_propietario - alquiler_anual, 0.0)

        inversion_inquilino *= (1 + rentabilidad_inversion_pct / 100)
        inversion_inquilino += aportacion
        capital_invertido += aportacion

        years.append(year)
        precio_vivienda_lst.append(valor_actual_vivienda)
        gastos_iniciales_lst.append(gastos_iniciales)
        hipoteca_amortizada_lst.append(hipoteca_amortizada)
        deuda_pendiente_lst.append(deuda_actual)
        gastos_anuales_lst.append(gastos_propietario)
        gastos_acumulados_lst.append(gasto_acumulado)
        patrimonio_neto_lst.append(patrimonio_actual)
        gasto_alquiler_anual_lst.append(alquiler_anual)
        gasto_alq_acum_lst.append(gasto_alquiler_acum)
        disponible_inv_lst.append(aportacion)
        total_invertido_lst.append(capital_invertido)
        inversion_acumulada_lst.append(inversion_inquilino)
        patrimonio_alq_lst.append(inversion_inquilino)

    df = pd.DataFrame({
        "Año": years,
        "Precio Vivienda (€)": precio_vivienda_lst,
        "Gastos iniciales (€)": gastos_iniciales_lst,
        "Hipoteca amortizada (€)": hipoteca_amortizada_lst,
        "Deuda Pendiente (€)": deuda_pendiente_lst,
        "Gastos anuales (€)": gastos_anuales_lst,
        "Gastos acumulados (€)": gastos_acumulados_lst,
        "Patrimonio neto compra (€)": patrimonio_neto_lst,
        "Gasto alquiler anual (€)": gasto_alquiler_anual_lst,
        "Gasto alquiler acumulado (€)": gasto_alq_acum_lst,
        "Disponible inversión (€)": disponible_inv_lst,
        "Total invertido (€)": total_invertido_lst,
        "Inversión acumulada (€)": inversion_acumulada_lst,
        "Patrimonio neto alquiler (€)": patrimonio_alq_lst,
    })

    resumen = {
        "desembolso_inicial_compra": entrada + gastos_compra,
        "costes_compra": gasto_acumulado,
        "valor_prop_final": valor_actual_vivienda,
        "hipoteca_pendiente": deuda_actual,
        "patrimonio_neto_final": patrimonio_actual,
        "inversion_inicial_alq": entrada + gastos_compra,
        "costes_alquiler_total": gasto_alquiler_acum,
        "capital_total_invertido": capital_invertido,
        "valor_final_inversion": inversion_inquilino,
        "patrimonio_neto_final_alq": inversion_inquilino,
        "diferencia_patrimonio": inversion_inquilino - patrimonio_actual,
        "diferencia_costes": gasto_alquiler_acum - gasto_acumulado,
        "anios": list(range(1, horizonte_anios + 1)),
        "patrimonio_compra": patrimonio_neto_lst[1:],
        "inversion_alquiler": inversion_acumulada_lst[1:],
        "coste_compra_acumulado": gastos_acumulados_lst[1:],
        "coste_alquiler_acumulado": gasto_alq_acum_lst[1:],
    }

    return resumen, df

st.markdown("""
    <style>
    .center-title {
        text-align: center;
        font-size: 2.7em;
        font-weight: 800;
        margin-bottom: 0.4em;
        margin-top: 0.5em;
    }
    .center-btn {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 2.5em;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

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
total_steps = 4
step_labels = ["Inicio", "Compra", "Alquiler", "Revisión", "Resultados"]
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
    st.markdown("<div class='step-header'>🏠 Paso 1 de 3: Datos de Compra</div>", unsafe_allow_html=True)
    precio_vivienda = st.number_input("💰 Precio de la vivienda (€)", 50000, 1000000, 250000, step=10000, help="El precio de la vivienda incluye todos los gastos asociados como reformas y muebles iniciales.")
    
    # Calcula la entrada en euros después de elegir el porcentaje
    entrada_pct = st.slider("Entrada para la hipoteca (%)", 0, 50, 20, help="Normalmente entre el 20 y el 30%.")
    entrada_eur = precio_vivienda * entrada_pct / 100

    # Badge de entrada en euros
    st.markdown(
        f"""
        <div style='display: inline-block; background: #e3f2fd; color: #1565c0;
                    border-radius: 12px; padding: 0.35em 1.3em; font-size: 1.1em;
                    font-weight: bold; margin-bottom: 0.6em; margin-top: -0.5em;'>
            Entrada: {entrada_eur:,.0f} €
        </div>
        """, unsafe_allow_html=True
    )

    gastos_compra_pct = st.slider(
    "Gastos de compra (%)",
    0, 15, 12,
    help="Incluye costes de:\n"
         "• Notaría (0,2%–0,5%)\n"
         "• Registro (0,1%–0,3%)\n"
         "• Gestoría (300–500 €, tarifa habitual)\n"
         "• Impuestos: 10% IVA (obra nueva) o 6–10% ITP (2ª mano, según CCAA)\n"
         "• Tasación (300–600 €, si hay hipoteca)\n"
         "• Comisión apertura hipoteca (0%–1%)")
    gastos_compra_eur = precio_vivienda * gastos_compra_pct / 100
    st.markdown(
    f"""
    <div style='display: inline-block; background: #e3f2fd; color: #1565c0;
                border-radius: 12px; padding: 0.32em 1.2em; font-size: 1.07em;
                font-weight: bold; margin-bottom: 0.5em; margin-top: -0.2em;'>
        Gastos estimados: {gastos_compra_eur:,.0f} €
    </div>
    """,
    unsafe_allow_html=True)
    tipo_interes_hipoteca = st.number_input("Interés hipoteca (%)", 0.1, 10.0, 2.5, 
                                            help="Tipo de interés anual de la hipoteca. En 2025 está alrededor del 2.5%, puede variar según perfil y banco.")
    plazo_hipoteca = st.slider("Plazo hipoteca (años)", 5, 40, 25, help="Duración de la hipoteca en años, normalmente entre 20 y 30 años.")
    capital_financiado = precio_vivienda - entrada_eur
    tipo_interes_mensual = tipo_interes_hipoteca / 100 / 12
    total_cuotas = plazo_hipoteca * 12
    cuota_mensual_eur = capital_financiado * (tipo_interes_mensual * (1 + tipo_interes_mensual) ** total_cuotas) / ((1 + tipo_interes_mensual) ** total_cuotas - 1)

    st.markdown(
    f"""
    <div style='display: inline-block; background: #e3f2fd; color: #1565c0;
                border-radius: 12px; padding: 0.32em 1.2em; font-size: 1.07em;
                font-weight: bold; margin-bottom: 0.5em; margin-top: -0.2em;'>
        Hipoteca mensual: {cuota_mensual_eur:,.0f} €
    </div>
    """,
    unsafe_allow_html=True)
    
    revalorizacion_vivienda_pct = st.number_input("Revalorización vivienda anual (%)", -5.0, 15.0, 4.5, help="Aumento esperado en el valor de la vivienda por año. Históricamente ha subido entre el 4% y el 5% anual, pero puede variar según zona y mercado.")
    gasto_propietario_pct = st.number_input(
    "Gastos propietario anuales (% valor vivienda)",
    0.0, 5.0, 1.5,
    help="Incluye la suma estimada de:\n"
         "• IBI anual (700 € aprox., suele oscilar entre 0,4% y 1,1% del valor catastral según municipio)\n"
         "• Comunidad (80 €/mes aprox., varía según servicios y tipo de edificio)\n"
         "• Mantenimiento (100 €/mes aprox., pequeñas reparaciones, electrodomésticos, pintura, etc.)\n"
         "• Tasa de basuras (120 €/año aprox., impuesto municipal por recogida de residuos)\n"
         "Puedes ajustar este porcentaje para que refleje el coste real de tu caso.")
    seguro_hogar_eur = st.number_input("Seguro hogar anual fijo (€)", 0, 5000, 400, step=50, help="Coste anual del seguro del hogar. 400€ es el precio medio para coberturas básicas, varía según tamaño y ubicación del inmueble")
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
    alquiler_inicial = st.number_input("💸 Alquiler mensual actual (€)", 300, 5000, 800, step=50, help="Precio de alquiler de propiedades parecidas en la zona.")
    subida_alquiler_anual_pct = st.number_input("Subida anual alquiler (%)", 0.0, 10.0, 2.0, help="Incremento estimado del alquiler cada año, normalmente similar al IPC (Índice de Precios al Consumidor), con valores habituales entre el 2% y el 3%. El aumento se calcula de forma compuesta.")
    rentabilidad_inversion_pct = st.number_input(
    "Rentabilidad inversión anual (%)",
    0.0, 20.0, 10.0,help="Rentabilidad media anual estimada al invertir el dinero ahorrado en fondos o activos globales.\n"
         "Ejemplos históricos:\n"
         "• MSCI World: ~8% anual\n"
         "• S&P 500: ~11% anual\n"
         "• Oro: ~9% anual\n"
         "Puedes ajustar este valor según tu perfil y horizonte de inversión.")
    horizonte_anios = st.slider(
        "Horizonte de análisis (años)", 1, 40, 25, help="Número de años para comparar compra y alquiler.",)

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Volver", key="alquiler_back"):
        cambiar_paso(2)
    if col2.button("Siguiente ➡️", key="alquiler_next"):
        st.session_state.alquiler = {
            "alquiler_inicial": alquiler_inicial,
            "subida_alquiler_anual_pct": subida_alquiler_anual_pct,
            "rentabilidad_inversion_pct": rentabilidad_inversion_pct,
            "horizonte_anios": horizonte_anios,
        }
        cambiar_paso(4)

# Paso 4: Confirmación con resumen visual
elif st.session_state.step == 4:
    st.markdown("<div class='step-header'>📋 Resumen y Confirmación</div>", unsafe_allow_html=True)
    
    # Estilo para las cajas
    st.markdown("""
    <style>
    .summary-box {
        background: #F8FAFB;
        border: 2px solid #2DCC70;
        border-radius: 16px;
        padding: 1.4em 1.6em 1em 1.6em;
        margin-bottom: 2em;
        box-shadow: 0 4px 20px rgba(44,204,112,0.05);
        max-width: 480px;
    }
    .summary-title {
        font-size: 1.32em;
        font-weight: 800;
        color: #2DCC70;
        margin-bottom: 0.8em;
        margin-top: 0.2em;
    }
    .summary-row {
        font-size: 1.08em;
        margin-bottom: 0.28em;
        font-weight: 600;
    }
    .summary-label {
        color: #222;
        font-weight: 600;
    }
    .summary-value {
        color: #1c6cb8;
        font-weight: 700;
        margin-left: 0.2em;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    # --- Caja 1: Compra ---
    with cols[0]:
        st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
        st.markdown("<div class='summary-title'>🏠 Datos de Compra</div>", unsafe_allow_html=True)
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
            st.markdown(
                f"<div class='summary-row'><span class='summary-label'>{label}:</span> <span class='summary-value'>{value}</span></div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Caja 2: Alquiler ---
    with cols[1]:
        st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
        st.markdown("<div class='summary-title'>🏡 Datos de Alquiler</div>", unsafe_allow_html=True)
        alquiler_labels = {
            "alquiler_inicial": "Alquiler mensual (€)",
            "subida_alquiler_anual_pct": "Subida anual alquiler (%)",
            "rentabilidad_inversion_pct": "Rentabilidad inversión anual (%)",
            "horizonte_anios": "Horizonte (años)",
        }
        for key, label in alquiler_labels.items():
            value = st.session_state.alquiler.get(key, "-")
            st.markdown(
                f"<div class='summary-row'><span class='summary-label'>{label}:</span> <span class='summary-value'>{value}</span></div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='big-text' style='margin-top:1em;'>Si quieres cambiar algo, usa los botones para volver atrás.</div>", unsafe_allow_html=True)
    
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
        c['seguro_hogar_eur'] = st.number_input(
                "Seguro hogar anual fijo (€)",
                0.0,
                5000.0,
                float(c.get('seguro_hogar_eur', 0.0)),
                step=50.0,
                key="res_seguro_hogar_eur",
            )
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
                float(c.get('seguro_vida_eur', 0.0)),
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
        a['horizonte_anios'] = st.slider(
            "Horizonte de análisis (años)",
            1,
            40,
            a.get('horizonte_anios', c.get('plazo_hipoteca', 25)),
            key="res_horizonte_anios",
        )

    # Guardar cambios
    st.session_state.compra = c
    st.session_state.alquiler = a

    resumen, df_resultados = calcular_resultados(c, a)

    horizonte_anios = len(resumen["anios"])

    desembolso_inicial_compra = resumen["desembolso_inicial_compra"]
    costes_compra = resumen["costes_compra"]
    valor_prop_final = resumen["valor_prop_final"]
    hipoteca_pendiente = resumen["hipoteca_pendiente"]
    patrimonio_neto_final = resumen["patrimonio_neto_final"]
    inversion_inicial_alq = resumen["inversion_inicial_alq"]
    costes_alquiler_total = resumen["costes_alquiler_total"]
    capital_total_invertido = resumen["capital_total_invertido"]
    valor_final_inversion = resumen["valor_final_inversion"]
    patrimonio_neto_final_alq = resumen["patrimonio_neto_final_alq"]
    diferencia_patrimonio = resumen["diferencia_patrimonio"]
    diferencia_costes = resumen["diferencia_costes"]
    anios = resumen["anios"]
    patrimonio_compra = resumen["patrimonio_compra"]
    inversion_alquiler = resumen["inversion_alquiler"]
    coste_compra_acumulado = resumen["coste_compra_acumulado"]
    coste_alquiler_acumulado = resumen["coste_alquiler_acumulado"]

    # --- Visualización tipo "caja resumen" ---
    st.markdown("""
    <style>
    .res-box {
        border-radius: 13px;
        border: 2px solid #dde4ee;
        padding: 1.25em 1.4em 1em 1.4em;
        margin-bottom: 1.1em;
        background: #f4f7fc;
        min-width: 320px;
        box-shadow: 0 4px 18px rgba(60,120,220,0.05);
    }
    .res-title {
        font-size: 1.22em; font-weight: 800; margin-bottom: 0.4em; margin-top: -0.1em;
    }
    .res-label { font-weight: 600; color: #222;}
    .res-value { font-weight: 700; color: #1c6cb8; margin-left: 0.5em;}
    .res-box.green { border: 2px solid #c8ebda; background: #f2fcf7;}
    .res-title.green { color: #13a656;}
    .res-value.green { color: #13a656;}
    .red { color: #e03a3a; font-weight: bold;}
    .line { border-bottom: 1.1px solid #b0b8c2; margin: 0.6em 0;}
    .final-row {font-size:1.13em; font-weight:900; margin-top:0.7em;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align:center; margin-bottom: 0.7em;'>Resultados Estimados a <span style='color:#1c6cb8;'>{horizonte_anios} años</span></h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='res-box'>", unsafe_allow_html=True)
        st.markdown("<div class='res-title'><span style='color:#1c6cb8;'>🏠 Opción Compra</span></div>", unsafe_allow_html=True)
        st.markdown(f"<span class='res-label'>Desembolso inicial total:</span><span class='res-value'>{desembolso_inicial_compra:,.0f} €</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='res-label'>Costes totales acumulados:</span><span class='res-value'>{costes_compra:,.0f} €</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='res-label'>Valor estimado propiedad:</span><span class='res-value'>{valor_prop_final:,.0f} €</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='res-label'>Hipoteca pendiente:</span><span class='res-value red'>{hipoteca_pendiente:,.0f} €</span>", unsafe_allow_html=True)
        st.markdown("<div class='line'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='final-row'>Patrimonio Neto Final: <span class='res-value'>{patrimonio_neto_final:,.0f} €</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='res-box green'>", unsafe_allow_html=True)
        st.markdown("<div class='res-title green'>🔑 Opción Alquiler + Inversión</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='res-label'>Inversión inicial:</span><span class='res-value green'>{inversion_inicial_alq:,.0f} €</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='res-label'>Costes alquiler acumulados:</span><span class='res-value green'>{costes_alquiler_total:,.0f} €</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='res-label'>Capital total invertido (acumulado):</span><span class='res-value green'>{capital_total_invertido:,.0f} €</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='res-label'>Valor final inversión:</span><span class='res-value green'>{valor_final_inversion:,.0f} €</span>", unsafe_allow_html=True)
        st.markdown("<div class='line'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='final-row'>Patrimonio Neto Final: <span class='res-value green'>{patrimonio_neto_final_alq:,.0f} €</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Comparativa global de resultados
    ventaja = "Alquiler + Inversión" if diferencia_patrimonio > 0 else "Compra"
    st.markdown(
        f"<div class='res-box' style='text-align:center;'>"
        f"<div class='res-title'>🧮 Comparativa global</div>"
        f"<span class='res-label'>Diferencia patrimonio final (alquiler - compra):</span>"
        f"<span class='res-value'>{diferencia_patrimonio:,.0f} €</span><br>"
        f"<span class='res-label'>Diferencia costes acumulados (alquiler - compra):</span>"
        f"<span class='res-value'>{diferencia_costes:,.0f} €</span><br>"
        f"<span class='res-label'>Ventaja:</span> <span class='res-value'>{ventaja}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

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
    

    if "email_confirmed" not in st.session_state:
        st.session_state.email_confirmed = False

    st.subheader("📧 Descarga de resultados")
    if not st.session_state.email_confirmed:
        email = st.text_input(
            "Introduce tu email para descargar los resultados",
            key="email_input",
        )
        if st.button("Enviar email", key="send_email"):
            if email:
                try:
                    email_path = os.path.join(os.path.dirname(__file__), "emails.txt")
                    with open(email_path, "a") as f:
                        f.write(email + "\n")
                    st.session_state.email_confirmed = True
                    st.success("Descarga habilitada.")
                except Exception as e:
                    st.error(f"Error al guardar el email: {e}")
            else:
                st.warning("Por favor ingresa un email válido.")

    if st.session_state.email_confirmed:
        st.download_button(
            "📥 Descargar resultados como CSV",
            df_resultados.to_csv(index=False),
            "alquiler_vs_compra_resultados.csv",
            "text/csv",
        )
