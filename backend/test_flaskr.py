import json
import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db
from settings import DB_PASSWORD, DB_USER


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    new_question = {
        'question': 'What is the capital of France?',
        'answer': 'Paris',
        'category': 1,
        'difficulty': 1
    }
    quiz = {'previous_questions': [], 'quiz_category': {'id': "1"}}

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            DB_USER, DB_PASSWORD, 'localhost:5432', self.database_name)
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

    """
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Category tests
    def test_get_categories(self):
        '''
        Test get categories
        '''
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    def test_get_categories_failure(self):
        '''
        Test get categories failure
        '''
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    # Questions tests (Get, Post, Delete)
    # ----------------------------------------------------------------

    # GET /questions
    def test_get_questions_success(self):
        '''
        Test get questions success
        '''
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_get_paginated_questions_success(self):
        '''
        Test get questions with pagination success

        '''

        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_get_paginated_questions_failure(self):
        '''
        Test get questions with pagination failure
        '''
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000', json={'rating': 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_delete_question_success(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)

    def test_delete_question_failure(self):
        '''
        Test delete question failure
        '''
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_create_new_question_success(self):
        '''
        Test create new question
        '''
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_create_new_question_failure(self):
        '''
        Test create new question failure
        '''
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_405_if_question_creation_not_allowed(self):
        '''
        Test if the question creation is not allowed
        '''
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    def test_search_question(self):
        '''
        Test search question
        '''
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'title'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_if_question_search_not_found(self):
        '''Test for 404 if question search not found'''
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'notfound'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    # Quiz tests

    def test_quiz(self):
        '''
        Quiz test with random questions
        '''
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_if_quiz_not_found(self):
        '''
        Test for 404 if quiz not found
        '''
        res = self.client().post(
            '/quizzes', json={"quiz_category": {'id': '1000'}, "previous_questions": []})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
