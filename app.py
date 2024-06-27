from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from fraud_detection import detect_fraud, generate_random_transactions
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/')
def login_page():
    graph_path = 'static/graph.png'
    if os.path.exists(graph_path):
        os.remove(graph_path)
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'bankadmin' and password == 'bankadmin':
        return redirect(url_for('index'))
    else:
        flash('Invalid username or password. Please try again.')
        return redirect(url_for('login_page'))


@app.route('/index')
def index():
    # Remove existing graph image if it exists
    graph_path = 'static/graph.png'
    if os.path.exists(graph_path):
        os.remove(graph_path)
    return render_template('index.html')


@app.route('/transaction_details', methods=['POST'])
def transaction_details():
    num_transactions = int(request.form['num_transactions'])
    transaction_data = generate_random_transactions(num_transactions)
    return render_template('transaction_details.html', num_transactions=num_transactions, transactions=transaction_data)


@app.route('/results', methods=['POST'])
def results():
    num_transactions = int(request.form['num_transactions'])
    transaction_data = []
    for i in range(num_transactions):
        source = request.form[f'source{i}']
        target = request.form[f'target{i}']
        amount = int(request.form[f'amount{i}'])
        timestamp = request.form[f'timestamp{i}']
        account_age = int(request.form[f'account_age{i}'])
        balance = int(request.form[f'balance{i}'])
        transaction_data.append((source, target, amount, timestamp, account_age, balance))

    fraudulent_transactions, fraud_reason = detect_fraud(transaction_data)
    frauds_with_reasons = zip(fraudulent_transactions, fraud_reason)
    return render_template('results.html', transactions=transaction_data, frauds_with_reasons=frauds_with_reasons)


@app.route('/graph')
def graph():
    return send_file('static/graph.png', mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
