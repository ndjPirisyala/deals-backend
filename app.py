from flask import Flask, Response, jsonify, send_file
from flask_cors import CORS
import pickle
import io

app = Flask(__name__)
CORS(app)

@app.route('/deals')
def deals():
    arr1 = pickle.load(open('temp', 'rb'))
    arr2 = arr1
    for i in arr2:
        if i[1] == 0:
            i[1] = 1
        else:
            break
    pickle.dump(arr2, open('temp', 'wb'))
    return jsonify(arr1)

@app.route('/count')
def count():
    return jsonify(pickle.load(open('count', 'rb')))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
