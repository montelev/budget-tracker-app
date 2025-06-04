
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Budget Tracker", layout="centered")

st.title("💰 Budget Tracker Dashboard")

# File upload
budget_file = st.file_uploader("Upload your 'budget.csv' file", type=["csv"])
goal_file = st.file_uploader("Upload your 'budget_goals.csv' file", type=["csv"])

if budget_file and goal_file:
    budget_df = pd.read_csv(budget_file)
    goals_df = pd.read_csv(goal_file)

    # Clean and display data
    st.subheader("📊 Transactions")
    st.dataframe(budget_df)

    st.subheader("🎯 Budget Goals")
    st.dataframe(goals_df)

    # Calculate totals
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
    st.info("Please upload both CSV files to proceed.")
