import spotipy, os, configparser, json, pprint
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from time import sleep


def main():
    here = os.path.realpath(__file__).replace(os.path.realpath(__file__).split("\\")[-1], "")
    config_path = f"{here}user_details.ini"
    spotipy_user_key = 'SPP_USER_ID'
    spotipy_id_key = 'SPP_USER_SECRET'

    # Read configuration (improve security for credentials)
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
    except FileNotFoundError:
        print("Config file not found. Please create it.")
        return

    # Get user credentials (improve security)
    user_name = config.get('DEFAULT', spotipy_user_key, fallback='')
    user_secret = config.get('DEFAULT', spotipy_id_key, fallback='')

    if not user_name or not user_secret:
        print("Missing credentials in config file. Please fill them out.")
        return

    scope = 'user-library-read,user-read-playback-state,user-library-modify'
    http_link = "http://127.0.0.1:9090"

    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=user_name,
                                                       client_secret=user_secret,
                                                       redirect_uri=http_link,
                                                       scope=scope))
    except Exception as e:
        print(f"Error during Spotify authentication: {e}")
        return

    while True:
        try:
            current_device = sp.devices()['devices']
            if current_device:
                # Check for active device playing before calling currently_playing
                info = sp.currently_playing(additional_types='track')
                if info and info['item']:
                    song_id = info['item']['id']
                    isLiked = sp.current_user_saved_tracks_contains(tracks=[song_id])
                    if isLiked == [True] and info['is_playing'] == True:
                        sp.next_track(device_id=None)
                        print(f"Skipped {info['item']['name']}.")
        except Exception as e:
            # Handle empty response or other exceptions
            if 'Expecting value' in str(e):
                print("An empty response was received from Spotify. No song currently playing.")
            else:
                print(f"Error during like logic: {e}")

        sleep(2)


if __name__ == "__main__":
    main()
