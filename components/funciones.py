from dash import dcc, html
from scipy.stats import norm
import numpy as np
from datetime import datetime



def function_option_price(S, K, r, T, sigma, option_type):
    """
    Calcula el precio de una opción europea (compra o venta) utilizando el modelo de Black-Scholes.
    
    Parámetros:
        S (float): Precio actual del activo subyacente.
        K (float): Precio de ejercicio de la opción.
        r (float): Tasa de interés libre de riesgo (anual).
        T (float): Tiempo hasta el vencimiento de la opción (en años).
        sigma (float): Volatilidad del activo.
        option_type (str): Tipo de opción ('call' para compra, 'put' para venta).
    
    Devuelve:
        float: Precio calculado de la opción.
    """

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    

def plot_option_evolution(S, K, r, sigma, T, num_steps, option_type):
    """
    Calcula y devuelve los precios de una opción en diferentes momentos hasta su vencimiento.
    
    Parámetros:
        S (float): Precio actual del activo.
        K (float): Precio de ejercicio.
        r (float): Tasa de interés libre de riesgo.
        sigma (float): Volatilidad del activo.
        T (float): Tiempo total hasta el vencimiento en años.
        num_steps (int): Número de intervalos de tiempo para calcular el precio de la opción.
        option_type (str): Tipo de opción ('call' o 'put').
    
    Devuelve:
        tuple of lists: Dos listas, una con los tiempos y otra con los precios de la opción en esos tiempos.
    """

    times = np.linspace(0, T, num_steps)
    option_prices = [function_option_price(S, K, r, T - ti, sigma, option_type) for ti in times]
    return times, option_prices

def monte_carlo_simulation(S, K, r, T, sigma, option_type, M):
    """
    Realiza una simulación de Monte Carlo para estimar el precio de una opción a través de la simulación de precios del activo subyacente.
    
    Parámetros:
        S (float): Precio inicial del activo.
        K (float): Precio de ejercicio de la opción.
        r (float): Tasa de interés libre de riesgo.
        T (float): Tiempo hasta el vencimiento de la opción en años.
        sigma (float): Volatilidad del activo.
        option_type (str): Tipo de la opción ('call' o 'put').
        M (int): Número de simulaciones a realizar.
    
    Devuelve:
        tuple of lists: Tiempos en los que se evalúa el precio y el valor esperado de los pagos de la opción.
    """

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


def simulate_gbm(S0, r, sigma, T, M, I):
    """
    Simula múltiples trayectorias de precios para un activo usando el modelo geométrico de movimiento browniano.
    
    Parámetros:
        S0 (float): Precio inicial del activo.
        r (float): Tasa de interés libre de riesgo.
        sigma (float): Volatilidad del activo.
        T (float): Duración del período de simulación.
        M (int): Número de pasos temporales en la simulación.
        I (int): Número de caminos independientes a simular.
    
    Devuelve:
        numpy.ndarray: Una matriz que contiene todas las trayectorias de precios simuladas.
    """

    dt = T / M
    paths = np.zeros((M + 1, I))
    paths[0] = S0
    for t in range(1, M + 1):
        z = np.random.standard_normal(I)
        paths[t] = paths[t - 1] * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)
    return paths

def monte_carlo_option_pricing(S0, E, r, sigma, T, M, I):
    """
    Calcula el precio de opciones de compra y venta utilizando el método de Monte Carlo a partir de trayectorias simuladas.
    
    Parámetros:
        S0 (float): Precio inicial del activo.
        E (float): Precio de ejercicio de las opciones.
        r (float): Tasa de interés libre de riesgo.
        sigma (float): Volatilidad del activo.
        T (float): Tiempo hasta el vencimiento de la opción.
        M (int): Número de pasos temporales en la simulación.
        I (int): Número de caminos simulados.
    
    Devuelve:
        tuple (float, float): Precio de la opción de compra y venta calculados.
    """

    paths = simulate_gbm(S0, r, sigma, T, M, I)
    S_T = paths[-1]
    call_payoff = np.maximum(S_T - E, 0)
    put_payoff = np.maximum(E - S_T, 0)
    call_price = np.exp(-r * T) * np.mean(call_payoff)
    put_price = np.exp(-r * T) * np.mean(put_payoff)
    return call_price, put_price




def determine_optimal_strategy(spot, strike, rate, volatility, date_value, date_expiration, option_type):
    """
    Determines the optimal options strategy based on market conditions and option parameters.
    """
    # Define volatility thresholds
    high_volatility_threshold = 25
    low_volatility_threshold = 15
    
    # Calculate the number of days to expiration
    days_to_expiration = (date_expiration - date_value).days
    
    # Calculate expected price movement
    expected_price_movement = (volatility / 100) * spot * np.sqrt(days_to_expiration / 365.25)
    price_movement_threshold = 0.1 * spot  # 10% of spot price

    # Debugging output
    print(f"Volatility: {volatility}, Expected Price Movement: {expected_price_movement}, Threshold: {price_movement_threshold}")

    if volatility > high_volatility_threshold:
        if expected_price_movement > price_movement_threshold:
            return 'Straddle'
        else:
            return 'Strangle'
    elif volatility < low_volatility_threshold:
        if expected_price_movement < price_movement_threshold:
            return 'Butterfly Spread'
    else:
        # Check relative position of spot to strike
        if spot >= strike:
            return 'Bull Spread'
        else:
            return 'Bear Spread'


def add_volatility_input(n_clicks, children):
    """
    Añade un campo de entrada para la volatilidad a una interfaz de usuario web de forma dinámica.
    
    Parámetros:
        n_clicks (int): Número de clics realizados, usado para indexar el nuevo campo de entrada.
        children (list): Lista actual de elementos HTML en la interfaz.
    
    Devuelve:
        list: Lista actualizada de elementos HTML con el nuevo campo de entrada añadido.
    """

    new_element = html.Div([
        dcc.Input(
            id={'type': 'volatility_input', 'index': n_clicks},
            type='number', placeholder='Volatilidad %',
            style={'marginRight': '5px', 'width': '200px'}
        )
    ])
    children.append(new_element)
    return children

def apply_visual_offset(prices, index):
    """
    Aplica un desplazamiento visual a una lista de precios para mejorar la visualización en gráficos.
    
    Parámetros:
        prices (list of float): Lista de precios originales.
        index (int): Índice utilizado para calcular el desplazamiento basado en el máximo de los precios.
    
    Devuelve:
        list of float: Lista de precios ajustados con el desplazamiento aplicado.
    """
    offset = index * 0.05 * max(prices)  
    return [price + offset for price in prices]

