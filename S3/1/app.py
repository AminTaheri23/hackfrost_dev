from flask import Flask, render_template
import requests
import decouple

CONTACT_FORM_ACTION = decouple.config("CONTACT_FORM_ACTION", default=None)

projects=[]
github_projects_i_want_to_display = []
github_url = "https://api.github.com/users/AminTaheri23/repos?per_page=100"
proj = requests.get(github_url).json()
for repo in proj:
    if repo["name"] not in github_projects_i_want_to_display:
        print("adding github project", repo["name"])
        projects.append(
            {
                "name": repo["name"],
                "description": repo["description"],
                "language": repo["language"],
                "url": repo["html_url"],
                # "image": f"https://picsum.photos/seed/{repo['name']}/800/500",
            }
        )

print(f"total of {len(projects)} projects added")


app = Flask(__name__)
name = "Amin"


@app.route("/")
def about_page():
    return render_template("about.html", Myname=name,)

@app.route("/projects")
def projects_page():
    return render_template("projects.html", projects=projects)

@app.route("/contact")
def contacts_page():
    return render_template("contact.html", api=CONTACT_FORM_ACTION)

if __name__ == "__main__":
    app.run(debug=True)
