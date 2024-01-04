import logging
import requests
import base64
import webbrowser
import urllib.parse
from random import randint
import datetime
import json
from dotenv import load_dotenv
import os

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT = os.getenv("SPOTIFY_REDIRECT")


class Spotify:
    def __init__(self, user_name, playlist_name, gui_ref=None):
        self.gui_ref = gui_ref
        self.user_name = user_name
        self.playlist_name = playlist_name
        self.access_token = self.get_access_token()
        self.playlist_id = self.create_playlist()

    def get_access_token(self):

        """Get Access Token and return it by authenticating or refreshing expired token"""

        # Check if the access token is saved in .cache and if it is expired
        try:
            with open(".cache", "r") as cache:
                data = json.loads(cache.read())
                expires_at = data["expires_at"]
                refresh_token = data["refresh_token"]

                if datetime.datetime.now().timestamp() < expires_at:
                    return data["access_token"]

                else:
                    return self.refresh_access_token(refresh_token)

        except (FileNotFoundError, ValueError):
            try:
                # Get Authorization Code

                url = "https://accounts.spotify.com/authorize?"
                data = {
                    "client_id": SPOTIFY_CLIENT_ID,
                    "response_type": "code",
                    "redirect_uri": SPOTIFY_REDIRECT,
                    "scope": "playlist-modify-private"
                }

                webbrowser.open(url + urllib.parse.urlencode(data))
                redirect_url = self.gui_ref.get_redirect_url()
                authorization_code = redirect_url.split("=", 1)[1]

                # Exchange Authorization Code for Access Token

                string = SPOTIFY_CLIENT_ID + ":" + SPOTIFY_CLIENT_SECRET
                byte_data = string.encode("utf-8")
                encoded = str(base64.b64encode(byte_data), "utf-8")

                url = "https://accounts.spotify.com/api/token"
                headers = {
                    "Authorization": "Basic " + encoded,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                data = {
                    "grant_type": "authorization_code",
                    "code": authorization_code,
                    "redirect_uri": SPOTIFY_REDIRECT,
                }

                response = requests.post(url, headers=headers, data=data)
                response.raise_for_status()

                # save the access token and refresh token

                with open(".cache", "w") as cache:
                    data = response.json()
                    data["expires_at"] = datetime.datetime.now().timestamp() + 3600
                    json_formatted = str(data).replace("'", '"')
                    cache.write(json_formatted)

                return response.json()["access_token"]

            except requests.exceptions.RequestException as error:
                logging.error(f"Error getting access token: {error}")
                self.gui_ref.show_error_message(f"URL not provided properly")
                raise

    def refresh_access_token(self, refresh_token):

        """Refreshes expired access token"""

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET
        }

        try:
            response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
            response.raise_for_status()

            # save the new access token
            with open(".cache", "w") as cache:
                data = response.json()
                data['expires_at'] = datetime.datetime.now().timestamp() + 3600
                data['refresh_token'] = refresh_token
                json_formatted = str(data).replace("'", '"')
                cache.write(json_formatted)

            return response.json()["access_token"]

        except requests.exceptions.RequestException as error:
            logging.error(f"Error refreshing access token: {error}")
            raise

    def create_playlist(self):

        """Creates a Spotify playlist and returns the ID """

        url = f"https://api.spotify.com/v1/users/{self.user_name}/playlists"
        header = {
            "Authorization": "Bearer " + self.access_token,
            "Content-Type": "application/json"
        }
        data = {
            "name": self.playlist_name,
            "public": False
        }

        try:
            response = requests.post(url, headers=header, json=data)
            response.raise_for_status()

            return response.json()["id"]

        except requests.exceptions.RequestException as error:
            logging.error(f"Error creating playlist: {error}")
            self.gui_ref.show_error_message(f"Please check your Username and try again")
            raise

    def search_songs_by_genre(self, genre):

        """Creates a list of 50 song titles by desired genre through Spotify search"""

        song_titles = []

        # Random offset used to get titles from next pages of search results
        search_url = f"https://api.spotify.com/v1/search?q=genre:{genre}&type=track&limit=50&offset={randint(1, 950)}"

        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()

            for item in response.json()["tracks"]["items"]:
                song_titles.append(item["name"])
            return song_titles

        except requests.exceptions.RequestException as error:
            logging.error(f"Error searching for songs: {error}")
            raise

    def add_songs(self, song_names, progress, label):

        """ Searches for songs in Spotify and add them to playlist """

        track_id_list = []
        all_tracks = song_names
        try:
            progress_increment = (100-progress["value"]) / len(all_tracks)
        except ZeroDivisionError:
            progress_increment = 1

        search_url = "https://api.spotify.com/v1/search?q="
        url = f"https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks"

        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Content-Type": "application/json"
        }

        for track in all_tracks:
            try:
                response = requests.get(url=search_url+track+"&type=track", headers=headers)
                response.raise_for_status()
                track_id_list.append(response.json()["tracks"]["items"][0]["uri"])
                self.gui_ref.update_progressbar(progress, label, progress_increment)

            except IndexError:
                logging.error(f"Track not found: {track}")
            except requests.exceptions.RequestException as error:
                logging.error(f"Error searching for song '{track}': {error}")
                raise

        try:
            response = requests.post(url, headers=headers, json={"uris": track_id_list})
            response.raise_for_status()

        except requests.exceptions.RequestException as error:
            logging.error(f"Error adding songs to playlist: {error}")
            self.gui_ref.show_error_message(f"No songs found! Please try with different parameters")
            raise
