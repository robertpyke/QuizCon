from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp.util import login_required

import yaml

# Author: Robert Pyke

f = open('constants.yaml')
const = yaml.load(f)
f.close()

class BasicQuiz(db.Model):
    author = db.UserProperty()

    title = db.StringProperty()
    category = db.StringProperty()

    date = db.DateTimeProperty(auto_now_add=True)
    
class HomePage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><head><title>' + const['home_title'] + '</title></head>')
        self.response.out.write('<body>')

        user = users.get_current_user()
        if user:
            self.response.out.write('<h3>Welcome ' + user.nickname() + '</h3>')
            self.response.out.write('<p><a href="' + users.create_logout_url(self.request.uri) + '">Logout</a></p>')   
        else:
            self.response.out.write('<h3>Welcome</h3>')
            self.response.out.write('<p><a href="' + users.create_login_url(self.request.uri) + '">Login</a></p>')

        self.response.out.write('<ul class="links">')
        self.response.out.write("""
            <li><a href="/create_quiz">Create Quiz</a></li>
            <li><a href="/txt/quiz_list">List of stored quizzes (txt)</a></li>
            </ul>
        """)
        self.response.out.write('</p>')
        self.response.out.write('</body></html>')

class ProfileQuiz(webapp.RequestHandler):
    def get(self):
        quiz_name = None
        while self.request.path_info_peek() != None:
            quiz_name = self.request.path_info_pop()

        self.response.out.write('<html><body><p>Quiz: ' + quiz_name + '</p></body></html>')    

class ProfileUser(webapp.RequestHandler):
    def get(self):
        user_name = None
        while self.request.path_info_peek() != None:
            user_name = self.request.path_info_pop()

        self.response.out.write('<html><body><p>User: ' + user_name + '</p></body></html>')


class TextQuizList(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        # TODO Fix magic number
        basic_quizzes = db.GqlQuery("SELECT * FROM BasicQuiz ORDER BY date") # DESC LIMIT 999")

        for b_quiz in basic_quizzes:
            self.response.out.write(b_quiz.title + ':\n') 
            self.response.out.write(
                '\tcreation_date: ' + str(b_quiz.date) + '\n'
            ) 
#            self.response.out.write('\tauthor: ' + b_quiz.author.nickname() + '\n'
            self.response.out.write('\tcategory: ' + b_quiz.category + '\n')

class CreateQuizPost(webapp.RequestHandler):
    def post(self):
        b_quiz = BasicQuiz()

        b_quiz.author = users.get_current_user()
        
        b_quiz.title = self.request.get('title')
        b_quiz.category = self.request.get('category')
        
        b_quiz.put()
        
        self.redirect('/')

class CreateQuiz(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
       

        self.response.out.write("""
            <html><head>
            <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
            </head><body>
        """)
        self.response.out.write('<p>Hello, ' + user.nickname() + '</p>')
        # Write the quiz creation form
        # TODO Make the select use the const vales...
        self.response.out.write("""
                <form action="/post/create_quiz" method="post">
                    <table class="form">
                        <tr>
                            <td>
                                <p class="prompt">Title:</p>
                            </td>
                            <td>
                                <input type="text" name="title" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <p class="prompt">Category:</p>
                            </td>
                            <td>
                                <select name="category">
                                    <option value="history">History</option>
                                    <option value="maths">Mathematics</option>
                                    <option value="media">Media (Music, TV, etc.)</option>
                                    <option value="sci_tech">Science/Tech</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <input type="submit" value="Create Quiz" />
                            </td>
                        </tr>
                    </table>
                </form>
            </body>
        </html>
        """)

application = webapp.WSGIApplication( 
                                    [
                                        ('/', HomePage), 
                                        ('/create_quiz', CreateQuiz),
                                        ('/profile/quiz/[^\/]+', ProfileQuiz),
                                        ('/profile/user/[^\/]+', ProfileUser),
                                        ('/post/create_quiz', CreateQuizPost),
                                        ('/txt/quiz_list', TextQuizList),
                                    ],
                                    debug=True
                                )

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


