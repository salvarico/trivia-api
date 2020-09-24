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
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question' : 'Who is the father of Singapore?',
            'answer' : 'Lee Kuan Yew',
            'category' : 4,
            'difficulty' : 2
        }

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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        """Test that the get_categories function works fine when sending a GET request"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        """Test that the get_questions function works fine when sending a GET request"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_404_sent_requesting_beyond_valid_page(self):
        """Test going beyond valid page.
        
        Test that when calling the get_questions function, if the page is beyond the limit
        of pages given the questions, it throws a 404 error
        """
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        """Testing if delete_question works fine for valid question ids"""
        res = self.client().delete('/questions/21')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 21).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 21)
        self.assertTrue(data['total_questions'])
        self.assertEqual(question, None)

    def test_404_deleting_unexistent_question(self):
        """Testing if delete_question works fine for not valid question ids"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_question(self):
        """Testing if create_or_search_question works fine when given all question attributes"""
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_creating_question_unprocessable(self):
        """Testing if create_or_search_question throws error when not all question attributes are given"""
        res = self.client().post('/questions', json={'question': 'something'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_question(self):
        """Testing if create_or_search_question works fine when "searchTerm" is given"""
        res = self.client().post('/questions', json={'searchTerm': 'painting'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 2)
    
    def test_questions_by_category(self):
        """Testing if questions_by_category works fine when given all question attributes"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_404_questions_by_category_no_such_category(self):
        """Testing if questions_by_category throws 404 error when the category id doesn't exist"""
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_selecting_remaining_question_play_quiz(self):
        """Testing if play_quiz works fine when only one question remains to be asked"""
        res = self.client().post('/quizzes', json={'previous_questions': [16, 17, 19],
                                                  'quiz_category': {'type': 'Art', 'id': '2'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question']['answer'], 'One')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()