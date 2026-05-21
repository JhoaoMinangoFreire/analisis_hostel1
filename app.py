"""
Aplicación principal - Análisis de Servicios de Hotel
"""
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import HotelAnalyzer
from visualizer import HotelCharts
from utils import load_excel, validate_dataset, prepare_data, COLUMNAS_ESPERADAS
from reports import generate_excel

st.set_page_config(page_title="Análisis Hotel", page_icon="🏨", layout="wide")

st.title("🏨 Análisis de Desempeño - Servicios de Hotel")

# ------------------------------------------------------------
# SIDEBAR: Carga de datos y filtros
# ------------------------------------------------------------
with st.sidebar:
    st.header("Carga de Datos")
    uploaded_file = st.file_uploader("Subir archivo Excel", type=['xlsx', 'xls'])
    if uploaded_file:
        df_raw, error = load_excel(uploaded_file)
        if error:
            st.error(f"Error al leer archivo: {error}")
        else:
            ok, msg = validate_dataset(df_raw)
            if not ok:
                st.error(msg)
                st.stop()
            df = prepare_data(df_raw)
            st.success("Datos cargados correctamente")

            # Filtro por Usuario
            st.subheader("Filtrar Usuarios")
            usuarios_disponibles = sorted(df['usuario'].dropna().unique())
            seleccion_usuarios = st.multiselect(
                "Seleccionar usuarios (todos si vacío)",
                options=usuarios_disponibles,
                default=usuarios_disponibles
            )
            if seleccion_usuarios:
                df = df[df['usuario'].isin(seleccion_usuarios)]

            # Filtro por Descripción
            st.subheader("Filtrar Descripciones")
            descripciones_disponibles = sorted(df['descripcion'].dropna().unique())
            seleccion_descripciones = st.multiselect(
                "Seleccionar descripciones (todas si vacío)",
                options=descripciones_disponibles,
                default=descripciones_disponibles
            )
            if seleccion_descripciones:
                df = df[df['descripcion'].isin(seleccion_descripciones)]

            # Filtro por Fecha (con manejo de valores nulos)
            if 'fecha del servicio' in df.columns and not df['fecha del servicio'].isna().all():
                st.subheader("Filtrar por Fecha")
                min_date = df['fecha del servicio'].min().date()
                max_date = df['fecha del servicio'].max().date()
                fechas = st.date_input(
                    "Rango de fechas",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
                if len(fechas) == 2:
                    inicio, fin = fechas
                    df = df[(df['fecha del servicio'].dt.date >= inicio) &
                            (df['fecha del servicio'].dt.date <= fin)]

# ------------------------------------------------------------
# CONTENIDO PRINCIPAL
# ------------------------------------------------------------
if 'df' in locals():
    analyzer = HotelAnalyzer(df)
    charts = HotelCharts(df)

    # ---- 1. Indicadores Generales ----
    st.subheader("📊 Indicadores Generales")
    total_debito = analyzer.total_debito()
    total_credito = df['credito'].sum()
    total_ambos = total_debito + total_credito          # ambos positivos
    num_servicios = len(df)
    num_usuarios = df['usuario'].nunique()
    num_descripciones = df['descripcion'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Débito", f"${total_debito:,.2f}")
    col2.metric("💳 Total Crédito", f"${total_credito:,.2f}")
    col3.metric("📊 Total (D+C)", f"${total_ambos:,.2f}")
    col4.metric("🔢 Servicios", num_servicios)

    # ---- 2. Ranking de Usuarios ----
    st.subheader("🏆 Ranking de Usuarios por Monto Total Débito")
    ranking = analyzer.ranking_usuarios_por_debito(10)
    st.dataframe(ranking.style.format({'debito': '${:,.2f}'}), use_container_width=True)

    fig_ranking = charts.ranking_barras(
        ranking, x='debito', y='usuario', title="Top 10 Usuarios por Débito"
    )
    st.plotly_chart(fig_ranking, use_container_width=True)

    # ---- 3. Descripciones más frecuentes ----
    st.subheader("🔁 Descripciones Más Frecuentes")
    freq_desc = analyzer.conceptos_mas_frecuentes(10)
    freq_desc.columns = ['Descripción', 'Frecuencia']

    # Total dinero generado por cada descripción (débito + crédito)
    total_por_desc = df.groupby('descripcion')[['debito', 'credito']].sum()
    total_por_desc['Total (D+C)'] = total_por_desc['debito'] + total_por_desc['credito']
    total_por_desc = total_por_desc.reset_index()[['descripcion', 'Total (D+C)']]
    total_por_desc.columns = ['Descripción', 'Total (D+C)']

    freq_desc = freq_desc.merge(total_por_desc, on='Descripción', how='left')
    st.dataframe(
        freq_desc.style.format({'Total (D+C)': '${:,.2f}'}),
        use_container_width=True
    )

    col1, col2 = st.columns(2)
    with col1:
        fig_freq = charts.barras_conceptos(
            freq_desc, x='Descripción', y='Frecuencia',
            title="Frecuencia de Descripciones"
        )
        st.plotly_chart(fig_freq, use_container_width=True)
    with col2:
        debito_desc = analyzer.debito_por_concepto()
        fig_pie = charts.pie_conceptos(
            names=debito_desc.index, values=debito_desc.values,
            title="Débito por Descripción"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ---- 4. Evolución temporal ----
    st.subheader("📈 Evolución Temporal del Total (Débito + Crédito)")
    col1, col2 = st.columns(2)
    with col1:
        freq_opciones = {'Diario': 'D', 'Semanal': 'W', 'Mensual': 'M'}
        freq_label = st.radio(
            "Frecuencia", list(freq_opciones.keys()),
            horizontal=True, key='freq_evol'
        )
        freq = freq_opciones[freq_label]
    with col2:
        desglose = st.radio(
            "Ver por:", ["Total", "Usuario"],
            horizontal=True, key='desglose_evol'
        )

    if desglose == "Total":
        deb_data = analyzer.debito_por_tiempo(freq=freq)
        cred_data = analyzer.credito_por_tiempo(freq=freq)
        if deb_data is not None and cred_data is not None:
            combined = deb_data.merge(cred_data, on='periodo', how='outer').fillna(0)
            combined['Total'] = combined['debito'] + combined['credito']
            fig_evol = charts.linea_tiempo(
                combined, x='periodo', y='Total',
                title=f"Total (Débito + Crédito) {freq_label.lower()}"
            )
            st.plotly_chart(fig_evol, use_container_width=True)
            with st.expander("Ver datos"):
                st.dataframe(
                    combined[['periodo', 'debito', 'credito', 'Total']].style.format(
                        {'debito': '${:,.2f}', 'credito': '${:,.2f}', 'Total': '${:,.2f}'}
                    )
                )
        else:
            st.info("No se pudieron generar datos temporales.")
    else:  # Por Usuario
        data_usuario = analyzer.total_por_tiempo_usuario(freq=freq)
        if data_usuario is not None and not data_usuario.empty:
            fig_evol = charts.lineas_multiples(
                data_usuario, x='periodo', y='total', color='usuario',
                title=f"Total por Usuario {freq_label.lower()}"
            )
            st.plotly_chart(fig_evol, use_container_width=True)
            with st.expander("Ver datos"):
                pivot = data_usuario.pivot(
                    index='periodo', columns='usuario', values='total'
                ).fillna(0)
                st.dataframe(pivot.style.format('${:,.2f}'))
        else:
            st.info("No se pudo generar la evolución por usuario.")

    # ---- 5. Tabla detalle: Usuario x Descripción ----
    st.subheader("📋 Detalle Débito: Usuario x Descripción")
    pivot = analyzer.debito_por_usuario_y_concepto(
        conceptos=seleccion_descripciones if 'seleccion_descripciones' in locals() else None
    )
    st.dataframe(pivot.style.format('${:,.2f}'), use_container_width=True)

    # ---- 6. Descargar Excel con las mismas tablas ----
    st.subheader("📥 Descargar Informe Excel")
    if st.button("Generar Excel"):
        # Recolectar DataFrames que ya tenemos
        tables = {}

        # Indicadores
        tables['indicadores'] = pd.DataFrame({
            'Indicador': ['Total Débito', 'Total Crédito', 'Total (D+C)',
                          'Servicios', 'Usuarios', 'Descripciones'],
            'Valor': [total_debito, total_credito, total_ambos,
                      num_servicios, num_usuarios, num_descripciones]
        })

        # Ranking
        tables['ranking'] = ranking

        # Descripciones
        tables['descripciones'] = freq_desc

        # Evolución diaria (independiente del selector actual)
        deb_d = analyzer.debito_por_tiempo(freq='D')
        cred_d = analyzer.credito_por_tiempo(freq='D')
        if deb_d is not None and cred_d is not None:
            evol_d = deb_d.merge(cred_d, on='periodo', how='outer').fillna(0)
            evol_d['Total (D+C)'] = evol_d['debito'] + evol_d['credito']
            tables['evolucion'] = evol_d[['periodo', 'debito', 'credito', 'Total (D+C)']]
        else:
            tables['evolucion'] = None

        # Detalle usuario x descripción
        tables['detalle'] = pivot

        # Filtros aplicados
        filtros = {}
        if 'seleccion_usuarios' in locals():
            filtros['Usuarios'] = ', '.join(seleccion_usuarios) if len(seleccion_usuarios) < 5 else f"{len(seleccion_usuarios)} usuarios"
        if 'seleccion_descripciones' in locals():
            filtros['Descripciones'] = ', '.join(seleccion_descripciones) if len(seleccion_descripciones) < 5 else f"{len(seleccion_descripciones)} descripciones"
        if 'inicio' in locals() and 'fin' in locals():
            filtros['Fecha'] = f"{inicio} a {fin}"

        excel_bytes = generate_excel(tables, filters=filtros)
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_bytes,
            file_name=f"informe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Por favor, carga un archivo Excel en la barra lateral para comenzar.")
    st.markdown("**Columnas esperadas:** " + ", ".join(COLUMNAS_ESPERADAS))