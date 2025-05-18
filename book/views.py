import logging
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import BooksBook
from .serializers import BookSerializer

# Set up logger
logger = logging.getLogger('book.views')

class BookPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 100
    page_size_query_param = 'page_size'

class BookListView(APIView):
    """
    API endpoint that allows books to be viewed.
    
    Retrieves a list of books, ordered by download count (descending).
    
    Can filter by:
    - gutenberg_id: Filter by multiple Gutenberg IDs, comma-separated
    - language: Filter by language code(s), comma-separated
    - topic: Filter by topic (subject or bookshelf), comma-separated
    - mime_type: Filter by mime-type, comma-separated
    - author: Filter by author name, comma-separated
    - title: Filter by title (case insensitive partial match), comma-separated
    """
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'gutenberg_id', 
                openapi.IN_QUERY, 
                description="Filter by multiple Gutenberg IDs (comma-separated)", 
                type=openapi.TYPE_STRING,
                example="1342,84,11"
            ),
            openapi.Parameter(
                'language', 
                openapi.IN_QUERY, 
                description="Filter by language code(s) (comma-separated)", 
                type=openapi.TYPE_STRING,
                example="en,fr"
            ),
            openapi.Parameter(
                'topic', 
                openapi.IN_QUERY, 
                description="Filter by topic (subject or bookshelf) with case-insensitive partial matching (comma-separated)", 
                type=openapi.TYPE_STRING,
                example="child,adventure"
            ),
            openapi.Parameter(
                'mime_type', 
                openapi.IN_QUERY, 
                description="Filter by MIME-type (comma-separated)", 
                type=openapi.TYPE_STRING,
                example="text/html,application/epub+zip"
            ),
            openapi.Parameter(
                'author', 
                openapi.IN_QUERY, 
                description="Filter by author name with case-insensitive partial matching (comma-separated)", 
                type=openapi.TYPE_STRING,
                example="twain,dickens"
            ),
            openapi.Parameter(
                'title', 
                openapi.IN_QUERY, 
                description="Filter by title with case-insensitive partial matching (comma-separated)", 
                type=openapi.TYPE_STRING,
                example="pride,adventure"
            ),
            openapi.Parameter(
                'page', 
                openapi.IN_QUERY, 
                description="Page number for pagination", 
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size', 
                openapi.IN_QUERY, 
                description="Number of results per page (max 100)", 
                type=openapi.TYPE_INTEGER,
                default=25
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved list of books",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of books on current page"),
                        'count_total': openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of books matching criteria"),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, description="URL for next page of results", nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, description="URL for previous page of results", nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            )
        }
    )
    def get(self, request, format=None):
        logger.info(f"Book list request received with params: {request.query_params}")
        
        # Start with the base queryset with prefetched related objects
        queryset = BooksBook.objects.prefetch_related(
            'authors', 
            'languages', 
            'subjects', 
            'bookshelves', 
            'booksformat_set'
        ).order_by('-download_count')
        
        # Track applied filters
        applied_filters = []
        
        # Filter by gutenberg_id (multiple IDs, comma-separated)
        gutenberg_ids = request.query_params.get('gutenberg_id')
        if gutenberg_ids:
            try:
                ids = [int(x.strip()) for x in gutenberg_ids.split(',') if x.strip().isdigit()]
                if ids:
                    queryset = queryset.filter(gutenberg_id__in=ids)
                    applied_filters.append(f"gutenberg_id: {ids}")
                    logger.debug(f"Applied gutenberg_id filter: {ids}")
            except Exception as e:
                logger.error(f"Error applying gutenberg_id filter: {str(e)}")
        
        # Filter by language
        languages = request.query_params.get('language')
        if languages:
            try:
                language_codes = [x.strip().lower() for x in languages.split(',') if x.strip()]
                if language_codes:
                    queryset = queryset.filter(languages__code__in=language_codes)
                    applied_filters.append(f"language: {language_codes}")
                    logger.debug(f"Applied language filter: {language_codes}")
            except Exception as e:
                logger.error(f"Error applying language filter: {str(e)}")
        
        # Filter by topic (subject or bookshelf)
        topics = request.query_params.get('topic')
        if topics:
            try:
                topic_list = [x.strip() for x in topics.split(',') if x.strip()]
                if topic_list:
                    q_objects = Q()
                    for topic in topic_list:
                        q_objects |= Q(subjects__name__icontains=topic) | Q(bookshelves__name__icontains=topic)
                    queryset = queryset.filter(q_objects).distinct()
                    applied_filters.append(f"topic: {topic_list}")
                    logger.debug(f"Applied topic filter: {topic_list}")
            except Exception as e:
                logger.error(f"Error applying topic filter: {str(e)}")
        
        # Filter by mime_type
        mime_types = request.query_params.get('mime_type')
        if mime_types:
            try:
                mime_type_list = [x.strip() for x in mime_types.split(',') if x.strip()]
                if mime_type_list:
                    queryset = queryset.filter(booksformat__mime_type__in=mime_type_list).distinct()
                    applied_filters.append(f"mime_type: {mime_type_list}")
                    logger.debug(f"Applied mime_type filter: {mime_type_list}")
            except Exception as e:
                logger.error(f"Error applying mime_type filter: {str(e)}")
        
        # Filter by author
        authors = request.query_params.get('author')
        if authors:
            try:
                author_list = [x.strip() for x in authors.split(',') if x.strip()]
                if author_list:
                    q_objects = Q()
                    for author in author_list:
                        q_objects |= Q(authors__name__icontains=author)
                    queryset = queryset.filter(q_objects).distinct()
                    applied_filters.append(f"author: {author_list}")
                    logger.debug(f"Applied author filter: {author_list}")
            except Exception as e:
                logger.error(f"Error applying author filter: {str(e)}")
        
        # Filter by title
        titles = request.query_params.get('title')
        if titles:
            try:
                title_list = [x.strip() for x in titles.split(',') if x.strip()]
                if title_list:
                    q_objects = Q()
                    for title in title_list:
                        q_objects |= Q(title__icontains=title)
                    queryset = queryset.filter(q_objects).distinct()
                    applied_filters.append(f"title: {title_list}")
                    logger.debug(f"Applied title filter: {title_list}")
            except Exception as e:
                logger.error(f"Error applying title filter: {str(e)}")
        
        # Log applied filters
        if applied_filters:
            logger.info(f"Applied filters: {', '.join(applied_filters)}")
        else:
            logger.info("No filters applied")
        
        # Count total results before pagination
        total_count = queryset.count()
        logger.debug(f"Found {total_count} results")
        
        # Apply pagination
        paginator = BookPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        # Serialize results
        if page is not None:
            serializer = BookSerializer(page, many=True)
            response = paginator.get_paginated_response(serializer.data)
            response.data['count_total'] = total_count
            
            page_num = request.query_params.get('page', 1)
            logger.info(f"Returned page {page_num} with {len(page)} results out of {total_count} total matches")
            
            return response
        
        # If no pagination
        serializer = BookSerializer(queryset, many=True)
        logger.info(f"Returned all {total_count} results without pagination")
        
        return Response({
            'count_total': total_count,
            'results': serializer.data
        })

class BookDetailView(APIView):
    """
    API endpoint to retrieve a specific book by ID.
    """
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Successfully retrieved book details"),
            404: openapi.Response(description="Book not found")
        }
    )
    def get(self, request, pk, format=None):
        logger.info(f"Book detail request received for book ID: {pk}")
        
        try:
            book = get_object_or_404(BooksBook.objects.prefetch_related(
                'authors', 
                'languages', 
                'subjects', 
                'bookshelves', 
                'booksformat_set'
            ), pk=pk)
            
            serializer = BookSerializer(book)
            
            logger.info(f"Retrieved book: '{book.title or f'Book {book.id}'}' (ID: {book.id}, Gutenberg ID: {book.gutenberg_id})")
            
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving book with ID {pk}: {str(e)}")
            raise
