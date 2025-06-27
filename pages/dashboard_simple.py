# importar librerias
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, callback
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

# crear la aplicación Dash
dash.register_page(__name__, path='/dashboard_simple', name='Dashboard Simple')

# definir opciones
min_year = df_siniestros['AÑO'].min()
max_year = df_siniestros['AÑO'].max()
year_range = [min_year, max_year]
department_options = df_siniestros['DEPARTAMENTO'].unique().tolist()
month_options = df_siniestros['MES'].unique().tolist()

#fig.add_trace(go.Pie(labels=['A', 'B', 'C'], values=[30, 50, 20]), row=1, col=1)
#fig.add_trace(go.Pie(labels=['A', 'B', 'C'], values=[30, 50, 20]), row=1, col=2)
pie_via = px.pie(names=['No Data'], values=[1], title="No data", color_discrete_sequence=['lightgray'])
pie_surf = px.pie(names=['No Data'], values=[1], title="No data", color_discrete_sequence=['lightgray'])
bar_sin = px.bar(pd.DataFrame({'x': [], 'y': []}), x='x', y='y', title='No data')
bar_wthr = px.bar(pd.DataFrame({'x': [], 'y': []}), x='x', y='y', title='No data')
bar_vType = px.bar(pd.DataFrame({'x': [], 'y': []}), x='x', y='y', title='No data')

heatmap_siniesto_via = px.imshow([[0]], text_auto=True, color_continuous_scale='Blues', title='Mapa de calor de siniestros por tipo de vía')
heatmap_siniesto_surf = px.imshow([[0]], text_auto=True, color_continuous_scale='Blues', title='Mapa de calor de siniestros por superficie de calzada')
heatmap_siniesto_wthr = px.imshow([[0]], text_auto=True, color_continuous_scale='Blues', title='Mapa de calor de siniestros por condición climática')
heatmap_siniesto_vType = px.imshow([[0]], text_auto=True, color_continuous_scale='Blues', title='Mapa de calor de siniestros por tipo de vehículo')
# definir el gráfico inicial

layout = html.Div([
    html.Div([
        html.H1('Siniestros de tránsito en Perú'),
        dcc.RangeSlider(min = min_year, max = max_year, step = 1, value = year_range, id = 'year-slider', marks = {i: str(i) for i in range(2021, 2024)}),
        dbc.Accordion([
            dbc.AccordionItem([
                dcc.Dropdown(
                    options=month_options, value=month_options, id='month-dropdown', 
                    multi=True, placeholder="Selecciona mes"
                )
            ], title="Mes"),

            dbc.AccordionItem([
                dcc.Dropdown(
                    options=department_options, value=department_options, id='dep-dropdown',
                    multi=True, placeholder="Selecciona departamento"
                )
            ], title="Departamento"),

            dbc.AccordionItem([
                dcc.Dropdown(
                    id='prov-dropdown', multi=True, placeholder="Selecciona provincia"
                )
            ], title="Provincia"),

            dbc.AccordionItem([
                dcc.Dropdown(
                    id='dist-dropdown', multi=True, placeholder="Selecciona distrito"
                )
            ], title="Distrito"),

        ], start_collapsed=True, flush=True),
        dcc.Store(id='user-level-store', storage_type='session')
    ]),

    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Dashboard Principal', value='tab-1'),
        dcc.Tab(label='Dashboard Relacionado', value='tab-2'),
        dcc.Tab(label='Dashboard Densidad Ubicación', value='tab-3'),
    ]),

    html.Div(id='tabs-content')
])

# ---------------------- CALLBACK DROPDOWN ----------------------
@callback(
    Output('prov-dropdown', 'options'),
    Output('prov-dropdown', 'value'),
    Input('dep-dropdown', 'value')
)
def update_provincias(dep_selected):
    provincias = df_siniestros[df_siniestros['DEPARTAMENTO'].isin(dep_selected)]['PROVINCIA'].unique()
    options = provincias
    value = list(provincias) if len(provincias) > 0 else None
    return options, value


@callback(
    Output('dist-dropdown', 'options'),
    Output('dist-dropdown', 'value'),
    Input('prov-dropdown', 'value'),
    Input('dep-dropdown', 'value')
)
def update_distritos(prov_selected, dep_selected):
    dff = df_siniestros[
        (df_siniestros['DEPARTAMENTO'].isin(dep_selected)) &
        (df_siniestros['PROVINCIA'].isin(prov_selected))
    ]
    distritos = dff['DISTRITO'].unique()
    options = distritos
    value = list(distritos) if len(distritos) > 0 else None
    return options, value

# ---------------------- CALLBACK GRÁFICOS ----------------------
@callback(
    Output(component_id = 'tabs-content', component_property = 'children'),
    Input(component_id = 'tabs', component_property = 'value'),
    Input(component_id = 'year-slider', component_property = 'value'),
    Input(component_id = 'month-dropdown', component_property = 'value'),
    Input(component_id = 'dep-dropdown', component_property = 'value'),
    Input(component_id = 'prov-dropdown', component_property = 'value'),
    Input(component_id = 'dist-dropdown', component_property = 'value')
)

def render_content(tab, selected_years, selected_months, selected_department, selected_province, selected_district):
    filtered_df = df_siniestros[
        (df_siniestros['AÑO'] >= selected_years[0]) &
        (df_siniestros['AÑO'] <= selected_years[1]) &
        (df_siniestros['MES'].isin(selected_months)) &
        (df_siniestros['DEPARTAMENTO'].isin(selected_department)) &
        (df_siniestros['PROVINCIA'].isin(selected_province)) &
        (df_siniestros['DISTRITO'].isin(selected_district))
    ]

    if filtered_df.empty:
        empty_fig = px.pie(names=['Sin datos'], values=[1], title='Sin datos')
        empty_bar = px.bar(x=[], y=[], title='Sin datos')
        return html.Div([
            dcc.Graph(figure=empty_fig),
            dcc.Graph(figure=empty_bar)
        ])

    if tab == 'tab-1':

        filtered_df_via = filtered_df.groupby(['AÑO','MES','DEPARTAMENTO', 'TIPO DE VÍA']).size().reset_index(name='counts')
        filtered_df_surf = filtered_df.groupby(['AÑO','MES','DEPARTAMENTO', 'SUPERFICIE DE CALZADA']).size().reset_index(name='counts')


        ######### pie de tipo de vía ##########
        pie_via = px.pie(filtered_df_via, values = 'counts', names = 'TIPO DE VÍA', title = 'Siniestros por tipo de vía', color_discrete_sequence = px.colors.qualitative.Pastel,
                         labels = {'TIPO DE VÍA': 'Tipo de Vía'},)

        ######### pie de superficie de calzada ##########
        pie_surf = px.pie(filtered_df_surf, values = 'counts', names = 'SUPERFICIE DE CALZADA', title = 'Siniestros por superficie de calzada', color_discrete_sequence=px.colors.qualitative.Pastel,
                          labels = {'SUPERFICIE DE CALZADA': 'Superficie de Calzada'},)
        ######### barras tipo de siniestro #########
        siniestros_by_type = filtered_df.groupby('CLASE SINIESTRO')['CÓDIGO SINIESTRO'].count().reset_index().sort_values(by = 'CÓDIGO SINIESTRO', ascending = False)

        # grafico de barras según el tipo de siniestro
        bar_sin = px.bar(siniestros_by_type, x = 'CLASE SINIESTRO', y = 'CÓDIGO SINIESTRO', color = 'CLASE SINIESTRO', color_discrete_sequence=px.colors.qualitative.Pastel)
        bar_sin.update_layout(xaxis_title="Clase de siniestro", yaxis_title="Cantidad de Siniestros", font = dict(size=10), title = 'Siniestros por Clase de Siniestro')
        bar_sin.update_traces(width=0.4)
        ######### barras condición climática #########
        # Agrupar por condición climática y contar los siniestros
        siniestros_by_weather = filtered_df.groupby('CONDICIÓN CLIMÁTICA')['CÓDIGO SINIESTRO'].count().reset_index().sort_values(by = 'CÓDIGO SINIESTRO', ascending = False)
        
        bar_wthr = px.bar(siniestros_by_weather, x = 'CONDICIÓN CLIMÁTICA', y = 'CÓDIGO SINIESTRO', title = 'Siniestros por Condición Climática', color = 'CONDICIÓN CLIMÁTICA', color_discrete_sequence=px.colors.qualitative.Pastel)
        bar_wthr.update_layout(xaxis_title="Condición climática", yaxis_title="Cantidad de Siniestros", font = dict(size=10))
        # # Seleccionar las 5 condiciones climáticas con más siniestros

        ######### barras tipo de vehículo #########
        siniestros_by_vehicle = filtered_df.groupby('VEHÍCULO')['CÓDIGO SINIESTRO'].count().reset_index().sort_values(by = 'CÓDIGO SINIESTRO', ascending = False)

        # grafico de barras según el tipo de vehículo
        bar_vType = px.bar(siniestros_by_vehicle, y = 'VEHÍCULO', x = 'CÓDIGO SINIESTRO', orientation = 'h', title = 'Siniestros por tipo de vehiculo', color = 'VEHÍCULO', color_discrete_sequence=px.colors.qualitative.Pastel)
        bar_vType.update_layout(yaxis_title="Tipo de vehículo", xaxis_title="Cantidad de Siniestros", font = dict(size=10))
        return html.Div([
            html.Div([
                dcc.Graph(figure=pie_via),
                dcc.Graph(figure=pie_surf)
            ], style={'display': 'flex', 'gap': '20px', 'height': '45vh', 'width': '100vw'}),
            html.Div([
                dcc.Graph(figure=bar_sin, style = {'flex': '1', 'maxWidth': '500px'}),
                dcc.Graph(figure=bar_wthr, style = {'flex': '1', 'maxWidth': '400px'}),
                dcc.Graph(figure=bar_vType, style = {'flex': '1', 'maxWidth': '600px'})
            ], style={'display': 'flex', 'gap': '20px', 'height': '50vh', 'width': '100vw', 'marginTop': '10px'})
        ])
    # agrupar el top de vehiculos
    # top_vehiculos = siniestros_by_vehicle['VEHíCULO'].head(5)

    elif tab == 'tab-2':
        # -------- Dashboard Secundario --------
        siniestro_vs_via = filtered_df.groupby(['CLASE SINIESTRO', 'TIPO DE VÍA']).size().reset_index(name='counts')
        map_sin_via = siniestro_vs_via.pivot(index='CLASE SINIESTRO', columns='TIPO DE VÍA', values='counts').fillna(0)
        heatmap_siniesto_via = px.imshow(map_sin_via, text_auto=True, color_continuous_scale='Blues', title='Mapa de calor de siniestros por tipo de vía')


        siniestro_vs_surface = filtered_df.groupby(['CLASE SINIESTRO', 'SUPERFICIE DE CALZADA']).size().reset_index(name='counts')
        map_sin_surf = siniestro_vs_surface.pivot(index='CLASE SINIESTRO', columns='SUPERFICIE DE CALZADA', values='counts').fillna(0)
        heatmap_siniesto_surf = px.imshow(map_sin_surf, text_auto=True, color_continuous_scale='Blues', title='Mapa de calor de siniestros por superficie de calzada')


        siniestro_vs_weather = filtered_df.groupby(['CLASE SINIESTRO', 'CONDICIÓN CLIMÁTICA']).size().reset_index(name='counts')
        map_sin_wthr = siniestro_vs_weather.pivot(index='CLASE SINIESTRO', columns='CONDICIÓN CLIMÁTICA', values='counts').fillna(0)
        heatmap_siniesto_wthr = px.imshow(map_sin_wthr, text_auto=True, color_continuous_scale='Blues', title='Mapa de calor de siniestros por condición climática')


        siniestro_vs_vehicle = filtered_df.groupby(['CLASE SINIESTRO', 'VEHÍCULO']).size().reset_index(name='counts')
        map_sin_vType = siniestro_vs_vehicle.pivot(index='CLASE SINIESTRO', columns='VEHÍCULO', values='counts').fillna(0)
        heatmap_siniesto_vType = px.imshow(map_sin_vType, text_auto=True, color_continuous_scale='Blues', title='Mapa de calor de siniestros por tipo de vehículo')


        return html.Div([
            html.Div([
                dcc.Graph(figure=heatmap_siniesto_via),
                dcc.Graph(figure=heatmap_siniesto_surf)
            ], style={'display': 'flex', 'gap': '20px'}),
            html.Div([
                dcc.Graph(figure=heatmap_siniesto_wthr),
                dcc.Graph(figure=heatmap_siniesto_vType)
            ], style={'display': 'flex', 'gap': '20px', 'marginTop': '20px'})
        ])
    elif tab == 'tab-3':
        siniestros_por_ubi = filtered_df.groupby(['COORDENADAS LATITUD', 'COORDENADAS  LONGITUD']).size().reset_index()
        # visualización base de siniestros por ubicación
        density_map_ubi = px.density_map(siniestros_por_ubi, lat = 'COORDENADAS LATITUD', lon = 'COORDENADAS  LONGITUD', radius = 10, title = 'Siniestros por ubicación')
        density_map_ubi.update_layout(height=600, width=1600, font = dict(size = 10))
        return html.Div([
            html.Div([
                dcc.Graph(figure=density_map_ubi),
            ], style={'display': 'flex', 'gap': '20px'}),
        ])   
    