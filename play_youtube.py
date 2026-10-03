# play_youtube.py
# 使用 yt-dlp 解析 YouTube 串流 URL
import yt_dlp

def play(url, download=False):
    """解析 YouTube 串流並回傳影片 URL。
    Args:
        url (str): YouTube 影片網址。
        download (bool): 是否下載影片，預設為 False。
    Returns:
        str: 解析後的影片串流 URL。
    """
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=download)
        stream_url = info.get('url') or info.get('formats')[-1].get('url')
        return stream_url

if __name__ == '__main__':
    # 測試區塊：直接執行驗證
    test_url = 'https://www.youtube.com/watch?v=jKrt3aaQLJk'
    print("解析結果 URL:", play(test_url))
