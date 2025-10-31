# Installation Guide

This guide covers all methods of installing ShelfLife, from Docker (recommended) to manual setup.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Compose (Recommended)](#docker-compose-recommended)
- [Manual Installation](#manual-installation)
- [Post-Installation](#post-installation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### For Docker Installation

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- At least 2GB of available RAM
- Port 8000 available (or configure a different port)

### For Manual Installation

**Backend:**
- Python 3.11 or 3.12 (recommended for best compatibility)
- pip (Python package manager)
- Rust toolchain (optional, needed for some dependencies)

**Frontend:**
- Node.js 18+ and npm

## Docker Compose (Recommended)

This is the easiest and recommended way to run ShelfLife.

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ShelfLife
```

### Step 2: Build and Start

```bash
docker-compose up -d
```

This will:
- Build the frontend and backend
- Start the ShelfLife container
- Make it available at `http://localhost:8000`

![Docker Setup](./screenshots/docker-setup.png)
*Screenshot: Docker Compose build process*

### Step 3: Verify Installation

Open your browser and navigate to `http://localhost:8000`. You should see the ShelfLife login/dashboard page.

### Docker Compose Options

**View logs:**
```bash
docker-compose logs -f shelflife
```

**Stop the container:**
```bash
docker-compose down
```

**Restart the container:**
```bash
docker-compose restart
```

**Rebuild after changes:**
```bash
docker-compose up -d --build
```

## Manual Installation

If you prefer to run ShelfLife without Docker, follow these steps.

### Backend Setup

#### Step 1: Install Python Dependencies

```bash
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Troubleshooting Rust/Cryptography Issues:**

If you encounter errors related to Rust compilation (especially with `cryptography`):

1. **Restart your terminal/PowerShell** - Rust may need to be on PATH
2. Install cryptography with pre-built wheels:
   ```bash
   pip install --only-binary :all: cryptography
   ```
3. See `backend/INSTALL.md` for detailed troubleshooting

#### Step 2: Run the Backend Server

```bash
python main.py
```

The backend will start on `http://localhost:8000` by default.

**Note:** The backend requires SQLite, which is included with Python. The database file will be created automatically in the `data/` directory.

![Backend Startup](./screenshots/backend-startup.png)
*Screenshot: Backend server starting up*

### Frontend Setup

#### Step 1: Install Node.js Dependencies

```bash
cd frontend
npm install
```

#### Step 2: Run the Development Server

```bash
npm run dev
```

The frontend will start on `http://localhost:3000` by default.

**Note:** In development mode, the frontend connects to the backend at `http://localhost:8000`. Make sure both are running.

![Frontend Development](./screenshots/frontend-dev.png)
*Screenshot: Frontend development server*

#### Production Build

To build the frontend for production:

```bash
npm run build
```

The built files will be in the `frontend/dist/` directory. The backend can serve these static files directly in production mode.

## Post-Installation

After installation, you need to configure ShelfLife:

1. **Access the web interface** at `http://localhost:8000` (Docker) or `http://localhost:3000` (manual dev)

2. **Configure Plex connection**:
   - Go to Settings
   - Enter your Plex URL and Token
   - Test the connection

![Settings Page](./screenshots/settings-page.png)
*Screenshot: Settings page for configuring Plex*

3. **Import libraries**:
   - Go to Libraries page
   - Click "Import Libraries"
   - Select libraries to import

4. **Create your first rule**:
   - Go to Rules page
   - Click "Create Rule"
   - Configure conditions and actions

For detailed configuration steps, see the [User Guide](USER_GUIDE.md#configuration).

## Troubleshooting

### Docker Issues

**Container won't start:**
- Check logs: `docker-compose logs shelflife`
- Ensure port 8000 is not in use: `netstat -an | grep 8000`
- Try rebuilding: `docker-compose build --no-cache`

**Build fails:**
- Ensure Docker has enough memory allocated (minimum 2GB recommended)
- Clear Docker cache: `docker system prune -a`
- Check disk space: `df -h`

**Can't access web interface:**
- Verify container is running: `docker-compose ps`
- Check if port is exposed: `docker-compose port shelflife 8000`
- Check firewall settings

### Manual Installation Issues

**Backend won't start:**
- Verify Python version: `python --version` (should be 3.11 or 3.12)
- Check if port 8000 is available
- Review error messages in the terminal

**Frontend won't build:**
- Verify Node.js version: `node --version` (should be 18+)
- Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
- Check for TypeScript errors: `npm run build`

**Dependency installation fails:**
- Upgrade pip: `python -m pip install --upgrade pip`
- Use virtual environment: `python -m venv venv && source venv/bin/activate`
- See `backend/INSTALL.md` for detailed troubleshooting

### Common Errors

**"database is locked":**
- This can occur with SQLite. ShelfLife uses WAL mode to prevent this, but if it persists:
  - Ensure only one instance is running
  - Check for stuck database connections
  - Restart the application

**"Connection refused" (frontend to backend):**
- Ensure backend is running
- Check CORS settings in backend
- Verify API base URL in frontend

**"Rust compilation error":**
- See Rust/Cryptography troubleshooting above
- Consider using Docker instead
- Use Python 3.11 or 3.12 for better wheel support

## Next Steps

Once installed, continue with:

1. [User Guide - Getting Started](USER_GUIDE.md#getting-started)
2. [User Guide - Configuration](USER_GUIDE.md#configuration)
3. [User Guide - Creating Rules](USER_GUIDE.md#creating-rules)

---

*Last updated: 2025*

