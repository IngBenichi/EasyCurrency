from fastapi import FastAPI, HTTPException, Depends, Request
import requests
import os
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

load_dotenv()


app = FastAPI()

# Configuración de Jinja2 para plantillas
templates = Jinja2Templates(directory="templates")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes cambiarlo por dominios específicos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


# Configuración del limitador de peticiones (máx. 5 por minuto por IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Clave API de ExchangeRate-API (Debes configurarla en tu entorno)
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

# Cache de tasas de cambio
exchange_rates = {}
cache_expiration = datetime.utcnow()

@app.get("/")
@limiter.limit("5/minute")  # Máx. 5 solicitudes por minuto
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def fetch_exchange_rates():
    """Obtiene tasas de cambio y actualiza la cache."""
    global exchange_rates, cache_expiration
    try:
        response = requests.get(BASE_URL, timeout=10)  # Timeout de 10s
        response.raise_for_status()
        data = response.json()

        if "conversion_rates" not in data:
            raise HTTPException(status_code=500, detail="Datos de tasas de cambio no disponibles.")

        exchange_rates = data["conversion_rates"]
        cache_expiration = datetime.utcnow() + timedelta(hours=24)  # Caché válida por 24 horas

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error al obtener tasas de cambio: {str(e)}")

@app.get("/convert")
@limiter.limit("5/minute")  # Máx. 5 solicitudes por minuto
def convert_currency(request: Request, from_currency: str, to_currency: str, amount: float):
    """Convierte una cantidad de una moneda a una o más monedas."""
    if datetime.utcnow() > cache_expiration or not exchange_rates:
        fetch_exchange_rates()

    to_currency_list = to_currency.split(",")

    conversions = {}
    for currency in to_currency_list:
        if currency not in exchange_rates:
            raise HTTPException(status_code=400, detail=f"Moneda no soportada: {currency}")

        rate = exchange_rates[currency] / exchange_rates.get(from_currency, 1)
        conversions[currency] = round(amount * rate, 2)

    return JSONResponse(content={
        "status": "success",
        "message": "Conversión realizada exitosamente.",
        "data": {
            "from": from_currency,
            "amount": amount,
            "conversions": conversions
        }
    })

@app.get("/rates")
@limiter.limit("5/minute")  # Máx. 5 solicitudes por minuto
def get_rates(request: Request):
    """Obtiene todas las tasas de cambio disponibles."""
    if datetime.utcnow() > cache_expiration or not exchange_rates:
        fetch_exchange_rates()

    return JSONResponse(content={
        "status": "success",
        "message": "Tasas de cambio obtenidas correctamente.",
        "data": exchange_rates
    })
