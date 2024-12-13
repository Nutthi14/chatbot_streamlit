import pandas as pd
import os

class DataHandler:
    _instance = None
    _data = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataHandler, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def load_data(self, path):
        """Load data from the specified file and standardize column names."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"File at {path} does not exist.")
        _, ext = os.path.splitext(path.lower())
        if ext == ".csv":
            self._data = pd.read_csv(path)
        elif ext in [".xls", ".xlsx"]:
            self._data = pd.read_excel(path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        # Standardize column names
        self._data.columns = self._data.columns.str.lower().str.strip()
        print(f"Data loaded successfully from {path}. Columns: {', '.join(self._data.columns)}")
        return self._data


    def get_data(self):
        """Retrieve the loaded data."""
        if self._data is None:
            raise ValueError("Data not loaded.")
        return self._data

    def update_data(self, updates):
        """Update the loaded data."""
        if self._data is not None:
            self._data.update(updates)
            print("Data updated successfully.")
        else:
            raise ValueError("Data not loaded. Load the data first.")

