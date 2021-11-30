# Combining Linking Techniques (Docker version)

## How to run front-end
1. Clone Github repository & go into its root folder
```
 git clone https://github.com/kmdn/agnos_collab_docker.git
```

2. Run docker container(s)

	1. Run only front-end docker container
```
docker-compose up
```

	2. Run front-end incl. linker recommendation and spaCy mention detection docker container
```
docker-compose -f ./docker-compose-all.yml up
```

3. Access front-end via browser at
```
 localhost:8080/
```


## Structure explanations
/linker_recommender_api - API template for entity linker recommendation.

/spacy_md_api - API template for mention detection based on spaCy.

/evaluation_datasets - Evaluation data sets accessible through the framework front-end.

/img - Images for 

[CLiT Website](http://clit.tech)
[![CLiT Website](/img/clit_website_part_core.png)](http://clit.tech)



Demo Video(s)
-------------
![Setup and Intro to Simple & Standard Linkers](/videos/ESWC2021_Demo_Simple_Standard_Linkers.mov)

[![ESWC2021 Demo Complex Pipeline](/img/video_simple.PNG)](https://www.youtube.com/watch?v=FQMnaR5hE0k)


How to create a ![Complex Pipeline](/videos/ESWC2021_Demo_Complex_Pipeline.mov)
[![ESWC2021 Demo Complex Pipeline](/img/video_complex.PNG)](https://www.youtube.com/watch?v=3gLGFAUDkVo)

Classical Pipeline
------------------

While Entity Linking (EL) systems
vary in terms of approaches and potential steps within respective
pipelines, we identify the most commonly-employed ones as the *classical
pipeline*. We use said pipeline as a template for our framework in order
to reach compatibility with as many existing systems as possible. In the
figure below, we present our understanding of the
functioning of a classical pipeline for a single system.

![Classic pipeline](/img/classic_pipeline.png)

### Input Document

Representing the starting point of any annotation framework, an input
document consists of plain text of some form, generally not bringing any
additional information for systems to take into account. The document
may be part of an evaluation data set or simple text - in both cases
only text is given as information to the successive step.

### Mention Detection

  ------------- ------------------------------------------------------------------
     **Input:** Text Document
    **Output:** Collection of mentions and their locations within given document
  ------------- ------------------------------------------------------------------

Also referred to as *spotting*, this task refers to the detection of
so-called *mentions* within a given plain text. Depending on system,
different kinds of mentions may be detected. POS tagging, NER-based techniques and string-matching to
labels of specific types of entities from considered knowledge bases are
among potential techniques. Further information pertaining to the
mention is sometimes passed on to a system's consequent step. From the
given text, mentions are extracted and passed on to the following step.

### Candidate Generation

  ------------- ---------------------------------------------------
     **Input:** Collection of mentions
    **Output:** Collection of candidate entities for each mention
  ------------- ---------------------------------------------------

Receiving a list of mentions, the process of *candidate generation*
finds lists of appropriate entities for each passed mention. Some
approaches additionally rank candidates at this step e.g. in terms of
general importance based on statistical measures.

### Entity Disambiguation

  ------------- ---------------------------------------------------
     **Input:** Collection of candidate entities
    **Output:** Disambiguated entities, either collections ranked
                by likelihood or at most one per mention
  ------------- ---------------------------------------------------

Part of the pipeline potentially granting the most sophisticated
techniques. Generally, this step is based on statistical measures,
allowing for the synthetization of contexts based on detected mentions
and suggested candidates.

### Results

Finally, results from the given pipeline are returned. These tend to be
in the form of annotations based on the initial input document or as
hyperlinks referring to specific knowledge bases, such as
Wikipedia, DBpedia or Wikidata.
Occasionally, some systems add an additional step for *pruning*

Pipeline Customization
----------------------

In order to allow for customized experiences and settings, we introduce
further processing possibilities
with the intent of allowing for nigh-infinite combinations of system
components. The following **subcomponents** place themselves
ideologically *in between* components presented within the classical
model of an EL
pipeline. We refer to them as *processors* or *subcomponents*, handling
post-processing of structures output from prior tasks, preparing them
for being potentially, in turn, further processed by subsequent steps in
the chosen workflow. In this paper, we define 4 types of processors:
*splitter*s *combiner*s, *filter*s and *translator*s.

### Splitter

  ------------------- ---------------------------------------------------------------
     **Preceded by:** Any single-connected component
    **Succeeded by:** 2 or more components
        **Commonly:** Directly passing same information to two (or more) components
  ------------------- ---------------------------------------------------------------

Allowing for processing of items prior to passing them on to a
subsequent step, a splitter is utilised in the case of a single stream
of data being sent to multiple components, potentially warranting
specific splitting of data streams. This step encompasses both a
post-processing step for a prior component, as well as a pre-processing
step for a following one. A potential post-processing step may be to
filter information from a prior step, such as eliminating superfluous
candidate entities or unwanted mentions.

As for pre-processing, a splitter may preprocessing --> translate from
one KB to another allows for processing of entities resulting from a
prior st

### Combiner

  ------------------- -----------------------------------------------------------
     **Preceded by:** Any multiply-connected > 2 component or subcomponent
    **Succeeded by:** Any single component, *translator* or *filter*
        **Commonly:** *Union* operation, *intersection* operation
  ------------------- -----------------------------------------------------------

In case multiple components were utilised in a prior step and are meant
to be consolidated through a variety of possible combinations actions, a
*combiner* subcomponent must be utilised. It combines results from
multiple inputs into a single output, passing merged partial results on
to a subsequent component. Common operations include *union* - taking
information from multiple sources and adding it together - and
*intersection* - checking multiple sources for certainty of information
prior to passing it on.

### Filter

  ------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------
     **Preceded by:** Any component or subcomponent.
    **Succeeded by:** Any component or *translator*.
        **Commonly:** NER-, POS-specific or `rdf:type` filtering.
  ------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------

In order to allow removal of particular sets of items through
user-defined rules or dynamic filtering, we introduce a subcomponent
capable of processing results on binary classifiers: a *filter*. The
truth values evaluated on passed partial results define which further
outcomes may be detected by a subsequent component or translator.

### Translator

  ------------------- --------------------------------------------------------------------------------------
     **Preceded by:** Any component or subcomponent.
    **Succeeded by:** Any component or subcomponent.
        **Commonly:** `owl:sameAs` linking across KGs.
  ------------------- --------------------------------------------------------------------------------------

Enabling seamless use of annotation tools regardless of underlying KG, we introduce the
translator subcomponent. It is meant as a processing unit capable of
translating entities and potentially other features used by one tool to
another, allowing further inter-system compatibility. It may be employed
at any level and succeeded by any (sub)component due to its ubiquitous
characteristics and necessity when working with heterogeneous systems.


Pipeline Examples
-----------------

Example of a simple EL pipeline with a processor component, translating from Wikidata to DBpedia entities:

![Simple pipeline graph](/img/pipeline_graph_simple.png)

Example of an advanced EL pipeline with a splitter and a combiner, merging the results of the mention detection of three different EL systems:

![Advanced pipeline graph](/img/pipeline_graph_advanced.png)


Protocol Development
--------------------

For the formal definition of a pipeline we use JSON.
A pipeline configuration consists of an *ID*, the *pipeline type*, a list of *components* for each component type, and a list of *connections* between the components.
Each component list consists of key-value-pairs, where the key is the ID of the component, and the value defines either the EL system used for this component, or in case of the *processors*, it defines their type.
Slightly differently, for the connection list the key represents the source and the value the target component of the connection.
An example of a JSON configuration for a simple pipeline (that corresponds to the simple pipeline in the former of the figures above) looks like this:

```
pipelineConfig = {
	"id": 123,
	"pipelineType": "complex",
	"md": [
		{"MD1": "Babelfy"} ],
	"cg": [
		{"CG1": "DBpediaSp"} ],
	"ed": [
		{"ED1": "AIDA"} ],
	"combiners": [],
	"splitters": [],
	"translators": [
		{"TR1": "WD2DBP"} ],
	"filters": [],
	"connections": [
		{"MD1": "CG1"},
		{"CG1": "ED1"},
		{"ED1": "TR1"} ]
}
```

