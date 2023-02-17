from flask import Flask, request, Response, jsonify
import json
import spacy

app = Flask(__name__)

print("Loading Custom Splitter")


# Example copy split
def process(document, number_of_child_nodes):

    return [ document for i in range(0, number_of_child_nodes) ]




@app.route('/', methods=['get', 'post'])
def index():
    print("Incoming request:")
    req = json.loads(request.data)
    document = req['document']

    number_of_child_nodes = 0
    for child in req['pipelineConfig']['connections']:
        if child['source'] == req['componentId']:
            number_of_child_nodes+=1
    if req['componentId'] in req['pipelineConfig']['endComponents']:
        number_of_child_nodes += 1


    documents = process(document, number_of_child_nodes+1)

    assert len(documents) == number_of_child_nodes

    documents_dict_array = [{'document': doc} for doc in documents]


    return jsonify(
            {'documents' : documents_dict_array,
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
    port = 5003
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host='0.0.0.0', port=port)
    #app.run()


