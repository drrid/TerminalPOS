from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Simple data table to store and manage data
data_table = []


# Route to serve the web app
@app.route('/')
def index():
    return render_template('index.html')


# WebSocket event to receive updates from the terminal app
@socketio.on('update_table')
def handle_update_table(data):
    data_table.append(data)  # Add the new data to the data table
    emit('table_updated', data_table, broadcast=True)  # Broadcast the updated data table to all clients


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')