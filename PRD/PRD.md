# 🧹 ShelfLife — Product Requirement Document (Reboot)

### *Keep your Plex libraries clean — automatically, safely, and visibly.*

---

## 1. Overview

**Product:** ShelfLife
**Version:** 3.0 (Reboot)
**Status:** Active Development
**Primary Goal:**
A self-hosted tool that automatically maintains Plex libraries using rule-based automation — fully managed through an intuitive **form-based UI**, with **no manual configuration** or `.env` files required.

**Tagline:**

> “Your media cleans itself — safely, visibly, and on your terms.”

---

## 2. Target Users

* Self-hosters running **Plex**, **Radarr**, and/or **Sonarr**
* Users who want automation **with control and visibility**
* People who prefer a **simple UI** instead of scripts or YAML
* Home-server admins (Unraid, TrueNAS, Docker, etc.)

---

## 3. Core Features

### 🧠 3.1 Rule-Based Cleanup Engine

ShelfLife uses a **JSON-based condition and action system** that evaluates each library item and executes defined actions automatically.

**Supported Library Types**

* **Movies:** Evaluated at the movie level.
* **TV Shows:** Evaluated per season, based on the most recently watched episode.

**Condition Fields**

* `movie.lastPlayedDays` — Days since movie was last viewed
* `movie.inCollections` — List of Plex collections
* `movie.hasKeepOverride` — Boolean flag for “Keep” protection
* `season.lastWatchedEpisodeDays` — Days since any episode in the season was watched
* `season.hasKeepOverride` — Boolean flag for show-level Keep protection

**Operators**

* Numeric: `>`, `>=`, `<`, `<=`, `=`, `!=`
* Boolean: `IS_TRUE`, `IS_FALSE`
* Set: `IN`, `NOT_IN`

**Logic**

* Top-level: `AND` or `OR`
* Flat structure (nested groups planned for future)

**Action Types**

* **Immediate:**

  * `ADD_TO_COLLECTION`
  * `SET_TITLE_FORMAT`
* **Delayed (with delayDays):**

  * `DELETE_VIA_RADARR`
  * `DELETE_VIA_SONARR`
  * `DELETE_IN_PLEX`
  * `REMOVE_FROM_COLLECTION`
  * `CLEAR_TITLE_FORMAT`

**Safety**

* Keep collections override all rules (`Keep`, `Favorites`, `Behalten`)
* Watched-again protection: cancels pending deletions
* Dry-run enabled by default
* All actions logged with timestamp and context

---

### 🧱 3.2 Form-Based Rule Builder (v1)

ShelfLife v1 features a fully **form-based rule builder** designed for clarity, safety, and modularity.

**Design Principles**

* Clear stacked syntax: *“If [Field] [Operator] [Value] → [Action]”*
* No technical setup — 100 % UI-driven
* Modular definition of fields, operators, and actions
* Round-trip safe: stored as JSON (`conditions_json`, `actions_json`)
* Visual warnings for unsafe combinations (e.g., delete without delay)
* Dry-run toggle per rule

**Key Features**

* Flat AND/OR logic
* Typed inputs (numeric, boolean, set)
* Separate Immediate and Delayed actions
* Live preview + “Why does this match?” trace
* Inline validation and per-rule dry-run control
* Localized (EN/DE) + light/dark theme support

**Goal:**
Deliver a simple, self-documenting builder that covers all rule scenarios safely, with a flexible backend for future workflow extensions.

---

### 🔗 3.3 Integrations

#### Plex

* Token-based API access via `plexapi`
* Library import and metadata read/write
* Collection management, title editing, lastViewedAt tracking
* Encrypted credentials in SQLite

#### Radarr

* REST API integration (v3)
* Delete movie via `/api/v3/movie/{id}?deleteFiles=true`
* Connection test + safe fallback to Plex deletion

#### Sonarr

* REST API integration (v3)
* Delete series via `/api/v3/series/{id}?deleteFiles=true`
* Series lookup via TVDB ID
* Safety: deletes only if **all seasons qualify**

---

### 🖥️ 3.4 Web Dashboard

Built with **React + Vite + Tailwind CSS**, providing a clean, fast, and modern interface optimized for self-hosted environments and Cursor development.

**Technology Stack**

* **React + Vite** — lightweight SPA, fast builds, and simple integration with FastAPI
* **Tailwind CSS + shadcn/ui** — consistent styling and reusable UI components
* **react-hook-form + zod** — typed, modular, and extensible form validation
* **TanStack Query + Router** — API fetching, caching, and route management
* **i18next** — multi-language support (English / German)
* **Zustand or Jotai** — lightweight state management
* **TanStack Table** — interactive data grids for rules, logs, and candidates
* **lucide-react** — consistent icon system

**Reasons for Choosing Vite Over Next.js**

* ShelfLife is a **pure admin dashboard**, no SSR or SEO required.
* **Vite** offers faster build times, simpler architecture, and better developer experience inside **Cursor**.
* SPA deployment allows **FastAPI** to serve both backend and static assets with a single Docker image.

**Main Sections**

* **Dashboard:** System status + quick actions
* **Rules:** Create, edit, run, enable/disable rules
* **Candidates:** Preview of items marked for deletion
* **Logs:** Full action history with timestamps
* **Settings:** Plex/Radarr/Sonarr connections, language, theme, auth

**Highlights**

* Real-time evaluation and dry-run visibility
* Safe deletion previews
* One-click “Run all rules” execution
* Local-only authentication with optional password protection

---

## 4. Architecture

| Component   | Tech                        | Description                                    |
| ----------- | --------------------------- | ---------------------------------------------- |
| Backend API | **Python + FastAPI**        | Core logic, rules, scheduler, integrations     |
| Frontend    | **React + Vite + Tailwind** | Web dashboard and form-based builder           |
| Database    | **SQLite**                  | Stores libraries, rules, logs, and credentials |
| Scheduler   | **APScheduler**             | Handles scans and delayed deletions            |
| Container   | **Docker**                  | Single container with backend + frontend       |
| Security    | **bcrypt + encryption**     | Password hashing, encrypted token storage      |

**Data Model**

* `SystemSettings`: Plex/Radarr/Sonarr URLs, tokens, language, auth mode
* `Library`: Plex ID, title, type (movie/show)
* `Rule`: Linked to library; contains JSON `conditions_json`, `actions_json`, dry-run flag
* `Candidate`: Item marked for action, with timestamps and reason
* `ActionLog`: Full audit of actions taken

---

## 5. Configuration Flow

1. Launch container → access web dashboard.
2. Enter Plex URL + Token (optional: Radarr/Sonarr).
3. Import Plex libraries.
4. Create rules via the form-based builder.
5. Run a dry-run scan → review results.
6. Enable actions when satisfied.

All credentials are encrypted and stored locally in SQLite.
Settings persist automatically; backup/export available via UI.

---

## 6. Safety & Reliability

* Dry-run by default on all new rules
* Keep-collection override protection
* Watched-again cancellation
* Fallback hierarchy for deletion (Radarr → Plex)
* Comprehensive action logging
* No deletions without explicit delay or confirmation
* Secure local-only access (LAN or password)

---

## 7. API Endpoints (v1)

* `GET /api/health`
* `GET /api/settings` / `POST /api/settings`
* `POST /api/settings/test` (Plex)
* `POST /api/settings/test_radarr`
* `POST /api/settings/test_sonarr`
* `GET /api/libraries` / `POST /api/libraries/import`
* `GET /api/rules` / `POST /api/rules` / `PUT /api/rules/{id}` / `DELETE /api/rules/{id}`
* `POST /api/tasks/scan` / `POST /api/tasks/scan/{rule_id}`
* `GET /api/candidates`
* `GET /api/logs`

---

## 8. Non-Functional Requirements

| Category      | Requirement                                     |
| ------------- | ----------------------------------------------- |
| Deployment    | Single Docker container                         |
| Performance   | Handle 10 000+ media items per scan             |
| Safety        | No file deletions without explicit confirmation |
| UX            | Zero technical knowledge required               |
| Localization  | English + German                                |
| Security      | Encrypted credentials, local-only access        |
| Extensibility | JSON-based rules allow future expansion         |

---

## 9. Roadmap

### ✅ v1 — Core MVP

* Modular form-based rule builder
* Plex/Radarr/Sonarr integrations
* Dry-run engine + preview UI
* Action logging and safe deletion flow

### 🚧 v2 — Enhancements

* Undo/Restore feature
* Enhanced condition fields (file size, rating, addedAt)
* Rule templates
* Nested condition groups

### 🔮 v3 — Future

* Optional visual workflow builder (n8n-style)
* External triggers (Plex webhooks, notifications)
* Multi-user support
* Jellyfin/Emby integration
* Reporting and analytics

---

## 10. Success Metrics

* Number of active users (self-hosted instances)
* Zero reports of unintended deletions
* Avg. setup time < 5 minutes
* High dry-run usage before activation
* Positive user feedback on clarity & transparency
