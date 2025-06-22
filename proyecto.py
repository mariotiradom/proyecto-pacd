# cargar librerías
import pandas as pd
import plotly.express as px
import datetime as dt
import plotly.io as pio

# definir dónde mostrar los gráficos
pio.renderers.default = 'browser'

# definir funciones
def load_data(file_path):
    try:
        data = pd.read_excel(file_path, header = 3)
        return data
    except Exception as e:
        print(f"Error al cargar la data de {file_path}: {e}")
        return None

# copiar ruta de los archivos
siniestros_path = '../proyecto-pacd/BBDD ONSV - SINIESTROS 2021-2023.xlsx' # modificar según sea necesario
vehiculos_path = '../proyecto-pacd/BBDD ONSV - VEHICULOS 2021-2023.xlsx' # modificar según sea necesario

# cargar datos
siniestros = load_data(siniestros_path)
vehiculos = load_data(vehiculos_path)

# limpiar siniestros 'CÓDIGO SINIESTRO'
siniestros = siniestros.drop_duplicates(subset = 'CÓDIGO SINIESTRO', keep = 'first')
print(siniestros.shape)
print(vehiculos.columns)

# seleccionar columnas de interés
siniestros = siniestros[['CÓDIGO SINIESTRO', 'FECHA SINIESTRO', 'HORA SINIESTRO', 'CLASE SINIESTRO', 'DEPARTAMENTO', 'PROVINCIA', 'DISTRITO', 'TIPO DE VÍA', 'COORDENADAS LATITUD', 'COORDENADAS  LONGITUD', 'CONDICIÓN CLIMÁTICA', 'SUPERFICIE DE CALZADA', 'CAUSA FACTOR PRINCIPAL']]
vehiculos = vehiculos[['CÓDIGO SINIESTRO', 'VEHÍCULO', 'MES', 'DÍA', 'HORA', 'AÑO']]

# realizar merge entre siniestros y vehículos
vehiculos_siniestros = pd.merge(siniestros, vehiculos, on = 'CÓDIGO SINIESTRO', how = 'inner')
print(vehiculos_siniestros.shape)

# mostrar las primeras filas del dataframe resultante
print(vehiculos_siniestros.head(10))

# crear una copia para realizar modificaciones
df_siniestros = vehiculos_siniestros.copy()

# mapa de calor de incidencias por departamento según la hora del día
## alistar dataframe para el mapa de calor
df_siniestros['HORA SINIESTRO'] = pd.to_datetime(df_siniestros['HORA SINIESTRO'], format='%H:%M', errors='coerce')
df_siniestros['HORA SINIESTRO'] = df_siniestros['HORA SINIESTRO'].dt.hour
siniestros_dep_por_hora = df_siniestros.groupby(['DEPARTAMENTO', 'HORA'])['CÓDIGO SINIESTRO'].count().reset_index()

print(siniestros_dep_por_hora.head())

## pivotear el dataframe
pivot_siniestros_dep_por_hora = siniestros_dep_por_hora.pivot(index='DEPARTAMENTO', columns='HORA', values='CÓDIGO SINIESTRO').fillna(0)
pivot_siniestros_dep_por_hora.index = pivot_siniestros_dep_por_hora.index.astype(str)
pivot_siniestros_dep_por_hora.columns = pivot_siniestros_dep_por_hora.columns.astype(int)
print(pivot_siniestros_dep_por_hora)
## crear el mapa de calor
heatmap_siniestros_dep_hora = px.imshow(
    pivot_siniestros_dep_por_hora,
    text_auto = True,
    color_continuous_scale = 'blues',
    title = 'Mapa de calor de siniestros por departamento y hora del día',
)
heatmap_siniestros_dep_hora.update_xaxes(tickmode = 'linear')

heatmap_siniestros_dep_hora.show()

# gráfico de barras de los siniestros por condición climática
## alistar dataframe para el gráfico
siniestros_por_condicion_climatica = df_siniestros.groupby('CONDICIÓN CLIMÁTICA')['CÓDIGO SINIESTRO'].count().reset_index().sort_values(by='CÓDIGO SINIESTRO', ascending=False)

## crear el gráfico de barras
bar_condiciones_climaticas = px.bar(
    siniestros_por_condicion_climatica,
    x = 'CONDICIÓN CLIMÁTICA',
    y = 'CÓDIGO SINIESTRO',
    title = 'Frecuencia de siniestros por condición climática',
    labels = {'CÓDIGO SINIESTRO': 'Número de siniestros', 'CONDICIÓN CLIMÁTICA': 'Condición climática'},
    color = 'CONDICIÓN CLIMÁTICA',
    color_discrete_sequence = px.colors.qualitative.G10,
)

bar_condiciones_climaticas.show()
# gráfico de barras apilada del tipo de siniestros para las 5 condiciones climáticas más frecuentes
top_5_condiciones_climaticas = siniestros_por_condicion_climatica['CONDICIÓN CLIMÁTICA'].head(5)
print(top_5_condiciones_climaticas)

## agrupar los siniestros por condición climática y tipo de siniestro
siniestros_por_cond_clima_clase = df_siniestros.groupby(['CONDICIÓN CLIMÁTICA', 'CLASE SINIESTRO'])['CÓDIGO SINIESTRO'].count().reset_index()
siniestros_por_cond_clima_clase = siniestros_por_cond_clima_clase[siniestros_por_cond_clima_clase['CONDICIÓN CLIMÁTICA'].isin(top_5_condiciones_climaticas)]

## crear el gráfico de barras agrupadas
hist_condiciones_climaticas_clase = px.histogram(
    siniestros_por_cond_clima_clase,
    x = 'CONDICIÓN CLIMÁTICA',
    y = 'CÓDIGO SINIESTRO',
    color = 'CLASE SINIESTRO',
    color_discrete_sequence = px.colors.qualitative.G10,
    barmode = 'group',
    labels = {'CONDICIÓN CLIMÁTICA': 'Condición climática', 'CLASE SINIESTRO': 'Clase de siniestro'},
    title = 'Frecuencia de siniestros agrupados por las 5 condiciones climáticas más frecuentes y clase de siniestro',
)
hist_condiciones_climaticas_clase.update_layout(yaxis_title="Número de siniestros")

hist_condiciones_climaticas_clase.show()