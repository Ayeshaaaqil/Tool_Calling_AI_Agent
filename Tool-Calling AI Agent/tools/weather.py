import requests

def get_weather(city):
    """
    Fetches real-time weather data using Open-Meteo (Free, No API Key required).
    """
    try:
        # Step 1: Get Coordinates (Latitude & Longitude) for the city name
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            return {"error": f"City '{city}' not found. Please try a major city name."}
            
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        
        # Step 2: Get Current Weather using the coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        
        current = weather_data["current_weather"]
        
        # Mapping WMO Weather Codes to readable descriptions
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle",
            61: "Slight rain", 71: "Slight snow", 95: "Thunderstorm"
        }
        condition = weather_codes.get(current['weathercode'], "Cloudy/Clear")
        
        return {
            "location": location["name"],
            "country": location.get("country", "N/A"),
            "temperature": f"{current['temperature']}°C",
            "condition": condition,
            "windspeed": f"{current['windspeed']} km/h",
            "source": "Open-Meteo Free API"
        }
        
    except Exception as e:
        return {"error": f"Internal Tool Error: {str(e)}"}