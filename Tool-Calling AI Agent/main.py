import json
import streamlit as st

# Simulated tool functions for testing (Replace with your actual imports)
def get_weather(city):
    # Dynamic UI/UX data based on weather conditions
    return {
        "temperature": "32°C",
        "condition": "Sunny",
        "humidity": "65%",
        "ui_hint": {
            "icon": "☀️", 
            "theme_color": "#FFEB3B",
            "bg_gradient": "linear-gradient(to right, #ff7e5f, #feb47b)"
        }
    }

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

# Mocking the Custom Exceptions for standalone execution
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

        # Step 1: Analyze Intent
        if "weather" in user_input.lower():
            tool_name = "get_weather"
            city = user_input.split("in")[-1].strip() if "in" in user_input else None
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


# ==========================================
# UI/UX LAYER (Streamlit Web Interface)
# ==========================================

# Page Configuration (Clean & Modern Design)
st.set_page_config(page_title="AI Tool Agent Dashboard", page_icon="🤖", layout="centered")

st.title("🤖 AI Tool Agent UI")
st.caption("Enter your command below to trigger backend tools dynamically.")

# User Input Layout
user_query = st.text_input("What would you like to do?", placeholder="e.g., What is the weather in Karachi? or search Python tutorials")

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
                ui = response.get("ui_hint", {})
                st.error(f"{ui.get('icon')} Error {response['code']}: {response['message']}")
                
            # Developer Toggle for Debugging (Raw JSON View)
            with st.expander("👁️ View Raw JSON Response (Backend Data)"):
                st.json(response)
