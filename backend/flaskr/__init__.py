import sys

from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Question, Category, db
import random

QUESTIONS_PER_PAGE = 10


def paginate_questions(questions: list, page: int):
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    selection = [question.format() for question in questions[start:end]]
    return selection


def get_and_validate_json():
    body = request.get_json()
    if not body:
        abort(400)
    return body


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r'*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        # list of dicts
        categories_list = [category.format() for category in Category.query.all()]
        # single dict via dict comprehension
        categories = {item['id']: item['type'] for item in categories_list}

        return jsonify(categories)

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
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
        body = get_and_validate_json()
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
        body = get_and_validate_json()
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

    @app.route('/quizzes', methods=['POST'])
    def get_questions_for_quiz():
        body = get_and_validate_json()
        if not all(k in body for k in ('previous_questions', 'quiz_category')):
            abort(422)
        quiz_category_id = body['quiz_category']['id']
        questions_by_category = [question.format() for question in
                                 Question.query.filter_by(category=quiz_category_id).all()]
        # get respective question_ids for all questions and already asked questions
        # as set to use set.difference afterwards
        questions_by_category_ids = set([q['id'] for q in questions_by_category])
        previous_questions_ids = set(body['previous_questions'])
        # get ids of questions, that haven't been asked yet
        open_questions_ids = questions_by_category_ids.difference(previous_questions_ids)
        # the anonymous function checks if the question's id is in the open_questions and if True,
        # filter yields it and then we turn the result into list
        open_questions = list(filter(lambda q: q['id'] in open_questions_ids, questions_by_category))
        if open_questions:
            open_question = random.choice(open_questions)
        else:
            open_question = False
        return jsonify({
            'question': open_question
        })

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
