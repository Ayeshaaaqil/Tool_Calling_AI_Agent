import json
import streamlit as st
import requests  # Free live weather API call karne ke liye

# Free live weather function (Bina kisi API Key ke chalega)
def get_weather(city):
    try:
        # wttr.in ka free live JSON endpoint
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url)
        
        if response.status_code == 200:
            web_data = response.json()
            
            # Live backend data extract karna
            current_condition = web_data['current_condition'][0]
            temp = f"{current_condition['temp_C']}°C"
            condition = current_condition['weatherDesc'][0]['value']
            humidity = f"{current_condition['humidity']}%"
            
            # Weather condition ke mutabiq dynamic icons aur themes set karna
            condition_lower = condition.lower()
            if "clear" in condition_lower or "sunny" in condition_lower:
                icon, theme_color = "☀️", "#FFEB3B"
            elif "cloud" in condition_lower or "overcast" in condition_lower:
                icon, theme_color = "☁️", "#B0BEC5"
            elif "rain" in condition_lower or "drizzle" in condition_lower or "shower" in condition_lower:
                icon, theme_color = "🌧️", "#2196F3"
            elif "thunder" in condition_lower:
                icon, theme_color = "🌩️", "#7E57C2"
            elif "snow" in condition_lower:
                icon, theme_color = "❄️", "#E0F7FA"
            else:
                icon, theme_color = "🌫️", "#CFD8DC" # Mist, Fog, Smoke etc.

            return {
                "temperature": temp,
                "condition": condition,
                "humidity": humidity,
                "ui_hint": {
                    "icon": icon, 
                    "theme_color": theme_color
                }
            }
        else:
            raise ValidationError(f"City '{city}' not found or service unavailable.", 404)
            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise ValidationError(f"Network error while fetching weather: {str(e)}", 500)

def web_search(query):
    return {
        "results": [
            {"title": f"Result 1 for {query}", "url": "https://example.com/1"},
            {"title": f"Result 2 for {query}", "url": "https://example.com/2"}
        ],
        "ui_hint": {
            "icon": "🔍",
            "theme_color": "#2196F3"
        }
    }

# Custom Exception for validation error handling
class ValidationError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

def format_error(message, code):
    return {
        "status": "error",
        "code": code,
        "message": message,
        "ui_hint": {"icon": "❌", "theme_color": "#F44336"}
    }

# Tool Registry
TOOLS = {
    "get_weather": get_weather,
    "web_search": web_search
}

def process_request(user_input):
    try:
        if not user_input.strip():
            raise ValidationError("Please enter a valid prompt.", 400)

        # Step 1: Analyze Intent and Extract City/Query
        if "weather" in user_input.lower():
            tool_name = "get_weather"
            # Agar user "weather in New York" likhe ya "New York weather", dono ko handle karega
            if "in " in user_input.lower():
                city = user_input.lower().split("in")[-1].strip()
            else:
                city = user_input.lower().replace("weather", "").strip()
            params = {"city": city}
        elif "search" in user_input.lower():
            tool_name = "web_search"
            query = user_input.replace("search", "").strip()
            params = {"query": query}
        else:
            raise ValidationError("Tool or function not found for your request.", 404)

        # Step 2: Validate Parameters
        if tool_name == "get_weather" and not params.get("city"):
            raise ValidationError("Missing required parameter: city (e.g., 'weather in Karachi')", 400)

        # Step 3: Execute Tool Dynamically
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


# ==========================================
# UI/UX LAYER (Streamlit Web Interface)
# ==========================================

st.set_page_config(page_title="AI Tool Agent Dashboard", page_icon="🤖", layout="centered")

st.title("🤖 AI Tool Agent UI")
st.caption("Enter your command below to trigger backend tools dynamically.")

user_query = st.text_input("What would you like to do?", placeholder="e.g., What is the weather in London? or weather tokyo")

if st.button("Execute Command", type="primary"):
    if user_query:
        with st.spinner("Processing request..."):
            response = process_request(user_query)
            
            st.write("---")
            
            # Handling UI/UX based on Response Status
            if response["status"] == "success":
                data = response["data"]
                ui = data.get("ui_hint", {})
                
                # Success Notification
                st.success(f"{ui.get('icon', '✅')} {response['message']}")
                
                # Dynamic UI Components based on Tool Type
                if "temperature" in data:  # Weather UI Card
                    col1, col2, col3 = st.columns(3)
                    col1.metric(label="Temperature", value=data["temperature"])
                    col2.metric(label="Condition", value=f"{ui.get('icon')} {data['condition']}")
                    col3.metric(label="Humidity", value=data["humidity"])
                    
                elif "results" in data:  # Search Results UI List
                    st.subheader("Search Results:")
                    for idx, link in enumerate(data["results"]):
                        st.markdown(f"{idx+1}. [{link['title']}]({link['url']})")
            
            else:  # Error UI Styling
                st.error(f"Error {response['code']}: {response['message']}")
                
            # Developer Toggle for Debugging (Raw JSON View)
            with st.expander("👁️ View Raw JSON Response (Backend Data)"):
                st.json(response)
