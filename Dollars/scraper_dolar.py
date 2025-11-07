import requests
from bs4 import BeautifulSoup
from datetime import datetime, time as dt_time
import pytz

TIMEZONE = pytz.timezone('America/Argentina/Buenos_Aires')

def obtener_cotizacion_dolar(url, nombre_dolar):
    """
    Hace scraping de una página de Cronista para obtener el valor y variación de un tipo de dólar.

    Args:
        url (str): URL de la página a scrapear
        nombre_dolar (str): Nombre del tipo de dólar (Oficial, Blue, MEP, CCL)

    Returns:
        dict: Diccionario con el formato {dollar: str, compra: float, venta: float, variacion: str, time: str}
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

        # Buscar todos los elementos con la clase markets-online__card__title
        card_titles = soup.find_all('div', class_='markets-online__card__title')

        # Buscar el precio de compra (4to elemento con la clase)
        precio_compra_text = None
        if len(card_titles) >= 4:
            compra_parent = card_titles[3].parent
            divs = compra_parent.find_all('div')
            if len(divs) > 1:
                precio_compra_text = divs[1].text.strip()

        # Buscar el valor de venta
        venta_element = soup.find('div', class_='markets-online__card--sell')
        precio_venta_text = None
        if venta_element:
            # Buscar el div que contiene el precio (segundo div dentro)
            divs = venta_element.find_all('div')
            if len(divs) > 1:
                precio_venta_text = divs[1].text.strip()

        # Buscar la variación
        variacion_element = soup.find('div', class_='markets-online__card--percentage')
        variacion_text = None
        if variacion_element:
            # Buscar el div que contiene la variación (segundo div dentro)
            divs = variacion_element.find_all('div')
            if len(divs) > 1:
                variacion_text = divs[1].text.strip()

        # Procesar el precio de compra
        precio_compra = None
        if precio_compra_text:
            precio_clean = precio_compra_text.replace('$', '').replace('.', '').replace(',', '.').strip()
            try:
                precio_compra = float(precio_clean)
            except ValueError:
                precio_compra = precio_compra_text

        # Procesar el precio de venta
        precio_venta = None
        if precio_venta_text:
            # Remover el símbolo $ y los puntos de miles
            precio_clean = precio_venta_text.replace('$', '').replace('.', '').replace(',', '.').strip()
            try:
                precio_venta = float(precio_clean)
            except ValueError:
                precio_venta = precio_venta_text

        # Construir el resultado
        now = datetime.now(TIMEZONE)

        resultado = {
            'dollar': nombre_dolar,
            'compra': precio_compra,
            'venta': precio_venta,
            'precio': precio_venta,
            'variacion': variacion_text,
            'time': now.strftime("%H:%M:%S")
        }

        return resultado

    except requests.RequestException as e:
        print(f"Error al realizar la petición para {nombre_dolar}: {e}")
        return {
            'dollar': nombre_dolar,
            'compra': None,
            'venta': None,
            'precio': None,
            'variacion': None,
            'error': str(e)
        }
    except Exception as e:
        print(f"Error inesperado para {nombre_dolar}: {e}")
        return {
            'dollar': nombre_dolar,
            'compra': None,
            'venta': None,
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
                  'Oficial': {dollar: 'Oficial', compra: float, venta: float, variacion: str, time: str},
                  'Blue': {dollar: 'Blue', compra: float, venta: float, variacion: str, time: str},
                  'MEP': {dollar: 'MEP', compra: float, venta: float, variacion: str, time: str},
                  'CCL': {dollar: 'CCL', compra: float, venta: float, variacion: str, time: str}
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
            print(f"  Compra: ${datos['compra']}")
            print(f"  Venta: ${datos['venta']}")
            print(f"  Variación: {datos['variacion']}")
            print(f"  Hora: {datos['time']}")
        else:
            print(f"{tipo}: Error - {datos['error']}")
        print()
