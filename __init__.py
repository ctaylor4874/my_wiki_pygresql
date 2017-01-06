"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, Markup
from wiki_linkify import wiki_linkify
from jinja2 import Environment, FileSystemLoader
from page import *
import markdown
import sys

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secretkey')

DBUSER = os.environ.get('DBUSER', True)
DBPASS = os.environ.get('DBPASS', True)
DBHOST = os.environ.get('DBHOST', True)
DBNAME = os.environ.get('DBNAME', True)


###
# Routing for my application.
###
@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)\


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


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
    page.username = str(request.form.get('username'))
    page.password = str(request.form.get('password'))
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


app.secret_key = 'secretkey'


@app.route('/<page_name>/edit')
def update_form(page_name):
    page = Page()
    page.title = page_name
    page.page_content = request.form.get('page_content')
    page.update()
    # page_content = M(markdown.markdown(page_content))
    if page.page_content:
        page_content = page.page_content[0]
        wiki_linkify(page_content)
        return edit.render(
            page_title=page.title,
            title=page.title,
            page_content=page_content
        )
    else:
        return edit.render(
            page_title='Edit Page',
            title=page.title
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


# env = Environment(loader=FileSystemLoader('templates'))
# env.filters['wiki_linkify'] = wiki_linkify
# view = env.get_template('view.html')
# edit = env.get_template('edit.html')

if __name__ == "__main__":
    app.run()
