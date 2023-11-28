from flask import Flask, request, Response, jsonify
import json
import requests
import pickle

from genre.fairseq_model import GENRE
from genre.trie import Trie


app = Flask(__name__)

print("Loading Custom ED")

# load the prefix tree (trie)
with open("data/kilt_titles_trie_dict.pkl", "rb") as f:
    trie = Trie.load_from_dict(pickle.load(f))

# load the model
model = GENRE.from_pretrained("models/fairseq_entity_disambiguation_aidayago").eval()

def add_assignment(score, assignment, mention):
    if not mention['assignment']:
        mention['assignment'] = {}
    mention['assignment']['score'] = score
    mention['assignment']['assignment'] = assignment


def add_possible_assignment(score, assignment, possible_assignments_list):
    possible_assignment_object = {
            "score": score,
            "assignment": assignment
            }

    possible_assignments_list.append(possible_assignment_object)


def choose_candidate(possible_assignments, all_possible_assignments):
    ''' possible assignment for a mention VS all_possible_assignments for all mentions '''
    maximum_score = 0
    assignment = {}
    for a in possible_assignments:
        if a['score'] > maximum_score:
            maximum_score = a['score']
            assignment = a
    return assignment

def process(document):
    mentions = document['mentions']
    text = document['text']

    for mention in mentions:
        if mention['possibleAssignments'] is None or not mention['possibleAssignments']:
            pass

        genre_assignments = []
        replacement = '[START_ENT] ' + mention['mention'] + ' [END_ENT]'
        offset = mention['offset']
        

        print('mention found : ' + mention['mention'] + "\n")
        new_text = ''
        new_text = text[:offset]
        new_text += replacement
        new_text += text[offset + len(mention['mention']):]
        print(new_text)
        res = model.sample(
            sentences=[new_text],
            prefix_allowed_tokens_fn=lambda batch_id, sent: trie.get(sent.tolist()),
        )
        for candidate in res[0]:
            add_possible_assignment(candidate['score'].item, candidate['text'], genre_assignments)

        

        all_possible_assignments_list = [m['possibleAssignments'] for m in mentions]
        all_possible_assignments = [possibleAssignment for sublist in all_possible_assignments_list for possibleAssignment in sublist]

        relevants_assignments = []
        for oa in genre_assignments:
            for passed_assignment in all_possible_assignments:
                if oa['assignment'] == passed_assignment['assignment']:
                    relevants_assignments.append(oa)

        choose_candidate(relevants_assignments, all_possible_assignments)


# received object: 
# "document": [{
    # "componentId": "CG1",
    # "mentions": [{
      # "offset": 0,
      # "assignment": null,
      # "possibleAssignments": [{
        # "score": 1.0,
        # "assignment": "http://dbpedia.org/resource/Emperor"
      # },
      # {
        # "score": 1.0,
        # "assignment": "http://babelnet.org/rdf/s00030591n"
      # }],
      # "originalWithoutStopwords": "Napoleon",
      # "detectionConfidence": -1.0,
      # "originalMention": "Napoleon",
      # "mention": "Napoleon"
    # },
    # {
      # "offset": 17,
      # "assignment": null,
      # "possibleAssignments": [{
        # "score": 1.0,
        # "assignment": "http://dbpedia.org/resource/Emperor"
      # },
      # {
        # "score": 1.0,
        # "assignment": "http://babelnet.org/rdf/s00030591n"
      # }],
      # "originalWithoutStopwords": "emperor",
      # "detectionConfidence": -1.0,
      # "originalMention": "emperor",
      # "mention": "emperor"
    # }],
    # "text": "Napoleon was the emperor of the First French Empire.",
    # "pipelineType": "CG",
    # "uri": null
  # }]
# curl http://127.0.0.1:5003/ --header "Content-Type: application/json" --request POST -d '{"document":{"uri":null,"text":"Napoleon was the emperor of the First French Empire.","mentions":[{"mention":"Napoleon","offset":0,"assignment":null,"detectionConfidence":-1.0,"possibleAssignments":[{"score":1.0,"assignment":"test.com/Napoleon"},{"score":1.0,"assignment":"test2.com/Napoleon"}],"originalMention":"Napoleon","originalWithoutStopwords":"Napoleon","logger":{"logName":"structure.datatypes.Mention"}},{"mention":"emperor","offset":17,"assignment":null,"detectionConfidence":-1.0,"possibleAssignments":[{"score":1.0,"assignment":"test.com/Napoleon"},{"score":1.0,"assignment":"test2.com/Napoleon"}],"originalMention":"emperor","originalWithoutStopwords":"emperor","logger":{"logName":"structure.datatypes.Mention"}}],"componentId":"MD1","pipelineType":"MD"},"pipelineConfig":{"startComponents":["MD1"],"components":{"cg":[{"id":"CG1","value":"http://127.0.0.1:5002"}],"md":[{"id":"MD1","value":"http://127.0.0.1:5001"}],"cg_ed":[]},"exampleId":"md_combined_cged","endComponents":["CG1"],"displayName":"MD + combined CG-ED","id":1,"connections":[{"source":"MD1","target":"CG1"}],"pipelineConfigType":"complex"},"componentId":"CG1"}'
#

@app.route('/', methods=['get', 'post'])
def index():
    print("Incoming request:")
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
    port = 5003
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host='0.0.0.0', port=port)
    #app.run()


