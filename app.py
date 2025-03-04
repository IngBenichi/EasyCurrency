from fastapi import FastAPI
import requests
import os

app = FastAPI()

# Clave API de ExchangeRate-API (Regístrate y obtén una gratis)
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

# Cache de tasas de cambio
exchange_rates = {}

@app.get("/convert")
def convert_currency(from_currency: str, to_currency: str, amount: float):
    if not exchange_rates:
        response = requests.get(BASE_URL).json()
        exchange_rates.update(response["conversion_rates"])

    if from_currency not in exchange_rates or to_currency not in exchange_rates:
        return {"error": "Moneda no soportada"}

    rate = exchange_rates[to_currency] / exchange_rates[from_currency]
    converted_amount = amount * rate

    return {
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "converted_amount": round(converted_amount, 2),
        "rate": round(rate, 4)
    }

@app.get("/rates")
def get_rates():
    if not exchange_rates:
        response = requests.get(BASE_URL).json()
        exchange_rates.update(response["conversion_rates"])
    return exchange_rates
