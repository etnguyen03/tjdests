#!/usr/bin/env python3
"""
Script to export college data from Django database to JSON format.
Each college is keyed by a unique identifier based on name and location.
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent / 'tjdests'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tjdests.settings')
import django
django.setup()

from tjdests.apps.destinations.models import College


def generate_unique_id(name, location):
    """Generate a unique identifier based on college name and location."""
    # Use MD5 hash of name and location
    combined = f"{name}|{location}"
    return hashlib.md5(combined.encode()).hexdigest()


def export_colleges_to_json():
    """Export all colleges from database to JSON format."""
    colleges = College.objects.all()
    
    college_data = {}
    
    for college in colleges:
        unique_id = generate_unique_id(college.name, college.location)
        
        college_data[unique_id] = {
            'id': college.id,
            'name': college.name,
            'location': college.location
        }
    
    return college_data


def main():
    """Main function to export college data and save to JSON file."""
    try:
        college_data = export_colleges_to_json()
        
        # Save to JSON file
        output_file = 'colleges_export.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(college_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(college_data)} colleges to {output_file}")
        
        # Print sample of the data
        if college_data:
            print("\nSample entries:")
            for i, (key, value) in enumerate(college_data.items()):
                if i >= 3:  # Show only first 3 entries
                    break
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error exporting colleges: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()