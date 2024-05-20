from dash import html, dcc, callback, Input, Output, State
from datetime import datetime
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

def function_option_price(S, E, r, T, sigma, option_type):
    d1 = (np.log(S / E) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        option_price = S * norm.cdf(d1) - E * np.exp(-r * T) * norm.cdf(d2)
    else:
        option_price = E * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return option_price

def plot_option_evolution(S, E, r, sigma, t, T, num_steps, option_type):
    times = np.linspace(t, T, num_steps)
    option_prices = [function_option_price(S, E, r, T - ti, sigma, option_type) for ti in times]
    return times, option_prices

layout = html.Div([
    html.H1("Simulación de Carteras de Opciones", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio al contado:', className="input-label"),
            dcc.Input(id='input-spot', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='input-strike', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interes (%):', className="input-label"),
            dcc.Input(id='input-rate', type='number', value=2, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='input-volatility', type='number', value=20, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='input-date-value', date='2024-05-01', className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='input-date-expiration', date='2024-11-01', className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tipo de opcion:', className="input-label"),
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
        html.Button('Calcular Precio', id='button-calculate', n_clicks=0, className="calculate-button"),
    ]),
    html.Div(id='output-option-price', className="output-container"),
    dcc.Graph(id='option-evolution-graph', className="output-container"),
    html.Div(id='portfolio-simulation-conclusion', className="output-container")
], className="container")

@callback(
    [Output('output-option-price', 'children'),
     Output('option-evolution-graph', 'figure'),
     Output('portfolio-simulation-conclusion', 'children')],
    Input('button-calculate', 'n_clicks'),
    State('input-spot', 'value'),
    State('input-strike', 'value'),
    State('input-rate', 'value'),
    State('input-date-value', 'date'),
    State('input-date-expiration', 'date'),
    State('input-volatility', 'value'),
    State('input-option-type', 'value')
)
def update_output(n_clicks, spot, strike, rate, date_value, date_expiration, volatility, option_type):
    if n_clicks > 0:
        date_value = datetime.strptime(date_value, '%Y-%m-%d')
        date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')
        T = (date_expiration - date_value).days / 365
        t = 0
        num_steps = 100

        rate = rate / 100
        volatility = volatility / 100

        times, option_prices = plot_option_evolution(spot, strike, rate, volatility, t, T, num_steps, option_type)
        
        # Crear la gráfica
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=option_prices, mode='lines', name=f'{option_type.capitalize()} Option Price'))
        fig.update_layout(title=f"Evolución del Precio de la Opción {option_type.capitalize()}",
                          xaxis_title="Tiempo hasta la Expiración (Años)",
                          yaxis_title="Precio de la Opción")

        # Calcular el precio de la opción en el momento actual
        current_option_price = function_option_price(spot, strike, rate, T, volatility, option_type)

        # Conclusión personalizada
        conclusion_text = f"El precio calculado de la opción {option_type.capitalize()} en el momento actual es {current_option_price:.2f}."
        conclusion = html.Div([
            html.H4("Conclusión de la Simulación:"),
            html.P(conclusion_text),
            html.P("A medida que el tiempo pasa, la opción se vuelve más 'segura' en el sentido de que es muy probable que esté en el dinero al vencimiento. "
                   "Sin embargo, el valor adicional que los inversores están dispuestos a pagar por el tiempo restante (valor temporal) disminuye. "
                   "Dado que el tiempo restante hasta el vencimiento se reduce, el valor de la opción disminuye, reflejando la pérdida de valor temporal.")
        ])

        return html.Div([
            html.H4("Resultados de la Simulación:"),
            html.P(f"El precio calculado de la opción es: {current_option_price:.2f}")
        ]), fig, conclusion
    
    return html.Div(), go.Figure(), html.Div()


