import os
from fastapi import FastAPI, HTTPException, Query
import httpx

# Replace "your_api_key_here" with your actual OpenWeatherMap API key
API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
app = FastAPI(title="Weather API - Selected Fields")

@app.get("/weather", summary="Get selected weather and air quality data")
async def get_weather(city: str = Query(..., description="Name of the city")):
    async with httpx.AsyncClient() as client:
        # 1. Get the coordinates for the city using the geocoding API
        geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geocode_response = await client.get(geocode_url)
        if geocode_response.status_code != 200:
            raise HTTPException(
                status_code=geocode_response.status_code,
                detail="Error retrieving geocoding data"
            )
        geo_data = geocode_response.json()
        if not geo_data:
            raise HTTPException(status_code=404, detail="City not found")
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # 2. Get the weather data for the coordinates
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        weather_response = await client.get(weather_url)
        if weather_response.status_code != 200:
            raise HTTPException(
                status_code=weather_response.status_code,
                detail="Error retrieving weather data"
            )
        weather_data = weather_response.json()

        # 3. Get the air quality data for the same coordinates
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        air_response = await client.get(air_url)
        if air_response.status_code != 200:
            raise HTTPException(
                status_code=air_response.status_code,
                detail="Error retrieving air quality data"
            )
        air_data = air_response.json()

    # 4. Extract the required fields from the responses
    main_data = weather_data.get("main", {})
    temperature = main_data.get("temp")
    feels_like = main_data.get("feels_like")
    temp_min = main_data.get("temp_min")
    temp_max = main_data.get("temp_max")
    humidity = main_data.get("humidity")
    # 'weather' is a list; we take the description from the first item
    weather_description = weather_data.get("weather", [{}])[0].get("description", "No description")
    # Extract AQI from air_data (expected structure: {"list": [{"main": {"aqi": value}}]})
    aqi = air_data.get("list", [{}])[0].get("main", {}).get("aqi")
    
    # 5. Return only the selected data as the response
    # return {
    #     "city": city,
    #     "temperature": temperature,
    #     "feels_like": feels_like,
    #     "temp_min": temp_min,
    #     "temp_max": temp_max,
    #     "humidity": humidity,
    #     "weather_description": weather_description,
    #     "aqi": aqi
    # }
    return {
    "city": city,
    "temperature": {"value": temperature, "unit": "°C"},
    "feels_like": {"value": feels_like, "unit": "°C"},
    "temp_min": {"value": temp_min, "unit": "°C"},
    "temp_max": {"value": temp_max, "unit": "°C"},
    "humidity": {"value": humidity, "unit": "%"},
    "weather_description": weather_description,
    "aqi": {"value": aqi, "unit": "AQI (1(Best)-5(Worst) scale)"}
}
