import os
import requests
import pandas as pd

class NSEDataFetcher:
    def __init__(self):
        try:
            # Initialize the session and make an initial request to the NSE website
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
            }
            self.session = requests.Session()
            self.session.get('http://nseindia.com', headers=self.headers)  # Initialize session by hitting NSE homepage
            print("Session initialized successfully.")
        except Exception as e:
            print(f"Error initializing session: {e}")

        # Define the columns for NIFTY_50_CASH
        self.columns = [
            "symbol", "identifier", "open", "dayHigh", "dayLow", "lastPrice", "previousClose",
            "change", "pChange", "ffmc", "yearHigh", "yearLow", "totalTradedVolume",
            "stockIndClosePrice", "totalTradedValue", "lastUpdateTime", "nearWKH", "nearWKL",
            "perChange365d", "date365dAgo", "date30dAgo", "perChange30d", "series"
        ]

        # Define data sources (NIFTY 50)
        self.data_sources = {
            "NIFTY_50_CASH": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        }

    def fetch_data(self, url):
        """
        Fetch data from the specified NSE API URL using the initialized session.
        """
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()  # Return parsed JSON data
            else:
                print(f"Failed to fetch data from {url}. HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching data from {url}: {e}")
            return None

    def process_data(self, data):
        """
        Process the JSON response and map the data to the specified columns.
        """
        rows = []
        records = data.get("data", [])

        for record in records:
            row = [
                record.get("symbol", None),
                record.get("identifier", None),
                record.get("open", None),
                record.get("dayHigh", None),
                record.get("dayLow", None),
                record.get("lastPrice", None),
                record.get("previousClose", None),
                record.get("change", None),
                record.get("pChange", None),
                record.get("ffmc", None),
                record.get("yearHigh", None),
                record.get("yearLow", None),
                record.get("totalTradedVolume", None),
                record.get("stockIndClosePrice", None),
                record.get("totalTradedValue", None),
                record.get("lastUpdateTime", None),
                record.get("nearWKH", None),
                record.get("nearWKL", None),
                record.get("perChange365d", None),
                record.get("date365dAgo", None),
                record.get("date30dAgo", None),
                record.get("perChange30d", None),
                record.get("series", None),
            ]
            rows.append(row)

        return pd.DataFrame(rows, columns=self.columns)

    def save_to_excel(self, data, filename, folder="output"):
        """
        Save processed data to an Excel file.
        """
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_path = os.path.join(folder, f"{filename}.xlsx")
        try:
            data.to_excel(file_path, index=False)
            print(f"Data successfully saved to {file_path}")
        except Exception as e:
            print(f"Error saving data to Excel for {filename}: {e}")

    def run(self):
        """
        Fetch and process data for NIFTY_50_CASH.
        """
        for key, url in self.data_sources.items():
            print(f"Fetching data for {key}...")
            raw_data = self.fetch_data(url)
            if raw_data:
                processed_data = self.process_data(raw_data)
                if not processed_data.empty:
                    self.save_to_excel(processed_data, filename=key)
                else:
                    print(f"No tabular data available for {key}.")
            else:
                print(f"Failed to fetch data for {key}.")


if __name__ == "__main__":
    print("Starting NSE Data Fetcher for NIFTY_50_CASH...")
    fetcher = NSEDataFetcher()
    fetcher.run()
