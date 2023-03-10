"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    if request.method == 'GET':
        user =  User()
        user = user.query.all()
        return jsonify(list(map(lambda item: item.serialize(), user)))

    return jsonify([]), 200


#PEOPLE

@app.route('/people', methods=['GET'])
def handle_people():
    if request.method == 'GET':
        people =  People()
        people = people.query.all()
        return jsonify(list(map(lambda item: item.serialize(), people)))

    return jsonify([]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def handle_user_by_id(people_id = None):
    if request.method == 'GET':
        if people_id == None:
            return jsonify({"Message: Bad request"}), 400
        else:
            people =  People()
            people = people.query.get(people_id)
            if people is None:
                return jsonify({"Message: Not found"}), 404
            else:
                return jsonify(people.serialize()), 200


@app.route('/people', methods=['POST'])
def add_new_person():
    if request.method == 'POST':
        body = request.json

        if body.get("name") is None or body.get("gender") is None or body.get("birth_year") is None:
            return jsonify({"Message: Bad property"}), 400

        person = People(name=body["name"], gender=body["gender"], birth_year=body["birth_year"])
        db.session.add(person)

        try:
            db.session.commit()
            return jsonify(body),200

        except Exception as error:
            print(error.args)
            db.session.rollback()
            return jsonify({"Message:" f'Error {error.args}'}), 400

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id=None):
    if request.method == 'DELETE':
        if people_id is None:
            return jsonify({"Message: Bad request"}), 400

        if people_id is not None:
            delete_person = People.query.get(people_id)

            if delete_person is None:
                return jsonify({"Message: Not found"}), 400
            else:
                db.session.delete(delete_person)

                try:
                    db.session.commit()
                    return jsonify([]), 204

                except Exception as error:
                    print(error.args)
                    return jsonify({"Message:" f'Error {error.args}'}), 500

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id=None):
    if request.method == 'PUT':
        body = request.json

        person = People()
        update_person = person.query.get(people_id)

        if update_person is None:
            return jsonify({"Message: Not found"}), 400

        else:
            update_person.name = body["name"]
            update_person.gender = body["gender"]
            update_person.birth_year = body["birth_year"]

            try:
                db.session.commit()
                return jsonify(update_person.serialize()), 201

            except Exception as error:
                print(error.args)
                return jsonify({"Message:" f'Error {error.args}'}), 500


#PLANETS

@app.route('/planets', methods=['GET'])
def handle_planets():
    if request.method == 'GET':
        planets =  Planets()
        planets = planets.query.all()
        return jsonify(list(map(lambda item: item.serialize(), planets)))

    return jsonify([]), 200

@app.route('/planets/<int:planets_id>', methods=['GET'])
def handle_planets_by_id(planets_id = None):
    if request.method == 'GET':
        if planets_id == None:
            return jsonify({"Message: Bad request"}), 400
        else:
            planets =  Planets()
            planets = planets.query.get(planets_id)
            if planets is None:
                return jsonify({"Message: Not found"}), 404
            else:
                return jsonify(planets.serialize()), 200


@app.route('/planets', methods=['POST'])
def add_new_planet():
    if request.method == 'POST':
        body = request.json

        if body.get("name") is None or body.get("diameter") is None:
            return jsonify({"Message: Bad property"}), 400

        planet = Planets(name=body["name"], diameter=body["diameter"])
        db.session.add(planet)

        try:
            db.session.commit()
            return jsonify(body),200

        except Exception as error:
            print(error.args)
            db.session.rollback()
            return jsonify({"Message:" f'Error {error.args}'}), 400

@app.route('/planets/<int:planets_id>', methods=['DELETE'])
def delete_planet(planets_id=None):
    if request.method == 'DELETE':
        if planets_id is None:
            return jsonify({"Message: Bad request"}), 400

        if planets_id is not None:
            delete_planet = Planets.query.get(planets_id)

            if delete_planet is None:
                return jsonify({"Message: Not found"}), 400
            else:
                db.session.delete(delete_planet)

                try:
                    db.session.commit()
                    return jsonify([]), 204

                except Exception as error:
                    print(error.args)
                    return jsonify({"Message:" f'Error {error.args}'}), 500

@app.route('/planets/<int:planets_id>', methods=['PUT'])
def update_planet(planets_id=None):
    if request.method == 'PUT':
        body = request.json

        planet = Planets()
        update_planet = planet.query.get(planets_id)

        if update_planet is None:
            return jsonify({"Message: Not found"}), 400

        else:
            update_planet.name = body["name"]
            update_planet.diameter = body["diameter"]

            try:
                db.session.commit()
                return jsonify(update_planet.serialize()), 201

            except Exception as error:
                print(error.args)
                return jsonify({"Message:" f'Error {error.args}'}), 500

#FAVORITES 

@app.route('/favorite/', methods=['GET'])
def handle_favorites():
    if request.method == 'GET':

            favorites =  Favorites()
            favorites = favorites.query.all()
            if favorites is None:
                return jsonify({"Message: Not found"}), 404
            else:
                return jsonify(list(map(lambda item: item.serialize(), favorites))), 200

            

@app.route('/favorite/<int:user_id>/people/<int:people_id>', methods=['POST'])
def add_new_favorite(people_id = None, user_id= None,):
    if request.method == 'POST':

        if user_id is None or people_id is None:
            return jsonify({"Message: Bad property"}), 400
        
        favorite = Favorites(user_id=user_id, people_id=people_id)
        db.session.add(favorite)

        try:
            db.session.commit()
            return jsonify(favorite.serialize()),200

        except Exception as error:
            print(error.args)
            db.session.rollback()
            return jsonify({"Message:" f'Error {error.args}'}), 400
        
@app.route('/favorite/<int:user_id>/people/<int:people_id>', methods=['DELETE'])
def delete_favorite(people_id = None, user_id= None,):
    if request.method == 'DELETE':

        if user_id is None or people_id is None:
            return jsonify({"Message: Bad property"}), 400
        
        if user_id is not None and people_id is not None:
            delete_favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
            db.session.delete(delete_favorite)

        try:
            db.session.commit()
            return jsonify([]), 204

        except Exception as error:
            print(error.args)
            db.session.rollback()
            return jsonify({"Message:" f'Error {error.args}'}), 400
        


# [GET] /users/favorites Get all the favorites that belong to the current user.
# [POST] /favorite/people/<int:people_id> Add a new favorite people to the current user with the people id = people_id.
# [POST] /favorite/planet/<int:planet_id> Add a new favorite planet to the current user with the planet id = planet_id.
# [DELETE] /favorite/planet/<int:planet_id> Delete favorite planet with the id = planet_id.
# [DELETE] /favorite/people/<int:people_id> Delete favorite people with the id = people_id

    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
