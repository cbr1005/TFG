# # metodo_implicito.py
import numpy as np
from dash import Dash, html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from scipy.stats import norm
from scipy.linalg import solve_banded

# Definimos las funciones que nos proporcionaste para el modelo de precios de opciones
def pay_off(S, E, type):
    if type == "call":
        return np.maximum(S - E, 0)
    elif type == "put":
        return np.maximum(E - S, 0)

def implicit_fd(S_max, K, T, sigma, r, option_type, N, M):
    dt = T / M
    ds = S_max / N
    V = np.zeros((N+1, M+1))
    S = np.linspace(0, S_max, N+1)
    alpha = 0.5 * sigma**2 * dt / ds**2
    beta = r * dt / ds

    # Setup the coefficients for the tridiagonal matrix
    a = -alpha + beta / 2
    b = 1 + 2 * alpha + r * dt
    c = -alpha - beta / 2

    # Setup boundary conditions
    V[:, M] = pay_off(S, K, option_type)

    # Tridiagonal matrix
    ab = np.zeros((3, N-1))
    ab[0, 1:] = c
    ab[1, :] = b
    ab[2, :-1] = a

    for j in reversed(range(M)):
        # Right hand side
        rhs = V[1:N, j+1]
        # Apply boundary conditions
        rhs[0] -= a * V[0, j+1]
        rhs[-1] -= c * V[N, j+1]

        V[1:N, j] = solve_banded((1, 1), ab, rhs)

        # Boundary conditions at spatial edges
        V[0, j] = 0 if option_type == 'call' else K * np.exp(-r * (T - j*dt))
        V[N, j] = S_max - K * np.exp(-r * (T - j*dt)) if option_type == 'call' else 0

    return V, S, dt

def function_option_price(S, E, r, T, sigma, type):
    d1 = (np.log(S / E) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if type == 'call':
        return S * norm.cdf(d1) - E * np.exp(-r * T) * norm.cdf(d2)
    else:
        return E * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

layout = html.Div([
    html.H1("Simulación de Opciones con Diferencias Finitas Impicitas", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio máximo del subyacente:', className="input-label"),
            dcc.Input(id='S_max_i', type='number', placeholder='Ingrese valor inicial', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='K_i', type='number', placeholder='Ingrese precio del ejercicio', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tiempo hasta el vencimiento (en años):', className="input-label"),
            dcc.Input(id='T_i', type='number', placeholder='Ingrese numero de años', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='sigma_i', type='number', placeholder='Ingrese volatilidad', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa libre de riesgo (%):', className="input-label"),
            dcc.Input(id='r_i', type='number', placeholder='Ingrese tasa de interes', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tipo de opción:', className="input-label"),
            dcc.Dropdown(
                id='option_type_i',
                options=[
                    {'label': 'Call', 'value': 'call'},
                    {'label': 'Put', 'value': 'put'}
                ],
                value='call',
                className="dropdown"
            ),
        ]),
        html.Div(id='error-message_i', className="error-message-container"),
        html.Button('Calcular', id='calculate_i', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='option_graph_i'),
    html.Div(id='price_output_i')
], className="container")

# The callback function using implicit method
@callback(
    Output('option_graph_i', 'figure'),
    Output('price_output_i', 'children'),
    Output('error-message_i', 'children' ),
    Input('calculate_i', 'n_clicks'),
    State('S_max_i', 'value'),
    State('K_i', 'value'),
    State('T_i', 'value'),
    State('sigma_i', 'value'),
    State('r_i', 'value'),
    State('option_type_i', 'value')
)
def update_graph(n_clicks, S_max, K, T, sigma, r, option_type):
    if n_clicks > 0:
        sigma /= 100  # Convert percentage to decimal
        r /= 100  # Convert percentage to decimal
        N = 100
        M = 100
        try:
            V, S, dt = implicit_fd(S_max, K, T, sigma, r, option_type, N, M)
            initial_option_price = V[:, 0]
            bs_prices = [function_option_price(s, K, r, T, sigma, option_type) for s in S]
            error = np.abs(bs_prices - initial_option_price)

            # Create a Plotly graph for options
            option_figure = go.Figure()
            option_figure.add_trace(go.Scatter(x=S, y=initial_option_price, mode='lines', name='Método Implícito'))
            option_figure.add_trace(go.Scatter(x=S, y=bs_prices, mode='lines', name='Black-Scholes'))
            option_figure.update_layout(title='Comparación de precios de opción', xaxis_title='Precio del subyacente S', yaxis_title='Precio de la opción')

            # Price output
            price_output = f"Precio inicial con Implícito: {initial_option_price[int(N/2)]:.2f}, Black-Scholes: {bs_prices[int(N/2)]:.2f}, Diferencia: {abs(initial_option_price[int(N/2)] - bs_prices[int(N/2)]):.2f}"

            return option_figure, price_output, ""
        except ValueError as e:
            return go.Figure(), "", f"Error: {str(e)}"
    return go.Figure(), "", ""






# import numpy as np
# from scipy.linalg import solve_banded
# from dash import html, dcc, Input, Output, State, callback
# import plotly.graph_objs as go

# def implicit_fd(S_max, K, T, sigma, r, N, M, option_type):
#     dt = T / M
#     ds = S_max / N
#     V = np.zeros((N+1, M+1))
#     S = np.linspace(0, S_max, N+1)
    
#     # Condición inicial
#     if option_type == 'put':
#         V[:, M] = np.maximum(K - S, 0)
#     else:
#         V[:, M] = np.maximum(S - K, 0)
    
#     A = np.zeros((3, N-1))
#     for i in range(1, N):
#         A[0, i-1] = 0.5 * dt * (sigma**2 * (i*ds)**2 - r * (i*ds))  # Coeficiente superior
#         A[1, i-1] = 1 + dt * (sigma**2 * (i*ds)**2 + r)        # Coeficiente diagonal
#         A[2, i-1] = 0.5 * dt * (sigma**2 * (i*ds)**2 + r * (i*ds))  # Coeficiente inferior

#     for j in range(M-1, -1, -1):
#         B = V[1:N, j+1].copy()  # Copiar el vector B para asegurar que no se modifica V directamente
#         if option_type == 'put':
#             B[0] -= A[0, 0] * (K * np.exp(-r * (T - j*dt)))
#         else:
#             B[0] -= A[0, 0] * 0
        
#         # Comprobaciones para NaNs e Infs en A y B
#         if np.any(np.isnan(A)) or np.any(np.isnan(B)):
#             print("NaNs found in matrix A or vector B")
#             print("A:", A)
#             print("B:", B)
#             raise ValueError("NaNs found in matrix A or vector B")
#         if np.any(np.isinf(A)) or np.any(np.isinf(B)):
#             print("Infs found in matrix A or vector B")
#             print("A:", A)
#             print("B:", B)
#             raise ValueError("Infs found in matrix A or vector B")

#         V[1:N, j] = solve_banded((1, 1), A, B)
#         if option_type == 'put':
#             V[0, j] = K * np.exp(-r * (T - j*dt))
#             V[N, j] = 0
#         else:
#             V[0, j] = 0
#             V[N, j] = S_max - K * np.exp(-r * (T - j*dt))
    
#     return V, S, dt

# # Estructura de la página
# layout = html.Div([
#     html.H1("Simulación de Opciones con Diferencias Finitas Implícitas", className="text-center title"),
#     html.Div(className="input-container", children=[
#         html.Div(className="input-group", children=[
#             html.Label('Precio máximo del subyacente:', className="input-label"),
#             dcc.Input(id='S_max_i', type='number', placeholder='Ingrese valor inicial', className="input-field"),
#         ]),
#         html.Div(className="input-group", children=[
#             html.Label('Precio de ejercicio:', className="input-label"),
#             dcc.Input(id='K_i', type='number', placeholder='Ingrese precio del ejercicio', className="input-field"),
#         ]),
#         html.Div(className="input-group", children=[
#             html.Label('Volatilidad (%):', className="input-label"),
#             dcc.Input(id='sigma_i', type='number', placeholder='Ingrese volatilidad', className="input-field"),
#         ]),
#         html.Div(className="input-group", children=[
#             html.Label('Tasa libre de riesgo (%):', className="input-label"),
#             dcc.Input(id='r_i', type='number', placeholder='Ingrese tasa de interes', className="input-field"),
#         ]),
#         html.Div(className="input-group", children=[
#             html.Label('Divisiones en el espacio:', className="input-label"),
#             dcc.Input(id='N_i', type='number', placeholder='Ingrese numero de divisiones', className="input-field"),
#         ]),
#         html.Div(className="input-group", children=[
#             html.Label('Divisiones en el tiempo:', className="input-label"),
#             dcc.Input(id='M_i', type='number', placeholder='Ingrese numero de divisiones', className="input-field"),
#         ]),
#         html.Div(className="input-group", children=[
#             html.Label('Tiempo hasta el vencimiento (en años):', className="input-label"),
#             dcc.Input(id='T_i', type='number', placeholder='Ingrese numero de años', className="input-field"),
#         ]),
#         html.Div(className="input-group", children=[
#             html.Label('Tipo de opción:', className="input-label"),
#             dcc.Dropdown(
#                 id='option_type_i',
#                 options=[
#                     {'label': 'Call', 'value': 'call'},
#                     {'label': 'Put', 'value': 'put'}
#                 ],
#                 value='call',
#                 className="dropdown"
#             ),
#         ]),
#         html.Div(id='error-message-imp', className="error-message-container"),
#         html.Button('Calcular', id='calculate-button-implicit', n_clicks=0, className="calculate-button"),
#     ]),
#     dcc.Graph(id='option-graph-implicit', className="output-container"),
#     html.Div(id='explanation-graph-implicit', className="explanation-container"),
#     dcc.Graph(id='option-surface-implicit', className="output-container"),
#     html.Div(id='explanation-surface-implicit', className="explanation-container"),
# ], className="container")

# # Callback para actualizar el gráfico basado en los inputs del usuario
# @callback(
#     [Output('option-graph-implicit', 'figure'),
#      Output('explanation-graph-implicit', 'children'),
#      Output('option-surface-implicit', 'figure'),
#      Output('explanation-surface-implicit', 'children'),
#      Output('error-message-imp', 'children')],
#     [Input('calculate-button-implicit', 'n_clicks')],
#     [State('option_type_i', 'value'),
#      State('S_max_i', 'value'),
#      State('K_i', 'value'),
#      State('T_i', 'value'),
#      State('sigma_i', 'value'),
#      State('r_i', 'value'),
#      State('N_i', 'value'),
#      State('M_i', 'value')]
# )
# def update_graph_implicit(n_clicks, option_type, S_max, K, T, sigma, r, N, M):
#     if n_clicks == 0:
#         # When no clicks, return empty figures and explanations and no error message
#         return {}, "", {}, "", ""

#     # Check for missing input fields
#     missing_fields = []
#     if option_type is None:
#         missing_fields.append("Tipo de opción")
#     if S_max is None:
#         missing_fields.append("Precio máximo del subyacente S_max")
#     if K is None:
#         missing_fields.append("Precio de ejercicio K")
#     if T is None:
#         missing_fields.append("Tiempo hasta la madurez T")
#     if sigma is None:
#         missing_fields.append("Volatilidad sigma")
#     if r is None:
#         missing_fields.append("Tasa de interés r")
#     if N is None:
#         missing_fields.append("Número de divisiones en el espacio N")
#     if M is None:
#         missing_fields.append("Número de divisiones en el tiempo M")
    
#     if missing_fields:
#         error_message = html.Div([
#             html.H4("Error de entrada:", style={'color': 'red'}),
#             html.P("Los siguientes campos están vacíos y son requeridos: " + ", ".join(missing_fields), style={'color': 'red'})
#         ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px', 'margin-right': '20px'})
#         # Return empty figures and error message for each output
#         return {}, "", {}, "", error_message
    
#     V, S, dt = implicit_fd(S_max, K, T, sigma, r, N, M, option_type)
    
#     # Grafico del valor de la opción en el tiempo inicial
#     option_graph = {
#         'data': [go.Scatter(x=S, y=V[:, 0], mode='lines', name=f'Opción {option_type.capitalize()} Europea al tiempo inicial')],
#         'layout': go.Layout(title=f'Valor de la Opción {option_type.capitalize()} Europea en el Tiempo 0', xaxis={'title': 'Precio del Subyacente S'}, yaxis={'title': 'Valor de la Opción'})
#     }
    
#     # Explicación del gráfico
#     explanation_graph = html.Div(f"Este gráfico muestra el valor de la opción {option_type.capitalize()} Europea en el tiempo inicial (T=0) utilizando el método implícito de diferencias finitas. El precio del subyacente se representa en el eje X y el valor de la opción en el eje Y.")
    
#     # Grafico de la evolución temporal de la superficie del valor de la opción
#     t = np.linspace(0, T, M+1)
#     S_grid, t_grid = np.meshgrid(S, t)
#     surface_graph = {
#         'data': [go.Surface(z=V.T, x=S_grid, y=t_grid)],
#         'layout': go.Layout(title=f'Superficie del Valor de la Opción {option_type.capitalize()} Europea', scene={'xaxis': {'title': 'Precio del Subyacente S'}, 'yaxis': {'title': 'Tiempo'}, 'zaxis': {'title': 'Valor de la Opción'}})
#     }
    
#     # Explicación de la superficie
#     explanation_surface = html.Div(f"Esta gráfica muestra cómo evoluciona el valor de la opción {option_type.capitalize()} Europea a lo largo del tiempo y con diferentes precios del subyacente. La superficie tridimensional proporciona una visión completa de la dinámica temporal y espacial del valor de la opción.")
    
#     return option_graph, explanation_graph, surface_graph, explanation_surface,""
