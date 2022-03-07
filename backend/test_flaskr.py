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
        self.database_path = "postgres://{}/{}".format('postgres:123@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # from list of Category objects via .all(), to dict with items like 'id':'type'
        # as the categories don't change we define here, to save space
        # BUG POTENTIAL if categories were changed during testing
        categories_list = [category.format() for category in Category.query.all()]
        self.categories = {item['id']: item['type'] for item in categories_list}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        body = json.loads(res.data)
        self.assertEqual(body, self.categories)
        self.assertEqual(res.status_code, 200)

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        body = json.loads(res.data)
        questions = [question.format() for question in Question.query.all()]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['questions'], questions[:10])
        self.assertEqual(body['total_questions'], len(questions))
        self.assertEqual(body['categories'], self.categories)
        # empty as not implemented
        self.assertEqual(body['current_category'], {})

    def test_404_if_page_not_found(self):
        impossible_page = len(Question.query.all()) + 1
        res = self.client().get(f'/questions?page={impossible_page}')
        self.assertEqual(res.status_code, 404)

    def test_get_question_by_category(self):
        # selecting first valid id
        category_id = list(self.categories.keys())[0]
        res = self.client().get(f'/categories/{category_id}/questions')
        body = json.loads(res.data)

        questions_by_category = [question.format() for question in Question.query.filter_by(category=category_id).all()]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['questions'], questions_by_category)
        self.assertEqual(body['total_questions'], len(Question.query.all()))
        self.assertEqual(body['current_category'], {})

    def test_404_if_category_not_found(self):
        impossible_category = 999999
        res = self.client().get(f'/categories/{impossible_category}/questions')
        self.assertEqual(res.status_code, 404)

    # POST SEARCH
    def test_search_for_existing(self):
        search_object = Question.query.first().format()
        search_term = search_object['question']
        res = self.client().post('/questions/search', json={
            'searchTerm': search_term
        })
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['questions'], [search_object])
        self.assertEqual(body['total_questions'], len(Question.query.all()))
        self.assertEqual(body['current_category'], {})

    def test_search_for_not_existing(self):
        search_term = 'qqqqqqqqq'
        res = self.client().post('/questions/search', json={
            'searchTerm': search_term
        })
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        # response should be empty
        self.assertEqual(body['questions'], [])
        self.assertEqual(body['total_questions'], len(Question.query.all()))
        self.assertEqual(body['current_category'], {})

    def test_422_if_bad_search(self):
        res = self.client().post('questions/search', json={
            'wrongSearch': 'o.o'
        })
        self.assertEqual(res.status_code, 422)



    # DELETE QUESTION
    def test_delete_question(self):
        # delete from behind
        question_id = Question.query.order_by('id').all()[-1].format()['id']
        res = self.client().delete(f'/questions/{question_id}')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Question.query.get(question_id))

    def test_404_if_question_not_found(self):
        question_id = 9999999
        res = self.client().delete(f'/questions/{question_id}')
        self.assertEqual(res.status_code, 404)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()