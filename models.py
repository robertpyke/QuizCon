from google.appengine.ext import db


# Quiz Model
class Quiz(db.Model):
    title = db.StringProperty()
    description = db.StringProperty()
    category = db.StringProperty()
    questions = db.ListProperty(db.Key)
    author = db.UserProperty()
    creation_date = db.DateTimeProperty(auto_now_add=True)
    scores = db.ListProperty(db.Key)
    ratings = db.ListProperty(db.Key)
    private = db.BooleanProperty()
    private_viewers = db.StringListProperty()

    def print_me (self):
        return_string = '<h4>' + self.title + '</h4>' + '<p>Description: ' + self.description + '</p>' + '<p>Category: ' + self.category + '</p>'
        return_string += '<p class="question_count">Questions: ' + str(len(self.questions)) + '</p>'
        return_string += '<ul class="questions">'        
        for q_key in self.questions:
            question = Question.get(q_key)
            return_string += '<li class="question">' + question.prompt + '</li>'

        return_string = return_string + '</ul>'
        return return_string
    
    def print_take_quiz (self):
        return_string = '<form action="/post/quiz/take" method="post">'
        return_string += '<div class="form">'
        return_string += '<input type="hidden" name="quiz_key" value="' + str(self.key()) + '"/>'
        return_string += '<fieldset class="takeQuiz">'
        return_string += '<legend>' +  self.title + '</legend>'
        return_string += '<p class="description">Description: ' + self.description + '</p>' + '<p class="category">Category: ' + self.category + '</p>'
        
        for q_key in self.questions:
            question = Question.get(q_key)
            return_string += '<div class="question">'
            return_string += '<p class="prompt">' 
            return_string += '<label for="' + str(q_key) + '">' + question.prompt + ':</label>'
            return_string += '<input type="text" name="' + str(q_key) + '"/>'
            return_string += '</p>'            
            return_string += '</div>'

        return_string += '<p class="submit"><input type="submit" value="Submit Answers"/></p>'
        return_string += '</fieldset></div></form>'
        
        return return_string

class Question(db.Model):
    prompt = db.StringProperty()
    solution = db.StringProperty()
    solution_case_sensitive = db.BooleanProperty()
    solution_description = db.StringProperty()
    solution_description_image_url = db.LinkProperty()
    quiz = db.ReferenceProperty(Quiz)

class Score(db.Model):
    user = db.UserProperty()
    correct = db.IntegerProperty()
    incorrect = db.IntegerProperty()
    quiz = db.ReferenceProperty(Quiz)

class Rating(db.Model):
    user = db.UserProperty()
    rating = db.IntegerProperty()
    quiz = db.ReferenceProperty(Quiz)


class Profile(db.Model):
    user = db.UserProperty()
    nick_name = db.StringProperty()
    language = db.StringProperty()
    scores = db.ListProperty(db.Key)
    ratings = db.ListProperty(db.Key)
    created_quizzes = db.ListProperty(db.Key)
    taken_quizzes = db.ListProperty(db.Key)
 
