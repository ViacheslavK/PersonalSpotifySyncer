# Spotify Account Synchronizer

Synchronizes liked tracks, albums, playlists, and artists between two Spotify accounts.

## What Gets Synchronized

- ✅ Liked tracks (Liked Songs)
- ✅ Saved albums
- ✅ Followed artists
- ✅ All playlists with all tracks

## What Does NOT Get Synchronized

- ❌ Listening history
- ❌ Statistics (Top tracks, Top artists)
- ❌ Recommendations

## Installation

### 1. Install Dependencies

```bash
pip install spotipy
```

### 2. Create a Spotify App

1. Go to <https://developer.spotify.com/dashboard>
2. Click "Create app"
3. Fill in:
   - **App name**: any name (e.g., "My Sync Tool")
   - **App description**: any description
   - **Redirect URIs**: `http://127.0.0.1:8888/callback`
4. Save your **Client ID** and **Client Secret**

### 3. Add Users to Your App

Since your app is in Development Mode, you need to add both accounts:

1. In your app's Dashboard, go to **Settings**
2. Find **"User Management"** section
3. Click **"Add User"**
4. Add **both** email addresses (source and target accounts)
5. Save changes

### 4. Configure the Application

On first run, the program will automatically create a `config.json` file. Edit it:

```json
{
    "CLIENT_ID": "your_client_id_from_spotify_dashboard",
    "CLIENT_SECRET": "your_client_secret_from_spotify_dashboard",
    "REDIRECT_URI": "http://127.0.0.1:8888/callback",
    "SOURCE_CACHE": ".cache-source",
    "TARGET_CACHE": ".cache-target"
}
```

Alternatively, copy `config.example.json` to `config.json` and fill in your credentials.

## Usage

Run the program:

```bash
python spotify_sync.py
```

### First Run (Authentication)

#### If No Accounts Are Authenticated Yet

1. The program will show an authorization link for the **source account**
2. Copy the link and open it in your browser
3. Log in to your source Spotify account
4. After authorization, copy the URL from the browser's address bar (starts with `http://127.0.0.1:8888/callback?code=...`)
5. Paste the URL back into the console
6. Repeat steps 1-5 for the **target account**

#### If Accounts Are Already Authenticated

The program will show current account info and ask if you want to re-authenticate:

```bash
SOURCE account currently authenticated as:
  Name: John Doe
  User ID: abc123xyz
  Email: john@example.com

Do you want to re-authenticate the source account? (yes/no):
```

This allows you to easily switch accounts without manually deleting cache files.

### Subsequent Runs

The program uses saved tokens - no authentication needed! Just run it and it will synchronize everything automatically.

### Confirmation Before Sync

Before starting synchronization, the program will show the direction and ask for confirmation:

```bash
======================================================================
SYNCHRONIZATION DIRECTION:
  FROM: John Doe (ID: abc123, Email: john@example.com)
  TO:   Jane Smith (ID: xyz789, Email: jane@work.com)
======================================================================

Proceed with synchronization? (yes/no):
```

## Project Structure

```bash
spotify-sync/
├── spotify_sync.py          # Main program code
├── config.json              # Your configuration (DO NOT commit to Git!)
├── config.example.json      # Configuration example
├── .gitignore              # Protects secrets
├── README.md               # This documentation
├── .cache-source           # Source account tokens (auto-generated)
└── .cache-target           # Target account tokens (auto-generated)
```

## Security

⚠️ **IMPORTANT**: Never commit to Git:

- `config.json` - contains your secrets
- `.cache-*` files - contain access tokens

The `.gitignore` file is already configured to protect these files.

## Automated Synchronization

If you need regular synchronization, set up cron (Linux/Mac) or Task Scheduler (Windows):

### Linux/Mac (cron)

```bash
# Open crontab
crontab -e

# Add a line (sync every 6 hours)
0 */6 * * * cd /path/to/project && python spotify_sync.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create a new task
3. Set trigger (e.g., every 6 hours)
4. Action: run program `python.exe` with argument `/path/to/spotify_sync.py`

## Troubleshooting

### "Redirect URI mismatch"

- Verify that **exactly** `http://127.0.0.1:8888/callback` is added in Spotify Dashboard
- Check that the same URI is in `config.json`

### "Invalid client"

- Check CLIENT_ID and CLIENT_SECRET in `config.json`
- Make sure there are no extra spaces

### "User may not be registered"

- Your app is in Development Mode
- Go to Spotify Dashboard → Your App → Settings → User Management
- Add both account emails (source and target)

### Tokens expired

Delete `.cache-*` files and run the program again to re-authenticate.

### Email shows as "Unknown"

This is normal - Spotify doesn't always return email depending on account privacy settings. The program shows User ID instead, which is always available and uniquely identifies each account.

## License

MIT
