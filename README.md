#Library Online Management System written in Django
---

####Link: https://django-library.herokuapp.com/

**Technologies**: django, python, html, css, less, Java Script, jQuery, Twitter Bootstrap, Git, Heroku, Selenium,
django_tables2, fandjango

**Date**: December, 2014

>It is an online interface for a library (with a few social-network features) and allows users to:
- borrow/return books
- create circles of friends
- share with friends books' quotation, borrowed books
- register/sign in via facebook and webpage
- save quotations from books

>There is also group of librarians with additional permissions:
- custom (outside of django admin) CRUD for authors, books' publishers, books etc.
- librarian can mark that book has been returned to library

Front-end is designed using Twitter Bootstrap and filled out with
sample data (mostly lorem ipsum). A few animations/effects are programmed using jQuery.

For facebook integration I used facepy and fandjango.

Application is provided with test (basic ones, unittests and selenium).

I intended to document every fragment of code that could be unclear. Enclosed is documentation
created by sphinx.

**Run**: 
```sh 
python manage.py runserver 127.0.0.1:8888
```

or simply visit website: http://library-django.heroku.com/

**Author: Tomasz Potanski, tomasz@potanski.pl**