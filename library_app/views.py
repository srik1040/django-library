from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.template.base import add_to_builtins
from .forms import AuthenticateForm, UserCreateForm, UserEditForm, AuthorForm, PublisherForm, LendPeriodForm, BookForm
from .models import Book, LendPeriods, QuotationFromBook, Author, Publisher, UserProfile
from .tables import BookTable, FriendTable, BookTableUser, AuthorTable, PublisherTable, PeriodsTable
from django_tables2 import RequestConfig
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .decorators.group_required import group_required
from django.db.models.base import ObjectDoesNotExist
from fandjango.decorators import facebook_authorization_required


add_to_builtins('library_app.templatetags.xextends')
add_to_builtins('library_app.templatetags.has_group')


@facebook_authorization_required
def fb_sign_up(request, what=None):
    """
    Responsible for sign in and sign up using facebook.

    :param what: string that determines whether it is sign in or sign up
    :type what: `string`
    """
    if request.method == 'POST':
        if what.__str__() == "sign_up":
            init_data = {'first_name': request.facebook.user.first_name,
                         'last_name': request.facebook.user.last_name,
                         'username': request.facebook.user.first_name +
                                     '_' + request.facebook.user.facebook_id.__str__(),
                         'password1': request.POST.get('password1', ""),
                         'password2': request.POST.get('password2', "")}
            user_form = UserCreateForm(data=init_data)
            if user_form.is_valid():
                username = user_form.clean_username()
                password = user_form.clean_password2()
                user_form.save()
                user = authenticate(username=username, password=password)
                user.profile.fb_name = request.facebook.user.facebook_id
                user.save()
                login(request, user)
                messages.success(request, "Congratulations, you have successfully sign up using facebook!")
                return redirect('/')
            messages.error(request, "Incorrect passwords/pass mismatch")
            user_form = UserCreateForm()
            return render(request, 'sign_up.html', {'user_form': user_form})
    else:
        user = authenticate(username=request.facebook.user.first_name + '_' +
                                     request.facebook.user.facebook_id.__str__())
        login(request, user)
        messages.success(request, "Mate, congratulation on successfully signing in using facebook ;)")
        return redirect('/')
    return redirect('/')


def sign_in(request, auth_form=None):
    """
    View responsible for sign in using username and password
    (standard authorisation without facebook)

    :param auth_form: form that validates whether user can be authorized
    :type auth_form: `AuthenticationForm()`
    """
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


def sign_up(request, user_form=None, incomplete_form=None):
    """
    View responsible for sign up (without facebook authorization)

    :param user_form: for to validate input data and create new user (UserProfile and User)
    :type user_form: `UserCreateForm()`
    :param incomplete_form: (temporary) variable that determines whether the user_form contains errors
    :type incomplete_form: `string`
    """
    if request.method == 'POST' and incomplete_form is None:
        user_form = UserCreateForm(data=request.POST)
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Form invalid")
            return sign_up(request, user_form=user_form, incomplete_form=True)
    if incomplete_form is None or not incomplete_form:
        user_form = UserCreateForm()
    return render(request, 'sign_up.html', {'user_form': user_form})


def logout_view(request):
    """
    View logs user out of the system.

    """
    logout(request)
    return redirect('/')


def home(request):
    """
    View for rendering home for both: authorized and unauthorized users.
    """
    if request.user.is_authenticated():
        # private home
        friends_quotations = []
        nr = 0
        for friend in request.user.profile.friends.all():
            friend_quots = (QuotationFromBook.objects.filter(user=friend.user))
            quote = list(friend_quots[:1])[0].get_full_quotation() if friend_quots.count() > 0 else "---"
            if friend_quots.count() > 0:
                author_instance = list(friend_quots[:1])[0].book.author
                author = author_instance.name + ' ' + author_instance.surname if friend_quots.count() > 0 else "---"
            else:
                author = '---'
            friends_quotations.append((friend, quote, author, nr))
            nr += 1

        count = friends_quotations.__len__()
        return render(request,
                      'home.html',
                      {'user': request.user,
                       'friends_quotations': friends_quotations,
                       'count': count})
    else:
        # public home
        return render(request,
                      'public_home.html',
                      {'user': request.user})


def about(request):
    """
    Renders information about the system.
    """
    return render(request, 'about.html', {})


@login_required(login_url='/sign_in/')
def periods(request):
    """
    View allows users to search LendingPeriods.
    """
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


@login_required(login_url='/sign_in/')
def search_users(request):
    users_qs = UserProfile.objects.all()
    return_dict = {}
    if request.method == 'POST':
        if request.POST['search'] and request.POST['keyword']:
            found_users = UserProfile.objects.filter(
                user__name__contains=request.POST['keyword']) | UserProfile.objects.filter(
                user__surname__contains=request.POST['keyword'])

            users_qs = found_users
            return_dict['last_phrase'] = request.POST['keyword']

    users_table = FriendTable(users_qs)
    RequestConfig(request, paginate={"per_page": 5}).configure(users_table)
    return_dict['users_table'] = users_table
    return render(request, 'search_users.html', return_dict)


@group_required("Librarians")
def authors(request):
    """
    View presents all book authors present in the system.
    """
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
    """
    View presents all book publishers present in the system.
    """
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
    """
    View presents all books present in the system.
    """
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
    """
    View presents specific book.

    :param book_id: id of the specific book
    :type book_id: `int`
    """
    try:
        book = Book.objects.get(id=book_id)
    except ObjectDoesNotExist:
        messages.error(request, "This book does not exist")
        return redirect('/')

    if book:
        pbu = "false"

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
    """
    View presents specific author.
    :param author_id: author's id
    :type author_id: `int`
    """
    try:
        author = Author.objects.get(id=author_id)
    except ObjectDoesNotExist:
        messages.error(request, "This author does not exist")
        return redirect('/')

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
    """
    View presents specific publisher form the system.

    :param publisher_id: publisher's id
    :type publisher_id: `int`
    """
    try:
        publisher = Publisher.objects.get(id=publisher_id)
    except ObjectDoesNotExist:
        messages.error(request, "This publisher does not exist")
        return redirect('/')

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
    """
    View presents specific LendingPeriod.

    :param period_id: period's id
    :type period_id: `int`
    """
    try:
        period = LendPeriods.objects.get(id=period_id)
    except ObjectDoesNotExist:
        messages.error(request, "This period does not exist")
        return redirect('/')

    if period:
        return render(request, 'period_show.html',
                      {'period': period})
    else:
        messages.info(request, "Period does not exist")
        return periods(request)


@group_required('Librarians')
def remove_instance(request, what, id_obj):
    """
    View responsible for removing specific instance from the system.

    :param what: describes type of instance to remove e.g., authors, publishers, periods, books
    :type what: `string`
    :param id_obj: instance's id
    :type id_obj: `int`
    """
    if what == 'authors':
        what_singular = 'Author'
        obj = Author.objects.get(id=id_obj)
    elif what == 'publishers':
        what_singular = 'Publisher'
        obj = Publisher.objects.get(id=id_obj)
    elif what == 'periods':
        what_singular = 'Period'
        obj = LendPeriods.objects.get(id=id_obj)
    elif what == 'books':
        what_singular = 'Book'
        obj = Book.objects.get(id=id_obj)
    else:
        messages.info(request, "Incorrect type of instance...")
        return redirect('/')

    obj.delete()
    messages.success(request, what_singular + ' has been successfully removed')
    return redirect('/')


@group_required('Librarians')
def edit_instance(request, what, id_obj):
    """
    View responsible for editing specific instance from the system.

    :param what: describes type of instance to edit e.g., authors, publishers, periods, books
    :type what: `string`
    :param id_obj: instance's id
    :type id_obj: `int`
    """

    if what == 'authors':
        what_singular = 'author'
        form = (AuthorForm(request.POST, instance=Author.objects.get(id=id_obj)) if request.method == 'POST' else
                AuthorForm(instance=Author.objects.get(id=id_obj)))
    elif what == 'publishers':
        what_singular = 'publisher'
        form = (PublisherForm(request.POST,
                              instance=Publisher.objects.get(id=id_obj)) if request.method == 'POST' else PublisherForm(
            instance=Publisher.objects.get(id=id_obj)))
    elif what == 'periods':
        what_singular = 'period'
        form = (
            LendPeriodForm(request.POST, instance=LendPeriods.objects.get(id=id_obj)) if request.method == 'POST' else
            LendPeriodForm(instance=LendPeriods.objects.get(id=id_obj)))
    elif what == 'books':
        what_singular = 'book'
        form = (BookForm(request.POST, instance=Book.objects.get(id=id_obj)) if request.method == 'POST' else BookForm(
            instance=Book.objects.get(id=id_obj)))
    else:
        messages.info(request, "Incorrect type of instance...")
        return redirect('/')

    title = 'Edit ' + what_singular

    if request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, what_singular + " has been edited.")
            return redirect('/')
        messages.info(request, "Incorrect or incomplete form")
    return render(request, 'new.html',
                  {'title': title,
                   'form': form,
                   'what': what,
                   'id_obj': id_obj})


@group_required('Librarians')
def create_instance(request, what):
    """
    View responsible for creating instance of specific type.

    :param what: describes type of instance to create e.g., authors, publishers, periods, books
    :type what: `string`
    """
    if what == 'authors':
        what_singular = 'author'
        form = (AuthorForm(request.POST) if request.method == 'POST' else AuthorForm())
    elif what == 'publishers':
        what_singular = 'publisher'
        form = (PublisherForm(request.POST) if request.method == 'POST' else PublisherForm())
    elif what == 'periods':
        what_singular = 'period'
        form = (LendPeriodForm(request.POST) if request.method == 'POST' else LendPeriodForm())
    elif what == 'books':
        what_singular = 'book'
        form = (BookForm(request.POST) if request.method == 'POST' else BookForm())
    else:
        messages.info(request, "Incorrect type of new instance...")
        return redirect('/')

    title = 'Add new ' + what_singular

    if request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, "New " + what_singular + " has been added.")
            return redirect('/')
        messages.info(request, "Incorrect or incomplete form")
    return render(request, 'new.html',
                  {'title': title,
                   'form': form,
                   'what': what})


# this decorator also checks if user is authenticated
@group_required('Librarians')
def return_book(request, book_id):
    """
    View responsible for marking that specific book has been returned to library.

    :param book_id: book's id
    :type book_id: `int`
    """
    book = Book.objects.get(id=book_id)
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
    """
    View responsible for marking that specific book has been borrowed and is not available in the library.

    :param book_id: book's id
    :type book_id: `int`
    """
    book = Book.objects.get(id=book_id)
    if book:
        if book.lend_by is None:
            book.lend_by = request.user.profile
            book.lend_from = timezone.now()
            book.save()
    return redirect('/books/')


@login_required(login_url='/sign_in/')
def user(request, username):
    """
    View presents information connected with userprofile of specific user.

    :param username: username of user whom profile to render
    :param username: `string`
    """
    if request.user.username != username:
        other_user = True
    else:
        other_user = False
    try:
        this_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, "This user does not exist")
        redirect('/')

    profile = this_user.profile
    other_is_friend = True if request.user.profile.friends.filter(user=this_user).count() == 1 else False

    friends_table = FriendTable(profile.friends.all())
    books_qs = Book.objects.filter(lend_by=profile)
    books_table = BookTableUser(books_qs)

    user_saved_quotations = QuotationFromBook.objects.filter(user=this_user)
    paginator = Paginator(user_saved_quotations, 2)

    page = request.GET.get('page')
    try:
        quotations = paginator.page(page)
    except PageNotAnInteger:
        quotations = paginator.page(1)
    except EmptyPage:
        quotations = paginator.page(paginator.num_pages)

    RequestConfig(request, paginate={"per_page": 5}).configure(friends_table)
    RequestConfig(request, paginate={"per_page": 5}).configure(books_table)
    return render(request, 'user.html',
                  {'profile': profile,
                   'friends_table': friends_table,
                   'books_table': books_table,
                   'books_qs': books_qs,
                   'other_user': other_user,
                   'this_user': this_user,
                   'other_is_friend': other_is_friend,
                   'quotations': quotations})


@login_required(login_url='/sign_in/')
def user_connect(request, action, username):
    """
    View marks that two users of the system either become friends or
    has unfriended each other.

    :param action: describes which action has been undertaken, befirend or unfriend
    :type action: `string`
    :param username: describes which user is the subject of action (it's username)
    :type username: `string`
    :return:
    """
    try:
        other_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, "This user does not exist")
        redirect('/')

    if action == '1':
        # befriend
        str = 'befriended'
        request.user.profile.friends.add(other_user.profile)

    elif action == '0':
        # unfriend
        str = 'unfriended'
        request.user.profile.friends.remove(other_user.profile)
    else:
        messages.error(request, "Unknown action")
        redirect('/')

    request.user.profile.save()
    messages.success(request, "User successfully " + str)
    return user(request, request.user.username)


@login_required(login_url='/sign_in/')
def user_quotations(request):
    """
    Renders user's quotation
    """
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
    """
    Allows to edit user preferences and data
    :param user_edit_form: form to edit user data
    :type user_edit_form: UserEditForm instance
    """
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
    """
    Responsible for changing user password
    """
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
