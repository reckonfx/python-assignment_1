import streamlit as st
import pandas as pd
import random
from collections import defaultdict
from fpdf import FPDF
from io import BytesIO

# Function to generate a weekly meal plan
def generate_weekly_meal_plan(num_people):
    meal_options = {
        "Breakfast": ["Halwa Puri", "Paratha with Omelette", "Chana Chaat", "Aloo Paratha", "Cheese Toast", "Fruit Salad", "Pancakes"],
        "Lunch": ["Biryani", "Dal Chawal", "Chicken Karahi", "Vegetable Pulao", "Palak Paneer", "Korma", "Mutton Curry"],
        "Dinner": ["Nihari", "Paya", "Aloo Gosht", "Butter Chicken", "Mutton Handi", "Paneer Tikka", "Grilled Fish"]
    }

    ingredient_mapping = {
        "Halwa Puri": {"Flour (kg)": 1, "Sugar (kg)": 0.5, "Oil (liters)": 0.5},
        "Paratha with Omelette": {"Flour (kg)": 1, "Eggs": num_people * 2, "Milk (liters)": 1},
        "Biryani": {"Rice (kg)": 1, "Chicken (kg)": num_people * 1.5, "Spices (grams)": 100},
        "Chicken Karahi": {"Chicken (kg)": num_people * 1.5, "Tomatoes": 3, "Spices (grams)": 100},
        "Butter Chicken": {"Chicken (kg)": num_people * 1.5, "Butter (grams)": 100, "Cream (ml)": 100},
    }

    weekly_meals = []
    grocery_list = defaultdict(float)

    for _ in range(7):
        day_meals = {meal: random.choice(dishes) for meal, dishes in meal_options.items()}
        weekly_meals.append(day_meals)

        for meal in day_meals.values():
            ingredients = ingredient_mapping.get(meal, {})
            for item, qty in ingredients.items():
                grocery_list[item] += qty

    # Round quantities to whole numbers
    grocery_list = {item: round(qty) for item, qty in grocery_list.items()}

    return weekly_meals, grocery_list


# ✅ Function to create an Excel file
def create_excel(grocery_list):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        grocery_df = pd.DataFrame(list(grocery_list.items()), columns=["Ingredient", "Quantity"])
        grocery_df.to_excel(writer, sheet_name="Grocery List", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Grocery List"]

        header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#4F81BD', 'border': 1})
        for col_num, value in enumerate(grocery_df.columns):
            worksheet.write(0, col_num, value, header_format)

        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 10)

    output.seek(0)
    return output


# ✅ Function to create a PDF file
def create_pdf(weekly_meals, grocery_list):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.cell(200, 10, "Pakistani Weekly Meal Plan", ln=True, align='C')
    pdf.ln(10)

    # Meal Plan Section
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day, meals in zip(days, weekly_meals):
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, day, ln=True)
        pdf.set_font("Arial", size=12)
        for meal_type, dish in meals.items():
            pdf.cell(0, 10, f"{meal_type}: {dish}", ln=True)
        pdf.ln(5)

    pdf.ln(10)

    # Grocery List Section
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Grocery List", ln=True)
    pdf.set_font("Arial", size=12)

    for item, qty in grocery_list.items():
        pdf.cell(0, 10, f"{item}: {qty}", ln=True)

    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest="S").encode("latin1", "replace"))  # Fix encoding error
    pdf_output.seek(0)

    return pdf_output


# ✅ Streamlit UI Enhancements
st.set_page_config(page_title="Pakistani Weekly Meal Planner", layout="centered")

# Header Section
st.markdown("<h1 style='text-align: center; color: #ff5733;'>🍛 Pakistani Weekly Meal Planner🍛</h1>", unsafe_allow_html=True)
st.image("https://t4.ftcdn.net/jpg/03/83/42/07/360_F_383420760_eLY1AXaZ5nr9ql7zcTG89k82k6OqUcez.jpg", use_container_width=True)

# ✅ Maintain State
if "weekly_meals" not in st.session_state:
    st.session_state.weekly_meals = None
    st.session_state.grocery_list = None

# Number of People Selector
num_people = st.slider("Select Number of People", min_value=1, max_value=10, value=4)

if st.button("Generate Weekly Meal Plan"):
    st.session_state.weekly_meals, st.session_state.grocery_list = generate_weekly_meal_plan(num_people)

if st.session_state.weekly_meals and st.session_state.grocery_list:
    # Display weekly meal plan
    st.markdown("<h2 style='color: #1f77b4;'>📅 Weekly Meal Plan</h2>", unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.weekly_meals, index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    st.table(df)

    # Display grocery list
    st.markdown("<h2 style='color: #1f77b4;'>🛒 Grocery List</h2>", unsafe_allow_html=True)
    st.table(pd.DataFrame(list(st.session_state.grocery_list.items()), columns=["Ingredient", "Quantity"]))

    # ✅ Excel Download Button (Only Grocery List)
    excel_file = create_excel(st.session_state.grocery_list)
    st.download_button(label="📥 Download Grocery List (Excel)", data=excel_file, file_name="grocery_list.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ✅ PDF Download Button (Meal Plan + Grocery List)
    pdf_file = create_pdf(st.session_state.weekly_meals, st.session_state.grocery_list)
    st.download_button(label="📥 Download Meal Plan & Grocery List (PDF)", data=pdf_file, file_name="meal_plan.pdf", mime="application/pdf")
