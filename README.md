SPOTIFY PLAYLIST CREATOR

The Spotify Playlist Generator is a python application that allows users to create Spotify playlists based on genre or the most popular songs from a specific date.
The applications uses Spotify API and BILLBOARD TOP 100 to search for songs and build playlists.

FEATURES

- Create Playlist by Genre - Select a genre from a predefined list and provide additional details to create a playlist
- Create Playlist by Date - Choose a date to generate a playlist based on the most popular song from that date

REQUIREMENTS

- Python 3.x
- tkkbootstrap library
- requests
- Spotify Developer Account (for API calls)


INSTALLATION

1. Obtain Spotify API Credentials:
    Visit the Spotify Developer Dashboard - https://developer.spotify.com/
    Create a new application to obtain the client ID, client secret, and set the redirect URI.

2. Update "spotify.py" File:
    Open the "spotify.py" file in your project.
    Replace the placeholders for "SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET" and "SPOTIFY_REDIRECT" with your credentials.

USAGE

- Run the application using Python
- Navigate through the GUI screens to create playlists by genre or date