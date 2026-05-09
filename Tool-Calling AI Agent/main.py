import json
from tools.weather import get_weather
from tools.search import web_search
from utils.error_handler import format_error, ValidationError

# Tool Registry
TOOLS = {
    "get_weather": get_weather,
    "web_search": web_search
}

def process_request(user_input):
    try:
        # Step 1: Analyze Intent (Simulated NLP/Logic)
        if "weather" in user_input.lower():
            tool_name = "get_weather"
            # Extracting city name (In production, use an LLM or Regex)
            city = user_input.split("in")[-1].strip() if "in" in user_input else None
            params = {"city": city}
        elif "search" in user_input.lower():
            tool_name = "web_search"
            query = user_input.replace("search", "").strip()
            params = {"query": query}
        else:
            raise ValidationError("Tool/function not found for your request.", 404)

        # Step 2: Validate Parameters
        if tool_name == "get_weather" and not params.get("city"):
            raise ValidationError("Missing required parameter: city", 400)

        # Step 3: Execute Tool
        if tool_name in TOOLS:
            result = TOOLS[tool_name](**params)
            return {
                "status": "success",
                "message": f"{tool_name.replace('_', ' ').title()} fetched successfully",
                "data": result
            }
        
    except ValidationError as e:
        return format_error(str(e), e.code)
    except Exception as e:
        return format_error(f"Internal Server Error: {str(e)}", 500)

# Local Testing
if __name__ == "__main__":
    test_query = "What is the weather in Karachi?"
    print(json.dumps(process_request(test_query), indent=2))