from flask import Flask, request, Response, jsonify
import json
from refined.inference.processor import Refined


app = Flask(__name__)

print("Loading Custom CG")


def add_possible_assignment(score, assignment, possible_assignments_list):
    possible_assignment_object = {
            "score": score,
            "assignment": assignment
            }

    possible_assignments_list.append(possible_assignment_object)


def generate_candidates(mention):

    possible_assignments = []

    text = mention['mention']

    refined = Refined.from_pretrained(model_name='wikipedia_model_with_numbers',
                                      entity_set="wikipedia")
    spans = refined.process_text(text)
    for span in spans:
        for entity, score in span.top_k_predicted_entities:
            if entity.wikidata_entity_id:
                possible_assignments.append({'score': score, 'assignment': entity.wikidata_entity_id})


    return possible_assignments


def process(document):
    mentions = document['mentions']

    for mention in mentions:
        if mention['possibleAssignments'] is None:
            mention['possibleAssignments'] = []

        # replace the following line with something like -> possible_assignments = own_system.get_candidates(mention) 
        # example

        possible_assignments = generate_candidates(mention)


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

