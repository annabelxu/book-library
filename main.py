import logging
import os,json
from flask import Flask, request, jsonify
from google.cloud import storage
from google.cloud import datastore

app = Flask(__name__)   
CLOUD_STORAGE_BUCKET = "book-library-123" 

@app.route("/")
def homepage():
    return "Hello Book Library!"

@app.errorhandler(404)
def page_not_found(e):
    return "Book not found.", 404

@app.route("/books")
def books():
    try:
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        query = datastore_client.query(kind='Books')
        books_entities = list(query.fetch())
        author = request.args.get('author')
        language = request.args.get('language')

        json_array = []
        logging.info(len(books_entities), author, language=="")
        for book in books_entities:
            if author and author != book['author']:
                continue
            if language and language != book['language']:
                continue
            obj = {}
            obj['title'] = book['title']
            obj['author'] = book['author']
            obj['language'] = book['language']
            obj['isbn'] = book['isbn']
            obj['pages'] = str(book['pages'])
            obj['year'] = str(book['year'])
            json_array.append(obj)
        
        return jsonify(json_array), 200
    except Exception as e:
        return str(e), 400

@app.route("/books/<isbn>")
def getbook(isbn):
    try:
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        query = datastore_client.query(kind='Books', )
        query.add_filter("isbn", "=", str(isbn))
        books_entities = list(query.fetch())
        if len(books_entities) == 0:
            return "Book not found.", 404
        book = books_entities[0]
        obj = {}
        obj['title'] = book['title']
        obj['author'] = book['author']
        obj['language'] = book['language']
        obj['isbn'] = book['isbn']
        obj['pages'] = str(book['pages'])
        obj['year'] = str(book['year'])
        return jsonify(obj), 200
      
    except Exception as e:
        return str(e), 400


@app.route("/books/<isbn>", methods=['PUT'])
def putbook(isbn):
    try:
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        query = datastore_client.query(kind='Books', )
        query.add_filter("isbn", "=", str(isbn))
        books_entities = list(query.fetch())
        if len(books_entities) == 0:
            return "Book not found.", 404
        
        isbn = str(isbn)
        book = books_entities[0]
        print(request.form['title'], 'author' in request.form)

        key = datastore_client.key('Books', isbn)

        # Create a Datastore entity
        entity = datastore.Entity(key)
        entity['isbn'] = isbn
        entity['title'] = str(request.form['title']) if 'title' in request.form else book['title']
        entity['author'] = str(request.form['author']) if 'author' in request.form else book['author']
        entity['language'] = str(request.form['language']) if 'language' in request.form else book['language']
        entity['pages'] = str(request.form['pages']) if 'pages' in request.form else book['pages']
        entity['year'] = str(request.form['year']) if 'year' in request.form else book['year']
        datastore_client.put(entity)
        return "Book updated successfully.", 200
      
    except Exception as e:
        return str(e), 400

@app.route("/books/<isbn>", methods=['DELETE'])
def delbook(isbn):
    try:
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        isbn = str(isbn)

        key = datastore_client.key('Books', isbn)
        datastore_client.delete(key)
        return "Book delete successfully.", 204
      
    except Exception as e:
        return str(e), 400

def dealPost(request, isbn=None):
    try:
        if not isbn:
            isbn = str(request.form['isbn'])
        title = str(request.form['title'])
        author = str(request.form['author'])
        language = str(request.form['language'])
        pages = str(request.form['pages'])
        year = str(request.form['year'])
        
        if len(isbn) != 13:
            return 'invalid isbn', 406
        
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        kind = 'Books'
        # name/id for the new entity
        name = isbn
        # Create the cloud datastore key for the new entity
        key = datastore_client.key(kind, name)

        entity = datastore.Entity(key)
        entity['isbn'] = isbn
        entity['title'] = title
        entity['author'] = author
        entity['language'] = language
        entity['pages'] = int(pages)
        entity['year'] = int(year)
        datastore_client.put(entity)
    
        return str(isbn) + 'save successully', 201
    except Exception as e:
        return str(e), 400
    
@app.route("/books/<int:isbn>", methods=['POST'])
def upload(isbn):
    return dealPost(request, str(isbn))

# isbn=978-0-596-520&title=test&author=test&language=test&pages=123&year=1987
@app.route("/books", methods=['POST'])
def uploadwithoutisbn():
    return dealPost(request)


if __name__ == '__main__':
    app.run(debug=True)