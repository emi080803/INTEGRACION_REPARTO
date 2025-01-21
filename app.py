import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(layout="wide")

# Función para cargar el Informe Diario de Unidades
@st.cache_data
def cargar_informe_unidades():
    # Leer el archivo Excel sin usar índices de las columnas
    return pd.read_excel('data/Informe_Diario_Unidades.xlsx', index_col=None)

# Función para cargar el archivo de PARADAS_UNIDADES
@st.cache_data
def cargar_paradas_unidades():
    # Leer todas las hojas del archivo 'PARADAS_UNIDADES.xlsx' sin índices
    hojas = pd.read_excel('data/PARADAS UNIDADES.xlsx', sheet_name=None, index_col=None)
    # Eliminar índices de todas las hojas
    for key in hojas:
        hojas[key] = hojas[key].reset_index(drop=True)
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
    return pd.DataFrame(data).reset_index(drop=True)

# Cargar los datos
df_unidades = cargar_informe_unidades().reset_index(drop=True)
df_paradas = cargar_paradas_unidades()
df_incidentes = cargar_inciidentes_diarios().reset_index(drop=True)

# Página principal
st.title("Página Principal - Unidades")

# Mostrar lista de unidades
unidad_seleccionada = st.selectbox("Selecciona una unidad", df_unidades['Número de unidad'].unique())

# Verificar si se ha seleccionado una unidad
if unidad_seleccionada:
    # Extraer la información básica de la unidad seleccionada
    info_basica = df_unidades[df_unidades['Número de unidad'] == unidad_seleccionada][['Operador', 'Modelo']]
    st.subheader("Información de la Unidad")
    st.table(info_basica)  # Mostrar la tabla
    
    st.subheader(f"Detalles de la Unidad: {unidad_seleccionada}")
    
    # Mostrar información de Informe Diario de Unidades
    unidad_info = df_unidades[df_unidades['Número de unidad'] == unidad_seleccionada]
    
    # Permitir al usuario seleccionar columnas adicionales
    columnas_disponibles = list(unidad_info.columns.difference(['Operador', 'Modelo']))
    columnas_seleccionadas = st.multiselect(
        "Selecciona las columnas adicionales para mostrar",
        options=columnas_disponibles,
        default=[]
    )
    
    # Mantener siempre visibles las columnas 'Operador' y 'Modelo'
    columnas_finales = ['Operador', 'Modelo', 'Puntuación de seguridad', 'Distancia total km', 'Combustible consumido (L)'] + columnas_seleccionadas
    st.write("Informe Diario de Unidades", unidad_info[columnas_finales].reset_index(drop=True))
    
    # Mostrar las paradas de la unidad seleccionada
    if str(unidad_seleccionada) in df_paradas:
        paradas_info = df_paradas[str(unidad_seleccionada)]
        st.write(f"Paradas de la Unidad {unidad_seleccionada}", paradas_info.reset_index(drop=True))
    else:
        st.write(f"No se encontraron paradas para la Unidad {unidad_seleccionada}.")
    
    # Mostrar incidentes de la unidad seleccionada
    incidentes_info = df_incidentes[df_incidentes['Unidad'] == unidad_seleccionada]
    if not incidentes_info.empty:
        st.write(f"Incidentes de la Unidad {unidad_seleccionada}", incidentes_info.reset_index(drop=True))
    else:
        st.write(f"No se encontraron incidentes para la Unidad {unidad_seleccionada}.")
