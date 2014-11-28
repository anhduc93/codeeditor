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

# Main Page Handler
class MainPageHandler(webapp2.RequestHandler):
	def get(self):
		is_current_user = False
		user_nickname = ""
		# Check if this is the current user
		if users.get_current_user():
			is_current_user = True
			user = users.get_current_user()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			user_nickname = user.nickname()
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		template_values={
			'is_current_user': is_current_user,
			'url' :url,
			'url_linktext': url_linktext,
			'user_nickname':user_nickname,
		}
		template = JINJA_ENVIRONMENT.get_template('templates/MainPage.html')
		self.response.write(template.render(template_values))

# Model
DEFAULT_FILE_NAME = 'default_filename'
#def codefile_key(file_name=DEFAULT_FILE_NAME):
#	"""Constructs a Datastore key for a File entity with file_name."""
#	return ndb.Key('CodeFile', file_name)

class CodeFile(ndb.Model):
	author = ndb.UserProperty()
	title = ndb.StringProperty()
	content = ndb.TextProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)
	
# Handle save file event
class CodeFileSaveHandler(webapp2.RequestHandler):
	def post(self):
		file_name = self.request.get('file_name', DEFAULT_FILE_NAME)	# get the "file_name" text field
		code_file = CodeFile()
		
		# Check and pass appropriate user data
		is_current_user = False
		user_nickname=""
		if users.get_current_user():
			# Save this file if this is the current user
			is_current_user = True
			code_file.author = users.get_current_user()
			code_file.content = self.request.get('file_content')
			code_file.title = file_name
			code_file.put()
			success_text = "Save successfully!"

			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			user = users.get_current_user()
			user_nickname = user.nickname()
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Log in using your Google Account'
			success_text = ""
		template_values={
			'url_linktext' : url_linktext,
			'url' : url,
			'user_nickname' : user_nickname,
			'is_current_user': is_current_user,
			'success_text':success_text,
		}
		template = JINJA_ENVIRONMENT.get_template('templates/Save.html')
		self.response.write(template.render(template_values))
			
# Lists all files belong to the current user
class CodeFileListHandler(webapp2.RequestHandler):
	def get(self):
		file_name = self.request.get('file_name', DEFAULT_FILE_NAME)
		
		is_current_user = False
		user_nickname = ""
		if users.get_current_user():
			is_current_user = True
			user = users.get_current_user()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			user_nickname = user.nickname()
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		
		query = CodeFile.query(CodeFile.author==users.get_current_user()).order(-CodeFile.date)
		codefiles = query.fetch(10)
		code_files = {}
		for codefile in codefiles:
			key = codefile.key
			view_url = key.urlsafe()
			code_files[view_url] = codefile;
			
		template_values={
			'url_linktext' : url_linktext,
			'url':url,
			'user_nickname' : user_nickname,
			'is_current_user': is_current_user,
			'codefiles': code_files,
		}
		template = JINJA_ENVIRONMENT.get_template('templates/List.html')
		self.response.write(template.render(template_values))

# View a specific file belongs to the current user
class CodeFileViewHandler(webapp2.RequestHandler):
	def get(self, key):
		is_current_user = False
		#self.response.write("dasdas")
		user_nickname = ""
		template = JINJA_ENVIRONMENT.get_template('templates/View.html')
		if users.get_current_user():
			is_authorized = False
			is_current_user = True
			user = users.get_current_user()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			user_nickname = user.nickname()
			
			file_key = ndb.Key(urlsafe=key)
			codefile = file_key.get()
			template_values = {}

			if (codefile.author == users.get_current_user()):
				is_authorized = True
				template_values={
					'url_linktext' : url_linktext,
					'url':url,
					'user_nickname' : user_nickname,
					'is_current_user': is_current_user,
					'codefile': codefile,
					'key':key,
					'is_authorized': is_authorized,
				}
			else:
				templates_values={
					'is_current_user': is_current_user,
					'is_authorized': is_authorized,
				}
			self.response.write(template.render(template_values))
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Log in using your Google Account'
			template_values={
				'url_linktext' : url_linktext,
				'url':url,
				'is_current_user': is_current_user,
			}
			self.response.write(template.render(template_values))

class CodeFileEditHandler(webapp2.RequestHandler):
	def post(self, key):		
		# Check and pass appropriate user data
		is_current_user = False
		user_nickname=""
		if users.get_current_user():
			file_key = ndb.Key(urlsafe=key)
			code_file = file_key.get()
			# Save this file if this is the current user
			is_current_user = True
			code_file.content = self.request.get('file_content')
			code_file.put()
			success_text = "Save successfully!"

			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			user = users.get_current_user()
			user_nickname = user.nickname()
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Log in using your Google Account'
			success_text = ""
		template_values={
			'url_linktext' : url_linktext,
			'url' : url,
			'user_nickname' : user_nickname,
			'is_current_user': is_current_user,
			'success_text':success_text,
		}
		template = JINJA_ENVIRONMENT.get_template('templates/Edit.html')
		self.response.write(template.render(template_values))

# Routing
application = webapp2.WSGIApplication([
	('/', MainPageHandler),
	('/list', CodeFileListHandler),
	('/save', CodeFileSaveHandler),
	(r'/save/(.*)', CodeFileEditHandler),
	(r'/view/(.*)', CodeFileViewHandler),
], debug=True)