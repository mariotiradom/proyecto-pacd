# importar librerias
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import dash
from scipy.stats import gmean

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



# agrupar tipos de vehículos
df_siniestros['VEHÍCULO'] = df_siniestros['VEHÍCULO']


dash.register_page(__name__, path='/dashboard_mun', name='Dashboard Interactivo')

layout = html.Div([
    html.H2("Dashboard Interactivo de Municipalidad"),
    dcc.Store(id='store-dep1', storage_type='session'),
    dcc.Store(id='store-dep2', storage_type='session'),
    html.Div(id='output-deps'),

    dcc.Tabs(
        id='tabs',
        value='tab-1',
        children=[
            dcc.Tab(label='Siniestros Generales', value='tab-1', children=[
                html.Div([
                    dcc.Graph(id='graph1', style={'flex': '1'}),
                    dcc.Graph(id='graph2', style={'flex': '1'}),
                    dcc.Graph(id='graph3', style={'flex': '1'}),
                    dcc.Graph(id='graph4', style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '10px'}),
                html.Div([
                    dcc.Graph(id='graph5', style={'flex': '1'}),
                    dcc.Graph(id='graph6', style={'flex': '1'}),
                    dcc.Graph(id='graph7', style={'flex': '1'}),
                    dcc.Graph(id='graph8', style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '10px', 'marginTop': '10px'})
            ]),
            dcc.Tab(label='Vehículos por Municipio', value='tab-2', children=[
                html.Div([
                    dcc.Graph(id='graph9', style={'flex': '1'}),
                    dcc.Graph(id='graph10', style={'flex': '1'}),
                    dcc.Graph(id='graph11', style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '10px'}),
                html.Div([
                    dcc.Graph(id='graph12', style={'flex': '1'}),
                    dcc.Graph(id='graph13', style={'flex': '1'}),
                    dcc.Graph(id='graph14', style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '10px', 'marginTop': '10px'})
            ])
        ]
    )
])

@callback(
    Output('output-deps', 'children'),
    Input('store-dep1', 'data'),
    Input('store-dep2', 'data')
)
def mostrar_departamentos(dep1, dep2):
    if dep1 is None and dep2 is None:
        return "No hay departamentos seleccionados"
    return f"Comparando: {dep1} y {dep2}"


# Callback para actualizar gráficos según pestaña
@callback(
    [Output(f'graph{i}', 'figure') for i in range(1, 15)],
    Input('store-dep1', 'data'),
    Input('store-dep2', 'data'),
    Input('tabs', 'value')
)
def update_graphs(dep1, dep2, tab):

    if not dep1 or not dep2:
        return [go.Figure()] * 14

    if tab == 'tab-1':
        siniestros_excluir = ["ESPECIAL","FERROVIARIO","INCENDIO"]

        filtro_siniestros_excluidos =~ df_siniestros["CLASE SINIESTRO"].isin(siniestros_excluir)
        df_siniestros_filtrado = df_siniestros.loc[filtro_siniestros_excluidos]

        filtro_dep1 = df_siniestros_filtrado["DEPARTAMENTO"] == dep1
        df_dep_1 = df_siniestros_filtrado.loc[filtro_dep1].copy()

        df_dep_1['clase_siniestro_mod'] = df_dep_1['CLASE SINIESTRO'].replace(to_replace=['CAÍDA DE PASAJERO', 'CHOQUE FUGA', 'VOLCADURA', 'ATROPELLO FUGA'], value=4*["OTROS"])
        df_dep_1['vehiculo_mod'] = df_dep_1['VEHÍCULO']

        # para siniestro vs vehiculos
        filtro_vehiculos_siniestros_excluidos = ~vehiculos_siniestros["VEHÍCULO"].isin(["OTROS", "BICICLETA", "PEATÓN", "BICIMOTO", "TRICICLO", "TRIMOTO"])
        df_vehiculos_siniestros_filtrado = vehiculos_siniestros.loc[filtro_vehiculos_siniestros_excluidos]

        filtro_vehi_dep1 = df_vehiculos_siniestros_filtrado["DEPARTAMENTO"] == dep1
        df_vehi_dep_1 = df_vehiculos_siniestros_filtrado.loc[filtro_vehi_dep1].copy()

        df_vehi_dep_1['clase_siniestro_mod'] = df_vehi_dep_1['CLASE SINIESTRO'].replace(to_replace=['CAÍDA DE PASAJERO', 'CHOQUE FUGA', 'VOLCADURA', 'ATROPELLO FUGA'], value=4*["OTROS"])
        df_vehi_dep_1['vehiculo_mod'] = df_vehi_dep_1['VEHÍCULO']
        ###

        df_dep_1['tipo_via_mod'] = df_dep_1['TIPO DE VÍA'].replace(to_replace=["JIRÓN",'PASAJE','OTRO'],value=3*['OTRAS VÍAS'])
        if dep1 == "LIMA":
            df_dep_1.loc[:,"CLIMA AGRUPADO"] = df_dep_1["CONDICIÓN CLIMÁTICA"].replace({"NUBLADO": "NUBLADO-NIEBLA", "NIEBLA": "NUBLADO-NIEBLA"})
            df_dep_1.loc[:,"SINIESTRO AGRUPADO"] = df_dep_1["CLASE SINIESTRO"].replace({"CHOQUE CON OBJETO FIJO": "CHOQUE FUGA-OBJETO FIJO", "CHOQUE FUGA": "CHOQUE FUGA-OBJETO FIJO", "ESPECIAL": "OTROS", "INCENDIO": "OTROS", "VOLCADURA": "OTROS", "CAÍDA DE PASAJERO": "OTROS"})
            tabla_clima_dep1 = pd.crosstab(df_dep_1['SINIESTRO AGRUPADO'], df_dep_1['CLIMA AGRUPADO'])
        else:
            tabla_clima_dep1 = pd.crosstab(df_dep_1['clase_siniestro_mod'], df_dep_1['CONDICIÓN CLIMÁTICA'])

        tabla_veh_dep1 = pd.crosstab(df_vehi_dep_1['clase_siniestro_mod'], df_vehi_dep_1['vehiculo_mod'])
        tabla_via_dep1 = pd.crosstab(df_dep_1['clase_siniestro_mod'], df_dep_1['tipo_via_mod'])
        tabla_surf_dep1 = pd.crosstab(df_dep_1['clase_siniestro_mod'], df_dep_1['SUPERFICIE DE CALZADA'])

        filtro_dep2 = df_siniestros_filtrado["DEPARTAMENTO"] == dep2
        df_dep_2 = df_siniestros_filtrado.loc[filtro_dep2].copy()

        df_dep_2['clase_siniestro_mod'] = df_dep_2['CLASE SINIESTRO'].replace(to_replace=['CAÍDA DE PASAJERO', 'CHOQUE FUGA', 'VOLCADURA', 'ATROPELLO FUGA'], value=4*["OTROS"])
        df_dep_2['vehiculo_mod'] = df_dep_2['VEHÍCULO']

        # para siniestro vs vehiculo
        filtro_vehi_dep2 = df_vehiculos_siniestros_filtrado["DEPARTAMENTO"] == dep2
        df_vehi_dep_2 = df_vehiculos_siniestros_filtrado.loc[filtro_vehi_dep2].copy()

        df_vehi_dep_2['clase_siniestro_mod'] = df_vehi_dep_2['CLASE SINIESTRO'].replace(to_replace=['CAÍDA DE PASAJERO', 'CHOQUE FUGA', 'VOLCADURA', 'ATROPELLO FUGA'], value=4*["OTROS"])
        df_vehi_dep_2['vehiculo_mod'] = df_vehi_dep_2['VEHÍCULO']
        ###


        df_dep_2['tipo_via_mod'] = df_dep_2['TIPO DE VÍA'].replace(to_replace=["JIRÓN",'PASAJE','OTRO'],value=3*['OTRAS VÍAS'])

        tabla_veh_dep2 = pd.crosstab(df_vehi_dep_2['clase_siniestro_mod'], df_vehi_dep_2['vehiculo_mod'])
        tabla_via_dep2 = pd.crosstab(df_dep_2['clase_siniestro_mod'], df_dep_2['tipo_via_mod'])
        tabla_surf_dep2 = pd.crosstab(df_dep_2['clase_siniestro_mod'], df_dep_2['SUPERFICIE DE CALZADA'])
        tabla_clima_dep2 = pd.crosstab(df_dep_2['clase_siniestro_mod'], df_dep_2['CONDICIÓN CLIMÁTICA'])

        def grafico_mapa_calor_interactivo(df, title, label_x, label_y):
            df = df.fillna(0)
            fig = px.imshow(df.values, x=df.columns.tolist(), y=df.index.tolist(), color_continuous_scale='YlGnBu', labels=dict(x=label_x, y=label_y, color='Frecuencia'), aspect='auto', title=title, text_auto=True)
            fig.update_layout(title_x=0.5, xaxis_title=label_x, yaxis_title=label_y, height=600, width=800)
            fig.update_xaxes(tickangle=45)
            fig.update_yaxes(tickangle=0)
            return fig

        figura_4 = grafico_mapa_calor_interactivo(tabla_veh_dep1, f"Frecuencias de Tipo de Siniestro vs Tipo de Vehículo en {dep1}", 'Tipo de Vehículo', 'Tipo de Siniestro')
        figura_1 = grafico_mapa_calor_interactivo(tabla_via_dep1, f"Frecuencias de Tipo de Siniestro vs Tipo de Vía en {dep1}", 'Tipo de Vía', 'Tipo de Siniestro')
        figura_3 = grafico_mapa_calor_interactivo(tabla_clima_dep1, f"Frecuencias de Tipo de Siniestro vs Clima en {dep1}", 'Clima', 'Tipo de Siniestro')
        figura_2 = grafico_mapa_calor_interactivo(tabla_surf_dep1, f"Frecuencias de Tipo de Siniestro vs Superficie de calzada en {dep1}", 'Superficie de Calzada', 'Tipo de Siniestro')
        figura_8 = grafico_mapa_calor_interactivo(tabla_veh_dep2, f"Frecuencias de Tipo de Siniestro vs Tipo de Vehículo en {dep2}", 'Tipo de Vehículo', 'Tipo de Siniestro')
        figura_5 = grafico_mapa_calor_interactivo(tabla_via_dep2, f"Frecuencias de Tipo de Siniestro vs Tipo de Vía en {dep2}", 'Tipo de Vía', 'Tipo de Siniestro')
        figura_6 = grafico_mapa_calor_interactivo(tabla_surf_dep2, f"Frecuencias de Tipo de Siniestro vs Superficie de calzada en {dep2}", 'Superficie de Calzada', 'Tipo de Siniestro')
        figura_7 = grafico_mapa_calor_interactivo(tabla_clima_dep2, f"Frecuencias de Tipo de Siniestro vs Clima en {dep2}", 'Clima', 'Tipo de Siniestro')

        return figura_1, figura_2, figura_3, figura_4, figura_5, figura_6, figura_7, figura_8, no_update, no_update, no_update, no_update, no_update, no_update

    elif tab == 'tab-2':
        df_dep_1 = df_siniestros[df_siniestros["DEPARTAMENTO"] == dep1].copy()
        df_dep_2 = df_siniestros[df_siniestros["DEPARTAMENTO"] == dep2].copy()

        df_vehi_dep_1 = vehiculos_siniestros[vehiculos_siniestros["DEPARTAMENTO"] == dep1].copy()
        df_vehi_dep_2 = vehiculos_siniestros[vehiculos_siniestros["DEPARTAMENTO"] == dep2].copy()

        def tasa_promedio(serie):
            if len(serie) < 3 or any(s == 0 for s in serie): return 0
            tasa_01 = round(serie.iloc[1] / serie.iloc[0], 6)
            tasa_02 = round(serie.iloc[2] / serie.iloc[1], 6)
            tasas = [tasa_01, tasa_02]
            media_geom = gmean(tasas)
            tasa_promedio = (media_geom - 1) * 100
            return tasa_promedio

        def valor_final(valor_inicial, tasa_promedio_percent, n):
            tasa_decimal = tasa_promedio_percent / 100
            val_fin = valor_inicial * (1 + tasa_decimal) ** n
            return val_fin

        def valores_proyecciones(serie):
            if len(serie) < 3: return [None] * 6
            tasa = tasa_promedio(serie)
            valor_2024 = int(valor_final(serie.iloc[-1], tasa, 1))
            valor_2025 = int(valor_final(valor_2024, tasa, 1))
            valor_2026 = int(valor_final(valor_2025, tasa, 1))
            eje_y = [int(serie.iloc[0]), int(serie.iloc[1]), int(serie.iloc[2]), valor_2024, valor_2025, valor_2026]
            return eje_y

        def grafico_lineas_interactivo(eje_y1, eje_y2, title, label_01, label_02, label_x, label_y):
            años = ["2021", "2022", "2023", "2024", "2025", "2026"]
            data = {'Año': años * 2, 'Cantidad': eje_y1 + eje_y2, 'Tipo': [label_01] * len(años) + [label_02] * len(años)}
            df = pd.DataFrame(data)
            fig = px.line(df, x='Año', y='Cantidad', color='Tipo', title=title, markers=True, labels={'Año': label_x, 'Cantidad': label_y}, color_discrete_sequence=['#FFA500', '#4682B4'])
            fig.update_layout(title_x=0.5, xaxis_title=label_x, yaxis_title=label_y, legend_title='Tipo de Siniestro', hovermode='x unified')
            return fig

        # Dep 1
        via_1_combinacion_01 = df_dep_1[(df_dep_1["CLASE SINIESTRO"] == "ATROPELLO") & (df_dep_1["TIPO DE VÍA"] == "AVENIDA")].groupby("AÑO").size()
        via_1_combinacion_02 = df_dep_1[(df_dep_1["CLASE SINIESTRO"] == "CHOQUE") & (df_dep_1["TIPO DE VÍA"] == "CARRETERA")].groupby("AÑO").size()
        figura9 = grafico_lineas_interactivo(valores_proyecciones(via_1_combinacion_01), valores_proyecciones(via_1_combinacion_02), f"Evolución de siniestros críticos en {dep1}", "Atropellos en Avenida", "Choque en Carretera", "Año", "Cantidad de siniestros")

        w_1_combinacion_01 = df_dep_1[(df_dep_1["CLASE SINIESTRO"] == "ATROPELLO") & (df_dep_1["CONDICIÓN CLIMÁTICA"] == "DESPEJADO")].groupby("AÑO").size()
        w_1_combinacion_02 = df_dep_1[(df_dep_1["CLASE SINIESTRO"] == "CHOQUE") & (df_dep_1["CONDICIÓN CLIMÁTICA"] == "DESPEJADO")].groupby("AÑO").size()
        figura10 = grafico_lineas_interactivo(valores_proyecciones(w_1_combinacion_01), valores_proyecciones(w_1_combinacion_02), f"Evolución y proyección de siniestros críticos en {dep1}", "Atropellos en clima despejado", "Choques en clima despejado", "Año", "Cantidad de siniestros")

        v_1_combinacion_01 = df_vehi_dep_1[(df_vehi_dep_1["CLASE SINIESTRO"] == "CHOQUE") & (df_vehi_dep_1["VEHÍCULO"] == "MOTOCICLETA")].groupby("AÑO").size()
        v_1_combinacion_02 = df_vehi_dep_1[(df_vehi_dep_1["CLASE SINIESTRO"] == "DESPISTE") & (df_vehi_dep_1["VEHÍCULO"] == "MOTOCICLETA")].groupby("AÑO").size()
        figura11 = grafico_lineas_interactivo(valores_proyecciones(v_1_combinacion_01), valores_proyecciones(v_1_combinacion_02), f"Evolución y proyección de siniestros críticos en {dep1}", "Choques en Moto", "Despistes en Moto", "Año", "Cantidad de siniestros")

        # Dep 2
        via_2_combinacion_01 = df_dep_2[(df_dep_2["CLASE SINIESTRO"] == "CHOQUE") & (df_dep_2["TIPO DE VÍA"] == "CARRETERA")].groupby("AÑO").size()
        via_2_combinacion_02 = df_dep_2[(df_dep_2["CLASE SINIESTRO"] == "DESPISTE") & (df_dep_2["TIPO DE VÍA"] == "CARRETERA")].groupby("AÑO").size()
        figura12 = grafico_lineas_interactivo(valores_proyecciones(via_2_combinacion_01), valores_proyecciones(via_2_combinacion_02), f"Evolución de siniestros críticos en {dep2}", "Choques en Carretera", "Despistes en Carretera", "Año", "Cantidad de siniestros")

        w_2_combinacion_01 = df_dep_2[(df_dep_2["CLASE SINIESTRO"] == "CHOQUE") & (df_dep_2["CONDICIÓN CLIMÁTICA"] == "DESPEJADO")].groupby("AÑO").size()
        w_2_combinacion_02 = df_dep_2[(df_dep_2["CLASE SINIESTRO"] == "DESPISTE") & (df_dep_2["CONDICIÓN CLIMÁTICA"] == "DESPEJADO")].groupby("AÑO").size()
        figura13 = grafico_lineas_interactivo(valores_proyecciones(w_2_combinacion_01), valores_proyecciones(w_2_combinacion_02), f"Evolución y proyección de siniestros críticos en {dep2}", "Choque en clima despejado", "Despiste en clima despejado", "Año", "Cantidad de siniestros")

        v_2_combinacion_01 = df_vehi_dep_2[(df_vehi_dep_2["CLASE SINIESTRO"] == "CHOQUE") & (df_vehi_dep_2["VEHÍCULO"] == "MOTOCICLETA")].groupby("AÑO").size()
        v_2_combinacion_02 = df_vehi_dep_2[(df_vehi_dep_2["CLASE SINIESTRO"] == "DESPISTE") & (df_vehi_dep_2["VEHÍCULO"] == "MOTOCICLETA")].groupby("AÑO").size()
        figura14 = grafico_lineas_interactivo(valores_proyecciones(v_2_combinacion_01), valores_proyecciones(v_2_combinacion_02), f"Evolución y proyección de siniestros críticos en {dep2}", "Choques en Moto", "Despistes en Moto", "Año", "Cantidad de siniestros")

        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, figura9, figura10, figura11, figura12, figura13, figura14

    return [no_update] * 14
