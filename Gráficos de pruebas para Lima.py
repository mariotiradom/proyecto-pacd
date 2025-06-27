# Gráficos de pruebas para Lima

# Cargar librerí­as
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency # Librería para prueba de chi-cuadrado
import plotly.express as px
import plotly.io as pio
from scipy.stats import gmean

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
def mapa_calor(df,color,title, label_x,label_y,mi,ma):
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(df, annot=True, fmt=".2f", cmap=color,vmin=mi, vmax=ma) 
    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
def grafico_mapa_calor_interactivo(df, title, label_x, label_y, nombre):
    fig = px.imshow(
        df.values,  # matriz de valores
        x=df.columns,
        y=df.index,
        color_continuous_scale='YlGnBu',
        labels=dict(x=label_x, y=label_y, color='Frecuencia'),
        text_auto=True,
        aspect='auto',
        title=title
    )

    fig.update_layout(
        title_x=0.5,
        xaxis_title=label_x,
        yaxis_title=label_y,
        height=600
    )

    fig.write_html(nombre)
    
def grafico_bar(df,title,label_x,label_y):
    
    eje_x=df.iloc[:,0]
    eje_y=df.iloc[:,1]
    
    plt.figure(figsize=(14, 8))
    plt.bar(eje_x,eje_y)
    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks(rotation=30)
    plt.yticks(range(0, 5000, 500))
    
    plt.tight_layout()
    
    plt.show()
    
def grafico_bar_interactivo(df, title, label_x, label_y,nombre):
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

    fig.write_html(nombre)

def grafico_lineas(eje_y1,eje_y2,title,label_01,label_02,label_x,label_y):
    plt.figure(figsize=(8, 5))
    
    plt.plot(["2021","2022","2023","2024","2025","2026"],eje_y1, marker='o', label=label_01)
    plt.plot(["2021","2022","2023","2024","2025","2026"],eje_y2, marker='o', label=label_02)
    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    plt.show()
    
def grafico_lineas_interactivo(eje_y1, eje_y2, title, label_01, label_02, label_x, label_y, nombre_guardar):
    # Años correspondientes al eje X
    años = [2021, 2022, 2023, 2024, 2025, 2026]

    df = pd.DataFrame({
        label_x: años,
        label_01: eje_y1,
        label_02: eje_y2
    })

    # Transformar a formato largo
    df_largo = df.melt(id_vars=label_x, var_name='Categoría', value_name=label_y)

    # Crear gráfico interactivo
    fig = px.line(
        df_largo,
        x=label_x,
        y=label_y,
        color='Categoría',
        markers=True,
        title=title,
        labels={label_x: label_x, 'Categoría': 'Categoría', label_y: label_y}
    )

    fig.update_layout(
        title_x=0.5,
        height=500,
        template='plotly_white',
        xaxis=dict(tickmode='linear', tick0=2021, dtick=1)
    )

    fig.write_html(nombre_guardar)

#%% Completar y filtrar para solo datos de Lima

# a. Agregar columna de días, meses, años y meses-años

MESES=["Enero","Febrero","Marzo","Abril",
       "Mayo","Junio","Julio","Agosto",
       "Setiembre","Octubre","Noviembre","Diciembre"]

MES_NUM=[]
MES=[]
YEAR=[]
MES_YEAR=[]

for i in siniestros['FECHA SINIESTRO']:
    elem_mes_num=int(i[3:5])
    elem_year=i[6:]
    MES_NUM.append(elem_mes_num)
    YEAR.append(elem_year)
    
siniestros["MES_NUM"]=MES_NUM
siniestros["AÑO"]=YEAR 

for j in siniestros["MES_NUM"]:
    elem_mes=MESES[j-1]
    MES.append(elem_mes)

siniestros["MES"]=MES

for k in range(0,len(MES)):
    elem_mes_year=str(MES[k])+"-"+YEAR[k]
    MES_YEAR.append(elem_mes_year)
    
siniestros["MES_AÑO"]=MES_YEAR

# b. Filtrar para quedarse con los siniestros con valores significativos
siniestros_excluir=["ESPECIAL","FERROVIARIO","INCENDIO"] # Debido a que los datos son pequeños en comparación con los otros

filtro_siniestros_excluidos=~siniestros["CLASE SINIESTRO"].isin(siniestros_excluir) #alt 126
df_filtro_siniestros_excluidos=siniestros.loc[filtro_siniestros_excluidos]

# c. Filtro para obtener solo registros de Lima

filtro_lima=df_filtro_siniestros_excluidos["DEPARTAMENTO"]=="LIMA"
df_lima=df_filtro_siniestros_excluidos.loc[filtro_lima]


#%% Prueba de independencia para tipo de vía y clase de siniestro en Lima

# a. Agrupar variables para hacer la prueba debido a que las frecuencias son menores a 5 en estas categorías

df_lima['clase_siniestro_mod'] = df_lima['CLASE SINIESTRO'].replace(to_replace=['CAÍDA DE PASAJERO','CHOQUE FUGA','VOLCADURA','ATROPELLO FUGA'],value=4*["OTROS"])

df_lima['tipo_via_mod'] = df_lima['TIPO DE VÍA'].replace(to_replace=["JIRÓN",'PASAJE','OTRO'],value=3*['OTRAS VÍAS'])


# b. Creación de tabla de doble entrada de clase de siniestro modificado y tipo de via modificado

tabla_lima = pd.crosstab(df_lima['clase_siniestro_mod'], df_lima['tipo_via_mod'])
print("-----Prueba de independencia-----\nTipo de Siniestros vs. Tipo de Vía")
print("\n")
print(tabla_lima)
print("\n")

# c. Prueba de independencia
chi2, p, dof, expected_lima = chi2_contingency(tabla_lima)

print("-----Resultados de la prueba de independencia-----\nTipo de Siniestros vs. Tipo de Vía\nLima\n")
print("Chi-cuadrado:", chi2)
print("p-valor:", p)
print("Grados de libertad:", dof)
print("Frecuencias esperadas:\n", expected_lima)
print("\n")

# d. Se convierte el array de expected que contiene las frecuencias esperadas a DataFrame
expected_df_lima = pd.DataFrame(expected_lima, index=tabla_lima.index, columns=tabla_lima.columns)

# e. Restar lo observado y lo esperado para obtener el exceso o déficit observado frente al esperado
diferencia_lima= tabla_lima - expected_df_lima

# f. Mostrar la diferencia
print("-----Tabla del exceso o déficit de siniestros-----\nLima")
print(diferencia_lima)
print("\n")


#%% Gráficos de mapas de calor

# Mapa de calor de tabla de contigencia 
grafico_mapa_calor_tabla_lima=mapa_calor(tabla_lima, 'YlGnBu', "Mapa de calor\nTipo de Vía vs Clase de Siniestro", 'Tipo de Vía', 'Tipo de Siniestro',0,180)

grafico_mapa_calor_interactivo_lima=grafico_mapa_calor_interactivo(tabla_lima, "Mapa de calor\nTipo de Vía vs Clase de Siniestro", 'Tipo de Vía', 'Tipo de Siniestro', "Grafico_mapa_calor_lima.html")


# Mapa de calor de tabla de diferencia de frecuencias
grafico_mapa_calor_diferencia_lima=mapa_calor(diferencia_lima, "coolwarm", 'Mapa de calor del exceso o déficit de siniestros observados\nrespecto a los esperados según la prueba de independencia\nentre tipo de vía y clase de siniestro', 'Tipo de Vía', 'Tipo de Siniestro',-1,15)

grafico_mapa_interactivo_diferencia_lima=grafico_mapa_calor_interactivo(diferencia_lima, 'Mapa de calor del exceso o déficit de siniestros observados\nrespecto a los esperados según la prueba de independencia\nentre tipo de vía y clase de siniestro', 'Tipo de Vía', 'Tipo de Siniestro',"Grafico_mapa_diferencias_lima.html")


#%% Funciones para el cálculo de las tasas de crecimiento de las dos categorías con mayor valor en la diferencia
    # Atropello en avenidas y despistes en carretera

# Calcular la tasa promedio de crecimiento o decrecimiento
def tasa_promedio(serie):
    tasa_01 = round(serie[1] / serie[0], 6)
    tasa_02 = round(serie[2] / serie[1], 6)
    
    tasas = [tasa_01, tasa_02]  # Tasa = 1 + crecimiento porcentual
    media_geom = gmean(tasas)
    tasa_promedio = (media_geom - 1) * 100
    
    return tasa_promedio

# Calcular valor final proyectado
def valor_final(valor_inicial, tasa_promedio_percent, n):
    tasa_decimal = tasa_promedio_percent / 100
    val_fin = valor_inicial * (1 + tasa_decimal) ** n
    return val_fin

# Generar valores proyectados para los próximos 3 años
def valores_proyecciones(serie,tasa):
    tasa = tasa_promedio(serie)

    valor_2024 = int(valor_final(serie[-1], tasa, 1))
    valor_2025 = int(valor_final(valor_2024, tasa, 1))
    valor_2026 = int(valor_final(valor_2025, tasa, 1))
    
    eje_y=[int(serie[0]),int(serie[1]),int(serie[2]),valor_2024,valor_2025,valor_2026]
    
    
    return eje_y

#%% Cálculo de las tasas de crecimiento de las dos categorías con mayor valor en la diferencia
    # Atropello en avenidas y despistes en carretera

# a. Filtrar atropellos en avenidas
combinacion_01 = df_lima[(df_lima["clase_siniestro_mod"] == "ATROPELLO") &
    (df_lima["tipo_via_mod"] == "AVENIDA")].groupby("AÑO").size()

# b. Filtrar despistes en carreteras
combinacion_02 = df_lima[(df_lima["clase_siniestro_mod"] == "CHOQUE") &
    (df_lima["tipo_via_mod"] == "CARRETERA")].groupby("AÑO").size()

# c. Valores de proyecciones de combinación 01
tasa_promedio_combinacion_01=tasa_promedio(combinacion_01)
eje_y_combinacion_01=valores_proyecciones(combinacion_01, tasa_promedio_combinacion_01)

print("\n")
print(f"La tasa promedio de crecimiento o decrecimiento de la combinación 01 es: {round(tasa_promedio_combinacion_01,4)} % anual.")
print("\n")

# d. Valores  de proyecciones de combinación 02
tasa_promedio_combinacion_02=tasa_promedio(combinacion_02)
eje_y_combinacion_02=valores_proyecciones(combinacion_02, tasa_promedio_combinacion_02)

print(f"La tasa promedio de crecimiento o decrecimiento de la combinación 02 es: {round(tasa_promedio_combinacion_02,4)} % anual.")
print("\n")

#%% Gráfico de líneas para ver la tendencia en clase de siniestro y tipo de via según los años

# a. Gráficos
grafico_lineas_combinaciones=grafico_lineas(eje_y_combinacion_01, eje_y_combinacion_02, "Evolución de siniestros críticos en Lima", 'Atropellos en Avenida', 'Choques en Carretera', "Año", "Cantidad de siniestros")
grafico_lineas_interactivo_combinaciones=grafico_lineas_interactivo(eje_y_combinacion_01, eje_y_combinacion_02, "Evolución de siniestros críticos en Lima", 'Atropellos en Avenida', 'Choques en Carretera', "Año", "Cantidad de siniestros", "Gráfico líneas Lima.html")



