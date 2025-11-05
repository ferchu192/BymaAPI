import requests
from bs4 import BeautifulSoup


def obtener_cotizacion_dolar(url, nombre_dolar):
    """
    Hace scraping de una página de Cronista para obtener el valor y variación de un tipo de dólar.

    Args:
        url (str): URL de la página a scrapear
        nombre_dolar (str): Nombre del tipo de dólar (Oficial, Blue, MEP, CCL)

    Returns:
        dict: Diccionario con el formato {dollar: str, precio: float, variacion: str}
    """
    try:
        # Realizar la petición HTTP
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parsear el HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar el valor de venta
        venta_element = soup.find('div', class_='markets-online__card--sell')
        precio_text = None
        if venta_element:
            # Buscar el div que contiene el precio (segundo div dentro)
            divs = venta_element.find_all('div')
            if len(divs) > 1:
                precio_text = divs[1].text.strip()

        # Buscar la variación
        variacion_element = soup.find('div', class_='markets-online__card--percentage')
        variacion_text = None
        if variacion_element:
            # Buscar el div que contiene la variación (segundo div dentro)
            divs = variacion_element.find_all('div')
            if len(divs) > 1:
                variacion_text = divs[1].text.strip()

        # Procesar el precio (remover $ y . para convertir a float)
        precio = None
        if precio_text:
            # Remover el símbolo $ y los puntos de miles
            precio_clean = precio_text.replace('$', '').replace('.', '').replace(',', '.').strip()
            try:
                precio = float(precio_clean)
            except ValueError:
                precio = precio_text

        # Construir el resultado
        resultado = {
            'dollar': nombre_dolar,
            'precio': precio,
            'variacion': variacion_text
        }

        return resultado

    except requests.RequestException as e:
        print(f"Error al realizar la petición para {nombre_dolar}: {e}")
        return {
            'dollar': nombre_dolar,
            'precio': None,
            'variacion': None,
            'error': str(e)
        }
    except Exception as e:
        print(f"Error inesperado para {nombre_dolar}: {e}")
        return {
            'dollar': nombre_dolar,
            'precio': None,
            'variacion': None,
            'error': str(e)
        }


def obtener_todos_los_dolares():
    """
    Obtiene las cotizaciones de todos los tipos de dólar disponibles en Cronista.

    Returns:
        dict: Diccionario con las cotizaciones de cada tipo de dólar
              Formato: {
                  'Oficial': {dollar: 'Oficial', precio: float, variacion: str},
                  'Blue': {dollar: 'Blue', precio: float, variacion: str},
                  'MEP': {dollar: 'MEP', precio: float, variacion: str},
                  'CCL': {dollar: 'CCL', precio: float, variacion: str}
              }
    """
    # Definir las URLs y nombres de cada tipo de dólar
    dolares = {
        'Oficial': 'https://www.cronista.com/MercadosOnline/moneda/ARS/',
        'Blue': 'https://www.cronista.com/MercadosOnline/moneda/ARSB/',
        'MEP': 'https://www.cronista.com/MercadosOnline/moneda/ARSMEP/',
        'CCL': 'https://www.cronista.com/MercadosOnline/moneda/ARSCONT/'
    }

    resultado = {}

    for nombre, url in dolares.items():
        print(f"Obteniendo cotización de dólar {nombre}...")
        cotizacion = obtener_cotizacion_dolar(url, nombre)
        resultado[nombre] = cotizacion

    return resultado


if __name__ == "__main__":
    # Ejemplo de uso: obtener todos los tipos de dólar
    resultado = obtener_todos_los_dolares()

    print("\n=== Cotizaciones del Dólar ===\n")
    for tipo, datos in resultado.items():
        if 'error' not in datos:
            print(f"{tipo}:")
            print(f"  Precio: ${datos['precio']}")
            print(f"  Variación: {datos['variacion']}")
        else:
            print(f"{tipo}: Error - {datos['error']}")
        print()
