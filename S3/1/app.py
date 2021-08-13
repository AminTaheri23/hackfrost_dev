from flask import Flask, render_template
from datetime import datetime
import requests
import decouple
import os
from pathlib import Path
import markdown
import sqlite3
import sys

sys.path.append("S3/1/blog")

db_connection = sqlite3.connect("./database.db")
db_cursor = db_connection.cursor()
# db_cursor.execute(
#     """
# CREATE TABLE FOODS (
#     name TEXT,
#     PRIMARY KEY (name)
# );
# """)
CONTACT_FORM_ACTION = decouple.config("CONTACT_FORM_ACTION", default=None)

blog_posts = []
projects=[]
# github_projects_i_want_to_display = []
# github_url = "https://api.github.com/users/AminTaheri23/repos?per_page=100"
# proj = requests.get(github_url).json()
# for repo in proj:
#     if repo["name"] not in github_projects_i_want_to_display:
#         # print("adding github project", repo["name"])
#         projects.append(
#             {
#                 "name": repo["name"],
#                 "description": repo["description"],
#                 "language": repo["language"],
#                 "url": repo["html_url"],
#                 # "image": f"https://picsum.photos/seed/{repo['name']}/800/500",
#             }
#         )

# print(f"total of {len(projects)} projects added")


app = Flask(__name__)
name = "Amin"

for f in sorted(os.listdir('blog')): print(f)

with os.scandir("blog") as it:
    for entry in it:
        if entry.name.endswith(".md") and entry.is_file:
            raw_post_date, post_name = entry.name.split("_")
            post_name = post_name.rstrip(".md")

            date = datetime.strptime(raw_post_date, "%Y-%m-%d")
            html = markdown.markdown(Path(entry.path).read_text())

            blog_posts.append({
                "name" : post_name,
                "date" : date,
                "html" : html
            })
@app.route("/")
def about_page():
    return render_template("about.html", Myname=name,)

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
            return render_template("blog_entry.html", name=name, post = post)
    
    return "Blog post not found"

if __name__ == "__main__":
    app.run(debug=True)
