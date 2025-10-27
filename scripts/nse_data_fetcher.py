"""
NSE Data Fetcher and Symbol Mapping Module
Downloads symbol lists from NSE APIs and maps them to Fyers format
"""
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from data_storage import get_parquet_manager
from my_fyers_model import MyFyersModel

class NSEDataFetcher:
    """Fetches symbol data from NSE APIs and maps to Fyers format"""
    
    def __init__(self):
        self.manager = get_parquet_manager()
        self.fyers = MyFyersModel()
        
        # Create NSE symbols directory in Parquet storage
        self.nse_symbols_dir = Path("data/parquet/nse_symbols")
        self.nse_symbols_dir.mkdir(parents=True, exist_ok=True)
        
        # NSE API endpoints for symbol data
        self.nse_endpoints = {
            # ETF Data
            'nifty50_etf': 'https://www.nseindia.com/api/nifty50etf?csv=true&selectValFormat=crores',
            'gold_etf': 'https://www.nseindia.com/api/goldetf?csv=true&selectValFormat=crores', 
            'all_etf': 'https://www.nseindia.com/api/etf?csv=true&selectValFormat=crores',
            
            # Index Constituents
            'nifty50': 'https://www.nseindia.com/api/equity-stockIndices?csv=true&index=NIFTY%2050&selectValFormat=crores',
            'nifty100': 'https://www.nseindia.com/api/equity-stockIndices?csv=true&index=NIFTY%20100&selectValFormat=crores',
            'nifty200': 'https://www.nseindia.com/api/equity-stockIndices?csv=true&index=NIFTY%20200&selectValFormat=crores',
            'nifty_smallcap100': 'https://www.nseindia.com/api/equity-stockIndices?csv=true&index=NIFTY%20SMALLCAP%20100&selectValFormat=crores',
            
            # Options/Derivatives  
            'stock_options': 'https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt&csv=true&selectValFormat=crores'
        }
        
        # Headers to mimic browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_nse_data(self, endpoint_key: str, save_csv: bool = False, auto_delete_csv: bool = True) -> Optional[pd.DataFrame]:
        """
        Fetch data from NSE API endpoint
        
        Args:
            endpoint_key (str): Key from self.nse_endpoints
            save_csv (bool): Whether to save downloaded CSV temporarily
            auto_delete_csv (bool): Whether to auto-delete CSV after processing
            
        Returns:
            Optional[pd.DataFrame]: Downloaded data or None if failed
        """
        if endpoint_key not in self.nse_endpoints:
            print(f"❌ Unknown endpoint: {endpoint_key}")
            return None
            
        url = self.nse_endpoints[endpoint_key]
        csv_path = None
        
        try:
            print(f"📥 Fetching {endpoint_key} data from NSE...")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Save CSV temporarily if requested
            if save_csv:
                csv_path = self.nse_symbols_dir / f"{endpoint_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(csv_path, 'wb') as f:
                    f.write(response.content)
                print(f"💾 Saved temporary CSV: {csv_path}")
            
            # Parse CSV content
            from io import StringIO
            csv_content = StringIO(response.text)
            df = pd.read_csv(csv_content)
            
            print(f"✅ Successfully fetched {len(df)} records for {endpoint_key}")
            
            # Auto-delete CSV file after successful processing
            if csv_path and auto_delete_csv and csv_path.exists():
                try:
                    csv_path.unlink()
                    print(f"🗑️ Auto-deleted temporary CSV: {csv_path.name}")
                except Exception as e:
                    print(f"⚠️ Failed to delete CSV {csv_path.name}: {e}")
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch {endpoint_key}: {e}")
            # Clean up CSV if it was created but processing failed
            if csv_path and csv_path.exists():
                try:
                    csv_path.unlink()
                    print(f"🗑️ Cleaned up failed CSV: {csv_path.name}")
                except Exception:
                    pass
            return None
        except pd.errors.ParserError as e:
            print(f"❌ Failed to parse CSV for {endpoint_key}: {e}")
            # Clean up CSV if it was created but processing failed
            if csv_path and csv_path.exists():
                try:
                    csv_path.unlink()
                    print(f"🗑️ Cleaned up failed CSV: {csv_path.name}")
                except Exception:
                    pass
            return None
    
    def nse_to_fyers_symbol(self, nse_symbol: str, instrument_type: str = "EQ") -> str:
        """
        Convert NSE symbol to Fyers format
        
        Args:
            nse_symbol (str): NSE symbol (e.g., "RELIANCE", "HDFCBANK")
            instrument_type (str): Instrument type ("EQ", "INDEX", "ETF")
            
        Returns:
            str: Fyers format symbol (e.g., "NSE:RELIANCE-EQ")
        """
        # Clean the symbol
        clean_symbol = str(nse_symbol).strip().upper()
        
        # Handle special cases
        symbol_mappings = {
            'NIFTY 50': 'NIFTY50-INDEX',
            'NIFTY50': 'NIFTY50-INDEX',
            'NIFTY BANK': 'NIFTYBANK-INDEX',
            'BANKNIFTY': 'NIFTYBANK-INDEX',
            'NIFTY FIN SERVICE': 'FINNIFTY-INDEX',
            'FINNIFTY': 'FINNIFTY-INDEX',
            'INDIA VIX': 'INDIAVIX-INDEX',
            'INDIAVIX': 'INDIAVIX-INDEX',
            'SENSEX': 'SENSEX-INDEX'
        }
        
        if clean_symbol in symbol_mappings:
            return f"NSE:{symbol_mappings[clean_symbol]}"
        
        # For regular stocks and ETFs
        if instrument_type == "INDEX":
            return f"NSE:{clean_symbol}-INDEX"
        elif instrument_type == "ETF":
            return f"NSE:{clean_symbol}-ETF"
        else:
            return f"NSE:{clean_symbol}-EQ"
    
    def process_index_constituents(self, endpoint_key: str) -> Dict[str, any]:
        """
        Process index constituent data (Nifty50/100/200, etc.)
        
        Args:
            endpoint_key (str): Index endpoint key
            
        Returns:
            Dict: Processed symbol data with mappings
        """
        df = self.fetch_nse_data(endpoint_key)
        if df is None:
            return {}
        
        # Common column mappings for index data
        symbol_columns = ['Symbol', 'SYMBOL', 'symbol', 'Company Name', 'COMPANY']
        
        symbol_col = None
        for col in symbol_columns:
            if col in df.columns:
                symbol_col = col
                break
        
        if symbol_col is None:
            print(f"❌ No symbol column found in {endpoint_key} data")
            print(f"Available columns: {list(df.columns)}")
            return {}
        
        symbols_data = []
        for _, row in df.iterrows():
            nse_symbol = str(row[symbol_col]).strip()
            fyers_symbol = self.nse_to_fyers_symbol(nse_symbol, "EQ")
            
            symbols_data.append({
                'nse_symbol': nse_symbol,
                'fyers_symbol': fyers_symbol,
                'index_name': endpoint_key,
                'last_updated': datetime.now().isoformat(),
                'market_cap': row.get('Market Cap', 0) if 'Market Cap' in df.columns else 0,
                'weightage': row.get('Weightage', 0) if 'Weightage' in df.columns else 0
            })
        
        return {
            'endpoint': endpoint_key,
            'total_symbols': len(symbols_data),
            'symbols': symbols_data,
            'last_updated': datetime.now().isoformat()
        }
    
    def process_etf_data(self, endpoint_key: str) -> Dict[str, any]:
        """
        Process ETF data
        
        Args:
            endpoint_key (str): ETF endpoint key
            
        Returns:
            Dict: Processed ETF symbol data
        """
        df = self.fetch_nse_data(endpoint_key)
        if df is None:
            return {}
        
        # ETF specific column mappings
        symbol_columns = ['Symbol', 'ETF Symbol', 'Fund Name', 'SYMBOL']
        
        symbol_col = None
        for col in symbol_columns:
            if col in df.columns:
                symbol_col = col
                break
        
        if symbol_col is None:
            print(f"❌ No symbol column found in {endpoint_key} ETF data")
            print(f"Available columns: {list(df.columns)}")
            return {}
        
        etf_data = []
        for _, row in df.iterrows():
            nse_symbol = str(row[symbol_col]).strip()
            fyers_symbol = self.nse_to_fyers_symbol(nse_symbol, "ETF")
            
            etf_data.append({
                'nse_symbol': nse_symbol,
                'fyers_symbol': fyers_symbol,
                'etf_type': endpoint_key,
                'fund_name': row.get('Fund Name', ''),
                'aum': row.get('AUM', 0) if 'AUM' in df.columns else 0,
                'last_updated': datetime.now().isoformat()
            })
        
        return {
            'endpoint': endpoint_key,
            'total_etfs': len(etf_data),
            'etfs': etf_data,
            'last_updated': datetime.now().isoformat()
        }
    
    def process_derivatives_data(self, endpoint_key: str) -> Dict[str, any]:
        """
        Process derivatives/options data
        
        Args:
            endpoint_key (str): Derivatives endpoint key
            
        Returns:
            Dict: Processed derivatives symbol data
        """
        df = self.fetch_nse_data(endpoint_key)
        if df is None:
            return {}
        
        # Derivatives specific processing
        derivatives_data = []
        
        # Look for relevant columns
        if 'Symbol' in df.columns or 'SYMBOL' in df.columns:
            symbol_col = 'Symbol' if 'Symbol' in df.columns else 'SYMBOL'
            
            for _, row in df.iterrows():
                underlying_symbol = str(row[symbol_col]).strip()
                fyers_symbol = self.nse_to_fyers_symbol(underlying_symbol, "EQ")
                
                derivatives_data.append({
                    'underlying_symbol': underlying_symbol,
                    'fyers_symbol': fyers_symbol,
                    'instrument_type': row.get('Instrument', ''),
                    'expiry_date': row.get('Expiry Date', ''),
                    'strike_price': row.get('Strike Price', 0),
                    'option_type': row.get('Option Type', ''),
                    'last_updated': datetime.now().isoformat()
                })
        
        return {
            'endpoint': endpoint_key,
            'total_derivatives': len(derivatives_data),
            'derivatives': derivatives_data,
            'last_updated': datetime.now().isoformat()
        }
    
    def save_symbols_to_parquet(self, symbols_data: Dict, category: str) -> bool:
        """
        Save symbol data to Parquet files
        
        Args:
            symbols_data (Dict): Processed symbol data
            category (str): Data category (indices, etfs, derivatives)
            
        Returns:
            bool: Success status
        """
        try:
            # Convert to DataFrame
            if category == 'indices' and 'symbols' in symbols_data:
                df = pd.DataFrame(symbols_data['symbols'])
            elif category == 'etfs' and 'etfs' in symbols_data:
                df = pd.DataFrame(symbols_data['etfs'])
            elif category == 'derivatives' and 'derivatives' in symbols_data:
                df = pd.DataFrame(symbols_data['derivatives'])
            else:
                print(f"❌ Invalid data structure for {category}")
                return False
            
            # Save to Parquet
            endpoint = symbols_data.get('endpoint', 'unknown')
            file_path = self.nse_symbols_dir / f"{category}_{endpoint}.parquet"
            
            df.to_parquet(file_path, compression='snappy')
            print(f"💾 Saved {len(df)} {category} symbols to {file_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save {category} data: {e}")
            return False
    
    def fetch_all_nse_data(self, save_to_parquet: bool = True) -> Dict[str, any]:
        """
        Fetch all NSE data and optionally save to Parquet
        
        Args:
            save_to_parquet (bool): Whether to save data to Parquet files
            
        Returns:
            Dict: Complete NSE data collection
        """
        all_data = {
            'indices': {},
            'etfs': {},
            'derivatives': {},
            'fetch_timestamp': datetime.now().isoformat()
        }
        
        # Process Index data
        index_endpoints = ['nifty50', 'nifty100', 'nifty200', 'nifty_smallcap100']
        for endpoint in index_endpoints:
            print(f"\n📊 Processing {endpoint} index data...")
            data = self.process_index_constituents(endpoint)
            if data:
                all_data['indices'][endpoint] = data
                if save_to_parquet:
                    self.save_symbols_to_parquet(data, 'indices')
        
        # Process ETF data
        etf_endpoints = ['nifty50_etf', 'gold_etf', 'all_etf']
        for endpoint in etf_endpoints:
            print(f"\n💰 Processing {endpoint} ETF data...")
            data = self.process_etf_data(endpoint)
            if data:
                all_data['etfs'][endpoint] = data
                if save_to_parquet:
                    self.save_symbols_to_parquet(data, 'etfs')
        
        # Process Derivatives data
        derivatives_endpoints = ['stock_options']
        for endpoint in derivatives_endpoints:
            print(f"\n⚡ Processing {endpoint} derivatives data...")
            data = self.process_derivatives_data(endpoint)
            if data:
                all_data['derivatives'][endpoint] = data
                if save_to_parquet:
                    self.save_symbols_to_parquet(data, 'derivatives')
        
        return all_data
    
    def get_fyers_symbols_by_category(self, category: str, endpoint: str = None) -> List[str]:
        """
        Get Fyers format symbols by category
        
        Args:
            category (str): Category (indices, etfs, derivatives)
            endpoint (str): Specific endpoint or None for all
            
        Returns:
            List[str]: List of Fyers format symbols
        """
        symbols = []
        
        # Load from Parquet files
        if endpoint:
            file_path = self.nse_symbols_dir / f"{category}_{endpoint}.parquet"
            if file_path.exists():
                df = pd.read_parquet(file_path)
                symbols.extend(df['fyers_symbol'].tolist())
        else:
            # Load all files for the category
            for file_path in self.nse_symbols_dir.glob(f"{category}_*.parquet"):
                df = pd.read_parquet(file_path)
                symbols.extend(df['fyers_symbol'].tolist())
        
        return list(set(symbols))  # Remove duplicates
    
    def cleanup_temp_files(self, older_than_hours: int = 24, file_extensions: List[str] = None):
        """
        Clean up temporary files older than specified hours
        
        Args:
            older_than_hours (int): Delete files older than this many hours
            file_extensions (List[str]): File extensions to clean (default: ['csv', 'txt'])
        """
        if file_extensions is None:
            file_extensions = ['csv', 'txt']
            
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        for ext in file_extensions:
            for temp_file in self.nse_symbols_dir.glob(f"*.{ext}"):
                try:
                    if temp_file.stat().st_mtime < cutoff_time.timestamp():
                        temp_file.unlink()
                        print(f"🗑️ Deleted old temp file: {temp_file.name}")
                except Exception as e:
                    print(f"❌ Failed to delete {temp_file.name}: {e}")
    
    def cleanup_all_temp_files(self):
        """Clean up all temporary CSV and TXT files immediately"""
        for ext in ['csv', 'txt']:
            for temp_file in self.nse_symbols_dir.glob(f"*.{ext}"):
                try:
                    temp_file.unlink()
                    print(f"🗑️ Deleted temp file: {temp_file.name}")
                except Exception as e:
                    print(f"❌ Failed to delete {temp_file.name}: {e}")


def get_nse_fetcher() -> NSEDataFetcher:
    """Get NSE data fetcher instance"""
    return NSEDataFetcher()


if __name__ == "__main__":
    # Example usage
    fetcher = get_nse_fetcher()
    
    print("🚀 Starting NSE data fetch...")
    all_data = fetcher.fetch_all_nse_data(save_to_parquet=True)
    
    print(f"\n📊 Fetch Summary:")
    print(f"Indices: {len(all_data['indices'])} endpoints")
    print(f"ETFs: {len(all_data['etfs'])} endpoints")  
    print(f"Derivatives: {len(all_data['derivatives'])} endpoints")
    
    # Get Nifty50 symbols in Fyers format
    nifty50_symbols = fetcher.get_fyers_symbols_by_category('indices', 'nifty50')
    print(f"\n🎯 Nifty50 Fyers symbols: {len(nifty50_symbols)}")
    
    # Cleanup old files
    fetcher.cleanup_temp_files()
    
    print("\n✅ NSE data fetch completed!")