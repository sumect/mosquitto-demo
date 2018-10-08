from flask import request, current_app

from route.base import acls_bp
from route.account import valid_username
from model import db
from model.acls import Acls
from util.response import success, error


@acls_bp.route('', methods=['GET'])
def get_acls():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    query = Acls.query.paginate(page=page, per_page=limit)
    items, total = query.items, query.total
    data = [
        {
            'username': item.username,
            'topic': item.topic,
            'rw': item.rw
        } for item in items
    ]
    return success(data, total=total)


@acls_bp.route('', methods=['POST'])
def post_acls():
    json_data = request.get_json()
    username_length = current_app.config['USERNAME_LENGTH']
    if not json_data or not isinstance(json_data, dict):
        return error(400, 'Json parse error.')
    username = str(json_data.get('username'))
    if not valid_username(username, username_length):
        return error(400, 'Username not valid.')
    topic = str(json_data.get('topic'))
    rw = int(json_data.get('rw'))
    acls = Acls.query.filter(
        Acls.topic == topic,
        Acls.username == username).first()
    if acls:
        return error(403, 'Acls already exists.')
    acls = Acls(username=username, ropic=topic, rw=rw)
    db.session.add(acls)
    db.session.commit()
    data = {
        'username': acls.username,
        'topic': acls.topic,
        'rw': acls.rw
    }
    return success(data)
