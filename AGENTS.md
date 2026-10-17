# AGENTS.md — 專案開發規範與 AI 代理指南

本文件為 AI 編程代理（Agents）提供 `mediapipe_hands` 專案的架構背景、環境配置與程式撰寫規範。

## 1. 專案目標與架構

本專案為電腦視覺手部關鍵點追蹤與手勢辨識教材實作，包含四個遞進階段：

1. **第 1 節 — 靜態手部 21 點偵測 (`hands_test.py`)**
   - 讀取 `hand_test.png`。
   - 初始化 `mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=1)`。
   - 將 BGR 轉為 RGB 後送入 `hands.process()`。
   - 繪製 `HAND_CONNECTIONS` 官方骨架，並將第 8 點（食指尖）畫紅色實心圓 `(0, 0, 255)`、第 4 點（大拇指尖）畫綠色實心圓 `(0, 255, 0)`，半徑皆為 `10`。
2. **第 2 節 — YouTube 串流手部動態偵測 (`play_youtube.py`, `hands_detect.py`)**
   - `play_youtube.py`：定義 `play(url, download=False)`，透過 `yt_dlp.YoutubeDL`（參數 `format='bestvideo+bestaudio/best'`, `quiet=True`, `noplaylist=True`）解析並回傳影片串流 URL。
   - `hands_detect.py`：匯入 `play_youtube as yt` 讀取串流（預設測試網址：`https://www.youtube.com/watch?v=nE4kuhO0l3E&t=22s`），逐幀 `cv2.resize(frame, (854, 480))`，繪製骨架與第 8、4 點標記，按 `ESC` (`27`) 離開。
3. **第 3 節 — 手指伸直判斷與數字手勢辨識 (`hands_gesture.py`)**
   - `fingers_up(pts)`：輸入 21 個關鍵點 `pts`，回傳 `[大拇指, 食指, 中指, 無名指, 小指]` 的伸直狀態串列（`1` 伸直、`0` 彎曲）。
     - 大拇指：`pts[4].x < pts[3].x` 為 `1`，否則 `0`。
     - 其餘四指 `[8, 12, 16, 20]` 與 PIP 關節 `[6, 10, 14, 18]` 比較：`pts[tip].y < pts[pip].y` 為 `1`，否則 `0`。
   - `count_to_gesture(fingers)`：依手指狀態對應數字手勢 `0~5`（`[0,1,0,0,0]->1`, `[0,1,1,0,0]->2`, `[0,1,1,1,0]->3`, `[0,1,1,1,1]->4`, `sum==5->5`, 其他 `->0`）。
4. **第 4 節 — 綜合應用專案：剪刀石頭布分析 (`Hands_main.py`)**
   - 讀取 `videos/rockPaperScissors.mp4`，逐幀縮放至 `(854, 480)`。
   - `detect_rps(fingers)`：忽略大拇指（只看 `fingers[1:]`），判斷 `'Rock'` (`[0,0,0,0]`, 藍色 `(255,0,0)`)、`'Paper'` (`[1,1,1,1]`, 綠色 `(0,255,0)`)、`'Scissors'` (`[1,1,0,0]`, 紅色 `(0,0,255)`) 或 `'Unknown'` (白色 `(255,255,255)`)。
   - 累計各手勢總幀數 `rps_stats` 與目前手勢持續時間（秒），注意未偵測到手之影格不計入任何手勢。
   - 使用 `cv2.VideoWriter`（`mp4v` 編碼，尺寸 `(854, 480)`，**必須在迴圈外初始化**）匯出 `outputs/annotated.mp4`。
   - 結束後輸出統計報告至 `outputs/report.txt` 並印出於終端機。

---

## 2. 環境與套件管理規範 (`uv`)

- **套件管理工具**：一律使用 `uv` 管理虛擬環境與套件。
- **Python 版本**：由於 `mediapipe==0.10.9` 官方 wheel 支援限制，虛擬環境應使用 **Python 3.10 或 3.11**（優先使用 `3.11`）。
- **核心相依套件**：
  - `mediapipe==0.10.9`
  - `opencv-python`
  - `numpy`
  - `yt-dlp`
- **執行指令**：使用 `uv run python <script.py>` 執行程式。

---

## 3. 程式碼風格與注意事項

1. **中文註解與可讀性**：教材要求程式碼具備清楚的繁體中文註解與 docstring，修改或新增程式碼時請保留或補齊繁體中文說明。
2. **色彩空間轉換**：OpenCV 讀取影像預設為 `BGR`，送入 `hands.process()` 前必須使用 `cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)` 轉換為 `RGB`；繪圖則直接在原 `BGR` 影像上進行。
3. **座標還原**：MediaPipe 輸出的 `landmark.x` 與 `landmark.y` 為 `[0.0, 1.0]` 歸一化座標，繪製 OpenCV 圖形前須乘以影像寬高 `int(pt.x * w), int(pt.y * h)`。
4. **影片匯出安全檢查**：
   - 寫入 `outputs/annotated.mp4` 或 `outputs/report.txt` 前，請確保 `outputs/` 目錄已存在（例如 `os.makedirs('outputs', exist_ok=True)`）。
   - `cv2.VideoWriter` 嚴禁放在 `while` 迴圈內初始化，且結束時必須呼叫 `out.release()`。

