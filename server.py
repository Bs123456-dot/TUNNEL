from flask import Flask, request
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store connected users
connected_users = {}

@app.route("/")
def home():
    return "🚀 Tunnel Relay on Render is running!"

@app.route("/message", methods=["POST"])
def twilio_message():
    sender = request.values.get("From")
    body = request.values.get("Body")

    print(f"📩 Twilio Message: {sender}: {body}")

    # Route message to user if connected
    if sender in connected_users:
        socket_id = connected_users[sender]
        socketio.emit("tunnel_message", {"from": sender, "body": body}, room=socket_id)
        return "Message forwarded", 200
    else:
        print("⚠️ User not connected")
        return "No connected user", 404

@socketio.on("register")
def register_user(data):
    user_id = data["user_id"]
    connected_users[user_id] = request.sid
    print(f"✅ {user_id} connected via socket")

@socketio.on("disconnect")
def disconnect_user():
    for user_id, sid in list(connected_users.items()):
        if sid == request.sid:
            del connected_users[user_id]
            print(f"❌ {user_id} disconnected")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
