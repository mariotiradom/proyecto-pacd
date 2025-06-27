# Cargar librerías
import pandas as pd
import plotly.express as px
from scipy.stats import gmean
import webbrowser

# Cargar los datos desde un archivo Excel
def load_data(file_path):
    try:
        data = pd.read_excel(file_path, header=3)
        return data
    except Exception as e:
        print(f"Error al cargar la data de {file_path}: {e}")
        return None

# Cargar los datos de siniestros y vehículos
siniestros_path = "C:/Users/Mildred/Downloads/Base de datos original/BBDD ONSV - SINIESTROS 2021-2023.xlsx"
vehiculos_path = "C:/Users/Mildred/Downloads/Base de datos original/BBDD ONSV - VEHICULOS 2021-2023.xlsx"

siniestros = load_data(siniestros_path)
vehiculos = load_data(vehiculos_path)

# Limpiar los duplicados en el dataset de siniestros
siniestros = siniestros.drop_duplicates(subset='CÓDIGO SINIESTRO', keep='first')

# Filtrar las columnas necesarias de cada dataset
siniestros = siniestros[['CÓDIGO SINIESTRO', 'FECHA SINIESTRO', 'HORA SINIESTRO', 
                         'CLASE SINIESTRO', 'DEPARTAMENTO', 'PROVINCIA', 'DISTRITO',
                         'TIPO DE VÍA', 'COORDENADAS LATITUD', 'COORDENADAS  LONGITUD', 
                         'CONDICIÓN CLIMÁTICA', 'SUPERFICIE DE CALZADA', 'CAUSA FACTOR PRINCIPAL']]

vehiculos = vehiculos[['CÓDIGO SINIESTRO', 'VEHÍCULO', 'MES', 'DÍA', 'HORA', 'AÑO']]

# Realizar el merge entre los datasets de siniestros y vehículos
vehiculos_siniestros = pd.merge(siniestros, vehiculos, on='CÓDIGO SINIESTRO', how='inner')

# Mostrar las primeras filas del dataframe fusionado
print(vehiculos_siniestros.head())

# ---------------------------------------------------------------
# Completar y filtrar los datos para LIMA
# ---------------------------------------------------------------

# a. Agregar columnas de días, meses, años y meses-años
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", 
         "Octubre", "Noviembre", "Diciembre"]

# Crear listas vacías para almacenar los valores de cada campo
MES_NUM = []
MES = []
YEAR = []
MES_YEAR = []

# Extraer mes y año de la fecha de los siniestros
for i in vehiculos_siniestros['FECHA SINIESTRO']:
    elem_mes_num = int(i[3:5])  # Obtener el mes (número)
    elem_year = i[6:]  # Obtener el año
    MES_NUM.append(elem_mes_num)
    YEAR.append(elem_year)

# Asignar los valores extraídos a nuevas columnas
vehiculos_siniestros["MES_NUM"] = MES_NUM
vehiculos_siniestros["AÑO"] = YEAR

# Asignar nombre del mes (como texto) según el número
for j in vehiculos_siniestros["MES_NUM"]:
    elem_mes = MESES[j - 1]  # Correlacionar número con nombre del mes
    MES.append(elem_mes)

# Asignar la columna con el nombre del mes
vehiculos_siniestros["MES"] = MES

# Crear una nueva columna con el formato "Mes-Año"
for k in range(0, len(MES)):
    elem_mes_year = str(MES[k]) + "-" + YEAR[k]
    MES_YEAR.append(elem_mes_year)

# Asignar la columna "Mes-Año"
vehiculos_siniestros["MES_AÑO"] = MES_YEAR

# b. Filtrar siniestros con valores significativos (eliminar categorías como "ESPECIAL", "FERROVIARIO", "INCENDIO")
siniestros_excluir = ["ESPECIAL", "FERROVIARIO", "INCENDIO"]
filtro_siniestros_excluidos = ~vehiculos_siniestros["CLASE SINIESTRO"].isin(siniestros_excluir)
df_filtro_siniestros_excluidos = vehiculos_siniestros.loc[filtro_siniestros_excluidos]

# c. Filtrar los registros solo para "LIMA"
filtro_lima = df_filtro_siniestros_excluidos["DEPARTAMENTO"] == "LIMA"
df_lima = df_filtro_siniestros_excluidos.loc[filtro_lima]
df_lima=df_lima.loc[df_lima['VEHÍCULO'] != '¿POSTE?']
df_lima = df_lima.loc[df_lima['CLASE SINIESTRO'] != 'CAÍDA DE PASAJERO']
df_lima = df_lima.loc[df_lima['CLASE SINIESTRO'] != 'VOLCADURA']
reemplazos1 = {
    'TRICICLO MOTORIZADO': 'OTRO',
    'TRICICLO NO MOTORIZADO': 'OTRO',
    'TRIMOTO CARGA': 'OTRO',  
    'CAMIONETA PANEL': 'OTRO',
    'SEMIREMOLQUE': 'OTRO',
    'MINIBUS': 'OTRO',
    'STATION WAGON': 'OTRO'
}
df_lima['VEHÍCULO'] = df_lima['VEHÍCULO'].replace(reemplazos1)

reemplazos2 = {
    'CHOQUE CON OBJETO FIJO': 'CHOQUE',
    'CHOQUE FUGA': 'CHOQUE',
    'ATROPELLO FUGA': 'ATROPELLO'
}
df_lima['CLASE SINIESTRO'] = df_lima['CLASE SINIESTRO'].replace(reemplazos2)

# Mostrar los datos filtrados
print(df_lima.head())

##MAPA DE CALOR

g1 = df_lima.groupby(['VEHÍCULO', 'CLASE SINIESTRO']).size().reset_index(name='contador')
g1['contador'] = g1['contador'].fillna(0)

fig1 = px.density_heatmap(g1, x='CLASE SINIESTRO', y='VEHÍCULO', z='contador', 
                         labels={'CLASE SINIESTRO': 'CLASE SINIESTRO', 'VEHÍCULO': 'VEHÍCULO', 'contador': 'Frecuencia'},
                         title='Tipo de Siniestro vs Tipo de Vehículo en Lima',
                         color_continuous_scale='Blues',  
                         text_auto=True,                   
                         range_color=[0, g1['contador'].max()])  

fig1.show()
fig1.write_html('mi_grafico_lima.html')
webbrowser.open('mi_grafico_lima.html')


# GRÁFICO DE LÍNEAS

def tasa_promedio(serie):
    if len(serie) < 3:
        return 0
    tasas = [serie[i] / serie[i-1] for i in range(1, len(serie))]
    media_geom = gmean(tasas)
    return (media_geom - 1) * 100

def valor_final(valor_inicial, tasa_percent, n):
    tasa_decimal = tasa_percent / 100
    return valor_inicial * (1 + tasa_decimal) ** n

def valores_proyecciones(serie):
    tasa = tasa_promedio(serie)
    val_2024 = int(valor_final(serie[-1], tasa, 1))
    val_2025 = int(valor_final(val_2024, tasa, 1))
    val_2026 = int(valor_final(val_2025, tasa, 1))
    return list(serie) + [val_2024, val_2025, val_2026]

# === GRÁFICO DE LÍNEAS INTERACTIVO CON PROYECCIONES PARA LIMA ===
def grafico_lineas_lima(df, nombre_html):
    df = df[df['DEPARTAMENTO'].str.upper() == "LIMA"]
    df = df.loc[df['VEHÍCULO'] == 'MOTOCICLETA']
    df = df.groupby(['CLASE SINIESTRO', 'AÑO']).size().reset_index(name='cantidad')
    
    # Top 2 siniestros más frecuentes
    top_2 = df.groupby('CLASE SINIESTRO')['cantidad'].sum().sort_values(ascending=False).head(2).index.tolist()
    
    # Filtrar las series para cada tipo de siniestro más frecuente
    serie1 = df[df['CLASE SINIESTRO'] == top_2[0]].sort_values('AÑO')['cantidad'].values
    serie2 = df[df['CLASE SINIESTRO'] == top_2[1]].sort_values('AÑO')['cantidad'].values
    
    # Obtener las proyecciones
    eje_y_1 = valores_proyecciones(serie1)
    eje_y_2 = valores_proyecciones(serie2)
    
    # Definir los años
    años = ["2021", "2022", "2023", "2024", "2025", "2026"]

    # Crear el DataFrame con las proyecciones
    df_proy = pd.DataFrame({
        'Año': años * 2,
        'Cantidad': eje_y_1 + eje_y_2,
        'Tipo': [top_2[0]] * 6 + [top_2[1]] * 6
    })

    # Crear el gráfico interactivo con Plotly
    fig = px.line(df_proy, x='Año', y='Cantidad', color='Tipo',
                  title="Proyección: Tipos de siniestro más frecuentes en Lima de Motocicletas",
                  markers=True,
                  color_discrete_sequence=['#FF5733', '#1F77B4'])

    # Ajustar el diseño del gráfico
    fig.update_layout(title_x=0.5, hovermode='x unified')

    # Guardar y mostrar el gráfico
    fig.write_html(nombre_html)
    fig.show()

# Llamar a la función para generar el gráfico de proyección para "LIMA"
grafico_lineas_lima(vehiculos_siniestros, "proyeccion_lima.html")
webbrowser.open('proyeccion_lima.html')
