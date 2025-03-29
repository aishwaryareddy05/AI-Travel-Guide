
import streamlit as st
import os
from groq import Groq
from datetime import date

# Load Groq API key
os.environ["GROQ_API_KEY"] = "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" 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  
client = Groq(api_key=GROQ_API_KEY)

# Initialize session state variables
if 'proceed_clicked' not in st.session_state:
    st.session_state.proceed_clicked = False
if 'generate_clicked' not in st.session_state:
    st.session_state.generate_clicked = False
if 'selected_preferences' not in st.session_state:
    st.session_state.selected_preferences = {}

# System prompt for AI
SYSTEM_PROMPT = '''
You are an AI-powered travel planner that creates highly personalized travel itineraries.
Your task is to:
- Gather and clarify user preferences through structured questions.
- Fetch relevant attractions dynamically using AI.
- Generate a well-structured itinerary with time allocation, travel duration, and meal breaks.
- Ensure results align with user preferences (e.g., history lovers get historical sites).
- Refine vague user inputs by prompting for missing details.
- Offer hotel and restaurant recommendations if requested.
- Keep responses clear, structured, and user-friendly.
'''

# Function to interact with Groq API
def ask_groq(prompt):
    """Fetches responses from Groq API."""
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error fetching response: {str(e)}"

# Function to collect user inputs
def get_user_inputs():
    """Collects structured user inputs for itinerary generation."""
    st.sidebar.header("📌 Trip Details")
    
    destination = st.sidebar.text_input("📍 Destination (City/Country)")
    starting_location = st.sidebar.text_input("🌍 Starting Location")
    start_date = st.sidebar.date_input("📅 Start Date", min_value=date.today())
    end_date = st.sidebar.date_input("📅 End Date", min_value=start_date)

    budget = st.sidebar.selectbox("💰 Budget", ["Budget-friendly", "Mid-range", "Luxury"])
    purpose = st.sidebar.selectbox("🎯 Purpose of Trip", ["Vacation", "Business", "Honeymoon", "Family Trip", "Other"])
    interests = st.sidebar.multiselect("🎭 Experiences You Enjoy", 
        ["Cultural & Historical", "Nature & Adventure", "Food & Culinary", "Nightlife & Entertainment", "Shopping & Markets", "Other"])

    user_data = {
        "destination": destination,
        "starting_location": starting_location,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "purpose": purpose,
        "interests": interests
    }
    
    return user_data

# Function to get structured preferences using AI
def get_additional_preferences():
    """Fetches additional travel preferences dynamically from AI."""
    st.subheader("📝 Additional Preferences")

    initial_prompt ="""Generate a structured list of additional travel preferences, ensuring that each category is separate and does not mix different types of preferences.
      Do not merge multiple categories into one (e.g., 'Airport transportation' and 'Travel mode' should be separate).
      Example format:
      Accommodation:
       -Hotel
       -Hostel
       -Vacation Rental
       -Bed and Breakfast
      Transportation:
       -Taxi
       -Public Transportation
       -Car Rental
       -Shuttle Service
      Dining Preferences:
       -Local Street Food
       -Fine Dining
       -Vegetarian/Vegan Options
       -Fast Food
Generate at least 7 well-structured categories with appropriate options.
"""
    raw_response = ask_groq(initial_prompt)

    structured_prefs = {}  # Dictionary to store structured preferences
    current_category = None  

    for line in raw_response.split("\n"):
        line = line.strip()
        if line.startswith("**") and line.endswith("**"):  
            current_category = line.replace("**", "").strip()
            structured_prefs[current_category] = []
        elif line.startswith("*") or line.startswith("+"):  
            if current_category:
                structured_prefs[current_category].append(line.lstrip("*+ ").strip())

    return structured_prefs

# Function to generate AI-powered itinerary
def generate_itinerary(user_data, additional_inputs):
    """Generates a structured itinerary using AI."""
    itinerary_prompt = f"""
    Generate a travel itinerary for {user_data['destination']} from {user_data['start_date']} to {user_data['end_date']}.
    - Budget: {user_data['budget']}
    - Purpose: {user_data['purpose']}
    - Interests: {', '.join(user_data['interests']) if user_data['interests'] else 'General sightseeing'}
    - Starting location: {user_data['starting_location']}
    - Additional Preferences: {additional_inputs}

    Please include:
    - Time allocation per attraction
    - Travel duration between locations
    - Meal break recommendations
    - Hotel suggestions (if applicable)
    - Nightlife/shopping options (if selected)
    """
    return ask_groq(itinerary_prompt)

# Streamlit App UI
st.title("🌟 AI-Powered Travel Planner")

# Step 1: Collect user inputs
user_inputs = get_user_inputs()

# Step 2: Proceed button to collect additional preferences
if st.sidebar.button("Proceed"):
    st.session_state.proceed_clicked = True

# Step 3: If Proceed was clicked, show additional preferences input
if st.session_state.proceed_clicked:

    # Fetch AI-generated structured preferences (only once)
    if "structured_prefs" not in st.session_state:
        st.session_state.structured_prefs = get_additional_preferences()
        st.session_state.selected_preferences = {}  # Store selected preferences

    # Show categories and let users select options
    for category, options in st.session_state.structured_prefs.items():
        st.session_state.selected_preferences[category] = st.multiselect(
            f"🔹 {category}", options, key=f"prefs_{category}"
        )

    # Show confirmation button after preferences are selected
    if st.button("✅ Confirm Preferences"):
        st.session_state.confirmed_preferences = True

# Step 4: Show "Generate Itinerary" button after confirming preferences
if st.session_state.get("confirmed_preferences", False):
    if st.button("🚀 Generate Itinerary"):
        st.session_state.generate_clicked = True

# Step 5: Display itinerary only after clicking "Generate Itinerary"
if st.session_state.get("generate_clicked", False):
    formatted_additional_inputs = "\n".join(
        [f"{key}: {', '.join(value)}" for key, value in st.session_state.selected_preferences.items()]
    )

    itinerary = generate_itinerary(user_inputs, formatted_additional_inputs)
    st.subheader(f"📍 Your Itinerary for {user_inputs['destination']}")
    st.write(itinerary)   