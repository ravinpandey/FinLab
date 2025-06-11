import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import load_data, add_expense

st.set_page_config(page_title="Expenditure Tracker", layout="wide")
st.title("💰 Expenditure Tracker (v1.0)")

# Sidebar Form for Adding Expenses
st.sidebar.header("➕ Add a New Expense")
with st.sidebar.form("expense_form"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Rent", "Utilities", "Entertainment", "Health", "Other"])
    amount = st.number_input("Amount (USD)", min_value=0.0, step=0.01, format="%.2f")
    description = st.text_input("Description (optional)")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        add_expense(date, category, amount, description)
        st.sidebar.success("✅ Expense added!")

# Load Data
df = load_data()

# If data is empty
if df.empty:
    st.info("No expenses recorded yet. Use the sidebar to add your first one.")
    st.stop()

# Data Table
st.subheader("📋 All Expenses")
st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

# Filters
with st.expander("🔎 Filter Options"):
    categories = st.multiselect("Filter by Category", df["Category"].unique())
    if categories:
        df = df[df["Category"].isin(categories)]

# Summary Stats
st.subheader("📊 Summary")
total = df["Amount"].sum()
st.metric("Total Spend", f"${total:,.2f}")

category_summary = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
st.bar_chart(category_summary)

# Pie Chart
st.subheader("🧁 Category Distribution")
fig, ax = plt.subplots()
ax.pie(category_summary, labels=category_summary.index, autopct="%1.1f%%", startangle=140)
ax.axis("equal")  # Equal aspect ratio ensures the pie is circular
st.pyplot(fig)
