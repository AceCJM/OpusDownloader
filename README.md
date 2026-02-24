# OpusDownloader

A Python tool to download YouTube videos as high-quality Opus audio files with embedded thumbnails and metadata.

## Features

- Download individual YouTube videos or entire playlists
- Convert audio to Opus format (lossless quality)
- Automatically embed video thumbnails as album art
- Include metadata (title, artist, album, date, description)
- Crop thumbnails to square format for better display

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)

### Install FFmpeg

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**On macOS:**
```bash
brew install ffmpeg
```

**On Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Install the Package

```bash
git clone <your-repo-url>
cd OpusDownloader
pip install .
```

For development:
```bash
pip install -e .
```

## Usage

### Download a Single Video

```bash
opusdownloader -s "https://www.youtube.com/watch?v=VIDEO_ID" -o /path/to/output/
```

### Download a Playlist

```bash
opusdownloader -p "https://www.youtube.com/playlist?list=PLAYLIST_ID" -o /path/to/output/
```

### Options

- `-s, --single URL`: Download a single video
- `-p, --playlist URL`: Download all videos in a playlist
- `-o, --output DIR`: Output directory (default: current directory)
- `--help`: Show help message

## Examples

```bash
# Download a single video to the current directory
opusdownloader -s "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download a playlist to a specific folder
opusdownloader -p "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5G1G8jQGzq9j9j9j" -o ~/Music/
```

## Dependencies

- yt-dlp: For downloading and extracting audio
- mutagen: For embedding metadata in audio files
- pytube: For playlist handling
- pillow: For image processing
- requests: For downloading thumbnails

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Disclaimer

This tool is for personal use only. Respect YouTube's terms of service and copyright laws. The author is not responsible for misuse.