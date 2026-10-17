import os
import threading
import cv2
import yt_dlp

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = None


def play(url, download=False, output_dir='videos'):
    """解析 YouTube 串流並回傳影片 URL，若 download=True 則下載至本機目錄。

    Args:
        url (str): YouTube 影片網址。
        download (bool): 是否下載影片，預設為 False。
        output_dir (str): 當 download=True 時的儲存目錄，預設為 'videos'。

    Returns:
        str: 解析後的影片串流 URL 或本機下載檔案路徑。
    """
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }

    # 若環境有提供 ffmpeg，指定給 yt-dlp 使用以支援影音自動合併
    if FFMPEG_PATH:
        ydl_opts['ffmpeg_location'] = FFMPEG_PATH

    if download:
        os.makedirs(output_dir, exist_ok=True)
        # 設定下載模板：儲存到 output_dir，保留影片標題與副檔名
        ydl_opts['outtmpl'] = os.path.join(output_dir, '%(title)s.%(ext)s')

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=download)
        if download:
            # 回傳本機下載檔案路徑
            filepath = ydl.prepare_filename(info)
            return filepath
        else:
            # 回傳串流 URL
            stream_url = info.get('url') or info.get('formats')[-1].get('url')
            return stream_url


def download_video(url, output_dir='videos'):
    """下載 YouTube 影片至指定的本機目錄（預設為 videos）。

    Args:
        url (str): YouTube 影片網址。
        output_dir (str): 下載儲存資料夾，預設為 'videos'。

    Returns:
        str: 下載完成之本機檔案路徑。
    """
    return play(url, download=True, output_dir=output_dir)


def play_and_download(url, output_dir='videos'):
    """取得影片串流網址並直接以 OpenCV 播放，同時在背景線程將影片下載至指定目錄。

    Args:
        url (str): YouTube 影片網址。
        output_dir (str): 影片下載目錄，預設為 'videos'。
    """
    print(f"正在解析影片串流與啟動背景下載：{url}")

    # 1. 在背景線程執行下載，不阻塞播放流程
    download_thread = threading.Thread(
        target=download_video,
        args=(url, output_dir),
        daemon=True
    )
    download_thread.start()
    print(f"背景下載任務已啟動，目標目錄: {output_dir}")

    # 2. 取得串流網址
    stream_url = play(url, download=False)
    if not stream_url:
        print("無法取得影片串流網址！")
        return

    print("已成功取得串流網址，開始播放影片（按 ESC 鍵離開）...")

    # 3. 使用 OpenCV 播放串流
    cap = cv2.VideoCapture(stream_url)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    delay = max(1, int(1000 / fps))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("影片播放結束或無法讀取影格。")
            break

        # 縮放至 854x480 (480p)
        frame = cv2.resize(frame, (854, 480))
        cv2.imshow('YouTube Player', frame)

        # 按 ESC (鍵碼 27) 或 'q' 鍵離開
        key = cv2.waitKey(delay) & 0xFF
        if key == 27 or key == ord('q'):
            print("使用者按下結束鍵，停止播放。")
            break

    cap.release()
    cv2.destroyAllWindows()

    # 4. 若播放結束時背景下載仍在進行，可等待其完成
    if download_thread.is_alive():
        print("影片播放已結束，正在等待背景下載完成...")
        download_thread.join()
        print("影片下載完成！")
    else:
        print("背景下載已完成。")


if __name__ == '__main__':
    # 測試區塊：取得串流直接播放，同時背景下載到 videos 目錄
    test_url = 'https://www.youtube.com/watch?v=jKrt3aaQLJk'
    play_and_download(test_url, output_dir='videos')
