"""Centralized symbol lists for major NSE indices.

These lists are curated for use with the Fyers API and downstream
market-data collection utilities. Each function returns a freshly
copied list to avoid accidental mutation of the module-level
constants.
"""
from typing import List

# ---------------------------------------------------------------------------
# Nifty 50 (exactly 50 symbols)
# ---------------------------------------------------------------------------
NIFTY50_SYMBOLS: List[str] = [
    "NSE:RELIANCE-EQ",
    "NSE:TCS-EQ",
    "NSE:HDFCBANK-EQ",
    "NSE:ICICIBANK-EQ",
    "NSE:HINDUNILVR-EQ",
    "NSE:INFY-EQ",
    "NSE:ITC-EQ",
    "NSE:SBIN-EQ",
    "NSE:BHARTIARTL-EQ",
    "NSE:KOTAKBANK-EQ",
    "NSE:LT-EQ",
    "NSE:AXISBANK-EQ",
    "NSE:ASIANPAINT-EQ",
    "NSE:MARUTI-EQ",
    "NSE:SUNPHARMA-EQ",
    "NSE:TITAN-EQ",
    "NSE:BAJFINANCE-EQ",
    "NSE:HCLTECH-EQ",
    "NSE:ULTRACEMCO-EQ",
    "NSE:WIPRO-EQ",
    "NSE:NESTLEIND-EQ",
    "NSE:NTPC-EQ",
    "NSE:POWERGRID-EQ",
    "NSE:TATAMOTORS-EQ",
    "NSE:ADANIENT-EQ",
    "NSE:BAJAJFINSV-EQ",
    "NSE:ONGC-EQ",
    "NSE:COALINDIA-EQ",
    "NSE:TATASTEEL-EQ",
    "NSE:DIVISLAB-EQ",
    "NSE:TECHM-EQ",
    "NSE:HINDALCO-EQ",
    "NSE:DRREDDY-EQ",
    "NSE:CIPLA-EQ",
    "NSE:INDUSINDBK-EQ",
    "NSE:JSWSTEEL-EQ",
    "NSE:GRASIM-EQ",
    "NSE:BRITANNIA-EQ",
    "NSE:M&M-EQ",
    "NSE:EICHERMOT-EQ",
    "NSE:BAJAJ-AUTO-EQ",
    "NSE:BPCL-EQ",
    "NSE:ADANIPORTS-EQ",
    "NSE:IOC-EQ",
    "NSE:APOLLOHOSP-EQ",
    "NSE:SHRIRAMFIN-EQ",
    "NSE:LTIM-EQ",
    "NSE:HEROMOTOCO-EQ",
    "NSE:SBILIFE-EQ",
    "NSE:PIDILITIND-EQ",
]

# ---------------------------------------------------------------------------
# Nifty 100 (Nifty 50 + 50 additional large/mid cap symbols)
# ---------------------------------------------------------------------------
NIFTY100_SYMBOLS: List[str] = [
    "NSE:RELIANCE-EQ",
    "NSE:TCS-EQ",
    "NSE:HDFCBANK-EQ",
    "NSE:ICICIBANK-EQ",
    "NSE:HINDUNILVR-EQ",
    "NSE:INFY-EQ",
    "NSE:ITC-EQ",
    "NSE:SBIN-EQ",
    "NSE:BHARTIARTL-EQ",
    "NSE:KOTAKBANK-EQ",
    "NSE:LT-EQ",
    "NSE:AXISBANK-EQ",
    "NSE:ASIANPAINT-EQ",
    "NSE:MARUTI-EQ",
    "NSE:SUNPHARMA-EQ",
    "NSE:TITAN-EQ",
    "NSE:BAJFINANCE-EQ",
    "NSE:HCLTECH-EQ",
    "NSE:ULTRACEMCO-EQ",
    "NSE:WIPRO-EQ",
    "NSE:NESTLEIND-EQ",
    "NSE:NTPC-EQ",
    "NSE:POWERGRID-EQ",
    "NSE:TATAMOTORS-EQ",
    "NSE:ADANIENT-EQ",
    "NSE:BAJAJFINSV-EQ",
    "NSE:ONGC-EQ",
    "NSE:COALINDIA-EQ",
    "NSE:TATASTEEL-EQ",
    "NSE:DIVISLAB-EQ",
    "NSE:TECHM-EQ",
    "NSE:HINDALCO-EQ",
    "NSE:DRREDDY-EQ",
    "NSE:CIPLA-EQ",
    "NSE:INDUSINDBK-EQ",
    "NSE:JSWSTEEL-EQ",
    "NSE:GRASIM-EQ",
    "NSE:BRITANNIA-EQ",
    "NSE:M&M-EQ",
    "NSE:EICHERMOT-EQ",
    "NSE:BAJAJ-AUTO-EQ",
    "NSE:BPCL-EQ",
    "NSE:ADANIPORTS-EQ",
    "NSE:IOC-EQ",
    "NSE:APOLLOHOSP-EQ",
    "NSE:SHRIRAMFIN-EQ",
    "NSE:LTIM-EQ",
    "NSE:HEROMOTOCO-EQ",
    "NSE:SBILIFE-EQ",
    "NSE:PIDILITIND-EQ",
    "NSE:TATACONSUM-EQ",
    "NSE:GODREJCP-EQ",
    "NSE:UPL-EQ",
    "NSE:HDFCLIFE-EQ",
    "NSE:ICICIPRULI-EQ",
    "NSE:VEDL-EQ",
    "NSE:TRENT-EQ",
    "NSE:DABUR-EQ",
    "NSE:JINDALSTEL-EQ",
    "NSE:GAIL-EQ",
    "NSE:LICI-EQ",
    "NSE:BAJAJHLDNG-EQ",
    "NSE:BANKBARODA-EQ",
    "NSE:SIEMENS-EQ",
    "NSE:ABB-EQ",
    "NSE:MARICO-EQ",
    "NSE:NAUKRI-EQ",
    "NSE:TORNTPHARM-EQ",
    "NSE:MUTHOOTFIN-EQ",
    "NSE:BERGEPAINT-EQ",
    "NSE:CHOLAFIN-EQ",
    "NSE:AMBUJACEM-EQ",
    "NSE:LUPIN-EQ",
    "NSE:SAIL-EQ",
    "NSE:BOSCHLTD-EQ",
    "NSE:MOTHERSON-EQ",
    "NSE:HAVELLS-EQ",
    "NSE:PNB-EQ",
    "NSE:CUMMINSIND-EQ",
    "NSE:MCDOWELL-N-EQ",
    "NSE:COLPAL-EQ",
    "NSE:CANFINHOME-EQ",
    "NSE:INDIGO-EQ",
    "NSE:ESCORTS-EQ",
    "NSE:BATAINDIA-EQ",
    "NSE:AUBANK-EQ",
    "NSE:HINDZINC-EQ",
    "NSE:BANDHANBNK-EQ",
    "NSE:VOLTAS-EQ",
    "NSE:DALBHARAT-EQ",
    "NSE:POLYCAB-EQ",
    "NSE:BEL-EQ",
    "NSE:IDFCFIRSTB-EQ",
    "NSE:BIOCON-EQ",
    "NSE:RBLBANK-EQ",
    "NSE:OFSS-EQ",
    "NSE:ZYDUSLIFE-EQ",
    "NSE:CONCOR-EQ",
    "NSE:PAGEIND-EQ",
    "NSE:LTTS-EQ",
]

if len(NIFTY100_SYMBOLS) != 100:
    raise ValueError(f"Expected 100 unique Nifty 100 symbols, found {len(NIFTY100_SYMBOLS)}")

# ---------------------------------------------------------------------------
# Nifty 200 (Nifty 100 + 100 additional liquid constituents)
# ---------------------------------------------------------------------------
NIFTY200_SYMBOLS: List[str] = [
    *NIFTY100_SYMBOLS,
    "NSE:ZEEL-EQ",
    "NSE:PVR-EQ",
    "NSE:INOXLEISUR-EQ",
    "NSE:ADANIGREEN-EQ",
    "NSE:ADANIPOWER-EQ",
    "NSE:ADANITRANS-EQ",
    "NSE:RPOWER-EQ",
    "NSE:TORNTPOWER-EQ",
    "NSE:BHEL-EQ",
    "NSE:CROMPTON-EQ",
    "NSE:WHIRLPOOL-EQ",
    "NSE:JKCEMENT-EQ",
    "NSE:INDIACEM-EQ",
    "NSE:ORIENT-EQ",
    "NSE:JKPAPER-EQ",
    "NSE:BALRAMCHIN-EQ",
    "NSE:CHAMBLFERT-EQ",
    "NSE:COROMANDEL-EQ",
    "NSE:GNFC-EQ",
    "NSE:GSFC-EQ",
    "NSE:NFL-EQ",
    "NSE:RCF-EQ",
    "NSE:SRF-EQ",
    "NSE:TATACHEMICALS-EQ",
    "NSE:AJANTA-EQ",
    "NSE:APLAPOLLO-EQ",
    "NSE:AAVAS-EQ",
    "NSE:ABCAPITAL-EQ",
    "NSE:ABFRL-EQ",
    "NSE:ADANIGAS-EQ",
    "NSE:AIAENG-EQ",
    "NSE:AJANTPHARM-EQ",
    "NSE:AKZOINDIA-EQ",
    "NSE:ALKYLAMINE-EQ",
    "NSE:ALLCARGO-EQ",
    "NSE:AMARAJABAT-EQ",
    "NSE:APLLTD-EQ",
    "NSE:ARVINDFASN-EQ",
    "NSE:ASAHIINDIA-EQ",
    "NSE:ASTRAL-EQ",
    "NSE:ATUL-EQ",
    "NSE:AVANTIFEED-EQ",
    "NSE:BAJAJCON-EQ",
    "NSE:BEML-EQ",
    "NSE:BHARATFORG-EQ",
    "NSE:BIRLACORPN-EQ",
    "NSE:BLUEDART-EQ",
    "NSE:BSOFT-EQ",
    "NSE:CAPLIPOINT-EQ",
    "NSE:CARBORUNIV-EQ",
    "NSE:CASTROLIND-EQ",
    "NSE:CCL-EQ",
    "NSE:CERA-EQ",
    "NSE:CHEMCON-EQ",
    "NSE:CHEMPLASTS-EQ",
    "NSE:CHENNPETRO-EQ",
    "NSE:CHOLAHLDNG-EQ",
    "NSE:CUB-EQ",
    "NSE:CYIENT-EQ",
    "NSE:DBREALTY-EQ",
    "NSE:DEEPAKFERT-EQ",
    "NSE:DEEPAKNTR-EQ",
    "NSE:DHANUKA-EQ",
    "NSE:DIXON-EQ",
    "NSE:DMART-EQ",
    "NSE:EDELWEISS-EQ",
    "NSE:EMAMILTD-EQ",
    "NSE:ENDURANCE-EQ",
    "NSE:ENGINERSIN-EQ",
    "NSE:EQUITAS-EQ",
    "NSE:ERIS-EQ",
    "NSE:ESABINDIA-EQ",
    "NSE:EXIDEIND-EQ",
    "NSE:FDC-EQ",
    "NSE:FINEORG-EQ",
    "NSE:FINCABLES-EQ",
    "NSE:FORCEMOT-EQ",
    "NSE:FORTIS-EQ",
    "NSE:GESHIP-EQ",
    "NSE:GILLETTE-EQ",
    "NSE:GLAXO-EQ",
    "NSE:GLENMARK-EQ",
    "NSE:GMRINFRA-EQ",
    "NSE:GODFRYPHLP-EQ",
    "NSE:GRANULES-EQ",
    "NSE:GRAPHITE-EQ",
    "NSE:GREAVESCOT-EQ",
    "NSE:GRINDWELL-EQ",
    "NSE:GTLINFRA-EQ",
    "NSE:GUJALKALI-EQ",
    "NSE:GUJGASLTD-EQ",
    "NSE:GULFOILLUB-EQ",
    "NSE:HAL-EQ",
    "NSE:HAPPSTMNDS-EQ",
    "NSE:HATSUN-EQ",
    "NSE:HEIDELBERG-EQ",
    "NSE:HEXAWARE-EQ",
    "NSE:HFCL-EQ",
    "NSE:HIMATSEIDE-EQ",
    "NSE:PIIND-EQ",
]

if len(NIFTY200_SYMBOLS) != 200:
    raise ValueError(f"Expected 200 unique Nifty 200 symbols, found {len(NIFTY200_SYMBOLS)}")

# ---------------------------------------------------------------------------
# Bank Nifty Constituents (Banking sector stocks)
# ---------------------------------------------------------------------------
BANK_NIFTY_SYMBOLS: List[str] = [
    "NSE:HDFCBANK-EQ",
    "NSE:ICICIBANK-EQ", 
    "NSE:SBIN-EQ",
    "NSE:KOTAKBANK-EQ",
    "NSE:AXISBANK-EQ",
    "NSE:INDUSINDBK-EQ",
    "NSE:BANKBARODA-EQ",
    "NSE:PNB-EQ",
    "NSE:IDFCFIRSTB-EQ",
    "NSE:BANDHANBNK-EQ",
    "NSE:RBLBANK-EQ",
    "NSE:AUBANK-EQ"
]

# ---------------------------------------------------------------------------
# Popular ETFs (Exchange Traded Funds)
# ---------------------------------------------------------------------------
POPULAR_ETFS: List[str] = [
    "NSE:NIFTYBEES-ETF",
    "NSE:BANKBEES-ETF", 
    "NSE:GOLDBEES-ETF",
    "NSE:LIQUIDBEES-ETF",
    "NSE:JUNIORBEES-ETF",
    "NSE:ITBEES-ETF",
    "NSE:PHARMABEES-ETF",
    "NSE:PSUBNKBEES-ETF"
]

# ---------------------------------------------------------------------------
# Major Market Indices
# ---------------------------------------------------------------------------
MAJOR_INDICES: List[str] = [
    "NSE:NIFTY50-INDEX",
    "NSE:NIFTYBANK-INDEX", 
    "NSE:NIFTY-INDEX",
    "NSE:FINNIFTY-INDEX",
    "NSE:NIFTYMIDCAP50-INDEX",
    "NSE:NIFTYSMALLCAP50-INDEX",
    "NSE:NIFTYIT-INDEX",
    "NSE:NIFTYPHARMA-INDEX",
    "NSE:NIFTYAUTO-INDEX",
    "NSE:NIFTYMETAL-INDEX",
    "NSE:NIFTYREALTY-INDEX",
    "NSE:INDIAVIX-INDEX"
]


def get_nifty50_symbols() -> List[str]:
    """Return a copy of the Nifty 50 symbols."""
    return list(NIFTY50_SYMBOLS)


def get_nifty100_symbols() -> List[str]:
    """Return a copy of the Nifty 100 symbols."""
    return list(NIFTY100_SYMBOLS)


def get_nifty200_symbols() -> List[str]:
    """Return a copy of the Nifty 200 symbols."""
    return list(NIFTY200_SYMBOLS)


def get_bank_nifty_symbols() -> List[str]:
    """Return a copy of the Bank Nifty symbols."""
    return list(BANK_NIFTY_SYMBOLS)


def get_popular_etfs() -> List[str]:
    """Return a copy of the popular ETF symbols."""
    return list(POPULAR_ETFS)


def get_major_indices() -> List[str]:
    """Return a copy of the major index symbols."""
    return list(MAJOR_INDICES)


def get_index_symbols(index_name: str) -> List[str]:
    """Generic accessor for index symbol lists.

    Args:
        index_name: One of "nifty50", "nifty100", or "nifty200" (case-insensitive).

    Returns:
        List of Fyers-formatted symbols associated with the index.

    Raises:
        KeyError: If an unsupported index name is provided.
    """

    lookup = {
        "nifty50": NIFTY50_SYMBOLS,
        "nifty100": NIFTY100_SYMBOLS,
        "nifty200": NIFTY200_SYMBOLS,
    }

    key = index_name.lower()
    if key not in lookup:
        raise KeyError(f"Unsupported index name: {index_name}")
    return list(lookup[key])
