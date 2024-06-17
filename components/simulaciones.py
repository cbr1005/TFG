import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from scipy.stats import norm

# Función para calcular precios de opciones usando Black-Scholes
def function_option_price(S, K, r, T, sigma, option_type):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# Función para trazar la evolución del precio de la opción en función del tiempo hasta la expiración
def plot_option_evolution(S, K, r, sigma, T, num_steps, option_type):
    times = np.linspace(0, T, num_steps)
    option_prices = [function_option_price(S, K, r, T - ti, sigma, option_type) for ti in times]
    return times, option_prices

# Función para simulación de Monte Carlo
def monte_carlo_simulation(S, K, r, T, sigma, option_type, M):
    num_steps = 365
    times = np.linspace(0, T, num_steps)
    dt = T / num_steps
    paths = np.zeros((num_steps, M))
    payoffs = np.zeros((num_steps, M))
    paths[0] = S
    for t in range(1, num_steps):
        Z = np.random.standard_normal(M)
        paths[t] = paths[t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)
        if option_type == 'call':
            payoffs[t] = np.exp(-r * (T - t/num_steps)) * np.maximum(paths[t] - K, 0)
        else:
            payoffs[t] = np.exp(-r * (T - t/num_steps)) * np.maximum(K - paths[t], 0)
    mean_payoffs = np.mean(payoffs, axis=1)
    return times, mean_payoffs


layout = html.Div([
    html.H1("Simulación de Carteras de Opciones", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio al contado inicial:', className="input-label"),
            dcc.Input(id='input-spot', type='number', placeholder='Ingrese valor inicial', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='input-strike', type='number', placeholder='Ingrese precio de ejercicio', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interés (%):', className="input-label"),
            dcc.Input(id='input-rate', type='number', placeholder='Ingrese tasa de interés', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='input-volatility', type='number', placeholder='Ingrese volatilidad', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='input-date-value', date=datetime.today().date(), className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='input-date-expiration', date=None, className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Número de simulaciones:', className="input-label"),
            dcc.Input(id='input-num-simulations', type='number', placeholder='Ingrese número de simulaciones', className="input-field"),
        ]),
        html.Div(id='1-error-message', className="error-message-container"),
        html.Div(className="input-group", children=[
            html.Label('Tipo de opción:', className="input-label"),
            dcc.Dropdown(
                id='input-option-type',
                options=[
                    {'label': 'Call', 'value': 'call'},
                    {'label': 'Put', 'value': 'put'}
                ],
                value='call',
                className="dropdown"
            ),
        ]),
        html.Button('Calcular Precio', id='button-calculate-bs', n_clicks=0, className="calculate-button"),
        html.Button('Simulación Monte Carlo', id='button-monte-carlo', n_clicks=0, className="calculate-button")
    ]),
    html.Div(id='output-option-price', className="output-container"),
    dcc.Graph(id='option-evolution-graph', className="output-container"),
    html.Div(id='portfolio-simulation-conclusion', className="output-container")
], className='container')

@callback(
    [Output('option-evolution-graph', 'figure'), Output('output-option-price', 'children'),Output('1-error-message', 'children')],
    [Input('button-calculate-bs', 'n_clicks'), Input('button-monte-carlo', 'n_clicks')],
    [State('input-spot', 'value'), State('input-strike', 'value'), State('input-rate', 'value'),
     State('input-date-value', 'date'), State('input-date-expiration', 'date'),
     State('input-volatility', 'value'), State('input-option-type', 'value'), State('input-num-simulations','value')]
)
def update_output(n_calculate_bs, n_monte_carlo, S, K, rate, date_value, date_expiration, volatility, option_type, M):
    ctx = dash.callback_context
    if not ctx.triggered:
        return go.Figure(), "", html.Div()

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Verificar si faltan valores o están mal introducidos
    missing_fields = []
    if S is None:
        missing_fields.append("Precio al contado inicial")
    if K is None:
        missing_fields.append("Precio de ejercicio")
    if rate is None:
        missing_fields.append("Tasa de interés")
    if volatility is None:
        missing_fields.append("Volatilidad")
    if date_value is None or date_expiration is None:
        missing_fields.append("Fechas (actual y de vencimiento)")

    if missing_fields:
        error_message = html.Div([
            html.H4("Error de entrada:", style={'color': 'red'}),
            html.P("Los siguientes campos están vacíos y son requeridos: " + ", ".join(missing_fields), style={'color': 'red'})
        ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px', 'margin-right': '20px'})
        return go.Figure(), "", error_message

    # Convertir las fechas a objetos datetime y verificar su validez
    try:
        date_value = datetime.strptime(date_value, '%Y-%m-%d')
        date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')
        if date_expiration <= date_value:
            raise ValueError("La fecha de vencimiento debe ser posterior a la fecha actual.")
    except ValueError as e:
        error_message = html.Div([
            html.H4("Error de Fecha:", style={'color': 'red'}),
            html.P(str(e), style={'color': 'red'})
        ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px', 'margin-right': '20px'})
        return go.Figure(), "", error_message

    # Cálculo de T, tasas y volatilidad
    T = (date_expiration - date_value).days / 365.0
    rate /= 100
    volatility /= 100
    num_steps = 365

    times, option_prices = plot_option_evolution(S, K, rate, volatility, T, num_steps, option_type)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=option_prices, mode='lines', name='Black-Scholes'))
    output_text = f"El precio de la opción {option_type} usando Black-Scholes es: {option_prices[-1]:.2f}"

    if button_id == 'button-monte-carlo':
        _, mean_payoffs = monte_carlo_simulation(S, K, rate, T, volatility, option_type, M)
        fig.add_trace(go.Scatter(x=times, y=mean_payoffs, mode='lines', name='Monte Carlo'))
        output_text += f" | El precio promedio de la opción {option_type} usando Monte Carlo es: {mean_payoffs[-1]:.2f}"

    fig.update_layout(title=f'Evolución del Precio de la Opción {option_type.capitalize()}',
                      xaxis_title='Tiempo hasta la Expiración (Años)',
                      yaxis_title='Precio de la Opción')

    return fig, output_text, html.Div()

