# Hands_main.py
# 綜合應用專案：剪刀石頭布分析、影片匯出與統計報表
import cv2
import mediapipe as mp
import datetime
import os

def detect_rps(fingers):
    """根據手指狀態判斷剪刀石頭布（忽略大拇指，只看食指～小指）"""
    four = fingers[1:]
    if four == [0, 0, 0, 0]:
        return 'Rock', (255, 0, 0)
    elif four == [1, 1, 1, 1]:
        return 'Paper', (0, 255, 0)
    elif four == [1, 1, 0, 0]:
        return 'Scissors', (0, 0, 255)
    else:
        return 'Unknown', (255, 255, 255)

def fingers_up(pts):
    """判斷五根手指伸直狀態"""
    thumb = 1 if pts[4].x < pts[3].x else 0
    index = 1 if pts[8].y < pts[6].y else 0
    middle = 1 if pts[12].y < pts[10].y else 0
    ring = 1 if pts[16].y < pts[14].y else 0
    pinky = 1 if pts[20].y < pts[18].y else 0
    return [thumb, index, middle, ring, pinky]

def Hands_main():
    video_path = 'videos/rockPaperScissors.mp4'
    if not os.path.exists(video_path):
        print(f"警告：找不到影片檔案 {video_path}，請先將測試影片放置於 videos/ 目錄下。")
        return

    os.makedirs('outputs', exist_ok=True)

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    rps_stats = {'Rock': 0, 'Paper': 0, 'Scissors': 0, 'Unknown': 0}
    current_gesture = None
    gesture_duration_frames = 0

    # 提醒：VideoWriter 必須在迴圈外初始化，否則會產生損毀檔案
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('outputs/annotated.mp4', fourcc, fps, (854, 480))

    with mp_hands.Hands(max_num_hands=1) as hands:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            frame = cv2.resize(frame, (854, 480))
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )
                    pts = hand_landmarks.landmark
                    fingers = fingers_up(pts)
                    cv2.putText(frame, f"Fingers: {fingers}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    gesture, color = detect_rps(fingers)
                    cv2.putText(frame, gesture, (w // 2 - 100, h // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)

                    if gesture == current_gesture:
                        gesture_duration_frames += 1
                    else:
                        current_gesture = gesture
                        gesture_duration_frames = 1

                    rps_stats[gesture] += 1
                    duration_sec = gesture_duration_frames / fps
                    cv2.putText(frame, f"{gesture}: {duration_sec:.1f}s", (w - 300, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                current_gesture = None
                gesture_duration_frames = 0

            # 每幀寫入輸出影片
            out.write(frame)
            cv2.imshow('Hands Main', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    total_frames = sum(rps_stats.values())
    total_time = total_frames / fps if fps > 0 else 0

    with open('outputs/report.txt', 'w', encoding='utf-8') as f:
        f.write("來源影片: videos/rockPaperScissors.mp4\n")
        f.write(f"分析時間: {datetime.datetime.now()}\n")
        f.write(f"總分析幀數: {total_frames}\n")
        f.write(f"總時長: {total_time:.2f} 秒\n")
        f.write("各手勢統計:\n")
        for gesture, count in rps_stats.items():
            pct = (count / total_frames * 100) if total_frames > 0 else 0
            f.write(f"  {gesture}: {count} 幀 ({pct:.1f}%)\n")

    print("=== 手勢統計結果 ===")
    print("來源影片: videos/rockPaperScissors.mp4")
    print(f"分析時間: {datetime.datetime.now()}")
    print(f"總幀數: {total_frames}, 總時長: {total_time:.2f}s")
    for gesture, count in rps_stats.items():
        pct = (count / total_frames * 100) if total_frames > 0 else 0
        print(f"  {gesture}: {count} 幀 ({pct:.1f}%)")

if __name__ == '__main__':
    Hands_main()
