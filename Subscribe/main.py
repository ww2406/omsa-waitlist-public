from flask import Request, abort, Response
import firebase_admin
from firebase_admin import firestore, messaging
import uuid

fb = firebase_admin.initialize_app()

def subscribe(request: Request):
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    request_json = request.get_json(silent=True)
    if not request_json\
            or 'token' not in request_json\
            or 'crn' not in request_json\
            or 'term' not in request_json:
        return Response(status=400, headers=headers)
    topic = request_json['term']+'_'+request_json['crn']
    if 'test' in request_json:
        topic += '_test'
    messaging.subscribe_to_topic(request_json['token'], topic)
    db: firestore.firestore.Client = firestore.client()
    db.collection('subscriptions').document(str(uuid.uuid4())).set({
        'topic': topic,
        'token': request_json['token']
    })
    return Response(status=204, headers=headers)
