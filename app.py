import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


st.set_page_config(layout="wide")

# Función para cargar el Informe Diario de Unidades
@st.cache_data
def cargar_informe_unidades():
    return pd.read_excel('data/Informe_Diario_Unidades.xlsx')

# Función para cargar el archivo de PARADAS_UNIDADES
@st.cache_data
def cargar_paradas_unidades():
    # Leer todas las hojas del archivo 'PARADAS_UNIDADES.xlsx'
    hojas = pd.read_excel('data/PARADAS UNIDADES.xlsx', sheet_name=None)
    return hojas

# Función para cargar el archivo de Incidentes Diarios desde Google Sheets
@st.cache_data
def cargar_inciidentes_diarios():
    # Definir el alcance de la API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Usar el archivo de credenciales descargado desde Google Cloud
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials_services.json', scope)
    
    # Autenticarse con las credenciales
    client = gspread.authorize(creds)
    
    # Abrir el Google Sheet
    sheet = client.open_by_key("17IFerZqnOsBBR27cVpDnTlWFT7NA2zgArHiMMxTQcR4")
    
    # Acceder a la primera hoja del documento
    worksheet = sheet.get_worksheet(0)
    
    # Obtener todos los valores de la hoja
    data = worksheet.get_all_records()
    
    # Convertir los datos en un DataFrame de pandas
    return pd.DataFrame(data)

# Cargar los datos
df_unidades = cargar_informe_unidades()
df_paradas = cargar_paradas_unidades()
df_incidentes = cargar_inciidentes_diarios()

# Página principal
st.title("Página Principal - Unidades")

# Mostrar lista de unidades
unidad_seleccionada = st.selectbox("Selecciona una unidad", df_unidades['Número de unidad'].unique())

# Verificar si se ha seleccionado una unidad
if unidad_seleccionada:
    # Extraer la información básica de la unidad seleccionada
    info_basica = df_unidades[df_unidades['Número de unidad'] == unidad_seleccionada][['Operador', 'Modelo']]
    st.subheader("Información de la Unidad")
    st.table(info_basica.reset_index(drop=True))  # Mostrar la tabla con solo las columnas seleccionadas
    
    st.subheader(f"Detalles de la Unidad: {unidad_seleccionada}")
    
    # Mostrar información de Informe Diario de Unidades
    unidad_info = df_unidades[df_unidades['Número de unidad'] == unidad_seleccionada]
    st.write("Informe Diario de Unidades", unidad_info)
    
    # Mostrar las paradas de la unidad seleccionada
    if str(unidad_seleccionada) in df_paradas:
        paradas_info = df_paradas[str(unidad_seleccionada)]
        st.write(f"Paradas de la Unidad {unidad_seleccionada}", paradas_info)
    else:
        st.write(f"No se encontraron paradas para la Unidad {unidad_seleccionada}.")
    
    # Mostrar incidentes de la unidad seleccionada
    incidentes_info = df_incidentes[df_incidentes['Unidad'] == unidad_seleccionada]
    if not incidentes_info.empty:
        st.write(f"Incidentes de la Unidad {unidad_seleccionada}", incidentes_info)
    else:
        st.write(f"No se encontraron incidentes para la Unidad {unidad_seleccionada}.")
