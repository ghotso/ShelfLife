# Architecture Documentation

Technical architecture and design decisions for ShelfLife.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Database Schema](#database-schema)
- [Rule Engine](#rule-engine)
- [Integrations](#integrations)
- [Security](#security)
- [Performance Considerations](#performance-considerations)

## Overview

ShelfLife is built as a modern, self-hosted web application with a clear separation between frontend and backend.

### Technology Stack

**Backend:**
- Python 3.11/3.12
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- SQLite (database)
- APScheduler (background tasks)
- plexapi (Plex integration)
- cryptography (credential encryption)

**Frontend:**
- React 18
- TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- TanStack Query (data fetching)
- react-hook-form (form management)
- Zod (validation)
- react-i18next (internationalization)

**Infrastructure:**
- Docker & Docker Compose
- Multi-stage builds
- Static file serving (production)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                        │
│                    (React + TypeScript)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼─────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routers    │  │ Rule Engine  │  │ Scheduler    │     │
│  │  (API Endpoints) │  (Evaluation)  │  (Tasks)      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Integrations Layer                     │    │
│  │  ┌────────┐  ┌────────┐  ┌────────┐               │    │
│  │  │ Plex   │  │ Radarr │  │ Sonarr │               │    │
│  │  └────────┘  └────────┘  └────────┘               │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    SQLite Database                           │
│  (Rules, Libraries, Candidates, Logs, Settings)             │
└─────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Application Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── app/
│   ├── database.py         # Database connection and migration
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas (API validation)
│   ├── security.py         # Encryption utilities
│   ├── rule_engine.py      # Rule evaluation logic
│   ├── scheduler.py        # Background task scheduling
│   ├── routers/            # API route handlers
│   │   ├── rules.py
│   │   ├── candidates.py
│   │   ├── libraries.py
│   │   ├── tasks.py
│   │   ├── settings.py
│   │   └── logs.py
│   └── integrations/       # External service integrations
│       ├── plex.py
│       ├── radarr.py
│       └── sonarr.py
```

### Request Flow

1. **Client Request** → FastAPI router
2. **Validation** → Pydantic schema validation
3. **Business Logic** → Rule engine, integrations, etc.
4. **Database** → SQLAlchemy ORM operations
5. **Response** → JSON response to client

### Key Components

#### Rule Engine (`rule_engine.py`)

The rule engine evaluates conditions against media items:

```python
class RuleEngine:
    def evaluate_conditions(self, conditions, logic, item_data):
        # Evaluate all conditions
        # Combine with AND/OR logic
        # Return True/False
```

**Evaluation Process:**
1. Parse conditions from JSON
2. Extract item data (from Plex)
3. Evaluate each condition
4. Combine results with AND/OR logic
5. Return match result

#### Scheduler (`scheduler.py`)

Handles background task execution:

- Scheduled rule scans
- Delayed action execution
- Cleanup tasks

Uses APScheduler for cron-like scheduling.

#### Database Models (`models.py`)

SQLAlchemy models for:
- `Rule` - Rule definitions
- `Library` - Plex libraries
- `Candidate` - Items scheduled for action
- `Log` - Action history
- `Settings` - System configuration

## Frontend Architecture

### Application Structure

```
frontend/
├── src/
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   ├── components/         # Reusable components
│   │   ├── Layout.tsx
│   │   ├── RuleBuilder.tsx
│   │   └── ConfirmDialog.tsx
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Rules.tsx
│   │   ├── Candidates.tsx
│   │   ├── Logs.tsx
│   │   └── Settings.tsx
│   ├── lib/
│   │   ├── api.ts          # API client
│   │   └── utils.ts        # Utility functions
│   └── i18n/               # Internationalization
│       ├── index.ts
│       └── locales/
```

### State Management

**TanStack Query:**
- Server state management
- Caching and refetching
- Optimistic updates

**React Hook Form:**
- Form state management
- Validation (with Zod)
- Field arrays

**Local State (useState):**
- UI state (modals, filters, etc.)
- Component-specific state

### Data Flow

```
User Action
    ↓
Component Event Handler
    ↓
TanStack Query Mutation/Query
    ↓
API Client (lib/api.ts)
    ↓
HTTP Request to Backend
    ↓
Backend Processing
    ↓
Response
    ↓
TanStack Query Cache Update
    ↓
Component Re-render
```

## Database Schema

### Tables

#### Rules

```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    library_id INTEGER,
    name TEXT NOT NULL,
    enabled BOOLEAN,
    dry_run BOOLEAN,
    logic TEXT,  -- 'AND' or 'OR'
    conditions_json TEXT,  -- JSON array
    actions_json TEXT,     -- JSON object
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (library_id) REFERENCES libraries(id)
);
```

#### Libraries

```sql
CREATE TABLE libraries (
    id INTEGER PRIMARY KEY,
    plex_id TEXT,
    title TEXT,
    library_type TEXT  -- 'movie' or 'show'
);
```

#### Candidates

```sql
CREATE TABLE candidates (
    id INTEGER PRIMARY KEY,
    rule_id INTEGER,
    plex_key TEXT,
    item_type TEXT,  -- 'movie' or 'season'
    item_title TEXT,
    season_number INTEGER,
    show_title TEXT,
    episode_count INTEGER,
    last_watched_episode_title TEXT,
    last_watched_episode_number INTEGER,
    last_watched_episode_date TIMESTAMP,
    reason TEXT,
    actions_json TEXT,  -- JSON array
    scheduled_date TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    cancelled BOOLEAN,
    FOREIGN KEY (rule_id) REFERENCES rules(id)
);
```

#### Logs

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    rule_id INTEGER,
    item_key TEXT,
    item_title TEXT,
    item_type TEXT,
    action_type TEXT,
    status TEXT,
    message TEXT,
    created_at TIMESTAMP
);
```

#### Settings

```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY,
    plex_url TEXT,
    plex_token_encrypted TEXT,
    radarr_url TEXT,
    radarr_api_key_encrypted TEXT,
    sonarr_url TEXT,
    sonarr_api_key_encrypted TEXT,
    language TEXT
);
```

### Database Features

- **WAL Mode**: Enabled for better concurrency
- **Migration System**: Automatic schema migration on startup
- **Indexes**: On foreign keys for performance

## Rule Engine

### Condition Evaluation

Conditions are evaluated using a flexible system:

```python
def evaluate_condition(condition, item_data):
    field = condition.field  # e.g., "movie.lastPlayedDays"
    operator = condition.operator  # e.g., ">="
    value = condition.value  # e.g., 90
    
    # Strip prefix (movie. or season.)
    field_name = field.split('.')[-1]
    field_value = item_data.get(field_name)
    
    # Apply operator
    if operator == ">=":
        return field_value >= value
    # ... other operators
```

### Supported Fields

**Movies:**
- `lastPlayedDays` - Days since last played
- `inCollections` - List of collection names
- `hasKeepOverride` - Boolean keep flag

**Seasons:**
- `lastWatchedEpisodeDays` - Days since last watched episode
- `inCollections` - List of collection names (show + season level)
- `hasKeepOverride` - Boolean keep flag

### Logic Combination

- **AND**: All conditions must match
- **OR**: Any condition must match

### Action Execution

**Immediate Actions:**
- Executed immediately when rule matches
- No delay, no candidate creation

**Delayed Actions:**
- Creates a candidate
- Scheduled for future execution
- Can be cancelled if item is watched again

## Integrations

### Plex Integration

**Library:** `plexapi`

**Features:**
- Library scanning
- Metadata retrieval
- Collection management
- Item deletion
- Watch history caching

**Key Methods:**
```python
get_libraries()      # List all libraries
get_movies()         # Get movies from library
get_shows()          # Get shows from library
get_seasons()        # Get seasons from show
get_movie_data()     # Extract movie data
get_season_data()    # Extract season data
add_to_collection()  # Add item to collection
remove_from_collection()  # Remove from collection
delete_item()        # Delete item
```

### Radarr Integration

**API:** Radarr v3 REST API

**Features:**
- Movie lookup
- Movie deletion
- Series deletion

### Sonarr Integration

**API:** Sonarr v3 REST API

**Features:**
- Series lookup
- Series deletion

## Security

### Credential Storage

All API keys and tokens are encrypted before storage:

```python
def encrypt_token(token: str) -> str:
    # Uses Fernet symmetric encryption
    # Key derived from system or user-provided
```

### Encryption Details

- **Algorithm**: Fernet (symmetric encryption)
- **Key Management**: Stored securely or derived
- **Decryption**: On-the-fly when needed

### Security Considerations

- No authentication yet (planned)
- Suitable for local/trusted network use
- Credentials never logged
- HTTPS recommended for remote access

## Performance Considerations

### Caching

**Plex Watch History Cache:**
- Caches watch history for faster lookups
- 5-minute TTL
- Max 50,000 entries

**Database:**
- SQLite WAL mode for better concurrency
- Indexes on foreign keys
- Connection pooling

### Optimization Strategies

1. **Batch Operations**: Process items in batches
2. **Lazy Loading**: Load data only when needed
3. **Database Indexing**: Index frequently queried fields
4. **Connection Reuse**: Reuse Plex connections
5. **Background Processing**: Use background tasks for scans

### Scalability

Current design supports:
- Libraries with thousands of items
- Hundreds of rules
- Thousands of candidates

For larger scale:
- Consider PostgreSQL instead of SQLite
- Add Redis for caching
- Implement job queue (Celery, etc.)

## Future Improvements

- [ ] Authentication and authorization
- [ ] PostgreSQL support
- [ ] Redis caching
- [ ] WebSocket for real-time updates
- [ ] GraphQL API option
- [ ] Unit and integration tests
- [ ] CI/CD pipeline
- [ ] Performance monitoring

---

*Documentation version: 1.0 | Last updated: 02.11.2025*

