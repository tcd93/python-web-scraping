from flask import Flask, jsonify, request
from scraper import scrap_itviec, scrap_vietnamwork

app = Flask(__name__)


@app.route('/itviec', methods=['GET'])
def search_itviec():
    return jsonify(result=scrap_itviec(
        page_num=int(request.args.get('page_num')) if 'page_num' in request.args else 1,
        limit=int(request.args.get('limit')) if 'limit' in request.args else 10,
    ))


@app.route('/vietnamwork', methods=['GET'])
def search_vietnamwork():
    return jsonify(result=scrap_vietnamwork(
        page_num=int(request.args.get('page_num')) if 'page_num' in request.args else 1,
        limit=int(request.args.get('limit')) if 'limit' in request.args else 50,
    ))


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.run(port=8080, host='localhost', debug=True)
