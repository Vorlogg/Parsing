from flask import Flask, jsonify, request, make_response, abort
from SberOfSite import SberOfSite
from SmartLab import SmartLab
from interfax import Interfax
from primpres import Primpress
from telegramparser import TelegramParser
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

sber = SberOfSite()
smartlab = SmartLab()
interfax=Interfax()
primpres=Primpress()
telegram=TelegramParser()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/data', methods=['POST'])
def get_data():
    if not request.json or not 'from' and 'id' in request.json:
        abort(400)
    id = int(request.json['id'])
    date = request.json['from']
    posts = []
    if request.json['source']=='all':
        print(request.json['source'])
        if request.json['id'] == '4':
            [posts.append(i) for i in sber.parse(date)]
        [posts.append(i) for i in smartlab.parse(id, date)]
        [posts.append(i) for i in interfax.parse(id, date)]
        [posts.append(i) for i in primpres.parse(id, date)]
        [posts.append(i) for i in telegram.get_news(id, date)]
    if request.json['source']=='smartlab':
        [posts.append(i) for i in smartlab.parse(id, date)]
    if request.json['source']=='interfax':
        [posts.append(i) for i in interfax.parse(id, date)]
    if request.json['source']=='primpres':
        [posts.append(i) for i in primpres.parse(id, date)]
    if request.json['source']=='telegram':
        [posts.append(i) for i in telegram.get_news(id, date)]
    if request.json['source']=='sber':
        [posts.append(i) for i in sber.parse(id, date)]



    return jsonify(posts), 201


if __name__ == '__main__':
    app.run()
