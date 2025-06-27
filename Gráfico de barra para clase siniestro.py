# Gráfico de barra para clase siniestro

# cargar librerí­as
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency # Librería para prueba de chi-cuadrado
import plotly.express as px
import plotly.io as pio


#%% Carga y limpieza de la base de datos

# definir funciones
def load_data(file_path):
    try:
        data = pd.read_excel(file_path, header = 3)
        return data
    except Exception as e:
        print(f"Error al cargar la data de {file_path}: {e}")
        return None

# copiar ruta de los archivos
siniestros_path = "F:/Ingeniería de la información/2025-I/Progr. avanzada ciencia datos/Trabajos de clase/Trabajos grupales/Base de datos original/BBDD ONSV - SINIESTROS 2021-2023.xlsx" # modificar segÃºn sea necesario
vehiculos_path = "F:/Ingeniería de la información/2025-I/Progr. avanzada ciencia datos/Trabajos de clase/Trabajos grupales/Base de datos original/BBDD ONSV - VEHICULOS 2021-2023.xlsx" # modificar segÃºn sea necesario

# cargar datos
siniestros = load_data(siniestros_path)
vehiculos = load_data(vehiculos_path)

# limpiar siniestros 'CÓDIGO SINIESTRO'
siniestros = siniestros.drop_duplicates(subset = 'CÓDIGO SINIESTRO', keep = 'first')
print(siniestros.shape)
print(vehiculos.columns)

# seleccionar columnas de interÃ©s
siniestros = siniestros[['CÓDIGO SINIESTRO', 'FECHA SINIESTRO', 'HORA SINIESTRO', 'CLASE SINIESTRO', 'DEPARTAMENTO', 'PROVINCIA', 'DISTRITO', 'TIPO DE VÍA', 'COORDENADAS LATITUD', 'COORDENADAS  LONGITUD', 'CONDICIÓN CLIMÁTICA', 'SUPERFICIE DE CALZADA', 'CAUSA FACTOR PRINCIPAL']]
vehiculos = vehiculos[['CÓDIGO SINIESTRO', 'VEHÍCULO', 'MES', 'DÍA', 'HORA', 'AÑO']]

# realizar merge entre siniestros y vehí­culos
vehiculos_siniestros = pd.merge(siniestros, vehiculos, on = 'CÓDIGO SINIESTRO', how = 'inner')
print(vehiculos_siniestros.shape)

# mostrar las primeras filas del dataframe resultante
print(vehiculos_siniestros.head(10))

#%% Funciones para gráficos
def mapa_calor(df,color,title, label_x,label_y):
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(df, annot=True, fmt=".0f", cmap=color) 
    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
def grafico_bar(df,title,label_x,label_y):
    
    eje_x=df.iloc[:,0]
    eje_y=df.iloc[:,1]
    
    plt.figure(figsize=(14, 8))
    plt.bar(eje_x,eje_y)
    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks(rotation=30)
    plt.yticks(range(0, 2500, 250))
    
    plt.tight_layout()
    
    plt.show()
    
def grafico_bar_interactivo(df, title, label_x, label_y,nombre_guardar):
    fig = px.bar(
        df,
        x=df.columns[0],
        y=df.columns[1],
        text=df.columns[1],
        title=title,
        labels={df.columns[0]: label_x, df.columns[1]: label_y},
        color=df.columns[0]
    )

    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(
        xaxis_tickangle=30,
        yaxis=dict(title=label_y, tick0=0, dtick=500),
        showlegend=False,
        title_x=0.5,
        height=600
    )

    fig.write_html(nombre_guardar)
    
#%% Gráfico de barras corregido para Clases de siniestro

# a. Filtrar para quedarse con los siniestros con valores significativos
siniestros_excluir=["ESPECIAL","FERROVIARIO","INCENDIO"] # Debido a que los datos son pequeños en comparación con los otros

filtro_siniestros_excluidos=~siniestros["CLASE SINIESTRO"].isin(siniestros_excluir) #alt 126
df_filtro_siniestros_excluidos=siniestros.loc[filtro_siniestros_excluidos]

# b. Agrupar para contar siniestros de tránsito por 'CLASE SINIESTRO' y 'AÑO'

tabla_siniestro=df_filtro_siniestros_excluidos.groupby("CLASE SINIESTRO").size().reset_index(name="Cant_siniestro")
tabla_siniestro.fillna(value=0,inplace=True)

# c. Gráfico
grafico_tabla_siniestro= grafico_bar(tabla_siniestro, "Distribución acumulada de clase de siniestros fatales \n(2021–2023)", "Tipo de siniestro", "Cantidad de siniestros fatales")

# d. Gráfico interactivo

pio.renderers.default = 'browser'
 
nombre_siniestro_interactivo="grafico_interactivo_clase siniestro.html"
grafico_tabla_siniestro_interactivo= grafico_bar_interactivo(tabla_siniestro, "Distribución acumulada de clase de siniestros fatales \n(2021–2023)", "Tipo de siniestro", "Cantidad de siniestros fatales",nombre_siniestro_interactivo)
