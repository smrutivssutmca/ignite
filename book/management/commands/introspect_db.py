import psycopg2
from django.core.management.base import BaseCommand
from django.conf import settings

# SQL type to Django field type mapping
type_mapping = {
    'integer': 'models.IntegerField()',
    'bigint': 'models.BigIntegerField()',
    'smallint': 'models.SmallIntegerField()',
    'varchar': 'models.CharField(max_length={})',
    'text': 'models.TextField()',
    'boolean': 'models.BooleanField()',
    'date': 'models.DateField()',
    'time': 'models.TimeField()',
    'timestamp': 'models.DateTimeField()',
    'timestamptz': 'models.DateTimeField()',
    'double precision': 'models.FloatField()',
    'real': 'models.FloatField()',
    'numeric': 'models.DecimalField(max_digits=19, decimal_places=10)',
    'uuid': 'models.UUIDField()',
    'json': 'models.JSONField()',
    'jsonb': 'models.JSONField()',
}

class Command(BaseCommand):
    help = 'Introspect database and generate Django models for Project Gutenberg tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='book/models.py',
            help='Output file to write the models to',
        )
        parser.add_argument(
            '--prefix',
            default='books',
            help='Prefix for tables to introspect',
        )

    def snake_to_camel_case(self, snake_str):
        """Convert snake_case to CamelCase for model names"""
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)

    def get_django_field(self, col_name, data_type, char_length, is_nullable, is_primary_key, default):
        """Convert PostgreSQL column details to Django model field"""
        django_field = None
        
        # Handle primary key
        if is_primary_key:
            return f"models.AutoField(primary_key=True)"
        
        # Map data types
        if data_type in type_mapping:
            django_field = type_mapping[data_type]
            if data_type == 'varchar':
                django_field = django_field.format(char_length)
        else:
            django_field = "models.TextField()"  # Default for unknown types
        
        # Add null=True for nullable fields
        if is_nullable == 'YES' and not is_primary_key:
            django_field = django_field.replace(')', ', null=True)')
        
        # Add default if specified
        if default and default not in ('NULL', None) and not is_primary_key:
            # Handle boolean defaults
            if data_type == 'boolean':
                if default.lower() in ('true', 't', 'yes', 'y', '1'):
                    default_val = 'True'
                else:
                    default_val = 'False'
                django_field = django_field.replace(')', f', default={default_val})')
            # Handle numeric defaults
            elif data_type in ('integer', 'bigint', 'smallint', 'double precision', 'real', 'numeric'):
                django_field = django_field.replace(')', f', default={default})')
            # Handle string defaults
            else:
                django_field = django_field.replace(')', f", default='{default}')")
        
        return django_field

    def generate_models(self, conn, prefix):
        cursor = conn.cursor()
        
        # Get list of tables that start with the specified prefix
        cursor.execute(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '{prefix}%'
        """)
        
        tables = cursor.fetchall()
        
        if not tables:
            self.stdout.write(self.style.WARNING(f"No tables starting with '{prefix}' found in the database."))
            return None
        
        models_code = "from django.db import models\n\n"
        
        for table in tables:
            table_name = table[0]
            class_name = self.snake_to_camel_case(table_name)
            
            # Get column information
            cursor.execute("""
                SELECT 
                    c.column_name,
                    c.data_type,
                    c.character_maximum_length,
                    c.is_nullable,
                    c.column_default,
                    CASE WHEN pk.constraint_name IS NOT NULL THEN 'YES' ELSE 'NO' END AS is_primary_key
                FROM information_schema.columns c
                LEFT JOIN (
                    SELECT ku.table_schema, ku.table_name, ku.column_name, tc.constraint_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage ku ON tc.constraint_name = ku.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                ) pk 
                ON c.table_schema = pk.table_schema 
                AND c.table_name = pk.table_name 
                AND c.column_name = pk.column_name
                WHERE c.table_name = %s
                AND c.table_schema = 'public'
                ORDER BY c.ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            # Create class header with docstring
            models_code += f"class {class_name}(models.Model):\n"
            models_code += f'    """\n'
            models_code += f'    Model for {table_name} table from Project Gutenberg database.\n'
            models_code += f'    """\n'
            
            for col in columns:
                col_name = col[0]
                data_type = col[1]
                char_length = col[2]
                is_nullable = col[3]
                default = col[4]
                is_primary_key = col[5]
                
                field = self.get_django_field(col_name, data_type, char_length, is_nullable, is_primary_key == 'YES', default)
                models_code += f"    {col_name} = {field}\n"
            
            models_code += f"\n    class Meta:\n        db_table = '{table_name}'\n\n"
            # Add __str__ method for readability
            if any(col[0] in ('name', 'title') for col in columns):
                str_field = next((col[0] for col in columns if col[0] in ('name', 'title')), None)
                if str_field:
                    models_code += f"    def __str__(self):\n"
                    models_code += f"        return self.{str_field} or f\"{class_name} {{{self.id}}}\"\n\n"
        
        cursor.close()
        return models_code

    def handle(self, *args, **options):
        output_file = options['output']
        table_prefix = options['prefix']
        
        # Get database settings from Django settings
        db_settings = settings.DATABASES['default']
        
        try:
            # Connect to the database
            conn = psycopg2.connect(
                dbname=db_settings['NAME'],
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                host=db_settings['HOST'],
                port=db_settings['PORT'],
                sslmode=db_settings['OPTIONS'].get('sslmode')
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully connected to the database.'))
            
            # Generate models
            models_code = self.generate_models(conn, table_prefix)
            
            if models_code:
                # Write to models.py
                with open(output_file, 'w') as f:
                    f.write(models_code)
                self.stdout.write(self.style.SUCCESS(f'Django models have been generated in {output_file}'))
            else:
                self.stdout.write(self.style.WARNING('No models were generated'))
            
            # Close the database connection
            conn.close()
            
        except psycopg2.Error as e:
            self.stdout.write(self.style.ERROR(f'Error connecting to the database: {e}'))
            raise 