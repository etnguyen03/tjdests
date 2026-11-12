#!/usr/bin/env python3
"""
Script to import user data from users_export.json back into the Django database.
- Saves original password to PasswordHash table
- Generates random password for user model
- Creates associated Decisions and TestScores
- Associates decisions with colleges using college hashes
"""

import os
import sys
import json
import hashlib
import secrets
import string
from pathlib import Path
from datetime import datetime

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent / 'tjdests'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tjdests.settings')
import django
django.setup()

from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError, transaction

from tjdests.apps.authentication.models import User, PasswordHash
from tjdests.apps.destinations.models import College, Decision, TestScore


def generate_college_hash(name, location):
    """Generate MD5 hash for college based on name and location."""
    combined = f"{name}|{location}"
    return hashlib.md5(combined.encode()).hexdigest()


def generate_random_password(length=12):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))


def find_college_by_hash(college_hash, colleges_cache=None):
    """Find college by its hash, with optional caching."""
    if colleges_cache is None:
        colleges_cache = {}
    
    if college_hash in colleges_cache:
        return colleges_cache[college_hash]
    
    # Try to find college by generating hashes for all colleges
    for college in College.objects.all():
        generated_hash = generate_college_hash(college.name, college.location)
        colleges_cache[generated_hash] = college
        if generated_hash == college_hash:
            return college
    
    return None


def import_users_from_json(json_file='users_export.json'):
    """Import users from JSON file into the database."""
    
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found!")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    
    imported_count = 0
    skipped_count = 0
    error_count = 0
    colleges_cache = {}
    
    print(f"Found {len(user_data)} users in {json_file}")
    
    for user_id, user_info in user_data.items():
        try:
            with transaction.atomic():
                username = user_info['username']
                
                # Check if user already exists
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': user_info['email'],
                        'first_name': user_info['first_name'],
                        'last_name': user_info['last_name'],
                        'nickname': user_info.get('nickname', ''),
                        'use_nickname': user_info.get('use_nickname', False),
                        'preferred_name': user_info.get('preferred_name', ''),
                        'graduation_year': user_info.get('graduation_year'),
                        'GPA': user_info.get('gpa'),
                        'is_student': user_info.get('is_student', False),
                        'is_staff': user_info.get('is_staff', False),
                        'is_superuser': user_info.get('is_superuser', False),
                        'is_banned': user_info.get('is_banned', False),
                        'accepted_terms': user_info.get('accepted_terms', False),
                        'publish_data': user_info.get('publish_data', False),
                        'use_additional_hashes': True,  # Enable additional hashes
                    }
                )
                
                if created:
                    # Generate random password for new user
                    random_password = generate_random_password()
                    user.set_password(random_password)
                    
                    # Only set biography if it's not empty after stripping
                    biography = user_info.get('biography', '').strip()
                    if biography:
                        user.biography = biography
                    
                    user.save()
                    print(f"Created new user: {username}")
                else:
                    # Update existing user
                    user.email = user_info['email']
                    user.first_name = user_info['first_name']
                    user.last_name = user_info['last_name']
                    user.nickname = user_info.get('nickname', '')
                    user.use_nickname = user_info.get('use_nickname', False)
                    user.preferred_name = user_info.get('preferred_name', '')
                    user.graduation_year = user_info.get('graduation_year')
                    user.GPA = user_info.get('gpa')
                    user.is_student = user_info.get('is_student', False)
                    user.is_staff = user_info.get('is_staff', False)
                    user.is_superuser = user_info.get('is_superuser', False)
                    user.is_banned = user_info.get('is_banned', False)
                    user.accepted_terms = user_info.get('accepted_terms', False)
                    user.publish_data = user_info.get('publish_data', False)
                    
                    # Only update biography if it's not empty after stripping
                    biography = user_info.get('biography', '').strip()
                    if biography:
                        user.biography = biography
                    
                    user.save()
                    print(f"Updated existing user: {username}")
                
                # Store original password in PasswordHash table (only for new users or if not exists)
                if user_info.get('password') and (created or not user.additional_hashes.exists()):
                    PasswordHash.objects.create(
                        user=user,
                        password_hash=user_info['password']
                    )
                
                # Import test scores
                for score_info in user_info.get('test_scores', []):
                    TestScore.objects.create(
                        user=user,
                        exam_type=score_info['exam_type'],
                        exam_score=score_info['exam_score'],
                        last_modified=parse_datetime(score_info['last_modified']) if score_info.get('last_modified') else None
                    )
                
                # Import decisions
                attending_decision = None
                for decision_info in user_info.get('decisions', []):
                    college_hash = decision_info['college_hash']
                    college = find_college_by_hash(college_hash, colleges_cache)
                    
                    if not college:
                        # Try to create college from the decision info
                        college_name = decision_info.get('college_name', f'Unknown College {college_hash[:8]}')
                        college_location = decision_info.get('college_location', 'Unknown Location')
                        
                        college, created = College.objects.get_or_create(
                            name=college_name,
                            location=college_location
                        )
                        
                        if created:
                            print(f"Created missing college: {college_name} - {college_location}")
                        
                        # Update cache
                        colleges_cache[college_hash] = college
                    
                    decision = Decision.objects.create(
                        user=user,
                        college=college,
                        decision_type=decision_info.get('decision_type'),
                        admission_status=decision_info['admission_status'],
                        last_modified=parse_datetime(decision_info['last_modified']) if decision_info.get('last_modified') else None
                    )
                    
                    # Check if this is the attending college
                    attending_college_hash = user_info.get('attending_college_hash')
                    if attending_college_hash and attending_college_hash == college_hash:
                        attending_decision = decision
                
                # Set attending decision if found
                if attending_decision:
                    user.attending_decision = attending_decision
                    user.save()
                
                action = "Created" if created else "Updated"
                print(f"{action} user: {username} (ID: {user.id}) with {len(user_info.get('decisions', []))} decisions and {len(user_info.get('test_scores', []))} test scores")
                imported_count += 1
                
        except IntegrityError as e:
            print(f"Integrity error importing {username}: {e}")
            error_count += 1
        except Exception as e:
            print(f"Unexpected error importing {username}: {e}")
            error_count += 1
    
    print(f"\nImport Summary:")
    print(f"  Processed: {imported_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total in file: {len(user_data)}")


def main():
    """Main function to import user data from JSON file."""
    try:
        json_file = 'users_export.json'
        if len(sys.argv) > 1:
            json_file = sys.argv[1]
        
        import_users_from_json(json_file)
        
    except Exception as e:
        print(f"Error during import: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()