import os,json
from flask import Flask, request, jsonify, render_template
from google.cloud import storage
from google.cloud import datastore
import logging

app = Flask(__name__)   
CLOUD_STORAGE_BUCKET = "book-library-123" 

@app.route("/")
def homepage():
    return "Hello Book Library!"

@app.errorhandler(404)
def page_not_found(e):
    return "Book not found.", 404


def get_add_book(dataclient, entity):
    entity['query_times'] += 1
    dataclient.put(entity)

def query_sort(e):
    return e['query_times']

@app.route("/dashboard")
def dashboard():
    datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
    query = datastore_client.query(kind='Books-image')
    books_entities = list(query.fetch())
    books_entities.sort(key=query_sort, reverse=True)
    return render_template('dashboard.html', books_entities=books_entities)

@app.route("/books")
def books():
    try:
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        query = datastore_client.query(kind='Books-image')
        books_entities = list(query.fetch())
        author = request.args.get('author')
        language = request.args.get('language')
        title = request.args.get('title')

        json_array = []
        for book in books_entities:
            if author and author not in book['author']:
                continue
            if language and language not in book['language']:
                continue
            if title and title not in book['title']:
                continue
            obj = {}
            obj['title'] = book['title']
            obj['author'] = book['author']
            obj['language'] = book['language']
            obj['isbn'] = book['isbn']
            obj['pages'] = int(book['pages'])
            obj['year'] = int(book['year'])
            obj['image'] = str(book['image'])
            get_add_book(datastore_client, book)
            json_array.append(obj)
        
        return jsonify(json_array), 200
    except Exception as e:
        logging.error(e)
        return str(e), 400

@app.route("/books/<isbn>")
def getbook(isbn):
    try:
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        query = datastore_client.query(kind='Books-image')
        if len(isbn) != 13:
            logging.warning(str(isbn) + ' is invalid')
            return 'invalid isbn', 406
        query.add_filter("isbn", "=", str(isbn))
        books_entities = list(query.fetch())
        if len(books_entities) == 0:
            logging.warning(str(isbn) + 'book not found')
            return "Book not found.", 404
        book = books_entities[0]
        obj = {}
        obj['title'] = book['title']
        obj['author'] = book['author']
        obj['language'] = book['language']
        obj['isbn'] = book['isbn']
        obj['pages'] = int(book['pages'])
        obj['year'] = int(book['year'])
        obj['image'] = str(book['image'])
        get_add_book(datastore_client, book)
        return jsonify(obj), 200
      
    except Exception as e:
        logging.error(e)
        return str(e), 400


@app.route("/books/<isbn>", methods=['PUT'])
def putbook(isbn):
    try:
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        query = datastore_client.query(kind='Books-image', )

        if len(isbn) != 13:
            logging.warning(str(isbn) + ' is invalid')
            return 'invalid isbn', 406
        
        query.add_filter("isbn", "=", str(isbn))
        books_entities = list(query.fetch())
        if len(books_entities) == 0:
            logging.warning(str(isbn) + 'book not found')
            return "Book not found.", 404
        
        isbn = str(isbn)
        book = books_entities[0]
        print(request.form['title'], 'author' in request.form)

        key = datastore_client.key('Books-image', isbn)

    
        entity = datastore.Entity(key)
        entity['isbn'] = isbn
        entity['title'] = str(request.form['title']) if 'title' in request.form else book['title']
        entity['author'] = str(request.form['author']) if 'author' in request.form else book['author']
        entity['language'] = str(request.form['language']) if 'language' in request.form else book['language']
        entity['pages'] = int(request.form['pages']) if 'pages' in request.form else book['pages']
        entity['year'] = int(request.form['year']) if 'year' in request.form else book['year']
        entity['image'] = book['image']
        entity['query_times'] = book['query_times']
        datastore_client.put(entity)
        return "Book updated successfully.", 200
      
    except Exception as e:
        logging.error(e)
        return str(e), 400

@app.route("/books/<isbn>", methods=['DELETE'])
def delbook(isbn):
    try:
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        isbn = str(isbn)
        logging.info('deleting book with isbn: ' + isbn)

        key = datastore_client.key('Books-image', isbn)
        datastore_client.delete(key)
        return "Book delete successfully.", 204
      
    except Exception as e:
        logging.error(e)
        return str(e), 400

def dealPost(request, isbn=None):
    try:
        if not isbn:
            isbn = str(request.form['isbn'])
        title = str(request.form['title'])
        author = str(request.form['author'])
        language = str(request.form['language'])
        pages = int(request.form['pages'])
        year = int(request.form['year'])
        image = request.files['file']
        
        if len(isbn) != 13:
            logging.warning(str(isbn) + ' is invalid')
            return 'invalid isbn', 406
        
        blob = None
        if image:
            
            storage_client = storage.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')

            bucket_name = CLOUD_STORAGE_BUCKET
            bucket = storage_client.bucket(bucket_name)
            bucket_thumbnail = storage_client.bucket(bucket_name)

            blob = bucket.blob(image.filename)
            blob.upload_from_string(image.read(), content_type=image.content_type)
            print(f"File uploaded: {image.filename} to {blob.public_url}")
            logging.info(f"File uploaded: {image.filename} to {blob.public_url}")
        
        datastore_client = datastore.Client.from_service_account_json('book-library-123-93f0c01b7c20.json')
        kind = 'Books-image'
        name = isbn
        key = datastore_client.key(kind, name)

        entity = datastore.Entity(key)
        entity['isbn'] = isbn
        entity['title'] = title
        entity['author'] = author
        entity['language'] = language
        entity['pages'] = int(pages)
        entity['year'] = int(year)
        entity['image'] = ""
        entity['query_times'] = 0
        if blob:
            entity['image'] = blob.public_url
        datastore_client.put(entity)
    
        return str(isbn) + 'save successully', 201
    except Exception as e:
        logging.error(e)
        return str(e), 400
    
@app.route("/books/<int:isbn>", methods=['POST'])
def upload(isbn):
    return dealPost(request, str(isbn))

@app.route("/books", methods=['POST'])
def uploadwithoutisbn():
    return dealPost(request)


if __name__ == '__main__':
    app.run(debug=True)