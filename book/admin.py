from django.contrib import admin

# Register your models here.

from .models import BooksBook, BooksAuthor, BooksLanguage, BooksSubject, BooksBookshelf, BooksFormat

admin.site.register(BooksBook)
admin.site.register(BooksAuthor)
admin.site.register(BooksLanguage)
admin.site.register(BooksSubject)
admin.site.register(BooksBookshelf)
admin.site.register(BooksFormat)
