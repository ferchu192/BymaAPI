import requests
from bs4 import BeautifulSoup


def obtener_dolar_oficial():
    """
    Hace scraping de la página de Cronista para obtener el valor del dólar oficial.

    Returns:
        dict: Diccionario con el formato {dollar: 'Oficial', precio: float, variacion: str}
    """
    url = "https://www.cronista.com/MercadosOnline/moneda/ARS/"

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
            'dollar': 'Oficial',
            'precio': precio,
            'variacion': variacion_text
        }

        return resultado

    except requests.RequestException as e:
        print(f"Error al realizar la petición: {e}")
        return {
            'dollar': 'Oficial',
            'precio': None,
            'variacion': None,
            'error': str(e)
        }
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {
            'dollar': 'Oficial',
            'precio': None,
            'variacion': None,
            'error': str(e)
        }


if __name__ == "__main__":
    # Ejemplo de uso
    resultado = obtener_dolar_oficial()
    print(resultado)
