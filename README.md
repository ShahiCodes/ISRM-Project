# 🔐 Cyber Attack Simulation on Student Management System

## 📌 Overview

This project simulates a full-scale cyber attack on a student management system, highlighting critical vulnerabilities across core application features. The goal is to demonstrate how attackers exploit weaknesses to compromise systems, escalate privileges, and exfiltrate sensitive data.

---

## ⚙️ Core Application Features (Attack Surface)

* **User Authentication**

  * Login system supporting student and administrator accounts.

* **Role-Based Access Control (RBAC)**

  * Different dashboards and permissions based on user roles.

* **Student Record Search**

  * API endpoint for querying academic data from the backend database.

* **Assignment Submission Module**

  * File upload system for student coursework submissions.

---

## 🎯 Attack Goal

The primary objective of this simulated cyber attack is:

* Bypass authentication mechanisms
* Escalate privileges to administrator level
* Extract sensitive academic data
* Disrupt system availability
* Evade detection mechanisms

---

# 🔐 Web Application Security Demonstration (Step-by-Step)

## 1. Initial Access: Credential Stuffing & SQLi Bypass

**Vulnerability:** Weak Authentication / SQL Injection
**Goal:** Gain entry without knowing a valid password

### Steps to Demonstrate:

1. Open your browser and navigate to:

   ```
   http://127.0.0.1:5000
   ```

2. **Credential Stuffing Demo:**

   * Username: `jdoe`
   * Password: `password123`
   * Click **Sign In**

3. **SQL Injection Bypass (Flashier Demo):**

   * Log out first.

   * In the password field, enter:

     ```
     ' OR '1'='1
     ```

   * username: `123` (or anything)

   * Click **Sign In**

### Result:

The SQL query evaluates to true, allowing login without valid credentials.

---

## 2. Privilege Escalation: Business Logic Flaw

**Vulnerability:** Insecure Session Management / Privilege Escalation
**Goal:** Upgrade from a student account to an admin account

### Steps to Demonstrate:

1. Log in as a student (e.g., `jdoe`).

2. Observe the role displayed as `student` on the dashboard.

3. Try accessing:

   ```
   http://127.0.0.1:5000/admin/users
   ```

   → You will receive a **403 Forbidden** error.

4. Open Developer Tools:

   * Press `F12`
   * Go to **Application** (Chrome/Edge) or **Storage** (Firefox)

5. Navigate to:

   ```
   Cookies → http://127.0.0.1:5000
   ```

6. Locate the cookie:

   ```
   role = student
   ```

7. Modify it:

   ```
   student → admin
   ```

8. Refresh the page or revisit:

   ```
   http://127.0.0.1:5000/admin/users
   ```

### Result:

You now have full access to the Admin Control Panel.

---

## 3. Execution: Insecure File Upload

**Vulnerability:** Unrestricted File Upload
**Goal:** Upload an executable script instead of a document

### Steps to Demonstrate:

1. Open a new terminal tab.

2. Create a malicious Python file:

   ```bash
   echo "print('System Compromised!')" > malware.py
   ```

3. Go to the Flask dashboard in your browser.

4. In the **Submit Assignment** section:

   * Click **Choose File**
   * Select `malware.py`

5. Click **Upload File**

### Result:

The server accepts the malicious file without validation.
Check the `uploads/` folder to confirm.

---

## 4. Collection & Exfiltration: Advanced SQL Injection

**Vulnerability:** SQL Injection / Sensitive Data Exposure
**Goal:** Extract usernames and passwords from the database

### Steps to Demonstrate:

1. Locate the **Search Student Records** feature.

2. Test normal search:

   ```
   John
   ```

3. Inject the following payload:

   ```sql
   ' UNION SELECT id, username, password, role, 'N/A', 'N/A' FROM users --
   ```

4. Click **Search**

### Result:

The application returns the entire users table, exposing sensitive credentials (e.g., `SuperSecretAdmin99!`).

---

## 5. Impact: Denial of Service (DoS - Login Flooding)

**Vulnerability:** Lack of Rate Limiting
**Goal:** Overwhelm the server to block legitimate users

### Steps to Demonstrate:

1. Open a new terminal tab.

2. Run the following command:

   ```bash
   while true; do curl -s -X POST http://127.0.0.1:5000/ -d "username=admin&password=123" > /dev/null & done
   ```

3. Observe the Flask server terminal.

4. Try accessing the application in a browser.

### Result:

* Server becomes slow or unresponsive
* Massive flood of POST requests observed

⚠️ **Important:**
Press `Ctrl + C` to stop the attack before crashing your system.

---

## ✅ Summary of Vulnerabilities

| Stage                | Vulnerability    | Impact                |
| -------------------- | ---------------- | --------------------- |
| Initial Access       | SQL Injection    | Authentication bypass |
| Privilege Escalation | Insecure Cookies | Admin access          |
| Execution            | File Upload      | Remote code execution |
| Exfiltration         | SQL Injection    | Data breach           |
| Impact               | No Rate Limiting | Denial of Service     |

---

## 📊 Attack Flow & Vulnerability Mapping

| MITRE Stage          | Technique         | Vulnerability           | Attack Vector           | CVSS Score | Importance | Stage Risk | Why It Matters                        |
| -------------------- | ----------------- | ----------------------- | ----------------------- | ---------- | ---------- | ---------- | ------------------------------------- |
| Initial Access       | Valid Accounts    | Credential Stuffing     | Authentication Module   | 7.5        | 4          | 30.0       | Entry point enabling the attack chain |
| Execution            | Command Injection | Insecure File Upload    | Assignment Submission   | 9.8        | 5          | 49.0       | Allows arbitrary code execution       |
| Privilege Escalation | Role Manipulation | Business Logic Flaw     | RBAC / Session Cookies  | 8.8        | 4          | 35.2       | Grants full admin control             |
| Defense Evasion      | Indicator Removal | No Logging              | Application Logic       | 5.0        | 3          | 15.0       | Prevents detection and tracking       |
| Collection           | Data Access       | SQL Injection           | Student Search Endpoint | 9.8        | 4          | 39.2       | Extracts entire backend database      |
| Exfiltration         | Data Transfer     | Sensitive Data Exposure | Web Shell Outbound      | 6.5        | 5          | 32.5       | Leads to data breach                  |
| Impact               | Endpoint DoS      | Login Flooding          | Authentication Module   | 5.3        | 3          | 15.9       | Disrupts system availability          |

---

## 🚨 Key Takeaways

* Multiple vulnerabilities can chain into a **full system compromise**
* Lack of **input validation, logging, and access control** are critical weaknesses
* Defense-in-depth is essential to prevent multi-stage attacks
* Monitoring and logging are as important as prevention

---

## Bandit Report and CVSS Score:
- **SQL Injection (9.8 - Critical)**: Network attack vector, low complexity, no privileges required, and high impact on confidentiality, integrity, and availability.

- **Insecure File Upload (9.8 - Critical)**: Allows remote code execution. Network vector, low complexity, no privileges required.

- **Privilege Escalation (8.8 - High)**: Requires basic student authentication first (Low Privileges Required), but leads to a total system compromise.

- **Sensitive Data Exposure (7.5 - High)**: Plaintext passwords in the database. Network vector, requires no privileges, high impact on confidentiality.

- **No Logging (5.0 - Medium)**: Does not directly compromise the system, but completely removes traceability
