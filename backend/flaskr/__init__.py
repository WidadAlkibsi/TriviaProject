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
  
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
 
  @app.after_request
  def after_request(response): 
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'POST,PATCH,GET,DELETE,OPTIONS')
    return response

 
  @app.route('/categories', methods=['GET'])
  def retrieve_categories():
    categories = Category.query.all()
    categs = {cat.id:cat.type for cat in categories}
    # formatted_categories = [category.format() for category in categories]

    if len(categs) == 0:
      abort(404)  #Not found
    
    return jsonify({
      'success' : True, 
      'categories': categs,
      # 'total categories': len(formatted_categories)
    })


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


 

  @app.route('/questions/<int:question_id>' , methods=['DELETE'])
  def delete_question(question_id):
    try: 
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404) #404 Not Found

      question.delete()
      qst = Question.query.order_by(Question.id).all()
      # quests = {question.id:question.type for question in qst}

      current_questions = [question.format() for question in qst]

      return jsonify({
        'success' : True, 
        'deleted' : question_id, 
        'questions': current_questions,
        'total questions': len(current_questions)
      })
    except: 
      abort(422) 

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
        'total questions': len(questions),
        'current_category': category_id
        # 'categories': formatted_categories
    })

  
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

  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({'success': False,
                        'error': 400,
                        'message': 'Bad request'}), 400
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

  