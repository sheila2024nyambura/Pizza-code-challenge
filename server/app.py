from flask import Flask, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Restaurant,Pizza,Restaurant_Pizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return 'WELCOME '

class Restaurants(Resource):
    def get(self):
        response_dict= [n.to_dict() for n in Restaurant.query.all()]
        response= make_response(jsonify(response_dict), 200)
        return  response

api.add_resource(Restaurants, '/restaurants')

class RestaurantsById(Resource):
    def get(self, id):
        record= Restaurant.query.filter_by(id=id).first()
        if record is None:
            response= make_response(jsonify({'error':'Restaurant not found'}),404)
            return response
        else:
            record_dict= record.serialize()
            response = make_response(record_dict, 200)
            return response
        
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            response= make_response(jsonify({'error':'Restaurant not found'}),404)
            return response
        db.session.delete(restaurant)
        db.session.commit()

        response = make_response(jsonify('Success: id deleted'))
        return response
api.add_resource(RestaurantsById, '/restaurants/<int:id>')

class Pizzas (Resource):
    def get(self): 
        pizza_dict = [pizza.serialize() for pizza in Pizza.query.all()]
        response = make_response(jsonify(pizza_dict), 200)
        return response
api.add_resource(Pizzas, '/pizzas')

class Restaurant_Pizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            price = data.get("price")
            pizza_id = data.get("pizza_id")
            restaurant_id = data.get("restaurant_id")

            pizza= Pizza.query.get(pizza_id)
            restaurant=  Restaurant.query.get(restaurant_id)

            if not pizza and restaurant:
                return make_response(jsonify({"message":["Pizza and Restaurant does not exist"]}),404)
        
            else:
                new_pizza= Restaurant_Pizza(price=price, pizza_id=pizza_id,  restaurant_id=restaurant_id )
                db.session.add(new_pizza)
                db.session.commit()

            return make_response(jsonify(new_pizza.serialize()), 201)
            
        except:
            error_dict= {"errors" : ["validation errors"]}
            response= make_response(error_dict, 404)
            db.session.rollback()
            return response

if __name__ == '__main__':
    app.run(port=5555)
