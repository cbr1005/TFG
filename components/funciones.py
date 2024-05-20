import math




def calcular_opcion_estandar_precio(Spot, Strike, tasa_interes, fecha_valor, fecha_vencimiento, volatilidad, tipo_opcion="call"):
    # Cálculo de variables necesarias
    S = Spot
    K = Strike
    T = (fecha_vencimiento - fecha_valor).days / 365  # Tiempo hasta el vencimiento en años
    r = tasa_interes
    sigma = volatilidad
    Factor = math.exp(-r * T)  # Factor de descuento

    # Cálculo de los valores de d1 y d2 para el modelo de Black-Scholes
    d1 = (math.log(S / K) + (r - + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - (sigma * math.sqrt(T))

    # Cálculo de las probabilidades acumuladas y no acumuladas de d1 y d2
    Nd1 = norm_dist(d1, True)
    Ndd1 = norm_dist(d1, False)
    Nd2 = norm_dist(d2, True)

    # Cálculo del precio de la opción estándar
    precio_opcion = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    precio_opcion[0][0] = (math.exp(1 * T) * S * Nd1 - K * Factor * Nd2)
    precio_opcion[0][1] = Nd1 * math.exp(1 * T)
    precio_opcion[0][2] = Ndd1 * math.exp(1 * T) / (S * sigma * math.sqrt(T))
    precio_opcion[0][3] = Ndd1 * math.exp(1 * T) * S * math.sqrt(T)

    # Ajuste para opción put si es necesario
    if tipo_opcion.lower()[0] == "p":
        precio_opcion[0][0] = precio_opcion[0][0] - S * math.exp(1 * T) + K * Factor
        precio_opcion[0][1] = precio_opcion[0][1] - math.exp(1 * T)

    precio_opcion[1][0] = precio_opcion[0][1]
    precio_opcion[2][0] = precio_opcion[0][2]
    precio_opcion[3][0] = precio_opcion[0][3]

    return precio_opcion


def calcular_volatilidad_implícita(Spot, Strike, tasa_interes, fecha_valor, fecha_vencimiento, Precio, dividendos=0, tipo_opcion="call", precision=0.000001):
    # Inicialización de las volatilidades mínima y máxima
    vol_min = 0.00001
    vol_max = 200
    error = 1

    # Verificación de errores en el cálculo de la volatilidad implícita
    if error_vol_implícita_black_scholes(Spot, Strike, tasa_interes, dividendos, (fecha_vencimiento - fecha_valor).days / 365, Precio, tipo_opcion):
        return "ERROR"

    # Búsqueda de la volatilidad implícita utilizando el método de bisección
    while error > precision:
        precio1 = calcular_opcion_estandar_precio(Spot, Strike, tasa_interes, fecha_valor, fecha_vencimiento, vol_min, dividendos, tipo_opcion)
        precio2 = calcular_opcion_estandar_precio(Spot, Strike, tasa_interes, fecha_valor, fecha_vencimiento, vol_max, dividendos, tipo_opcion)
        volatilidad = (vol_min + vol_max) / 2
        precio_int = calcular_opcion_estandar_precio(Spot, Strike, tasa_interes, fecha_valor, fecha_vencimiento, volatilidad, dividendos, tipo_opcion)
        if (precio_int[0][0] - Precio) * (precio2[0][0] - Precio) > 0:
            vol_max = volatilidad
        else:
            vol_min = volatilidad
        error = abs(precio1[0][0] - precio2[0][0])

    return volatilidad


def calcular_opcion_black_76_precio(Forward, Strike, tasa_interes, fecha_valor, fecha_vencimiento, Volatilidad, tipo_opcion="call"):
    # Simplemente redirige la llamada a la función de cálculo de opción estándar para el modelo Black-76
    return calcular_opcion_estandar_precio(Forward, Strike, tasa_interes, fecha_valor, fecha_vencimiento, Volatilidad, tasa_interes, tipo_opcion)


def calcular_volatilidad_implícita_black_76(Forward, Strike, tasa_interes, fecha_valor, fecha_vencimiento, Precio, tipo_opcion="call", precision=0.000001):
    # Simplemente redirige la llamada a la función de cálculo de volatilidad implícita para el modelo Black-76
    return calcular_volatilidad_implícita(Forward, Strike, tasa_interes, fecha_valor, fecha_vencimiento, Precio, tasa_interes, tipo_opcion, precision)


def error_vol_implícita_black_scholes(Spot, Strike, tasa_interes, Dividendos, plazo, Precio, tipo_opcion):
    # Verifica si hay errores en los cálculos de la volatilidad implícita
    try:
        OutPut = False

        if tipo_opcion.lower()[0] == "c":
            if Precio < math.exp(-tasa_interes * plazo) * max(Spot * math.exp((tasa_interes - Dividendos) * plazo) - Strike, 0):
                OutPut = True
        elif tipo_opcion.lower()[0] == "p":
            if Precio < math.exp(-tasa_interes * plazo) * max(-Spot * math.exp((tasa_interes - Dividendos) * plazo) + Strike, 0):
                OutPut = True
        else:
            OutPut = True

        if Spot <= 0 or Strike <= 0 or plazo < 0 or Precio >= Spot:
            OutPut = True

    except:
        OutPut = True

    return OutPut


def norm_dist(x, cumulative=True):
    # Función auxiliar para calcular la función de distribución normal
    try:
        from scipy.stats import norm
        if cumulative:
            return norm.cdf(x)
        else:
            return norm.pdf(x)
    except ImportError:
        return "Scipy is required for normal distribution calculation."
