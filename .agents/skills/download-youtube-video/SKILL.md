---
name: download-youtube-video
description: >-
  Download YouTube videos with maximum quality and auto-merged audio/video into a specified local directory (defaulting to videos/). Use when the user requests downloading a YouTube video, extracting video files from a YouTube URL, or saving YouTube media locally.
---

# Download YouTube Video Skill

本技能提供標準且自動化的流程，利用專案內建的 `uv` 環境、`yt-dlp` 及 `imageio-ffmpeg`，將 YouTube 影片自動下載並合併最高畫質影音至指定本機資料夾（預設為 `videos/`）。

---

## 執行工作流程 (Workflow)

當收到使用者要求「下載 YouTube 影片」或提供 YouTube 網址要求存檔時，請按以下步驟執行：

### 步驟 1：確認目標 URL 與輸出目錄
- 取得使用者提供的 YouTube URL（例如 `https://www.youtube.com/watch?v=...`）。
- 若使用者未指定儲存目錄，預設儲存於專案根目錄下的 `videos/`。

### 步驟 2：執行下載指令
使用專案的輔助腳本 [download_cli.py](./scripts/download_cli.py) 進行下載：

```bash
uv run python .agents/skills/download-youtube-video/scripts/download_cli.py "<YOUTUBE_URL>" --output-dir "<OUTPUT_DIR>"
```

**範例**：
```bash
uv run python .agents/skills/download-youtube-video/scripts/download_cli.py "https://www.youtube.com/watch?v=jKrt3aaQLJk" --output-dir "videos"
```

### 步驟 3：在 Python 程式碼中呼叫（替代方案）
若需要在其他 Python 模組內整合下載功能，可直接匯入 [play_youtube.py](file:///d:/Course/20260912/mediapipe_hands/play_youtube.py) 的 `download_video` 函式：

```python
from play_youtube import download_video

# 下載影片至指定目錄（預設為 'videos'）
file_path = download_video("https://www.youtube.com/watch?v=jKrt3aaQLJk", output_dir="videos")
print(f"下載完成: {file_path}")
```

---

## 常見問題與注意事項

1. **影音合併問題**：
   - 專案依賴已內建 `imageio-ffmpeg`，腳本會自動抓取虛擬環境中的 FFmpeg 執行檔注入給 `yt-dlp`，不需在 Windows 系統手動安裝 FFmpeg。
2. **目錄自動建立**：
   - 目標資料夾若不存在會自動建立（`os.makedirs(output_dir, exist_ok=True)`）。
3. **重複下載**：
   - `yt-dlp` 會自動比對檔案是否存在，若已存在相同檔名且完整的檔案將自動略過下載。

