from flask import Flask, request, render_template_string, redirect, make_response, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import logging
import json

app = Flask(__name__)
# VULNERABILITY FIXED: Cryptographic key added for secure session signing
app.secret_key = os.urandom(24) 
app.config['UPLOAD_FOLDER'] = 'uploads/'

# VULNERABILITY FIXED: Whitelist for file uploads
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}

# VULNERABILITY FIXED: Security logging implemented
logging.basicConfig(filename='security.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Secure Database Setup (Expanded) ---
def init_db():
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, major TEXT, grades TEXT)''')
    
    # Clear tables just in case to avoid primary key conflicts during testing
    c.execute('DELETE FROM users')
    c.execute('DELETE FROM students')
    
    # All users share the same securely hashed password for easy testing: 'password123'
    # EXCEPT the admin, whose password is: 'SuperSecretAdmin99!'
    admin_hash = generate_password_hash('SuperSecretAdmin99!')
    student_hash = generate_password_hash('password123')
    
    # Expanded Users Table (1 Admin, 9 Students)
    users_data = [
        (1, 'admin', admin_hash, 'admin'),
        (2, 'jdoe', student_hash, 'student'),
        (3, 'harshit', student_hash, 'student'),
        (4, 'asmith', student_hash, 'student'),
        (5, 'bwayne', student_hash, 'student'),
        (6, 'ckent', student_hash, 'student'),
        (7, 'dprince', student_hash, 'student'),
        (8, 'pparker', student_hash, 'student'),
        (9, 'tstark', student_hash, 'student'),
        (10, 'nromanoff', student_hash, 'student')
    ]
    c.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users_data)
    
    # Expanded Students Table (15 Records with diverse realistic data)
    students_data = [
        (1, 'John Doe', 'jdoe@university.edu', '555-0101', 'Computer Science', 'CS101: A, MATH201: B+'),
        (2, 'Alice Smith', 'asmith@university.edu', '555-0102', 'Information Technology', 'IT105: A, ENG101: A-'),
        (3, 'Harshit', 'harshit@university.edu', '555-0103', 'Information Technology', 'ISRM301: A, ML401: A, LinuxSys: B+'),
        (4, 'Bruce Wayne', 'bwayne@university.edu', '555-0104', 'Business Analytics', 'BUS101: A, FIN202: A'),
        (5, 'Clark Kent', 'ckent@university.edu', '555-0105', 'Journalism', 'JRN101: A, ENG101: B'),
        (6, 'Diana Prince', 'dprince@university.edu', '555-0106', 'History', 'HIS200: A, ANTH101: A'),
        (7, 'Peter Parker', 'pparker@university.edu', '555-0107', 'Physics', 'PHY101: A+, MATH201: A'),
        (8, 'Tony Stark', 'tstark@university.edu', '555-0108', 'Robotics & Automation', 'CS101: A+, EE201: A+'),
        (9, 'Natasha Romanoff', 'nromanoff@university.edu', '555-0109', 'Cybersecurity', 'SEC300: A, CRYPT101: A'),
        (10, 'Barry Allen', 'ballen@university.edu', '555-0110', 'Forensic Science', 'FOR201: B+, SEC300: A-'),
        (11, 'Victor Stone', 'vstone@university.edu', '555-0111', 'System-level Programming', 'OS201: A, NET301: A'),
        (12, 'Arthur Curry', 'acurry@university.edu', '555-0112', 'Marine Biology', 'BIO101: C, OCN201: B'),
        (13, 'Hal Jordan', 'hjordan@university.edu', '555-0113', 'Aviation', 'AER101: A, PHY101: C+'),
        (14, 'Wanda Maximoff', 'wmaximoff@university.edu', '555-0114', 'Quantum Computing', 'QC401: A, MATH301: B'),
        (15, 'Stephen Strange', 'sstrange@university.edu', '555-0115', 'Medical Science', 'MED501: A, BIO202: A-')
    ]
    c.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", students_data)
    
    conn.commit()
    conn.close()

init_db()

# --- Upgraded HTML Templates (Same as Phase 2) ---
LOGIN_HTML = '''<!DOCTYPE html><html lang="en"><head><title>University Portal</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gray-900 text-gray-200 h-screen flex items-center justify-center font-sans"><div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-gray-700"><h2 class="text-3xl font-extrabold text-white text-center mb-6">University Portal</h2><form method="POST" action="/" class="space-y-6"><div><label class="block text-sm font-medium mb-2">Username</label><input type="text" name="username" class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500" required></div><div><label class="block text-sm font-medium mb-2">Password</label><input type="password" name="password" class="w-full px-4 py-3 bg-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500" required></div><button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 rounded-lg">Sign In</button></form></div></body></html>'''

DASHBOARD_HTML = '''<!DOCTYPE html><html lang="en"><head><title>Dashboard</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gray-900 text-gray-200 min-h-screen p-8"><div class="max-w-5xl mx-auto space-y-8"><header class="flex justify-between items-center bg-gray-800 p-6 rounded-xl border border-gray-700"><h1 class="text-2xl font-bold text-white">Dashboard <span class="text-sm bg-blue-900 px-2 py-1 rounded ml-2">{{ role }}</span></h1><a href="/logout" class="bg-red-600 px-4 py-2 rounded text-white text-sm">Logout</a></header><div class="grid grid-cols-1 md:grid-cols-2 gap-8"><div class="bg-gray-800 p-6 rounded-xl border border-gray-700"><h3 class="text-lg font-semibold mb-4">Search Records</h3><form method="GET" action="/search" class="flex space-x-3 mb-4"><input type="text" name="query" class="flex-1 px-4 py-2 bg-gray-700 rounded-lg" placeholder="Search by name..."><button type="submit" class="bg-blue-600 px-4 py-2 rounded-lg">Search</button></form><div class="bg-gray-900 p-4 rounded-lg font-mono text-sm text-green-400 min-h-[100px]">{{ search_results | safe if search_results else "No queries." }}</div></div><div class="bg-gray-800 p-6 rounded-xl border border-gray-700"><h3 class="text-lg font-semibold mb-4">Submit Assignment</h3><form method="POST" action="/upload" enctype="multipart/form-data" class="space-y-4"><input type="file" name="file" class="w-full text-sm text-gray-400 bg-gray-700 p-2 rounded"><button type="submit" class="w-full bg-green-600 py-2 rounded-lg text-white">Upload</button></form></div></div></div></body></html>'''

# --- Secure Routes ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # VULNERABILITY FIXED: Parameterized Query prevents SQLi
        conn = sqlite3.connect('university.db')
        c = conn.cursor()
        c.execute("SELECT id, password, role FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        
        # VULNERABILITY FIXED: Verifying the cryptographic hash
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['role'] = user[2]
            logging.info(f"Successful login for user: {username}")
            return redirect('/dashboard')
        else:
            logging.warning(f"Failed login attempt for username: {username}")
            return "Login Failed. Invalid credentials."
            
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template_string(DASHBOARD_HTML, role=session.get('role'))

@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect('/')
        
    query = request.args.get('query', '')
    
    # VULNERABILITY FIXED: Parameterized Query using wildcards safely
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + query + '%',))
    results = c.fetchall()
    conn.close()
        
    return render_template_string(DASHBOARD_HTML, role=session.get('role'), search_results=results)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect('/')
        
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    
    # VULNERABILITY FIXED: Strict file extension validation and secure filename formatting
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        logging.info(f"User {session['user_id']} successfully uploaded {filename}")
        return f"File {filename} uploaded securely!"
    else:
        logging.warning(f"User {session['user_id']} attempted invalid file upload: {file.filename}")
        return "Upload rejected: Invalid file type."

@app.route('/api/v1/students', methods=['GET'])
def get_students_api():
    # VULNERABILITY FIXED: Added Authentication and Authorization checks
    if 'user_id' not in session or session.get('role') != 'admin':
        logging.warning(f"Unauthorized API access attempt by user ID: {session.get('user_id')}")
        abort(403)
        
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    data = c.fetchall()
    conn.close()
    
    result = [{"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "major": row[4], "grades": row[5]} for row in data]
    return app.response_class(response=json.dumps(result, indent=4), status=200, mimetype='application/json')

@app.route('/admin/users')
def admin_panel():
    if 'user_id' not in session:
        return redirect('/')
        
    if session.get('role') != 'admin':
        logging.warning(f"User {session['user_id']} attempted unauthorized admin panel access.")
        return "403 Forbidden: You do not have administrative access.", 403
        
    logging.info(f"Admin (User ID: {session['user_id']}) accessed the user control panel.")
    # (HTML omitted for brevity, logic is identical to before)
    return "Welcome to the Secure Admin Panel."

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)