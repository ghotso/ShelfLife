# Backend Installation Guide

## Prerequisites

- Python 3.11 or 3.12 (recommended for better wheel compatibility)
- pip (upgraded to latest version)

## Installation

### Option 1: Install with pre-built wheels (Recommended)

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Option 2: If Rust is required (for cryptography)

If you encounter Rust compilation errors:

1. **Restart your terminal/PowerShell** to ensure Rust is on PATH
2. Or manually add Rust to PATH:
   ```powershell
   $env:Path += ";$env:USERPROFILE\.cargo\bin"
   ```
3. Then install:
   ```bash
   pip install -r requirements.txt
   ```

### Option 3: Use Python 3.11 (if wheels aren't available for your Python version)

If you're using Python 3.14 or newer, some packages may not have pre-built wheels yet. Consider using Python 3.11 or 3.12 for better compatibility.

```bash
# Using pyenv or similar tool
pyenv install 3.11.7
pyenv local 3.11.7

# Then install dependencies
pip install -r requirements.txt
```

## Common Issues

### Error: "Cargo not found"

**Solution**: Restart your terminal/PowerShell session. Rust should be on PATH after installation.

### Error: "Could not find platform independent libraries"

**Solution**: This usually means Python isn't properly configured. Ensure you're using a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### Error: "metadata-generation-failed" with cryptography

**Solution**: Try installing cryptography separately with pre-built wheels:
```bash
pip install --upgrade pip
pip install --only-binary :all: cryptography
pip install -r requirements.txt
```

