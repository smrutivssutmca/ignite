from django.db import models

class BooksAuthor(models.Model):
    """
    Author model representing writers of books in the Project Gutenberg catalog.
    Contains biographical information like birth and death years.
    """
    id = models.AutoField(primary_key=True)
    birth_year = models.SmallIntegerField(null=True)
    death_year = models.SmallIntegerField(null=True)
    name = models.TextField()

    class Meta:
        db_table = 'books_author'
        
    def __str__(self):
        return self.name

class BooksBook(models.Model):
    """
    Main book model representing works in the Project Gutenberg catalog.
    Contains information about books including title, download statistics,
    and relationships to authors, languages, subjects, and bookshelves.
    """
    id = models.AutoField(primary_key=True)
    download_count = models.IntegerField(null=True)
    gutenberg_id = models.IntegerField()
    media_type = models.TextField()
    title = models.TextField(null=True)
    
    authors = models.ManyToManyField('BooksAuthor', through='BooksBookAuthors')
    bookshelves = models.ManyToManyField('BooksBookshelf', through='BooksBookBookshelves')
    languages = models.ManyToManyField('BooksLanguage', through='BooksBookLanguages')
    subjects = models.ManyToManyField('BooksSubject', through='BooksBookSubjects')

    class Meta:
        db_table = 'books_book'
        
    def __str__(self):
        return self.title or f"Book {self.id}"

class BooksBookAuthors(models.Model):
    """
    Junction table linking books to their authors.
    Represents the many-to-many relationship between books and authors.
    """
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey('BooksBook', on_delete=models.CASCADE, db_column='book_id')
    author = models.ForeignKey('BooksAuthor', on_delete=models.CASCADE, db_column='author_id')

    class Meta:
        db_table = 'books_book_authors'

class BooksBookBookshelves(models.Model):
    """
    Junction table linking books to bookshelves.
    Represents the many-to-many relationship between books and bookshelves.
    """
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey('BooksBook', on_delete=models.CASCADE, db_column='book_id')
    bookshelf = models.ForeignKey('BooksBookshelf', on_delete=models.CASCADE, db_column='bookshelf_id')

    class Meta:
        db_table = 'books_book_bookshelves'

class BooksBookLanguages(models.Model):
    """
    Junction table linking books to languages.
    Represents the many-to-many relationship between books and languages.
    """
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey('BooksBook', on_delete=models.CASCADE, db_column='book_id')
    language = models.ForeignKey('BooksLanguage', on_delete=models.CASCADE, db_column='language_id')

    class Meta:
        db_table = 'books_book_languages'

class BooksBookSubjects(models.Model):
    """
    Junction table linking books to subjects.
    Represents the many-to-many relationship between books and subjects.
    """
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey('BooksBook', on_delete=models.CASCADE, db_column='book_id')
    subject = models.ForeignKey('BooksSubject', on_delete=models.CASCADE, db_column='subject_id')

    class Meta:
        db_table = 'books_book_subjects'

class BooksBookshelf(models.Model):
    """
    Bookshelf model representing categories or collections of books in Project Gutenberg.
    Examples include "Adventure", "Fantasy", "Children's Literature", etc.
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    class Meta:
        db_table = 'books_bookshelf'
        
    def __str__(self):
        return self.name

class BooksFormat(models.Model):
    """
    Format model representing the available download formats for a book.
    Each book can have multiple formats (EPUB, HTML, Text, etc.)
    """
    id = models.AutoField(primary_key=True)
    mime_type = models.TextField()
    url = models.TextField()
    book = models.ForeignKey('BooksBook', on_delete=models.CASCADE, db_column='book_id')

    class Meta:
        db_table = 'books_format'

class BooksLanguage(models.Model):
    """
    Language model representing the languages in which books are available.
    Uses language codes (e.g., 'en' for English, 'fr' for French).
    """
    id = models.AutoField(primary_key=True)
    code = models.TextField()

    class Meta:
        db_table = 'books_language'
        
    def __str__(self):
        return self.code

class BooksSubject(models.Model):
    """
    Subject model representing topics or subjects assigned to books.
    Examples include "Fiction", "Love stories", "Historical Fiction", etc.
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    class Meta:
        db_table = 'books_subject'
        
    def __str__(self):
        return self.name

