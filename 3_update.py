import urllib
import httplib2
import os.path

# Change this to adapt to the destination repository
repository = 'Eurecom'
endpoint = "http://localhost:8080/openrdf-sesame/repositories/%s/statements" % (repository)
headers = { 
  'content-type': 'application/x-www-form-urlencoded', 
  'accept': 'application/sparql-results+json' 
}

# --- TO BE CHANGED : query the external geonames dataset instead, once they setup an official sparql endpoint ? ---
# ----- GEO -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/geo/>""" % (os.path.abspath("geo.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- COURSES -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/course/>""" % (os.path.abspath("courses.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- SEMESTERS -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/semester/>""" % (os.path.abspath("semesters.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- PEOPLE -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/people/>""" % (os.path.abspath("people.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- PUBLICATIONS -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/publication/>""" % (os.path.abspath("publications.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- COURSES SESSIONS -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/session/>""" % (os.path.abspath("sessions.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- ROOMS -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/room/>""" % (os.path.abspath("rooms.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- TRACKS -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/track/>""" % (os.path.abspath("tracks.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- ROLES -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/role/>""" % (os.path.abspath("roles.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- DEPARTMENTS -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/department/>""" % (os.path.abspath("departments.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status

# ----- EVENTS -----
update = """LOAD <file://%s> INTO GRAPH <http://data.eurecom.fr/event/>""" % (os.path.abspath("events.rdf"))
print update
params = { 'queryLn': "SPARQL", 'update': update }
(response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
print "Response %s" % response.status
