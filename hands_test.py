# hands_test.py
# 手部 21 個點靜態偵測
import cv2
import mediapipe as mp

# 初始化 MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# 讀取本地端靜態圖片
image = cv2.imread('hand_test.png')
if image is not None:
    h, w, _ = image.shape

    # 轉為 RGB 格式送入模型
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_image)
    print(results.multi_hand_landmarks)  # 印出結果以檢查是否有偵測到手部

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 1. 繪製官方標準骨架連線
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 2. 手動還原第 8 點 (食指尖) 與第 4 點 (大拇指尖) 像素座標並放大標註
            pts = hand_landmarks.landmark
            cx8, cy8 = int(pts[8].x * w), int(pts[8].y * h)
            cx4, cy4 = int(pts[4].x * w), int(pts[4].y * h)

            cv2.circle(image, (cx8, cy8), 10, (0, 0, 255), -1)  # 紅色標記食指
            cv2.circle(image, (cx4, cy4), 10, (0, 255, 0), -1)  # 綠色標記大拇指

    cv2.imshow('Static Hand Test', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("請確認當前目錄是否有 hand_test.png 圖片")
