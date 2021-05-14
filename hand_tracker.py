import cv2
import mediapipe
from numpy import ndarray


class hand_tracker():
    def __init__(self, debug_draw: bool = False, max_hands: int = 1, min_detection_confidence: float = 0.7, min_tracking_confidence: float = 0.5):
        self.mp_hands = mediapipe.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=max_hands,
                                         min_detection_confidence=min_detection_confidence,
                                         min_tracking_confidence=min_tracking_confidence)
        if debug_draw:
            self.debug_draw = mediapipe.solutions.drawing_utils
        else:
            self.debug_draw = None

    def process_frame(self, frame: ndarray):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_image)

        if result.multi_hand_landmarks:
            hands = result.multi_hand_landmarks
            hand_data = {}
            for hand_num, hand in enumerate(hands):
                hand_data[hand_num] = {}
                for landmark_id, landmark in enumerate(hand.landmark):
                    height, width, channels = rgb_image.shape
                    cx, cy = int(landmark.x*width), int(landmark.y*height)
                    hand_data[hand_num][landmark_id] = [landmark.x, landmark.y, cx, cy]
                if self.debug_draw:
                    self.debug_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)
            return frame, hand_data
        else:
            return frame, None
