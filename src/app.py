"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

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

# User endpoints
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# Character endpoints
@app.route('/people', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route('/people/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id)
    if character:
        return jsonify(character.serialize()), 200
    return jsonify({"msg": "Character not found"}), 404

@app.route('/people', methods=['POST'])
def add_character():
    data = request.json
    new_character = Character(name=data['name'])
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 201

@app.route('/people/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    data = request.json
    character = Character.query.get(character_id)
    if character:
        character.name = data['name']
        db.session.commit()
        return jsonify(character.serialize()), 200
    return jsonify({"msg": "Character not found"}), 404

@app.route('/people/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get(character_id)
    if character:
        db.session.delete(character)
        db.session.commit()
        return jsonify({"msg": "Character deleted"}), 200
    return jsonify({"msg": "Character not found"}), 404

# Planet endpoints
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    return jsonify({"msg": "Planet not found"}), 404

@app.route('/planets', methods=['POST'])
def add_planet():
    data = request.json
    new_planet = Planet(name=data['name'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.json
    planet = Planet.query.get(planet_id)
    if planet:
        planet.name = data['name']
        db.session.commit()
        return jsonify(planet.serialize()), 200
    return jsonify({"msg": "Planet not found"}), 404

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify({"msg": "Planet deleted"}), 200
    return jsonify({"msg": "Planet not found"}), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)