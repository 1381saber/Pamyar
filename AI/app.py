from flask import Flask, request
from flask_socketio import SocketIO # type: ignore
from gemini_chatter import GeminiChatter

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

print("Initializing Gemini Chatter...")
gemini_session = GeminiChatter(socketio_instance=socketio)
print("Gemini Chatter Initialized.")

@socketio.on('connect')
def handle_connect():
    print('✅ Client connected!')
    socketio.emit('status_update', {'message': 'Successfully connected to Pamyar AI server!'})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected. Stopping session.')
    if gemini_session.is_running:
        gemini_session.stop()

@socketio.on('start_chat')
def handle_start_chat(data):
    print("▶️ 'start_chat' event received. Starting session...")
    if not gemini_session.is_running:
        gemini_session.start()
    else:
        print("ℹ️ Session is already running.")

@socketio.on('stop_chat')
def handle_stop_chat(data):
    print("⏹️ 'stop_chat' event received. Stopping session...")
    if gemini_session.is_running:
        gemini_session.stop()

if __name__ == '__main__':
    print("🚀 Starting Flask-SocketIO AI Bridge Server on http://127.0.0.1:5001")
    socketio.run(app, host='127.0.0.1', port=5001, debug=False)