use_local_streaming = True


from flask import Flask, request, redirect, url_for, jsonify, Response
from vae_robit import Robit
import logging

if use_local_streaming:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput

import io
import threading

robit = Robit()

app = Flask(__name__)

logging.getLogger("werkzeug").setLevel(logging.WARNING)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
if use_local_streaming:
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))

    output = StreamingOutput()
    picam2.start_recording(JpegEncoder(), FileOutput(output))

def generate_frames():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def send_command(cmd):
    print(f"Send serial command: [{cmd}]")
    robit.serial.sendCommand(cmd)

@app.route('/video_feed')
def video_feed():
    if use_local_streaming:
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route("/")
def index():
    content = """
    <html>
        <head>
            <title>Robot Control</title>
        </head>
        <body>
            <h1>Control Panel</h1>
            
            <button onclick="sendCommand('FORWARD')">Forward</button><br><br>
            <button onclick="sendCommand('BACKWARD')">Backward</button><br><br>
            <button onclick="sendCommand('LEFT')">Turn Left</button><br><br>
            <button onclick="sendCommand('RIGHT')">Turn Right</button><br><br>
            <button onclick="sendCommand('RESET')">Reset</button>
    """

    if use_local_streaming:
        content += """
            <h2>Camera Feed</h2>
            <img src="/video_feed" width="640" height="480" style="transform: rotate(180deg);" loading="eager">
        """

    content += """
            <h2>Serial Output</h2>
            <textarea id="serialBox" rows="20" cols="80" readonly></textarea>

            <script>
                async function updateSerial() {
                    try {
                        console.info("update")
                    
                        const response = await fetch('/serial');
                        const data = await response.json();

                        const box = document.getElementById('serialBox');
                        if (!box) return;

                        const newText = data.lines.join('\\n');

                        // Only update if changed (prevents flicker)
                        if (box.value !== newText) {
                            box.value = newText;
                            box.scrollTop = box.scrollHeight;
                        }

                    } catch (e) {
                        console.error("Error fetching serial data:", e);
                    }
                }

                // Ensure DOM is ready before running
                window.onload = function () {
                    updateSerial();                  // initial load
                    const intervalId = setInterval(updateSerial, 1000); // poll every second
                };
            </script>
            <script>
            async function sendCommand(cmd) {
                try {
                    await fetch('/cmd', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ command: cmd })
                    });
                } catch (e) {
                    console.error("Command failed:", e);
                }
            }
            </script>
        </body>
    </html>
    """
    return content

@app.route("/cmd", methods=["POST"])
def command():
    data = request.get_json()
    cmd = data.get("command") if data else None

    valid_commands = {
            "FORWARD": "M3M1000",
            "BACKWARD": "M3M-1000",
            "LEFT": "M1M400",
            "RIGHT": "M2M400",
            "SPIN_LEFT": ("M1M400", "M2M-400"),
            "SPIN_RIGHT": ("M2M400", "M1M-400"),
            "RESET": "SR"
    }

    if cmd in valid_commands:
        scmd = valid_commands[cmd]
        if isinstance(scmd, str):
            send_command(scmd)
        elif isinstance(scmd, list) or isinstance(scmd, tuple):
            for i in scmd:
                send_command(i)
        else:
            return jsonify({"status": "error"}), 500
        return jsonify({"status": "ok"})

    return jsonify({"status": "error"}), 400

@app.route("/serial")
def get_serial():
    return jsonify({"lines": list(robit.serial.history)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
