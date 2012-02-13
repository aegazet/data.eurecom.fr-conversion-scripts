from SPARQLWrapper import SPARQLWrapper, JSON
import json

# --- PUBLICATIONS ---

sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/Eurecom")
sparql.setQuery("""
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX reve:<http://data.eurecom.fr/ontology/reve#>
PREFIX dct:<http://purl.org/dc/terms/>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
PREFIX aiiso:<http://purl.org/vocab/aiiso/schema#>
PREFIX part:<http://purl.org/vocab/participation/schema#>
PREFIX lode:<http://linkedevents.org/ontology/>
PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX bibo:<http://purl.org/ontology/bibo/>
PREFIX time:<http://www.w3.org/2006/time#>

SELECT DISTINCT ?pub ?title ?date ?conf ?conf_title ?lat ?long ?author
WHERE {
?pub rdf:type foaf:Document .
?pub dct:title ?title .
?pub dct:date ?date .
?pub bibo:presentedAt ?conf .
?conf rdfs:label ?conf_title .
?conf lode:atPlace ?place .
?place geo:lat ?lat .
?place geo:long ?long .
?pub dct:creator ?author
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

d = {'items':[], 
	"properties":
	{
		"author": { "valueType": "item" },
		"conf": { "valueType": "item" },
		"date": { "valueType": "date" }
	},
	"types": {
           "Document" : {
               "pluralLabel": "Documents"
           }
	}
    }

for result in results["results"]["bindings"]:
	item = {}
	item['type'] = 'Document'
	item['label'] = result['title']['value']
	item['id'] = result['pub']['value']
	conf_item = {}
	conf_item['type'] = 'Conference'
	conf_item['label'] = result['conf_title']['value']
	conf_item['id'] = result['conf']['value']
	conf_item['lat'] = result['lat']['value']
	conf_item['long'] = result['long']['value']
	for field in ['date', 'author', 'conf']:
		item[field] = result[field]['value']
	d['items'].append(item)
	d['items'].append(conf_item)

#f = open("pub_results.js", "w")
#f.write(json.dumps(d, sort_keys=True, indent=4))
#f.close()

# --- AUTHORS ---

sparql.setQuery("""
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX reve:<http://data.eurecom.fr/ontology/reve#>
PREFIX dct:<http://purl.org/dc/terms/>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
PREFIX aiiso:<http://purl.org/vocab/aiiso/schema#>
PREFIX part:<http://purl.org/vocab/participation/schema#>
PREFIX lode:<http://linkedevents.org/ontology/>
PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX bibo:<http://purl.org/ontology/bibo/>
PREFIX time:<http://www.w3.org/2006/time#>

SELECT DISTINCT ?author ?fn ?ln ?roletype ?depname
WHERE {
?pub rdf:type foaf:Document .
?pub dct:creator ?author .
?author foaf:firstName ?fn .
?author foaf:lastName ?ln .
?author part:holder_of ?role . ?role rdf:type ?roletype . 
OPTIONAL {?role part:role_at ?dep . ?dep rdfs:label ?depname}
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

#d = {'items':[], 
#	"properties":
#	{
#		"author": { "valueType": "item" }
#	}}

for result in results["results"]["bindings"]:
	item = {}
	item['type'] = 'Person'
	item['label'] = result['ln']['value'] + ', ' + result['fn']['value']
	item['id'] = result['author']['value']
	item['uri'] = result['author']['value']
	if 'depname' in result:
		item['dep'] = result['depname']['value']
	if 'roletype' in result:
		if result['roletype']['value'] == 'http://data.eurecom.fr/ontology/reve#Teacher':
			item['role'] = 'Teacher'
		if result['roletype']['value'] == 'http://data.eurecom.fr/ontology/reve#Researcher':
			item['role'] = 'Researcher'
		if result['roletype']['value'] == 'http://data.eurecom.fr/ontology/reve#DoctoralStudent':
			item['role'] = 'Doctoral Student'
	d['items'].append(item)

#f = open("authors_results.js", "w")
f = open("exhibit-data.js", "w")
f.write(json.dumps(d, sort_keys=True, indent=4))
f.close()

