import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")

# Función para cargar el Informe Diario de Unidades
@st.cache_data
def cargar_informe_unidades():
    return pd.read_excel('data/Informe_Diario_Unidades.xlsx', index_col=None)

# Función para cargar el Informe Mensual de Unidades
@st.cache_data
def cargar_informe_mensual_unidades():
    return pd.read_excel('data/Informe_Mensual_Unidades.xlsx', index_col=None)

# Función para cargar el archivo de PARADAS_UNIDADES
@st.cache_data
def cargar_paradas_unidades():
    hojas = pd.read_excel('data/PARADAS UNIDADES.xlsx', sheet_name=None, index_col=None)
    for key in hojas:
        hojas[key] = hojas[key].reset_index(drop=True)
    return hojas

# Función para cargar el archivo de PARADAS_UNIDADES_COORD
@st.cache_data
def cargar_paradas_unidades_coord():
    return pd.read_excel('data/PARADAS_UNIDADES_COORD.xlsx', index_col=None)

# Función para cargar el archivo de Incidentes Diarios desde Google Sheets
@st.cache_data
def cargar_incidentes_diarios():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Leer el secreto desde Streamlit Secrets
    credentials_json = st.secrets["google"]["GOOGLE_CREDENTIALS_JSON"]
    if credentials_json is None:
        raise ValueError("El secreto 'GOOGLE_CREDENTIALS_JSON' no está configurado correctamente.")

    # Escribir el contenido del secreto en un archivo temporal
    creds_path = "temp_credentials.json"
    with open(creds_path, 'w') as f:
        f.write(credentials_json)

    # Autenticarse con el archivo de credenciales
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    # Abrir el Google Sheet usando su clave
    sheet = client.open_by_key("17IFerZqnOsBBR27cVpDnTlWFT7NA2zgArHiMMxTQcR4")

    # Acceder a la primera hoja del documento
    worksheet = sheet.get_worksheet(0)

    # Obtener todos los valores de la hoja
    data = worksheet.get_all_records()

    # Eliminar el archivo temporal por seguridad
    os.remove(creds_path)

    # Convertir los datos en un DataFrame
    return pd.DataFrame(data).reset_index(drop=True)

# Cargar los datos
df_paradas = cargar_paradas_unidades()
df_paradas_coord = cargar_paradas_unidades_coord()
df_incidentes = cargar_incidentes_diarios().reset_index(drop=True)

# Página principal
st.title("Página Principal - Unidades")

# Selección inicial de unidad
unidad_seleccionada = st.selectbox(
    "Selecciona una unidad",
    options=["Todas"] + list(cargar_informe_unidades()['Número de unidad'].unique()),
    key="unidad_selector"
)

# Selector para elegir entre Informe Diario y Mensual
modo_informe = st.radio(
    "Selecciona el tipo de informe:",
    ("Informe Diario", "Informe Mensual"),
    key="modo_informe"
)

# Cargar el DataFrame correspondiente al modo seleccionado
if modo_informe == "Informe Diario":
    df_unidades = cargar_informe_unidades().reset_index(drop=True)
else:
    df_unidades = cargar_informe_mensual_unidades().reset_index(drop=True)

# Mostrar datos según la unidad seleccionada
if unidad_seleccionada == "Todas":
    st.subheader("Información General de Unidades")

    columnas_predeterminadas = ['Número de unidad', 'Operador', 'Modelo', 'Distancia total km', 'Combustible consumido (L)', 'Puntuación de seguridad']
    columnas_disponibles = list(df_unidades.columns.difference(columnas_predeterminadas))

    columnas_seleccionadas = st.multiselect(
        "Selecciona las columnas adicionales para mostrar",
        options=columnas_disponibles,
        default=[]
    )

    columnas_finales = columnas_predeterminadas + columnas_seleccionadas

    st.write("Informe de Unidades", df_unidades[columnas_finales].reset_index(drop=True))

    st.subheader("Gráfico de Correlación - Distancia y Combustible")
    fig = px.scatter(
        df_unidades,
        x='Distancia total km',
        y='Combustible consumido (L)',
        hover_data={'Número de unidad': True, 'Operador': True},
        labels={"Distancia total km": "Distancia (km)", "Combustible consumido (L)": "Combustible (L)"},
        title="Relación entre Distancia y Combustible Consumido"
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.subheader(f"Detalles de la Unidad: {unidad_seleccionada}")

    info_basica = df_unidades[df_unidades['Número de unidad'] == unidad_seleccionada][['Operador', 'Modelo']]
    st.subheader("Información de la Unidad")
    st.table(info_basica)

    st.subheader("Informe de la Unidad")

    unidad_info = df_unidades[df_unidades['Número de unidad'] == unidad_seleccionada]
    columnas_predeterminadas = ['Número de unidad', 'Operador', 'Modelo', 'Distancia total km', 'Combustible consumido (L)', 'Puntuación de seguridad']
    columnas_disponibles = list(unidad_info.columns.difference(columnas_predeterminadas))

    columnas_seleccionadas = st.multiselect(
        "Selecciona las columnas adicionales para mostrar",
        options=columnas_disponibles,
        default=[],
        key="columnas_unidad"
    )

    columnas_finales = columnas_predeterminadas + columnas_seleccionadas
    st.write(unidad_info[columnas_finales].reset_index(drop=True))

    if str(unidad_seleccionada) in df_paradas:
        paradas_info = df_paradas[str(unidad_seleccionada)]
        st.write(f"Paradas de la Unidad {unidad_seleccionada}", paradas_info.reset_index(drop=True))
    else:
        st.write(f"No se encontraron paradas para la Unidad {unidad_seleccionada}.")

    incidentes_info = df_incidentes[df_incidentes['Unidad'] == unidad_seleccionada]
    if not incidentes_info.empty:
        st.write(f"Incidentes de la Unidad {unidad_seleccionada}", incidentes_info.reset_index(drop=True))
    else:
        st.write(f"No se encontraron incidentes para la Unidad {unidad_seleccionada}.")

    st.subheader("Mapa de Paradas")

    paradas_coord_filtradas = df_paradas_coord[df_paradas_coord['unidad'] == int(unidad_seleccionada)]

    if not paradas_coord_filtradas.empty:
        centro = [
            paradas_coord_filtradas.iloc[0]['LATITUD'],
            paradas_coord_filtradas.iloc[0]['LONGITUD']
        ]
        mapa = folium.Map(location=centro, zoom_start=12)

        colores = {
            'NO ENTREGADO': 'orange',
            'ENTREGADO': 'green',
            'PARADA INVÁLIDA': 'red'
        }
        for _, row in paradas_coord_filtradas.iterrows():
            popup_info = f"""
                <strong>Nombre del Cliente:</strong> {row['NOMBRE_CLIENTE']}<br>
                <strong>Hora:</strong> {row['hora_final']}<br>
                <strong>Tiempo de Espera:</strong> {row['tiempo_espera']}<br>
                <strong>Estatus:</strong> {row['parada_status']}
            """
            folium.Marker(
                location=[row['LATITUD'], row['LONGITUD']],
                popup=popup_info,
                icon=folium.Icon(color=colores.get(row['parada_status'], 'blue'))
            ).add_to(mapa)

        st_folium(mapa, width=1600, height=600)
    else:
        st.write(f"No se encontraron coordenadas para la Unidad {unidad_seleccionada}.")
