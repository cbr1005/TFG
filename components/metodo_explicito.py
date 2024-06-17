import numpy as np
from dash import Dash, html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from scipy.stats import norm

# Definimos las funciones que nos proporcionaste para el modelo de precios de opciones
def pay_off(S, E, type):
    if type == "call":
        return np.maximum(S - E, 0)
    elif type == "put":
        return np.maximum(E - S, 0)

def u_m_inf(dx, tau, E, r, type):
    if type == "call":
        return 0  # Límite inferior para una call cuando el precio del activo es muy bajo
    elif type == "put":
        return E * np.exp(-r * tau)  # Valor del put cuando el precio del activo tiende a 0

def u_p_inf(S, type):
    if type == "call":
        return S  # Límite superior para una call
    elif type == "put":
        return 0  # Límite superior para un put cuando el precio del activo es muy alto

def explicit_fd(S_max, K, T, sigma, r, option_type, N, M):
    dt = T / M
    ds = S_max / N
    V = np.zeros((N+1, M+1))
    S = np.linspace(0, S_max, N+1)
    alpha = 0.5 * sigma**2 * dt / ds**2

    if alpha > 0.5:
        raise ValueError(f"El valor de alpha es {alpha}, lo que puede comprometer la estabilidad. Ajuste los parámetros.")

    V[:, M] = pay_off(S, K, option_type)
    for j in range(M-1, -1, -1):
        for i in range(1, N):
            V[i, j] = V[i, j+1] + alpha * (V[i-1, j+1] - 2 * V[i, j+1] + V[i+1, j+1])

        V[0, j] = u_m_inf(ds, T - dt * (M-j), K, r, option_type)
        V[N, j] = u_p_inf(S_max, option_type)

    return V, S, dt

def function_option_price(S, E, r, T, sigma, type):
    d1 = (np.log(S / E) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if type == 'call':
        return S * norm.cdf(d1) - E * np.exp(-r * T) * norm.cdf(d2)
    else:
        return E * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

layout = html.Div([
    html.H1("Simulación de Opciones con Diferencias Finitas Explícitas", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio máximo del subyacente:', className="input-label"),
            dcc.Input(id='S_max', type='number', placeholder='Ingrese valor inicial', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='K', type='number', placeholder='Ingrese precio del ejercicio', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tiempo hasta el vencimiento (en años):', className="input-label"),
            dcc.Input(id='T', type='number', placeholder='Ingrese numero de años', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='sigma', type='number', placeholder='Ingrese volatilidad', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa libre de riesgo (%):', className="input-label"),
            dcc.Input(id='r', type='number', placeholder='Ingrese tasa de interes', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tipo de opción:', className="input-label"),
            dcc.Dropdown(
                id='option_type',
                options=[
                    {'label': 'Call', 'value': 'call'},
                    {'label': 'Put', 'value': 'put'}
                ],
                value='call',
                className="dropdown"
            ),
        ]),
        html.Div(id='error-message', className="error-message-container"),
        html.Button('Calcular', id='calculate', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='option_graph'),
    html.Div(id='price_output')
], className="container")

@callback(
    Output('option_graph', 'figure'),
    Output('price_output', 'children'),
    Output('error-message', 'children' ),
    Input('calculate', 'n_clicks'),
    State('S_max', 'value'),
    State('K', 'value'),
    State('T', 'value'),
    State('sigma', 'value'),
    State('r', 'value'),
    State('option_type', 'value')
)
def update_graph(n_clicks, S_max, K, T, sigma, r, option_type):
    if n_clicks > 0:
        sigma /= 100  # Convert percentage to decimal
        r /= 100  # Convert percentage to decimal
        N = 100
        M = 100
        try:
            V, S, dt = explicit_fd(S_max, K, T, sigma, r, option_type, N, M)
            initial_option_price = V[:, 0]
            bs_prices = [function_option_price(s, K, r, T, sigma, option_type) for s in S]
            error = np.abs(bs_prices - initial_option_price)

            # Create a Plotly graph for options
            option_figure = go.Figure()
            option_figure.add_trace(go.Scatter(x=S, y=initial_option_price, mode='lines', name='Método Explícito'))
            option_figure.add_trace(go.Scatter(x=S, y=bs_prices, mode='lines', name='Black-Scholes'))
            option_figure.update_layout(title='Comparación de precios de opción', xaxis_title='Precio del subyacente S', yaxis_title='Precio de la opción')

            # Price output
            price_output = f"Precio inicial con Explícito: {initial_option_price[int(N/2)]:.2f}, Black-Scholes: {bs_prices[int(N/2)]:.2f}, Diferencia: {abs(initial_option_price[int(N/2)] - bs_prices[int(N/2)]):.2f}"

            return option_figure, price_output, ""
        except ValueError as e:
            return go.Figure(), "", f"Error: {str(e)}"
    return go.Figure(), "", ""

