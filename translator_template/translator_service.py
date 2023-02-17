from flask import Flask, request, Response, jsonify
import json
import spacy

app = Flask(__name__)

print("Loading Custom Translator")



# translates dbpedia to wikipedia
def process_link(link, mention):
    processed_link = link.replace("http://dbpedia.org/resource/", "https://wikipedia.org/wiki/")
    return processed_link


def process(document):
    for mention_dict in document['mentions']:
        mention_value = mention_dict['mention']
        link = mention_dict['assignment']['assignment']
        processed_link = process_link(link, mention_value)
        mention_dict['assignment']['assignment'] = processed_link

        for possible_assignment in mention_dict['possibleAssignments']:
            processed_link_possible_assignment = process_link(possible_assignment['assignment'], mention_value)
            possible_assignment['assignment'] = processed_link_possible_assignment

    return document


@app.route('/', methods=['get', 'post'])
def index():
    print("Incoming request:")
    req = json.loads(request.data)


    document = process(req['document'])

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
    port = 5005
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host='0.0.0.0', port=port)
    #app.run()


