import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')
		self.response.write('This is a test')

application = webapp2.WSGIApplication([
    ('/', MainPage),
	('/', SecondPage),
], debug=True)
