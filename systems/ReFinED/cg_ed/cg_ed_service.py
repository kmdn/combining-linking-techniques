import json
import re

from flask import Flask, Response, jsonify, request
from refined.data_types.base_types import Entity, Span
from refined.inference.processor import Refined

app = Flask(__name__)


print("Loading Custom Combined CG and ED")


def create_span_by_mention(mention) -> Span:
    text = mention["mention"]
    offset = mention["offset"]

    return Span(text=text, start=offset, ln=offset + len(text))


def add_assignment(score, assignment, mention):
    if not mention["assignment"]:
        mention["assignment"] = {}
    mention["assignment"]["score"] = score
    mention["assignment"]["assignment"] = assignment


def add_possible_assignment(score, assignment, possible_assignments_list):
    possible_assignment_object = {"score": score, "assignment": assignment}
    possible_assignments_list.append(possible_assignment_object)


def process(document):
    mentions = document["mentions"]
    text = document["text"]

    refined = Refined.from_pretrained(
        model_name="wikipedia_model_with_numbers", entity_set="wikipedia"
    )

    # Decission to run pipline once, and not for every span mention
    result = refined.process_text(text, [create_span_by_mention(m) for m in mentions])

    assert len(mentions) == len(result)

    for idx, mention in enumerate(mentions):
        span = result[idx]

        if mention["possibleAssignments"] is None or mention["possibleAssignments"] == [
            None
        ]:
            mention["possibleAssignments"] = []

        # replace the following line with something like -> possible_assignments = own_system.get_candidates(mention)
        # example

        for cand, score in span.candidate_entities:
            add_possible_assignment(
                score, cand.wikidata_entity_id, mention["possibleAssignments"]
            )

        assignment = span.predicted_entity

        assignment_score = 1  # TODO which score do not know if refined provides one
        assignment_value = assignment.wikidata_entity_id

        add_assignment(assignment_score, assignment_value, mention)


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


@app.route("/", methods=["get", "post"])
def index():
    print("Incoming request:")
    req = json.loads(request.data)
    document = req["document"]

    process(document)
    print(document)

    return jsonify(
        {
            "document": document,
            "pipelineConfig": req["pipelineConfig"],
            "componentId": req["componentId"],
        }
    )


class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, env, resp):
        errorlog = env["wsgi.errors"]
        # pprint.pprint(('REQUEST', env), stream=errorlog)

        def log_response(status, headers, *args):
            # pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(env, log_response)


# Run at flask startup (https://stackoverflow.com/a/55573732)
with app.app_context():
    pass

if __name__ == "__main__":
    port = 5006
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    # app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host="0.0.0.0", port=port)
    # app.run()
