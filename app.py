from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "collegebot123"

# ---------------- LOGIN DATA ----------------
students = {"rasmi": "1234"}
admins = {"admin": "admin123"}


# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS placements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        package TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS department_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        user_message TEXT,
        bot_response TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_data():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    # Clear old data
    cursor.execute("DELETE FROM placements")
    cursor.execute("DELETE FROM department_details")

    # Insert placements
    companies = [
        ("TCS", "4 LPA"),
        ("Infosys", "5 LPA"),
        ("Wipro", "4.5 LPA"),
        ("Cognizant", "5 LPA"),
        ("HCL", "4 LPA"),
        ("Accenture", "6 LPA"),
        ("Capgemini", "5 LPA"),
        ("Zoho", "8 LPA"),
        ("Amazon", "18 LPA"),
        ("Google", "25 LPA"),
        ("Microsoft", "22 LPA"),
        ("IBM", "6 LPA"),
        ("Tech Mahindra", "4 LPA"),
        ("Oracle", "12 LPA"),
        ("Deloitte", "7 LPA"),
        ("HP", "6 LPA"),
        ("PayPal", "15 LPA"),
        ("Flipkart", "14 LPA"),
        ("Byjus", "10 LPA"),
        ("L&T", "5 LPA")
    ]
    cursor.executemany("INSERT INTO placements (company, package) VALUES (?, ?)", companies)

    # Insert department details
    details = [
        ("Department", "The Department of AI & DS focuses on AI, ML, Data Science and emerging technologies."),
        ("Symposium", "We the department of AI&DS conducted a national level technical and non technical symposium . This was a grant sucess meting that held in our clg on october 20 , 2025 . we had 4 technical and 4 non technical games . and over 60 students from other clg participated in our dept symposium"),
        ("Association", "AI & DS Association conducts seminars, guest lectures, hackathons and technical events."),
        ("Industrial Visit", "Regular industrial visits to reputed IT companies for real-world exposure.")
    ]
    cursor.executemany("INSERT INTO department_details (title, description) VALUES (?, ?)", details)

    conn.commit()
    conn.close()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        if role == "student" and username in students and students[username] == password:
            session["user"] = username
            return redirect("/chat")

        elif role == "admin" and username in admins and admins[username] == password:
            session["user"] = username
            return redirect("/chat")

        else:
            return "Invalid Credentials"

    return render_template("login.html")


# ---------------- CHAT ----------------
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user" not in session:
        return redirect("/")

    response = ""

    if request.method == "POST":
        message = request.form["message"].lower()

        # Placement
        if "placement" in message:
            conn = sqlite3.connect("college.db")
            cursor = conn.cursor()
            cursor.execute("SELECT company, package FROM placements")
            data = cursor.fetchall()
            conn.close()

            response = "📌 Placement Details:\n"
            for company, package in data:
                response += f"{company} - {package}\n"

        # Department Related
        elif any(word in message for word in ["department", "symposium", "association", "industrial"]):
            conn = sqlite3.connect("college.db")
            cursor = conn.cursor()

            if "department" in message:
                cursor.execute("SELECT description FROM department_details WHERE title='Department'")
            elif "symposium" in message:
                cursor.execute("SELECT description FROM department_details WHERE title='Symposium'")
            elif "association" in message:
                cursor.execute("SELECT description FROM department_details WHERE title='Association'")
            elif "industrial" in message:
                cursor.execute("SELECT description FROM department_details WHERE title='Industrial Visit'")

            result = cursor.fetchone()
            conn.close()

            if result:
                response = result[0]
            else:
                response = "No details found."

        # Simple Replies
        elif "exam" in message:
            response = "Students must score above 70 marks. Improvement test will be conducted in the evening."

        elif "bye" in message:
            response = "Thank you for using the chatbot. Bye 😊"

        else:
            response = "Please ask about placement, department, symposium, association or industrial visit."

        # Save chat history
        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (username, user_message, bot_response) VALUES (?, ?, ?)",
            (session["user"], message, response)
        )
        conn.commit()
        conn.close()

    # Fetch history
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, bot_response FROM chat_history WHERE username=?", (session["user"],))
    history = cursor.fetchall()
    conn.close()

    return render_template("chatbot.html", name=session["user"], history=history)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    init_db()
    insert_data()
    app.run(debug=True)
