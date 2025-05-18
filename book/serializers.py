from rest_framework import serializers
from .models import (
    BooksBook, BooksAuthor, BooksLanguage, 
    BooksSubject, BooksBookshelf, BooksFormat
)

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksLanguage
        fields = ['code']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksAuthor
        fields = ['name', 'birth_year', 'death_year']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksSubject
        fields = ['name']

class BookshelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksBookshelf
        fields = ['name']

class FormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksFormat
        fields = ['mime_type', 'url']

class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    bookshelves = BookshelfSerializer(many=True, read_only=True)
    formats = FormatSerializer(source='booksformat_set', many=True, read_only=True)
    
    class Meta:
        model = BooksBook
        fields = [
            'id', 'title', 'gutenberg_id', 'download_count',
            'authors', 'languages', 'subjects', 'bookshelves', 'formats'
        ] 