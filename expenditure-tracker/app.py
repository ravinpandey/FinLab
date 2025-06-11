import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load or initialize data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("expenditure_data.csv", parse_dates=["Date"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
    return df

# Save data to CSV
def save_data(df):
    df.to_csv("expenditure_data.csv", index=False)

# Set spending limits
CATEGORY_LIMITS = {
    "Food": 500,
    "Transport": 300,
    "Shopping": 400,
    "Entertainment": 200,
    "Utilities": 250
}

st.title("\ud83d\udcb8 Expenditure Tracker Dashboard")

# Load data
expenditure_df = load_data()

# Input form
with st.form("entry_form"):
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", list(CATEGORY_LIMITS.keys()))
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    description = st.text_input("Description")
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        new_entry = pd.DataFrame({
            "Date": [date],
            "Category": [category],
            "Amount": [amount],
            "Description": [description]
        })
        expenditure_df = pd.concat([expenditure_df, new_entry], ignore_index=True)
        save_data(expenditure_df)
        st.success("\u2705 Entry added successfully!")

# Sidebar filter
st.sidebar.header("Filter Options")
start_date = st.sidebar.date_input("Start Date", value=expenditure_df["Date"].min() if not expenditure_df.empty else datetime.today())
end_date = st.sidebar.date_input("End Date", value=expenditure_df["Date"].max() if not expenditure_df.empty else datetime.today())

filtered_df = expenditure_df[
    (expenditure_df["Date"] >= pd.to_datetime(start_date)) &
    (expenditure_df["Date"] <= pd.to_datetime(end_date))
]

# Budget alert
st.subheader("\u26a0\ufe0f Budget Alerts")
if not filtered_df.empty:
    for cat in filtered_df["Category"].unique():
        total = filtered_df[filtered_df["Category"] == cat]["Amount"].sum()
        if total > CATEGORY_LIMITS[cat]:
            st.warning(f"You have exceeded the limit for **{cat}**: {total:.2f} > {CATEGORY_LIMITS[cat]}")

# Grouping logic
def group_data(df, group_by):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    if group_by == "Daily":
        df["Group"] = df["Date"].dt.date
    elif group_by == "Weekly":
        df["Group"] = df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    elif group_by == "Monthly":
        df["Group"] = df["Date"].dt.to_period("M").apply(lambda r: r.start_time)
    elif group_by == "Quarterly":
        df["Group"] = df["Date"].dt.to_period("Q").apply(lambda r: r.start_time)
    elif group_by == "Yearly":
        df["Group"] = df["Date"].dt.year
    return df.groupby(["Group", "Category"]).sum(numeric_only=True).reset_index()

# Visualization section
st.subheader("\ud83d\udcca Visual Analytics")
group_by = st.selectbox("Group By", ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])
grouped_df = group_data(filtered_df, group_by)
pivot_df = grouped_df.pivot(index="Group", columns="Category", values="Amount").fillna(0)

st.bar_chart(pivot_df)
st.line_chart(pivot_df)

# Pie chart
st.subheader("\ud83e\udd67 Pie Chart - Total Spend by Category")
category_sum = filtered_df.groupby("Category")["Amount"].sum()
fig, ax = plt.subplots()
ax.pie(category_sum, labels=category_sum.index, autopct="%1.1f%%")
ax.axis("equal")
st.pyplot(fig)

# ML Recommendation
st.subheader("\ud83e\udd16 Expense Recommendation Engine")
if len(expenditure_df) >= 10:
    df_ml = expenditure_df.copy()
    df_ml["Day"] = df_ml["Date"].dt.day
    df_ml["Month"] = df_ml["Date"].dt.month
    df_ml["Year"] = df_ml["Date"].dt.year

    le = LabelEncoder()
    df_ml["Category_encoded"] = le.fit_transform(df_ml["Category"])

    X = df_ml[["Day", "Month", "Year"]]
    y = df_ml["Category_encoded"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)

    today = datetime.today()
    pred = clf.predict([[today.day, today.month, today.year]])
    recommended_cat = le.inverse_transform(pred)[0]
    st.info(f"\ud83d\udccc Suggested category to monitor today: **{recommended_cat}**")
else:
    st.info("\u2139\ufe0f Add at least 10 entries to get ML-based suggestions.")
