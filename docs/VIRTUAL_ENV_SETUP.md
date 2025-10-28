# Virtual Environment Setup for Backtesting

## 🎯 Problem Statement

**Python Version Conflict:**
- **Fyers API:** Works with Python 3.14 ✅
- **vectorbt:** Requires Python <3.14 (Numba limitation) ❌

**Solution:** Create isolated Python 3.13 environment for backtesting while keeping Python 3.14 for Fyers API work.

---

## 🚀 Quick Setup Guide

### Step 1: Check Python 3.13 Availability

```powershell
# Check if Python 3.13 is installed
py -3.13 --version

# Expected output:
# Python 3.13.x
```

**If Python 3.13 is not installed:**
1. Download from: https://www.python.org/downloads/
2. Install Python 3.13.x (latest stable)
3. ✅ **Important:** Check "Add Python to PATH" during installation
4. Verify installation: `py -3.13 --version`

---

### Step 2: Create Virtual Environment

```powershell
# Navigate to project root
cd D:\Learn_Coding\extract-data-from-fyers-api\Extract-data-from-fyers-api

# Create virtual environment with Python 3.13
py -3.13 -m venv venv_backtesting

# Expected output:
# Created virtual environment at: .\venv_backtesting\
```

**Directory Structure:**
```
Extract-data-from-fyers-api/
├── venv_backtesting/          # Python 3.13 environment ⭐ NEW
│   ├── Scripts/
│   │   ├── Activate.ps1       # PowerShell activation
│   │   ├── python.exe         # Python 3.13 interpreter
│   │   └── pip.exe            # Package installer
│   ├── Lib/
│   └── pyvenv.cfg
├── scripts/
├── data/
└── ...
```

---

### Step 3: Activate Virtual Environment

```powershell
# Activate the environment
.\venv_backtesting\Scripts\Activate.ps1

# Your prompt should change to:
# (venv_backtesting) PS D:\Learn_Coding\extract-data-from-fyers-api\Extract-data-from-fyers-api>

# Verify Python version
python --version
# Should show: Python 3.13.x (not 3.14)
```

**Troubleshooting Activation Issues:**

If you get execution policy error:
```powershell
# Option 1: Bypass policy for current session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Then activate again
.\venv_backtesting\Scripts\Activate.ps1

# Option 2: Use activate.bat instead
.\venv_backtesting\Scripts\activate.bat
```

---

### Step 4: Install Backtesting Dependencies

```powershell
# Ensure environment is activated (check prompt for "venv_backtesting")

# Upgrade pip first
python -m pip install --upgrade pip

# Install vectorbt (this will also install numba, pandas, numpy)
pip install vectorbt

# Install additional dependencies
pip install plotly          # Interactive visualizations
pip install pyarrow         # Parquet file support (if not already installed)
pip install jupyter         # Notebook support (optional)
pip install matplotlib      # Additional plotting (optional)

# Install project requirements (if you have requirements.txt)
pip install -r requirements.txt
```

**Expected Installation Output:**
```
Collecting vectorbt
  Downloading vectorbt-0.28.1-py3-none-any.whl
Collecting numba>=0.57.0
  Downloading numba-0.60.0-cp313-cp313-win_amd64.whl
...
Successfully installed vectorbt-0.28.1 numba-0.60.0 ...
```

---

### Step 5: Verify Installation

```powershell
# Test vectorbt installation
python -c "import vectorbt as vbt; print(f'✅ vectorbt {vbt.__version__} installed successfully!')"

# Test data loader compatibility
python scripts\backtesting\engine\data_loader.py

# Expected output:
# ================================================================================
# Backtest Data Loader Demo
# ================================================================================
# ... (data loading demo results)
```

---

## 🔄 Environment Switching Workflow

### For Fyers API Work (Market Data, Authentication, etc.)

```powershell
# Use system Python 3.14 (default)
python scripts\market_data\quotes_api.py
python scripts\market_data\history_api.py
python scripts\symbol_discovery\comprehensive_symbol_discovery.py

# No environment activation needed - uses global Python
```

### For Backtesting Work (Strategies, Optimization, Analysis)

```powershell
# 1. Activate backtesting environment
.\venv_backtesting\Scripts\Activate.ps1

# 2. Run backtesting scripts
python scripts\backtesting\engine\data_loader.py
python scripts\backtesting\strategies\ma_crossover.py
python scripts\backtesting\analysis\strategy_ranker.py

# 3. Deactivate when done
deactivate
```

---

## 📋 Environment Management Commands

### Activation
```powershell
# PowerShell
.\venv_backtesting\Scripts\Activate.ps1

# Command Prompt
.\venv_backtesting\Scripts\activate.bat

# Git Bash
source venv_backtesting/Scripts/activate
```

### Deactivation
```powershell
# Works in all shells
deactivate
```

### Check Current Environment
```powershell
# Check Python version
python --version

# Check Python path
python -c "import sys; print(sys.executable)"

# Check installed packages
pip list

# Check vectorbt specifically
pip show vectorbt
```

### Update Dependencies
```powershell
# Activate environment first
.\venv_backtesting\Scripts\Activate.ps1

# Update pip
python -m pip install --upgrade pip

# Update vectorbt
pip install --upgrade vectorbt

# Update all packages
pip list --outdated
pip install --upgrade <package_name>
```

### Recreate Environment (if needed)
```powershell
# Deactivate if active
deactivate

# Remove old environment
Remove-Item -Recurse -Force venv_backtesting

# Create fresh environment
py -3.13 -m venv venv_backtesting

# Activate and reinstall
.\venv_backtesting\Scripts\Activate.ps1
pip install vectorbt plotly pyarrow
```

---

## 🎯 VS Code Integration

### Configure VS Code to Use Virtual Environment

**Option 1: Python Interpreter Selection**
1. Open VS Code in project folder
2. Press `Ctrl+Shift+P`
3. Type "Python: Select Interpreter"
4. Choose: `.\venv_backtesting\Scripts\python.exe`

**Option 2: Workspace Settings**

Create/edit `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv_backtesting/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true
}
```

**Benefits:**
- ✅ VS Code automatically activates environment in new terminals
- ✅ IntelliSense works with vectorbt
- ✅ Debugging uses correct Python version
- ✅ Jupyter notebooks use virtual environment kernel

---

## 📦 Requirements Management

### Create requirements.txt for Backtesting Environment

```powershell
# Activate environment
.\venv_backtesting\Scripts\Activate.ps1

# Export installed packages
pip freeze > requirements_backtesting.txt

# Deactivate
deactivate
```

**Sample `requirements_backtesting.txt`:**
```
vectorbt==0.28.1
numba==0.60.0
pandas==2.2.0
numpy==1.26.4
plotly==5.18.0
pyarrow==14.0.1
matplotlib==3.8.2
jupyter==1.0.0
```

### Install from requirements.txt (on new machine)
```powershell
# Create and activate environment
py -3.13 -m venv venv_backtesting
.\venv_backtesting\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements_backtesting.txt
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Python 3.13 Not Found
```powershell
py -3.13 --version
# py.exe: can't open file '3.13': [Errno 2] No such file or directory
```

**Solution:**
1. Install Python 3.13 from https://www.python.org/downloads/
2. Verify installation: `py --list` (should show 3.13)
3. Try again: `py -3.13 -m venv venv_backtesting`

### Issue 2: Activation Script Blocked
```powershell
.\venv_backtesting\Scripts\Activate.ps1
# ... cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
# Temporarily bypass execution policy
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Or use .bat file instead
.\venv_backtesting\Scripts\activate.bat
```

### Issue 3: vectorbt Installation Fails in Virtual Environment
```powershell
pip install vectorbt
# ERROR: Could not find a version that satisfies the requirement numba...
```

**Solution:**
```powershell
# Verify you're in Python 3.13 environment
python --version  # Should show 3.13.x

# Try installing numba first
pip install numba

# Then install vectorbt
pip install vectorbt
```

### Issue 4: Wrong Python Version in VS Code
**Problem:** VS Code still uses Python 3.14 even after environment setup

**Solution:**
1. Close all VS Code terminals
2. Press `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose `.\venv_backtesting\Scripts\python.exe`
4. Open new terminal (should auto-activate)
5. Verify: `python --version` (should show 3.13.x)

---

## 🎓 Best Practices

### 1. Separate Concerns
```
✅ DO: Use Python 3.14 for Fyers API work
✅ DO: Use venv_backtesting (Python 3.13) for vectorbt work
❌ DON'T: Mix environments - causes dependency conflicts
```

### 2. Document Dependencies
```powershell
# Always maintain up-to-date requirements file
pip freeze > requirements_backtesting.txt
git add requirements_backtesting.txt
git commit -m "Update backtesting dependencies"
```

### 3. Ignore Virtual Environment in Git
```gitignore
# .gitignore
venv_backtesting/
*.pyc
__pycache__/
```

### 4. Environment Variables (if needed)
```powershell
# Set environment-specific variables in activation script
# Edit: venv_backtesting\Scripts\Activate.ps1

# Add before deactivate function:
$env:BACKTESTING_MODE = "True"
$env:VECTORBT_CACHE_DIR = ".\cache\vectorbt"
```

---

## 🔗 Integration with Existing Project

### File Organization
```
Extract-data-from-fyers-api/
├── venv_backtesting/          # Python 3.13 + vectorbt
├── scripts/
│   ├── auth/                  # Python 3.14 (Fyers API)
│   ├── market_data/           # Python 3.14 (Fyers API)
│   ├── backtesting/           # Python 3.13 (vectorbt) ⭐
│   │   ├── engine/
│   │   │   └── data_loader.py
│   │   ├── strategies/
│   │   │   ├── built_in/
│   │   │   └── custom/
│   │   └── analysis/
│   └── ...
├── requirements.txt           # Main project (Python 3.14)
├── requirements_backtesting.txt  # Backtesting (Python 3.13) ⭐
└── .gitignore
```

### Workflow Example
```powershell
# Morning: Download fresh market data (Python 3.14)
python scripts\market_data\history_api.py

# Afternoon: Run backtests on new data (Python 3.13)
.\venv_backtesting\Scripts\Activate.ps1
python scripts\backtesting\strategies\run_all.py
deactivate

# Evening: Update trading signals (Python 3.14)
python scripts\signal_generator\generate_signals.py
```

---

## 📈 Next Steps After Setup

### 1. Verify Installation ✅
```powershell
.\venv_backtesting\Scripts\Activate.ps1
python -c "import vectorbt as vbt; print(vbt.__version__)"
python scripts\backtesting\engine\data_loader.py
deactivate
```

### 2. Implement First Strategy
```powershell
.\venv_backtesting\Scripts\Activate.ps1
python scripts\backtesting\strategies\ma_crossover.py
```

### 3. Run Backtests on Available Data
```powershell
# Test with limited data (8 symbols, 2-4 days)
python scripts\backtesting\analysis\test_strategies.py
```

### 4. Wait for API Recovery, Download Data
```powershell
# After midnight IST, back to Python 3.14
deactivate
python scripts\market_data\history_api.py
```

### 5. Run Full Backtests
```powershell
# Switch back to backtesting environment
.\venv_backtesting\Scripts\Activate.ps1
python scripts\backtesting\analysis\run_all_strategies.py
```

---

## 🎯 Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐍 DUAL PYTHON ENVIRONMENT SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 MAIN ENVIRONMENT (System Python 3.14)
  Purpose:    Fyers API, Market Data, Authentication
  Usage:      python scripts\market_data\*.py
  Status:     ✅ WORKING

🔬 BACKTESTING ENVIRONMENT (venv_backtesting Python 3.13)
  Purpose:    vectorbt, Strategy Backtesting, Optimization
  Activation: .\venv_backtesting\Scripts\Activate.ps1
  Usage:      python scripts\backtesting\*.py
  Status:     ⏳ TO BE CREATED

🎯 SETUP COMMANDS
  1. py -3.13 -m venv venv_backtesting
  2. .\venv_backtesting\Scripts\Activate.ps1
  3. pip install vectorbt plotly pyarrow
  4. python -c "import vectorbt as vbt; print(vbt.__version__)"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ READY TO PROCEED: Create virtual environment and install vectorbt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

**Created:** October 28, 2025  
**Purpose:** Resolve Python version conflict between Fyers (3.14) and vectorbt (<3.14)  
**Status:** Ready for implementation  
**Next:** Execute setup commands and verify installation
