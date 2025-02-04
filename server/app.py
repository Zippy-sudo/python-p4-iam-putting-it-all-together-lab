#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        new_user_data = request.get_json()

        if not new_user_data.get("username"):
            response = make_response({"Error":"Unprocessable Entity"}, 422)
            return response

        else:
            new_user = User(
                username = new_user_data.get("username"),
                image_url = new_user_data.get("image_url"),
                bio = new_user_data.get("bio")
            )
            new_user.password_hash = new_user_data.get("password")
            db.session.add(new_user)
            db.session.commit()

            session["user_id"] = new_user.id
            
            response = make_response(new_user.to_dict(),201)
            return response


class CheckSession(Resource):
    
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()

        if user:
            user_dict = user.to_dict()
            return make_response({"id":user_dict["id"], "username":user_dict["username"], "image_url":user_dict["image_url"], "bio":user_dict["bio"]}, 200)
        
        return make_response({"Error": "Login to continue"}, 401)

class Login(Resource):
    
    def post(self):
        user = User.query.filter_by(username = request.get_json()["username"]).first()

        if user and user.authenticate(request.get_json()["password"]):
            user_dict = user.to_dict()
            session["user_id"] = user.id
            response = make_response({"id":user_dict["id"], "username":user_dict["username"], "image_url":user_dict["image_url"], "bio":user_dict["bio"]}, 200)

            return response
        
        return make_response({"Error": "Unauthorized"}, 401)

class Logout(Resource):

    def delete(self):
        if not session["user_id"]:
            return make_response({"Error":"Unauthorized"}, 401)
        
        session["user_id"] = None
        return make_response({}, 204)


class RecipeIndex(Resource):
    
    def get(self):
        if not session["user_id"]:
            return make_response({"Error":"Unauthorized"},401)
        
        response = [recipe.to_dict() for recipe in Recipe.query.all()]
        return make_response(response,200)
    
    def post(self):
        new_recipe_data = request.get_json()
        if not session["user_id"]:
            return make_response({"Error":"Unauthorized"}, 401)
        elif new_recipe_data.get("title") and len(new_recipe_data.get("instructions")) >= 50 and new_recipe_data.get("minutes_to_complete"):

                new_recipe = Recipe(
                    title = new_recipe_data["title"],
                    instructions = new_recipe_data["instructions"],
                    minutes_to_complete = new_recipe_data["minutes_to_complete"],
                    user_id = session["user_id"]
                )
                db.session.add(new_recipe)
                db.session.commit()

                response = make_response(new_recipe.to_dict(), 201)
                return response
        
        else:
            return make_response({"Error":"Unprocessable Entity"}, 422)


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)