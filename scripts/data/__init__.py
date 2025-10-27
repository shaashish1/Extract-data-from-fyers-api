"""
Data Management Module
=======================
Data storage, processing, and management utilities.

Components:
- data_storage.py: Parquet data manager
- timeframe_converter.py: Timeframe conversion utilities
- update_tables.py: Data update management
"""

from .data_storage import ParquetDataManager

__all__ = ['ParquetDataManager']