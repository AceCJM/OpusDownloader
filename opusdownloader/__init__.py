import sys, requests, base64, os
import yt_dlp, re
from mutagen.oggopus import OggOpus
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.flac import Picture
from pytube import Playlist
from PIL import Image
import argparse


def grab_thumb(url: str, output) -> str:
    videoId = get_video_id(url)
    url = f"http://img.youtube.com/vi/{videoId}/maxresdefault.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        image_file_path = f"{output}{videoId}_thumb.jpg"
        with open(image_file_path, "wb") as f:
            f.write(response.content)
        print("Thumbnail downloaded")
        return image_file_path
    else:
        print("Failed to download thumbnail")
        return -1


def crop_thumb(image_file_path):
    image_file = Image.open(image_file_path)
    width, height = image_file.size
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
    cropped_img = image_file.crop((left, top, right, bottom))
    cropped_img.save(image_file_path)
    print(f"Cropped thumbnail to square: {image_file_path}")


def download(url: str, output, format="best"):
    ydl_opts = {
        "format": "bestaudio/best",
        "embed-metadata": True,
        "add-metadata": True,
        "continuedl": False,
        "outtmpl": os.path.join(output, "%(title)s [%(id)s]"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": format,
                "preferredquality": "0",  # 0 is best
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        print(f"Downloaded: {filename}")
        return f"{filename}.{format}", info


def embed_image_in_file(audio_file_path, image_file_path, info):
    try:
        with open(image_file_path, "rb") as f:
            image_data = f.read()

        cover_art = Picture()
        cover_art.data = image_data
        cover_art.type = 3

        encoded_picture = base64.b64encode(cover_art.write()).decode("ascii")
        if audio_file_path.endswith(".mp3"):
            # Embed image into MP3 file using mutagen
            audio_file = MP3(audio_file_path, ID3=ID3)
            try:
                audio_file.add_tags()
            except error:
                pass
            audio_file.tags.add(
                APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,
                    desc="Cover",
                    data=image_data,
                ),
                # Add metadata tags
                ID3.TIT2(encoding=3, text=info.get("title", "")),
                ID3.TPE1(encoding=3, text=info.get("uploader", "")),
                ID3.TALB(encoding=3, text=info.get("album", "")),
                ID3.TDRC(encoding=3, text=str(info.get("upload_date", ""))),
                ID3.COMM(encoding=3, lang="eng", desc="Description", text=info.get("description", ""))
            )
            audio_file.save()


            
        elif audio_file_path.endswith(".opus"):
            audio_file = OggOpus(audio_file_path)
            audio_file["metadata_block_picture"] = encoded_picture
            audio_file["title"] = info.get("title", "")
            audio_file["artist"] = info.get("uploader", "")
            audio_file["album"] = info.get("album", "")
            audio_file["date"] = str(info.get("upload_date", ""))
            audio_file["description"] = info.get("description", "")
            audio_file.save()
        else:
            print(
                f"Unsupported format for embedding metadata: {audio_file_path}. Skipping metadata embedding."
            )
            return

        print(f"Successfully embedded metadata and image into {audio_file_path}")

    except FileNotFoundError:
        print(
            f"Error: Make sure files '{audio_file_path}' and '{image_file_path}' exist."
        )
    except Exception as e:
        print(f"An error occurred: {e}")


def get_video_id(url):
    youtube_regex = r"v=([^&]+)"
    match = re.search(youtube_regex, url)
    if match:
        return match.group(1)
    else:
        return None


def main(url, output="./", format="best"):
    audio_file_path, info = download(url, output, format)
    image_file_path = grab_thumb(url, output)
    crop_thumb(image_file_path)
    embed_image_in_file(audio_file_path, image_file_path, info)
    if os.path.exists(image_file_path):
        os.remove(image_file_path)
        print(f"Deleted thumbnail file {image_file_path}")


def cli():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos as Opus audio with embedded thumbnails."
    )
    parser.add_argument(
        "-s", "--single", type=str, help="Download a single video from URL"
    )
    parser.add_argument(
        "-p", "--playlist", type=str, help="Download all videos from playlist URL"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="./", help="Output directory (default: ./)"
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="best",
        help="Audio format (opus, flac, etc.) (default: best)",
    )
    parser.add_argument(
        "-l",
        "--listFormats",
        action="store_true",
        help="List available audio formats and exit",
    )

    args = parser.parse_args()

    if args.listFormats:
        print("Available audio formats:")
        print(
            "- best (default, auto-selects the best format)\n- aac\n- alac\n- flac\n- m4a\n- mp3\n- opus\n- vorbis\n- wav",
            "Metadata is only embedded in opus and mp3 formats due to mutagen limitations.",
        )
        return

    if args.single:
        main(args.single, args.output, args.format)
    elif args.playlist:
        yt_play = Playlist(args.playlist)
        print(f"Downloading {len(yt_play.video_urls)} videos")
        for video in yt_play.videos:
            main(video.watch_url, args.output, args.format)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
