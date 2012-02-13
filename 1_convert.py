import json
import rdflib
import glob
import urllib

types = {}
#jsonDataFolder = "/home/zabou/SemesterProject/jsonData4"
baseurl = "http://intranet-v2.eurecom.fr/data/"

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
LED_DEP = rdflib.Namespace("http://data.eurecom.fr/department/")

#Preparation des graphes
gCourses = rdflib.ConjunctiveGraph()
gSemesters = rdflib.ConjunctiveGraph()
gPeople = rdflib.ConjunctiveGraph()
gPubs = rdflib.ConjunctiveGraph()
gSessions = rdflib.ConjunctiveGraph()
gRooms = rdflib.ConjunctiveGraph()
gTracks = rdflib.ConjunctiveGraph()
gRoles = rdflib.ConjunctiveGraph()
gDeps = rdflib.ConjunctiveGraph()

# ----- COURSES -----

for year in range(2004, 2013):
	request = baseurl + "course/" + str(year) + "/list.json"
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
			for course in r:
				period = course[u'periodList'][0]
				ind = LED_COURSE[str(period[u'id'])]
				gCourses.add((ind, RDF["type"], REVE["Course"]))
				gCourses.add((ind, RDFS["label"], rdflib.Literal(period[u'display_value'], lang=u'en')))
				gCourses.add((ind, AIISO["code"], rdflib.Literal(period[u'code'])))
				gCourses.add((ind, DCT["abstract"], rdflib.Literal(period[u'abstract_en'])))
				gCourses.add((ind, DCT["description"], rdflib.Literal(period[u'description_en'])))
				gCourses.add((ind, REVE["availableDuring"], LED_SEMESTER[period[u'period'][u'name']]))
				gSemesters.add((LED_SEMESTER[period[u'period'][u'name']], RDF["type"], REVE["Semester"]))
				gSemesters.add((LED_SEMESTER[period[u'period'][u'name']], REVE["hasAvailableCourse"], ind))
				gSemesters.add((LED_SEMESTER[period[u'period'][u'name']], RDFS["label"], rdflib.Literal(period[u'period'][u'name'])))
				
				if period[u'category'] == u'General Teaching':
					gCourses.add((ind, RDF["type"], REVE["GeneralCourse"]))
				if period[u'category'] == u'Technical Teaching':
					gCourses.add((ind, RDF["type"], REVE["TechnicalCourse"]))
				
				for contributor in period[u'contributorList']:
					people = contributor[u'role'][u'people']
					gPeople.add((LED_PEOPLE[str(people[u'id'])], RDF["type"], FOAF["Person"]))
					gPeople.add((LED_PEOPLE[str(people[u'id'])], FOAF["firstName"], rdflib.Literal(people[u'firstname'])))
					gPeople.add((LED_PEOPLE[str(people[u'id'])], FOAF["lastName"], rdflib.Literal(people[u'lastname'])))
					gPeople.add((LED_PEOPLE[str(people[u'id'])], AIISO["responsibleFor"], ind))
					gCourses.add((ind, AIISO["responsibilityOf"], LED_PEOPLE[str(people[u'id'])]))



# ----- PUBLICATIONS -----

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
				ind = LED_PUB[str(pub[u'id'])]
				gPubs.add((ind, RDF["type"], FOAF["Document"]))
				gPubs.add((ind, DCT["date"], rdflib.Literal(pub[u'publisheddate'], datatype=rdflib.namespace.XSD.date)))
				gPubs.add((ind, DCT["title"], rdflib.Literal(pub[u'title'])))
				gPubs.add((ind, REVE["referenceAtEurecom"], rdflib.Literal(pub[u'code'])))
				
				for author in pub[u'authorList']:
					person = LED_PEOPLE[str(author[u'role'][u'people'][u'id'])]
					gPeople.add((person, RDF["type"], FOAF["Person"]))
					role = LED_ROLE[str(author[u'role'][u'id'])]
					gRoles.add((role, RDF["type"], PART["Role"]))
					if author[u'role'][u'type'] == u'teacher':
						gRoles.add((role, RDF["type"], REVE["Teacher"]))
					if author[u'role'][u'type'] == u'researcher':
						gRoles.add((role, RDF["type"], REVE["Researcher"]))
					if author[u'role'][u'type'] == u'phd':
						gRoles.add((ind, RDF["type"], REVE["DoctoralStudent"]))
					gPeople.add((person, PART["holder_of"], role))
					gPeople.add((person, FOAF["firstName"], rdflib.Literal(author[u'role'][u'people'][u'firstname'])))
					gPeople.add((person, FOAF["lastName"], rdflib.Literal(author[u'role'][u'people'][u'lastname'])))
					gPubs.add((ind, DCT["creator"], person))
			
			
# ----- COURSE SESSIONS -----
coursesessions = {}
sessionsWithoutTeacher = []
sessionsWithoutRoom = []

for year in range(2004, 2013):
	request = baseurl + "course/" + str(year) + "/session/list.json"
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
			for course in r:
				for period in course[u'periodList']:
					ind_course = LED_COURSE[str(period[u'id'])]
					gCourses.add((ind_course, RDF["type"], REVE["Course"]))
					gCourses.add((ind_course, RDFS["label"], rdflib.Literal(period[u'display_value'], lang=u'en')))
					gCourses.add((ind_course, AIISO["code"], rdflib.Literal(period[u'code'])))
					gCourses.add((ind_course, REVE["availableDuring"], LED_SEMESTER[period[u'period'][u'name']]))
					gSemesters.add((LED_SEMESTER[period[u'period'][u'name']], RDF["type"], REVE["Semester"]))
					gSemesters.add((LED_SEMESTER[period[u'period'][u'name']], REVE["hasAvailableCourse"], ind_course))
					gSemesters.add((LED_SEMESTER[period[u'period'][u'name']], RDFS["label"], rdflib.Literal(period[u'period'][u'name'])))
				
					for session in period[u'sessionList']:
						ind = LED_SESSION[str(session[u'id'])]
						gSessions.add((ind, RDF["type"], REVE["CourseSession"]))
						gSessions.add((ind, REVE["isConstituentOf"], ind_course))
						gCourses.add((ind_course, REVE["hasConstituent"], ind))
					
						interval = rdflib.BNode()
						beginInstant = rdflib.BNode()
						endInstant = rdflib.BNode()
						gSessions.add((interval, RDF["type"], TIME["ProperInterval"]))
						gSessions.add((beginInstant, RDF["type"], TIME["Instant"]))
						gSessions.add((endInstant, RDF["type"], TIME["Instant"]))
						gSessions.add((interval, TIME["hasBeginning"], beginInstant))
						gSessions.add((interval, TIME["hasEnd"], endInstant))
						gSessions.add((beginInstant, TIME["inXSDDateTime"], rdflib.Literal(session[u'begindate'], datatype=rdflib.namespace.XSD.dateTime)))
						gSessions.add((endInstant, TIME["inXSDDateTime"], rdflib.Literal(session[u'enddate'], datatype=rdflib.namespace.XSD.dateTime)))
						gSessions.add((ind, LODE["atTime"], interval))
						
						if u'resourceList' in session.keys():
							for room in session[u'resourceList']:
								if room[u'type'] == u'room':
									indRoom = LED_ROOM[str(room[u'id'])]
									gRooms.add((indRoom, RDF["type"], ROOMS["Room"]))
									gRooms.add((indRoom, RDFS["label"], rdflib.Literal(room[u'label_en'])))
									gSessions.add((ind, LODE["atPlace"], indRoom))
						
						if u'teacherList' in session.keys():
							for teacher in session[u'teacherList']:
								person = LED_PEOPLE[str(teacher[u'id'])]
								gPeople.add((person, RDF["type"], FOAF["Person"]))
								gPeople.add((person, FOAF["firstName"], rdflib.Literal(teacher[u'firstname'])))
								gPeople.add((person, FOAF["lastName"], rdflib.Literal(teacher[u'lastname'])))
								gSessions.add((ind, LODE["involvedAgent"], person))


# ----- TRACKS -----

for year in range(2007, 2013):
	request = baseurl + "track/" + str(year) + "/list.json"
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
			for track in r:
				ind = LED_TRACK[str(track[u'id'])]
				gTracks.add((ind, RDF["type"], REVE["Track"]))
				gTracks.add((ind, AIISO["code"], rdflib.Literal(track[u'code'])))
				gTracks.add((ind, RDFS["label"], rdflib.Literal(track[u'title_en'], lang=u'en')))
				
				for resp in track[u'responsibleList']:
					person = resp[u'role'][u'people']
					p = LED_PEOPLE[str(person[u'id'])]
					gPeople.add((p, FOAF["firstName"], rdflib.Literal(person[u'firstname'])))
					gPeople.add((p, FOAF["lastName"], rdflib.Literal(person[u'lastname'])))
					gTracks.add((ind, REVE["hasCoordinator"], p))
					gPeople.add((p, REVE["isCoordinatorOf"], ind))
				
				for catalog in track[u'catalogList']:
					gSemesters.add((LED_SEMESTER[catalog[u'period'][u'name']], RDF["type"], REVE["Semester"]))
					for course in catalog[u'courseList']:
						ind_course = LED_COURSE[str(course[u'id'])]
						gCourses.add((ind_course, AIISO["code"], rdflib.Literal(course[u'code'])))
						if course[u'liberty'] == 'optionnal':
							gTracks.add((ind, REVE["hasOptionalCourse"], ind_course))
							gCourses.add((ind_course, REVE["isOptionalFor"], ind))
						if course[u'liberty'] == 'mandatory':
							gTracks.add((ind, REVE["hasMandatoryCourse"], ind_course))
							gCourses.add((ind_course, REVE["isMandatoryFor"], ind))
					
						ccft = rdflib.BNode()
						gCourses.add((ccft, RDF["type"], REVE["CourseCreditForTrack"]))
						gCourses.add((ind_course, REVE["hasCreditForTrack"], ccft))
						gCourses.add((ccft, REVE["hasTrack"], ind))
						gCourses.add((ccft, REVE["hasCredit"], rdflib.Literal(float(course[u'nbcredits']), datatype=rdflib.namespace.XSD.float)))


# ----- ROLES -----

for word in ["phd", "doctor", "teacher", "researcher"]:
	request = baseurl + word + "/list.json"
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
			for role in r:
				types[role[u'type']] = 1
				ind = LED_ROLE[str(role[u'id'])]
				person = LED_PEOPLE[role[u'people_id']]
				gRoles.add((ind, RDF["type"], PART["Role"]))
				gRoles.add((ind, PART["holder"], person))
				gPeople.add((person, RDF["type"], FOAF["Person"]))
				gPeople.add((person, PART["holder_of"], ind))
				gPeople.add((person, FOAF["firstName"], rdflib.Literal(role[u'people'][u'firstname'])))
				gPeople.add((person, FOAF["lastName"], rdflib.Literal(role[u'people'][u'lastname'])))
			
				comment = ""
				if u'education_en' in role[u'people'] and role[u'people'][u'education_en'] != None:
					comment += "Education: " + role[u'people'][u'education_en']
				if u'experience_en' in role[u'people'] and role[u'people'][u'experience_en'] != None:
					if comment != "":
						comment += "<br>"
					comment += "Experience: " + role[u'people'][u'experience_en']
				if comment != "":
					gPeople.add((person, RDFS["comment"], rdflib.Literal(comment)))
			
				if role[u'begindate'] != None:
					gRoles.add((ind, PART["startDate"], rdflib.Literal(role[u'begindate'], datatype=rdflib.namespace.XSD.date)))
				if role[u'enddate'] != None:
					gRoles.add((ind, PART["endDate"], rdflib.Literal(role[u'enddate'], datatype=rdflib.namespace.XSD.date)))
			
				if role[u'type'] == u'teacher':
					gRoles.add((ind, RDF["type"], REVE["Teacher"]))
				if role[u'type'] == u'researcher':
					gRoles.add((ind, RDF["type"], REVE["Researcher"]))
				if role[u'type'] == u'phd':
					gRoles.add((ind, RDF["type"], REVE["DoctoralStudent"]))
				if u'department' in role:
					dep = LED_DEP[str(role[u'department'][u'id'])]
					if role[u'department'][u'type'] == u'research':
						gDeps.add((dep, RDF["type"], REVE["ResearchUnit"]))
					else:
						gDeps.add((dep, RDF["type"], AIISO["Department"]))
					gDeps.add((dep, RDFS["label"], rdflib.Literal(role[u'department'][u'label_en'], lang=u'en')))
					gRoles.add((ind, PART["role_at"], dep))

# ----- OUTPUT FILES -----

print "Length of gPeople : " + str(len(gPeople))
print "Nb of persons : " + str(len(list(gPeople.triples((None, RDF["type"], FOAF["Person"])))))
outfile = open("people.rdf", "w")
outfile.write(gPeople.serialize())
outfile.close()

print "Length of gPubs : " + str(len(gPubs))
print "Nb of publications : " + str(len(list(gPubs.triples((None, RDF["type"], FOAF["Document"])))))
outfile = open("publications.rdf", "w")
outfile.write(gPubs.serialize())
outfile.close()

print "Length of gSemesters : " + str(len(gSemesters))
print "Nb of semesters : " + str(len(list(gSemesters.triples((None, RDF["type"], REVE["Semester"])))))
outfile = open("semesters.rdf", "w")
outfile.write(gSemesters.serialize())
outfile.close()

print "Length of gCourses : " + str(len(gCourses))
print "Nb of courses : " + str(len(list(gCourses.triples((None, RDF["type"], REVE["Course"])))))
outfile = open("courses.rdf", "w")
outfile.write(gCourses.serialize())
outfile.close()

print "Length of gRooms : " + str(len(gRooms))
print "Nb of rooms : " + str(len(list(gRooms.triples((None, RDF["type"], ROOMS["Room"])))))
outfile = open("rooms.rdf", "w")
outfile.write(gRooms.serialize())
outfile.close()

print "Length of gTracks : " + str(len(gTracks))
print "Nb of tracks : " + str(len(list(gTracks.triples((None, RDF["type"], REVE["Track"])))))
outfile = open("tracks.rdf", "w")
outfile.write(gTracks.serialize())
outfile.close()

print "Length of gRoles : " + str(len(gRoles))
print "Nb of roles : " + str(len(list(gRoles.triples((None, RDF["type"], PART["Role"])))))
print "Nb of phd roles : " + str(len(list(gRoles.triples((None, RDF["type"], REVE["DoctoralStudent"])))))
print "Nb of teacher roles : " + str(len(list(gRoles.triples((None, RDF["type"], REVE["Teacher"])))))
print "Nb of researcher roles : " + str(len(list(gRoles.triples((None, RDF["type"], REVE["Researcher"])))))
outfile = open("roles.rdf", "w")
outfile.write(gRoles.serialize())
outfile.close()

print "Length of gSessions : " + str(len(gSessions))
print "Nb of course sessions : " + str(len(list(gSessions.triples((None, RDF["type"], REVE["CourseSession"])))))
outfile = open("sessions.rdf", "w")
outfile.write(gSessions.serialize())
outfile.close()

print "Length of gDeps : " + str(len(gDeps))
print "Nb of departments : " + str(len(list(gDeps.triples((None, RDF["type"], AIISO["Department"])))))
print "Nb of research units : " + str(len(list(gDeps.triples((None, RDF["type"], REVE["ResearchUnit"])))))
outfile = open("departments.rdf", "w")
outfile.write(gDeps.serialize())
outfile.close()

#outfile = open("webint.json", "w")
#outfile.write(json.dumps(webintCourses, sort_keys=True, indent=4))
#outfile.close()

