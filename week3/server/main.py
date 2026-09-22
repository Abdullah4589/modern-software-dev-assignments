from os import name
from mcp.server.fastmcp import FastMCP
import httpx
mcp=FastMCP("Weather Server")
def get_coordinates(city:str):
    url="https://geocoding-api.open-meteo.com/v1/search"
    params={
        "name":city,
        "count":1,
        "language":"en",
        "format":"json",
    }
    response=httpx.get(url,params=params,timeout=10.0)
    response.raise_for_status()

    data =response.json()
    results=data.get("results",[])

    if not results:
        return None

    place = results[0]

    return {
        "name": place["name"],
        "country": place.get("country", ""),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
    }




@mcp.tool()
def test_connection()-> str:
    """Check whether the MCP weather server is running."""
    return "Connection successful!"
@mcp.tool()
def get_current_weather(city: str) -> str:
      """Get the current weather for a city."""
      try:
          location = get_coordinates(city)
      except httpx.TimeoutException:
          return "The weather services took too long to respond. Please try again later."
      except httpx.HTTPStatusError as error:
          if error.response.status_code == 429:
              return "The weather service is busy. Please try again in a minute."
      except httpx.RequestError:
          return "Could not connect to the weather service. Please check your internet connection."
      if not location:
          return f"City {city} not found."
      url = "https://api.open-meteo.com/v1/forecast"
      params = {
          "latitude": location["latitude"],
          "longitude": location["longitude"],
          "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
      }
      response = httpx.get(url, params=params, timeout=10.0)
      response.raise_for_status()
      current = response.json().get("current", {})
      return (
      f"Current weather in {location['name']}, {location['country']}: "
      f"{current.get('temperature_2m')}°C, "
      f"feels like {current.get('apparent_temperature')}°C, "
      f"wind speed {current.get('wind_speed_10m')} km/h."
      )


@mcp.tool()
def get_weather_forecast(city: str, days: int = 3) -> str:
    """Get the weather forecast for a city in a readable format."""
    if days < 1 or days > 7:
        return "Please choose between 1 and 7 forecast days."
    try:
        location = get_coordinates(city)
    except httpx.TimeoutException:
        return "The weather services took too long to respond. Please try again later."
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 429:
            return "The weather service is busy. Please try again in a minute."
    except httpx.RequestError:
        return "Could not connect to the weather service. Please check your internet connection."
    if not location:
        return f"City {city} not found."

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
          "latitude": location["latitude"],
          "longitude": location["longitude"],
          "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
          "timezone": "auto",
          "forecast_days": days,
      }
    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()
    daily = response.json().get("daily", {})

    dates = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    rain_chances = daily.get("precipitation_probability_max", [])
    weather_codes = daily.get("weather_code", [])

    forecast_lines = []
    for index, date in enumerate(dates):
        high = highs[index] if index < len(highs) else "N/A"
        low = lows[index] if index < len(lows) else "N/A"
        rain_chance = (
            rain_chances[index] if index < len(rain_chances) else "N/A"
        )
        weather_code = (
            weather_codes[index] if index < len(weather_codes) else "N/A"
        )
        forecast_lines.append(
            f"{date}: high {high}°C, low {low}°C, "
            f"precipitation chance {rain_chance}%, weather code {weather_code}"
        )

    return (
        f"Weather forecast for {location['name']}, {location['country']}:\n"
        + "\n".join(forecast_lines)
    )
if __name__ == "__main__":
    mcp.run(transport="stdio")