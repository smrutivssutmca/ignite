# Gutenberg Books API

A RESTful API for searching and retrieving books from the Project Gutenberg catalog.

Access the running server in [https://ignite-production-d92d.up.railway.app/](https://ignite-production-d92d.up.railway.app/)

## Deliverables

- **Swagger Description**: Available at `/swagger/` or in the `swagger.yaml` file
- **API Implementation**: Publicly accessible API with endpoints for retrieving books
- **Source Code**: Well-structured Django project with modular components

## Features

- Retrieve books with various filter criteria:
  - Book ID (Gutenberg ID) - Multiple IDs supported with comma-separated values
  - Language - Multiple languages supported with comma-separated values (e.g., `en,fr`)
  - MIME-type - Filter by available formats with comma-separated values
  - Topic - Search in subjects and bookshelves with case-insensitive partial matching
  - Author - Case-insensitive partial matching with support for comma-separated values
  - Title - Case-insensitive partial matching with support for comma-separated values
- Pagination with 25 books per page
- Books returned in decreasing order of popularity (download count)
- Results in JSON format with proper pagination links
- Complete Swagger/OpenAPI documentation

## API Endpoints

### Base URL: `/api/books/`

### Query Parameters

- `gutenberg_id`: Filter by multiple Gutenberg IDs (comma-separated)
- `language`: Filter by language code(s) (comma-separated)
- `topic`: Filter by topic (subject or bookshelf) with case-insensitive partial matching (comma-separated)
- `mime_type`: Filter by MIME-type (comma-separated)
- `author`: Filter by author name with case-insensitive partial matching (comma-separated)
- `title`: Filter by title with case-insensitive partial matching (comma-separated)

## Implementation Details

- **Framework**: Django + Django REST Framework
- **Database**: PostgreSQL
- **Documentation**: Swagger/OpenAPI using drf-yasg
- **Environment Variables**: Configuration via dotenv
- **Containerization**: Docker support

## Setup

### Requirements

- Python 3.8+
- PostgreSQL

### Environment Variables

Create a `.env` file in the root directory with the following variables:
```
# Django settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS="localhost"

# Database settings
DBNAME=defaultdb
DBUSER=username
DBPASSWORD=password
DBHOST=hostname
DBPORT=5432
DBSSLMODE=require
```

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/smrutivssutmca/ignite.git
   cd ignite
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```
   python manage.py runserver
   ```

4. Access the API documentation at [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

### Database Introspection

The project includes a Django management command to introspect the PostgreSQL database dump and generate Django models:

```
python manage.py introspect_db [--output=OUTPUT_FILE] [--prefix=TABLE_PREFIX]
```

Options:
- `--output`: Specify the output file (default: book/models.py)
- `--prefix`: Specify the table prefix to look for (default: books)

## Docker Setup

1. Build the Docker image:
   ```
   docker build -t gutenberg-api .
   ```

2. Run the Docker container:
   ```
   docker run -p 8000:8000 --env-file .env gutenberg-api
   ```

## Example Queries

- Get all books: `/api/v1/books/`
- Get a specific book by ID: `/api/v1/books/1/`
- Filter books by language: `/api/v1/books/?language=en`
- Find children's books: `/api/v1/books/?topic=children`
- Filter by multiple authors: `/api/v1/books/?author=twain,dickens`
- Combine filters: `/api/v1/books/?language=en&topic=adventure&author=stevenson`

## Response Format

```json
{
  "count": 25,
  "count_total": 547,
  "next": "http://example.com/api/v1/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Pride and Prejudice",
      "gutenberg_id": 1342,
      "download_count": 42389,
      "authors": [
        {
          "name": "Jane Austen",
          "birth_year": 1775,
          "death_year": 1817
        }
      ],
      "languages": [
        {
          "code": "en"
        }
      ],
      "subjects": [
        {
          "name": "Love stories"
        },
        {
          "name": "England -- Fiction"
        }
      ],
      "bookshelves": [
        {
          "name": "Best Books Ever Listing"
        }
      ],
      "formats": [
        {
          "mime_type": "text/html",
          "url": "https://www.gutenberg.org/files/1342/1342-h/1342-h.htm"
        },
        {
          "mime_type": "application/epub+zip",
          "url": "https://www.gutenberg.org/ebooks/1342.epub.images"
        }
      ]
    }
    // More books...
  ]
}
```

## Project Structure

```
ignite/
├── book/                    # Django app containing the book models and API
│   ├── management/
│   │   └── commands/        # Custom Django management commands
│   │       └── introspect_db.py # DB introspection command
│   ├── models.py            # Django models for book data
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # URL routing
│   └── views.py             # API views
├── ignite/                  # Project settings
│   ├── settings.py          # Django settings
│   └── urls.py              # Main URL configuration
├── .env                     # Environment variables (not tracked in git)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
└── swagger.yaml             # OpenAPI/Swagger specification
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 