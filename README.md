# 🧹 ShelfLife

**Keep your Plex libraries clean — automatically, safely, and visibly.**

ShelfLife is a self-hosted tool that automatically maintains Plex libraries using rule-based automation. It features a fully managed form-based UI with no manual configuration or `.env` files required.

## Features

- **Rule-Based Cleanup Engine**: JSON-based condition and action system
- **Form-Based Rule Builder**: Intuitive UI for creating rules without technical knowledge
- **Plex Integration**: Full library management, collection handling, and metadata editing
- **Radarr & Sonarr Integration**: Seamless deletion via *arr services
- **Safety Features**: Keep collections, dry-run mode, watched-again protection
- **Modern Web Dashboard**: React + Vite + Tailwind CSS with search and filtering
- **Search & Filter**: Powerful search and filtering on candidates page by title, rule, or type
- **Multi-language Support**: English and German
- **Automated Scheduling**: Background scans and delayed action execution

## Quick Start

### Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd ShelfLife
```

2. Build and run:
```bash
docker-compose up -d
```

3. Access the web interface at `http://localhost:8000`

### Manual Setup

#### Backend

**Prerequisites**: Python 3.11 or 3.12 recommended for best compatibility

1. Install Python dependencies:
```bash
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Troubleshooting**: If you encounter Rust compilation errors (especially with `cryptography`):
- **Restart your terminal/PowerShell** - Rust may need to be on PATH
- Or install cryptography separately with pre-built wheels:
  ```bash
  pip install --only-binary :all: cryptography
  ```
- See `backend/INSTALL.md` for more detailed installation instructions

2. Run the server:
```bash
python main.py
```

#### Frontend

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Access the frontend at `http://localhost:3000`

## Configuration Flow

1. Launch container → access web dashboard
2. Enter Plex URL + Token (optional: Radarr/Sonarr)
3. Import Plex libraries
4. Create rules via the form-based builder
5. Run a dry-run scan → review results
6. Enable actions when satisfied

All credentials are encrypted and stored locally in SQLite.

## User Interface

### Candidates Page

The candidates page shows all items scheduled for removal based on your rules. It includes:

- **Search**: Search candidates by item title, show title, or rule name
- **Rule Filter**: Filter candidates by specific rule
- **Type Filter**: Filter by movies or seasons
- **Quick Actions**: Add items to collections directly from the candidates list
- **Detailed Information**: 
  - For seasons: Show title, season title, episode count, last watched episode details
  - For movies: Title, rule, scheduled date, and actions

Use the search and filter tools to quickly find specific candidates or review items from particular rules.

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/settings` / `POST /api/settings` - System settings
- `POST /api/settings/test` - Test Plex connection
- `POST /api/settings/test_radarr` - Test Radarr connection
- `POST /api/settings/test_sonarr` - Test Sonarr connection
- `GET /api/libraries` / `POST /api/libraries/import` - Library management
- `GET /api/rules` / `POST /api/rules` / `PUT /api/rules/{id}` / `DELETE /api/rules/{id}` - Rule management
- `POST /api/tasks/scan` / `POST /api/tasks/scan/{rule_id}` - Trigger scans
- `GET /api/candidates` - View candidates for deletion
- `GET /api/logs` - View action logs

## Safety Features

- **Dry-run by default**: All new rules start in dry-run mode
- **Keep collection override**: Items in "Keep", "Favorites", or "Behalten" collections are protected
- **Watched-again protection**: Cancels pending deletions if item is watched again
- **Delayed deletions**: All deletions require a delay period
- **Comprehensive logging**: Full audit trail of all actions

## Technology Stack

- **Backend**: Python + FastAPI
- **Frontend**: React + Vite + Tailwind CSS
- **Database**: SQLite
- **Scheduler**: APScheduler
- **Integrations**: plexapi, Radarr v3 API, Sonarr v3 API

## License

[Add your license here]

## Troubleshooting

### Backend Installation Issues

If you encounter errors installing dependencies, especially related to Rust/cryptography:

1. Ensure you're using Python 3.11 or 3.12 (better wheel support)
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Restart your terminal/PowerShell after Rust installation
4. See `backend/INSTALL.md` for detailed troubleshooting

### Docker Issues

If the Docker build fails:
- Ensure Docker has enough memory allocated
- Try building without cache: `docker-compose build --no-cache`

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- **[Documentation Index](docs/INDEX.md)** - Start here for documentation overview
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed installation instructions
- **[User Guide](docs/USER_GUIDE.md)** - Complete guide to using ShelfLife
- **[API Documentation](docs/API.md)** - REST API reference
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to ShelfLife
- **[Translations Guide](docs/TRANSLATIONS.md)** - How to add new languages
- **[Architecture](docs/ARCHITECTURE.md)** - Technical architecture and design

## Contributing

Contributions are welcome! Please see the [Contributing Guide](docs/CONTRIBUTING.md) for details.

