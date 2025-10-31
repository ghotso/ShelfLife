"""
Rule evaluation and action execution engine
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.integrations.plex import PlexIntegration


class RuleEngine:
    def __init__(self, plex: PlexIntegration, radarr=None, sonarr=None):
        self.plex = plex
        self.radarr = radarr
        self.sonarr = sonarr
    
    def evaluate_condition(self, condition: Dict[str, Any], item_data: Dict[str, Any]) -> bool:
        """Evaluate a single condition against item data"""
        field = condition.get("field", "")
        operator = condition.get("operator", "")
        value = condition.get("value")
        
        # Strip prefix from field name (e.g., "movie.lastPlayedDays" -> "lastPlayedDays")
        # Item data keys don't have the prefix
        field_key = field
        if "." in field:
            field_key = field.split(".", 1)[1]  # Take everything after the first dot
        
        # Get field value from item data
        field_value = item_data.get(field_key)
        
        # Debug logging
        print(f"  Evaluating condition: {field} {operator} {value} (looked up as '{field_key}', field_value={field_value})")
        
        # Numeric operators
        if operator in [">", ">=", "<", "<=", "=", "!="]:
            try:
                # Handle None values - for days since last played, None means never played
                # We'll treat None as a very large number (999999 days) for ">" comparisons
                if field_value is None:
                    # For "days since last played", None means never played, so it's > any number of days
                    if "lastPlayedDays" in field_key or "lastWatchedEpisodeDays" in field_key:
                        if operator in [">", ">="]:
                            # Never played is considered > any number of days
                            field_num = 999999
                        else:
                            # For <, =, !=, treat as 0 or False
                            field_num = 0
                    else:
                        # For other numeric fields, None means no value
                        return False
                else:
                    field_num = float(field_value)
                
                value_num = float(value) if value is not None else 0
                
                if operator == ">":
                    result = field_num > value_num
                    print(f"  Numeric comparison: {field_num} > {value_num} = {result}")
                    return result
                elif operator == ">=":
                    return field_num >= value_num
                elif operator == "<":
                    return field_num < value_num
                elif operator == "<=":
                    return field_num <= value_num
                elif operator == "=":
                    return field_num == value_num
                elif operator == "!=":
                    return field_num != value_num
            except (ValueError, TypeError) as e:
                print(f"Error evaluating numeric condition: {e}, field_value={field_value}, value={value}")
                return False
        
        # Boolean operators
        elif operator == "IS_TRUE":
            return bool(field_value) is True
        elif operator == "IS_FALSE":
            return bool(field_value) is False
        
        # Set operators
        elif operator == "IN":
            if isinstance(field_value, list):
                # Handle empty/null values
                if not value:
                    print(f"  IN operator: value is empty, returning False")
                    return False  # Can't match if value is empty
                if isinstance(value, list):
                    result = any(v in field_value for v in value if v)
                    print(f"  IN operator (list): '{value}' in {field_value} = {result}")
                    return result
                # Ensure value is a string for comparison
                # Normalize collection names for comparison (case-insensitive, strip whitespace)
                value_str = str(value).strip() if value else ""
                # Check if any collection in field_value matches (case-insensitive)
                result = any(value_str.lower() == str(c).strip().lower() for c in field_value if c)
                print(f"  IN operator: '{value_str}' in {field_value} = {result} (case-insensitive comparison)")
                return result
            else:
                print(f"  IN operator: field_value is not a list (type: {type(field_value).__name__}, value: {field_value}), returning False")
            return False
        elif operator == "NOT_IN":
            # If field_value is not a list, we can't evaluate NOT_IN - return False
            if not isinstance(field_value, list):
                print(f"  WARNING: NOT_IN operator requires a list, but field_value is {type(field_value).__name__}: {field_value}")
                return False
            # Handle empty/null values
            if not value:
                return True  # Empty value is considered NOT_IN
            if isinstance(value, list):
                result = not any(v in field_value for v in value if v)
                print(f"  Set NOT_IN comparison (list): '{value}' not in {field_value} = {result}")
                return result
            # Ensure value is a string for comparison
            value_str = str(value).strip() if value else ""
            result = value_str not in field_value
            print(f"  Set NOT_IN comparison: '{value_str}' not in {field_value} = {result}")
            return result
        
        return False
    
    def evaluate_conditions(self, conditions: List[Dict[str, Any]], logic: str, item_data: Dict[str, Any]) -> bool:
        """Evaluate all conditions with AND/OR logic"""
        if not conditions:
            return False
        
        results = [self.evaluate_condition(cond, item_data) for cond in conditions]
        
        if logic.upper() == "OR":
            return any(results)
        else:  # AND (default)
            return all(results)
    
    def execute_immediate_actions(self, actions: List[Dict[str, Any]], item_key: str, item_type: str, dry_run: bool, delayed_actions: List[Dict[str, Any]] = None, item_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute immediate actions
        
        Args:
            actions: List of immediate actions to execute
            item_key: Plex item key
            item_type: Item type ('movie' or 'season')
            dry_run: Whether this is a dry run
            delayed_actions: Optional list of delayed actions to calculate deletion_date from
            item_data: Optional item data dict to get original title from
        """
        results = []
        
        # Get original title from item_data
        original_title = None
        if item_data:
            if item_type == "movie":
                # For movies, use the title field
                original_title = item_data.get("title", "")
            elif item_type == "season":
                # For seasons, use only the season_title for the {title} placeholder
                original_title = item_data.get("season_title", "")
        
        # Calculate deletion date if delayed actions are provided
        deletion_date_formatted = None
        deletion_date_readable = None
        if delayed_actions:
            max_delay = max([action.get("delay_days", 0) for action in delayed_actions], default=0)
            if max_delay > 0:
                deletion_date = datetime.now() + timedelta(days=max_delay)
                # Format as YYYY-MM-DD
                deletion_date_formatted = deletion_date.strftime("%Y-%m-%d")
                # Also provide a more readable format
                deletion_date_readable = deletion_date.strftime("%B %d, %Y")
        
        for action in actions:
            action_type = action.get("type")
            status = "dry_run" if dry_run else "success"
            
            if dry_run:
                results.append({
                    "action_type": action_type,
                    "status": "dry_run",
                    "message": f"Would execute {action_type}"
                })
                continue
            
            try:
                if action_type == "ADD_TO_COLLECTION":
                    collection_name = action.get("collection_name", "")
                    success = self.plex.add_to_collection(item_key, collection_name, item_type)
                    results.append({
                        "action_type": action_type,
                        "status": "success" if success else "failed",
                        "message": f"Added to collection {collection_name}" if success else "Failed to add to collection"
                    })
                
                elif action_type == "REMOVE_FROM_COLLECTION":
                    collection_name = action.get("collection_name", "")
                    print(f"  Executing REMOVE_FROM_COLLECTION: removing {item_type} '{item_key}' from collection '{collection_name}'")
                    success = self.plex.remove_from_collection(item_key, collection_name, item_type)
                    print(f"  REMOVE_FROM_COLLECTION result: success={success}")
                    results.append({
                        "action_type": action_type,
                        "status": "success" if success else "failed",
                        "message": f"Removed from collection {collection_name}" if success else "Failed to remove from collection"
                    })
                
                elif action_type == "SET_TITLE_FORMAT":
                    title_format = action.get("title_format", "")
                    
                    # Replace variables in title format
                    if title_format:
                        # Replace {title} with original title
                        if original_title and "{title}" in title_format:
                            title_format = title_format.replace("{title}", original_title)
                        
                        # Replace deletion date variables if available
                        if deletion_date_formatted:
                            # Replace {deletion_date} with formatted date (YYYY-MM-DD)
                            title_format = title_format.replace("{deletion_date}", deletion_date_formatted)
                            # Replace {deletion_date_readable} with readable format
                            if deletion_date_readable:
                                title_format = title_format.replace("{deletion_date_readable}", deletion_date_readable)
                    
                    success = self.plex.set_title_format(item_key, title_format, item_type)
                    results.append({
                        "action_type": action_type,
                        "status": "success" if success else "failed",
                        "message": f"Set title format to {title_format}" if success else "Failed to set title format"
                    })
                
                elif action_type == "CLEAR_TITLE_FORMAT":
                    success = self.plex.clear_title_format(item_key, item_type)
                    results.append({
                        "action_type": action_type,
                        "status": "success" if success else "failed",
                        "message": "Cleared title format" if success else "Failed to clear title format"
                    })
            
            except Exception as e:
                results.append({
                    "action_type": action_type,
                    "status": "failed",
                    "message": str(e)
                })
        
        return results
    
    def execute_delayed_action(self, action: Dict[str, Any], item_key: str, item_title: str, item_type: str, dry_run: bool) -> Dict[str, Any]:
        """Execute a delayed action"""
        action_type = action.get("type")
        
        if dry_run:
            return {
                "action_type": action_type,
                "status": "dry_run",
                "message": f"Would execute {action_type}"
            }
        
        try:
            if action_type == "DELETE_VIA_RADARR":
                if not self.radarr:
                    return {"action_type": action_type, "status": "failed", "message": "Radarr not configured"}
                
                movie = self.radarr.find_movie_by_title(item_title)
                if movie:
                    success, message = self.radarr.delete_movie(movie["id"], delete_files=True)
                    return {"action_type": action_type, "status": "success" if success else "failed", "message": message}
                else:
                    # Fallback to Plex deletion
                    success = self.plex.delete_item(item_key)
                    return {"action_type": "DELETE_IN_PLEX", "status": "success" if success else "failed", "message": "Movie not found in Radarr, deleted via Plex"}
            
            elif action_type == "DELETE_VIA_SONARR":
                if not self.sonarr:
                    return {"action_type": action_type, "status": "failed", "message": "Sonarr not configured"}
                
                # For seasons, we need the show title
                show_title = item_title.split(" - Season")[0].strip()
                series = self.sonarr.find_series_by_title(show_title)
                if series:
                    # Check if all seasons qualify (simplified - in production, track this)
                    success, message = self.sonarr.delete_series(series["id"], delete_files=True)
                    return {"action_type": action_type, "status": "success" if success else "failed", "message": message}
                else:
                    success = self.plex.delete_item(item_key)
                    return {"action_type": "DELETE_IN_PLEX", "status": "success" if success else "failed", "message": "Series not found in Sonarr, deleted via Plex"}
            
            elif action_type == "DELETE_IN_PLEX":
                success = self.plex.delete_item(item_key)
                return {"action_type": action_type, "status": "success" if success else "failed", "message": "Deleted from Plex" if success else "Failed to delete from Plex"}
            
            elif action_type == "REMOVE_FROM_COLLECTION":
                collection_name = action.get("collection_name", "")
                success = self.plex.remove_from_collection(item_key, collection_name, item_type)
                return {"action_type": action_type, "status": "success" if success else "failed", "message": f"Removed from collection {collection_name}" if success else "Failed to remove from collection"}
            
            elif action_type == "CLEAR_TITLE_FORMAT":
                success = self.plex.clear_title_format(item_key, item_type)
                return {"action_type": action_type, "status": "success" if success else "failed", "message": "Cleared title format" if success else "Failed to clear title format"}
        
        except Exception as e:
            return {"action_type": action_type, "status": "failed", "message": str(e)}
        
        return {"action_type": action_type, "status": "failed", "message": "Unknown action type"}

