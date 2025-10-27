"""
Market Data Module
==================
Market data collection, analysis, and storage management.

Components:
- stocks_data.py: Stock data collection and historical data extraction
- data_analysis.py: Market data analysis and reporting tools  
- market_depth_storage.py: Level 2 market depth management (production version)
"""

from .market_depth_storage import MarketDepthManager

__all__ = ['MarketDepthManager']