
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from datetime import datetime
import os
import json

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client.test_mongodb
users_collection = db.users
products_collection = db.products
departemen_collection = db.departemen
jabatan_collection = db.jabatan
karyawan_collection = db.karyawan
absensi_collection = db.absensi
gaji_collection = db.gaji



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

# Custom JSON Encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# Helper function to convert MongoDB Object to JSON-compatible format
def object_to_dict(obj):
    if obj is None:
        return None
    obj_copy = obj.copy()
    obj_copy['_id'] = str(obj_copy['_id'])
    return obj_copy


@app.route('/')
def user():
    return render_template('index.html')

@app.route('/product')
def products():
    return render_template('products.html')

@app.route('/departemen')
def departemen():
    return render_template('departemen.html')

@app.route('/jabatan')
def jabatan():
    return render_template('jabatan.html')


@app.route('/karyawan')
def karyawan():
    return render_template('karyawan.html')

@app.route('/absensi')
def absensi():
    return render_template('absensi.html')

@app.route('/gaji')
def gaji():
    return render_template('gaji.html')


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

@app.route('/departemens', methods=['POST'])
def create_departemen():
    """Create a new departemen"""
    data = request.get_json()
    nama_departemen = data.get('nama_departemen')

    if not nama_departemen:
        return jsonify({'message': 'Nama departemen is required!'}), 400

    departemen = {
        'nama_departemen': nama_departemen
    }

    result = departemen_collection.insert_one(departemen)
    return jsonify({
        'message': 'Departemen created!', 
        'departemen_id': str(result.inserted_id)
    }), 201

@app.route('/departemens', methods=['GET'])
def get_departemens():
    """Retrieve all departemen records"""
    departemen = list(departemen_collection.find())
    departemen_list = [object_to_dict(dep) for dep in departemen]
    return jsonify(departemen_list), 200

@app.route('/departemens/<departemen_id>', methods=['GET'])
def get_single_departemen(departemen_id):
    """Retrieve a single departemen by ID"""
    try:
        departemen = departemen_collection.find_one({'_id': ObjectId(departemen_id)})
        if not departemen:
            return jsonify({'message': 'Departemen not found!'}), 404
        return jsonify(object_to_dict(departemen)), 200
    except Exception as e:
        return jsonify({'message': f'Invalid departemen ID: {str(e)}'}), 400

@app.route('/departemens/<departemen_id>', methods=['PUT'])
def update_departemen(departemen_id):
    """Update an existing departemen"""
    data = request.get_json()
    nama_departemen = data.get('nama_departemen')

    if not nama_departemen:
        return jsonify({'message': 'Nama departemen is required!'}), 400

    try:
        result = departemen_collection.update_one(
            {'_id': ObjectId(departemen_id)}, 
            {'$set': {'nama_departemen': nama_departemen}}
        )

        if result.matched_count == 0:
            return jsonify({'message': 'Departemen not found!'}), 404

        return jsonify({'message': 'Departemen updated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'Update failed: {str(e)}'}), 400

@app.route('/departemens/<departemen_id>', methods=['DELETE'])
def delete_departemen(departemen_id):
    """Delete a departemen"""
    try:
        result = departemen_collection.delete_one({'_id': ObjectId(departemen_id)})
        if result.deleted_count == 0:
            return jsonify({'message': 'Departemen not found!'}), 404
        return jsonify({'message': 'Departemen deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'Delete failed: {str(e)}'}), 400# CRUD routes for Jabatan

@app.route('/jabatans', methods=['POST'])
def create_jabatan():
    """Create a new jabatan"""
    data = request.get_json()
    nama_jabatan = data.get('nama_jabatan')
    deskripsi = data.get('deskripsi', '')

    if not nama_jabatan:
        return jsonify({'message': 'Nama jabatan is required!'}), 400

    jabatan = {
        'nama_jabatan': nama_jabatan,
        'deskripsi': deskripsi
    }

    result = jabatan_collection.insert_one(jabatan)
    return jsonify({'message': 'Jabatan created!', 'jabatan_id': str(result.inserted_id)}), 201

@app.route('/jabatans', methods=['GET'])
def get_jabatan():
    """Get all jabatans"""
    jabatan = jabatan_collection.find()
    jabatan_list = [object_to_dict(jab) for jab in jabatan]
    return jsonify(jabatan_list), 200

@app.route('/jabatans/<jabatan_id>', methods=['GET'])
def get_single_jabatan(jabatan_id):
    """Get a single jabatan by ID"""
    try:
        jabatan = jabatan_collection.find_one({'_id': ObjectId(jabatan_id)})
        if not jabatan:
            return jsonify({'message': 'Jabatan not found!'}), 404
        return jsonify(object_to_dict(jabatan)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/jabatans/<jabatan_id>', methods=['PUT'])
def update_jabatan(jabatan_id):
    """Update a jabatan"""
    data = request.get_json()
    nama_jabatan = data.get('nama_jabatan')
    deskripsi = data.get('deskripsi')

    update_data = {}
    if nama_jabatan:
        update_data['nama_jabatan'] = nama_jabatan
    if deskripsi:
        update_data['deskripsi'] = deskripsi

    if not update_data:
        return jsonify({'message': 'No fields to update!'}), 400

    result = jabatan_collection.update_one(
        {'_id': ObjectId(jabatan_id)}, 
        {'$set': update_data}
    )

    if result.matched_count == 0:
        return jsonify({'message': 'Jabatan not found!'}), 404

    return jsonify({'message': 'Jabatan updated successfully!'}), 200

@app.route('/jabatans/<jabatan_id>', methods=['DELETE'])
def delete_jabatan(jabatan_id):
    """Delete a jabatan"""
    result = jabatan_collection.delete_one({'_id': ObjectId(jabatan_id)})

    if result.deleted_count == 0:
        return jsonify({'message': 'Jabatan not found!'}), 404

    return jsonify({'message': 'Jabatan deleted successfully!'}), 200


@app.route('/jabatan/list', methods=['GET'])
def get_jabatan_list():
    """Alias for getting all jabatans"""
    return get_jabatan()  # Reuse the existing function


@app.route('/departemen/list', methods=['GET'])
def get_departemen_list():
    """Alias for getting all jabatans"""
    return get_departemens()  # Reuse the existing function


# CRUD routes for Karyawan
@app.route('/karyawans', methods=['POST'])
def create_karyawan():
    try:
        data = request.get_json()
        required_fields = ['nama_lengkap', 'email', 'departemen_id', 'jabatan_id']

        # Enhanced validation
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required!'}), 400

        # Validate ObjectId
        try:
            departemen_id = ObjectId(data['departemen_id'])
            jabatan_id = ObjectId(data['jabatan_id'])
        except Exception:
            return jsonify({'message': 'Invalid departemen or jabatan ID'}), 400

        # Check if departemen and jabatan exist
        departemen = departemen_collection.find_one({'_id': departemen_id})
        jabatan = jabatan_collection.find_one({'_id': jabatan_id})

        if not departemen:
            return jsonify({'message': 'Departemen not found!'}), 404
        if not jabatan:
            return jsonify({'message': 'Jabatan not found!'}), 404

        karyawan = {
            'nama_lengkap': data['nama_lengkap'],
            'email': data['email'],
            'nomor_telepon': data.get('nomor_telepon'),
            'tanggal_lahir': data.get('tanggal_lahir'),
            'alamat': data.get('alamat'),
            'tanggal_masuk': data.get('tanggal_masuk', datetime.now().isoformat()),
            'departemen_id': departemen_id,
            'jabatan_id': jabatan_id,
            'status': data.get('status', 'aktif')
        }

        result = karyawan_collection.insert_one(karyawan)
        return jsonify({
            'message': 'Karyawan created successfully!', 
            'karyawan_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({
            'message': 'Failed to create karyawan.', 
            'error': str(e)
        }), 500


@app.route('/karyawans', methods=['GET'])
def get_karyawan():
    try:
        # Aggregate to join departemen and jabatan information
        pipeline = [
            {
                '$lookup': {
                    'from': 'departemen',
                    'localField': 'departemen_id',
                    'foreignField': '_id',
                    'as': 'departemen'
                }
            },
            {
                '$lookup': {
                    'from': 'jabatan',
                    'localField': 'jabatan_id',
                    'foreignField': '_id',
                    'as': 'jabatan'
                }
            },
            {
                '$unwind': '$departemen'
            },
            {
                '$unwind': '$jabatan'
            }
        ]

        karyawans = list(karyawan_collection.aggregate(pipeline))

        # Convert to a format that includes departemen and jabatan names
        karyawan_list = []
        for k in karyawans:
            karyawan_dict = object_to_dict(k)
            karyawan_dict['departemen_name'] = k['departemen']['nama_departemen']
            karyawan_dict['jabatan_name'] = k['jabatan']['nama_jabatan']
            karyawan_list.append(karyawan_dict)

        # Use custom JSON encoder to handle ObjectId
        return app.response_class(
            response=json.dumps(karyawan_list, cls=JSONEncoder),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({
            'message': 'Failed to fetch karyawan list.', 
            'error': str(e)
        }), 500

@app.route('/karyawans/<karyawan_id>', methods=['GET'])
def get_karyawan_by_id(karyawan_id):
    try:
        # Find the karyawan by ID
        karyawan = karyawan_collection.find_one({'_id': ObjectId(karyawan_id)})
        if not karyawan:
            return jsonify({'message': 'Karyawan not found!'}), 404

        # Lookup departemen and jabatan information
        departemen = departemen_collection.find_one({'_id': karyawan['departemen_id']}) if 'departemen_id' in karyawan else None
        jabatan = jabatan_collection.find_one({'_id': karyawan['jabatan_id']}) if 'jabatan_id' in karyawan else None

        # Format the response data
        karyawan_dict = object_to_dict(karyawan)
        karyawan_dict['departemen_name'] = departemen['nama_departemen'] if departemen else None
        karyawan_dict['jabatan_name'] = jabatan['nama_jabatan'] if jabatan else None
        karyawan_dict['departemen_id'] = str(departemen['_id']) if departemen else None
        karyawan_dict['jabatan_id'] = str(jabatan['_id']) if jabatan else None

        return app.response_class(
            response=json.dumps(karyawan_dict, cls=JSONEncoder),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({'message': 'Failed to fetch karyawan details.', 'error': str(e)}), 500

@app.route('/karyawans/<karyawan_id>', methods=['PUT'])
def update_karyawan(karyawan_id):
    try:
        data = request.get_json()
        update_data = {key: data[key] for key in data if key in ['nama_lengkap', 'email', 'nomor_telepon', 'tanggal_lahir', 'alamat', 'status']}
        if 'departemen_id' in data:
            update_data['departemen_id'] = ObjectId(data['departemen_id'])
        if 'jabatan_id' in data:
            update_data['jabatan_id'] = ObjectId(data['jabatan_id'])

        result = karyawan_collection.update_one({'_id': ObjectId(karyawan_id)}, {'$set': update_data})
        if result.matched_count == 0:
            return jsonify({'message': 'Karyawan not found!'}), 404

        return jsonify({'message': 'Karyawan updated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to update karyawan.', 'error': str(e)}), 500


@app.route('/karyawans/<karyawan_id>', methods=['DELETE'])
def delete_karyawan(karyawan_id):
    try:
        result = karyawan_collection.delete_one({'_id': ObjectId(karyawan_id)})
        if result.deleted_count == 0:
            return jsonify({'message': 'Karyawan not found!'}), 404
        return jsonify({'message': 'Karyawan deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete karyawan.', 'error': str(e)}), 500

# CRUD routes for Absensi
@app.route('/absensis', methods=['POST'])
def create_absensi():
    data = request.get_json()
    karyawan_id = data.get('karyawan_id')
    tanggal = data.get('tanggal', datetime.now().date().isoformat())
    waktu_masuk = data.get('waktu_masuk', datetime.now().time().isoformat())
    waktu_keluar = data.get('waktu_keluar')
    status_absensi = data.get('status_absensi', 'hadir')

    if not karyawan_id:
        return jsonify({'message': 'Karyawan ID is required!'}), 400

    absensi = {
        'karyawan_id': ObjectId(karyawan_id),
        'tanggal': tanggal,
        'waktu_masuk': waktu_masuk,
        'waktu_keluar': waktu_keluar,
        'status_absensi': status_absensi
    }

    result = absensi_collection.insert_one(absensi)
    return jsonify({'message': 'Absensi created!', 'absensi_id': str(result.inserted_id)}), 201

@app.route('/absensis', methods=['GET'])
def get_absensi():
    absensi = absensi_collection.find()
    absensi_list = [object_to_dict(a) for a in absensi]
    return app.response_class(
        response=json.dumps(absensi_list, cls=JSONEncoder),
        status=200,
        mimetype='application/json'
    )

@app.route('/absensis/<absensi_id>', methods=['GET'])
def get_single_absensi(absensi_id):
    absensi = absensi_collection.find_one({'_id': ObjectId(absensi_id)})
    if not absensi:
        return jsonify({'message': 'Absensi not found!'}), 404
    return jsonify(object_to_dict(absensi)), 200

@app.route('/absensis/<absensi_id>', methods=['PUT'])
def update_absensi(absensi_id):
    data = request.get_json()

    update_data = {}
    for field in ['karyawan_id', 'tanggal', 'waktu_masuk', 'waktu_keluar', 'status_absensi']:
        if field in data:
            if field == 'karyawan_id':
                update_data[field] = ObjectId(data[field])
            else:
                update_data[field] = data[field]

    if not update_data:
        return jsonify({'message': 'No fields to update!'}), 400

    result = absensi_collection.update_one(
        {'_id': ObjectId(absensi_id)}, 
        {'$set': update_data}
    )

    if result.matched_count == 0:
        return jsonify({'message': 'Absensi not found!'}), 404

    return jsonify({'message': 'Absensi updated successfully!'}), 200

@app.route('/absensis/<absensi_id>', methods=['DELETE'])
def delete_absensi(absensi_id):
    result = absensi_collection.delete_one({'_id': ObjectId(absensi_id)})
    if result.deleted_count == 0:
        return jsonify({'message': 'Absensi not found!'}), 404
    return jsonify({'message': 'Absensi deleted successfully!'}), 200

# CRUD routes for Gaji
@app.route('/gajis', methods=['POST'])
def create_gaji():
    data = request.get_json()
    karyawan_id = data.get('karyawan_id')
    bulan = data.get('bulan', datetime.now().strftime('%B %Y'))
    gaji_pokok = data.get('gaji_pokok')
    tunjangan = data.get('tunjangan', 0)
    potongan = data.get('potongan', 0)
    total_gaji = data.get('total_gaji')

    if not karyawan_id or not gaji_pokok:
        return jsonify({'message': 'Karyawan ID and Gaji Pokok are required!'}), 400

    # Calculate total gaji if not provided
    if not total_gaji:
        total_gaji = float(gaji_pokok) + float(tunjangan) - float(potongan)

    gaji = {
        'karyawan_id': ObjectId(karyawan_id),
        'bulan': bulan,
        'gaji_pokok': float(gaji_pokok),
        'tunjangan': float(tunjangan),
        'potongan': float(potongan),
        'total_gaji': float(total_gaji)
    }

    result = gaji_collection.insert_one(gaji)
    return jsonify({'message': 'Gaji created!', 'gaji_id': str(result.inserted_id)}), 201

@app.route('/gajis', methods=['GET'])
def get_gaji():
    gaji = gaji_collection.find()
    gaji_list = [object_to_dict(g) for g in gaji]
    return app.response_class(
        response=json.dumps(gaji_list, cls=JSONEncoder),
        status=200,
        mimetype='application/json'
    )

# Add these routes to your existing app.py file

@app.route('/gajis/<gaji_id>', methods=['PUT'])
def update_gaji(gaji_id):
    try:
        data = request.get_json()
        
        # Prepare update data
        update_data = {}
        if 'karyawan_id' in data:
            update_data['karyawan_id'] = ObjectId(data['karyawan_id'])
        if 'bulan' in data:
            update_data['bulan'] = data['bulan']
        if 'gaji_pokok' in data:
            update_data['gaji_pokok'] = float(data['gaji_pokok'])
        if 'tunjangan' in data:
            update_data['tunjangan'] = float(data['tunjangan'])
        if 'potongan' in data:
            update_data['potongan'] = float(data['potongan'])
        
        # Recalculate total gaji if relevant fields are updated
        if 'gaji_pokok' in update_data or 'tunjangan' in update_data or 'potongan' in update_data:
            gaji_pokok = update_data.get('gaji_pokok', existing_gaji['gaji_pokok'])
            tunjangan = update_data.get('tunjangan', existing_gaji['tunjangan'])
            potongan = update_data.get('potongan', existing_gaji['potongan'])
            update_data['total_gaji'] = float(gaji_pokok) + float(tunjangan) - float(potongan)
        
        # Perform the update
        result = gaji_collection.update_one(
            {'_id': ObjectId(gaji_id)}, 
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Gaji not found!'}), 404
        
        return jsonify({'message': 'Gaji updated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to update gaji.', 'error': str(e)}), 500

@app.route('/gajis/<gaji_id>', methods=['DELETE'])
def delete_gaji(gaji_id):
    try:
        result = gaji_collection.delete_one({'_id': ObjectId(gaji_id)})
        
        if result.deleted_count == 0:
            return jsonify({'message': 'Gaji not found!'}), 404
        
        return jsonify({'message': 'Gaji deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete gaji.', 'error': str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


