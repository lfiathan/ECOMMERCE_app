
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
import os

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client.test_mongodb
users_collection = db.users
products_collection = db.products

# Check MongoDB connection
try:
    client.admin.command('ping')  # 'ping' command tests connection
    print("MongoDB connection successful!")
except ConnectionFailure:
    print("MongoDB connection failed!")

# Sample route to check the connection via a request
@app.route('/check_db')
def check_db():
    try:
        # Try a simple query
        db_names = client.list_database_names()
        return f"Connected to MongoDB! Databases: {db_names}", 200
    except Exception as e:
        return f"Database connection error: {str(e)}", 500

# Helper function to convert MongoDB Object to JSON-compatible format
def object_to_dict(obj):
    obj['_id'] = str(obj['_id'])  # convert ObjectId to string
    return obj

@app.route('/')
def user():
    return render_template('index.html')


@app.route('/product')
def products():
    return render_template('products.html')

# Create user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'message': 'Name and email are required!'}), 400

    user = {
        'name': name,
        'email': email
    }

    result = users_collection.insert_one(user)
    return jsonify({'message': 'User created!', 'user_id': str(result.inserted_id)}), 201

# Read: Get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = users_collection.find()
    users_list = [object_to_dict(user) for user in users]
    return jsonify(users_list), 200

# Read: Get a user by ID
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    return jsonify(object_to_dict(user)), 200

# Update: Modify an existing user
@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    update_data = {}
    if name:
        update_data['name'] = name
    if email:
        update_data['email'] = email

    if not update_data:
        return jsonify({'message': 'No fields to update!'}), 400

    result = users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
    if result.matched_count == 0:
        return jsonify({'message': 'User not found!'}), 404

    return jsonify({'message': 'User updated successfully!'}), 200

# Delete: Remove a user by ID
@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = users_collection.delete_one({'_id': ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({'message': 'User not found!'}), 404
    return jsonify({'message': 'User deleted successfully!'}), 200

# CRUD routes for products
@app.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        description = data.get('description', '')

        if not name or not price:
            return jsonify({'message': 'Name and price are required!'}), 400

        product = {
            'name': name,
            'price': float(price),
            'description': description
        }

        result = products_collection.insert_one(product)
        return jsonify({
            'message': 'Product created!', 
            'product_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'message': f'Error creating product: {str(e)}'}), 500

@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = products_collection.find()
        if not products:
            return jsonify({'message': 'No products found!'}), 404
        products_list = [object_to_dict(product) for product in products]
        return jsonify(products_list), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching products: {str(e)}'}), 500

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'message': 'Product not found!'}), 404
        return jsonify(object_to_dict(product)), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching product: {str(e)}'}), 500

@app.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        description = data.get('description')

        update_data = {}
        if name:
            update_data['name'] = name
        if price:
            update_data['price'] = float(price)
        if description:
            update_data['description'] = description

        if not update_data:
            return jsonify({'message': 'No fields to update!'}), 400

        result = products_collection.update_one(
            {'_id': ObjectId(product_id)}, 
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Product not found!'}), 404

        return jsonify({'message': 'Product updated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'Error updating product: {str(e)}'}), 500

@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        result = products_collection.delete_one({'_id': ObjectId(product_id)})
        if result.deleted_count == 0:
            return jsonify({'message': 'Product not found!'}), 404
        return jsonify({'message': 'Product deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'Error deleting product: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

