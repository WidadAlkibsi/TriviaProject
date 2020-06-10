import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import unittest
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response): 
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'POST,PATCH,GET,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def retrieve_categories():
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]

    if len(formatted_categories) == 0:
      abort(404)  #Not found
    
    return jsonify({
      'success' : True, 
      'categories': formatted_categories,
      # 'total categories': len(formatted_categories)
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions' , methods=['GET'])
  def retrieve_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = Question.query.all()
    # categories = Question.category.query.all()
    current_questions = [question.format() for question in questions]
    # formatted_categories = [ formatted_questions.category for category in categories]
    categories = Category.query.all()
    # formatted_categories = [category.format() for category in categories]
    categs = {cat.id:cat.type for cat in categories}

    if len(current_questions) == 0:
      abort(404)  #Not found
    
    return jsonify({
      'success' : True, 
      'questions': current_questions[start:end],
      'total_questions': len(current_questions),
      'categories': categs,
      'current_categories': None
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>' , methods=['DELETE'])
  def delete_question(question_id):
    try: 
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404) #404 Not Found

      question.delete()
      qst = Question.query.order_by(Question.id).all()
      current_questions = [question.format() for question in qst]

      return jsonify({
        'success' : True, 
        'deleted' : question_id, 
        'questions': current_questions,
        'total questions': len(current_questions)
      })
    except: 
      abort(422) 

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    search = body.get('searchTerm', None)

    try: 
      if search: 
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        current_quest = [question.format() for question in selection]

        return jsonify({
          'success' : True, 
          'questions' : current_quest,
          'total_questions' : len(current_quest)
        })

      else: 
        question = Question(question=new_question, answer=new_answer
        , category=new_category, difficulty=new_difficulty)
        question.insert()

        questions = Question.query.order_by(Question.id).all()
        formatted_questions = [title.question for title in questions]

        return jsonify({
          'success' : True, 
          'created': question.id,
          'questions' : formatted_questions, 
          'total_questions' : len(formatted_questions)
        })
    
    except:
         abort(422) # Unprocessable Entity


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  # @app.route('/questions/search', methods=['POST'])
  # def search_questions():
  #   body = request.get_json()
  #   search = body.get('search', None)

  #   page = request.args.get('page', 1, type=int)
  #   start = (page - 1) * 10 
  #   end = start + 10

  #   selection = searched_question=Question.query.filter(Question.question.ilike('%{}%'.format(search)).all())
  #   current_quests = [question.format() for question in selection]
  #   try: 

  #    if search is None:
  #     abort(404)
  
    
  #    return jsonify ({
  #       'questions' : current_quests[start:end] ,
  #       'total_questions' : len(current_quests) ,
  #       'success' : True 
      
  #      })
  #   except: 
  #     abort(422)
  # return app

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions' , methods=['GET'])
  def get_questions_basedon_category(category_id):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 1

    categ = Category.query.filter_by(id == category_id).one_or_none()
    questions = Question.query.filter(Question.category == category_id).all()
    formatted_questions = [question.format() for question in questions]
    formatted_category = categ.format()

    if not questions:
        abort(404) 
    if not categ:
        abort(404)  
    
    return jsonify({
        'success' : True, 
        'questions': formatted_questions[start:end],
        'total questions in category': len(formatted_questions),
        'Category': formatted_category
        # 'categories': formatted_categories
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
    '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    previous_question = body.get('previousQuestions', None)
    quiz_category = body.get('quizCategory', None)

    if previous_question is None or quiz_category is None:
      abort(400)
    try:
        category_id = quiz_category['id']
        if category_id == 0:
             questions = [question.format() for question in
                         Question.query.all() if
                         question.id not in previous_question]
        else:
             questions = [question.format() for question in
                         Question.query.filter_by(category=category_id).all()
                         if question.id not in previous_question]
  
        if len(questions) == 0:
             return jsonify({'success': True})

        question = random.choice(questions)

    except Exception:
            abort(422)

    return jsonify({'success': True,
                    'question': question,
                    # 'previous_questions': previous_question,
                    # 'quizCategory':quiz_category
      
                    })


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  # @app.errorhandler(400)
  # def bad_request(error):
  #       return jsonify({'success': False,
  #                       'error': 400,
  #                       'message': 'Bad request'}), 400
  @app.errorhandler(404)
  def not_Found(error):
        return jsonify({'success': False,
                        'error': 404,
                        'message': 'Not Found'}), 404
  @app.errorhandler(422)
  def Unprocessable_entitiy(error):
        return jsonify({'success': False,
                        'error': 422,
                        'message': 'Unprocessable Entitiy'}), 422


  return app

  