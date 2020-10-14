from app import app
from app.FlewLexer import FlewLexer
from flask import jsonify,request,abort

@app.route('/')
def index():
    return jsonify({'status': 'OK'})


@app.route('/api/parse', methods=['GET', 'POST'])
def parse():
    if not request.json or not 'input' in request.json:
        abort(400)
    f = FlewParser()
    json_input = request.json['input']
    print(json_input)
    response = f.parse_line(json_input)
    return jsonify(response)
