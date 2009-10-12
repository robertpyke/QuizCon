from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Quiz(db.Model):
    author = db.UserProperty()
    quiz_name = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)

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
                                        [('/', MainPage), ('/create_quiz', CreateQuiz)],
                                        debug=True
                                    )

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


