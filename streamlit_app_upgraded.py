
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Budget Tracker", layout="centered")
st.title("💰 Budget Tracker Dashboard")

def guess_category(description):
    description = description.lower()
    if any(x in description for x in ["mcdonald", "wawa", "doordash", "aldi", "wendy", "pizza", "restaurant"]):
        return "Food"
    if any(x in description for x in ["walmart", "target", "burlington", "five below", "shopping", "gift"]):
        return "Shopping"
    if any(x in description for x in ["uber", "gas", "shell", "bp", "mobil"]):
        return "Gas"
    if any(x in description for x in ["netflix", "spotify", "apple", "openai", "subscription"]):
        return "Entertainment"
    if any(x in description for x in ["rent", "spectrum", "electric", "capital one", "student", "education", "paypal", "vanguard"]):
        return "Bills"
    return "Other"

def extract_pdf_transactions(uploaded_pdf):
    text = ""
    with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()

    pattern = r"(\d{2}/\d{2}/\d{2}).+?(?<![A-Z])([A-Za-z0-9 \*\-\&']{5,40})\s+-?\$?(-?\d{1,4}\.\d{2})"
    matches = re.findall(pattern, text)

    data = []
    for date, description, amount in matches:
        try:
            amount = float(amount.replace("$", "").replace(",", ""))
            category = guess_category(description)
            data.append((date.strip(), description.strip(), category, amount))
        except:
            continue

    return pd.DataFrame(data, columns=["Date", "Description", "Category", "Amount"])

upload_type = st.radio("Choose your upload type:", ["CSV Upload", "Bank PDF Statement"])

if upload_type == "CSV Upload":
    budget_file = st.file_uploader("Upload your 'budget.csv' file", type=["csv"])
    goal_file = st.file_uploader("Upload your 'budget_goals.csv' file", type=["csv"])

    if budget_file and goal_file:
        budget_df = pd.read_csv(budget_file)
        goals_df = pd.read_csv(goal_file)

elif upload_type == "Bank PDF Statement":
    pdf_file = st.file_uploader("Upload your bank PDF statement", type=["pdf"])
    goal_file = st.file_uploader("Upload your 'budget_goals.csv' file", type=["csv"])

    if pdf_file and goal_file:
        budget_df = extract_pdf_transactions(pdf_file)
        goals_df = pd.read_csv(goal_file)

if 'budget_df' in locals() and 'goals_df' in locals():
    st.subheader("📊 Transactions")
    st.dataframe(budget_df)

    st.subheader("🎯 Budget Goals")
    st.dataframe(goals_df)

    # Totals
    category_totals = budget_df.groupby("Category")["Amount"].sum().reset_index()
    merged = pd.merge(goals_df, category_totals, on="Category", how="left").fillna(0)
    merged["Remaining"] = merged["Goal"] - merged["Amount"]

    st.subheader("📈 Spending vs Goals")
    st.dataframe(merged)

    # Pie Chart
    st.subheader("🍕 Expense Distribution")
    fig, ax = plt.subplots()
    ax.pie(category_totals["Amount"], labels=category_totals["Category"], autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("Please upload required files to begin.")
