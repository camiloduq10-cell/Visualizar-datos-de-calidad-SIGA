import streamlit as st
import pandas as pd
import plotly.express as px

# 🛠️ Configuración
st.set_page_config(page_title="Promedios por estación", layout="wide")
st.title("📊 Comparación de variables por escenario en una estación")

# 📥 Cargar datos
df = pd.read_csv('df_anual_preprocesado.csv', parse_dates=['Fecha'])
df_puntos = pd.read_excel('Puntos_SIGA.xlsx')  # Nuevo archivo con metadatos

# 🔗 Unir metadatos
df = df.merge(df_puntos, on='ID_SIGA', how='left')

# 🎯 Extraer variables
variables = [col for col in df.columns if col not in ['Escenario', 'ID_SIGA', 'Fecha', 'Cuenca', 'Subcuenca']]
cuencas = sorted(df['Cuenca'].dropna().unique())

# 🎛️ Selección de cuenca y estación
cuenca_seleccionada = st.selectbox("Selecciona la cuenca", cuencas)

# Estaciones disponibles en esa cuenca
estaciones_filtradas = df[df['Cuenca'] == cuenca_seleccionada][['ID_SIGA', 'Subcuenca']].drop_duplicates()
estaciones_opciones = {
    f"{row['ID_SIGA']} - {row['Subcuenca']}": row['ID_SIGA']
    for _, row in estaciones_filtradas.iterrows()
}
estacion_label = st.selectbox("Selecciona la estación", list(estaciones_opciones.keys()))
estacion = estaciones_opciones[estacion_label]

# 🎛️ Tipo de promedio
tipo_promedio = st.radio("Tipo de promedio", ["Total", "Por año"])

# 🔍 Filtrar datos por estación
df_filtrado = df[df['ID_SIGA'] == estacion].copy()

# 📊 Calcular promedios
if tipo_promedio == "Total":
    df_promedios = df_filtrado.groupby('Escenario')[variables].mean().reset_index()
    titulo = f"Promedio total de variables por escenario en estación {estacion_label}"

    # 📈 Visualización de todas las variables
    df_melt = df_promedios.melt(id_vars='Escenario', var_name='Variable', value_name='Promedio')
    fig = px.bar(
        df_melt,
        x='Variable',
        y='Promedio',
        color='Escenario',
        barmode='group',
        title=titulo,
        labels={'Promedio': 'Valor promedio'}
    )

else:
    df_filtrado['Año'] = df_filtrado['Fecha'].dt.year
    variable_seleccionada = st.selectbox("Selecciona la variable a visualizar", variables)
    df_promedios = df_filtrado.groupby(['Año', 'Escenario'])[variable_seleccionada].mean().reset_index()
    titulo = f"Promedio anual de {variable_seleccionada} por escenario en estación {estacion_label}"

    # 📈 Visualización de una sola variable
    fig = px.line(
        df_promedios,
        x='Año',
        y=variable_seleccionada,
        color='Escenario',
        markers=True,
        title=titulo,
        labels={variable_seleccionada: 'Valor promedio'}
    )

# 📊 Mostrar gráfico
st.plotly_chart(fig, use_container_width=True)

# 📋 Mostrar tabla
st.dataframe(df_promedios.style.format("{:.2f}"), use_container_width=True)

# 📥 Exportar tabla
nombre_variable = variable_seleccionada if tipo_promedio == "Por año" else "todas"
st.download_button(
    label="📥 Descargar tabla de promedios",
    data=df_promedios.to_csv(index=False),
    file_name=f"promedios_{estacion}_{nombre_variable}_{tipo_promedio.lower().replace(' ', '_')}.csv"
)
