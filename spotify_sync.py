"""
Spotify Account Synchronizer
Synchronizes liked tracks, albums, playlists, and artists between two Spotify accounts
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from typing import List, Dict, Set, Optional
import os
from pathlib import Path

class SpotifySync:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize the synchronizer
        
        Args:
            client_id: Client ID from Spotify Developer Dashboard
            client_secret: Client Secret from Spotify Developer Dashboard
            redirect_uri: Redirect URI (e.g., http://127.0.0.1:8888/callback)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Scope - required permissions
        self.scope = (
            "user-library-read "
            "user-library-modify "
            "playlist-read-private "
            "playlist-modify-public "
            "playlist-modify-private "
            "user-follow-read "
            "user-follow-modify"
        )
    
    def authenticate_account(self, cache_path: str, account_name: str = "", force_reauth: bool = False) -> Optional[spotipy.Spotify]:
        """
        Authenticate a Spotify account
        
        Args:
            cache_path: Path to token cache file (e.g., .cache-source)
            account_name: Account name for display (e.g., "source" or "target")
            force_reauth: If True, force re-authentication even if token exists
        
        Returns:
            Spotify API object or None if user cancels
        """
        # If force reauth, delete existing cache
        if force_reauth and Path(cache_path).exists():
            Path(cache_path).unlink()
        
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path=cache_path,
            open_browser=False  # Don't open browser automatically
        )
        
        # Check if we have a cached token
        token_info = auth_manager.get_cached_token()
        
        if not token_info:
            # Generate authorization URL
            auth_url = auth_manager.get_authorize_url()
            
            print(f"\n{'='*70}")
            print(f"AUTHENTICATION - {account_name.upper()} ACCOUNT")
            print(f"{'='*70}")
            print("\n1. Copy this link and open it in your browser:")
            print(f"\n{auth_url}\n")
            print("2. Log in to the appropriate Spotify account")
            print("3. After authorization, you'll be redirected to 127.0.0.1")
            print("4. Copy the FULL URL from the browser's address bar")
            print("   (it will look like: http://127.0.0.1:8888/callback?code=...)")
            print(f"{'='*70}\n")
            
            # Get URL from user
            response_url = input("Paste the copied URL here (or 'cancel' to abort): ").strip()
            
            if response_url.lower() == 'cancel':
                print("Authentication cancelled.")
                return None
            
            # Extract authorization code from URL
            code = auth_manager.parse_response_code(response_url)
            token_info = auth_manager.get_access_token(code)
            
            print(f"✓ Authentication successful for {account_name} account!\n")
        else:
            print(f"✓ Using cached token for {account_name} account\n")
        
        return spotipy.Spotify(auth_manager=auth_manager)
    
    def get_account_info(self, sp: spotipy.Spotify) -> Dict[str, str]:
        """Get basic account information"""
        user = sp.current_user()
        return {
            'display_name': user.get('display_name', 'Unknown'),
            'email': user.get('email', 'Unknown'),
            'id': user['id']
        }
    
    def should_reauth_account(self, cache_path: str, account_name: str) -> bool:
        """
        Ask user if they want to re-authenticate an account
        
        Args:
            cache_path: Path to token cache file
            account_name: Account name for display
        
        Returns:
            True if user wants to re-authenticate
        """
        if not Path(cache_path).exists():
            return False
        
        # Try to get current account info
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=cache_path,
                open_browser=False
            )
            token_info = auth_manager.get_cached_token()
            if token_info:
                sp = spotipy.Spotify(auth_manager=auth_manager)
                info = self.get_account_info(sp)
                print(f"\n{account_name.upper()} account currently authenticated as:")
                print(f"  Name: {info['display_name']}")
                print(f"  User ID: {info['id']}")
                print(f"  Email: {info['email']}")
                
                response = input(f"\nDo you want to re-authenticate the {account_name} account? (yes/no): ").strip().lower()
                return response in ['yes', 'y']
        except Exception as e:
            print(f"⚠️  Could not read {account_name} account info: {e}")
            response = input(f"\nDo you want to re-authenticate the {account_name} account? (yes/no): ").strip().lower()
            return response in ['yes', 'y']
        
        return False
    
    def get_saved_tracks(self, sp: spotipy.Spotify) -> List[str]:
        """Get all saved tracks (liked songs)"""
        tracks = []
        results = sp.current_user_saved_tracks(limit=50)
        
        while results:
            for item in results['items']:
                tracks.append(item['track']['id'])
            
            if results['next']:
                results = sp.next(results)
            else:
                break
        
        print(f"Found {len(tracks)} saved tracks")
        return tracks
    
    def save_tracks(self, sp: spotipy.Spotify, track_ids: List[str]):
        """Save tracks to library"""
        # Spotify API allows adding max 50 tracks at a time
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i+50]
            sp.current_user_saved_tracks_add(batch)
        print(f"Saved {len(track_ids)} tracks")
    
    def get_saved_albums(self, sp: spotipy.Spotify) -> List[str]:
        """Get all saved albums"""
        albums = []
        results = sp.current_user_saved_albums(limit=50)
        
        while results:
            for item in results['items']:
                albums.append(item['album']['id'])
            
            if results['next']:
                results = sp.next(results)
            else:
                break
        
        print(f"Found {len(albums)} saved albums")
        return albums
    
    def save_albums(self, sp: spotipy.Spotify, album_ids: List[str]):
        """Save albums to library"""
        for i in range(0, len(album_ids), 50):
            batch = album_ids[i:i+50]
            sp.current_user_saved_albums_add(batch)
        print(f"Saved {len(album_ids)} albums")
    
    def get_followed_artists(self, sp: spotipy.Spotify) -> List[str]:
        """Get all followed artists"""
        artists = []
        results = sp.current_user_followed_artists(limit=50)
        
        while results:
            for item in results['artists']['items']:
                artists.append(item['id'])
            
            if results['artists']['next']:
                results = sp.next(results['artists'])
            else:
                break
        
        print(f"Found {len(artists)} followed artists")
        return artists
    
    def follow_artists(self, sp: spotipy.Spotify, artist_ids: List[str]):
        """Follow artists"""
        for i in range(0, len(artist_ids), 50):
            batch = artist_ids[i:i+50]
            sp.user_follow_artists(batch)
        print(f"Followed {len(artist_ids)} artists")
    
    def get_playlists(self, sp: spotipy.Spotify) -> List[Dict]:
        """Get all user's playlists"""
        playlists = []
        results = sp.current_user_playlists(limit=50)
        
        while results:
            for item in results['items']:
                playlists.append({
                    'id': item['id'],
                    'name': item['name'],
                    'description': item['description'],
                    'public': item['public'],
                    'owner': item['owner']['id']
                })
            
            if results['next']:
                results = sp.next(results)
            else:
                break
        
        print(f"Found {len(playlists)} playlists")
        return playlists
    
    def get_playlist_tracks(self, sp: spotipy.Spotify, playlist_id: str) -> List[str]:
        """Get all tracks from a playlist"""
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        
        while results:
            for item in results['items']:
                if item['track']:  # Check that track exists
                    tracks.append(item['track']['id'])
            
            if results['next']:
                results = sp.next(results)
            else:
                break
        
        return tracks
    
    def create_playlist(self, sp: spotipy.Spotify, name: str, description: str, 
                       public: bool, track_ids: List[str]) -> str:
        """Create a playlist with tracks"""
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(
            user_id, 
            name, 
            public=public, 
            description=description
        )
        
        # Add tracks (max 100 at a time)
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            sp.playlist_add_items(playlist['id'], batch)
        
        return playlist['id']
    
    def sync_accounts(self, source_cache: str, target_cache: str):
        """
        Main synchronization function
        
        Args:
            source_cache: Path to source account cache (e.g., .cache-source)
            target_cache: Path to target account cache (e.g., .cache-target)
        """
        print("=== SPOTIFY ACCOUNT SYNCHRONIZATION ===\n")
        
        # Check if we need to re-authenticate any accounts
        force_source_reauth = self.should_reauth_account(source_cache, "source")
        force_target_reauth = self.should_reauth_account(target_cache, "target")
        
        # Authenticate both accounts
        print("\n📱 STEP 1: Authenticating source account...")
        source_sp = self.authenticate_account(source_cache, "source", force_source_reauth)
        if source_sp is None:
            print("❌ Synchronization cancelled.")
            return
        
        source_info = self.get_account_info(source_sp)
        print(f"✓ Logged in as: {source_info['display_name']} (ID: {source_info['id']})\n")
        
        print("📱 STEP 2: Authenticating target account...")
        target_sp = self.authenticate_account(target_cache, "target", force_target_reauth)
        if target_sp is None:
            print("❌ Synchronization cancelled.")
            return
        
        target_info = self.get_account_info(target_sp)
        print(f"✓ Logged in as: {target_info['display_name']} (ID: {target_info['id']})\n")
        
        # Confirm synchronization direction
        print(f"\n{'='*70}")
        print("SYNCHRONIZATION DIRECTION:")
        print(f"  FROM: {source_info['display_name']} (ID: {source_info['id']}, Email: {source_info['email']})")
        print(f"  TO:   {target_info['display_name']} (ID: {target_info['id']}, Email: {target_info['email']})")
        print(f"{'='*70}\n")
        
        response = input("Proceed with synchronization? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Synchronization cancelled.")
            return
        
        print("\n🔄 Starting synchronization...\n")
        
        # 1. Synchronize saved tracks
        print("--- Synchronizing Liked Tracks ---")
        source_tracks = set(self.get_saved_tracks(source_sp))
        target_tracks = set(self.get_saved_tracks(target_sp))
        new_tracks = list(source_tracks - target_tracks)
        
        if new_tracks:
            self.save_tracks(target_sp, new_tracks)
        else:
            print("No new tracks to sync\n")
        
        # 2. Synchronize albums
        print("\n--- Synchronizing Albums ---")
        source_albums = set(self.get_saved_albums(source_sp))
        target_albums = set(self.get_saved_albums(target_sp))
        new_albums = list(source_albums - target_albums)
        
        if new_albums:
            self.save_albums(target_sp, new_albums)
        else:
            print("No new albums to sync\n")
        
        # 3. Synchronize artists
        print("\n--- Synchronizing Artists ---")
        source_artists = set(self.get_followed_artists(source_sp))
        target_artists = set(self.get_followed_artists(target_sp))
        new_artists = list(source_artists - target_artists)
        
        if new_artists:
            self.follow_artists(target_sp, new_artists)
        else:
            print("No new artists to sync\n")
        
        # 4. Synchronize playlists
        print("\n--- Synchronizing Playlists ---")
        source_playlists = self.get_playlists(source_sp)
        target_playlists = self.get_playlists(target_sp)
        
        # Get names of existing playlists in target account
        target_playlist_names = {pl['name'] for pl in target_playlists}
        
        for playlist in source_playlists:
            # Only sync playlists that don't exist in target
            if playlist['name'] not in target_playlist_names:
                print(f"Copying playlist: {playlist['name']}")
                tracks = self.get_playlist_tracks(source_sp, playlist['id'])
                
                if tracks:
                    self.create_playlist(
                        target_sp,
                        playlist['name'],
                        playlist['description'] or "",
                        playlist['public'],
                        tracks
                    )
                    print(f"Created playlist with {len(tracks)} tracks\n")
        
        print("\n=== SYNCHRONIZATION COMPLETE ===")


def load_config():
    """
    Load configuration from config.json
    If file doesn't exist - create a template
    """
    config_file = Path("config.json")
    
    if not config_file.exists():
        # Create configuration template
        template = {
            "CLIENT_ID": "your_client_id_here",
            "CLIENT_SECRET": "your_client_secret_here",
            "REDIRECT_URI": "http://127.0.0.1:8888/callback",
            "SOURCE_CACHE": ".cache-source",
            "TARGET_CACHE": ".cache-target"
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4, ensure_ascii=False)
        
        print("⚠️  Created config.json file")
        print("📝 Please edit it and add your CLIENT_ID and CLIENT_SECRET")
        print("🔗 Get them here: https://developer.spotify.com/dashboard")
        return None
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Check if required fields are filled
    if config['CLIENT_ID'] == "your_client_id_here" or config['CLIENT_SECRET'] == "your_client_secret_here":
        print("⚠️  Error: CLIENT_ID and CLIENT_SECRET are not configured in config.json")
        print("📝 Please edit config.json and add your credentials")
        return None
    
    return config


def main():
    """
    Main entry point
    """
    # Load configuration
    config = load_config()
    if config is None:
        return
    
    # Create synchronizer
    sync = SpotifySync(
        config['CLIENT_ID'],
        config['CLIENT_SECRET'],
        config['REDIRECT_URI']
    )
    
    # Run synchronization
    sync.sync_accounts(
        source_cache=config['SOURCE_CACHE'],
        target_cache=config['TARGET_CACHE']
    )


if __name__ == "__main__":
    main()