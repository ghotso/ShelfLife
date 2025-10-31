# API Documentation

Complete reference for ShelfLife's REST API.

## Base URL

- **Production**: `http://your-server:8000/api`
- **Development**: `http://localhost:8000/api`

All endpoints return JSON unless otherwise specified.

## Authentication

Currently, ShelfLife does not require authentication. This is suitable for local/trusted network use. Authentication support is planned for future versions.

## Response Format

### Success Response

```json
{
  "id": 1,
  "name": "Example",
  ...
}
```

### Error Response

```json
{
  "detail": "Error message here"
}
```

HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Endpoints

### Health Check

#### GET `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "version": "3.0.0"
}
```

---

### Settings

#### GET `/settings`

Get current system settings.

**Response:**
```json
{
  "plex_url": "http://192.168.1.100:32400",
  "plex_token": "encrypted_token_here",
  "radarr_url": "http://192.168.1.100:7878",
  "radarr_api_key": "encrypted_key_here",
  "sonarr_url": "http://192.168.1.100:8989",
  "sonarr_api_key": "encrypted_key_here",
  "language": "en"
}
```

#### POST `/settings`

Update system settings.

**Request Body:**
```json
{
  "plex_url": "http://192.168.1.100:32400",
  "plex_token": "your_plex_token",
  "radarr_url": "http://192.168.1.100:7878",
  "radarr_api_key": "your_radarr_api_key",
  "sonarr_url": "http://192.168.1.100:8989",
  "sonarr_api_key": "your_sonarr_api_key",
  "language": "en"
}
```

**Response:**
```json
{
  "plex_url": "http://192.168.1.100:32400",
  ...
}
```

#### POST `/settings/test`

Test Plex connection.

**Request Body:**
```json
{
  "url": "http://192.168.1.100:32400",
  "token_or_key": "your_plex_token",
  "service_type": "plex"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

#### POST `/settings/test_radarr`

Test Radarr connection.

**Request Body:**
```json
{
  "url": "http://192.168.1.100:7878",
  "token_or_key": "your_radarr_api_key",
  "service_type": "radarr"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

#### POST `/settings/test_sonarr`

Test Sonarr connection.

**Request Body:**
```json
{
  "url": "http://192.168.1.100:8989",
  "token_or_key": "your_sonarr_api_key",
  "service_type": "sonarr"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

---

### Libraries

#### GET `/libraries`

Get all imported libraries.

**Response:**
```json
[
  {
    "id": 1,
    "plex_id": "1",
    "title": "Movies",
    "library_type": "movie"
  },
  {
    "id": 2,
    "plex_id": "2",
    "title": "TV Shows",
    "library_type": "show"
  }
]
```

#### POST `/libraries/import`

Import libraries from Plex.

**Response:**
```json
{
  "imported": 2,
  "libraries": [
    {
      "id": 1,
      "plex_id": "1",
      "title": "Movies",
      "library_type": "movie"
    }
  ]
}
```

---

### Rules

#### GET `/rules`

Get all rules.

**Response:**
```json
[
  {
    "id": 1,
    "library_id": 1,
    "name": "Delete Old Movies",
    "enabled": true,
    "dry_run": true,
    "logic": "AND",
    "conditions": [
      {
        "field": "movie.lastPlayedDays",
        "operator": ">=",
        "value": 90
      }
    ],
    "immediate_actions": [],
    "delayed_actions": [
      {
        "type": "DELETE_IN_PLEX",
        "delay_days": 30
      }
    ],
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00",
    "library": {
      "id": 1,
      "title": "Movies"
    }
  }
]
```

#### POST `/rules`

Create a new rule.

**Request Body:**
```json
{
  "library_id": 1,
  "name": "Delete Old Movies",
  "enabled": true,
  "dry_run": true,
  "logic": "AND",
  "conditions": [
    {
      "field": "movie.lastPlayedDays",
      "operator": ">=",
      "value": 90
    }
  ],
  "immediate_actions": [],
  "delayed_actions": [
    {
      "type": "DELETE_IN_PLEX",
      "delay_days": 30
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Delete Old Movies",
  ...
}
```

#### PUT `/rules/{id}`

Update an existing rule.

**Request Body:** (same as POST `/rules`)

**Response:**
```json
{
  "id": 1,
  "name": "Updated Rule Name",
  ...
}
```

#### DELETE `/rules/{id}`

Delete a rule.

**Response:**
```json
{
  "success": true,
  "message": "Rule deleted"
}
```

---

### Tasks

#### POST `/tasks/scan`

Scan all enabled rules.

**Response:**
```json
{
  "status": "started",
  "message": "Scan started for all rules"
}
```

#### POST `/tasks/scan/{rule_id}`

Scan a specific rule.

**Response:**
```json
{
  "status": "started",
  "message": "Scan started for rule 1"
}
```

---

### Candidates

#### GET `/candidates`

Get all candidates (items scheduled for action).

**Response:**
```json
[
  {
    "id": 1,
    "rule_id": 1,
    "plex_key": "/library/metadata/12345",
    "item_type": "movie",
    "item_title": "Example Movie",
    "season_number": null,
    "show_title": null,
    "episode_count": null,
    "last_watched_episode_title": null,
    "last_watched_episode_number": null,
    "last_watched_episode_date": null,
    "reason": "Matched rule 'Delete Old Movies'",
    "actions": [
      {
        "type": "DELETE_IN_PLEX",
        "delay_days": 30
      }
    ],
    "scheduled_date": "2025-02-01T00:00:00",
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00",
    "cancelled": false,
    "rule": {
      "id": 1,
      "name": "Delete Old Movies"
    }
  }
]
```

**Season Candidate Example:**
```json
{
  "id": 2,
  "rule_id": 1,
  "plex_key": "/library/metadata/67890",
  "item_type": "season",
  "item_title": "Season 1",
  "season_number": 1,
  "show_title": "Example Show",
  "episode_count": 10,
  "last_watched_episode_title": "Episode Title",
  "last_watched_episode_number": 5,
  "last_watched_episode_date": "2024-12-01T00:00:00",
  ...
}
```

#### POST `/candidates/{candidate_id}/add-to-collection`

Add a candidate to a collection (and remove from candidates).

**Query Parameters:**
- `collection_name` (optional): Collection name (defaults to "Keep")

**Response:**
```json
{
  "success": true,
  "message": "Added to collection 'Keep' and triggered rule rescan",
  "collection_name": "Keep"
}
```

---

### Logs

#### GET `/logs`

Get action logs.

**Query Parameters:**
- `limit` (optional): Maximum number of logs to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "rule_id": 1,
    "item_key": "/library/metadata/12345",
    "item_title": "Example Movie",
    "item_type": "movie",
    "action_type": "DELETE_IN_PLEX",
    "status": "success",
    "message": "Deleted from Plex",
    "created_at": "2025-01-01T00:00:00"
  }
]
```

---

## Data Models

### Rule

```typescript
interface Rule {
  id: number
  library_id: number
  name: string
  enabled: boolean
  dry_run: boolean
  logic: "AND" | "OR"
  conditions: Condition[]
  immediate_actions: Action[]
  delayed_actions: Action[]
  created_at: string
  updated_at: string
  library?: Library
}
```

### Condition

```typescript
interface Condition {
  field: string  // e.g., "movie.lastPlayedDays", "season.inCollections"
  operator: string  // e.g., ">=", "IN", "NOT_IN"
  value: string | number  // Depends on operator type
}
```

### Action

```typescript
interface Action {
  type: string  // e.g., "DELETE_IN_PLEX", "ADD_TO_COLLECTION"
  delay_days?: number  // For delayed actions
  collection_name?: string  // For collection actions
  title_format?: string  // For title format actions
}
```

### Candidate

```typescript
interface Candidate {
  id: number
  rule_id: number
  plex_key: string
  item_type: "movie" | "season"
  item_title: string
  season_number?: number
  show_title?: string
  episode_count?: number
  last_watched_episode_title?: string
  last_watched_episode_number?: number
  last_watched_episode_date?: string
  reason: string
  actions: Action[]
  scheduled_date: string
  created_at: string
  updated_at: string
  cancelled: boolean
  rule?: {
    id: number
    name: string
  }
}
```

### Library

```typescript
interface Library {
  id: number
  plex_id: string
  title: string
  library_type: "movie" | "show"
}
```

---

## Error Handling

All errors return a JSON response with a `detail` field:

```json
{
  "detail": "Error message here"
}
```

Common error scenarios:

- **400 Bad Request**: Invalid request data (e.g., missing required fields)
- **404 Not Found**: Resource doesn't exist (e.g., rule ID not found)
- **500 Internal Server Error**: Server error (e.g., Plex connection failed)

---

## Rate Limiting

Currently, ShelfLife does not implement rate limiting. However, it's recommended to:
- Avoid rapid successive API calls
- Use reasonable polling intervals
- Consider implementing rate limiting in production deployments

---

## Versioning

API versioning is not yet implemented. All endpoints are currently under `/api` without version prefixes. Future versions may introduce versioning (e.g., `/api/v1`).

---

*Last updated: 31st October 2025*