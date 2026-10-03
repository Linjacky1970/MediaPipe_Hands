# hands_gesture.py
# 手指伸直判斷與數字手勢辨識
import cv2
import mediapipe as mp
import play_youtube as yt

url = 'https://www.youtube.com/watch?v=nE4kuhO0l3E&t=22s'
stream_url = yt.play(url, download=False)
cap = cv2.VideoCapture(stream_url)

hands = mp.solutions.hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

def fingers_up(pts):
    """回傳 [大拇指, 食指, 中指, 無名指, 小指] 是否伸直的布林串列"""
    fingers = []
    # 大拇指：以 X 座標判斷（適用右手）
    if pts[4].x < pts[3].x:
        fingers.append(1)
    else:
        fingers.append(0)
    # 其餘四指：指尖 Y < PIP Y 視為伸直
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if pts[tip].y < pts[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

def count_to_gesture(fingers):
    """依伸直的手指組合，回傳數字手勢 0～5"""
    total = sum(fingers)
    if fingers == [0, 1, 0, 0, 0]:
        return 1
    if fingers == [0, 1, 1, 0, 0]:
        return 2
    if fingers == [0, 1, 1, 1, 0]:
        return 3
    if fingers == [0, 1, 1, 1, 1]:
        return 4
    if total == 5:
        return 5
    return 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (854, 480))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame, hand_landmarks,
                mp.solutions.hands.HAND_CONNECTIONS)
            pts = hand_landmarks.landmark
            fingers = fingers_up(pts)
            gesture = count_to_gesture(fingers)
            cv2.putText(frame, f"Fingers: {fingers}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"Gesture: {gesture}", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.imshow('Hand Gesture', frame)
    if cv2.waitKey(20) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
