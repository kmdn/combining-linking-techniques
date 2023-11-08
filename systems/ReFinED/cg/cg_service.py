import json
import os
from typing import Literal

from flask import Flask, Response, jsonify, request
from refined.doc_preprocessing.candidate_generator import (
    CandidateGenerator,
    CandidateGeneratorExactMatch,
)
from refined.resource_management.data_lookups import LookupsInferenceOnly

app = Flask(__name__)
ENTITY_SET: Literal["wikipedia, wikidata"] = "wikipedia"

print("Loading Custom CG")


def init_generator() -> CandidateGenerator:
    lookups = LookupsInferenceOnly(
        data_dir=os.path.join(os.path.expanduser("~"), ".cache", "refined"),
        entity_set=ENTITY_SET,
        use_precomputed_description_embeddings=True,
        return_titles=False,
    )

    candidate_generator: CandidateGenerator = CandidateGeneratorExactMatch(
        max_candidates=30,
        pem=lookups.pem,
        human_qcodes=lookups.human_qcodes,
    )

    return candidate_generator


def add_possible_assignment(score, assignment, possible_assignments_list):
    possible_assignment_object = {"score": score, "assignment": assignment}
    possible_assignments_list.append(possible_assignment_object)


def process(document):
    mentions = document["mentions"]

    for mention in mentions:
        if mention["possibleAssignments"] is None or mention["possibleAssignments"] == [
            None
        ]:
            mention["possibleAssignments"] = []

        # replace the following line with something like -> possible_assignments = own_system.get_candidates(mention)
        # example

        possible_assignments = generate_candidates(mention)

        for possibleAssignment in possible_assignments:
            assignment_score = possibleAssignment["score"]
            assignment_value = possibleAssignment["assignment"]

            add_possible_assignment(
                assignment_score, assignment_value, mention["possibleAssignments"]
            )


def generate_candidates(mention):
    possible_assignments = []

    text = mention["mention"]
    generator = init_generator()
    # TODO: not load complete model every time
    candidates, _ = generator.get_candidates(text)
    for idx, score in candidates:
        if score == 0:
            break
        possible_assignments.append({"score": score, "assignment": idx})

    return possible_assignments


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


@app.route("/", methods=["get", "post"])
def index():
    print("Incoming request:")
    print(request.data)
    req = json.loads(request.data)
    document = req["document"]

    process(document)

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
    port = 5005
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    # app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host="0.0.0.0", port=port)
# app.run()
