import json
import rdflib
import hashlib
import urllib
import pickle

baseurl = "http://intranet-v2.eurecom.fr/data/"

#Previous geocoding results are saved to disk to be reused
try:
	f = open('cityPickle', 'r')
except IOError:
	cities = {}
else:
	try:
		cities = pickle.load(f)
		print "Nb of city records : " + str(len(cities))
		f.close()
	except EOFError:
		cities = {}

#Same with places that couldn't be found...
#These should be processed manually
try:
	f = open('unknownPlacesPickle', 'r')
except IOError:
	unknownPlaces = set()
else:
	try:
		unknownPlaces = pickle.load(f)
		print "Nb of unknown places : " + str(len(unknownPlaces))
		f.close()
	except EOFError:
		unknownPlaces = set()
		
FOAF = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
RDF = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
DCT = rdflib.Namespace("http://purl.org/dc/terms/")
XSD = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")
PART = rdflib.Namespace("http://purl.org/vocab/participation/schema#")
ROOMS = rdflib.Namespace("http://vocab.deri.ie/rooms#")
LODE = rdflib.Namespace("http://linkedevents.org/ontology/")
TIME = rdflib.Namespace("http://www.w3.org/2006/time#")
AIISO = rdflib.Namespace("http://purl.org/vocab/aiiso/schema#")
BIBO = rdflib.Namespace("http://purl.org/ontology/bibo/")
REVE = rdflib.Namespace("http://data.eurecom.fr/ontology/reve#")
TL = rdflib.Namespace("http://purl.org/NET/c4dm/timeline.owl#")
LED_COURSE = rdflib.Namespace("http://data.eurecom.fr/course/")
LED_SEMESTER = rdflib.Namespace("http://data.eurecom.fr/semester/")
LED_PEOPLE = rdflib.Namespace("http://data.eurecom.fr/people/")
LED_PUB = rdflib.Namespace("http://data.eurecom.fr/publication/")
LED_SESSION = rdflib.Namespace("http://data.eurecom.fr/session/")
LED_ROOM = rdflib.Namespace("http://data.eurecom.fr/room/")
LED_TRACK = rdflib.Namespace("http://data.eurecom.fr/track/")
LED_ROLE = rdflib.Namespace("http://data.eurecom.fr/role/")
LED_EVENT = rdflib.Namespace("http://data.eurecom.fr/event/")
GEO = rdflib.Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

#Preparation des graphes
#g = rdflib.ConjunctiveGraph()
gCourses = rdflib.ConjunctiveGraph()
gSemesters = rdflib.ConjunctiveGraph()
gPeople = rdflib.ConjunctiveGraph()
gPubs = rdflib.ConjunctiveGraph()
gSessions = rdflib.ConjunctiveGraph()
gRooms = rdflib.ConjunctiveGraph()
gTracks = rdflib.ConjunctiveGraph()
gRoles = rdflib.ConjunctiveGraph()
gEvents = rdflib.ConjunctiveGraph()
gGeo = rdflib.ConjunctiveGraph()

#PUBLICATIONS

geoCodeFail = 0
urlopenFail = 0

gPubs.parse("publications.rdf")
print "Length of gPubs : " + str(len(gPubs))

for year in range(1992, 2013):
	request = baseurl + "publication/" + str(year) + "/list.json"
	try:
		page = urllib.urlopen(request)
	except IOError as (errno, strerror):
		print "I/O error({0}): {1}".format(errno, strerror)
		print request
	else:						
		try:
			response = json.load(page)
		except ValueError:
			print "Could not parse json file: " + request
		else:
			r = response[u'response']
			for pub in r:
				publi = LED_PUB[str(pub[u'id'])]
				if pub[u'source'] != None:
					n = hashlib.md5(pub[u'source'].encode('utf-8')).hexdigest()
					event = LED_EVENT[n]
					gPubs.add((publi, BIBO["presentedAt"], event))
					gEvents.add((event, RDF["type"], BIBO["Conference"]))
					gEvents.add((event, RDFS["label"], rdflib.Literal(pub[u'source'])))
				
					interval = rdflib.BNode()
					gEvents.add((interval, RDF["type"], TIME["Interval"]))
					gEvents.add((interval, TL["atDate"], rdflib.Literal(pub[u'publisheddate'], datatype=rdflib.namespace.XSD.date)))
					gEvents.add((event, LODE["atTime"], interval))
				
					key = (pub[u'country'][u'id'][-2:], pub[u'city'])
				
					if key in cities:
						geoID = cities[key]['id']
						lat = cities[key]['lat']
						lng = cities[key]['lng']
						place = rdflib.URIRef('http://sws.geonames.org/' + str(geoID))
						gEvents.add((event, LODE['atPlace'], place))
						#Keep a copy of lat and long, since we retrieve it
						#(would be more logical to get it from the geonames sparql endpoint, though :))
						gGeo.add((place, RDF['type'], GEO['SpatialThing']))
						gGeo.add((place, GEO['lat'], rdflib.Literal(str(lat))))
						gGeo.add((place, GEO['long'], rdflib.Literal(str(lng))))
					else:
						if key in unknownPlaces:
							pass
						else:
							if pub[u'city'] == None:
								request = 'http://ws.geonames.org/searchJSON?country=' + pub[u'country'][u'id'][-2:] + '&maxRows=1'
							else:
								request = 'http://ws.geonames.org/searchJSON?q=' + urllib.quote(pub[u'city'].encode('utf-8')) + '&country=' + pub[u'country'][u'id'][-2:] + '&maxRows=1'
					
							try:
								page = urllib.urlopen(request)
							except IOError as (errno, strerror):
								print "I/O error({0}): {1}".format(errno, strerror)
								urlopenFail += 1
							else:	
								try:
									response = json.load(page)
								except ValueError:
									print "Could not parse json file: " + request
								else:
									try:
										geoID = response[u'geonames'][0][u'geonameId']
										lat = response[u'geonames'][0][u'lat']
										lng = response[u'geonames'][0][u'lng']
										cities[(pub[u'country'][u'id'][-2:], pub[u'city'])] = {'id':geoID, 'lat':lat, 'lng':lng}
										f = open('cityPickle', 'w')
										pickle.dump(cities, f)
										f.close()
										place = rdflib.URIRef('http://sws.geonames.org/' + str(geoID))
										gEvents.add((event, LODE['atPlace'], place))
										gGeo.add((place, GEO['lat'], rdflib.Literal(lat)))
										gGeo.add((place, GEO['long'], rdflib.Literal(lng)))
									except IndexError:
										geoCodeFail += 1
										unknownPlaces.add((pub[u'country'][u'id'][-2:], pub[u'city']))
										print "Failed to geocode for " + str((pub[u'country'][u'id'][-2:], pub[u'city']))
				else: #no source
					pass

print "Nb of geocoding failures : " + str(geoCodeFail)
print "Nb of urlopen pbs : " + str(urlopenFail)

f = open('cityPickle', 'w')
pickle.dump(cities, f)
print "Nb of city records : " + str(len(cities))
f.close()

f = open('unknownPlacesPickle', 'w')
pickle.dump(unknownPlaces, f)
print "Nb of unknown places : " + str(len(unknownPlaces))
f.close()

print "Length of gPubs : " + str(len(gPubs))
print "Nb of publications : " + str(len(list(gPubs.triples((None, RDF["type"], FOAF["Document"])))))
outfile = open("publications.rdf", "w")
outfile.write(gPubs.serialize())
outfile.close()

print "Length of gEvents : " + str(len(gEvents))
print "Nb of conferences : " + str(len(list(gEvents.triples((None, RDF["type"], BIBO["Conference"])))))
outfile = open("events.rdf", "w")
outfile.write(gEvents.serialize())
outfile.close()

outfile = open("geo.rdf", "w")
outfile.write(gGeo.serialize())
outfile.close()
