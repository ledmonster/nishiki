# -*- coding: utf-8 -*-
import datetime
import json
import os

import requests
from flask import Flask, request, abort, jsonify


app = Flask(__name__)

BOT_NAME = os.environ.get('BOT_NAME', 'chat-bot')
API_URL = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue'
API_KEY = os.environ['DOCOMO_API_KEY']
TOKEN = os.environ['SLACK_TOKEN']

CONTEXT = None
MODE = None
LAST_ACCESS = datetime.datetime.now()


@app.route('/', methods=['POST'])
def main():
    global MODE, CONTEXT, LAST_ACCESS

    if request.form['token'] != TOKEN:
        abort(401)
    user_id = request.form['user_id']
    user_name = request.form['user_name']
    text = request.form['text'].replace(BOT_NAME, "")

    # docomo API に対する request
    api_req = {
        'utt': text,
        'nickname': user_name,
        'place': '東京',
        # 't': 20,
    }

    # 前回のアクセスが3分以内の場合のみ、コンテキストを保持
    now = datetime.datetime.now()
    if now < LAST_ACCESS + datetime.timedelta(seconds=180):
        if CONTEXT is not None:
            api_req['context'] = CONTEXT
        if MODE is not None:
            api_req['mode'] = MODE

    r = requests.post(
        API_URL,
        params={'APIKEY': API_KEY},
        data=json.dumps(api_req))
    ret = r.json()

    # global 変数を上書き
    MODE = ret['mode']
    CONTEXT = ret['context']
    LAST_ACCESS = now

    return jsonify(text="{}: {}".format(user_name, ret['utt']))


if __name__ == "__main__":
    app.run()
