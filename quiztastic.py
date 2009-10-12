from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import yaml

# Author: Robert Pyke

f = open('constants.yaml')
const = yaml.load(f)
f.close()

class BasicQuiz(db.Model):
    author = db.UserProperty()

    quiz_title = db.StringProperty()
    quiz_category = db.StringProperty()

    date = db.DateTimeProperty(auto_now_add=True)
    
class HomePage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.out.write('<html><head><title>' + const['home_title'] + '</title></head>')
        self.response.out.write('<body>')

        if user:
            self.response.out.write('<h3>Welcome ' + user.nickname() + '</h3>')
            self.response.out.write('<p><a href="' + users.create_logout_url(self.request.uri) + '">Logout</a></p>')   
        else:
            self.response.out.write('<h3>Welcome</h3>')
            self.response.out.write('<p><a href="' + users.create_login_url(self.request.uri) + '">Login</a></p>')

        self.response.out.write('</body></html>')

class ProfileQuiz(webapp.RequestHandler):
    def get(self):
        quiz_name = None
        while self.request.path_info_peek() != None:
            quiz_name = self.request.path_info_pop()

        self.response.out.write('<html><body><p>Quiz Name: ' + quiz_name + '</p></body></html>')    

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        if user:
            quizzes = db.GqlQuery("SELECT * FROM Quiz ORDER BY date DESC LIMIT 20")
        
            self.response.out.write('<ul class="quizzes">')

            for quiz in quizzes:
                self.response.out.write('<li class="quiz">')
                self.response.out.write('Author: ' + quiz.author.nickname() + ', Quiz Name: ' + quiz.quiz_name ) 
                self.response.out.write('</li>')


            self.response.out.write('</ul>')
            self.response.out.write('<html><body>')
            self.response.out.write('<p>Hello, ' + user.nickname() + '</p>')
            # Write the quiz creation form
            self.response.out.write("""
                    <form action="/create_quiz" method="post">
                        <p class="prompt">Quiz Name:</p>
                        <input type="text" name="quiz_name" />
                            <input type="submit" value="Create Quiz" />
                        </form>
                    </body>
                </html>
            """)
        else:
            self.redirect(users.create_login_url(self.request.uri))
    
class CreateQuiz(webapp.RequestHandler):
    def post(self):
        quiz = Quiz()

        if users.get_current_user():
            quiz.author = users.get_current_user()
        else:
            self.redirect('/')
        
        quiz.quiz_name = self.request.get('quiz_name')
        quiz.put()
        self.redirect('/')

application = webapp.WSGIApplication( 
                                    [
                                        ('/', HomePage), 
                                        ('/create_quiz', CreateQuiz), 
                                        ('/profile/quiz/[^\/]+', ProfileQuiz)
                                    ],
                                    debug=True
                                )

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


