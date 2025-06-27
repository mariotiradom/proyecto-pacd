# importar librerias
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash

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
siniestros = siniestros.drop_duplicates(subset = 'CÓDIGO SINIESTRO', keep = 'first') # eliminar duplicados de la base de datos de siniestros

# seleccionar columnas de interés
siniestros = siniestros[['CÓDIGO SINIESTRO', 'FECHA SINIESTRO', 'HORA SINIESTRO', 'CLASE SINIESTRO', 'DEPARTAMENTO', 'PROVINCIA', 'DISTRITO', 'TIPO DE VÍA', 'COORDENADAS LATITUD', 'COORDENADAS  LONGITUD', 'CONDICIÓN CLIMÁTICA', 'SUPERFICIE DE CALZADA', 'CAUSA FACTOR PRINCIPAL']]
vehiculos = vehiculos[['CÓDIGO SINIESTRO', 'VEHÍCULO', 'MES', 'DÍA', 'HORA', 'AÑO']]

# realizar merge entre siniestros y vehículos
vehiculos_siniestros = pd.merge(siniestros, vehiculos, on = 'CÓDIGO SINIESTRO', how = 'inner')


# crear una copia del dataframe para evitar modificar el original
df_siniestros = vehiculos_siniestros.copy()

# dropear los duplicados en 'CÓDIGO SINIESTRO'
df_siniestros = df_siniestros.drop_duplicates(subset= 'CÓDIGO SINIESTRO', keep='first') # basicamente es siniestros, pero ahora incluye un codigo de vehiculo


# modificar las columna 'FECHA SINIESTRO', 'MES', 'DÍA', 'HORA' para que sea del tipo datetime
df_siniestros['FECHA SINIESTRO'] = pd.to_datetime(df_siniestros['FECHA SINIESTRO'], errors='coerce')
    
# excluir tipos de siniestro muy pequeños
siniestros_excluir = ["ESPECIAL","FERROVIARIO","INCENDIO"] # Debido a que los datos son pequeños en comparación con los otros

filtro_siniestros_excluidos =~ df_siniestros["CLASE SINIESTRO"].isin(siniestros_excluir) #alt 126
df_siniestros = df_siniestros.loc[filtro_siniestros_excluidos]

filtro_v_siniestros_excluidos =~ vehiculos_siniestros["CLASE SINIESTRO"].isin(siniestros_excluir) #alt 126
vehiculos_siniestros = vehiculos_siniestros.loc[filtro_v_siniestros_excluidos]

# agrupar tipos de vehículos
df_siniestros['VEHÍCULO'] = df_siniestros['VEHÍCULO']


dash.register_page(__name__, path='/dashboard_mun', name='Dashboard Interactivo')

layout = html.Div([
    html.H2("Dashboard Avanzado"),
    dcc.Store(id='store-dep1', storage_type='session'),
    dcc.Store(id='store-dep2', storage_type='session'),
    html.Div(id='output-deps'),

    html.Div([
        dcc.Graph(id = 'graph1', style={'flex': '1'}),
        dcc.Graph(id = 'graph2', style={'flex': '1'}),
        dcc.Graph(id = 'graph3', style={'flex': '1'}),
        dcc.Graph(id = 'graph4', style={'flex': '1'}),
    ], style={'display': 'flex', 'gap': '10px'}),

    html.Div([
        dcc.Graph(id = 'graph5', style={'flex': '1'}),
        dcc.Graph(id = 'graph6', style={'flex': '1'}),
        dcc.Graph(id = 'graph7', style={'flex': '1'}),
        dcc.Graph(id = 'graph8', style={'flex': '1'}),
    ], style={'display': 'flex', 'gap': '10px', 'marginTop': '10px'})
], )

@callback(
    Output('output-deps', 'children'),
    Input('store-dep1', 'data'),
    Input('store-dep2', 'data')
)
def mostrar_departamentos(dep1, dep2):
    if dep1 is None and dep2 is None:
        return "No hay departamentos seleccionados"
    return f"Comparando: {dep1} y {dep2}"

@callback(
    Output('graph1', 'figure'),
    Output('graph2', 'figure'),
    Output('graph3', 'figure'),
    Output('graph4', 'figure'),
    Output('graph5', 'figure'),
    Output('graph6', 'figure'),
    Output('graph7', 'figure'),
    Output('graph8', 'figure'),
    Input('store-dep1', 'data'),
    Input('store-dep2', 'data')
)
def update_graphs(dep1, dep2):
    # filtrar por el primer departamento
    filtro_dep1 = df_siniestros["DEPARTAMENTO"] == dep1
    df_dep_1 = df_siniestros.loc[filtro_dep1]


    # agrupar variables para hacer la prueba debido a que las frecuencias son menores a 5 en estas categorías
    df_dep_1['clase_siniestro_mod'] = df_dep_1['CLASE SINIESTRO'].replace(to_replace=['CAÍDA DE PASAJERO', 'CHOQUE FUGA', 'VOLCADURA', 'ATROPELLO FUGA'], value=4*["OTROS"])
    df_dep_1['vehiculo_mod'] = df_dep_1['VEHÍCULO']  # Usando las categorías originales de vehículo
    df_dep_1['tipo_via_mod'] = df_dep_1['TIPO DE VÍA'].replace(to_replace=["JIRÓN",'PASAJE','OTRO'],value=3*['OTRAS VÍAS'])
    # agregar el clima
    if dep1 == "LIMA":
        df_dep_1.loc[:,"CLIMA AGRUPADO"] = df_dep_1["CONDICIÓN CLIMÁTICA"].replace({
            "NUBLADO": "NUBLADO-NIEBLA",
            "NIEBLA": "NUBLADO-NIEBLA"
        })
        df_dep_1.loc[:,"SINIESTRO AGRUPADO"] = df_dep_1["CLASE SINIESTRO"].replace({
            "CHOQUE CON OBJETO FIJO": "CHOQUE FUGA-OBJETO FIJO",
            "CHOQUE FUGA": "CHOQUE FUGA-OBJETO FIJO",
            "ESPECIAL": "OTROS",
            "INCENDIO": "OTROS",
            "VOLCADURA": "OTROS",
            "CAÍDA DE PASAJERO": "OTROS"
        })

        tabla_clima_dep1 = pd.crosstab(df_dep_1['SINIESTRO AGRUPADO'], df_dep_1['CLIMA AGRUPADO'])
    # b. Creación de tabla de doble entrada 
    tabla_veh_dep1 = pd.crosstab(df_dep_1['clase_siniestro_mod'], df_dep_1['vehiculo_mod'])
    tabla_via_dep1 = pd.crosstab(df_dep_1['clase_siniestro_mod'], df_dep_1['tipo_via_mod'])
    tabla_surf_dep1 = pd.crosstab(df_dep_1['clase_siniestro_mod'], df_dep_1['SUPERFICIE DE CALZADA'])
    if dep1 != "LIMA":
        tabla_clima_dep1 = pd.crosstab(df_dep_1['clase_siniestro_mod'], df_dep_1['CONDICIÓN CLIMÁTICA'])

    # filtrar por el segundo departamento
    filtro_dep2 = df_siniestros["DEPARTAMENTO"] == dep2
    df_dep_2 = df_siniestros.loc[filtro_dep2] 

    # agrupar variables para hacer la prueba debido a que las frecuencias son menores a 5 en estas categorías
    df_dep_2['clase_siniestro_mod'] = df_dep_2['CLASE SINIESTRO'].replace(to_replace=['CAÍDA DE PASAJERO', 'CHOQUE FUGA', 'VOLCADURA', 'ATROPELLO FUGA'], value=4*["OTROS"])
    df_dep_2['vehiculo_mod'] = df_dep_2['VEHÍCULO']  # Usando las categorías originales de vehículo


    df_dep_2['tipo_via_mod'] = df_dep_2['TIPO DE VÍA'].replace(to_replace=["JIRÓN",'PASAJE','OTRO'],value=3*['OTRAS VÍAS'])
    if dep2 == 'LA LIBERTAD':
        df_dep_2.loc[:,"SINIESTRO AGRUPADO"] = df_dep_2["CLASE SINIESTRO"].replace({
            "ESPECIAL": "OTROS",
            "VOLCADURA": "OTROS",
            "CAÍDA DE PASAJERO": "OTROS"
        })

        tabla_clima_dep2 = pd.crosstab(df_dep_2['SINIESTRO AGRUPADO'], df_dep_2['CONDICIÓN CLIMÁTICA'])


    # b. Creación de tabla de doble entrada 
    tabla_veh_dep2 = pd.crosstab(df_dep_2['clase_siniestro_mod'], df_dep_2['vehiculo_mod'])
    tabla_via_dep2 = pd.crosstab(df_dep_2['clase_siniestro_mod'], df_dep_2['tipo_via_mod'])
    tabla_surf_dep2 = pd.crosstab(df_dep_2['clase_siniestro_mod'], df_dep_2['SUPERFICIE DE CALZADA'])
    if dep2 != "LIMA":
        tabla_clima_dep2 = pd.crosstab(df_dep_2['clase_siniestro_mod'], df_dep_2['CONDICIÓN CLIMÁTICA'])

    def grafico_mapa_calor_interactivo(df, title, label_x, label_y):
        # Asegurarse de que el DataFrame no tenga valores NaN
        df = df.fillna(0)
        
        fig = px.imshow(
            df.values,
            x=df.columns.tolist(),
            y=df.index.tolist(),
            color_continuous_scale='YlGnBu',
            labels=dict(x=label_x, y=label_y, color='Frecuencia'),
            aspect='auto',
            title=title,
            text_auto=True
        )
        
        fig.update_layout(
            title_x=0.5,
            xaxis_title=label_x,
            yaxis_title=label_y,
            height=600,
            width=800
        )
        
        # Mejorar la legibilidad
        fig.update_xaxes(tickangle=45)
        fig.update_yaxes(tickangle=0)

        return fig

    figura_4 = grafico_mapa_calor_interactivo(tabla_veh_dep1, 
                              f"Frecuencias de Tipo de Siniestro vs Tipo de Vehículo en {dep1}", 
                              'Tipo de Vehículo',
                              'Tipo de Siniestro'
                              ) 
    figura_4.update_layout(font = dict(size = 9))
    figura_1 = grafico_mapa_calor_interactivo(tabla_via_dep1, 
                              f"Frecuencias de Tipo de Siniestro vs Tipo de Vía en {dep1}", 
                              'Tipo de Vía',
                              'Tipo de Siniestro'
                              )  
    figura_1.update_layout(font = dict(size = 9))
    figura_3 = grafico_mapa_calor_interactivo(tabla_clima_dep1, 
                              f"Frecuencias de Tipo de Siniestro vs Clima en {dep1}",
                              'Clima',
                              'Tipo de Siniestro'
                              )
    figura_3.update_layout(font = dict(size = 9))
    figura_2 = grafico_mapa_calor_interactivo(tabla_surf_dep1, 
                              f"Frecuencias de Tipo de Siniestro vs Superficie de calzada en {dep1}", 
                              'Superficie de Calzada',
                              'Tipo de Siniestro'
                              )
    figura_2.update_layout(font = dict(size = 9))
    
    figura_8 = grafico_mapa_calor_interactivo(tabla_veh_dep2, 
                              f"Frecuencias de Tipo de Siniestro vs Tipo de Vehículo en {dep2}", 
                              'Tipo de Vehículo',
                              'Tipo de Siniestro'
                              ) 
    figura_8.update_layout(font = dict(size = 9))
    figura_5 = grafico_mapa_calor_interactivo(tabla_via_dep2, 
                              f"Frecuencias de Tipo de Siniestro vs Tipo de Vía en {dep2}", 
                              'Tipo de Vía',
                              'Tipo de Siniestro'
                              )  
    figura_5.update_layout(font = dict(size = 9))

    figura_6 = grafico_mapa_calor_interactivo(tabla_surf_dep2, 
                              f"Frecuencias de Tipo de Siniestro vs Superficie de calzada en {dep2}", 
                              'Superficie de Calzada',
                              'Tipo de Siniestro'
                              )
    figura_6.update_layout(font = dict(size = 9))
    figura_7 = grafico_mapa_calor_interactivo(tabla_clima_dep2, 
                              f"Frecuencias de Tipo de Siniestro vs Clima en {dep2}",
                              'Clima',
                              'Tipo de Siniestro'
                              )
    figura_7.update_layout(font = dict(size = 9))
    return figura_1, figura_2, figura_3, figura_4, figura_5, figura_6, figura_7, figura_8