from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import json

app = Flask(__name__)
app.jinja_env.globals.update(enumerate=enumerate) 
app.secret_key = "secretkey"  
QUIZ_FILE = "quizzes.json"
USER_FILE = "users.json" 

def load_quizzes():
    try:
        with open(QUIZ_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}   
    except json.JSONDecodeError:
        return {}

def load_users():
    try:
        with open(USER_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_quizzes(quizzes):
    with open(QUIZ_FILE, 'w') as file:
        json.dump(quizzes, file, indent=4)

def save_users(users):
    with open(USER_FILE, 'w') as file:
        json.dump(users, file, indent=4)

@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        username = request.form["username"]
        users = load_users()
        
        if username in users:
            flash("Username already exists! Please choose a different one.", "warning")
            return redirect(url_for("welcome"))
        
        users[username] = {"username": username, "quizzes_taken": []}
        save_users(users)
        return redirect(url_for("home", username=username))
    
    return render_template("welcome.html")

@app.route("/home/<username>")
def home(username):
    quizzes = load_quizzes()
    return render_template("home.html", quizzes=quizzes, username=username)


@app.route("/quiz/<quiz_title>/<username>", methods=["GET", "POST"])
def take_quiz(quiz_title, username):
    quizzes = load_quizzes()
    if quiz_title not in quizzes:
        return "Quiz not found!", 404

    quiz = quizzes[quiz_title]
    if request.method == "POST":
        score = 0
        for idx, question in enumerate(quiz["questions"]):
            answer = int(request.form.get(f"question_{idx}", 0))
            if answer == question["answer"]:
                score += 1

        users = load_users()
        users[username]["quizzes_taken"].append({"quiz_title": quiz_title, "score": score})
        save_users(users)

        return render_template(
            "result.html",
            score=score,
            total=len(quiz["questions"]),
            username=username,
            quiz_title=quiz_title
        )

    return render_template("quiz.html", quiz=quiz, username=username)

@app.route("/create/<username>", methods=["GET", "POST"])
def create_quiz(username):
    if request.method == "POST":
        title = request.form["title"]
        questions = []
        num_questions = int(request.form["num_questions"])
        for i in range(num_questions):
            question = request.form[f"question_{i}"]
            options = [
                request.form[f"option_{i}_1"],
                request.form[f"option_{i}_2"],
                request.form[f"option_{i}_3"],
                request.form[f"option_{i}_4"]
            ]
            answer = int(request.form[f"answer_{i}"])
            questions.append({"question": question, "options": options, "answer": answer})
        
        quizzes = load_quizzes()
        quizzes[title] = {"title": title, "questions": questions}
        save_quizzes(quizzes)
        
        return redirect(url_for("home", username=username))
    
    return render_template("create.html", username=username)
@app.route("/leaderboard/<quiz_title>/<username>")
def leaderboard(quiz_title, username):
    users = load_users()
    quizzes = load_quizzes()

    if quiz_title not in quizzes:
        return "Quiz not found!", 404

    leaderboard_data = []
    for user, user_data in users.items():
        for quiz in user_data["quizzes_taken"]:
            if quiz["quiz_title"] == quiz_title:
                leaderboard_data.append({"username": user, "score": quiz["score"]})

    leaderboard_data = sorted(leaderboard_data, key=lambda x: x["score"], reverse=True)

    return render_template(
        "leaderboard.html",
        quiz_title=quiz_title,
        leaderboard=leaderboard_data,
        username=username
    )
if __name__ == "__main__":
    app.run(debug=True)
