from flask import Flask, request, Response, jsonify
import json
import blink.main_dense as main_dense
import argparse

app = Flask(__name__)

print("Loading Custom CG")
models_path = "models/" # the path where you stored the BLINK models

config = {
    "test_entities": None,
    "test_mentions": None,
    "interactive": False,
    "top_k": 10,
    "biencoder_model": models_path+"biencoder_wiki_large.bin",
    "biencoder_config": models_path+"biencoder_wiki_large.json",
    "entity_catalogue": models_path+"entity.jsonl",
    "entity_encoding": models_path+"all_entities_large.t7",
    "crossencoder_model": models_path+"crossencoder_wiki_large.bin",
    "crossencoder_config": models_path+"crossencoder_wiki_large.json",
    "fast": False, # set this to be true if speed is a concern
    "output_path": "logs/" # logging directory
}

args = argparse.Namespace(**config)

models = main_dense.load_models(args, logger=None)


def add_possible_assignment(score, assignment, possible_assignments_list):
    possible_assignment_object = {
            "score": score,
            "assignment": assignment
            }

    possible_assignments_list.append(possible_assignment_object)


def generate_candidates(text, mention):

    possible_assignments = []


    context_left = text[:mention['offset']].lower()
    context_right = text[mention['offset']+len(mention['mention'])+1:].lower()
    mention_text = mention['mention'].lower()
    data_to_link = [ {
                        "id": 0,
                        "label": "unknown",
                        "label_id": -1,
                        "context_left": context_left,
                        "mention": mention_text,
                        "context_right": context_right
                    },
                    ]

    print("left", context_left)
    print("right", context_right)
    print("mention", mention_text)
    _, _, _, _, _, predictions, scores, = main_dense.run(args, None, *models, test_data=data_to_link)

    print("for the mention: ", mention_text, " the following candidates were found:", predictions) 
    print("-------------------------")
    print(scores)
    print(len(predictions[0]))
    print("-------------------------")
    for i in range(len(predictions[0])):
        add_possible_assignment(scores[0][i].item(), predictions[0][i], possible_assignments)
    return possible_assignments


def process(document):

    mentions = document['mentions']

    for mention in mentions:
        if mention['possibleAssignments'] is None:
            mention['possibleAssignments'] = []

        # replace the following line with something like -> possible_assignments = own_system.get_candidates(mention) 
        # example

        possible_assignments = generate_candidates(document['text'], mention)


        for possibleAssignment in possible_assignments:
            assignment_score = possibleAssignment['score']
            assignment_value = possibleAssignment['assignment']

            add_possible_assignment(assignment_score, assignment_value, mention['possibleAssignments'])






# received object: 
# {
  # ...
  # "document": {
    # "componentId":"input",
    # "mentions":[
        # {'mention': 'Napoleon', 'offset': 0},
        # {'mention': 'emperor', 'offset': 17}
    # ],
    # "pipelineType":"NONE",
    # "text":"Napoleon was the emperor of the First French Empire.", <-- the input text ------------------------------------------------
    # "uri":null
  # },
  # ...
  # }
# }
# curl http://127.0.0.1:5002/ --header "Content-Type: application/json" --request POST -d '{"document":{"uri":null,"text":"Napoleon was the emperor of the First French Empire.","mentions":[{"mention":"Napoleon","offset":0,"assignment":null,"detectionConfidence":-1.0,"possibleAssignments":[],"originalMention":"Napoleon","originalWithoutStopwords":"Napoleon","logger":{"logName":"structure.datatypes.Mention"}},{"mention":"emperor","offset":17,"assignment":null,"detectionConfidence":-1.0,"possibleAssignments":[],"originalMention":"emperor","originalWithoutStopwords":"emperor","logger":{"logName":"structure.datatypes.Mention"}}],"componentId":"MD1","pipelineType":"MD"},"pipelineConfig":{"startComponents":["MD1"],"components":{"cg":[{"id":"CG1","value":"http://127.0.0.1:5002"}],"md":[{"id":"MD1","value":"http://127.0.0.1:5001"}],"cg_ed":[]},"exampleId":"md_combined_cged","endComponents":["CG1"],"displayName":"MD + combined CG-ED","id":1,"connections":[{"source":"MD1","target":"CG1"}],"pipelineConfigType":"complex"},"componentId":"CG1"}'

#

@app.route('/', methods=['get', 'post'])
def index():
    print("Incoming request:")
    print(request.data)
    req = json.loads(request.data)
    document = req['document']

    process(document)

    print(document)
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
    port = 5002
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host='0.0.0.0', port=port)
    #app.run()



