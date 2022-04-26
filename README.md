# URL
URL=http://127.0.0.1:5000
URL=https://book-library-123.uc.r.appspot.com

# Web-based analytics dashboard
URL=http://127.0.0.1:5000/dashboard

# Resize image
curl -X POST -H "Content-Type:multipart/form-data" -F "file=@cover1.png" -F "isbn=9781501124020"  -F "author=Ray Dalio" -F "language=English" -F "pages=592" -F "title=Principles" -F "year=2017" http://127.0.0.1:5000/books 

