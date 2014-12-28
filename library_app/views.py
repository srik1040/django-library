from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.template.base import add_to_builtins
from .forms import AuthenticateForm, UserCreateForm, UserEditForm, AuthorForm
from .models import Book, LendPeriods, QuotationFromBook, Author, Publisher
from .tables import BookTable, FriendTable, BookTableUser, AuthorTable, PublisherTable, PeriodsTable
from django.http import Http404
import django_tables2 as tables
from django_tables2 import RequestConfig
from django.http import HttpRequest
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .decorators.group_required import group_required


add_to_builtins('library_app.templatetags.xextends')
add_to_builtins('library_app.templatetags.has_group')


def home(request):
    # is_authenticated = request.user.is_authenticated()
    if request.user.is_authenticated():
        user = request.user
        return render(request, 'home.html', {'user': user})
    else:
        return render(request, 'public_home.html', {})


def about(request):
    return render(request, 'about.html', {})


def sign_in(request, auth_form=None):
    if request.user.is_authenticated():
        redirect('/')
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/')
        else:
            auth_form = auth_form or AuthenticateForm()
            return render(request, 'sign_in.html', {'auth_form': auth_form})
    auth_form = AuthenticateForm()
    return render(request, 'sign_in.html', {'auth_form': auth_form})


def sign_up(request, user_form=None):
    if request.method == 'POST':
        user_form = UserCreateForm(data=request.POST)
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return sign_up(request, user_form=user_form)
    user_form = UserCreateForm()
    return render(request, 'sign_up.html', {'user_form': user_form})


    # if request.method == 'POST':
    # form = AuthenticateForm(data=request.POST)
    # if form.is_valid():
    # login(request, form.get_user())
    # return redirect('/')
    # else:
    # return sign_in(request, auth_form=form)
    # return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required(login_url='/sign_in/')
def periods(request):
    periods_qs = LendPeriods.objects.all()
    return_dict = {}
    if request.method == 'POST':
        if request.POST['search'] and request.POST['keyword']:
            found_periods = LendPeriods.objects.filter(
                name__contains=request.POST['keyword'])

            periods_qs = found_periods
            return_dict['last_phrase'] = request.POST['keyword']

    periods_table = PeriodsTable(periods_qs)
    RequestConfig(request, paginate={"per_page": 5}).configure(periods_table)
    return_dict['periods_table'] = periods_table
    return render(request, 'periods.html', return_dict)


@group_required("Librarians")
def authors(request):
    authors_qs = Author.objects.all()
    return_dict = {}
    if request.method == 'POST':
        if request.POST['search'] and request.POST['keyword']:
            found_authors = Author.objects.filter(
                name__contains=request.POST['keyword']) | Author.objects.filter(
                surname__contains=request.POST['keyword'])

            authors_qs = found_authors
            return_dict['last_phrase'] = request.POST['keyword']

    authors_table = AuthorTable(authors_qs)
    RequestConfig(request, paginate={"per_page": 5}).configure(authors_table)
    return_dict['authors_table'] = authors_table
    return render(request, 'authors.html', return_dict)


@group_required("Librarians")
def publishers(request):
    publishers_qs = Publisher.objects.all()
    return_dict = {}
    if request.method == 'POST':
        if request.POST['search'] and request.POST['keyword']:
            found_publishers = Publisher.objects.filter(name__contains=request.POST['keyword'])

            publishers_qs = found_publishers
            return_dict['last_phrase'] = request.POST['keyword']

    publishers_table = PublisherTable(publishers_qs)
    RequestConfig(request, paginate={"per_page": 5}).configure(publishers_table)
    return_dict['publishers_table'] = publishers_table
    return render(request, 'publishers.html', return_dict)


@login_required(login_url='/sign_in/')
def books(request):
    books_qs = Book.objects.all()
    return_dict = {}
    if request.method == 'POST':
        if request.POST['search'] and request.POST['title_keyword'] and request.POST['where']:
            if request.POST['where'] == 'title':
                found_books = Book.objects.filter(title__contains=request.POST['title_keyword'])
            elif request.POST['where'] == 'author':
                found_books = Book.objects.filter(
                    author__name__contains=request.POST['title_keyword']) | Book.objects.filter(
                    author__surname__contains=request.POST['title_keyword'])
            else:  # searching in publishers
                found_books = Book.objects.filter(publisher__name__contains=request.POST['title_keyword'])

            # print request.POST
            # print request.POST.getlist('only_available')
            if request.POST.get('only_available', False):
                found_books = found_books.filter(lend_by__isnull=True)
            books_qs = found_books
            return_dict['last_phrase'] = request.POST['title_keyword']
            return_dict['last_where'] = request.POST['where']

    books_table = BookTable(books_qs)
    RequestConfig(request, paginate={"per_page": 5}).configure(books_table)
    return_dict['books_table'] = books_table
    return render(request, 'books.html', return_dict)


@login_required(login_url='/sign_in/')
def books_show(request, book_id):
    book = Book.objects.filter(id=book_id)[0]
    if book:
        pbu = "false"

        # print book.lend_by
        # print request.user.profile
        if request.method == 'POST':
            if request.POST.get('quotation', False):
                new_quote = QuotationFromBook(user=request.user, book=book, quotation=request.POST['quotation'],
                                              creation_date=timezone.now())
                new_quote.save()
                messages.success(request, 'New quotation has been successfully saved!')

        if book.lend_by == request.user.profile:
            pbu = "true"
        return render(request, 'book_show.html',
                      {'book': book,
                       'pbu': pbu})
    else:
        return redirect('/books/')


@login_required(login_url='/sign_in/')
def authors_show(request, author_id):
    author = Author.objects.get(id=author_id)
    if author:
        books_qs = Book.objects.filter(author=author)
        books_table = BookTable(books_qs)
        RequestConfig(request, paginate={"per_page": 5}).configure(books_table)

        return render(request, 'author_show.html',
                      {'author': author,
                       'books_table': books_table,
                       'books_qs': books_qs})
    else:
        messages.info(request, "Author does not exist")
        return authors(request)


@login_required(login_url='/sign_in/')
def publishers_show(request, publisher_id):
    publisher = Publisher.objects.get(id=publisher_id)
    if publisher:
        books_qs = Book.objects.filter(publisher=publisher)
        books_table = BookTable(books_qs)
        RequestConfig(request, paginate={"per_page": 5}).configure(books_table)

        return render(request, 'publisher_show.html',
                      {'publisher': publisher,
                       'books_table': books_table,
                       'books_qs': books_qs})
    else:
        messages.info(request, "Publisher does not exist")
        return publishers(request)


@login_required(login_url='/sign_in/')
def periods_show(request, period_id):
    period = LendPeriods.objects.get(id=period_id)
    if period:
        return render(request, 'period_show.html',
                      {'period': period})
    else:
        messages.info(request, "Period does not exist")
        return periods(request)


@group_required('Librarians')
def new_author(request):
    title = 'Add new author'
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New author has been added")
            return redirect('/')
        messages.info(request, "Incorrect or incomplete form")
    else:
        form = AuthorForm()
    return render(request, 'new_author.html',
                  {'title': title,
                   'form': form})


# this decorator also checks if user is authenticated
@group_required('Librarians')
def return_book(request, book_id):
    book = Book.objects.get(id=book_id)
    print book
    if book.lend_by is not None:
        book.lend_by = None
        book.lend_from = None
        book.save()
        messages.success(request, 'Book ' + book.title[5:] + ' has been marked as returned')
        return books_show(request, book_id)
    else:
        return redirect('/')


@login_required(login_url='/sign_in/')
def borrow_book(request, book_id):
    book = Book.objects.filter(id=book_id)[0]
    if book:
        # print "1st if"
        # print book.lend_period
        # print book.lend_by
        if book.lend_by is None:
            print "2d if"
            book.lend_by = request.user.profile
            book.lend_from = timezone.now()
            book.save()
    return redirect('/books/')


@login_required(login_url='/sign_in/')
def user(request, username):
    if request.user.username != username:
        user(request, request.user.username)
    else:
        profile = request.user.profile
        friends_table = FriendTable(profile.friends.all())
        books_qs = Book.objects.filter(lend_by=profile)
        books_table = BookTableUser(books_qs)
        # print request.user.profile.friends.all()
        # books_table.exclude = ('lend_period')
        RequestConfig(request, paginate={"per_page": 5}).configure(friends_table)
        RequestConfig(request, paginate={"per_page": 5}).configure(books_table)
        return render(request, 'user.html',
                      {'profile': profile,
                       'friends_table': friends_table,
                       'books_table': books_table,
                       'books_qs': books_qs})


@login_required(login_url='/sign_in/')
def user_quotations(request):
    user_saved_quotations = QuotationFromBook.objects.filter(user=request.user)
    paginator = Paginator(user_saved_quotations, 2)

    page = request.GET.get('page')
    try:
        quotations = paginator.page(page)
    except PageNotAnInteger:
        quotations = paginator.page(1)
    except EmptyPage:
        quotations = paginator.page(paginator.num_pages)

    return render(request, 'my_quotations.html',
                  {'quotations': quotations})


@login_required(login_url='/sign_in/')
def useredit(request, user_edit_form=None):
    # create form
    if request.method == 'POST':
        user_edit_form = UserEditForm(request.POST)
        if user_edit_form.is_valid():
            user_edit_form.save(request.user)
            messages.success(request, 'Profile successfully edited!')
            return user(request, request.user.username)
        else:
            messages.error(request, 'Invalid form...')
            return render(request, 'useredit.html', {'user_edit_form': user_edit_form})
    else:
        user_edit_form = UserEditForm(initial={'username': request.user.username, 'email': request.user.email,
                                               'first_name': request.user.first_name,
                                               'last_name': request.user.last_name,
                                               'mobile': request.user.profile.mobile,
                                               'website': request.user.profile.website})
        return render(request, 'useredit.html', {'user_edit_form': user_edit_form})


@login_required(login_url='/sign_in/')
def change_password(request):
    # messages.info(request, 'Hallo! asdkfj asdkl')
    # messages.info(request, 'Hallo! asdkfj asdkl')
    # messages.success(request, 'Hallo! asdkfj asdkl')
    if request.method == 'POST':
        if check_password(request.POST['current_pass'], request.user.password):
            if request.POST['new_pass'] == request.POST['new_pass_confirm']:
                # passwords are the same
                messages.success(request, 'Password has been changed successfully, you need to login once again')
                request.user.set_password(request.POST['new_pass'])
                request.user.save()

                return redirect('/sign_in/')
            else:
                # different password
                messages.error(request, 'Passwords are different')
                return redirect('/change_password/')
        else:
            # incorrect password
            messages.error(request, 'Incorrect password')
            return redirect('/change_password')
    else:
        return render(request, 'change_password.html', {})
