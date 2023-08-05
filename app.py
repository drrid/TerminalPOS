from flask import Flask, jsonify, render_template, request
import conf

app = Flask(__name__)

textile_data = []


@app.route('/')
def index():
    return render_template('index.html', data=textile_data)

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    textile_data.append(data)
    return jsonify({"success": True})

@app.route('/clear', methods=['POST'])
def clear():
    textile_data.clear()
    return jsonify({"success": True})

@app.route('/data')
def data():
    return jsonify(textile_data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5555)
