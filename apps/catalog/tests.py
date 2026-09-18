from django.test import TestCase, Client
from django.db.models import ProtectedError
from django.db import IntegrityError
from django.contrib.admin.sites import site
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from apps.core.validators import BOOK_PDF_MAX_SIZE
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


class CatalogAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            password="testpassword123",
            email="admin@example.com"
        )
        self.client = Client()
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

    def test_book_admin_form_rejects_fake_pdf_content(self):
        author = Author.objects.create(name='Upload Admin Author')
        category = Category.objects.create(name='Upload Admin Category')
        request = RequestFactory().get('/admin/catalog/book/add/')
        request.user = self.admin_user
        form_class = site._registry[Book].get_form(request)
        form = form_class(
            data={
                'title': 'Invalid Admin Upload',
                'author': author.pk,
                'category': category.pk,
                'is_published': True,
            },
            files={
                'pdf_file': SimpleUploadedFile(
                    'fake.pdf', b'not a PDF', content_type='application/pdf'
                ),
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('pdf_file', form.errors)


class BookUploadValidationTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name='Validation Author')
        self.category = Category.objects.create(name='Validation Category')

    def _book(self, filename, content):
        return Book(
            title='Validated Book',
            author=self.author,
            category=self.category,
            pdf_file=SimpleUploadedFile(filename, content),
        )

    def test_valid_pdf_passes_model_validation(self):
        self._book('book.pdf', b'%PDF-1.4 content').full_clean()

    def test_non_pdf_extension_is_rejected(self):
        with self.assertRaises(ValidationError):
            self._book('book.txt', b'%PDF-1.4 content').full_clean()

    def test_fake_pdf_content_is_rejected(self):
        with self.assertRaises(ValidationError):
            self._book('book.pdf', b'not a PDF').full_clean()

    def test_zero_byte_pdf_is_rejected(self):
        with self.assertRaises(ValidationError):
            self._book('book.pdf', b'').full_clean()

    def test_oversized_pdf_is_rejected(self):
        book = self._book('book.pdf', b'%PDF-1.4 content')
        book.pdf_file.file.size = BOOK_PDF_MAX_SIZE + 1
        with self.assertRaises(ValidationError):
            book.full_clean()


class CatalogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.book_list_url = reverse('catalog:book_list')
        self.author = Author.objects.create(name="Test Author View")
        self.category = Category.objects.create(name="Test Category View")

    def test_book_list_url_resolves(self):
        resolver = resolve('/books/')
        self.assertEqual(resolver.view_name, 'catalog:book_list')

    def test_anonymous_user_can_access_book_list(self):
        self.client.logout()
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, 200)

    def test_book_list_resolves_and_returns_200(self):
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_list.html')

    def test_book_list_displays_published_books(self):
        book = Book.objects.create(title="Published View Book", author=self.author, category=self.category, is_published=True, publication_year=2024, pdf_file="books/pdfs/test.pdf")
        response = self.client.get(self.book_list_url)
        self.assertContains(response, "Published View Book")
        self.assertContains(response, "Test Author View")
        self.assertContains(response, "Test Category View")
        self.assertContains(response, "2024")

    def test_book_list_does_not_display_unpublished_books(self):
        book = Book.objects.create(title="Unpublished View Book", author=self.author, category=self.category, is_published=False, pdf_file="books/pdfs/test.pdf")
        response = self.client.get(self.book_list_url)
        self.assertNotContains(response, "Unpublished View Book")

    def test_book_without_publication_year_does_not_break(self):
        book = Book.objects.create(title="No Year Book", author=self.author, category=self.category, is_published=True, pdf_file="books/pdfs/test.pdf")
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Year Book")
        self.assertNotContains(response, "سنة النشر:")

    def test_empty_catalog_message(self):
        response = self.client.get(self.book_list_url)
        self.assertContains(response, "لا توجد كتب متاحة حالياً.")

    def test_no_pdf_url_rendered(self):
        book = Book.objects.create(title="PDF Check Book", author=self.author, category=self.category, is_published=True, pdf_file="books/pdfs/secret.pdf")
        response = self.client.get(self.book_list_url)
        self.assertNotContains(response, "secret.pdf")
        self.assertNotContains(response, book.pdf_file.url)


class CatalogDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name="Detail Author", biography="Bio")
        self.category = Category.objects.create(name="Detail Category", description="Desc")
        self.pub_book = Book.objects.create(title="Pub Book", author=self.author, category=self.category, is_published=True, pdf_file="books/pdfs/pub.pdf")
        self.unpub_book = Book.objects.create(title="Unpub Book", author=self.author, category=self.category, is_published=False, pdf_file="books/pdfs/unpub.pdf")

    def test_book_detail_url_resolves(self):
        resolver = resolve(f'/books/{self.pub_book.pk}/')
        self.assertEqual(resolver.view_name, 'catalog:book_detail')

    def test_published_book_detail_returns_200(self):
        url = reverse('catalog:book_detail', args=[self.pub_book.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_detail.html')
        self.assertContains(response, "Pub Book")
        self.assertContains(response, "Detail Author")
        self.assertContains(response, "Detail Category")
        self.assertNotContains(response, "pub.pdf")
        self.assertNotContains(response, self.pub_book.pdf_file.url)

    def test_unpublished_book_detail_returns_404(self):
        url = reverse('catalog:book_detail', args=[self.unpub_book.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_author_detail_returns_200_and_shows_only_published(self):
        url = reverse('catalog:author_detail', args=[self.author.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Author")
        self.assertContains(response, "Pub Book")
        self.assertNotContains(response, "Unpub Book")

    def test_category_detail_returns_200_and_shows_only_published(self):
        url = reverse('catalog:category_detail', args=[self.category.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Category")
        self.assertContains(response, "Pub Book")
        self.assertNotContains(response, "Unpub Book")

    def test_anonymous_access_to_detail_pages(self):
        self.client.logout()
        b_url = reverse('catalog:book_detail', args=[self.pub_book.pk])
        a_url = reverse('catalog:author_detail', args=[self.author.pk])
        c_url = reverse('catalog:category_detail', args=[self.category.pk])
        self.assertEqual(self.client.get(b_url).status_code, 200)
        self.assertEqual(self.client.get(a_url).status_code, 200)
        self.assertEqual(self.client.get(c_url).status_code, 200)

    def test_book_list_links_to_detail(self):
        url = reverse('catalog:book_list')
        response = self.client.get(url)
        self.assertContains(response, reverse('catalog:book_detail', args=[self.pub_book.pk]))
        self.assertContains(response, reverse('catalog:author_detail', args=[self.author.pk]))
        self.assertContains(response, reverse('catalog:category_detail', args=[self.category.pk]))


class CatalogSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.book_list_url = reverse('catalog:book_list')

        self.author1 = Author.objects.create(name="Author Alpha", biography="Bio A")
        self.author2 = Author.objects.create(name="Author Beta", biography="Bio B")

        self.cat1 = Category.objects.create(name="Cat Fiction", description="Fictional")
        self.cat2 = Category.objects.create(name="Cat Science", description="Scientific")

        # Book 1: Author1, Cat1
        self.book1 = Book.objects.create(
            title="The Alpha Fiction",
            description="A great story about alphas",
            author=self.author1,
            category=self.cat1,
            is_published=True,
            pdf_file="books/pdfs/book1.pdf"
        )
        # Book 2: Author2, Cat2
        self.book2 = Book.objects.create(
            title="The Beta Science",
            description="Scientific study of betas",
            author=self.author2,
            category=self.cat2,
            is_published=True,
            pdf_file="books/pdfs/book2.pdf"
        )
        # Book 3: Unpublished
        self.book3_unpub = Book.objects.create(
            title="Secret Alpha",
            description="Unpublished alpha secrets",
            author=self.author1,
            category=self.cat1,
            is_published=False,
            pdf_file="books/pdfs/secret.pdf"
        )

    def test_search_by_partial_title(self):
        response = self.client.get(self.book_list_url, {'q': 'Alpha'})
        self.assertContains(response, "The Alpha Fiction")
        self.assertNotContains(response, "The Beta Science")

    def test_search_by_description(self):
        response = self.client.get(self.book_list_url, {'q': 'study'})
        self.assertContains(response, "The Beta Science")
        self.assertNotContains(response, "The Alpha Fiction")

    def test_search_by_author_name(self):
        response = self.client.get(self.book_list_url, {'q': 'Beta'})
        self.assertContains(response, "The Beta Science")
        self.assertNotContains(response, "The Alpha Fiction")

    def test_search_by_category_name(self):
        response = self.client.get(self.book_list_url, {'q': 'Fiction'})
        self.assertContains(response, "The Alpha Fiction")
        self.assertNotContains(response, "The Beta Science")

    def test_search_never_returns_unpublished(self):
        response = self.client.get(self.book_list_url, {'q': 'Secret'})
        self.assertNotContains(response, "Secret Alpha")
        self.assertContains(response, "لا توجد كتب متاحة حالياً.")

    def test_category_filter(self):
        response = self.client.get(self.book_list_url, {'category': self.cat1.pk})
        self.assertContains(response, "The Alpha Fiction")
        self.assertNotContains(response, "The Beta Science")

    def test_author_filter(self):
        response = self.client.get(self.book_list_url, {'author': self.author2.pk})
        self.assertContains(response, "The Beta Science")
        self.assertNotContains(response, "The Alpha Fiction")

    def test_combined_q_and_category(self):
        # Matches book1, but cat2 filters it out
        response = self.client.get(self.book_list_url, {'q': 'Alpha', 'category': self.cat2.pk})
        self.assertNotContains(response, "The Alpha Fiction")

    def test_combined_q_and_author(self):
        response = self.client.get(self.book_list_url, {'q': 'Science', 'author': self.author2.pk})
        self.assertContains(response, "The Beta Science")

    def test_combined_all_filters(self):
        response = self.client.get(self.book_list_url, {'q': 'Alpha', 'category': self.cat1.pk, 'author': self.author1.pk})
        self.assertContains(response, "The Alpha Fiction")

    def test_empty_search_returns_all_published(self):
        response = self.client.get(self.book_list_url, {'q': '', 'category': '', 'author': ''})
        self.assertContains(response, "The Alpha Fiction")
        self.assertContains(response, "The Beta Science")
        self.assertNotContains(response, "Secret Alpha")

    def test_no_result_displays_empty_state(self):
        response = self.client.get(self.book_list_url, {'q': 'NonExistentXYZ'})
        self.assertContains(response, "لا توجد كتب متاحة حالياً.")

    def test_search_form_preserves_state(self):
        response = self.client.get(self.book_list_url, {'q': 'TestQuery', 'category': self.cat1.pk, 'author': self.author1.pk})
        self.assertContains(response, 'value="TestQuery"')
        self.assertContains(response, f'value="{self.cat1.pk}" selected')
        self.assertContains(response, f'value="{self.author1.pk}" selected')

    def test_invalid_category_parameter_does_not_crash(self):
        response = self.client.get(self.book_list_url, {'category': 'invalid'})
        self.assertEqual(response.status_code, 200)

    def test_invalid_author_parameter_does_not_crash(self):
        response = self.client.get(self.book_list_url, {'author': 'invalid'})
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_can_search(self):
        self.client.logout()
        response = self.client.get(self.book_list_url, {'q': 'Alpha'})
        self.assertEqual(response.status_code, 200)

    def test_no_pdf_url_exposed_in_search(self):
        response = self.client.get(self.book_list_url, {'q': 'Alpha'})
        self.assertNotContains(response, "book1.pdf")
        self.assertNotContains(response, self.book1.pdf_file.url)

    def test_existing_detail_links_present(self):
        response = self.client.get(self.book_list_url, {'q': 'Alpha'})
        self.assertContains(response, reverse('catalog:book_detail', args=[self.book1.pk]))
        self.assertContains(response, reverse('catalog:author_detail', args=[self.author1.pk]))
        self.assertContains(response, reverse('catalog:category_detail', args=[self.cat1.pk]))
