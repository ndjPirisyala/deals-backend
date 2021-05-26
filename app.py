from flask import Flask, Response, jsonify, send_file
from flask_cors import CORS
import pickle
import io

app = Flask(__name__)
CORS(app)

@app.route('/deals')
def deals():
    return jsonify(pickle.load(open('temp', 'rb')))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
