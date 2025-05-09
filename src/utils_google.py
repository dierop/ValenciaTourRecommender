# src/utils_google.py ----------------------------------------------------------
import requests
api_key = open('api-key-maps.txt').read().strip()

def get_place_details(place_name, api_key=api_key):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{place_name} in Valencia, Spain",
        "key":   api_key,
        "language": "es",
    }
    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("results"):
            return "Sin resultados"

        place            = data["results"][0]
        nombre           = place.get("name", "N/A")
        direccion        = place.get("formatted_address", "N/A")
        abierto          = place.get("opening_hours", {}).get("open_now", "Sin información")
        abierto = {True:"Sí", False:"No"}.get(abierto, abierto)
        valoracion       = place.get("rating", "N/A")
        n_valoraciones   = place.get("user_ratings_total", "N/A")

        return nombre, direccion, abierto, valoracion, n_valoraciones

    except requests.exceptions.RequestException as e:
        return f"Error Google Maps: {e}"
