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

# funcion para combinar vehiculos
def agrupar_vehiculos(valor):
    if 'CAMIONETA' in str(valor): # Convertir a string para manejar posibles no-strings
        return 'CAMIONETA'
    elif 'REMOL' in str(valor):
        return 'REMOLQUE'
    elif 'TRICICLO' in str(valor):
        return 'TRICICLO'
    elif 'TRIMOTO' in str(valor):
        return 'TRIMOTO'
    else:
        return valor
    
# excluir tipos de siniestro muy pequeños
siniestros_excluir = ["ESPECIAL","FERROVIARIO","INCENDIO"] # Debido a que los datos son pequeños en comparación con los otros

filtro_siniestros_excluidos =~ df_siniestros["CLASE SINIESTRO"].isin(siniestros_excluir) #alt 126
df_siniestros = df_siniestros.loc[filtro_siniestros_excluidos]

# agrupar tipos de vehículos
df_siniestros['VEHÍCULO'] = df_siniestros['VEHÍCULO'].apply(agrupar_vehiculos)

dash.register_page(__name__, path='/identify', name='Log In')

department_options = df_siniestros['DEPARTAMENTO'].unique().tolist()

layout = dbc.Container([
    dbc.Card([
        dbc.CardBody([
            html.H2("Identificación de municipalidad", className="text-center mb-4"),
            
            dbc.Input(id="name-input", type="text", placeholder="Tu nombre", className="mb-3"),
            
            dbc.Row([
                dbc.Col(dbc.Select(id='dep1-dropdown', 
                                   options=[{'label': i, 'value': i} for i in department_options], 
                                   value='LIMA'), md=6),
                dbc.Col(dbc.Select(id='dep2-dropdown', 
                                   options=[{'label': i, 'value': i} for i in department_options], 
                                   value='LA LIBERTAD'), md=6)
            ], className="mb-3"),

            dbc.Button("Entrar", id="enter-btn", color="primary", className="w-100"),

            dcc.Store(id='store-dep1', storage_type='session'),
            dcc.Store(id='store-dep2', storage_type='session'),
            dcc.Location(id="go-mun")
        ])
    ], className="mt-5", style={"maxWidth": "500px", "margin": "auto"})
])

@callback(
    Output('store-dep1', 'data'),
    Output('store-dep2', 'data'),
    Output("go-mun", "pathname"),
    Input("enter-btn", "n_clicks"),
    State('dep1-dropdown', 'value'),
    State('dep2-dropdown', 'value'),
    State("name-input", "value"),
    prevent_initial_call=True
)
def redirect_user(n_clicks, dep1, dep2, name):
    if name and dep1 and dep2:
        return dep1, dep2, "/dashboard_mun"
    return dash.no_update, dash.no_update, dash.no_update
    
