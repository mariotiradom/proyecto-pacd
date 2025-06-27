import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Store(id='user-level-store', storage_type='session'),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)