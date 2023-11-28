import json
import os
from typing import Literal

from flask import Flask, Response, jsonify, request
from refined.inference.processor import Refined
from refined.inference.standalone_md import MentionDetector
from refined.data_types.base_types import Entity, Span
from refined.doc_preprocessing.candidate_generator import (
    CandidateGenerator,
    CandidateGeneratorExactMatch,
)
from refined.resource_management.data_lookups import LookupsInferenceOnly

app = Flask(__name__)

print("Loading Custom EL")
ENTITY_SET: Literal["wikipedia, wikidata"] = "wikipedia"
# TODO NL: extract single layer
refined = Refined.from_pretrained(
    model_name="wikipedia_model_with_numbers", entity_set="wikipedia"
)

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

generator = init_generator()

def add_mention(mention, offset, mentions_list):
    mention_object = {"mention": mention, "offset": offset, "possibleAssignments": []}
    mentions_list.append(mention_object)

def add_possible_assignment(score, assignment, possible_assignments_list):
    possible_assignment_object = {"score": score, "assignment": assignment}
    possible_assignments_list.append(possible_assignment_object)

def detect(text):
    """replace the following line with something like -> mentions = own_system.detect(text)"""

    # TODO: not load complete model every time

    result = refined.process_text(text)

    mentions = [{"text": span.text, "offset": span.start} for span in result]
    return mentions

def generate_candidates(mention):
    possible_assignments = []

    text = mention["mention"]
    candidates, _ = generator.get_candidates(text)
    for idx, score in candidates:
        if score == 0:
            break
        possible_assignments.append({"score": score, "assignment": idx})

    return possible_assignments


def add_assignment(score, assignment, mention):
    if not "assignment" in mention:
        mention["assignment"] = {}
    mention["assignment"]["score"] = score
    mention["assignment"]["assignment"] = assignment

def create_span_by_mention(mention) -> Span:
    text = mention["mention"]
    offset = mention["offset"]

    return Span(
        text=text,
        start=offset,
        ln=offset + len(text),
        candidate_entities=[
            (Entity(wikidata_entity_id=cand["assignment"]), cand["score"])
            for cand in mention["possibleAssignments"]
        ],  # TODO Check if refined uses those candidates and not genereate their own
    )
def process(document):
    text = document["text"]

    # Mention detection
    # detect mentions with your own system
    # example
    mentions = detect(text)

    if document["mentions"] is None:
        document["mentions"] = []

    for mention in mentions:
        mention_text = mention["text"]
        mention_offset = mention["offset"]
        add_mention(mention_text, mention_offset, document["mentions"])

    # Candidate gen
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
    # Disambiguation


    result = refined.process_text(text, [create_span_by_mention(m) for m in mentions])

    assert len(mentions) == len(result)

    for idx, mention in enumerate(mentions):
        if mention["possibleAssignments"] is None or not mention["possibleAssignments"]:
            pass

        assignment = result[idx].predicted_entity

        assignment_score = 1  # TODO which score do not know if refined provides one
        assignment_value = assignment.wikidata_entity_id

        add_assignment(assignment_score, assignment_value, mention)


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


@app.route("/", methods=["get", "post"])
def index():
    print("Incoming request:")
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
    port = 5004
    print("Running app... on port: ", port)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    # app.run(host='0.0.0.0', port=80)
    # expose 0.0.0.0 - esp. important for docker
    app.run(host="0.0.0.0", port=port)
    # app.run()
