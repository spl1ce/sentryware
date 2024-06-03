import cv2
import numpy as np
from flask import Flask, Response
import mss
import pyautogui
# from flask_lt import run_with_lt

app = Flask(__name__)
# run_with_lt(app)

def capture_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not start camera.")
    
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                continue
            
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error capturing webcam: {e}")
            break
    cap.release()

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while True:
            try:
                img = sct.grab(monitor)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                cursor_x, cursor_y = pyautogui.position()
                cursor_color = (0, 255, 255)
                cursor_radius = 10
                cursor_thickness = 2
                cv2.circle(frame, (cursor_x, cursor_y), cursor_radius, cursor_color, cursor_thickness)

                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Error capturing screen: {e}")

@app.route('/webcam')
def wecam_feed():
    return Response(capture_webcam(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/screen')
def screen_feed():
    return Response(capture_screen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, threaded=True, debug=True)