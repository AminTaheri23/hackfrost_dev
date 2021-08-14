from flask import send_from_directory
import sys
import os

from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from datetime import datetime, timedelta
import requests
import decouple
from pathlib import Path
import markdown
import sqlite3
from werkzeug.utils import secure_filename
from functools import wraps
import urllib

UPLOAD_FOLDER = 'blog'
ALLOWED_EXTENSIONS = {'md'}
DATABASE_PATH = "example-portfolio.db"
CONTACT_FORM_ACTION = decouple.config("CONTACT_FORM_ACTION", default=None)
REACTIONS = ["💖️"]

db_connection = sqlite3.connect(DATABASE_PATH)
db_cursor = db_connection.cursor()
db_cursor.execute(
    """
CREATE TABLE IF NOT EXISTS post_reaction (
    post_slug TEXT,
    value TEXT NOT NULL,
    amount INTEGER NOT NULL,
    PRIMARY KEY (post_slug, value)
)
"""
)
db_cursor.close()
db_connection.commit()


CONTACT_FORM_ACTION = decouple.config("CONTACT_FORM_ACTION", default=None)

app = Flask(__name__)
name = "S. M. Amin Taheri G."

app.secret_key = 'sleepy dude'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# login required decorator


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


def date_returner_dict(ict):
    """This function will get a dict and return the 'date' values

    Args:
        ict (dict): a dict to find 'date'

    Returns:
        datetim object: the date time object in the 'date' 
    """
    if "date" in ict.keys():
        return ict["date"]

    if "updated_at" in ict.keys():
        return ict["updated_at"]


blog_posts = []
blog_slug_to_post = {}
with os.scandir("blog") as it:
    for entry in it:
        if entry.name.endswith(".md") and entry.is_file:
            raw_post_date, post_name = entry.name.split("_")
            post_name = post_name.rstrip(".md")

            date = datetime.strptime(raw_post_date, "%Y-%m-%d")
            html = markdown.markdown(Path(entry.path).read_text())

            slug = "".join(filter(str.isalnum, post_name))
            slug = urllib.parse.quote_plus(slug).lower()

            for reaction in REACTIONS:
                db_connection = sqlite3.connect(DATABASE_PATH)
                db_cursor = db_connection.cursor()
                db_cursor.execute(
                    "SELECT * FROM post_reaction WHERE post_slug = :slug AND value = :value",
                    {"slug": slug, "value": reaction},
                )
                results = db_cursor.fetchall()

                if len(results) == 0:
                    print(
                        f"creating post_reaction row for blog post '{post_name}' for reaction '{reaction}'"
                    )
                    db_cursor.execute(
                        """
                        INSERT INTO post_reaction (
                            post_slug,
                            value,
                            amount
                        ) VALUES (
                            :post_slug,
                            :value,
                            :amount
                        )
                        """,
                        {"post_slug": slug, "value": reaction, "amount": 0},
                    )

                db_cursor.close()

            db_connection.commit()
            post = {
                "name": html.split(">")[1][:-4],
                "date": date,
                "html": html,
                "slug": slug,
            }
            blog_posts.append(post)
            blog_slug_to_post[slug] = post

            print(f"total of {len(blog_posts)} blog posts added")

# Sort the blog posts based on time (reversed)
blog_posts.sort(key=date_returner_dict, reverse=True)

# Routes


@app.route("/")
def about_page():
    return render_template("about.html", Myname=name)


# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # I know this is pretty basic, I'll make it better in the future.
        if request.form['username'] != 'smat' or request.form['password'] != 'hackfrost':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('admin'))
    return render_template('login.html', error=error, Myname=name)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('about_page'))


@app.route("/projects")
def projects_page():
    projects = []
    github_projects_i_want_to_display = []
    github_url = "https://api.github.com/users/AminTaheri23/repos?per_page=1000"
    proj = requests.get(github_url).json()
    for repo in proj:
        date, _ = repo["updated_at"].split('T')
        today = datetime.now()
        # projects that have been updated in the last 6 months
        DD = timedelta(days=180)
        earlier = today - DD
        if datetime.strptime(date, "%Y-%m-%d").date() > earlier.date():
            if repo["name"] not in github_projects_i_want_to_display and repo["owner"]["login"] == "AminTaheri23":
                projects.append(
                    {
                        "name": repo["name"],
                        "description": repo["description"],
                        "language": repo["language"],
                        "url": repo["html_url"],
                        "updated_at": repo["updated_at"]
                    }
                )

    projects.sort(key=date_returner_dict, reverse=True)
    return render_template("projects.html", Myname=name, projects=projects)


@app.route("/contact")
def contacts_page():
    return render_template("contact.html", Myname=name, api=CONTACT_FORM_ACTION)


@app.route("/blog/<slug>")
def blog_post_route(slug):
    post = blog_slug_to_post.get(slug)

    if post is None:
        abort(404, description="Post not found")

    db_cursor = sqlite3.connect(DATABASE_PATH).cursor()
    db_cursor.execute(
        "SELECT value, amount FROM post_reaction WHERE post_slug = :slug",
        {"slug": slug},
    )
    results = db_cursor.fetchall()

    return render_template("blog_entry.html", Myname=name, post=post, reactions=results)


@app.route("/api/react/<slug>/<value>")
def api_react(slug, value):
    if value not in REACTIONS:
        abort(400, description="Invalid value")

    post_exists = slug in blog_slug_to_post.keys()

    if not post_exists:
        abort(404, description="Post not found")

    db_connection = sqlite3.connect(DATABASE_PATH)
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        "UPDATE post_reaction SET amount = amount + 1 WHERE post_slug = :slug AND value = :value",
        {"slug": slug, "value": value},
    )
    db_connection.commit()

    return '', 204

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            if filename.endswith(".md"):
                raw_post_date, post_name = filename.split("_")
                post_name = post_name.rstrip(".md")

                date = datetime.strptime(raw_post_date, "%Y-%m-%d")
                html = markdown.markdown(Path(file_path).read_text())

                slug = "".join(filter(str.isalnum, post_name))
                slug = urllib.parse.quote_plus(slug).lower()
                for reaction in REACTIONS:
                    db_connection = sqlite3.connect(DATABASE_PATH)
                    db_cursor = db_connection.cursor()
                    db_cursor.execute(
                        "SELECT * FROM post_reaction WHERE post_slug = :slug AND value = :value",
                        {"slug": slug, "value": reaction},
                    )
                    results = db_cursor.fetchall()

                    if len(results) == 0:
                        print(
                            f"creating post_reaction row for blog post '{post_name}' for reaction '{reaction}'"
                        )
                        db_cursor.execute(
                            """
                            INSERT INTO post_reaction (
                                post_slug,
                                value,
                                amount
                            ) VALUES (
                                :post_slug,
                                :value,
                                :amount
                            )
                            """,
                            {"post_slug": slug, "value": reaction, "amount": 0},
                        )

                    db_cursor.close()

                db_connection.commit()
                post = {
                    "name": html.split(">")[1][:-4],
                    "date": date,
                    "html": html,
                    "slug": slug,
                }
                blog_posts.append(post)
                blog_slug_to_post[slug] = post

                blog_posts.sort(key=date_returner_dict, reverse=True)

            return redirect(url_for('uploaded_file', filename=filename))
    return render_template("admin.html", Myname=name)


@app.route('/admin/<filename>')
@login_required
def uploaded_file(filename):
    flash(f"File {filename} has succefuly uploaded")
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/blog")
def blog_listing_page():
    return render_template("blog_listing.html", Myname=name, blog_p=blog_posts)


if __name__ == "__main__":
    app.run(debug=True)
