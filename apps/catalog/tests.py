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
