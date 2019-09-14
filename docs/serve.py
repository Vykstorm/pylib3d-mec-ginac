'''
Author: Víctor Ruiz Gómez
Description: This script creates a small Flask application to serve the documentation of this library
rendered in html files by sphinx.
'''

from flask import Flask

app = Flask(__name__, static_url_path='/', static_folder='_build/html/')

@app.route('/docs/')
@app.route('/docs/<path:path>')
def serve_sphinx_docs(path='index.html'):
    return app.send_static_file(path)
