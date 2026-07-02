import sqlite3
import requests
from flask import Flask, render_template, request, redirect, session, url_for
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv("/home/shaikrafi04/CineVerse/.env")
app = Flask(__name__)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
conn = sqlite3.connect("movie.db", check_same_thread=False)

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    movie TEXT,
    review TEXT
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS wishlist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_name TEXT,
    movie_image TEXT,
    movie_rating TEXT
)
""")
conn.commit()
app.secret_key = "movieapp"
wishlist = []
reviews = []


@app.route("/tmdb_test")
def tmdb_test():

    movie = "RRR"

    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie}"

    response = requests.get(url)

    return response.json()

from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

@app.route("/ai", methods=["GET", "POST"])
def ai():

    answer = ""

    if request.method == "POST":

        prompt = request.form["prompt"]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content

    return render_template(
        "ai.html",
        answer=answer
    )



@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def user_login():

    email = request.form["email"]
    password = request.form["password"]

    cursor.execute(
        "INSERT INTO users(email,password) VALUES(?,?)",
        (email, password)
    )

    conn.commit()

    session["user"] = email

    return redirect("/home")


@app.route("/home")
def home():

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_original_language=te&sort_by=popularity.desc"

    response = requests.get(url)

    data = response.json()

    movies = data["results"][:6]

    return render_template(
        "index.html",
        session=session,
        movies=movies
    )
    


@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")

@app.route("/movies")
def movies_page():

    search = request.args.get("search", "")

    if search:

        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={search}&language=te-IN"

    else:

        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_original_language=te&sort_by=popularity.desc"

    response = requests.get(url)

    data = response.json()

    movies = data["results"]

    return render_template(
        "movies.html",
        movies=movies
    )

@app.route("/add_review", methods=["POST"])
def add_review():

    username = request.form["username"]
    movie = request.form["movie"]
    review = request.form["review"]
    cursor.execute(
    "INSERT INTO reviews(username,movie,review) VALUES(?,?,?)",
    (username, movie, review)
    )
    conn.commit()

    return redirect("/reviews")

@app.route("/reviews")
def reviews_page():

    cursor.execute("SELECT * FROM reviews")

    all_reviews = cursor.fetchall()

    return render_template(
        "reviews.html",
        reviews=all_reviews
    )
@app.route("/test")
def test():

    cursor.execute("SELECT * FROM reviews")

    return str(cursor.fetchall())

@app.route("/delete_review/<int:index>")
def delete_review(index):

    reviews.pop(index)

    return redirect("/reviews")


@app.route("/add_wishlist/<movie_name>/<movie_image>/<movie_rating>")
def add_wishlist(movie_name, movie_image, movie_rating):

    print(movie_name)
    print(movie_image)
    print(movie_rating)

    cursor.execute(
        "INSERT INTO wishlist(movie_name, movie_image, movie_rating) VALUES (?, ?, ?)",
        (movie_name, movie_image, movie_rating)
    )

    conn.commit()

    return redirect("/wishlist")


@app.route("/wishlist")
def wishlist_page():

    cursor.execute("SELECT * FROM wishlist")

    wishlist = cursor.fetchall()

    return render_template(
        "wishlist.html",
        wishlist=wishlist
    )


@app.route("/remove_wishlist/<int:id>")
def remove_wishlist(id):

    cursor.execute(
        "DELETE FROM wishlist WHERE id=?",
        (id,)
    )

    conn.commit()

    return redirect("/wishlist")

@app.route("/trending")
def trending():
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_original_language=te&sort_by=popularity.desc"

    response = requests.get(url)
    data = response.json()

    movies = data["results"]

    return render_template(
        "trending.html",
        movies=movies
    )
if __name__ == "__main__":
    app.run(debug=True)