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
            "strikePrice", "expiryDate", "optionType", "underlying", "Product", "Ticker", "Expiry", "OptionType", 
            "StrikePrice", "openInterest", "changeinOpenInterest", "pchangeinOpenInterest", "totalTradedVolume", 
            "impliedVolatility", "lastPrice", "change", "pChange", "totalBuyQuantity", "totalSellQuantity", 
            "bidQty", "bidprice", "askQty", "askPrice", "underlyingValue", "timestamp", "totOI", "totVol"
        ]

        # Include CE and PE suffix for CE/PE-specific data
        self.columns_ce = [col + "_CE" for col in self.columns]
        self.columns_pe = [col + "_PE" for col in self.columns]

        # Data sources for both Nifty and BankNifty (URLs for fetching options chain data)
        self.data_sources = {
            "BANKNIFTY": "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY",
            "NIFTY": "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
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
        Process fetched data to extract relevant columns for CE and PE data.
        """
        rows = []
        records = data.get("records", {}).get("data", [])
        tot_oi = data.get("records", {}).get("totOI", None)
        tot_vol = data.get("records", {}).get("totVol", None)
        timestamp = data.get("records", {}).get("timestamp", None)

        for record in records:
            strike_price = record.get("strikePrice")
            expiry_date = record.get("expiryDate")

            for option_type, option_data in {"CE": record.get("CE", {}), "PE": record.get("PE", {})}.items():
                # Extract identifier fields
                identifier = option_data.get("identifier", "")
                identifier_parts = identifier.split(" ")
                product, ticker, expiry, option_type_id, strike = (
                    identifier_parts[0] if len(identifier_parts) > 0 else None,
                    identifier_parts[1] if len(identifier_parts) > 1 else None,
                    identifier_parts[2] if len(identifier_parts) > 2 else None,
                    identifier_parts[3] if len(identifier_parts) > 3 else None,
                    identifier_parts[4] if len(identifier_parts) > 4 else None,
                )

                row = [
                    strike_price,
                    expiry_date,
                    option_type,
                    option_data.get("underlying", None),
                    product,
                    ticker,
                    expiry,
                    option_type_id,
                    strike,
                    option_data.get("openInterest", None),
                    option_data.get("changeinOpenInterest", None),
                    option_data.get("pchangeinOpenInterest", None),
                    option_data.get("totalTradedVolume", None),
                    option_data.get("impliedVolatility", None),
                    option_data.get("lastPrice", None),
                    option_data.get("change", None),
                    option_data.get("pChange", None),
                    option_data.get("totalBuyQuantity", None),
                    option_data.get("totalSellQuantity", None),
                    option_data.get("bidQty", None),
                    option_data.get("bidprice", None),
                    option_data.get("askQty", None),
                    option_data.get("askPrice", None),
                    option_data.get("underlyingValue", None),
                    timestamp,
                    tot_oi,
                    tot_vol,
                ]
                rows.append(row)

        return pd.DataFrame(rows, columns=self.columns_ce if option_type == "CE" else self.columns_pe)

    def save_to_excel(self, data, filename, folder="output"):
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_path = os.path.join(folder, f"{filename}_OPTIONS.xlsx")
        try:
            data.to_excel(file_path, index=False)
            print(f"Data successfully saved to {file_path}")
        except Exception as e:
            print(f"Error saving data to Excel for {filename}: {e}")

    def run(self):
        """
        Fetch and process data for NIFTY and BANKNIFTY.
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
    print("Starting NSE Data Fetcher...")
    fetcher = NSEDataFetcher()
    fetcher.run()

# Ensure this is at the end
def main():
    # Create an instance of the class and call the run method
    fetcher = NSEDataFetcher()
    fetcher.run()

# This ensures the script runs if executed directly
if __name__ == "__main__":
    main()
