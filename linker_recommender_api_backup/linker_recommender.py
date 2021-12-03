from flask import Flask, request, Response, jsonify
#import pprint
import json
# to load classifier and topic model
import joblib
#from joblib import load

# create feature vectors to train with
import numpy as np
import re
import spacy
from numpy import mean
import gensim
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')


app = Flask(__name__)

# https://spacy.io/usage/models
# python -m spacy download en_core_web_sm
_nlp = spacy.load("en_core_web_sm") # is faster
#_nlp = spacy.load("en_core_web_trf") # performs better

# Load recommender model
model_path = './models/label_features_f1.csv.model'
model = joblib.load(model_path)
# load labels
labels = joblib.load(model_path + '.labels')
# Load LDA topic model
lda_model = joblib.load('./models/lda.model')


# Run with
# <s>flask run --port=5002</s>
# TODO Didn't work with spaCy, use
# python app.py

# Test with
# curl http://127.0.0.1:5002/ --header "Content-Type: application/json" --request POST -d '{"document" : {"text": "", "mentions": []}, "pipelineConfig" : "<config>", "componentId" : "123"}'



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#                                           START PREDICTION CODE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


ner_label_positions = ["CARDINAL","DATE","EVENT","FAC","GPE","LANGUAGE","LAW","LOC","MONEY","NORP","ORDINAL","ORG","PERCENT","PERSON","PRODUCT","QUANTITY","TIME","WORK_OF_ART"]

stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
# Adding email-related stopwords...
stop_words.extend(['new', 'subject', 'email', 'ascii', 'plain', 'text', 'type', 'message', 'id', 'message', 'id', 'javamail', 'evans', 'thyme', 'date', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'sep', 'pdt', 'theresa', 'connor', 'smith', 'enron', 'com', 'kenneth', 'lay', 'enron', 'com', 'confidential', 'question', 'mime', 'version', 'content', 'charset', 'us', 'content', 'transfer', 'encoding', 'bit'])
id2word = joblib.load('./models/id2word.dictionary')
header = joblib.load('./models/header.labels')




def document_characteristics(doc=""):
    vector_document_feature = []
    # document length
    if doc is None:
        doc = ""
    vector_document_feature.append(len(doc))
    # number of tokens - regex
    tokens_re = re.split('\\s+', doc)
    # if tokens_split is empty... add an entry
    if (tokens_re is None or len(tokens_re) == 0):
        tokens_re = [""]
    vector_document_feature.append(len(tokens_re))
    # max token length
    vector_document_feature.append(max([len(x) for x in tokens_re]))
    # min token length
    vector_document_feature.append(min([len(x) for x in tokens_re]))
    # avg
    vector_document_feature.append(mean([len(x) for x in tokens_re]))
    # number of tokens - basic split
    tokens_split = doc.split()
    vector_document_feature.append(len(tokens_split))
    
    
    # if tokens_split is empty... add an entry
    if (tokens_split is None or len(tokens_split) == 0):
        tokens_split = [""]
    # max token length
    vector_document_feature.append(max([len(x) for x in tokens_split]))
    # min token length
    vector_document_feature.append(min([len(x) for x in tokens_split]))
    # avg
    vector_document_feature.append(mean([len(x) for x in tokens_split]))
    # spacy
    spacy_doc = _nlp(doc)
    mentions = []
    # initialise distribution with zeros
    ner_label_distribution = [0 for ner_label in ner_label_positions]
    for ent in spacy_doc.ents:
        #print(f'[{ent.start_char}:{ent.end_char}] {ent.text} ({ent.label_})')
        #mention = spacy_ent_to_mention(ent)
        ner_label_index = ner_label_positions.index(ent.label_)
        # Increment distribution counter by one
        ner_label_distribution[ner_label_index] = ner_label_distribution[ner_label_index] + 1 
        #mentions.append(ent)
        #print(ent)
        #print(ent.text, ent.start_char, ent.end_char, ent.label_)
    #print(ner_label_distribution)
    #print(f'Detected {len(mentions)} mentions')

    # Add document's NER class distribution to the feature vector
    vector_document_feature.extend(ner_label_distribution)

    # Add sum of NER classes to doc features
    vector_document_feature.append(sum(ner_label_distribution))
    
    # Add avg (by distribution) of NER classes to doc features
    vector_document_feature.append(mean(ner_label_distribution))

    # Add avg (by token count) of NER classes to doc features
    vector_document_feature.append(sum(ner_label_distribution)/len(tokens_split))
    
    #print(vector_document_feature)
    
    return vector_document_feature
    
    
def sent_to_words(sentences):
    for sentence in sentences:
        # deacc=True removes punctuations
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))
    
    
def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) 
             if word not in stop_words] for doc in texts]

    
def process_document_texts(docs=[""], display_some=True, lda_model=None):
    data_words = list(sent_to_words([doc.split(' ') if doc is not None else "" for doc in docs]))

    # print(data_words)
    # remove stop words
    data_words = remove_stopwords(data_words)

    # Term Document Frequency
    corpus = [id2word.doc2bow(doc) for doc in data_words]

    # View
    #print(corpus[:1][0][:30])
    if display_some:
        for index, doc in enumerate(corpus):
            #0 [(0, 0.050012715), (1, 0.050015952), (2, 0.050007522), (3, 0.54990005), (4, 0.050010785), (5, 0.05000899), (6, 0.05000739), (7, 0.050011847), (8, 0.050007924), (9, 0.05001683)]
            print(index, lda_model.get_document_topics(doc))
            # Only display first 100
            if index >= 100:
                break

    return corpus, data_words


def create_feature_vectors(lda_model, input_docs=[], display_some=True):
    corpus, data_words = process_document_texts(input_docs, display_some=display_some, lda_model=lda_model)

    all_features = []#np.empty(1)#np.array([])
    for index, doc in enumerate(corpus):
        vector_feature = []
        # the n topic dimensions for each document
        # print(index, lda_model.get_document_topics(doc))
        topic_vector = np.zeros(lda_model.num_topics)
        for topic in lda_model.get_document_topics(doc):
            topic_vector[topic[0]] = topic[1]
        # print(topic_vector)
        vector_feature.extend(topic_vector)

        # document characteristics...
        # document content: print(docs[index])
        vector_document_feature = document_characteristics(input_docs[index])
        vector_feature.extend(vector_document_feature)

        # Add this feature vector to the list of all feature vectors
        all_features.append(vector_feature)
    return all_features


def recommend_linkers(model=None, doc="Hello world"):
    text_docs = [doc]
    X_features = create_feature_vectors(lda_model=lda_model, input_docs=text_docs, display_some=False)
    #print("Features: ", X_features)
    y_pred = model.predict(X_features)
    #print("Predicting: ", y_pred)
    linkers = [labels[index] for index, val in enumerate(y_pred[0]) if val != 0]
    return linkers


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#                                           END PREDICTION CODE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


def process(doc):
    text = doc['text']
    recommended_linkers = recommend_linkers(model=model, doc=text)
    print("Labels: ",labels)
    mentions = [{'offset':0, 'mention': linker} for linker in recommended_linkers]
    doc['mentions'] = mentions
    return doc


@app.route('/', methods=['get', 'post'])
def index():
    print(request.data)
    req = json.loads(request.data)
    document = req['document']
    pipelineConfig = req['pipelineConfig']
    componentId = req['componentId']
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
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5002)
    #app.run()
