from django.test import TestCase
from django.db.models import ProtectedError
from django.db import IntegrityError
from .models import Author, Category, Book

class CatalogModelTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Jane Doe", biography="A great writer.")
        self.category = Category.objects.create(name="Science Fiction", description="Sci-Fi books")
        self.book = Book.objects.create(
            title="The Future",
            author=self.author,
            category=self.category,
            publication_year=2050,
            pdf_file="books/pdfs/test-book.pdf"
        )

    def test_author_creation_and_str(self):
        self.assertEqual(self.author.name, "Jane Doe")
        self.assertEqual(str(self.author), "Jane Doe")

    def test_category_creation_and_str(self):
        self.assertEqual(self.category.name, "Science Fiction")
        self.assertEqual(str(self.category), "Science Fiction")

    def test_category_name_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Science Fiction")

    def test_book_creation_and_str(self):
        self.assertEqual(self.book.title, "The Future")
        self.assertEqual(str(self.book), "The Future")

    def test_book_defaults(self):
        self.assertTrue(self.book.is_published)

    def test_book_blank_publication_year(self):
        book2 = Book.objects.create(
            title="Another Book",
            author=self.author,
            category=self.category,
            pdf_file="books/pdfs/test-book2.pdf"
        )
        self.assertIsNone(book2.publication_year)

    def test_reverse_relationships(self):
        self.assertIn(self.book, self.author.books.all())
        self.assertIn(self.book, self.category.books.all())

    def test_author_protect(self):
        with self.assertRaises(ProtectedError):
            self.author.delete()

    def test_category_protect(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_book_pdf_file(self):
        self.assertEqual(self.book.pdf_file.name, "books/pdfs/test-book.pdf")

from django.contrib.admin.sites import site
from django.urls import reverse
from django.contrib.auth import get_user_model

class CatalogAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            password="testpassword123",
            email="admin@example.com"
        )
        self.client.login(username="admin_test", password="testpassword123")

    def test_models_are_registered(self):
        self.assertTrue(site.is_registered(Author))
        self.assertTrue(site.is_registered(Category))
        self.assertTrue(site.is_registered(Book))

    def test_admin_classes(self):
        from .admin import AuthorAdmin, CategoryAdmin, BookAdmin
        self.assertIsInstance(site._registry[Author], AuthorAdmin)
        self.assertIsInstance(site._registry[Category], CategoryAdmin)
        self.assertIsInstance(site._registry[Book], BookAdmin)

    def test_book_admin_configuration(self):
        from .admin import BookAdmin
        admin_instance = site._registry[Book]

        self.assertIn("title", admin_instance.list_display)
        self.assertIn("author", admin_instance.list_display)
        self.assertIn("category", admin_instance.list_display)
        self.assertIn("publication_year", admin_instance.list_display)
        self.assertIn("is_published", admin_instance.list_display)

        self.assertIn("is_published", admin_instance.list_filter)
        self.assertIn("category", admin_instance.list_filter)
        self.assertIn("author", admin_instance.list_filter)

        self.assertIn("title", admin_instance.search_fields)
        self.assertIn("author__name", admin_instance.search_fields)
        self.assertIn("category__name", admin_instance.search_fields)

    def test_admin_login_page_reachable(self):
        self.client.logout()
        url = reverse('admin:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_author_admin_changelist_view(self):
        url = reverse('admin:catalog_author_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_category_admin_changelist_view(self):
        url = reverse('admin:catalog_category_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_book_admin_changelist_view(self):
        url = reverse('admin:catalog_book_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
