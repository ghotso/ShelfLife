"""
Plex integration using plexapi
"""
from plexapi.server import PlexServer
from plexapi.exceptions import BadRequest, NotFound, PlexApiException
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta



class PlexIntegration:
    def __init__(self, baseurl: str, token: str):
        self.server = PlexServer(baseurl, token)
        self._history_cache = None
        self._history_cache_time = None
    
    def test_connection(self) -> tuple[bool, str]:
        """Test Plex connection"""
        try:
            self.server.library.sections()
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
    
    def get_libraries(self) -> List[Dict[str, Any]]:
        """Get all movie and TV show libraries"""
        libraries = []
        for section in self.server.library.sections():
            if section.type in ["movie", "show"]:
                libraries.append({
                    "plex_id": str(section.key),
                    "title": section.title,
                    "library_type": section.type
                })
        return libraries
    
    def get_movies(self, library_key: str) -> List[Any]:
        """Get all movies from a library"""
        section = self.server.library.sectionByID(int(library_key))
        if section.type == "movie":
            # Fetch movies with full metadata including viewing history
            movies = section.all()
            # Pre-build history cache once for the entire library scan
            self._get_history_cache()
            return movies
        return []
    
    def get_shows(self, library_key: str) -> List[Any]:
        """Get all TV shows from a library"""
        section = self.server.library.sectionByID(int(library_key))
        if section.type == "show":
            shows = section.all()
            # Pre-build history cache once for the entire library scan
            self._get_history_cache()
            return shows
        return []
    
    def get_seasons(self, show) -> List[Any]:
        """Get all seasons from a show"""
        return show.seasons()
    
    def _get_history_cache(self):
        """Get or build a cache of watch history"""
        # Cache for 5 minutes to avoid hitting the API too frequently
        if self._history_cache is None or (self._history_cache_time and 
            (datetime.now() - self._history_cache_time).total_seconds() > 300):
            try:
                print("  DEBUG: Building history cache from Plex API...")
                # Use the history API to get all watch history
                history = self.server.history(maxresults=50000)  # Get a large number
                self._history_cache = {}
                for item in history:
                    if hasattr(item, "ratingKey") and hasattr(item, "viewedAt"):
                        rating_key = str(item.ratingKey)
                        viewed_at = item.viewedAt
                        # Store the most recent viewing date per ratingKey
                        if rating_key not in self._history_cache:
                            self._history_cache[rating_key] = viewed_at
                        else:
                            # Keep the most recent date
                            if isinstance(viewed_at, datetime) and isinstance(self._history_cache[rating_key], datetime):
                                if viewed_at > self._history_cache[rating_key]:
                                    self._history_cache[rating_key] = viewed_at
                            elif isinstance(viewed_at, (int, float)) and isinstance(self._history_cache[rating_key], (int, float)):
                                if viewed_at > self._history_cache[rating_key]:
                                    self._history_cache[rating_key] = viewed_at
                self._history_cache_time = datetime.now()
                print(f"  DEBUG: History cache built with {len(self._history_cache)} items")
            except Exception as e:
                print(f"  DEBUG: Error building history cache: {e}")
                self._history_cache = {}
                self._history_cache_time = datetime.now()
        return self._history_cache
    
    def get_movie_data(self, movie) -> Dict[str, Any]:
        """Extract movie data for rule evaluation"""
        # Note: movie.reload() can be slow for large libraries, so we'll try to get 
        # lastViewedAt directly first, and only reload if needed
        
        collections = []
        if hasattr(movie, "collections") and movie.collections:
            for c in movie.collections:
                # In plexapi, movie.collections returns tag objects with .tag attribute
                # Collection objects (from library.collections()) have .title attribute
                # Check .tag first as that's what movie.collections typically returns
                try:
                    if hasattr(c, "tag"):
                        collections.append(c.tag)
                    elif hasattr(c, "title"):
                        collections.append(c.title)
                    elif isinstance(c, str):
                        collections.append(c)
                    elif hasattr(c, "name"):
                        collections.append(c.name)
                except (AttributeError, TypeError):
                    # Skip if we can't get the name
                    continue
        last_played = None
        # Try multiple ways to get last viewed date
        # Check various attribute names plexapi might use
        view_attrs_to_try = [
            "lastViewedAt",
            "lastViewed",
            "viewedAt",
            "lastPlayedAt",
            "lastPlayed",
        ]
        
        for attr in view_attrs_to_try:
            if hasattr(movie, attr):
                try:
                    value = getattr(movie, attr, None)
                    # Check if value is not None and not empty/zero
                    if value:
                        last_played = value
                        print(f"  DEBUG: Found last viewed date for '{movie.title}' via {attr}: {last_played}")
                        break
                except (AttributeError, PlexApiException, TypeError, ValueError):
                    continue
        
        # If still not found, try reloading the movie to get full metadata
        if not last_played:
            try:
                # Force reload with all metadata
                movie.reload()
                # Try again after reload
                for attr in view_attrs_to_try:
                    if hasattr(movie, attr):
                        try:
                            value = getattr(movie, attr, None)
                            if value:
                                last_played = value
                                print(f"  DEBUG: Found last viewed date after reload for '{movie.title}' via {attr}: {last_played}")
                                break
                        except (AttributeError, PlexApiException, TypeError, ValueError):
                            continue
            except Exception as e:
                print(f"  DEBUG: Could not reload movie '{movie.title}': {e}")
        
        # If still not found, print debug info
        if not last_played:
            # Check what attributes the movie actually has
            view_count = getattr(movie, "viewCount", None)
            print(f"  DEBUG: No last viewed date found for '{movie.title}' (viewCount={view_count})")
        
        # Last resort: Try getting from history cache (built from history API)
        if not last_played:
            try:
                rating_key = str(getattr(movie, "ratingKey", None))
                if rating_key:
                    history_cache = self._get_history_cache()
                    if rating_key in history_cache:
                        last_played = history_cache[rating_key]
                        print(f"  DEBUG: Found last viewed date for '{movie.title}' from history cache: {last_played}")
            except Exception as e:
                print(f"  DEBUG: Error checking history cache: {e}")
        
        last_played_days = None
        if last_played:
            try:
                if isinstance(last_played, datetime):
                    delta = datetime.now() - last_played
                elif isinstance(last_played, (int, float)):
                    delta = datetime.now() - datetime.fromtimestamp(last_played)
                elif isinstance(last_played, str):
                    # Try parsing as ISO format or timestamp
                    try:
                        last_played_dt = datetime.fromisoformat(last_played.replace('Z', '+00:00'))
                        delta = datetime.now() - last_played_dt.replace(tzinfo=None)
                    except:
                        delta = datetime.now() - datetime.fromtimestamp(float(last_played))
                else:
                    print(f"  DEBUG: Unknown last_played type: {type(last_played)}, value: {last_played}")
                    delta = None
                
                if delta:
                    last_played_days = delta.days
            except Exception as e:
                print(f"  DEBUG: Error calculating days: {e}, last_played={last_played}, type={type(last_played)}")
        
        return {
            "key": movie.key,
            "title": movie.title,
            "lastPlayedDays": last_played_days,
            "inCollections": collections
        }
    
    def get_season_data(self, season) -> Dict[str, Any]:
        """Extract season data for rule evaluation"""
        show = season.show()
        collections = []
        
        # Check show collections (applies to entire show)
        if hasattr(show, "collections") and show.collections:
            print(f"  DEBUG: Show '{show.title}' has {len(show.collections)} collection(s) via show.collections")
            for c in show.collections:
                # In plexapi, show.collections returns tag objects with .tag attribute
                # Collection objects (from library.collections()) have .title attribute
                # Check .tag first as that's what show.collections typically returns
                try:
                    coll_name = None
                    if hasattr(c, "tag"):
                        coll_name = c.tag
                    elif hasattr(c, "title"):
                        coll_name = c.title
                    elif isinstance(c, str):
                        coll_name = c
                    elif hasattr(c, "name"):
                        coll_name = c.name
                    
                    if coll_name:
                        collections.append(coll_name)
                        print(f"  DEBUG: Found collection '{coll_name}' via show.collections")
                except (AttributeError, TypeError) as e:
                    # Skip if we can't get the name
                    print(f"  DEBUG: Error extracting collection name from show.collections item: {e}")
                    continue
        else:
            print(f"  DEBUG: Show '{show.title}' has no collections via show.collections (hasattr: {hasattr(show, 'collections')})")
        
        # ALSO check library collections to see if this specific season is in any collection
        # This is needed because seasons can be added to collections individually
        # Check BOTH show-level and season-level collections for rule conditions
        # The condition should return TRUE if EITHER the show OR the season is in the collection
        try:
            section = season.section()
            library_collections = section.collections()
            season_key = season.key
            show_key = show.key
            
            for collection in library_collections:
                # Get collection name
                coll_name = None
                if hasattr(collection, "tag"):
                    coll_name = collection.tag
                elif hasattr(collection, "title"):
                    coll_name = collection.title
                elif hasattr(collection, "name"):
                    coll_name = collection.name
                
                # Only check if we haven't already found this collection
                # Note: We check all collections, even if we found them via show.collections, to catch direct season memberships
                if coll_name:
                    # Check if EITHER the show OR the season is in this collection
                    try:
                        # Get all items in the collection
                        collection_items = collection.items()
                        show_in_collection = False
                        season_in_collection = False
                        
                        # Check all items to see if show or season is present
                        print(f"  DEBUG: Checking collection '{coll_name}' - found {len(collection_items)} item(s)")
                        for item in collection_items:
                            if hasattr(item, "key"):
                                item_type = getattr(item, "type", "unknown")
                                print(f"  DEBUG: Collection item: key={item.key}, type={item_type}, title={getattr(item, 'title', 'N/A')}")
                                if item.key == show_key:
                                    show_in_collection = True
                                    print(f"  DEBUG: Match! Show key {show_key} found in collection '{coll_name}'")
                                elif item.key == season_key:
                                    season_in_collection = True
                                    print(f"  DEBUG: Match! Season key {season_key} found in collection '{coll_name}'")
                        
                        # If EITHER show OR season is in collection, add it to the list (if not already there)
                        if (show_in_collection or season_in_collection) and coll_name not in collections:
                            collections.append(coll_name)
                            if show_in_collection:
                                print(f"  DEBUG: Found season in collection '{coll_name}' via show membership (show in collection)")
                            if season_in_collection:
                                print(f"  DEBUG: Found season in collection '{coll_name}' via direct season membership")
                    except Exception as e:
                        # Skip if we can't check collection items
                        print(f"  DEBUG: Error checking collection '{coll_name}' for season: {e}")
                        continue
        except Exception as e:
            print(f"  DEBUG: Error checking library collections for season: {e}")
        
        print(f"  DEBUG: Season '{season.title}' collections: {collections}")
        
        # Find most recently watched episode in season
        # We need to check both the episode objects AND the history cache
        last_watched_episode = None
        last_watched_episode_title = None
        last_watched_episode_number = None
        last_watched_episode_date = None
        last_watched_days = None
        episode_count = 0
        history_cache = self._get_history_cache()
        
        if hasattr(season, "episodes"):
            episodes = season.episodes()
            episode_count = len(episodes) if episodes else 0
            for episode in episodes:
                ep_time = None
                
                # First try to get from episode object directly
                if hasattr(episode, "lastViewedAt") and episode.lastViewedAt:
                    ep_time = episode.lastViewedAt
                
                # If not found, try history cache by ratingKey
                if not ep_time:
                    try:
                        rating_key = str(getattr(episode, "ratingKey", None))
                        if rating_key and rating_key in history_cache:
                            ep_time = history_cache[rating_key]
                            print(f"  DEBUG: Found watch date for episode '{episode.title}' (S{season.index}E{episode.index}) from history cache: {ep_time}")
                    except Exception:
                        pass
                
                # Calculate days if we found a watch time
                if ep_time:
                    # Convert to datetime if needed
                    ep_datetime = None
                    if isinstance(ep_time, datetime):
                        ep_datetime = ep_time
                        delta = datetime.now() - ep_time
                    elif isinstance(ep_time, (int, float)):
                        ep_datetime = datetime.fromtimestamp(ep_time)
                        delta = datetime.now() - ep_datetime
                    else:
                        try:
                            # Try parsing as string
                            if isinstance(ep_time, str):
                                ep_datetime = datetime.fromisoformat(ep_time.replace('Z', '+00:00')).replace(tzinfo=None)
                                delta = datetime.now() - ep_datetime
                            else:
                                continue
                        except Exception:
                            continue
                    
                    days = delta.days
                    # Keep the most recent watch (smallest number of days)
                    if last_watched_days is None or days < last_watched_days:
                        last_watched_days = days
                        last_watched_episode = episode
                        last_watched_episode_title = episode.title if hasattr(episode, "title") else None
                        last_watched_episode_number = episode.index if hasattr(episode, "index") else None
                        last_watched_episode_date = ep_datetime
        
        return {
            "key": season.key,
            "show_title": show.title,
            "season_title": season.title,
            "season_number": season.index,
            "episode_count": episode_count,
            "lastWatchedEpisodeDays": last_watched_days,
            "lastWatchedEpisodeTitle": last_watched_episode_title,
            "lastWatchedEpisodeNumber": last_watched_episode_number,
            "lastWatchedEpisodeDate": last_watched_episode_date,
            "inCollections": collections  # Add collections support for seasons
        }
    
    def add_to_collection(self, item_key: str, collection_name: str, item_type: str = "movie") -> bool:
        """Add item to a collection
        
        For movies: adds the movie to the collection
        For seasons: adds the season (not the show) to the collection
        This is used for rule-based actions.
        """
        try:
            item = self.server.fetchItem(item_key)
            # For seasons, keep the season itself (don't convert to show)
            # This ensures we add only the season, not the entire show
            
            # Get or create collection
            # For seasons, we need to get the section from the show, but add the season itself
            if item_type == "season":
                section = item.show().section()
            else:
                section = item.section()
            
            collections = section.collections()
            collection = None
            for c in collections:
                # Get collection name - could be .tag, .title, or .name
                coll_name = None
                if isinstance(c, str):
                    coll_name = c
                elif hasattr(c, "tag"):
                    coll_name = c.tag
                elif hasattr(c, "title"):
                    coll_name = c.title
                elif hasattr(c, "name"):
                    coll_name = c.name
                
                if coll_name == collection_name:
                    collection = c
                    break
            
            if not collection:
                # Create new collection with the item included (Plex requires items when creating)
                collection = section.createCollection(collection_name, items=[item])
            else:
                # Add the item to existing collection
                collection.addItems([item])
            return True
        except Exception as e:
            print(f"Error adding to collection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def add_show_to_collection(self, season_key: str, collection_name: str) -> bool:
        """Add the show (not the season) to a collection
        
        This is used for manual "Add to Collection" button clicks on season candidates.
        For season candidates, we want to add the entire show to the collection.
        
        Since Plex doesn't allow mixing seasons and shows in the same collection,
        if the collection already contains seasons from this show, we remove them first.
        """
        try:
            season = self.server.fetchItem(season_key)
            show = season.show()
            show_key = show.key
            
            # First, check if the show is already in this collection (via show.collections)
            if hasattr(show, "collections") and show.collections:
                for c in show.collections:
                    coll_name = None
                    if isinstance(c, str):
                        coll_name = c
                    elif hasattr(c, "tag"):
                        coll_name = c.tag
                    elif hasattr(c, "title"):
                        coll_name = c.title
                    elif hasattr(c, "name"):
                        coll_name = c.name
                    
                    if coll_name == collection_name:
                        # Show is already in the collection, nothing to do
                        return True
            
            # Get section from the show
            section = show.section()
            
            # Get or create collection
            collections = section.collections()
            collection = None
            for c in collections:
                # Get collection name - could be .tag, .title, or .name
                coll_name = None
                if isinstance(c, str):
                    coll_name = c
                elif hasattr(c, "tag"):
                    coll_name = c.tag
                elif hasattr(c, "title"):
                    coll_name = c.title
                elif hasattr(c, "name"):
                    coll_name = c.name
                
                if coll_name == collection_name:
                    collection = c
                    break
            
            if not collection:
                # Create new collection with the show included (Plex requires items when creating)
                collection = section.createCollection(collection_name, items=[show])
            else:
                # Check if collection already has seasons from this show - if so, remove them first
                try:
                    existing_items = collection.items()
                    if existing_items:
                        # Check if any seasons from this show are in the collection
                        seasons_to_remove = []
                        for item in existing_items:
                            # Check if this item is a season from our show
                            if hasattr(item, "type") and item.type == "season":
                                try:
                                    item_show = item.show()
                                    if hasattr(item_show, "key") and item_show.key == show_key:
                                        seasons_to_remove.append(item)
                                except Exception:
                                    pass
                        
                        # Remove seasons from this show before adding the show
                        if seasons_to_remove:
                            print(f"  DEBUG: Removing {len(seasons_to_remove)} season(s) from '{collection_name}' before adding show")
                            collection.removeItems(seasons_to_remove)
                except Exception as e:
                    print(f"  DEBUG: Error checking/removing existing items: {e}")
                    # Continue anyway - try to add the show
                
                # Try to add the show to existing collection
                try:
                    collection.addItems([show])
                except BadRequest as e:
                    # If still mixing types error, there might be seasons from other shows
                    if "mix media types" in str(e).lower():
                        error_msg = f"Collection '{collection_name}' contains seasons from other shows and cannot accept shows. Please create a new collection or remove those seasons first."
                        print(f"  DEBUG: {error_msg}")
                        raise ValueError(error_msg)
                    raise
            return True
        except ValueError:
            # Re-raise ValueError as-is (for user-friendly error messages)
            raise
        except Exception as e:
            print(f"Error adding show to collection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def remove_from_collection(self, item_key: str, collection_name: str, item_type: str = "movie") -> bool:
        """Remove item from a collection
        
        For movies: removes the movie from the collection
        For seasons: 
        - If the show is in the collection, removes the show (which removes all seasons)
        - If only the season is in the collection, removes just the season
        """
        try:
            item = self.server.fetchItem(item_key)
            
            # Get the section/library to access actual Collection objects
            if item_type == "season":
                section = item.show().section()
            else:
                section = item.section()
            
            # Get all collections from the library
            library_collections = section.collections()
            
            # Find the collection by name
            target_collection = None
            for collection in library_collections:
                coll_name = None
                if hasattr(collection, "tag"):
                    coll_name = collection.tag
                elif hasattr(collection, "title"):
                    coll_name = collection.title
                elif hasattr(collection, "name"):
                    coll_name = collection.name
                
                # Normalize collection names for comparison (case-insensitive, strip whitespace)
                if coll_name and collection_name and coll_name.strip().lower() == collection_name.strip().lower():
                    target_collection = collection
                    break
            
            if not target_collection:
                print(f"  DEBUG: Collection '{collection_name}' not found")
                return False
            
            if item_type == "season":
                # For seasons, first check if the show is in the collection
                # If so, remove the show (which will remove all seasons from the collection)
                show = item.show()
                show_key = show.key
                
                try:
                    collection_items = target_collection.items()
                    show_in_collection = False
                    season_in_collection = False
                    
                    for coll_item in collection_items:
                        if hasattr(coll_item, "key"):
                            if coll_item.key == show_key:
                                show_in_collection = True
                            elif coll_item.key == item.key:
                                season_in_collection = True
                    
                    if show_in_collection:
                        # Show is in collection, remove the show
                        target_collection.removeItems([show])
                        print(f"  DEBUG: Removed show '{show.title}' from collection '{collection_name}'")
                        return True
                    elif season_in_collection:
                        # Season is directly in collection, remove just the season
                        target_collection.removeItems([item])
                        print(f"  DEBUG: Removed season '{item.title}' from collection '{collection_name}'")
                        return True
                except Exception as e:
                    print(f"  DEBUG: Error checking/removing from collection: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                # For movies, check if the movie is in the collection and remove it
                try:
                    collection_items = target_collection.items()
                    for coll_item in collection_items:
                        if hasattr(coll_item, "key") and coll_item.key == item.key:
                            target_collection.removeItems([item])
                            print(f"  DEBUG: Removed movie '{item.title}' from collection '{collection_name}'")
                            return True
                except Exception as e:
                    print(f"  DEBUG: Error removing movie from collection: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            return False
        except Exception as e:
            print(f"Error removing from collection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_title_format(self, item_key: str, title_format: str, item_type: str = "movie") -> bool:
        """Set title format for an item"""
        try:
            item = self.server.fetchItem(item_key)
            if item_type == "movie":
                item.editTitle(title_format)
            elif item_type == "season":
                # For seasons, we might want to edit the show title or season title
                # This is a simplified version
                pass
            return True
        except Exception as e:
            print(f"Error setting title format: {e}")
            return False
    
    def clear_title_format(self, item_key: str, item_type: str = "movie") -> bool:
        """Clear custom title format by restoring the original title"""
        try:
            item = self.server.fetchItem(item_key)
            original_title = getattr(item, "originalTitle", None) or getattr(item, "title", "")
            if item_type == "movie":
                item.editTitle(original_title)
            elif item_type == "season":
                # For seasons, restore the original title
                item.editTitle(original_title)
            return True
        except Exception as e:
            print(f"Error clearing title format: {e}")
            return False
    
    def delete_item(self, item_key: str) -> bool:
        """Delete item from Plex (doesn't delete files, just removes from library)"""
        try:
            item = self.server.fetchItem(item_key)
            item.delete()
            return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False

