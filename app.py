from flask import Flask, jsonify, render_template, request
import conf
from flask_socketio import SocketIO


app = Flask(__name__)
socketio = SocketIO(app)
textile_data = []

@socketio.on('clear')
def clear():
    textile_data.clear()
    socketio.emit('update_data', textile_data)

@socketio.on('update')
def update(data):
    textile_data.append(data)
    socketio.emit('update_data', textile_data)

@socketio.on('fetch_data')
def handle_fetch_data():
    socketio.emit('update_data', textile_data)

@app.route('/')
def index():
    return render_template('index.html', data=textile_data)

@app.route('/data')
def data():
    return jsonify(textile_data)

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5555)

