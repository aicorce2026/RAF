from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.catalog.models import Author, Category, Book

class CoreInterfaceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_home_page_returns_200(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(self.home_url)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_home_page_contains_arabic_content(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, 'المكتبة الرقمية')

    def test_rtl_document_direction(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, 'lang="ar"')
        self.assertContains(response, 'dir="rtl"')

    def test_shared_base_navigation(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, '<nav')
        self.assertContains(response, 'الرئيسية')
        self.assertContains(response, 'الكتب')

    def test_anonymous_navigation(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, reverse('accounts:login'))
        self.assertContains(response, reverse('accounts:register'))
        self.assertNotContains(response, 'تسجيل الخروج')

    def test_authenticated_navigation(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.home_url)
        self.assertContains(response, reverse('accounts:profile'))
        self.assertContains(response, 'تسجيل الخروج')
        self.assertNotContains(response, reverse('accounts:login'))

    def test_logout_is_post(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.home_url)
        self.assertContains(response, 'method="post"')
        self.assertContains(response, reverse('accounts:logout'))
        # Ensure it's not just a regular href link
        self.assertNotContains(response, f'href="{reverse("accounts:logout")}"')

    def test_navbar_books_link(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, f'href="{reverse("catalog:book_list")}"')


class CoreHomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')
        self.author = Author.objects.create(name="Test Author")
        self.category = Category.objects.create(name="Test Category")

    def test_home_displays_published_books(self):
        book = Book.objects.create(title="Published Book", author=self.author, category=self.category, is_published=True, pdf_file="books/pdfs/test.pdf")
        response = self.client.get(self.home_url)
        self.assertContains(response, "Published Book")
        self.assertContains(response, "Test Author")
        self.assertContains(response, "Test Category")

    def test_home_does_not_display_unpublished_books(self):
        book = Book.objects.create(title="Unpublished Book", author=self.author, category=self.category, is_published=False, pdf_file="books/pdfs/test.pdf")
        response = self.client.get(self.home_url)
        self.assertNotContains(response, "Unpublished Book")

    def test_home_recent_book_limit(self):
        for i in range(10):
            Book.objects.create(title=f"Book {i}", author=self.author, category=self.category, is_published=True, pdf_file="books/pdfs/test.pdf")
        response = self.client.get(self.home_url)
        self.assertEqual(len(response.context['published_books']), 6)

    def test_view_all_books_link(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, reverse('catalog:book_list'))

    def test_home_page_links_to_detail(self):
        book = Book.objects.create(title="Home Detail Book", author=self.author, category=self.category, is_published=True, pdf_file="books/pdfs/home.pdf")
        response = self.client.get(self.home_url)
        self.assertContains(response, reverse('catalog:book_detail', args=[book.pk]))
        self.assertContains(response, reverse('catalog:author_detail', args=[self.author.pk]))
        self.assertContains(response, reverse('catalog:category_detail', args=[self.category.pk]))
