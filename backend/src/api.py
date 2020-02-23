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

## ROUTES
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
        new_drink.title=validated_body['title']
        new_drink.recipe=json.dumps(validated_body['recipe'])
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': new_drink.long(),
        }), 201
    except DatabaseError:
        abort(422)
    

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


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


## Error Handling
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

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
