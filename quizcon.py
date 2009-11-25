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
            template_values['body'] = ('<p>Welcome ' + user.nickname() + '</p>')
        else:
            template_values['log_text'] = "Sign in"
            template_values['log_link'] = users.create_login_url(self.request.uri)

        path = os.path.join(os.path.dirname(__file__), 'templates')
        links_path = os.path.join(path, 'links.html')
       
        links_template_values = {}
        links_template_values['my_profile'] = "notCurrent"
        links_template_values['my_quiz_list'] = "notCurrent"
        links_template_values['quiz_quiz_list'] = "notCurrent"

        template_values['links'] = template.render(links_path, links_template_values)

        main_path = os.path.join(path, 'index.html')
        self.response.out.write(template.render(main_path, template_values))

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
        
        
        path = os.path.join(os.path.dirname(__file__), 'templates')
        links_path = os.path.join(path, 'links.html')
        
        links_template_values = {}
        links_template_values['my_profile'] = "current"
        links_template_values['my_quiz_list'] = "notCurrent"
        links_template_values['quiz_quiz_list'] = "notCurrent"

        template_values['links'] = template.render(links_path, links_template_values)

        body_path = os.path.join(path, 'my_profile.html')
        
        body_template_values = {}        
        users_quizzes = BasicQuiz.gql("WHERE author = :1 ORDER BY date", user)
        users_quizzes_count = users_quizzes.count()
        body_template_values['quiz_list_size'] = str(users_quizzes_count)

        template_values['body'] = template.render(body_path, body_template_values)

        main_path = os.path.join(path, 'index.html')
        self.response.out.write(template.render(main_path, template_values))
        
# Get /my/quiz_list (handler)
class MyQuizList(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        template_values = {}
        template_values['base_uri'] = const['base_uri']
        template_values['log_text'] = "Sign out"
        template_values['log_link'] = users.create_logout_url(const['base_uri'])
        template_values['nickname'] = user.nickname()
        
        
        path = os.path.join(os.path.dirname(__file__), 'templates')
        links_path = os.path.join(path, 'links.html')
        
        links_template_values = {}
        links_template_values['my_profile'] = "notCurrent"
        links_template_values['my_quiz_list'] = "current"
        links_template_values['quiz_quiz_list'] = "notCurrent"

        template_values['links'] = template.render(links_path, links_template_values)

        body_path = os.path.join(path, 'my_quiz_list.html')
        
        body_template_values = {}
        users_quizzes = BasicQuiz.gql("WHERE author = :1 ORDER BY date", user)
        users_quizzes_count = users_quizzes.count()
        body_template_values['quiz_list_size'] = str(users_quizzes_count)
        
        quiz_list = ""
        up_to = 0
        out_of = users_quizzes_count
        for quiz in users_quizzes:
            up_to += 1
            quiz_list += '<div class="quizContainer">'
            quiz_list += '<p class="floatOptions"><a href="/quiz/modify/' + str(quiz.key()) + '">modify</a></p>'
            quiz_list += '<p class="titile"><strong>' + quiz.title + '</strong></p>'
            quiz_list += '<p class="quiz">'
            quiz_list += '<ul>'
            quiz_list += '<li>Category: ' + quiz.category + '</li>'
            quiz_list += '</ul>'
            quiz_list += '</p>'
            quiz_list += '<p class="options"><em>' + str(up_to)  + '/' + str(out_of) + '</em></p>'
            quiz_list += '</div>'
        
        body_template_values['quiz_list'] = quiz_list
        template_values['body'] = template.render(body_path, body_template_values)

        main_path = os.path.join(path, 'index.html')
        self.response.out.write(template.render(main_path, template_values))
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
        
        template_values = {}
        template_values['base_uri'] = const['base_uri']
        template_values['log_text'] = "Sign out"
        template_values['log_link'] = users.create_logout_url(const['base_uri'])
        template_values['nickname'] = user.nickname()
        
        
        path = os.path.join(os.path.dirname(__file__), 'templates')
        links_path = os.path.join(path, 'links.html')
        
        links_template_values = {}
        links_template_values['my_profile'] = "notCurrent"
        links_template_values['my_quiz_list'] = "notCurrent"
        links_template_values['quiz_quiz_list'] = "notCurrent"

        template_values['links'] = template.render(links_path, links_template_values)


        quiz = None
        # Try to load the specified quiz
        try:
            quiz = BasicQuiz.get(quiz_key)
        except:
        # Failed to load the quiz
            template_values['body'] = '<p class="error">Bad Quiz Key. Failed to load quiz</p>'

            main_path = os.path.join(path, 'index.html')
            self.response.out.write(template.render(main_path, template_values))
            return
        
        if quiz == None: 
            template_values['body'] = '<p class="error">Bad Quiz Key. Failed to load quiz</p>'

            main_path = os.path.join(path, 'index.html')
            self.response.out.write(template.render(main_path, template_values))
            return

        # If the user is not the author
        if user != quiz.author:
            template_values['body'] = '''<p class="error">You don't have permission to edit that quiz</p>'''

            main_path = os.path.join(path, 'index.html')
            self.response.out.write(template.render(main_path, template_values))
        else:
            body_path = os.path.join(path, 'modify_quiz.html')
            body_template_values = {}
            body_template_values['quiz_key'] = quiz_key
            body_template_values['quiz'] = quiz.print_me() 

            template_values['body'] = template.render(body_path, body_template_values)

            main_path = os.path.join(path, 'index.html')
            self.response.out.write(template.render(main_path, template_values))

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
            # TODO: Redirect with error
            path = os.path.join(os.path.dirname(__file__), 'templates')
            links_path = os.path.join(path, 'links.html')
       
            links_template_values = {}
            links_template_values['my_profile'] = "notCurrent"
            links_template_values['my_quiz_list'] = "notCurrent"
            links_template_values['quiz_quiz_list'] = "notCurrent"

            template_values = {}
            template_values['links'] = template.render(links_path, links_template_values)
            template_values['body'] = '<p class="error">Failed modify quiz</p>'

            main_path = os.path.join(path, 'index.html')
            self.response.out.write(template.render(main_path, template_values))            
            return

        # Add the question to the quiz
        quiz.questions.append(question.key())  
        quiz.put()

        self.redirect('/quiz/modify/' + str(quiz_key))


application = webapp.WSGIApplication( 
                                    [
                                        ('/', HomePage), 
                                        ('/my/profile', MyProfile),
                                        ('/my/quiz_list', MyQuizList),
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


