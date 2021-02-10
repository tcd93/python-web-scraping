from flask import Flask, jsonify
from scraper import scrap_itviec

app = Flask(__name__)


@app.route('/', methods=['GET'])
def search_api():
    return jsonify(result=scrap_itviec())


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(port=8080, host='localhost')
