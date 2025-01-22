import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

st.set_page_config(layout="wide")

# Función para cargar el Informe Diario de Unidades
@st.cache_data
def cargar_informe_unidades():
    return pd.read_excel('data/Informe_Diario_Unidades.xlsx', index_col=None)

# Función para cargar el archivo de PARADAS_UNIDADES
@st.cache_data
def cargar_paradas_unidades():
    hojas = pd.read_excel('data/PARADAS UNIDADES.xlsx', sheet_name=None, index_col=None)
    for key in hojas:
        hojas[key] = hojas[key].reset_index(drop=True)
    return hojas

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
df_unidades = cargar_informe_unidades().reset_index(drop=True)
df_paradas = cargar_paradas_unidades()
df_incidentes = cargar_incidentes_diarios().reset_index(drop=True)

# Página principal
st.title("Página Principal - Unidades")

# Mostrar lista de unidades
unidad_seleccionada = st.selectbox("Selecciona una unidad", df_unidades['Número de unidad'].unique())

# Verificar si se ha seleccionado una unidad
if unidad_seleccionada:
    # Información básica de la unidad
    info_basica = df_unidades[df_unidades['Número de unidad'] == unidad_seleccionada][['Operador', 'Modelo']]
    st.subheader("Información de la Unidad")
    st.table(info_basica)

    st.subheader(f"Detalles de la Unidad: {unidad_seleccionada}")

    # Información de Informe Diario de Unidades
    unidad_info = df_unidades[df_unidades['Número de unidad'] == unidad_seleccionada]
    columnas_disponibles = list(unidad_info.columns.difference(['Operador', 'Modelo']))
    columnas_seleccionadas = st.multiselect(
        "Selecciona las columnas adicionales para mostrar",
        options=columnas_disponibles,
        default=[]
    )
    columnas_finales = ['Operador', 'Modelo', 'Puntuación de seguridad', 'Distancia total km', 'Combustible consumido (L)'] + columnas_seleccionadas
    st.write("Informe Diario de Unidades", unidad_info[columnas_finales].reset_index(drop=True))

    # Paradas
    if str(unidad_seleccionada) in df_paradas:
        paradas_info = df_paradas[str(unidad_seleccionada)]
        st.write(f"Paradas de la Unidad {unidad_seleccionada}", paradas_info.reset_index(drop=True))
    else:
        st.write(f"No se encontraron paradas para la Unidad {unidad_seleccionada}.")

    # Incidentes
    incidentes_info = df_incidentes[df_incidentes['Unidad'] == unidad_seleccionada]
    if not incidentes_info.empty:
        st.write(f"Incidentes de la Unidad {unidad_seleccionada}", incidentes_info.reset_index(drop=True))
    else:
        st.write(f"No se encontraron incidentes para la Unidad {unidad_seleccionada}.")
