import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    # get the post request data  'title' , 'recipe'
    body = request.get_json()
    # if request missing any data
    if (not (('title' in body) or ('recipe' in body))):
        abort(400)
        # if empty
    if ((body.get('title') == "") or (body.get('recipe') == "")):
        abort(422)
    recipes = body.get('recipe')
    for recipe in recipes:
        if ((recipe[0] == "")or (recipe[1] == "")):
            abort(422)
    try:
        # create drink
        drink = Drink(title=body.get('title', None), recipe=json.dumps(body.get('recipe', None)))
        drink.insert()
        # return a Response with the JSON representation 'sucsses' , 'drink'
        return jsonify({
            'success': True,
            "drinks": [drink.long()]
        })
    except:
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
@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt,drink_id):
    # get the post request data  'title' , 'recipe'
    body = request.get_json()
    if ((not('title' in body) and not('recipe' in body))):
        abort(400)
    if ((body.get('title') == "") and (body.get('recipe') == "")):
        abort(422)
    # get drink that matches with drink_id
    drink = Drink.query.get(drink_id)
    # if there isnot such id with this id
    if drink is None:
        abort(404)

    try:
        if ('title' in body):
            drink.title = body.get('title', None)
        if ('recipe' in body):
            recipes = body.get('recipe')
            for recipe in recipes:
               if ((recipe[0] == "") or (recipe[1] == "")):
                   abort(422)
            drink.recipe = json.dumps(body.get('recipe', None))

        drink.update()
        # return a Response with the JSON representation 'sucsses' , 'drink'
        return jsonify({
            'success': True,
            "drinks": [drink.long()]
        })
    except:
        abort(422)



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt,drink_id):
    # get drink that matches with drink_id
    drink = Drink.query.get(drink_id)
    # if there isnot such id with this id
    if drink is None:
      abort(422)
    # if exist
    else:
      # delete this drink
      drink.delete()
      # return a Response with the JSON representation 'sucsses' , 'delete'
      return jsonify({
        'success': True,
        'delete': drink_id
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error
                    }), error.status_code
