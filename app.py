
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client.test_mongodb
users_collection = db.users
products_collection = db.products
departemen_collection = db.departemen
jabatan_collection = db.jabatan
karyawan_collection = db.karyawan


# Helper function to convert MongoDB Object to JSON-compatible format
def object_to_dict(obj):
    obj['_id'] = str(obj['_id'])  # convert ObjectId to string
    return obj


@app.route('/departemen')
def departemen():
    return render_template('departemen.html')

@app.route('/jabatan')
def jabatan():
    return render_template('jabatan.html')


@app.route('/karyawan')
def karyawan():
    return render_template('karyawan.html')


@app.route('/gaji')
def gaji():
    return render_template('gaji.html')


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
    return jsonify(gaji_list), 

@app.route('/departemen/list', methods=['GET'])
def get_departemen_list():
    """Alias for getting all jabatans"""
    return get_departemens()  # Reuse the existing function

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
        
        return jsonify(karyawan_list), 200
    except Exception as e:
        return jsonify({
            'message': 'Failed to fetch karyawan list.', 
            'error': str(e)
        }), 500

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


