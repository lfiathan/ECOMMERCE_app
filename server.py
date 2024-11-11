from flask import Flask, request, jsonify
from flask import render_template
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
import os

app = Flask(__name__)

# MongoDB connection setup

client = MongoClient(os.getenv('MONGO_URI'))
db = client.test_mongodb
users_collection = db.users
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

#helper function to convert mongoDB object to JSON
def user_to_dict(user):
    user['_id'] = str(user['_id']) #convert object to string
    return user

@app.route('/')
def home():
    return render_template('index.html')

# Create = create users
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    
    if not name or not email:
        return jsonify({'massage': 'Name and email didapatkan'})

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
    users_list = [user_to_dict(user) for user in users]
    return jsonify(users_list), 200

# Read: Get a user by ID
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    return jsonify(user_to_dict(user)), 200

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

