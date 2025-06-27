import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name='Inicio')

layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("Selecciona tu tipo de usuario:", className="text-center mb-4"),
                    dbc.Button("Usuario", id="usr-btn", color="primary", className="mb-2", style={"width": "100%"}),
                    dbc.Button("Municipalidad", id="mun-btn", color="secondary", style={"width": "100%"}),
                    dcc.Store(id='user-level-store', storage_type='session'),
                    dcc.Location(id="url", refresh=True)
                ]),
                className="shadow rounded"
            ),
            width=6, className="mx-auto my-5"
        )
    ),
    fluid=True
)


@callback(
    Output("user-level-store", "data"),
    Output("url", "pathname"),
    Input("usr-btn", "n_clicks"),
    Input("mun-btn", "n_clicks"),
    prevent_initial_call=True
)
def go_to_next(n_low, n_high):
    ctx = dash.callback_context.triggered_id
    if ctx == "usr-btn":
        return "low", "/dashboard_simple"
    elif ctx == "mun-btn":
        return "high", "/identify"
