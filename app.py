from flask import Flask, render_template, jsonify, request
import replicate
import cv2
import mediapipe as mp
import time
import requests
import pickle
import numpy as np

app = Flask(__name__)

# Pose detection setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# Initialize counters and feedback
pushup_counter = 0
squat_counter = 0
stage_pushup = None
stage_squat = None
pushup_feedback = ""
squat_feedback = ""
detection_feedback = ""

# Replicate API settings
REPLICATE_API_KEY = "your_replicate_api_key_here"
REPLICATE_MODEL_URL = "https://api.replicate.com/v1/predictions"

@app.route('/')
def home():
    return render_template('first.html')  # Main home page

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("question", "")
    if not user_input:
        return jsonify({"answer": "Please ask a question."})

    # Fitness-related chat response
    if "fitness plan" in user_input.lower() or "exercise plan" in user_input.lower():
        response = call_replicate_model(user_input)
        return jsonify({"answer": response})
    else:
        return jsonify({"answer": "I'm here to assist with fitness-related questions only."})

def call_replicate_model(user_input):
    headers = {
        "Authorization": f"Token {REPLICATE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "input": {
            "text": f"Please provide a fitness plan based on the following request: {user_input}",
        }
    }

    response = requests.post(REPLICATE_MODEL_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return "Sorry, I couldn't process that request."

@app.route('/fit')
def fit():
    return render_template('fit.html')  # HTML page for fitness detection

@app.route('/live_track', methods=['GET'])
def live_track():
    return render_template('live_track.html')  # HTML page for live tracking

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    image_data = request.form['image']
    nparr = np.fromstring(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Analyzes the face expression using a placeholder function
    emotion = analyze_face_expression(img)
    suggestion = suggest_activity(emotion)

    return jsonify({'emotion': emotion, 'suggestion': suggestion})

@app.route('/start-exercise', methods=['POST'])
def start_exercise():
    global pushup_counter, squat_counter, stage_pushup, stage_squat
    global pushup_feedback, squat_feedback, detection_feedback
    
    pushup_counter = 0
    squat_counter = 0
    pushup_feedback = ""
    squat_feedback = ""
    detection_feedback = ""

    cap = cv2.VideoCapture(0)
    start_time = time.time()
    while time.time() - start_time < 30:  # 30 seconds
        ret, frame = cap.read()
        if not ret:
            break

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        # Pose detected
        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Detect push-ups
            detect_pushups(results)

            # Detect squats
            detect_squats(results)
        else:
            detection_feedback = "Move closer to the camera!"

        # Display feedback on the frame
        cv2.putText(frame, pushup_feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, squat_feedback, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, detection_feedback, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("Exercise Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return jsonify({"pushups": pushup_counter, "squats": squat_counter})

def detect_pushups(results):
    global pushup_counter, stage_pushup, pushup_feedback

    if results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility < 0.5 or \
       results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].visibility < 0.5 or \
       results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].visibility < 0.5:
        pushup_feedback = "Make sure your arms are visible!"
        return

    left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
    left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]

    angle_pushup = calculate_angle(left_shoulder, left_elbow, left_wrist)

    if angle_pushup > 160:
        stage_pushup = "up"
        pushup_feedback = "Good! Keep your body straight."
    elif angle_pushup < 90 and stage_pushup == "up":
        stage_pushup = "down"
        pushup_counter += 1
        pushup_feedback = "Nice! You've completed a push-up."
    else:
        pushup_feedback = "Adjust your form!"

def detect_squats(results):
    global squat_counter, stage_squat, squat_feedback

    if results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].visibility < 0.5 or \
       results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].visibility < 0.5 or \
       results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].visibility < 0.5:
        squat_feedback = "Make sure your legs are visible!"
        return

    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

    angle_squat = calculate_angle(left_hip, left_knee, left_ankle)

    if angle_squat > 170:
        stage_squat = "up"
        squat_feedback = "Good! Keep your back straight."
    elif angle_squat < 90 and stage_squat == "up":
        stage_squat = "down"
        squat_counter += 1
        squat_feedback = "Nice! You've completed a squat."
    else:
        squat_feedback = "Make sure to go lower!"

def calculate_angle(a, b, c):
    a = [a.x, a.y]
    b = [b.x, b.y]
    c = [c.x, c.y]

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def load_model():
    with open('model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model

def analyze_face_expression(image):
    emotions = ['happy', 'neutral', 'sad']
    return np.random.choice(emotions)

def suggest_activity(emotion):
    if emotion == 'happy':
        return "Great to see you happy! Keep it up by doing something you enjoy."
    elif emotion == 'neutral':
        return "You're feeling neutral. How about taking a short walk?"
    else:
        return "It seems you might need some positivity. Try some deep breathing exercises."

if __name__ == '__main__':
    app.run(debug=True)
