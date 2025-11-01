# Services Directory

## Microservice Architecture

This directory contains service modules for the parallel data processing pipeline.

### Services

1. **SymbolLoadingService** - Loads and caches symbols from CSV files
2. **DataDownloadService** - Parallel historical data downloads  
3. **BacktestingService** - Strategy backtesting at scale
4. **ServiceOrchestrator** - Coordinates all services

### Architecture

```
ServiceOrchestrator
├── SymbolLoadingService (loads 9K+ symbols)
├── DataDownloadService (10 workers, 6 timeframes)
└── BacktestingService (8 workers, 100+ strategies)
```

### Usage

```python
from scripts.services.service_orchestrator import ServiceOrchestrator

# Initialize orchestrator
orchestrator = ServiceOrchestrator(
    download_workers=10,
    backtest_workers=8
)

# Run full pipeline
orchestrator.run_full_pipeline(
    download_data=True,
    run_backtests=True,
    category='nifty50',
    timeframes=['1D', '1m'],
    strategies=['RSI_Strategy', 'MACD_Strategy']
)
```

### Features

- **Parallel Processing**: 10 download workers, 8 backtest workers
- **Real-time Progress**: Rich progress bars and metrics
- **Service Isolation**: Each service is independent and reusable
- **Scalability**: Handle 9K symbols × 6 timeframes × 100+ strategies = 5.4M tests
- **Error Handling**: Resilient with auto-retry and detailed logging
