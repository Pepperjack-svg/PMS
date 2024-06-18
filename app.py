from flask import Flask, render_template, request, redirect, url_for, session, flash
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace 'your_secret_key' with your actual secret key

def read_users():
    try:
        with open('users.txt', 'r') as file:
            lines = file.readlines()
            users = [line.strip().split(':') for line in lines]
            return {username: (password, email) for username, password, email in users}
    except FileNotFoundError:
        return {}

def write_user(username, password, email):
    with open('users.txt', 'a') as file:
        file.write(f'{username}:{password}:{email}\n')

class User:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class Reservation:
    def __init__(self, username, space_number, start_time, end_time):
        self.username = username
        self.space_number = space_number
        self.start_time = start_time
        self.end_time = end_time

def read_reservations():
    try:
        with open('reservations.txt', 'r') as file:
            lines = file.readlines()
            reservations = [line.strip().split(':') for line in lines]
            return [Reservation(username, space_number, start_time, end_time) for username, space_number, start_time, end_time in reservations]
    except FileNotFoundError:
        return []

def write_reservation(username, space_number, start_time, end_time):
    with open('reservations.txt', 'a') as file:
        file.write(f'{username}:{space_number}:{start_time}:{end_time}\n')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username_or_email = request.form['username_or_email']
    password = request.form['password']

    users = read_users()

    # Check if the entered value is a username
    if username_or_email in users and sha256_crypt.verify(password, users[username_or_email][0]):
        session['user_id'] = username_or_email
        flash('Login successful', 'success')
        return redirect(url_for('dashboard'))
    else:
        # If not a username, check if it's an email
        for username, (hashed_password, email) in users.items():
            if email == username_or_email and sha256_crypt.verify(password, hashed_password):
                session['user_id'] = username
                flash('Login successful', 'success')
                return redirect(url_for('dashboard'))

    flash('Invalid username or password', 'danger')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']

        users = read_users()

        if username in users:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        hashed_password = sha256_crypt.hash(password)
        write_user(username, hashed_password, email)

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    users = read_users()
    user = User(username=user_id, password=users[user_id][0], email=users[user_id][1])

    reservations = read_reservations()

    return render_template('dashboard.html', user=user, reservations=reservations)

@app.route('/reserve', methods=['POST'])
def reserve():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    space_number = request.form['space_number']
    start_time = request.form['start_time']
    end_time = request.form['end_time']

    # Add your dynamic pricing logic here based on start_time and end_time
    # For simplicity, let's assume a basic pricing calculation.
    # You may want to adjust this based on your specific pricing strategy.
    # The example below just calculates the difference in hours and charges $5 per hour.
    price = 5 * (int(end_time) - int(start_time))

    write_reservation(user_id, space_number, start_time, end_time)
    flash(f'Reservation for Parking Space {space_number} successful! Total Price: ${price}', 'success')

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=25570)
