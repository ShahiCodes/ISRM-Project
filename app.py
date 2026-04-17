from flask import Flask, request, render_template_string, redirect, make_response
import sqlite3
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# VULNERABILITY: No Logging implemented for security events

# --- Database Setup (Runs on startup) ---
def init_db():
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    
    # Drop existing tables to refresh the schema if you've run this before
    c.execute('''DROP TABLE IF EXISTS users''')
    c.execute('''DROP TABLE IF EXISTS students''')
    
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, major TEXT, grades TEXT)''')
    
    # VULNERABILITY: Sensitive Data Exposure (Plaintext Passwords)
    users_data = [
        (1, 'admin', 'SuperSecretAdmin99!', 'admin'),
        (2, 'jdoe', 'password123', 'student'),
        (3, 'asmith', 'qwerty', 'student'),
        (4, 'mwilson', 'ilovecats', 'student'),
        (5, 'bwayne', 'batman', 'student')
    ]
    c.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users_data)
    
    # Expanded Academic Data
    students_data = [
        (1, 'John Doe', 'jdoe@university.edu', '555-0101', 'Computer Science', 'CS101: A, MATH201: B+'),
        (2, 'Alice Smith', 'asmith@university.edu', '555-0102', 'Information Technology', 'IT105: A, ENG101: A-'),
        (3, 'Michael Wilson', 'mwilson@university.edu', '555-0103', 'Cybersecurity', 'SEC300: B, CS101: C+'),
        (4, 'Bruce Wayne', 'bwayne@university.edu', '555-0104', 'Business', 'BUS101: A, FIN202: A'),
        (5, 'Clark Kent', 'ckent@university.edu', '555-0105', 'Journalism', 'JRN101: A, ENG101: B'),
        (6, 'Diana Prince', 'dprince@university.edu', '555-0106', 'History', 'HIS200: A, ANTH101: A'),
        (7, 'Barry Allen', 'ballen@university.edu', '555-0107', 'Physics', 'PHY101: B+, MATH201: A-'),
        (8, 'Victor Stone', 'vstone@university.edu', '555-0108', 'Robotics', 'CS101: A, EE201: A'),
        (9, 'Arthur Curry', 'acurry@university.edu', '555-0109', 'Marine Biology', 'BIO101: C, OCN201: B'),
        (10, 'Hal Jordan', 'hjordan@university.edu', '555-0110', 'Aviation', 'AER101: A, PHY101: C+')
    ]
    c.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", students_data)
    
    conn.commit()
    conn.close()

init_db()


LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>University Portal - Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-200 h-screen flex items-center justify-center font-sans">
    <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-gray-700">
        <div class="text-center mb-8">
            <h2 class="text-3xl font-extrabold text-white tracking-tight">University Portal</h2>
            <p class="text-sm text-gray-400 mt-2">Sign in to your account</p>
        </div>
        <form method="POST" action="/" class="space-y-6">
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Username</label>
                <input type="text" name="username" class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition" placeholder="Enter your username" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Password</label>
                <input type="password" name="password" class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition" placeholder="••••••••" required>
            </div>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-4 rounded-lg shadow-lg transition duration-200 ease-in-out transform hover:-translate-y-0.5">
                Sign In
            </button>
        </form>
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-200 min-h-screen p-8 font-sans">
    <div class="max-w-5xl mx-auto space-y-8">
        
        <header class="flex justify-between items-center bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div>
                <h1 class="text-2xl font-bold text-white">Dashboard</h1>
                <p class="text-gray-400">Current Session Role: <span class="px-2 py-1 bg-blue-900 text-blue-200 text-xs font-bold rounded ml-2 uppercase">{{ role }}</span></p>
            </div>
            <a href="/" class="text-sm bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded shadow transition">Logout</a>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
                <h3 class="text-lg font-semibold text-white mb-4 border-b border-gray-700 pb-2">Search Student Records</h3>
                <form method="GET" action="/search" class="flex space-x-3 mb-4">
                    <input type="text" name="query" class="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Search by name...">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition">Search</button>
                </form>
                
                <div class="bg-gray-900 p-4 rounded-lg min-h-[100px] border border-gray-700 overflow-x-auto text-sm font-mono text-green-400">
                    {{ search_results | safe if search_results else "No queries executed." }}
                </div>
            </div>

            <div class="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
                <h3 class="text-lg font-semibold text-white mb-4 border-b border-gray-700 pb-2">Submit Assignment</h3>
                <form method="POST" action="/upload" enctype="multipart/form-data" class="space-y-4">
                    <div class="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center hover:border-blue-500 transition cursor-pointer bg-gray-700">
                        <input type="file" name="file" class="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer">
                    </div>
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-500 text-white font-semibold py-2 px-4 rounded-lg transition">Upload File</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
'''

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # VULNERABILITY: SQL Injection in Authentication
        conn = sqlite3.connect('university.db')
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        c.execute(query)
        user = c.fetchone()
        conn.close()
        
        if user:
            resp = make_response(redirect('/dashboard'))
            # VULNERABILITY: Business Logic Flaw / Privilege Escalation
            # Trusting client-side cookie for role authorization
            resp.set_cookie('role', user[3]) 
            return resp
        else:
            return "Login Failed"
            
    return render_template_string(LOGIN_HTML)

@app.route('/dashboard')
def dashboard():
    role = request.cookies.get('role', 'guest')
    return render_template_string(DASHBOARD_HTML, role=role)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    
    # VULNERABILITY: SQL Injection in Data Collection
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    sql_query = f"SELECT * FROM students WHERE name LIKE '%{query}%'"
    
    try:
        c.execute(sql_query)
        results = c.fetchall()
    except sqlite3.Error as e:
        results = str(e) # Information Disclosure
    finally:
        conn.close()
        
    role = request.cookies.get('role', 'guest')
    return render_template_string(DASHBOARD_HTML, role=role, search_results=results)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
        
    # VULNERABILITY: Insecure File Upload (No extension validation, saving to local dir)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return f"File {file.filename} uploaded successfully!"

@app.route('/api/v1/students', methods=['GET'])
def get_students_api():
    """API Endpoint to fetch all student data. Fulfills project requirement."""
    # VULNERABILITY: Broken Access Control / Information Disclosure
    # This API does not check if the user is authenticated at all!
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    data = c.fetchall()
    conn.close()
    
    # Format as JSON
    result = [{"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "major": row[4], "grades": row[5]} for row in data]
    return app.response_class(
        response=json.dumps(result, indent=4),
        status=200,
        mimetype='application/json'
    )

@app.route('/admin/users')
def admin_panel():
    """A restricted panel only meant for administrators."""
    role = request.cookies.get('role', 'guest')
    
    # Check if the user has escalated privileges
    if role != 'admin':
        return "403 Forbidden: You do not have administrative access.", 403
        
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()
    conn.close()
    
    # Quick inline HTML for the admin panel
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-red-900 text-white p-8">
        <h1 class="text-3xl font-bold mb-4">CONFIDENTIAL: Admin Control Panel</h1>
        <p class="mb-6">Warning: Authorized Personnel Only.</p>
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-red-800"><th class="p-2 border border-red-700">ID</th><th class="p-2 border border-red-700">Username</th><th class="p-2 border border-red-700">Role</th></tr>
            </thead>
            <tbody>
                {"".join([f"<tr><td class='p-2 border border-red-700'>{u[0]}</td><td class='p-2 border border-red-700'>{u[1]}</td><td class='p-2 border border-red-700'>{u[2]}</td></tr>" for u in users])}
            </tbody>
        </table>
        <a href="/dashboard" class="mt-6 inline-block bg-white text-red-900 px-4 py-2 rounded font-bold">Back to Dashboard</a>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)