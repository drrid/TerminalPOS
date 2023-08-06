from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_socketio import SocketIO
import conf

app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app)
textile_data = []


@app.route('/textiles', methods=['GET'])
def get_textiles():
    textiles = conf.select_all_textiles()
    return jsonify([textile.name for textile in textiles])

@socketio.on('fetch_data')
def handle_fetch_data():
    textiles = conf.select_all_textiles()
    data = [{'name': textile.name, 'quantity': 0, 'price': textile.price, 'quantity_left': 0} for textile in textiles]
    socketio.emit('update_data', data)

@app.route('/')
def index():
    return render_template('index.html', data=textile_data)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

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

@app.route('/confirm_transaction', methods=['POST'])
def confirm_transaction():
    # Implement your logic to confirm the transaction, print receipt, etc.
    return jsonify({"status": "success"})

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5555)
