# hands_detect.py
# 手部動態偵測（讀取 YouTube 串流）
import cv2
import mediapipe as mp
import numpy as np
import play_youtube as yt

url = 'https://www.youtube.com/watch?v=nE4kuhO0l3E&t=22s'  # youtube 影片
stream_url = yt.play(url, download=False)  # 取得影片串流 URL
cap = cv2.VideoCapture(stream_url)

# 初始化 MediaPipe Hands
hands = mp.solutions.hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (854, 480))  # 統一縮放為 480p 提高運算效能
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 1. 繪製官方標準骨架連線
            mp_draw.draw_landmarks(
                frame, hand_landmarks,
                mp.solutions.hands.HAND_CONNECTIONS
            )

            # 2. 手動還原第 8 點 (食指尖) 與第 4 點 (大拇指尖) 像素座標並放大標註
            pts = hand_landmarks.landmark
            cx8, cy8 = int(pts[8].x * w), int(pts[8].y * h)
            cx4, cy4 = int(pts[4].x * w), int(pts[4].y * h)

            cv2.circle(frame, (cx8, cy8), 10, (0, 0, 255), -1)  # 紅色標記食指
            cv2.circle(frame, (cx4, cy4), 10, (0, 255, 0), -1)  # 綠色標記大拇指

    cv2.imshow('hands points', frame)
    if cv2.waitKey(20) & 0xFF == 27:  # 按 ESC 鍵離開
        break

cap.release()
cv2.destroyAllWindows()
