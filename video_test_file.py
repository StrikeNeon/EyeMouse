import cv2
from hand_tracker import hand_tracker


cap = cv2.VideoCapture(0)
h_tracker = hand_tracker(debug_draw=True)
while True:
    ret, frame = cap.read()

    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hands = h_tracker.find_hands(rgb_image)
    if hands:
        hand_data = h_tracker.get_landmark_data(rgb_image, hands)
        frame = h_tracker.draw_debug_landmarks(frame, hands)
        print(hand_data)

    cv2.imshow("image", frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
