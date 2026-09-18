from django.db import models
from django.core.exceptions import ValidationError

from apps.core.validators import validate_book_pdf_upload

class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    description = models.TextField(blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    pdf_file = models.FileField(upload_to="books/pdfs/")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def clean(self):
        super().clean()
        if self.pdf_file:
            try:
                validate_book_pdf_upload(self.pdf_file)
            except ValidationError as error:
                raise ValidationError({"pdf_file": error}) from error

    def __str__(self):
        return self.title
