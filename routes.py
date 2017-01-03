from flask import Flask, render_template, request, redirect
from wiki_linkify import wiki_linkify
from jinja2 import Environment, FileSystemLoader
from page import *
import markdown
from flask import Markup
from flask import Flask, session

app = Flask('mywiki')


@app.route("/")
def home():
    homeContent = Page.getObjects()
    titlesDict = {}
    for item in homeContent:
        titlesDict[item[0]] = [item[0]]
        titlesDict[item[0]].append(item[1])
        titlesDict[item[0]].append(item[2])
    return render_template(
        'wiki_home.html',
        title='Wiki',
        titlesDict=titlesDict
    )


@app.route('/<page_name>')
def placeholder(page_name):
    page = Page()
    page.title = page_name
    exists = page.placeHolder()

    if exists:
        page.page_content = Markup(markdown.markdown(page.page_content))
        return view.render(
            page_title=page.title,
            title=page.title,
            page_content=page.page_content,
            last_modified_date=page.last_modified_date,
            author_last_modified=page.author_last_modified,
        )
    else:
        return render_template('placeholder.html', title=page.title)


@app.route('/logout')
def logout():
    session.clear()
    return render_template(
        'logout.html'
    )


@app.route('/<page_name>/login_page', methods=['POST', 'GET'])
def login_page(page_name):
    page = Page()
    page.title = page_name
    if session:
        return redirect('/%s/edit' % page.title)
    else:
        return render_template(
            "login.html",
            page_title=page.title,
            title=page.title
        )


@app.route('/<page_name>/login', methods=['POST', 'GET'])
def login(page_name):
    page = Page()
    page.title = page_name
    page.username = request.form.get('username')
    page.password = request.form.get('password')
    result_dict = page.login()
    if len(result_dict):
        if result_dict['password'] == page.password:
            session['username'] = result_dict['username']
            return redirect('/%s/edit' % page.title)
    else:
        return render_template(
            "login.html",
            page_title=page.title,
            title=page.title
        )


app.secret_key = 'hello there'


@app.route('/<page_name>/edit')
def update_form(page_name):
    page = Page()
    page.title = page_name
    page.page_content = request.form.get('page_content')
    page.update()
    if page.page_content:
        return render_template(
            "edit.html",
            page_title=page.title,
            title=page.title,
            page_content=page.page_content,
        )
    else:
        return render_template(
            'edit.html',
            page_title='Edit Page',
            title=page.title,
        )


@app.route('/<page_name>/save', methods=['POST', 'GET'])
def save(page_name):
    page = Page()
    page.id = request.form.get('id')
    page.title = page_name
    page.page_content = request.form.get('page_content')
    page.author_last_modified = request.form.get('author_last_modified')
    page.pageid = page.id
    page.save()
    page.page_content = Markup(markdown.markdown(page.page_content))
    return view.render(
        title=page.title,
        page_content=page.page_content,
        last_modified_date=page.last_modified_date,
        author_last_modified=page.author_last_modified)


@app.route('/<page_name>/archives')
def archives(page_name):
    list = Page.getArchives(page_name)
    return render_template(
        "archives.html", title_list=list, title=page_name)


@app.route('/<page_name>/archives/<revisionid>')
def archiveView(page_name, revisionid):
    title = page_name
    archiveContent = Page.archiveContent(revisionid)
    page_content = archiveContent.get('page_content', None)
    author_last_modified = archiveContent.get('author_last_modified', None)
    last_modified_date = archiveContent.get('last_modified_date', None)
    page_content = Markup(markdown.markdown(page_content))
    return view.render(
        title=title,
        page_content=page_content,
        author_last_modified=author_last_modified,
        last_modified_date=last_modified_date
    )


# conn = Database.getConnection()
# cur = conn.cursor()
env = Environment(loader=FileSystemLoader('templates'))
env.filters['wiki_linkify'] = wiki_linkify
view = env.get_template('view.html')
# cur.close()
# conn.close()

if __name__ == "__main__":
    app.run(debug=True)
# cur.close()
#
# conn.close()
