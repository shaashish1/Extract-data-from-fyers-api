# Python 3.13 Installation Guide for vectorbt

## 🎯 Current Situation

**System Python:** Python 3.14.0 (at `C:\Python314\`)  
**Required for vectorbt:** Python 3.13.x or lower (Numba limitation)  
**Solution:** Install Python 3.13 side-by-side with Python 3.14

---

## 📥 Step 1: Download Python 3.13

### Option A: Official Python.org (Recommended)

1. **Visit:** https://www.python.org/downloads/
2. **Find Python 3.13.x** (latest stable 3.13 release)
3. **Download:** Windows installer (64-bit)
   - File: `python-3.13.x-amd64.exe`

### Option B: Direct Download Link
- **Latest 3.13:** https://www.python.org/downloads/release/python-3130/
- Choose: **Windows installer (64-bit)**

---

## 🔧 Step 2: Install Python 3.13

### Installation Settings

**⚠️ IMPORTANT:** Use these exact settings during installation:

#### 1. **Initial Screen**
- ✅ **CHECK:** "Add python.exe to PATH"
- ✅ **CHECK:** "Install launcher for all users (recommended)"
- Click: **"Customize installation"** (don't use "Install Now")

#### 2. **Optional Features**
- ✅ **CHECK ALL:**
  - Documentation
  - pip
  - tcl/tk and IDLE
  - Python test suite
  - py launcher
- Click: **"Next"**

#### 3. **Advanced Options** ⭐ CRITICAL
- ✅ **CHECK:**
  - Install for all users
  - Associate files with Python (requires py launcher)
  - Create shortcuts for installed applications
  - Add Python to environment variables
  - Precompile standard library
  - Download debugging symbols
  
- ⚠️ **CUSTOMIZE INSTALL LOCATION:**
  - Default: `C:\Program Files\Python313\`
  - **Change to:** `C:\Python313\` ⭐ IMPORTANT
  
  **Why?** Keeps versions organized:
  ```
  C:\Python313\      # Python 3.13 (new)
  C:\Python314\      # Python 3.14 (existing)
  ```

- Click: **"Install"**

#### 4. **Disable Path Length Limit**
- After installation completes, you'll see: "Setup was successful"
- ✅ **CLICK:** "Disable path length limit" (optional but recommended)
- Click: **"Close"**

---

## ✅ Step 3: Verify Installation

### PowerShell Commands

```powershell
# Check Python 3.13 installation
C:\Python313\python.exe --version
# Expected: Python 3.13.x

# Check Python 3.14 (should still work)
C:\Python314\python.exe --version
# Expected: Python 3.14.0

# Check pip for Python 3.13
C:\Python313\python.exe -m pip --version
# Expected: pip 24.x ... (python 3.13)
```

### Launcher Verification

```powershell
# If py launcher is configured correctly:
py -3.13 --version  # Should show Python 3.13.x
py -3.14 --version  # Should show Python 3.14.0
py --version        # Shows default version
```

**Note:** If `py` command conflicts with Flask app, use direct paths instead:
- Python 3.13: `C:\Python313\python.exe`
- Python 3.14: `C:\Python314\python.exe`

---

## 🔨 Step 4: Create Virtual Environment

### Method 1: Using Direct Path (Recommended if `py` doesn't work)

```powershell
# Navigate to project
cd D:\Learn_Coding\extract-data-from-fyers-api\Extract-data-from-fyers-api

# Create virtual environment using Python 3.13
C:\Python313\python.exe -m venv venv_backtesting

# Verify creation
Test-Path .\venv_backtesting\Scripts\python.exe
# Should return: True
```

### Method 2: Using py launcher (if working)

```powershell
# Navigate to project
cd D:\Learn_Coding\extract-data-from-fyers-api\Extract-data-from-fyers-api

# Create virtual environment
py -3.13 -m venv venv_backtesting
```

---

## 🚀 Step 5: Activate and Install vectorbt

### Activation

```powershell
# Activate the environment
.\venv_backtesting\Scripts\Activate.ps1

# Your prompt should change to:
# (venv_backtesting) PS D:\Learn_Coding\...\Extract-data-from-fyers-api>

# Verify Python version in virtual environment
python --version
# Should show: Python 3.13.x (NOT 3.14.0)

# Verify it's using the venv Python
python -c "import sys; print(sys.executable)"
# Should show: ...\venv_backtesting\Scripts\python.exe
```

**If activation fails:**
```powershell
# Set execution policy for current session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Try activation again
.\venv_backtesting\Scripts\Activate.ps1

# Or use .bat file
.\venv_backtesting\Scripts\activate.bat
```

### Install Dependencies

```powershell
# Ensure environment is activated (check prompt)

# Upgrade pip first
python -m pip install --upgrade pip

# Install vectorbt (this installs numba, pandas, numpy automatically)
pip install vectorbt

# Install additional dependencies
pip install plotly          # Interactive visualizations
pip install pyarrow         # Parquet support
pip install jupyter         # Notebook support (optional)
pip install matplotlib      # Additional plots (optional)
pip install seaborn         # Statistical visualization (optional)

# Save installed packages
pip freeze > requirements_backtesting.txt
```

---

## ✅ Step 6: Verify vectorbt Installation

```powershell
# Ensure environment is activated

# Test vectorbt import
python -c "import vectorbt as vbt; print(f'✅ vectorbt {vbt.__version__} installed successfully!')"

# Test numba (vectorbt dependency)
python -c "import numba; print(f'✅ numba {numba.__version__} installed successfully!')"

# Test data loader compatibility
python scripts\backtesting\engine\data_loader.py
# Should run without errors

# Deactivate when done
deactivate
```

---

## 🎯 Post-Installation Checklist

### System Status After Installation

```
✅ Python 3.14.0       → C:\Python314\python.exe  (Fyers API)
✅ Python 3.13.x       → C:\Python313\python.exe  (backtesting)
✅ venv_backtesting    → .\venv_backtesting\      (virtual env)
✅ vectorbt installed  → In venv_backtesting
✅ Data loader tested  → Working
```

### Quick Reference Card

```powershell
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUICK REFERENCE - PYTHON VERSION SWITCHING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# CHECK VERSIONS
python --version                         # Shows default (3.14)
C:\Python313\python.exe --version       # Explicitly use 3.13
C:\Python314\python.exe --version       # Explicitly use 3.14

# FYERS API WORK (Python 3.14 - default)
python scripts\market_data\quotes_api.py
python scripts\market_data\history_api.py

# BACKTESTING WORK (Python 3.13 - virtual env)
.\venv_backtesting\Scripts\Activate.ps1
python scripts\backtesting\engine\data_loader.py
python scripts\backtesting\strategies\ma_crossover.py
deactivate

# CREATE NEW VENV (if needed)
C:\Python313\python.exe -m venv venv_name

# INSTALL PACKAGES IN VENV
.\venv_backtesting\Scripts\Activate.ps1
pip install package_name
deactivate
```

---

## 🚨 Troubleshooting

### Issue: "py -3.13" doesn't work (Flask app interferes)

**Solution:** Use direct Python path instead
```powershell
# Instead of:
py -3.13 -m venv venv_backtesting

# Use:
C:\Python313\python.exe -m venv venv_backtesting
```

### Issue: Activation script blocked

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\venv_backtesting\Scripts\Activate.ps1
```

### Issue: pip not found in virtual environment

**Solution:**
```powershell
# Reinstall pip in venv
.\venv_backtesting\Scripts\python.exe -m ensurepip --upgrade
```

### Issue: vectorbt installation fails even in Python 3.13 venv

**Solution:**
```powershell
# Check Python version in venv
python --version  # Must be 3.13.x

# If still 3.14, recreate venv
deactivate
Remove-Item -Recurse -Force venv_backtesting
C:\Python313\python.exe -m venv venv_backtesting
.\venv_backtesting\Scripts\Activate.ps1

# Install vectorbt
pip install vectorbt
```

### Issue: Two Python versions conflict

**Solution:** Both can coexist peacefully if:
1. Installed in separate directories (`C:\Python313\` and `C:\Python314\`)
2. Use virtual environments for project-specific dependencies
3. Use explicit paths when creating venvs

---

## 📚 Additional Resources

### Python Installation
- Official Guide: https://docs.python.org/3/using/windows.html
- Multiple Versions: https://docs.python.org/3/using/windows.html#multiple-python-versions

### Virtual Environments
- venv Documentation: https://docs.python.org/3/library/venv.html
- Tutorial: https://realpython.com/python-virtual-environments-a-primer/

### vectorbt
- Installation: https://vectorbt.dev/install/
- Quick Start: https://vectorbt.dev/docs/quickstart/

---

## 🎓 Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 INSTALLATION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ⏳ Download Python 3.13.x from python.org
2. ⏳ Install to C:\Python313\ (custom location)
3. ⏳ Verify: C:\Python313\python.exe --version
4. ⏳ Create venv: C:\Python313\python.exe -m venv venv_backtesting
5. ⏳ Activate: .\venv_backtesting\Scripts\Activate.ps1
6. ⏳ Install: pip install vectorbt plotly pyarrow
7. ⏳ Test: python -c "import vectorbt as vbt; print(vbt.__version__)"
8. ⏳ Run: python scripts\backtesting\engine\data_loader.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTIMATED TIME: 15-20 minutes
DIFFICULTY: Easy (follow step-by-step)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

**Created:** October 28, 2025  
**Purpose:** Install Python 3.13 for vectorbt compatibility  
**Status:** Step-by-step guide ready  
**Next:** Download and install Python 3.13, then proceed with venv setup
