"""YouTube 影片下載輔助腳本。
支援透過命令列直接下載最高畫質影片並自動合併影音至指定目錄。
"""

import argparse
import os
import sys

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = None

import yt_dlp


def download(url: str, output_dir: str = 'videos') -> str:
    """下載 YouTube 影片至目標目錄。

    Args:
        url: YouTube 影片 URL。
        output_dir: 儲存目錄，預設為 'videos'。

    Returns:
        str: 下載後的檔案完整路徑。
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': False,
        'noplaylist': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

    if FFMPEG_PATH:
        ydl_opts['ffmpeg_location'] = FFMPEG_PATH

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
        return filepath


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='下載 YouTube 影片工具')
    parser.add_argument('url', type=str, help='YouTube 影片網址')
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='videos',
        help='下載儲存目錄（預設：videos）'
    )

    args = parser.parse_args()
    try:
        saved_path = download(args.url, args.output_dir)
        print(f"\n[SUCCESS] 影片已成功下載至: {saved_path}")
    except Exception as e:
        print(f"\n[ERROR] 下載失敗: {e}", file=sys.stderr)
        sys.exit(1)

