from flask import Flask, request, Response, jsonify
#import pprint
import json
import spacy

app = Flask(__name__)

print("Loading spacy SM")
_nlp = spacy.load("en_core_web_sm")
#_nlp = spacy.load("en_core_web_trf") # performs better

# Run with
# <s>flask run --port=5002</s>
# TODO Didn't work with spaCy, use
# python app.py

# Test with
# curl http://127.0.0.1:5002/ --header "Content-Type: application/json" --request POST -d '{"doc" : {"text": "Napoleon was the emperor of the First French Empire."}}'


def process(doc):
    text = doc['text']
    spacy_doc = _nlp(text)
    doc['mentions'] = []
    for ent in spacy_doc.ents:
        print(f'[{ent.start_char}:{ent.end_char}] {ent.text} ({ent.label_})')
        mention = spacy_ent_to_mention(ent)
        doc['mentions'].append(mention)
    print(f'Detected {len(doc["mentions"])} mentions')
    return doc


def spacy_ent_to_mention(ent):
    return {
        'offset' : ent.start_char,
        'mention' : ent.text
        }


@app.route('/', methods=['get', 'post'])
def index():
    print("Incoming request:")
    print(request.data)
    req = json.loads(request.data)
    document = req['document']
    pipelineConfig = req['pipelineConfig']
    componentId = req['componentId']

    # TODO The component has only one functionality, so no matter what is currentComponent, it there is only one way of processing the document
    #if findComponentInPipelineConfig(current_component).getType() is EnumComponentType.MD:

    document = process(document)

    return jsonify(
            {'document' : document,
            'pipelineConfig' : pipelineConfig,
            'componentId' : componentId}
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
    port = 5001
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host='0.0.0.0', port=port)
    #app.run()
