from django.test import TestCase
from .models import Book, Author, Publisher, LendPeriods
from django.utils import timezone
from django.test import Client
import unittest
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime


class SimpleDataTests(TestCase):
    """
    Performs simple database tests e.g., if certain models (Author,
    Publisher, LendingPeriod, Book) can be correctly instantiated
    """
    def test_author(self):
        self.assertEqual(Author.objects.all().count(), 0)
        self.author1 = Author.objects.create(name="Imie", surname="Nazwisko", date_of_birth=timezone.now())
        self.assertEqual(Author.objects.all().count(), 1)
        self.assertEqual(Author.objects.filter(name__exact="Imie").count(), 1)

    def test_publisher(self):
        self.assertEqual(Publisher.objects.all().count(), 0)
        self.publisher1 = Publisher.objects.create(name="Nazwa wydawnictwa")
        self.assertEqual(Publisher.objects.all().count(), 1)
        self.assertEqual(Publisher.objects.filter(name__exact="Nazwa wydawnictwa").count(), 1)

    def test_period(self):
        self.assertEqual(LendPeriods.objects.all().count(), 0)
        self.period1 = LendPeriods.objects.create(name="month", days_amount=31)
        self.assertEqual(LendPeriods.objects.all().count(), 1)
        self.assertEqual(LendPeriods.objects.filter(days_amount__exact=31).count(), 1)

    def test_book(self):
        self.assertEqual(Book.objects.all().count(), 0)
        self.author1 = Author.objects.create(name="Imie", surname="Nazwisko", date_of_birth=timezone.now())
        self.publisher1 = Publisher.objects.create(name="Nazwa wydawnictwa")
        self.period1 = LendPeriods.objects.create(name="month", days_amount=31)

        self.book1 = Book.objects.create(title="Tytul", ISBN="9232",
                                         publisher=self.publisher1,
                                         author=self.author1,
                                         lend_period=self.period1,
                                         page_amount=360)

        self.assertEqual(Book.objects.all().count(), 1)
        self.assertEqual(Book.objects.filter(title__exact="Tytul").count(), 1)


class SimpleWebTest(TestCase):
    """
    Tests if specific urls (about, home, sign in/up) exist and contains
    necessary phrases
    """
    def setUp(self):
        self.client = Client()

    def test_about(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')
        self.assertContains(response, 'About us')

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public_home.html')
        self.assertContains(response, 'Welcome in Library Online Management System')

    def test_sign_in(self):
        response = self.client.get('/sign_in/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_in.html')
        self.assertContains(response, 'Please sign in')

    def test_sign_up(self):
        response = self.client.get('/sign_up/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        self.assertContains(response, 'Please sign up')
        self.assertContains(response, 'Sign up with FB')


class PagesForAuthorizedUserAreBlocked(unittest.TestCase):
    """
    Checks if pages restricted to authorized users can not
    be accessible by unauthorized ones.
    """
    def setUp(self):
        self.client = Client()

    def test_books(self):
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, 302)

    def test_authors(self):
        response = self.client.get('/authors/')
        self.assertEqual(response.status_code, 302)

    def test_periods(self):
        response = self.client.get('/periods/')
        self.assertEqual(response.status_code, 302)

    def test_quotations(self):
        response = self.client.get('/my_quotations')
        self.assertEqual(response.status_code, 301)

        # pages for librarians

    def test_adding_book(self):
        response = self.client.get('/books/new')
        self.assertEqual(response.status_code, 301)

    def test_adding_publisher(self):
        response = self.client.get('/publishers/new')
        self.assertEqual(response.status_code, 301)

    def test_adding_period(self):
        response = self.client.get('/periods/new')
        self.assertEqual(response.status_code, 301)

    def test_adding_author(self):
        response = self.client.get('/authors/new')
        self.assertEqual(response.status_code, 301)

    def test_editing_book(self):
        response = self.client.get('/books/edit/1')
        self.assertEqual(response.status_code, 302)

    def test_editing_publisher(self):
        response = self.client.get('/publishers/edit/1')
        self.assertEqual(response.status_code, 302)

    def test_editing_period(self):
        response = self.client.get('/periods/edit/1')
        self.assertEqual(response.status_code, 302)

    def test_editing_author(self):
        response = self.client.get('/authors/edit/1')
        self.assertEqual(response.status_code, 302)


class AdminPanelTest(LiveServerTestCase):
    """
    Simple selenium test. In this case we are adding an Author instance
    in django admin (which is, obviously, not necessarily
    what we usually want to test, but this demonstrates
    ability to use selenium for testing purposes).
    """
    fixtures = ['users.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_create_new_authors_via_admin_site(self):
        # Gertrude opens her web browser, and goes to the admin page
        self.browser.get(self.live_server_url + '/admin/')

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)

        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('potan')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('12345')
        password_field.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)
        self.assertIn('Authors', body.text)

        new_author_link = self.browser.find_element_by_link_text('Authors')
        new_author_link.click()

        new_author_link = self.browser.find_element_by_link_text('Add Author')
        new_author_link.click()

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Name:', body.text)
        self.assertIn('Surname:', body.text)
        self.assertIn('Date of birth:', body.text)

        field = self.browser.find_element_by_name('name')
        field.send_keys("Piotr")
        field = self.browser.find_element_by_name('surname')
        field.send_keys("Gasowski")
        field = self.browser.find_element_by_name('date_of_birth')

        now = datetime.now()
        date = "%d-%d-%d" % (now.year, now.month, now.day)
        field.send_keys(date)

        # self.browser.find_elements_by_link_text("Today").click()

        save_button = self.browser.find_element_by_css_selector("input[value='Save']")
        save_button.click()

        links = self.browser.find_elements_by_link_text(
            "Author: Piotr Gasowski"
        )
        self.assertEquals(len(links), 1)
