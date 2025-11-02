# User Guide

Complete guide to using ShelfLife for automated Plex library management.

## Table of Contents

- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Creating Rules](#creating-rules)
- [Managing Candidates](#managing-candidates)
- [Understanding Actions](#understanding-actions)
- [Safety Features](#safety-features)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Getting Started

After installation, your first steps with ShelfLife:

### 1. Initial Setup

![Dashboard Home](./screenshots/dashboard-home.png)
*Screenshot: Dashboard home page*

1. **Access the dashboard** at `http://localhost:8000`
2. **Navigate to Settings** from the sidebar
3. **Configure Plex connection** (see Configuration section below)
4. **Import your libraries** (see Configuration section below)

### 2. Understanding the Interface

ShelfLife has five main pages:

- **Dashboard**: Overview and statistics
- **Rules**: Create and manage automation rules
- **Candidates**: Review items scheduled for deletion
- **Logs**: View action history
- **Settings**: Configure Plex, Radarr, and Sonarr connections

## Configuration

### Plex Configuration

![Settings - Plex](./screenshots/settings-plex.png)
*Screenshot: Plex configuration in Settings*

**Step 1: Get your Plex Token**

1. Go to your Plex Media Server
2. Navigate to Settings → Network
3. Enable "Show Advanced" if needed
4. Or use the [Plex Token Finder](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) method

**Step 2: Enter Plex Details**

1. Go to Settings in ShelfLife
2. Enter your Plex server URL (e.g., `http://192.168.1.100:32400`)
3. Enter your Plex token
4. Click "Test Connection"
5. If successful, the connection is saved automatically

**Step 3: Import Libraries**

1. Go to Libraries page (or Settings → Libraries)
2. Click "Import Libraries"
3. Select the libraries you want ShelfLife to manage
4. Libraries will be imported and available for rule creation

![Import Libraries](./screenshots/import-libraries.png)
*Screenshot: Importing Plex libraries*

### Radarr Configuration (Optional)

![Settings - Radarr](./screenshots/settings-radarr.png)
*Screenshot: Radarr configuration*

1. Go to Settings in ShelfLife
2. Enter your Radarr URL (e.g., `http://192.168.1.100:7878`)
3. Enter your Radarr API key (found in Radarr → Settings → General → API Key)
4. Click "Test Connection"
5. If successful, Radarr integration is enabled

**Note:** Radarr integration allows ShelfLife to delete movies through Radarr instead of directly in Plex, which can help maintain your Radarr library state.

### Sonarr Configuration (Optional)

![Settings - Sonarr](./screenshots/settings-sonarr.png)
*Screenshot: Sonarr configuration*

1. Go to Settings in ShelfLife
2. Enter your Sonarr URL (e.g., `http://192.168.1.100:8989`)
3. Enter your Sonarr API key (found in Sonarr → Settings → General → API Key)
4. Click "Test Connection"
5. If successful, Sonarr integration is enabled

**Note:** Sonarr integration allows ShelfLife to delete TV shows through Sonarr instead of directly in Plex.

### Language Settings

ShelfLife supports multiple languages. To change:

1. Go to Settings
2. Use the Language dropdown
3. Select your preferred language (English, German, or others)
4. The interface will update immediately

## Creating Rules

Rules are the heart of ShelfLife. They define what actions to take on your media.

### Rule Components

A rule consists of:

1. **Conditions**: When the rule should apply
2. **Logic**: How conditions are combined (AND/OR)
3. **Actions**: What to do when conditions match
4. **Settings**: Enable/disable, dry-run mode

![Rule Builder](./screenshots/rule-builder.png)
*Screenshot: Rule builder modal*

### Basic Rule Example

Let's create a rule to delete movies that haven't been watched in 90 days:

**Step 1: Open Rule Builder**

1. Go to Rules page
2. Click "Create Rule"
3. Enter a name: "Delete Old Movies"

**Step 2: Select Library**

1. Choose your Movies library from the dropdown
2. This rule will only apply to items in this library

**Step 3: Add Condition**

1. Click "+ Add Condition"
2. Field: Select "Days since last played (Movie)"
3. Operator: Select "Greater than or equal"
4. Value: Enter `90`

**Step 4: Add Action**

1. In "Delayed Actions" section, click "+ Add Action"
2. Type: Select "Delete in Plex"
3. Delay Days: Enter `30` (30-day delay before deletion)

**Step 5: Configure Settings**

1. **Enabled**: Check this to activate the rule
2. **Dry Run**: Leave checked to preview actions without executing

**Step 6: Save and Test**

1. Click "Create Rule"
2. Go back to Rules page
3. Click the "Play" button to scan the rule
4. Check the Candidates page to see results

![Rule List](./screenshots/rules-list.png)
*Screenshot: Rules list with actions*

### Available Conditions

#### Movie Conditions

- **Days since last played**: Number of days since the movie was last watched
- **In collections**: Whether the movie is in specific collections
- **Has Keep override**: Whether the movie is protected by Keep collections

#### Season Conditions

- **Days since last watched episode**: Number of days since any episode in the season was watched
- **In collections**: Whether the season (or its show) is in specific collections
- **Has Keep override**: Whether the season is protected by Keep collections

### Operators

**Numeric operators** (for days):
- `>` Greater than
- `>=` Greater than or equal
- `<` Less than
- `<=` Less than or equal
- `=` Equal
- `!=` Not equal

**Set operators** (for collections):
- `IN` Item is in the collection
- `NOT_IN` Item is not in the collection

**Boolean operators**:
- `IS_TRUE` Condition is true
- `IS_FALSE` Condition is false

### Combining Conditions

You can combine multiple conditions using AND/OR logic:

- **AND**: All conditions must match
- **OR**: Any condition must match

**Example - Multiple Conditions:**

"Delete movies that haven't been watched in 90 days AND are not in Keep collection"

1. Condition 1: Days since last played >= 90
2. Condition 2: In collections NOT_IN Keep
3. Logic: AND

## Managing Candidates

Candidates are items that match your rules and are scheduled for action.

![Candidates Page](./screenshots/candidates-page.png)
*Screenshot: Candidates page with search and filters*

### Viewing Candidates

1. Go to Candidates page
2. You'll see all items scheduled for deletion or other actions
3. Each candidate shows:
   - Item title and type
   - Rule that matched
   - Scheduled action date
   - Actions to be performed

### Search and Filter

Use the powerful search and filter tools:

**Search:**
- Search by item title, show title, or rule name
- Real-time filtering as you type

**Rule Filter:**
- Filter candidates by specific rule
- Useful for reviewing results from a single rule

**Type Filter:**
- Filter by Movies or Seasons
- Switch between library types

![Candidates Filters](./screenshots/candidates-filters.png)
*Screenshot: Using search and filters*

### Candidate Information

For **Movies**, you'll see:
- Movie title
- Rule that matched
- Scheduled date
- Actions to be performed

For **Seasons**, you'll see:
- Show title and season title
- Episode count
- Last watched episode details (if any)
- "Never watched" indicator if applicable
- Rule that matched
- Scheduled date
- Actions to be performed

### Managing Candidates

**Add to Collection:**
- Click "Add to Collection" on any candidate
- Enter a collection name (defaults to "Keep")
- The item will be added to the collection and removed from candidates
- The rule will be automatically rescanned

**Note:** For season candidates, adding to collection adds the entire show to the collection (not just the season).

## Understanding Actions

ShelfLife supports two types of actions:

### Immediate Actions

Executed immediately when a rule matches:

**Add to Collection:**
- Adds the item to a specified Plex collection
- Useful for organizing or marking items
- Example: Add all watched movies to "Completed" collection

**Set Title Format:**
- Modifies the item's title in Plex
- Useful for adding prefixes or suffixes
- Example: Add "[Archived]" prefix to old items

### Delayed Actions

Scheduled for future execution (after delay period):

**Delete via Radarr:**
- Deletes the movie through Radarr API
- Removes from both Radarr and Plex
- Requires Radarr configuration

**Delete via Sonarr:**
- Deletes the TV show through Sonarr API
- Removes from both Sonarr and Plex
- Requires Sonarr configuration

**Delete in Plex:**
- Deletes the item directly from Plex
- Works for both movies and seasons
- Doesn't require Radarr/Sonarr

**Remove from Collection:**
- Removes the item from a specified collection
- Useful for cleanup operations

**Clear Title Format:**
- Removes any custom title formatting
- Restores original title

### Action Delays

Delayed actions have a customizable delay period:

- **Delay Days**: Number of days to wait before executing
- Items become "candidates" during this period
- You can still cancel by adding to Keep collection

**Example:**
- Rule matches on Day 1
- Action has 30-day delay
- Scheduled date: Day 31
- If watched again before Day 31, deletion is cancelled

## Safety Features

ShelfLife includes multiple safety mechanisms:

### Keep Collections

Items in these collections are **never** deleted:
- `Keep`
- `Favorites`
- `Behalten` (German)

**How it works:**
1. Add items to a Keep collection manually or via rule
2. Even if a rule matches, items in Keep collections are skipped
3. Works for both show-level and season-level collections

![Keep Collection](./screenshots/keep-collection.png)
*Screenshot: Adding candidate to Keep collection*

### Dry Run Mode

**Enabled by default** for all new rules:

- Rules in dry-run mode scan and show candidates
- But **no actions are executed**
- Perfect for testing rules safely

**To enable actual actions:**
1. Edit the rule
2. Uncheck "Dry Run (preview only)"
3. Save the rule

**Always test with dry-run first!**

### Watched-Again Protection

If an item is watched again after being scheduled for deletion:
- The scheduled deletion is automatically cancelled
- The candidate is removed
- You'll need to manually rescan to re-trigger rules

### Comprehensive Logging

All actions are logged with:
- Timestamp
- Rule name
- Item details
- Action performed
- Result (success/failure)

View logs in the Logs page:

![Logs Page](./screenshots/logs-page.png)
*Screenshot: Action logs*

### Delayed Deletion

All deletion actions have a mandatory delay:
- Prevents accidental immediate deletion
- Gives you time to review candidates
- Allows you to add items to Keep if needed

## Advanced Usage

### Multiple Rules

You can create multiple rules for different scenarios:

**Example Setup:**
- Rule 1: Delete movies not watched in 90 days
- Rule 2: Delete seasons not watched in 60 days
- Rule 3: Archive old content (add to collection, don't delete)

Rules work independently - each item is evaluated against all enabled rules.

### Collection-Based Organization

Use collections strategically:

**Keep Collections:**
- Protect important content
- Automatically skip deletion

**Archive Collections:**
- Mark items for review
- Use with immediate actions to organize

**Temporary Collections:**
- Mark items for specific handling
- Use in rule conditions for targeted rules

### Scheduling Scans

ShelfLife can automatically scan rules on a schedule:

- Configure scan frequency in Settings (if available)
- Or use external schedulers (cron, task scheduler)
- Regular scans keep your candidates up to date

### Rule Logic Strategies

**AND Logic:**
- Use when you want strict matching
- Example: "Old AND not in Keep" (both must be true)

**OR Logic:**
- Use when you want flexible matching
- Example: "Not watched OR in Archive" (either can be true)

## Troubleshooting

### Rule Not Matching Items

**Check:**
1. Is the rule enabled?
2. Is it in dry-run mode (check candidates, not logs)?
3. Do the conditions match your items?
4. Are items in Keep collections (they're automatically skipped)?

**Debug:**
1. Enable dry-run mode
2. Scan the rule
3. Check Candidates page
4. Review item details to see why they matched (or didn't)

### Candidates Not Appearing

**Possible reasons:**
1. Rule is in dry-run mode (check Candidates, not Logs)
2. Items are in Keep collections
3. Conditions don't match any items
4. Rule is disabled

**Solution:**
1. Verify rule settings
2. Check item details in Plex
3. Test with a simpler rule first

### Actions Not Executing

**If in dry-run mode:**
- This is expected! Actions only execute when dry-run is disabled

**If not in dry-run mode:**
1. Check Logs page for errors
2. Verify service connections (Plex, Radarr, Sonarr)
3. Check API permissions
4. Review error messages in logs

### Connection Issues

**Plex connection fails:**
1. Verify URL and token
2. Check if Plex server is accessible
3. Ensure token has proper permissions
4. Try testing connection multiple times

**Radarr/Sonarr connection fails:**
1. Verify URL and API key
2. Check API version compatibility (v3 required)
3. Ensure API is enabled in Radarr/Sonarr settings
4. Check firewall/network settings

### Performance Issues

**Slow scans:**
- Large libraries take time to scan
- First scan builds cache (subsequent scans are faster)
- Consider scanning individual rules instead of all rules

**High memory usage:**
- SQLite WAL mode is enabled for performance
- Database size grows with logs
- Consider archiving old logs if needed

### Database Issues

**"Database is locked":**
- Ensure only one instance is running
- Restart ShelfLife
- Check for stuck processes

**Data loss:**
- Regular backups recommended
- Database is in `data/shelflife.db`
- Back up this file regularly

## Tips and Best Practices

1. **Start with dry-run**: Always test rules in dry-run mode first
2. **Use Keep collections**: Protect important content proactively
3. **Set reasonable delays**: Give yourself time to review candidates
4. **Review logs regularly**: Stay informed about what's happening
5. **Test with simple rules**: Start simple, add complexity gradually
6. **Backup your database**: Regular backups prevent data loss
7. **Monitor candidates**: Review candidates page regularly
8. **Use search and filters**: Quickly find specific candidates

---

*Documentation version: 1.0 | Last updated: 02.11.2025*

