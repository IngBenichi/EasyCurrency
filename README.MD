# Exchange Rate API

## Descripción
Esta API permite convertir una cantidad de dinero de una moneda a otra utilizando tasas de cambio en tiempo real. La API obtiene los datos de `ExchangeRate-API` y almacena en caché las tasas de cambio durante 1 hora para mejorar el rendimiento. Además, se ha implementado una limitación de peticiones para evitar abuso del servicio y se han mejorado los mensajes de respuesta de los endpoints.

## Tecnologías Utilizadas
- **FastAPI** - Framework para la creación de la API.
- **Requests** - Para realizar solicitudes a la API de tasas de cambio.
- **JSONResponse** - Para estructurar las respuestas de la API.
- **Limiter** - Para restringir el número de peticiones permitidas por IP.
- **Cache** - Para almacenar las tasas de cambio y reducir llamadas a la API externa.

## Instalación y Uso

1. **Clonar el repositorio**:
    ```sh
    git clone https://github.com/tu_usuario/exchange-rate-api.git
    cd exchange-rate-api
    ```
2. **Crear un entorno virtual e instalar dependencias**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3. **Configurar la clave API**:
    - Obtener una API Key gratuita en [ExchangeRate-API](https://www.exchangerate-api.com/)
    - Crear un archivo `.env` en el directorio del proyecto:
      ```sh
      EXCHANGE_RATE_API_KEY=tu_api_key
      ```
4. **Ejecutar el servidor**:
    ```sh
    uvicorn main:app --reload
    ```

## Limitación de Peticiones
Para evitar abuso del servicio, se ha implementado un limitador de peticiones que restringe la cantidad de solicitudes que un usuario puede realizar en un período determinado. Por defecto:
- **5 solicitudes por minuto** por IP.
- Si se excede el límite, la API devuelve un error `429 Too Many Requests`.

## Endpoints

### 1. Obtener tasas de cambio
- **URL:** `/rates`
- **Método:** `GET`
- **Descripción:** Obtiene todas las tasas de cambio disponibles.
- **Respuesta Ejemplo:**
    ```json
    {
        "status": "success",
        "message": "Tasas de cambio obtenidas correctamente.",
        "data": {
            "USD": 1,
            "EUR": 0.92,
            "JPY": 150.2
        }
    }
    ```

### 2. Convertir moneda
- **URL:** `/convert`
- **Método:** `GET`
- **Parámetros:**
    - `from_currency` (str) - Moneda de origen.
    - `to_currency` (str) - Moneda(s) de destino (separadas por coma `,`).
    - `amount` (float) - Cantidad a convertir.
- **Ejemplo de uso:**
    ```sh
    curl "http://127.0.0.1:8000/convert?from_currency=USD&to_currency=EUR,JPY&amount=100"
    ```
- **Respuesta Ejemplo:**
    ```json
    {
        "status": "success",
        "message": "Conversión realizada exitosamente.",
        "data": {
            "from": "USD",
            "amount": 100,
            "conversions": {
                "EUR": 92.5,
                "JPY": 15020
            }
        }
    }
    ```

## Consideraciones
- La API almacena los tipos de cambio en caché durante 1 hora para evitar llamadas innecesarias a la API externa.
- Se han mejorado los mensajes de error para ofrecer una mejor experiencia de usuario.
- Si una moneda no es válida, devuelve un error con un mensaje claro.
- La limitación de peticiones protege la API contra abuso y uso excesivo.
- Si la API de ExchangeRate-API no responde o hay un error, se utilizan los últimos valores almacenados en caché.

## Licencia
Este proyecto está bajo la licencia MIT. Puedes usarlo y modificarlo según tus necesidades.

