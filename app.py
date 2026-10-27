from flask import Flask, render_template, redirect, request, session, url_for
import json
import random
import os
from mail import send_email

app = Flask(__name__)
app.secret_key = 'atm@26_apex_secure_vault'

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def get_data():
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def generate_otp():
    return str(random.randint(100000, 999999))

def get_current_user():
    user_id = session.get('id')
    if not user_id:
        return None
    data = get_data()
    for u in data.get('users', []):
        if u['id'] == user_id:
            return u
    return None

@app.context_processor
def inject_user():
    return {
        'session_user': session.get('username'),
        'is_logged_in': 'id' in session
    }

@app.route('/')
def base():
    if 'id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    info = request.args.get('info')
    if request.method == 'POST':
        acc_num = request.form.get('accnum', '').strip()
        pin = request.form.get('pin', '').strip()
        data = get_data()
        users = data.get("users", [])
        for i in users:
            if i["accnum"] == acc_num and i["pin"] == pin:
                session["username"] = i.get("name") or i.get("username", "Customer")
                session["id"] = i["id"]
                session["accnum"] = i["accnum"]
                return redirect(url_for('dashboard'))
        return redirect(url_for('login', info="Invalid Account Number or PIN"))
    return render_template('login.html', info=info)

@app.route('/confirmemail', methods=['GET', 'POST'])
def confirmemail():
    info = request.args.get('info')
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        data = get_data()
        users = data.get("users", [])
        for i in users:
            if i.get("email", "").lower() == email:
                otp = generate_otp()
                name = i.get("name") or i.get("username", "Customer")
                print(f"\n==========================================")
                print(f"[ATM SECURITY SYSTEM] OTP for {email} ({name}): {otp}")
                print(f"==========================================\n")
                send_email(email, "ATM OTP Verification", f"Hello {name}, your OTP for PIN reset is: {otp}")
                session["otp"] = otp
                session["email"] = email
                session["reset_name"] = name
                return redirect(url_for('verify'))
        return redirect(url_for('confirmemail', info="Email address not found in system"))
    return render_template('confirmemail.html', info=info)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    info = request.args.get('info')
    if 'otp' not in session:
        return redirect(url_for('confirmemail', info="Please request an OTP first"))
    
    # Expose OTP in debug mode for easy testing if mail failed
    otp_hint = session.get('otp')
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        if otp == session.get("otp"):
            session.pop("otp", None)
            return redirect(url_for('setuppin'))
        return redirect(url_for('verify', info="Invalid OTP. Please check and try again."))
    return render_template('verify.html', info=info, otp_hint=otp_hint)

@app.route('/setuppin', methods=['GET', 'POST'])
def setuppin():
    info = request.args.get('info')
    if 'email' not in session:
        return redirect(url_for('confirmemail', info="Session expired, please start over"))

    if request.method == 'POST':
        pin = request.form.get('pin', '').strip()
        cpin = request.form.get('cpin', '').strip()
        
        if not pin or not cpin:
            return redirect(url_for('setuppin', info="Please fill in both PIN fields"))
        
        if len(pin) < 4:
            return redirect(url_for('setuppin', info="PIN should be at least 4 digits"))

        if pin == cpin:
            data = get_data()
            users = data.get("users", [])
            for i in users:
                if i.get("email", "").lower() == session.get("email", "").lower():
                    session.pop("email", None)
                    session.pop("reset_name", None)
                    i["pin"] = pin
                    save_data(data)
                    return redirect(url_for('login', info="PIN updated successfully! Please login with your new PIN."))
            return redirect(url_for('setuppin', info="User account could not be found"))
        return redirect(url_for('setuppin', info="PINs do not match. Please try again."))
    return render_template('setuppin.html', info=info)

@app.route('/dashboard')
def dashboard():
    if 'id' not in session:
        return redirect(url_for('login', info="Please login to continue"))
    user = get_current_user()
    if not user:
        session.clear()
        return redirect(url_for('login', info="User not found. Please login again."))
    return render_template('dashboard.html', user=user)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'id' not in session:
        return redirect(url_for('login', info="Please login to continue"))

    user = get_current_user()
    if not user:
        return redirect(url_for('login', info="User not found"))

    info = request.args.get('info')
    if request.method == 'POST':
        amount_raw = request.form.get('amount', '').strip()
        try:
            amount = int(amount_raw)
        except ValueError:
            return redirect(url_for('deposit', info="Please enter a valid numeric amount"))

        if amount <= 0:
            return redirect(url_for('deposit', info="Amount must be greater than zero"))
        
        data = get_data()
        for i in data.get("users", []):
            if i["id"] == session["id"]:
                i["balance"] += amount
                if "History" not in i:
                    i["History"] = []
                i["History"].insert(0, f"{amount} - Deposited")
                save_data(data)
                return redirect(url_for('checkbalance', info=f"Successfully deposited ₹{amount:,}!"))
    return render_template('deposit.html', info=info, balance=user.get('balance', 0), user=user)

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'id' not in session:
        return redirect(url_for('login', info="Please login to continue"))

    user = get_current_user()
    if not user:
        return redirect(url_for('login', info="User not found"))

    info = request.args.get('info')
    if request.method == 'POST':
        amount_raw = request.form.get('amount', '').strip()
        try:
            amount = int(amount_raw)
        except ValueError:
            return redirect(url_for('withdraw', info="Please enter a valid numeric amount"))

        if amount <= 0:
            return redirect(url_for('withdraw', info="Amount must be greater than zero"))

        data = get_data()
        for i in data.get("users", []):
            if i["id"] == session["id"]:
                if amount <= i["balance"]:
                    i["balance"] -= amount
                    if "History" not in i:
                        i["History"] = []
                    i["History"].insert(0, f"{amount} - Withdrawn")
                    save_data(data)
                    return redirect(url_for('checkbalance', info=f"Successfully withdrawn ₹{amount:,}!"))
                else:
                    return redirect(url_for('withdraw', info="Insufficient balance for this transaction"))
    return render_template('withdraw.html', info=info, balance=user.get('balance', 0), user=user)

@app.route('/transactions')
def transactions():
    if "id" not in session:
        return redirect(url_for('login', info="Please login to continue"))
    user = get_current_user()
    if not user:
        return redirect(url_for('login', info="User not found"))
    
    history_list = user.get("History", [])
    return render_template('transactions.html', history=history_list, History=history_list, user=user)

@app.route('/checkbalance')
def checkbalance():
    if "id" not in session:
        return redirect(url_for('login', info="Please login to continue"))
    user = get_current_user()
    if not user:
        return redirect(url_for('login', info="User not found"))
    info = request.args.get('info')
    return render_template('checkbalance.html', balance=user.get('balance', 0), user=user, info=info)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login', info="You have logged out safely. Thank you for using Apex ATM."))

if __name__ == '__main__':
    app.run(debug=True, port=5000)