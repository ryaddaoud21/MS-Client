from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock Database
customers = [
    {"id": 1, "name": "Client 1", "email": "client1@example.com"},
    {"id": 2, "name": "Client 2", "email": "client2@example.com"},
]

@app.route('/customers', methods=['GET'])
def get_customers():
    return jsonify(customers)

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = next((c for c in customers if c['id'] == id), None)
    if customer:
        return jsonify(customer)
    return jsonify({'message': 'Client non trouvé'}), 404

@app.route('/customers', methods=['POST'])
def create_customer():
    new_customer = request.json
    new_customer['id'] = len(customers) + 1
    customers.append(new_customer)
    return jsonify(new_customer), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = next((c for c in customers if c['id'] == id), None)
    if customer:
        data = request.json
        customer.update(data)
        return jsonify(customer)
    return jsonify({'message': 'Client non trouvé'}), 404

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = next((c for c in customers if c['id'] == id), None)
    if customer:
        customers.remove(customer)
        return jsonify({'message': 'Client supprimé'})
    return jsonify({'message': 'Client non trouvé'}), 404

if __name__ == '__main__':
    app.run(debug=True)
