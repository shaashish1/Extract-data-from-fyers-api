# Fyers Scripts Package
"""
FYERS WebSocket Live - Organized scripts package.

Structure:
- auth/: Authentication and configuration
- websocket/: Real-time WebSocket streaming  
- market_data/: Market data collection and analysis
- symbol_discovery/: Symbol discovery and management (156K+ symbols)
- data/: Data storage and management
- core/: Core utilities and constants
- archive/: Archived old scripts
- test/: Testing utilities
"""

# Import commonly used classes for backward compatibility
import sys
from pathlib import Path

# Add subdirectories to path for easier imports
scripts_dir = Path(__file__).parent
for subdir in ['auth', 'core', 'data', 'symbol_discovery', 'market_data', 'websocket']:
    sys.path.insert(0, str(scripts_dir / subdir))

__version__ = "1.0.0"
__author__ = "Fyers WebSocket Live Project"