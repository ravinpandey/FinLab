import pandas as pd

def load_data(file='expenses.csv'):
    try:
        return pd.read_csv(file, parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

def save_data(df, file='expenses.csv'):
    df.to_csv(file, index=False)

def add_expense(date, category, amount, description, file='expenses.csv'):
    df = load_data(file)
    new_row = pd.DataFrame([[date, category, amount, description]],
                           columns=["Date", "Category", "Amount", "Description"])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df, file)
