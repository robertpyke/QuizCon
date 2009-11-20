import os
from google.appengine.ext.webapp import template

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
    questions = db.ListProperty(db.Key)

    date = db.DateTimeProperty(auto_now_add=True)

    def print_me (self):
        return_string = '<h4>' + self.title + '</h4>' + '<p>Category: ' + self.category + '</p>'
        return_string = return_string + '<ul class="questions">'        
        for q_key in self.questions:
            question = Question.get(q_key)
            return_string = return_string + '<li class="question">' + question.prompt + '</li>'

        return_string = return_string + '</ul>'
        return return_string

class Question(db.Model):
    prompt = db.StringProperty()
    answer = db.StringProperty()
    
# Get / (index) handler
class HomePage(webapp.RequestHandler):
    def get(self):

        user = users.get_current_user()
        template_values = {}
        template_values['base_uri'] = const['base_uri']
        if user:
            template_values['log_text'] = "Sign out"
            template_values['log_link'] = users.create_logout_url(const['base_uri'])
            template_values['nickname'] = user.nickname()
            template_values['body_text'] = ("Welcome " + user.nickname())
        else:
            template_values['log_text'] = "Sign in"
            template_values['log_link'] = users.create_login_url(self.request.uri)

        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'index.html')
        self.response.out.write(template.render(path, template_values))

# Get /my/profile (handler)
class MyProfile(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        template_values = {}
        template_values['base_uri'] = const['base_uri']
        template_values['log_text'] = "Sign out"
        template_values['log_link'] = users.create_logout_url(const['base_uri'])
        template_values['nickname'] = user.nickname()
        
        users_quizzes = BasicQuiz.gql("WHERE author = :1 ORDER BY date", user)
        users_quizzes_count = users_quizzes.count()
        template_values['quiz_list_size'] = str(users_quizzes_count)
        
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'my_profile.html')
        self.response.out.write(template.render(path, template_values))
        
class ProfileQuiz(webapp.RequestHandler):
    def get(self):
        quiz_name = None
        while self.request.path_info_peek() != None:
            quiz_name = self.request.path_info_pop()

        self.response.out.write('<html><body><p>Quiz: ' + quiz_name + '</p></body></html>')    

class ModifyQuiz(webapp.RequestHandler):
    @login_required
    def get(self):
        quiz_key = None
        while self.request.path_info_peek() != None:
            quiz_key = self.request.path_info_pop()

        user = users.get_current_user()

        quiz = None
        # Try to load the specified quiz
        try:
            quiz = BasicQuiz.get(quiz_key)
        except:
        # Failed to load the quiz
            self.response.out.write('<html><body><p>Bad Quiz Key.. No such quiz!</p></body></html>')
            return
        
        # If the user is not the author
        if user != quiz.author:
            self.response.out.write("<html><body><p>You don't have permission to edit that quiz</p></body></html>")
        else:
            # We found the quiz, and the current user is the author.
            self.response.out.write('<html><head<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /></head><body>')
            self.response.out.write(quiz.print_me())
            
            # Print form to add a question
            self.response.out.write('<form action="/post/quiz/add_question" method="post">')            
            self.response.out.write('<input type="hidden" name="quiz_key" value="' + quiz_key + '"/>')
            self.response.out.write("""
                    <table class="form">
                        <tr>
                            <td>
                                <p class="prompt">Question prompt: </p>
                            </td>
                            <td>
                                <input type="text" name="prompt" />
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <p class="prompt">Answer: </p>
                            </td>
                            <td>
                                <input type="text" name="answer" />
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <input type="submit" value="Add Question" />
                            </td>
                        </tr>
                    </table>
                </form>
            """)
            self.response.out.write('</body></html>')


class ProfileUser(webapp.RequestHandler):
    def get(self):
        target_user_name = None
        while self.request.path_info_peek() != None:
            target_user_name = self.request.path_info_pop()

        user = users.get_current_user()
        if user == None or user.nickname() != target_user_name:
            self.response.out.write('<html><body><p>User: ' + target_user_name + '</p></body></html>')
        else:
            users_quizzes = BasicQuiz.gql("WHERE author = :1 ORDER BY date", user)
            self.response.out.write("""
                <html>
                    <head<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /></head>
                    <body>
            """)
            self.response.out.write('<h3>User: ' + user.nickname() + '</h3>')

            self.response.out.write('<h4>My Quizzes</h4>')
            self.response.out.write('<div class="my_quizzes">')
            
            for quiz in users_quizzes:
                self.response.out.write('<div class="quiz">')
                self.response.out.write('<h4><strong>' + quiz.title + '</strong></h4>')
                self.response.out.write('<ul>')
                self.response.out.write('<li>Category: ' + quiz.category + '</li>')
                self.response.out.write('</ul>')
                self.response.out.write('<p><a href="/quiz/modify/' + str(quiz.key()) + '">Modify?</a></p>')
                self.response.out.write('</div>')
            
            self.response.out.write('</div>')
            
            self.response.out.write('</body></html>')
            



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
        
        self.redirect('/quiz/modify/' + str(b_quiz.key()))

class AddQuestionPost(webapp.RequestHandler):
    def post(self):
        question = Question()

        quiz_key = self.request.get('quiz_key')

        question.prompt = self.request.get('prompt')
        question.answer = self.request.get('answer')

        question.put()
        
        quiz = None
        # Try to load the specified quiz
        try:
            quiz = BasicQuiz.get(quiz_key)
        except:
            # TODO
            return

        # Add the question to the quiz
        quiz.questions.append(question.key())  
        quiz.put()

        self.redirect('/quiz/modify/' + str(quiz_key))

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
                <form action="/post/quiz/create_quiz" method="post">
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
                                    <option value="youtube">YouTube</option>
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
                                        ('/my/profile', MyProfile),
                                        ('/quiz/create_quiz', CreateQuiz),
                                        ('/quiz/profile/[^\/]+', ProfileQuiz),
                                        ('/user/profile/[^\/]+', ProfileUser),
                                        ('/post/quiz/create_quiz', CreateQuizPost),
                                        ('/txt/quiz/quiz_list', TextQuizList),
                                        ('/quiz/modify/[^\/]+', ModifyQuiz),
                                        ('/post/quiz/add_question', AddQuestionPost)
                                    ],
                                    debug=True
                                )

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


