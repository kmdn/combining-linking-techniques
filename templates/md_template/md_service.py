from flask import Flask, request, Response, jsonify
import json
import spacy

app = Flask(__name__)

print("Loading Custom MD")

def add_mention(mention, offset, mentions_list):
    mention_object = {
            "mention": mention,
            "offset": offset
            }
    mentions_list.append(mention_object)


def detect(text):
    ''' replace the following line with something like -> mentions = own_system.detect(text) '''

    mentions = [{"text": "Napoleon", "offset": 0}, {"text": "emperor", "offset": 17}] 
    return mentions


def process(document):
    text = document['text']

    # detect mentions with your own system
    # example
    mentions = detect(text)

    if document['mentions'] is None:
        document['mentions'] = []

    for mention in mentions:
        mention_text = mention["text"]
        mention_offset = mention["offset"]
        add_mention(mention_text, mention_offset, document['mentions'])




# received object: 
# {
  # "componentId":"MD1",
  # "document": {
    # "componentId":"input",
    # "mentions":[],
    # "pipelineType":"NONE",
    # "text":"Napoleon was the emperor of the First French Empire.", <-- the input text ------------------------------------------------
    # "uri":null
  # },
  # "pipelineConfig":{
    # "components":{
      # "cg_ed":[],
      # "md":[{
        # "id":"MD1",
        # "value":"http://host.docker.internal:5001"
      # }]
    # },
    # "connections":[],
    # "displayName":"MD + combined CG-ED",
    # "endComponents":["MD1"],
    # "exampleId":"md_combined_cged",
    # "id":1,
    # "pipelineConfigType":"complex",
    # "startComponents":["MD1"]
  # }
# }
# curl http://127.0.0.1:5001/ --header "Content-Type: application/json" --request POST -d '{"document" : {"text": "Napoleon was the emperor of the First French Empire."},"pipelineConfig": "complex","componentId": "MD1"}'
#

@app.route('/', methods=['get', 'post'])
def index():
    print("Incoming request:")
    print(request.data)
    req = json.loads(request.data)
    document = req['document']

    process(document)

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
    port = 5001
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host='0.0.0.0', port=port)
    #app.run()
