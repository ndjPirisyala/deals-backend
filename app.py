from flask import Flask, Response, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)


@app.route('/deals')
def deals():
    return jsonify(pickle.load(open('temp', 'rb')))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
