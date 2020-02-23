import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from sqlalchemy.exc import DatabaseError


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    drinks_list = [drink.short() for drink in drinks]
    if len(drinks) < 1:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = Drink.query.all()
    drinks_list = [drink.long() for drink in drinks]
    if len(drinks) < 1:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    body = request.get_json()
    validated_body = {}
    required_fields = ['title', 'recipe']
    for field in required_fields:
        resp = body.get(field, None)
        if resp is None:
            abort(400)
        validated_body[field] = resp

    try:
        new_drink = Drink()
        new_drink.title = validated_body['title']
        new_drink.recipe = json.dumps(validated_body['recipe'])
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': new_drink.long(),
        }), 200
    except DatabaseError:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(drink_id):
    body = request.get_json()
    drink = Drink.query.filter(
        Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    validated_body = {}
    fields = ['title', 'recipe']
    for field in fields:
        resp = body.get(field, None)
        validated_body[field] = resp

    if validated_body['title'] is not None:
        drink.title = validated_body['title']
    if validated_body['recipe'] is not None:
        drink.recipe = json.dumps(validated_body['recipe'])

    drink_dict = drink.long()
    drink_array = [value for value in drink_dict.values()]
    try:
        drink.update()
        return jsonify({
            'success': True,
            'drinks': drink_array,
        }), 200
    except DatabaseError:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    drink = Drink.query.filter(
        Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink_id,
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed."
    })


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error."
    })
