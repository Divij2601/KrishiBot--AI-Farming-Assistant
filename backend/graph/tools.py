"""Tool implementations used by the KrishiBot LangGraph agent."""

from __future__ import annotations

import re
from typing import Any, Dict

import requests
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

from backend.config import OPENWEATHER_API_KEY, TAVILY_API_KEY


def _format_search_results(results: Any) -> str:
    """Normalize Tavily results into a readable text block."""

    if not results:
        return "No relevant results were found."

    if isinstance(results, str):
        return results

    formatted_results = []
    for idx, item in enumerate(results, start=1):
        if isinstance(item, dict):
            title = item.get("title", "Untitled result")
            content = item.get("content", "No summary available.")
            url = item.get("url", "No URL provided")
            formatted_results.append(
                f"{idx}. {title}\nSummary: {content}\nSource: {url}"
            )
        else:
            formatted_results.append(f"{idx}. {item}")
    return "\n\n".join(formatted_results)


def _extract_first_price(text: str) -> str | None:
    """Extract a market price mention from free text if available."""

    patterns = [
        r"(?:Rs\.?|INR|₹)\s?[\d,]+(?:\.\d+)?\s*(?:per\s+quintal|/quintal|quintal)?",
        r"[\d,]+(?:\.\d+)?\s*(?:Rs\.?|INR|₹)\s*(?:per\s+quintal|/quintal|quintal)?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


@tool
def web_search_tool(query: str) -> str:
    """Search the web for real-time agricultural information, pest identification, disease control, market prices, farming news, and agronomic research."""

    if not TAVILY_API_KEY:
        return "Tavily API key is not configured. Please add TAVILY_API_KEY to your environment."

    try:
        search_tool = TavilySearchResults(max_results=5)
        results = search_tool.invoke({"query": query})
        return _format_search_results(results)
    except Exception as exc:  # pragma: no cover
        return f"Unable to complete the web search right now: {exc}"


@tool
def get_weather_tool(location: str) -> str:
    """Get the current weather for a farming location, including temperature, humidity, weather condition, wind speed, and a farming-relevant interpretation."""

    if not OPENWEATHER_API_KEY:
        return "OpenWeather API key is not configured. Please add OPENWEATHER_API_KEY to your environment."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": OPENWEATHER_API_KEY, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.HTTPError:
        error_message = "Could not fetch weather data for that location. Please check the city name and try again."
        try:
            api_message = response.json().get("message")
            if api_message:
                error_message = f"Weather service error: {api_message}"
        except Exception:
            pass
        return error_message
    except requests.RequestException as exc:
        return f"Weather service is currently unreachable: {exc}"

    temperature = data.get("main", {}).get("temp")
    humidity = data.get("main", {}).get("humidity")
    condition = data.get("weather", [{}])[0].get("description", "unknown")
    wind_speed = data.get("wind", {}).get("speed")
    city_name = data.get("name", location)

    interpretation = []
    if humidity is not None:
        if humidity >= 80:
            interpretation.append("High humidity may increase fungal disease risk.")
        elif humidity <= 35:
            interpretation.append("Low humidity can increase crop water stress.")
    if temperature is not None:
        if temperature >= 35:
            interpretation.append("Hot conditions may require more frequent irrigation and heat stress monitoring.")
        elif temperature <= 10:
            interpretation.append("Cool temperatures may slow crop growth and germination.")
    if wind_speed is not None and wind_speed >= 8:
        interpretation.append("Strong wind can increase evapotranspiration and lodging risk in taller crops.")
    if not interpretation:
        interpretation.append("Current conditions look broadly manageable, but continue routine field monitoring.")

    return (
        f"Current weather for {city_name}:\n"
        f"- Temperature: {temperature} deg C\n"
        f"- Humidity: {humidity}%\n"
        f"- Condition: {condition}\n"
        f"- Wind Speed: {wind_speed} m/s\n"
        f"- Farming Interpretation: {' '.join(interpretation)}"
    )


_CROP_CALENDAR: Dict[str, Dict[str, str | int]] = {
    "wheat": {"sowing": "October to December", "harvest": "March to May", "duration": 120, "temp": "10-25 deg C", "water": "medium"},
    "rice": {"sowing": "June to July", "harvest": "October to November", "duration": 120, "temp": "20-35 deg C", "water": "high"},
    "maize": {"sowing": "June to July or January to February", "harvest": "September to October or April to May", "duration": 100, "temp": "18-27 deg C", "water": "medium"},
    "tomato": {"sowing": "Throughout the year depending on region", "harvest": "70-90 days after transplanting", "duration": 85, "temp": "18-30 deg C", "water": "medium"},
    "potato": {"sowing": "October to November", "harvest": "January to March", "duration": 100, "temp": "15-22 deg C", "water": "medium"},
    "onion": {"sowing": "October to November or January to February", "harvest": "90-150 days after sowing", "duration": 130, "temp": "13-25 deg C", "water": "medium"},
    "cotton": {"sowing": "April to June", "harvest": "October to January", "duration": 180, "temp": "21-30 deg C", "water": "medium"},
    "sugarcane": {"sowing": "February to April or September to October", "harvest": "10-18 months after planting", "duration": 330, "temp": "20-32 deg C", "water": "high"},
    "soybean": {"sowing": "June to July", "harvest": "October to November", "duration": 110, "temp": "20-30 deg C", "water": "medium"},
    "sunflower": {"sowing": "January to February or June to July", "harvest": "April to May or September to October", "duration": 95, "temp": "20-25 deg C", "water": "low"},
    "millet": {"sowing": "June to July", "harvest": "September to October", "duration": 85, "temp": "25-35 deg C", "water": "low"},
    "sorghum": {"sowing": "June to July or September to October", "harvest": "September to October or January to February", "duration": 110, "temp": "26-34 deg C", "water": "low"},
    "barley": {"sowing": "October to November", "harvest": "March to April", "duration": 120, "temp": "12-25 deg C", "water": "low"},
    "mustard": {"sowing": "October to November", "harvest": "February to March", "duration": 115, "temp": "10-25 deg C", "water": "low"},
    "chickpea": {"sowing": "October to November", "harvest": "February to March", "duration": 110, "temp": "15-30 deg C", "water": "low"},
}


@tool
def get_crop_calendar_tool(crop: str, hemisphere: str = "northern") -> str:
    """Look up the sowing window, harvest window, crop duration, ideal temperature range, and water requirement for a common crop."""

    crop_key = crop.strip().lower()
    crop_data = _CROP_CALENDAR.get(crop_key)
    if not crop_data:
        supported = ", ".join(sorted(_CROP_CALENDAR.keys()))
        return f"Crop calendar data is not available for '{crop}'. Supported crops are: {supported}."

    season_note = (
        "The listed seasons are based on northern hemisphere farming patterns."
        if hemisphere.strip().lower() == "northern"
        else "These seasons should be adjusted to the local cropping calendar for the southern hemisphere."
    )
    return (
        f"Crop calendar for {crop.title()}:\n"
        f"- Sowing Season: {crop_data['sowing']}\n"
        f"- Harvesting Season: {crop_data['harvest']}\n"
        f"- Duration: {crop_data['duration']} days\n"
        f"- Ideal Temperature Range: {crop_data['temp']}\n"
        f"- Water Requirement: {crop_data['water']}\n"
        f"- Note: {season_note}"
    )


_SOIL_RECOMMENDATIONS: Dict[str, Dict[str, str]] = {
    "clay": {"npk": "2:1:1", "ph": "6.5-7.5", "organic": "Add compost to improve structure and aeration.", "drainage": "Ensure raised beds or drainage channels to avoid waterlogging."},
    "sandy": {"npk": "1:1:1 with split nitrogen", "ph": "5.8-6.8", "organic": "Add farmyard manure or compost regularly to improve water holding.", "drainage": "Drainage is usually good; focus on moisture retention instead."},
    "loamy": {"npk": "2:1:1 balanced program", "ph": "6.0-7.0", "organic": "Maintain organic matter with crop residue incorporation and compost.", "drainage": "Generally well drained; avoid compaction."},
    "silty": {"npk": "2:1:1", "ph": "6.2-7.0", "organic": "Use cover crops to improve aggregate stability.", "drainage": "Prevent crusting and provide moderate drainage support."},
    "peaty": {"npk": "1:2:1", "ph": "5.5-6.5", "organic": "Organic matter is naturally high; focus on balanced mineral supplementation.", "drainage": "Improve drainage to reduce root disease risk."},
    "chalky": {"npk": "2:1.5:1", "ph": "6.5-7.5", "organic": "Use compost and micronutrient-rich organics to offset nutrient lock-up.", "drainage": "Usually free draining; monitor moisture stress."},
    "saline": {"npk": "1.5:1:2", "ph": "6.5-8.0", "organic": "Apply well-decomposed organic matter and gypsum where locally recommended.", "drainage": "Good drainage and periodic leaching are important to reduce salt buildup."},
}

_CROP_NPK_ADJUSTMENTS: Dict[str, str] = {
    "rice": "Rice benefits from steady nitrogen supply and careful water management.",
    "wheat": "Wheat usually responds well to split nitrogen applications.",
    "maize": "Maize often needs higher nitrogen during vegetative growth.",
    "tomato": "Tomato benefits from balanced potassium for fruit development.",
    "potato": "Potato often needs more potassium for tuber bulking.",
    "cotton": "Cotton requires balanced nutrition with attention to potassium.",
    "mustard": "Mustard can benefit from sulfur along with core NPK nutrition.",
    "chickpea": "Chickpea needs modest nitrogen and adequate phosphorus for nodulation.",
}


@tool
def soil_npk_advisor_tool(soil_type: str, crop: str) -> str:
    """Provide a rule-based NPK ratio, pH target, organic matter advice, and drainage guidance based on soil type and crop."""

    soil_key = soil_type.strip().lower()
    soil_data = _SOIL_RECOMMENDATIONS.get(soil_key)
    if not soil_data:
        supported = ", ".join(sorted(_SOIL_RECOMMENDATIONS.keys()))
        return f"Unsupported soil type '{soil_type}'. Supported soil types are: {supported}."

    crop_note = _CROP_NPK_ADJUSTMENTS.get(
        crop.strip().lower(),
        "Use local soil testing to fine-tune the recommendation for this crop.",
    )
    return (
        f"Soil advisory for {soil_type.title()} soil and {crop.title()}:\n"
        f"- Recommended NPK Ratio: {soil_data['npk']}\n"
        f"- Target pH Range: {soil_data['ph']}\n"
        f"- Organic Matter Advice: {soil_data['organic']}\n"
        f"- Drainage Advice: {soil_data['drainage']}\n"
        f"- Crop Note: {crop_note}"
    )


_FERTILITY_MULTIPLIERS = {"low": 1.2, "medium": 1.0, "high": 0.8}

_FERTILIZER_BASE_RATES: Dict[str, Dict[str, float]] = {
    "wheat": {"n": 50, "p": 25, "k": 20},
    "rice": {"n": 60, "p": 30, "k": 25},
    "maize": {"n": 65, "p": 30, "k": 25},
    "tomato": {"n": 55, "p": 30, "k": 35},
    "potato": {"n": 60, "p": 35, "k": 40},
    "onion": {"n": 45, "p": 25, "k": 25},
    "cotton": {"n": 50, "p": 25, "k": 30},
    "sugarcane": {"n": 80, "p": 35, "k": 40},
    "soybean": {"n": 20, "p": 30, "k": 20},
    "sunflower": {"n": 35, "p": 20, "k": 20},
    "millet": {"n": 30, "p": 15, "k": 15},
    "sorghum": {"n": 35, "p": 20, "k": 20},
    "barley": {"n": 40, "p": 20, "k": 15},
    "mustard": {"n": 30, "p": 15, "k": 15},
    "chickpea": {"n": 15, "p": 20, "k": 15},
}


@tool
def fertilizer_calculator_tool(crop: str, area_acres: float, soil_fertility: str) -> str:
    """Estimate per-acre and total NPK fertilizer requirements, suggest timing for application, and mention organic alternatives for a crop."""

    crop_key = crop.strip().lower()
    fertility_key = soil_fertility.strip().lower()

    base_rates = _FERTILIZER_BASE_RATES.get(crop_key)
    if not base_rates:
        supported = ", ".join(sorted(_FERTILIZER_BASE_RATES.keys()))
        return f"Fertilizer data is not available for '{crop}'. Supported crops are: {supported}."

    if fertility_key not in _FERTILITY_MULTIPLIERS:
        return "soil_fertility must be one of: low, medium, high."

    multiplier = _FERTILITY_MULTIPLIERS[fertility_key]
    per_acre = {nutrient: round(value * multiplier, 2) for nutrient, value in base_rates.items()}
    total = {nutrient: round(value * area_acres, 2) for nutrient, value in per_acre.items()}

    return (
        f"Fertilizer recommendation for {crop.title()} on {area_acres} acre(s) with {soil_fertility.lower()} soil fertility:\n"
        f"- Per Acre: Nitrogen {per_acre['n']} kg, Phosphorus {per_acre['p']} kg, Potassium {per_acre['k']} kg\n"
        f"- Total Requirement: Nitrogen {total['n']} kg, Phosphorus {total['p']} kg, Potassium {total['k']} kg\n"
        f"- Application Schedule: Apply full phosphorus and potassium plus 40-50% nitrogen before sowing or at planting. Use the remaining nitrogen in 1-2 top dressings during early vegetative growth and before peak nutrient demand.\n"
        f"- Organic Alternative Note: Compost, vermicompost, well-decomposed manure, biofertilizers, and crop residue recycling can partially replace synthetic inputs.\n"
        f"- Advisory: Always confirm with a soil test before final fertilizer planning."
    )


@tool
def get_market_prices_tool(crop: str, country: str = "India") -> str:
    """Search current crop market price information per quintal using Tavily and return the most relevant finding with its source URL."""

    if not TAVILY_API_KEY:
        return "Tavily API key is not configured. Please add TAVILY_API_KEY to your environment."

    query = f"current {crop} market price per quintal {country} mandi 2025"
    try:
        search_tool = TavilySearchResults(max_results=5)
        results = search_tool.invoke({"query": query})
    except Exception as exc:  # pragma: no cover
        return f"Unable to fetch market price information right now: {exc}"

    if not results:
        return (
            f"I could not find reliable market price data for {crop} in {country}. "
            "Please also check your local APMC or mandi website for the latest region-specific rates."
        )

    best_result = None
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict):
                text_blob = " ".join(str(item.get(key, "")) for key in ("title", "content", "snippet"))
                price = _extract_first_price(text_blob)
                if price:
                    best_result = {
                        "title": item.get("title", "Market price result"),
                        "price": price,
                        "url": item.get("url", "No URL provided"),
                        "summary": item.get("content", "No summary available."),
                    }
                    break
        if best_result is None and results and isinstance(results[0], dict):
            item = results[0]
            best_result = {
                "title": item.get("title", "Market price result"),
                "price": "Price mention not clearly extracted",
                "url": item.get("url", "No URL provided"),
                "summary": item.get("content", "No summary available."),
            }

    if best_result is None:
        return (
            f"I found references about {crop} markets, but not a clean price quote. "
            "Please also check your local APMC or mandi website for the latest rates."
        )

    return (
        f"Market price insight for {crop.title()} in {country}:\n"
        f"- Result Title: {best_result['title']}\n"
        f"- Indicative Price: {best_result['price']}\n"
        f"- Summary: {best_result['summary']}\n"
        f"- Source: {best_result['url']}\n"
        f"- Note: Market prices vary by mandi, grade, and date, so confirm locally before selling."
    )


TOOLS = [
    web_search_tool,
    get_weather_tool,
    get_crop_calendar_tool,
    soil_npk_advisor_tool,
    fertilizer_calculator_tool,
    get_market_prices_tool,
]
