import sys, requests, base64, os
import yt_dlp, re
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
from pytube import Playlist
from PIL import Image
import argparse


def grab_thumb(url: str, output) -> str:
    videoId = get_video_id(url)
    url = f"http://img.youtube.com/vi/{videoId}/maxresdefault.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        thumbnailFileName = f"{output}{videoId}_thumb.jpg"
        with open(thumbnailFileName, "wb") as f:
            f.write(response.content)
        print("Thumbnail downloaded")
        return thumbnailFileName
    else:
        print("Failed to download thumbnail")
        return -1

def crop_thumb(filepath):
    img = Image.open(filepath)
    width, height = img.size
    # Assuming width > height, crop to square
    if width > height:
        left = (width - height) // 2
        top = 0
        right = left + height
        bottom = height
    else:
        # If height > width, but in this case it's not
        top = (height - width) // 2
        left = 0
        bottom = top + width
        right = width
    cropped_img = img.crop((left, top, right, bottom))
    cropped_img.save(filepath)
    print(f"Cropped thumbnail to square: {filepath}")


def download_opus(url: str, output):
    ydl_opts = {
        "format": "bestaudio/best",
        'embed-metadata': True,
        'add-metadata': True,
        'outtmpl': os.path.join(output, '%(title)s [%(id)s]'),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "opus",
                "preferredquality": "0",  # 0 is best
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        print(f"Downloaded: {filename}")
        return f"{filename}.opus", info

def embed_image_in_opus(audio_file_path, image_file_path, info):
    try:
        with open(image_file_path, 'rb') as f:
            image_data = f.read()

        cover_art = Picture()
        cover_art.data = image_data
        cover_art.type = 3 

        encoded_picture = base64.b64encode(cover_art.write()).decode('ascii')

        audio = OggOpus(audio_file_path)
        audio['metadata_block_picture'] = encoded_picture
        audio['title'] = info.get('title', '')
        audio['artist'] = info.get('uploader', '')
        audio['album'] = info.get('album', '')
        audio['date'] = str(info.get('upload_date', ''))
        audio['description'] = info.get('description', '')
        audio.save()
        
        print(f"Successfully embedded metadata and image into {audio_file_path}")

    except FileNotFoundError:
        print(f"Error: Make sure files '{audio_file_path}' and '{image_file_path}' exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_video_id(url):
    youtube_regex = r'v=([^&]+)'
    match = re.search(youtube_regex, url)
    if match: return match.group(1)
    else: return None

def main(url, output="./"):
    filename, info = download_opus(url, output)
    thumbFilename = grab_thumb(url, output)
    crop_thumb(thumbFilename)
    embed_image_in_opus(filename, thumbFilename, info)
    if os.path.exists(thumbFilename):
        os.remove(thumbFilename)
        print(f"Deleted thumbnail file {thumbFilename}")

def cli():
    parser = argparse.ArgumentParser(description="Download YouTube videos as Opus audio with embedded thumbnails.")
    parser.add_argument('-s', '--single', type=str, help='Download a single video from URL')
    parser.add_argument('-p', '--playlist', type=str, help='Download all videos from playlist URL')
    parser.add_argument('-o', '--output', type=str, default='./', help='Output directory (default: ./)')
    
    args = parser.parse_args()
    
    if args.single:
        main(args.single, args.output)
    elif args.playlist:
        yt_play = Playlist(args.playlist)
        print(f"Downloading {len(yt_play.video_urls)} videos")
        for video in yt_play.videos:
            main(video.watch_url, args.output)
    else:
        parser.print_help()

if __name__ == '__main__':
    cli()