import pandas as pd

# Helper function to read data
def data_to_df(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        elif file.name.endswith((".xlsx", ".xls")):
            return pd.read_excel(file)
        else:
            raise ValueError("Unsupported file type. Please upload CSV or Excel files.")
    except Exception as e:
        return None