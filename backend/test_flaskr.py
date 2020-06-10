import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    
    def test_qet_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_qet_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_categories'])
    
    def test_get_questions_search_with_results(self):
        res = self.client().post('/questions', json={'search':'Who'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_get_questions_search_without_results(self):
        res = self.client().post('/questions', json={'search':'hero'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'], 0)
        self.assertTrue(data['total_questions'], 0)
    

    def test_delete_question(self):
        res = self.client().delete(f'/questions/{1}')
        data = json.loads(res.data)

        question = Question.query.filter_by(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual('deleted', 1)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total questions'])
     
    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/question/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    
    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_category_questions(self):
        res = self.client().get(f'/categories/{1}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 1)
        self.assertTrue(data['questions'])
        

    def test_post_quizzes(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [21, 22],
            'quiz_category': {'type': "Art", 'id': 2}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question']['category'], 1)
        self.assertTrue(data['question'])
        self.assertTrue(data['success'])

    def test_400_bad_add_question(self):
        res = self.client().post('/questions',
                                 json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])
        

    def test_422_category_bad_number(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()