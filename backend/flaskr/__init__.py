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

    @app.route('/questions', methods=['POST'])
    def add_new_question():
        body = request.get_json()
        question_elements = ['question', 'answer', 'category', 'difficulty']
        if not all(key in body for key in question_elements):
            abort(422)
        try:
            new_question = Question(question=body['question'], answer=body['answer'],
                                    category=body['category'], difficulty=body['difficulty'])
            db.session.add(new_question)
            db.session.commit()
        except:
            db.session.rollback()
            print('err: ', sys.exc_info())
            abort(500)
        finally:
            db.session.close()
        return jsonify({
            'success': True
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            db.session.delete(question)
            db.session.commit()
        except:
            if question is None:
                abort(404)
            db.session.rollback()
            print(sys.exc_info())
            abort(500)
        finally:
            db.session.close()
        return jsonify({
            'success': True
        })

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

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'error': 422,
            'message': 'unprocessable entity'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app

