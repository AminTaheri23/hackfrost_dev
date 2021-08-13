import sys
import os

from flask import Flask, render_template
from datetime import datetime
import requests
import decouple
from pathlib import Path
import markdown
import sqlite3

# sys.path.append("S3/1/blog")

db_connection = sqlite3.connect("./database.db")
db_cursor = db_connection.cursor()
# db_cursor.execute(
#     """
# CREATE TABLE FOODS (
#     name TEXT,
#     PRIMARY KEY (name)
# );
# """)
db_cursor.close()
db_connection.commit()

CONTACT_FORM_ACTION = decouple.config("CONTACT_FORM_ACTION", default=None)
blog_posts = []
projects = []
github_projects_i_want_to_display = []
github_url = "https://api.github.com/users/AminTaheri23/repos?per_page=100"
proj = requests.get(github_url).json()
for repo in proj:
    if repo["name"] not in github_projects_i_want_to_display:
        projects.append(
            {
                "name": repo["name"],
                "description": repo["description"],
                "language": repo["language"],
                "url": repo["html_url"],
                # "image": f"https://picsum.photos/seed/{repo['name']}/800/500",
            }
        )

app = Flask(__name__)
name = "Amin"

# SCAN blog folder
with os.scandir("blog") as it:
    for entry in it:
        if entry.name.endswith(".md") and entry.is_file:
            raw_post_date, post_name = entry.name.split("_")
            post_name = post_name.rstrip(".md")

            date = datetime.strptime(raw_post_date, "%Y-%m-%d")
            html = markdown.markdown(Path(entry.path).read_text())

            blog_posts.append({
                "name": post_name,
                "date": date,
                "html": html
            })


def date_returner_dict(ict):
    """This function will get a dict and return the 'date' values

    Args:
        ict (dict): a dict to find 'date'

    Returns:
        datetim object: the date time object in the 'date' 
    """
    return ict["date"]


# Sort the blog posts based on time (reversed)
blog_posts.sort(key=date_returner_dict, reverse=True)

# Routes


@app.route("/")
def about_page():
    db_cursor = sqlite3.connect("./database.db").cursor()
    db_cursor.execute('SELECT * from FOODS;')
    list_of_food = db_cursor.fetchall()
    return render_template("about.html", Myname=name, list_of_food=list_of_food)


@app.route("/projects")
def projects_page():
    return render_template("projects.html", projects=projects)


@app.route("/contact")
def contacts_page():
    return render_template("contact.html", api=CONTACT_FORM_ACTION)


@app.route("/blog")
def blog_listing_page():
    return render_template("blog_listing.html", blog_p=blog_posts)


@app.route("/blog/<postname>")
def blog_entry_page(postname):
    for post in blog_posts:
        if postname == post["name"]:
            return render_template("blog_entry.html", name=name, post=post)

    return "Blog post not found"


if __name__ == "__main__":
    app.run(debug=True)
