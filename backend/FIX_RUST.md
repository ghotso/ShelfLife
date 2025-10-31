# Fix Rust Installation for Python 3.14

Since Python 3.14 doesn't have pre-built wheels for many packages, you need Rust to compile them.

## Option 1: Install Rust Properly (Recommended)

1. Download and install Rust from: https://rustup.rs/
   - Or run: `winget install Rustlang.Rustup`

2. After installation, **restart PowerShell completely**

3. Verify Rust is installed:
   ```powershell
   rustc --version
   cargo --version
   ```

4. Then install dependencies:
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

## Option 2: Use Docker (Easiest - No Rust needed)

```bash
docker-compose up -d
```

Docker will handle all dependencies automatically.

## Option 3: Install Python 3.11 or 3.12

1. Download Python 3.11 or 3.12 from python.org
2. Install it
3. Create a new virtual environment:
   ```powershell
   py -3.11 -m venv .venv311
   .venv311\Scripts\activate
   pip install -r requirements.txt
   ```

## Quick Fix: Add Rust to PATH Manually

If Rust is installed but not on PATH:

```powershell
# Add to PATH for current session
$env:Path += ";$env:USERPROFILE\.cargo\bin"

# Verify
cargo --version

# If that works, add permanently:
[Environment]::SetEnvironmentVariable("Path", $env:Path, "User")
```

