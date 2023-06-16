# Combining Linking Techniques (Docker version)

## How to run
0. Requirements
	1. [Git](https://git-scm.com/downloads)
	2. [Docker / docker-compose](https://www.docker.com/)

1. Clone Github repository and all the submodules & go into its root folder.
	1. Execute command
	```
	 git clone --recurse-submodules https://github.com/kmdn/combining-linking-techniques && cd combining-linking-techniques
	```

	2. In case git gives you "over data quota" issues, you may clone (non-LFS data) with - this will not download benchmark data sets:
	```
	GIT_LFS_SKIP_SMUDGE=1 git clone --recurse-submodules https://github.com/kmdn/combining-linking-techniques.git && cd combining-linking-techniques
	```

2. Run front-end

	1. Option 1: Run only simple front-end
		```
		docker-compose up
		```

	2. Option 2: Run front-end incl. following docker containers:

		1. linker recommendation. (Executed by default when no linker is chosen.)
		2. spacy mention detection. (Default when adding IP-based API.)
		```
		docker-compose -f ./docker-compose-all.yml up
		```

## Build yourself
0. Requirements
	1. [Git](https://git-scm.com/downloads)
	2. [Docker / docker-compose](https://www.docker.com/)
	3. [Maven](https://maven.apache.org/download.cgi)
	4. An internet browser and open ports.

1. Clone Github repository & go into its root folder.
```
 git clone --recurse-submodules https://github.com/kmdn/combining-linking-techniques && cd combining-linking-techniques
```

2. Build with Maven (Note: issues may arise depending on local mvn settings, hence we recommend the first step)
	1. Build clit_backend
	```
	cd clit_backend && mvn clean install -Dmaven.wagon.http.ssl.insecure=true -Dmaven.wagon.http.ssl.allowall=true -Dmaven.wagon.http.ssl.ignore.validity.dates=true && cd ..
	```
	
	2. Build clit_frontend (relies on backend)
	```
	cd clit_frontend && mvn clean install && cd ..
	```

3. Build & run docker container(s).

	1. Run only front-end docker container.
	```
	docker-compose -f ./docker-compose-build.yml up
	```

	2. Run front-end incl. following docker containers. Note: Building Python dependencies may take a while.
		1. linker recommendation. (Executed by default when no linker is chosen.)
		2. spacy mention detection. (Default when adding IP-based API.)
		```
		docker-compose -f ./docker-compose-build-all.yml up
		```

3. Access front-end via browser at address:
```
 localhost:8080/
```


## Repository structure
*/linker_recommender_api*

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;API template for entity linker recommendation.


*/spacy_md_api*

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;API template for mention detection based on spaCy.


*/evaluation_datasets*

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Evaluation data sets accessible through the framework front-end.


*/img*

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Images for README.md




## [CLiT Website (barebone)](http://clit.tech:8080)
[![CLiT Website](/img/clit_website_part_core.png)](http://clit.tech:8080)



## Tutorials and Videos
-------------
Tutorials will be made available at https://github.com/kmdn/clit-tutorials

For videos regarding the use of our framework, we refer to the following public YouTube playlist: 
https://www.youtube.com/playlist?list=PLjJ1ICImS5q7D3k6bLGSUts_qEgtlVJnO


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
	 **Description:** Splits results from components in intelligent ways (e.g. person-type entities to ).
     **Preceded by:** Any single-connected component.
    **Succeeded by:** 2 or more components.
        **Commonly:** Directly passing same information to two (or more) components.
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
	 **Description:** Combines results from components in intelligent ways.
     **Preceded by:** Any multiply-connected ≥ 2 component or subcomponent.
    **Succeeded by:** Any single component, *translator* or *filter*.
        **Commonly:** *Union* operation, *intersection* operation.
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
	 **Description:** Removes certain parts of information. Aims to facilitate further downstream processing.
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
	 **Description:** 'Translates' entities from one KB to another (e.g. from Wikipedia to Wikidata).
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


## JSON Result structure
Pipeline Results:
```
	JSONObject{
		"experimentId": int,
		"experimentTasks": 
			JSONArray[
				EXPERIMENTS
			]
	}
```	

EXPERIMENTS:
```	
	JSONObject{
		"currentComponent": String,
		"documents": 
			JSONArray[
				DOCUMENTS
			],
		"pipelineConfig": 
			PIPELINE,
		"errorMessage": String,
		"experimentId": int,
		"state": String (e.g. "DONE"),
		"pipelineType": String (e.g. "FULL"),
		"taskId": int
	}

```	

DOCUMENTS: 
```	
	JSONArray[			-- need double JSONArray in order to store sub-pipeline results for each document
		JSONObject{
			"componentId": String,
			"mentions": 
				JSONArray[
					MENTIONS
				],
			"text": String (e.g. "Napoleon was the emperor of the First French Empire."),
			"pipelineType": String (e.g. "ED"),
			"uri": String
		}
	]
```	

MENTIONS:
```	
	JSONObject{
		"offset": int,
		"assignment": 
			JSONObject{
				"score": double,
				"assignment": String (e.g. "http://dbpedia.org/resource/Empire")
			},
			"possibleAssignments": 
				JSONArray[
					JSONObject{
						"score": double, 
						"assignment": String
					}
				]
		},
		"originalWithoutStopwords": String (e.g. "Empire"),
		"detectionConfidence": double (e.g. 0.0),
		"originalMention": String (e.g. "Empire"),
		"mention": String (e.g. "Empire")
	}
```	

PIPELINE:
```	
	JSONObject{
		"startComponents": 
			JSONArray[
				String (e.g. "MD1")
			],
		"components": 
			JSONObject{
				"md" (Only if present. May be: md, cg, ed, md_cg_ed, md_cg, cg_ed, ...):
					JSONArray[
						JSONObject{
							"id": String (e.g. "MD1"; ID matches w/ IDs in connections),
							"value": String (e.g. "Babelfy")
						}
					],

				"cg_ed" (IF PRESENT): 
					JSONArray[
						JSONObject{
							"id": String (e.g. "CG_ED1"),
							"value": String (e.g. "Babelfy")
						}
					]
			},
		"exampleId": String (e.g. "md_combined_cged"),
		"endComponents": 
			JSONArray[
				String (e.g. "CG_ED1", "MD1")
			],
		"displayName": String (e.g. "MD + combined CG-ED"),
		"id": int (e.g. 1),
		"connections":
			JSONArray[
				JSONObject{
					"source": String (e.g. "MD1"),
					"target": String (e.g. "CG_ED1")
				}
			],
		"pipelineConfigType": String (e.g. "complex")
	}
```	


