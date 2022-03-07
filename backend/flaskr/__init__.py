import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(questions: list, page: int):
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    selection = [question.format() for question in questions[start:end]]
    return selection


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app, resources={r'*': {'origins': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories')
    def get_categories():
        # list of dicts
        categories_list = [category.format() for category in Category.query.all()]
        # single dict via dict comprehension
        categories = {item['id']: item['type'] for item in categories_list}

        return jsonify(categories)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def get_questions():
        page = int(request.args['page'])
        questions = Question.query.all()
        selection = paginate_questions(questions, page)
        # 404 if selection is empty
        if not selection:
            abort(404)
        categories_list = [category.format() for category in Category.query.all()]
        categories = {item['id']: item['type'] for item in categories_list}
        # not implemented in frontend
        current_category = {}

        return jsonify({
            'questions': selection,
            'total_questions': len(questions),
            'categories': categories,
            'current_category': current_category
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    @app.route('/questions/search', methods=['POST'])
    def search_for_question():
        body = request.get_json()
        if 'searchTerm' not in body:
            abort(422)
        search_term = body['searchTerm']
        questions = [question.format() for question in
                     Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()]
        return jsonify({
            'questions': questions,
            'total_questions': len(Question.query.all()),
            'current_category': {}
        })

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        questions_by_category = [question.format() for question in Question.query.filter_by(category=category_id).all()]
        if not questions_by_category:
            abort(404)
        total_questions = len(Question.query.all())
        current_category = {}

        return jsonify({
            'questions': questions_by_category,
            'total_questions': total_questions,
            'current_category': current_category
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

