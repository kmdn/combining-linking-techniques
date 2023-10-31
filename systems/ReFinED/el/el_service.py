from flask import Flask, request, Response, jsonify
import json
from refined.inference.processor import Refined



app = Flask(__name__)

print("Loading Custom ED")


def add_assignment(score, assignment, mention):
    if not mention['assignment']:
        mention['assignment'] = {}
    mention['assignment']['score'] = score
    mention['assignment']['assignment'] = assignment

def create_mentions():
    
    pass

def process(document):

    text = document['text']
    refined = Refined.from_pretrained(model_name='wikipedia_model_with_numbers',
                                      entity_set="wikipedia")


    spans = refined.process_text(text)
    for span in spans:
        assignment_value = span.doc_id
        assignment_value = span.predicted_entity.wikidata_entity_id
        print([span.candidate_entities, span.coarse_mention_type, span.coarse_type, span.date, span.doc_id, span.entity_linking_model_confidence_score, span.failed_class_check, span.gold_entity, span.predicted_entity, span.predicted_entity_types, span.pruned_candidates, span.top_k_predicted_entities])


        print(dir(type(predicted_entity)))
    
    # add_assignment(assignment_score, assignment_value, mention)







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



