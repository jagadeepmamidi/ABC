import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from web3 import Web3
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a real secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress warning
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Ensure Ganache is running
blockchain_url = "http://127.0.0.1:7545"  # Ensure this matches your Ganache or node setup
web3 = Web3(Web3.HTTPProvider(blockchain_url))

# Check if connected to blockchain
if not web3.is_connected():
    raise Exception("Cannot connect to the blockchain. Please check Ganache is running.")

contract_address = "0x336Ac6455AcDA2c5f6e8C3fd795573c860655447"  # Replace with your deployed contract address

compiled_contract_path = os.path.join(os.path.dirname(__file__), "../build/contracts/HealthcarePlatform.json")
if not os.path.exists(compiled_contract_path):
    raise Exception("Compiled contract file not found. Please ensure it exists.")

with open(compiled_contract_path, "r") as file:
    audit_contract_json = json.load(file)
    audit_contract_abi = audit_contract_json["abi"]

contract = web3.eth.contract(address=contract_address, abi=audit_contract_abi)

# Set default account
web3.eth.default_account = web3.eth.accounts[0]

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    ethereum_address = db.Column(db.String(42), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ethereum_address = request.form.get('ethereum_address')
        
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 400
        
        user = User(username=username, ethereum_address=ethereum_address)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({"message": "User registered successfully"}), 201
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({"message": "Logged in successfully"}), 200
        return jsonify({"message": "Invalid username or password"}), 401
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Testing blockchain connection
@app.route('/test_blockchain')
def test_blockchain():
    if web3.is_connected():
        return jsonify({"message": "Connected to the blockchain!"}), 200
    else:
        return jsonify({"message": "Blockchain connection failed."}), 500


# Test storing health records
@app.route('/test_store_record', methods=['GET'])
@login_required
def test_store_record_page():
    return render_template('test_store_record.html')


# Test retrieving health records
@app.route('/test_get_records')
@login_required
def test_get_records():
    try:
        records = contract.functions.getHealthRecords().call({'from': current_user.ethereum_address})
        return jsonify({"records": records}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Test granting access
@app.route('/test_grant_access', methods=['POST'])
@login_required
def test_grant_access():
    try:
        to_address = request.form.get('to_address')
        tx_hash = contract.functions.grantAccess(to_address).transact({'from': current_user.ethereum_address})
        return jsonify({"message": "Access granted", "transaction": tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Test revoking access
@app.route('/test_revoke_access', methods=['POST'])
@login_required
def test_revoke_access():
    try:
        to_address = request.form.get('to_address')
        tx_hash = contract.functions.revokeAccess(to_address).transact({'from': current_user.ethereum_address})
        return jsonify({"message": "Access revoked", "transaction": tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Test rewarding a user with tokens
@app.route('/test_reward_user', methods=['POST'])
@login_required
def test_reward_user():
    try:
        user_address = request.form.get('user_address')
        amount = int(request.form.get('amount'))
        tx_hash = contract.functions.rewardUser(user_address, amount).transact({'from': web3.eth.accounts[0]})
        return jsonify({"message": "User rewarded", "transaction": tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
