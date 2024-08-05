import os
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

#for more security it is better to put these in to a file 

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def start(update, context):
    update.message.reply_text('Send me a Spotify playlist, album, or song link, and I will download the music for you.')

def get_spotify_track_info(url):
    try:
        if 'track' in url:
            track = sp.track(url)
            return [{'name': track['name'], 'artist': track['artists'][0]['name']}]
        elif 'album' in url:
            results = sp.album_tracks(url)
            tracks = [{'name': item['name'], 'artist': item['artists'][0]['name']} for item in results['items']]
            return tracks
        elif 'playlist' in url:
            results = sp.playlist_tracks(url)
            tracks = [{'name': item['track']['name'], 'artist': item['track']['artists'][0]['name']} for item in results['items']]
            return tracks
    except Exception as e:
        logger.error(f"Error fetching Spotify track info: {e}")
    return None

def download_track(track_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{track_name}", download=True)
        if result:
            return ydl.prepare_filename(result['entries'][0])
    return None

def handle_message(update, context):
    url = update.message.text
    update.message.reply_text('Processing your request, please wait...')
    
    tracks = get_spotify_track_info(url)
    if not tracks:
        update.message.reply_text('Invalid Spotify URL. Please provide a valid track, album, or playlist URL.')
        return
    
    for track in tracks:
        track_name = f"{track['name']} {track['artist']}"
        update.message.reply_text(f"Downloading {track_name}...")
        file_name = download_track(track_name)
        if file_name:
            update.message.reply_audio(audio=open(file_name, 'rb'))
            os.remove(file_name)
        else:
            update.message.reply_text(f"Failed to download {track_name}.")


updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler('start', start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
updater.idle()
