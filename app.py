import streamlit as st
import pandas as pd
import numpy as np
import base64

# Load the dataset (make sure this file has the 'cluster' column)
df = pd.read_csv("clustered_diets.csv")

st.set_page_config(page_title="Smart Diet Recommendation", layout="centered")
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode()

    background_css = f"""
    <style>
    /* Global Background */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{encoded_image}");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: cover;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background-color: rgba(0, 0, 0, 0.6);
    }}

    .block-container {{
        background-color: rgba(0, 0, 0, 0.85);
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 95%;
        font-size: 1.1rem;
    }}

    /* Improve mobile scaling */
    @media screen and (max-width: 768px) {{
        [data-testid="stAppViewContainer"] {{
            background-size: cover;
            background-attachment: scroll;
            background-position: center top;
        }}

        .block-container {{
            padding: 1rem;
            margin: 0.5rem auto;
            width: 100%;
            font-size: 1.2rem;
        }}

        .stTextInput input, .stTextArea textarea, .stSelectbox div, .stButton button {{
            font-size: 1.1rem !important;
        }}

        .stRadio label, .stMarkdown p {{
            font-size: 1.1rem !important;
        }}
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

set_background("background.jpeg")

st.title("🥗 DietPreg Recommender System")

# --- Nutrient Calculator Function ---
def nutrients(age, height, weight, preg_stage, active):
    if active == 'Sedentary':
        active = 1.2
    elif active == "Light Active":
        active = 1.375
    elif active == "Moderately Active":
        active = 1.55
    elif active == "Very Active":
        active = 1.75

    bmi = weight / (height * height)
    if bmi < 18.5:
        person = 'Underweight'
        if preg_stage == "FirstTrimester":
            goal = 2
        elif preg_stage == "SecondTrimester":
            goal = 10
        elif preg_stage == "ThirdTrimester":
            goal = 18
    elif bmi >= 18.5 and bmi <= 25:
        person = 'Health in Weight'
        if preg_stage == "FirstTrimester":
            goal = 2
        elif preg_stage == "SecondTrimester":
            goal = 10
        elif preg_stage == "ThirdTrimester":
            goal = 16
    elif bmi > 25:
        person = 'Overweight'
        if preg_stage == "FirstTrimester":
            goal = 2
        elif preg_stage == "SecondTrimester":
            goal = 7
        elif preg_stage == "ThirdTrimester":
            goal = 11

    # Mifflin-St Jeor BMR equation to get the BMR formula
    bmr = 10 * weight + 6.25 * height - 5 * age - 161
     
    # Needed calories = BMR multiplied by the activity level
    caloric_intake = bmr * float(active)

    return caloric_intake

# --- Caloric Classifier ---
def classify_caloric_intake(caloric_intake):
    if caloric_intake < 300:
        return "low"
    elif 300 <= caloric_intake <= 350:
        return "mid"
    else:
        return "high"

# --- Diet Recommender ---
def recommend_diets(caloric_level, caloric_value, n=5):
    filtered_data = df[df['cluster'] == caloric_level]
    sorted_diets = filtered_data.sort_values(by='Energ_Kcal', ascending=False)
    recommended = sorted_diets[(sorted_diets['Energ_Kcal'] >= caloric_value) &
                               (sorted_diets['Energ_Kcal'] <= caloric_value + 10)]
    return recommended[['Shrt_Desc', 'Energ_Kcal']].head(n)

# --- User Input Form ---
st.sidebar.header("Enter Your Info")
age = st.sidebar.number_input("Age (years)")
height = st.sidebar.number_input("Height (meters)", min_value=1.0, max_value=2.5, value=1.6)
weight = st.sidebar.number_input("Weight (kg)")
preg_stage = st.sidebar.selectbox("Pregnancy Stage", ["FirstTrimester", "SecondTrimester", "ThirdTrimester"])
activity = st.sidebar.selectbox("Activity Level", ["Sedentary", "Light Active", "Moderately Active", "Very Active"])

if st.sidebar.button("Get Recommendations"):
    caloric_intake = nutrients(age, height, weight, preg_stage, activity)
    caloric_class = classify_caloric_intake(caloric_intake)

    st.subheader("🔍 Results")
    st.write(f"**Estimated Daily Caloric Intake:** {round(caloric_intake, 2)} kcal")
    st.write(f"**Caloric Intake Level:** {caloric_class.capitalize()}")

    st.markdown("---")
    st.subheader("🥗 Top Diet Recommendations")
    top_diets = df[df['Energ_Kcal'] < caloric_intake + 100].sort_values(by=['Energ_Kcal'], ascending=False).head(10)
    st.dataframe(top_diets[['Shrt_Desc', 'Energ_Kcal']])

    csv = top_diets.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Recommendations as CSV",
        data=csv,
        file_name='diet_recommendations.csv',
        mime='text/csv'
    )
