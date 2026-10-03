# Rock-Paper-Scissors 手勢分析專案 (MediaPipe Hands)

本專案基於 **Google MediaPipe Hands** 與 **OpenCV**，實現從單幀 RGB 影像到連續視訊的手部 21 個 3D 關鍵點偵測、手指伸直狀態演算，並完成「剪刀、石頭、布」（Rock-Paper-Scissors）手勢識別、持續時間統計、標註影片匯出及分析報告生成。

---

## 目錄
- [專案簡介](#專案簡介)
- [專案結構](#專案結構)
- [環境安裝](#環境安裝)
- [使用方式](#使用方式)
- [手勢判斷邏輯說明](#手勢判斷邏輯說明)
  - [手部 21 個 3D 關鍵點拓撲圖](#手部-21-個-3d-關鍵點拓撲圖)
  - [手指伸直判定原理](#手指伸直判定原理)
  - [剪刀石頭布判定邏輯（為何忽略大拇指？）](#剪刀石頭布判定邏輯為何忽略大拇指)
- [輸出檔案說明](#輸出檔案說明)
  - [標註影片 (`outputs/annotated.mp4`)](#標註影片-outputsannotatedmp4)
  - [統計報告 (`outputs/report.txt`)](#統計報告-outputsreporttxt)
- [常見問題與排除 (FAQ)](#常見問題與排除-faq)

---

## 專案簡介

在電腦視覺領域中，手部追蹤常面臨**自我遮蔽（Occlusion）**以及**缺乏高對比特徵**等挑戰。MediaPipe Hands 透過輕量化的深度學習模型，僅憑單一鏡頭 RGB 畫面即可以毫秒級推算出單手或雙手的 21 個 3D 立體關節座標。

本專案提供四個階段的實作：
1. **第 1 節 (`hands_test.py`)**：靜態圖片手部 21 關鍵點偵測與特定指尖像素座標還原標註。
2. **第 2 節 (`hands_detect.py` + `play_youtube.py`)**：搭配 `yt-dlp` 解析串流，進行動態即時手部追蹤。
3. **第 3 節 (`hands_gesture.py`)**：幾何關節運算，辨識伸直手指數量與 0～5 數字手勢。
4. **第 4 節 (`Hands_main.py` / `main.py`)**：綜合應用專案，分析 `videos/rockPaperScissors.mp4`，繪製即時骨架、手勢與秒數，匯出 `annotated.mp4` 並輸出 `report.txt`。

---

## 專案結構

```text
MediaPipe_Hands/
├── .python-version             # Python 版本宣告 (3.11)
├── .gitignore                  # Git 忽略設定 (.venv, 暫存與影片檔)
├── README.md                   # 專案說明文件
├── Hands_main.py               # [主要程式] 綜合應用：猜拳辨識、影片匯出、報表生成
├── main.py                     # 進入點（直接呼叫 Hands_main.py）
├── hands_gesture.py            # [教學第 3 節] 手指伸直與 0~5 數字手勢辨識
├── hands_detect.py             # [教學第 2 節] YouTube 影片即時動態手部追蹤
├── play_youtube.py             # [教學第 2 節] 使用 yt-dlp 提取影片串流工具模組
├── hands_test.py               # [教學第 1 節] 單張圖片靜態 21 點偵測
├── videos/                     # 存放來源測試影片 (例: rockPaperScissors.mp4)
└── outputs/                    # 分析產出目錄 (annotated.mp4, report.txt)
```

---

## 環境安裝

本專案使用高效 Python 套件管理工具 **`uv`** 進行虛擬環境與套件管理。

> [!IMPORTANT]
> **版本限制說明**：
> - MediaPipe 官方套件建議搭配 **Python 3.10 ~ 3.11** 執行。
> - 本專案限定使用 `mediapipe==0.10.9`，以確保 `mp.solutions.hands` 與 `drawing_utils` API 的相容性與穩定度。

### 步驟 1：建立虛擬環境

```bash
# 建立 Python 3.11 虛擬環境
uv venv --python 3.11 .venv
```

### 步驟 2：啟用虛擬環境

- **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 步驟 3：安裝相依套件

```bash
uv pip install mediapipe==0.10.9 opencv-python numpy yt-dlp
```

---

## 使用方式

### 1. 執行剪刀石頭布綜合分析 (主要專案)

確保測試影片放置於 `videos/rockPaperScissors.mp4`：

```bash
python Hands_main.py
# 或
python main.py
```

- 畫面操作：
  - 視窗中央大字顯示當前手勢（藍色 **Rock** / 綠色 **Paper** / 紅色 **Scissors** / 白色 **Unknown**）。
  - 左上角顯示五指狀態串列 `Fingers: [拇指, 食指, 中指, 無名指, 小指]`。
  - 右上角顯示手勢持續秒數 `Gesture: X.Xs`。
  - 隨時按鍵盤 **`q`** 即可中途停止並產出報表。

### 2. 執行其他教學章節腳本

- **靜態單張照片偵測 (第 1 節)**：
  ```bash
  python hands_test.py
  ```
  *(請確保當前目錄有 `hand_test.png`，按任意鍵關閉視窗)*

- **YouTube 動態串流手部追蹤 (第 2 節)**：
  ```bash
  python hands_detect.py
  ```
  *(按 `ESC` 鍵離開)*

- **數字 0~5 手勢辨識 (第 3 節)**：
  ```bash
  python hands_gesture.py
  ```
  *(按 `ESC` 鍵離開)*

---

## 手勢判斷邏輯說明

### 手部 21 個 3D 關鍵點拓撲圖

MediaPipe Hands 推算的 21 個 Landmark 節點索引如下：

```text
       8. TIP          12. TIP         16. TIP         20. TIP
         |               |               |               |
       7. DIP          11. DIP         15. DIP         19. DIP
         |               |               |               |
       6. PIP          10. PIP         14. PIP         18. PIP
         \               |               |              /
          5. MCP ---- 9. MCP ---- 13. MCP --- 17. MCP
               \                         /
     4. TIP     \                       /
       |         \                     /
     3. IP        \                   /
       |           \                 /
     2. MCP         \               /
       |             \             /
     1. CMC ---------- 0. WRIST --
```

| 關節部位 | 關鍵點索引 | 關節部位 | 關鍵點索引 |
| :--- | :--- | :--- | :--- |
| **手腕 (WRIST)** | `0` | **中指 (MIDDLE)** | `9` (MCP), `10` (PIP), `11` (DIP), `12` (TIP) |
| **大拇指 (THUMB)** | `1` (CMC), `2` (MCP), `3` (IP), `4` (TIP) | **無名指 (RING)** | `13` (MCP), `14` (PIP), `15` (DIP), `16` (TIP) |
| **食指 (INDEX)** | `5` (MCP), `6` (PIP), `7` (DIP), `8` (TIP) | **小指 (PINKY)** | `17` (MCP), `18` (PIP), `19` (DIP), `20` (TIP) |

---

### 手指伸直判定原理

MediaPipe 影像歸一化座標系中：
- 畫面最頂端 $Y = 0.0$
- 畫面最底端 $Y = 1.0$
- **$Y$ 軸由上往下遞增**。

#### 1. 食指、中指、無名指、小指
手指向上伸直時，指尖（TIP）在畫面上方，關節（PIP）在下方：
$$\text{伸直條件：} \quad \text{pts}[\text{TIP}].y < \text{pts}[\text{PIP}].y \implies 1 \,(\text{伸直}) \quad \text{否則} \implies 0 \,(\text{彎曲})$$

- 食指：`pts[8].y < pts[6].y`
- 中指：`pts[12].y < pts[10].y`
- 無名指：`pts[16].y < pts[14].y`
- 小指：`pts[20].y < pts[18].y`

#### 2. 大拇指
大拇指運動方向主要為水平開合。以**右手**為例：
$$\text{大拇指伸直條件：} \quad \text{pts}[4].x < \text{pts}[3].x \implies 1 \,(\text{伸直}) \quad \text{否則} \implies 0 \,(\text{彎曲})$$

---

### 剪刀石頭布判定邏輯（為何忽略大拇指？）

#### ❓ 為什麼要忽略大拇指？
在現實日常的猜拳情境中：
1. **石頭（Rock）**：有人習慣將大拇指扣在四指外側，有人習慣包進拳頭內，拇指開合差異極大。
2. **剪刀（Scissors）**：部分文化或個人習慣比「食指 + 中指」兩指，亦有人習慣比「大拇指 + 食指」，甚至比兩指時大拇指翹起。
3. **布（Paper）**：有人五指緊繃張開，有人四指併攏大拇指微收。

因此，**忽略大拇指**，僅觀察**食指、中指、無名指、小指**（即 `four = fingers[1:]`），是辨識剪刀石頭布最簡約且魯棒（Robust）的方法！

#### 手勢判定對照表

| 手勢 | 四指狀態 `four = fingers[1:]` | 顏色 (BGR) | 說明 |
| :--- | :---: | :---: | :--- |
| **Rock (石頭)** | `[0, 0, 0, 0]` | 藍色 `(255, 0, 0)` | 食指、中指、無名指、小指皆彎曲 |
| **Paper (布)** | `[1, 1, 1, 1]` | 綠色 `(0, 255, 0)` | 四指皆伸直 |
| **Scissors (剪刀)** | `[1, 1, 0, 0]` | 紅色 `(0, 0, 255)` | 僅食指與中指伸直 |
| **Unknown** | 其他任意組合 | 白色 `(255, 255, 255)` | 無法辨識之手勢（例：單伸食指、蜘蛛人手勢等） |

---

## 輸出檔案說明

執行完畢後，結果自動儲存於 `outputs/` 目錄：

### 標註影片 (`outputs/annotated.mp4`)
- **影像格式**：MP4 (編碼器 `mp4v`)
- **解析度**：$854 \times 480$ (統一 480p 兼顧運算速度與畫質)
- **視覺呈現**：
  - 手部骨架線條與關節點（MediaPipe 官方繪圖工具標註）
  - 左上方五指伸直狀態標籤
  - 中央動態顯示手勢判定字樣（字體大小 2、線寬 4）
  - 右上方顯示手勢名稱與該手勢累積持續秒數

### 統計報告 (`outputs/report.txt`)
檔案內容記錄來源檔案、分析時間戳記、分析總幀數、時長以及各手勢出現的幀數與比例。

範例內容如下：
```text
來源影片: videos/rockPaperScissors.mp4
分析時間: 2026-09-15 15:37:34.974901
總分析幀數: 1376
總時長: 22.93 秒
各手勢統計:
  Rock: 671 幀 (48.8%)
  Paper: 307 幀 (22.3%)
  Scissors: 396 幀 (28.8%)
  Unknown: 2 幀 (0.1%)
```

終端機亦會同步印出相同統計結果。

---

## 常見問題與排除 (FAQ)

### Q1: 提示找不到影片或無法讀取影片 (`cap.read()` 回傳 False)？
- 請檢查 `videos/` 資料夾中是否存在 `rockPaperScissors.mp4`，注意大小寫需完全相符。
- 若使用 `play_youtube.py`，請確認網路連線正常，且 `yt-dlp` 為最新版本（YouTube 串流規則更新頻繁）。

### Q2: 輸出的影片 `outputs/annotated.mp4` 毀損、無法播放或大小為 0 位元組？
- **關鍵注意**：`cv2.VideoWriter` **必須在 `while` 迴圈外部初始化**。若放在迴圈內，每一幀都會重新建立檔案覆蓋，導致檔案毀損。
- 寫入幀尺寸必須與 `VideoWriter` 初始化設定的解析度完全一致（例如 `(854, 480)`）。
- 程式結束時必須正確呼叫 `out.release()` 與 `cap.release()` 釋放寫入緩衝區。

### Q3: 手勢辨識常出現抖動 (Flickering) 或 Unknown 誤判？
- **左右手相反**：大拇指 X 座標判定目前預設為右手（`pts[4].x < pts[3].x`），若是左手需改為 `pts[4].x > pts[3].x`。但剪刀石頭布判定已忽略拇指，不受左右手拇指開合影響。
- **手掌方向**：若手背朝向鏡頭、手部傾斜或水平出拳，指尖與關節在 Y 軸的相對位置可能失真。請維持手掌直立朝向攝影鏡頭。
- **動態模糊**：若影片快速揮動造成手部模糊，MediaPipe 信心度不足可能造成短暫遺漏（程式已設計未偵測到手時不計入任何手勢）。

### Q4: 安裝 `mediapipe` 時發生錯誤？
- MediaPipe 官方預編譯 wheel 僅支援 Python 3.8 ~ 3.11。請確認使用的環境為 Python 3.11（本專案已使用 `uv venv --python 3.11`）。
- Windows 環境請確認已安裝 Microsoft Visual C++ 2015-2022 Redistributable。
