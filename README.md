# MediaPipe Hands 手部追蹤與手勢分析專案

## 專案簡介

本專案使用 **Python + OpenCV + MediaPipe Hands** 實作高精度的手部 21 個 3D 關鍵點（Landmarks）即時偵測與手勢辨識，涵蓋從基礎靜態影像偵測、YouTube 串流動態追蹤、數字手勢（0～5）辨識，到綜合應用分析專案（分析 `videos/rockPaperScissors.mp4` 影片中的剪刀、石頭、布手勢，並匯出標註影片與統計報告）。

---

## 專案結構與章節內容

```text
mediapipe_hands/
├── hand_test.png              # 第1節：靜態手部測試圖片
├── hands_test.py              # 第1節：手部 21 個點靜態偵測與特定關鍵點標記
├── play_youtube.py            # 第2節：封裝 yt-dlp 解析 YouTube 影片串流網址模組
├── hands_detect.py            # 第2節：讀取 YouTube 串流進行手部動態骨架追蹤
├── hands_gesture.py           # 第3節：手指伸直判斷與數字手勢（0～5）即時辨識
├── Hands_main.py              # 第4節：綜合應用專案（剪刀石頭布辨識、時長統計與影片匯出）
├── videos/
│   └── rockPaperScissors.mp4  # 第4節：剪刀石頭布測試影片
├── outputs/
│   ├── annotated.mp4          # 匯出之標註骨架與手勢結果影片
│   └── report.txt             # 手勢出現幀數、時長與百分比統計報告
├── pyproject.toml             # uv 專案設定與套件相依性定義
├── AGENTS.md                  # AI 代理開發規範與專案指南
└── README.md                  # 專案說明文件
```

---

## 環境安裝

本專案使用 [uv](https://docs.astral.sh/uv/) 進行 Python 虛擬環境與套件管理（注意：`mediapipe==0.10.9` 建議搭配 Python 3.10 或 3.11 環境）。

```bash
# 1. 建立虛擬環境並安裝專案相依套件
uv venv --python 3.11
uv pip install mediapipe==0.10.9 opencv-python numpy yt-dlp

# 若使用 pyproject.toml 同步環境：
uv sync
```

---

## 使用方式

### 第 1 節：手部 21 個點靜態偵測 (`hands_test.py`)
讀取本機圖片 `hand_test.png`，繪製官方骨架連線，並將食指尖（第 8 點）標記為紅點、大拇指尖（第 4 點）標記為綠點：
```bash
uv run python hands_test.py
```
> 按任意鍵關閉預覽視窗。

### 第 2 節：YouTube 串流手部動態偵測 (`play_youtube.py` & `hands_detect.py`)
先透過 `play_youtube.py` 解析 YouTube 串流 URL，再以 OpenCV 逐幀讀取（縮放至 `854x480`）並即時繪製手部關鍵點：
```bash
# 測試解析 YouTube 串流網址
uv run python play_youtube.py

# 執行 YouTube 串流手部動態追蹤
uv run python hands_detect.py
```
> 按 `ESC` 鍵離開視窗。

### 第 3 節：手指伸直判斷與數字手勢辨識 (`hands_gesture.py`)
即時判斷五根手指伸直狀態 `[大拇指, 食指, 中指, 無名指, 小指]`，並在畫面左上角顯示 `Fingers: [...]` 與數字手勢 `Gesture: 0~5`：
```bash
uv run python hands_gesture.py
```
> 按 `ESC` 鍵離開視窗。

### 第 4 節：綜合應用專案 — 剪刀石頭布手勢分析 (`Hands_main.py`)
分析 `videos/rockPaperScissors.mp4` 影片中的手勢（`Rock` / `Paper` / `Scissors` / `Unknown`），即時顯示手勢名稱與持續秒數，並匯出標註影片與統計報告：
```bash
uv run python Hands_main.py
```
> 按 `q` 鍵可提前結束分析。

---

## 輸出檔案說明

執行 `Hands_main.py` 後，會在 `outputs/` 目錄下產生以下兩個檔案：

1. **`outputs/annotated.mp4`**：
   - 畫面上標註 MediaPipe 手部骨架連線、左上角顯示五指狀態 `Fingers: [...]`、畫面中央以不同顏色大字顯示目前手勢（`Rock` 藍色、`Paper` 綠色、`Scissors` 紅色、`Unknown` 白色）、右上角顯示該手勢持續秒數。
2. **`outputs/report.txt`**：
   - 記錄來源影片、分析時間、總分析幀數、總時長，以及各手勢出現幀數與百分比。內容範例如下：

```text
來源影片: videos/rockPaperScissors.mp4
分析時間: 2026-09-15 15:37:34.974682
總分析幀數: 1376
總時長: 22.93 秒
各手勢統計:
  Rock: 671 幀 (48.8%)
  Paper: 307 幀 (22.3%)
  Scissors: 396 幀 (28.8%)
  Unknown: 2 幀 (0.1%)
```

---

## 手勢判斷邏輯說明

### 1. MediaPipe Hands 21 個關鍵點編號

```text
        8   12  16  20
        |   |   |   |
        7   11  15  19
    4   |   |   |   |
    |   6   10  14  18
    3   |   |   |   |
    |   5---9---13--17
    2    \         /
     \    \       /
      1    \     /
       \    \   /
        0 ---+
```

| 手指 | 指尖 (TIP) 編號 | 比較關節編號 | 判斷方式（MediaPipe Y 軸由上往下遞增 0.0 → 1.0） |
| :--- | :---: | :---: | :--- |
| **大拇指 (Thumb)** | `4` | `3` (IP) | 水平方向比較 X 座標：`pts[4].x < pts[3].x` 視為伸直（適用右手） |
| **食指 (Index)** | `8` | `6` (PIP) | 垂直方向比較 Y 座標：`pts[8].y < pts[6].y` 視為向上伸直 |
| **中指 (Middle)** | `12` | `10` (PIP) | 垂直方向比較 Y 座標：`pts[12].y < pts[10].y` 視為向上伸直 |
| **無名指 (Ring)** | `16` | `14` (PIP) | 垂直方向比較 Y 座標：`pts[16].y < pts[14].y` 視為向上伸直 |
| **小指 (Pinky)** | `20` | `18` (PIP) | 垂直方向比較 Y 座標：`pts[20].y < pts[18].y` 視為向上伸直 |

### 2. 數字手勢對應表（`hands_gesture.py`）

| 數字手勢 | `fingers` 狀態 `[拇指, 食指, 中指, 無名指, 小指]` | 伸直的手指 |
| :---: | :---: | :--- |
| **0** | 其他組合（如 `[0, 0, 0, 0, 0]`） | 無（握拳） |
| **1** | `[0, 1, 0, 0, 0]` | 食指 |
| **2** | `[0, 1, 1, 0, 0]` | 食指 + 中指 |
| **3** | `[0, 1, 1, 1, 0]` | 食指 + 中指 + 無名指 |
| **4** | `[0, 1, 1, 1, 1]` | 食指 + 中指 + 無名指 + 小指（大拇指彎曲） |
| **5** | `[1, 1, 1, 1, 1]`（總和為 5） | 五指全伸 |

### 3. 剪刀石頭布判斷邏輯（`Hands_main.py`）

在 `detect_rps(fingers)` 中，**忽略大拇指，只取後四指 `fingers[1:]`（食指、中指、無名指、小指）**：

- **`[0, 0, 0, 0]`** → `'Rock'`（石頭，藍色 `(255, 0, 0)`）
- **`[1, 1, 1, 1]`** → `'Paper'`（布，綠色 `(0, 255, 0)`）
- **`[1, 1, 0, 0]`** → `'Scissors'`（剪刀，紅色 `(0, 0, 255)`）
- **其他組合** → `'Unknown'`（未知，白色 `(255, 255, 255)`）

> **💡 為什麼要忽略大拇指？**
> 1. 玩家在出「石頭（握拳）」或「剪刀」時，大拇指常自然擺放在側面、斜上方或微伸，容易導致 X 座標比較（`pts[4].x < pts[3].x`）在 `0` 與 `1` 之間跳動。
> 2. 大拇指的 X 座標判斷受手掌旋轉角度與左右手方向影響極大；而剪刀、石頭、布僅憑其餘四指（食指～小指）的伸直與彎曲組合即可完全且穩定地區分，忽略大拇指能大幅降低誤判為 `Unknown` 的機率。

---

## 常見問題 (FAQ)

### Q1：無法讀取影片或畫面直接結束？
- **本機影片**：請確認 `videos/rockPaperScissors.mp4` 檔案存在且路徑正確，並確保執行目錄位於專案根目錄。
- **YouTube 串流**：若 `yt-dlp` 無法解析網址，請執行 `uv pip install -U yt-dlp` 更新至最新版本，並確認網路連線正常。

### Q2：手勢判斷出現偏誤（例如大拇指方向相反或頻繁跳出 Unknown）？
- 大拇指判斷條件 `pts[4].x < pts[3].x` 預設適用於畫面中手心朝向鏡頭或特定方向的右手；若使用左手或手背朝向鏡頭，X 軸方向會相反。
- 在剪刀石頭布專案中已透過 `fingers[1:]` 忽略大拇指來解決此問題；若四指判斷仍有偏誤，請確保手部在畫面中主要呈現直立向上姿勢（因為四指是以 Y 座標 `tip.y < pip.y` 判斷）。

### Q3：輸出的 `outputs/annotated.mp4` 影片損毀或無法播放？
- **關鍵原因 1**：`cv2.VideoWriter` **必須在 `while` 迴圈外初始化**！若放在迴圈內，每一幀都會重新覆寫建立檔案，導致最終產出損毀檔案。
- **關鍵原因 2**：寫入 `out.write(frame)` 的影像尺寸必須與初始化 `VideoWriter` 時設定的 `(854, 480)` 完全一致，且程式結束前務必呼叫 `out.release()`，並確認 `outputs/` 資料夾已建立。

