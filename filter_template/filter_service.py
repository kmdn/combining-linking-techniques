from flask import Flask, request, Response, jsonify
import json
import spacy

app = Flask(__name__)

print("Loading Custom Filter")




# remove mentions that are in the banned_words list
def process(document):
    banned_words = ['emperor']

    filtered_mentions = [i for i in document['mentions'] if i['mention'] not in banned_words]
    document['mentions'] = filtered_mentions

    return document



@app.route('/', methods=['get', 'post'])
def index():
    print("Incoming request:")
    req = json.loads(request.data)
    document = req['document']

    document = process(document)
    # print(document)

    return jsonify(
            {'document' : document,
            'pipelineConfig' : req['pipelineConfig'],
            'componentId' : req['componentId']}
            )




class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, env, resp):
        errorlog = env['wsgi.errors']
        #pprint.pprint(('REQUEST', env), stream=errorlog)

        def log_response(status, headers, *args):
            #pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(env, log_response)


# Run at flask startup (https://stackoverflow.com/a/55573732)
with app.app_context():
    pass

if __name__ == '__main__':
    port = 5007
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host='0.0.0.0', port=port)
    #app.run()


