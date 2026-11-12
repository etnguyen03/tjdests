#!/usr/bin/env python3
"""
Script to import college data from colleges_export.json back into the Django database.
Skips colleges that already exist in the database.
"""

import os
import sys
import json
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent / 'tjdests'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tjdests.settings')
import django
django.setup()

from tjdests.apps.destinations.models import College
from django.db import IntegrityError


def import_colleges_from_json(json_file='colleges_export.json'):
    """Import colleges from JSON file into the database."""
    
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found!")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        college_data = json.load(f)
    
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"Found {len(college_data)} colleges in {json_file}")
    
    for hash_key, college_info in college_data.items():
        name = college_info['name']
        location = college_info['location']
        
        try:
            # Check if college already exists
            existing_college = College.objects.filter(name=name, location=location).first()
            
            if existing_college:
                print(f"Skipping existing college: {name} - {location}")
                skipped_count += 1
                continue
            
            # Create new college
            new_college = College.objects.create(
                name=name,
                location=location
            )
            
            print(f"Imported: {name} - {location} (ID: {new_college.id})")
            imported_count += 1
            
        except IntegrityError as e:
            print(f"Error importing {name} - {location}: {e}")
            error_count += 1
        except Exception as e:
            print(f"Unexpected error importing {name} - {location}: {e}")
            error_count += 1
    
    print(f"\nImport Summary:")
    print(f"  Imported: {imported_count}")
    print(f"  Skipped (already exists): {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total processed: {len(college_data)}")


def main():
    """Main function to import college data from JSON file."""
    try:
        json_file = 'colleges_export.json'
        if len(sys.argv) > 1:
            json_file = sys.argv[1]
        
        import_colleges_from_json(json_file)
        
    except Exception as e:
        print(f"Error during import: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()