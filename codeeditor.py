import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class MainPage(webapp2.RequestHandler):
	def get(self):
		current_user = False
		if users.get_current_user():
			current_user = True
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		template_values={
			'current_user':current_user,
			'url' :url,
			'url_linktext': url_linktext,
		}
		template = JINJA_ENVIRONMENT.get_template('templates/index.html')
		self.response.write(template.render(template_values))

DEFAULT_FILE_NAME = 'default_filename'
def codefile_key(file_name=DEFAULT_FILE_NAME):
	"""Constructs a Datastore key for a File entity with file_name."""
	return ndb.Key('CodeFile', file_name)

class CodeFile(ndb.Model):
	author = ndb.UserProperty()
	title = ndb.StringProperty()
	content = ndb.TextProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)
	
# Handling file-save event
class CodeFileSave(webapp2.RequestHandler):
	def post(self):
		file_name = self.request.get('file_name', DEFAULT_FILE_NAME)	# get the file name textfield
		code_file = CodeFile(parent = codefile_key(file_name))
		
		if users.get_current_user():
			code_file.author = users.get_current_user()
			code_file.content = self.request.get('file_content')
			code_file.title = file_name
			code_file.put()
			self.response.write("You have successfully saved this file to your account!")

# Lists all file
class CodeFileListHandler(webapp2.RequestHandler):
	def get(self):
		file_name = self.request.get('file_name', DEFAULT_FILE_NAME)
		self.response.write("This is the list of all files!")
		query = CodeFile.query(
			ancestor=codefile_key(file_name)).order(-CodeFile.date)
		codefiles = query.fetch(10)
		
		template_values={
			'codefiles': codefiles,
		}
		template = JINJA_ENVIRONMENT.get_template('templates/list.html')
		self.response.write(template.render(template_values))			


# Routing
application = webapp2.WSGIApplication([
	('/', MainPage),
	('/list', CodeFileListHandler),
	('/save', CodeFileSave),
], debug=True)

"""
	Pass JavaScript variable to Python
	Save into the database
	Load the file and display to the mainpage
	Design the interface
"""