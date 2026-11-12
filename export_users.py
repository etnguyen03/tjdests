#!/usr/bin/env python3
"""
Script to export user data with their decisions and test scores from Django database to JSON format.
Uses MD5 hash for college identifiers matching export_colleges.py format.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent / 'tjdests'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tjdests.settings')
import django
django.setup()

from tjdests.apps.authentication.models import User
from tjdests.apps.destinations.models import Decision, TestScore, College


def generate_college_hash(name, location):
    """Generate MD5 hash for college based on name and location."""
    combined = f"{name}|{location}"
    return hashlib.md5(combined.encode()).hexdigest()


def export_users_to_json():
    """Export all users with their decisions and test scores to JSON format."""
    users = User.objects.all().prefetch_related('decision_set', 'testscore_set')
    
    user_data = {}
    
    for user in users:
        # Get user's decisions
        decisions = []
        for decision in user.decision_set.all():
            college_hash = generate_college_hash(decision.college.name, decision.college.location)
            decisions.append({
                'college_hash': college_hash,
                'college_name': decision.college.name,
                'college_location': decision.college.location,
                'decision_type': decision.decision_type,
                'admission_status': decision.admission_status,
                'last_modified': decision.last_modified.isoformat() if decision.last_modified else None
            })
        
        # Get user's test scores
        test_scores = []
        for score in user.testscore_set.all():
            test_scores.append({
                'exam_type': score.exam_type,
                'exam_score': score.exam_score,
                'last_modified': score.last_modified.isoformat() if score.last_modified else None
            })
        
        # Get attending college hash if it exists
        attending_college_hash = None
        if user.attending_decision and user.attending_decision.college:
            attending_college_hash = generate_college_hash(
                user.attending_decision.college.name,
                user.attending_decision.college.location
            )
        
        user_data[str(user.id)] = {
            'username': user.username,
            'password': user.password,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'nickname': getattr(user, 'nickname', '') or '',
            'use_nickname': getattr(user, 'use_nickname', False),
            'preferred_name': getattr(user, 'preferred_name', '') or '',
            'graduation_year': user.graduation_year,
            'gpa': float(user.GPA) if user.GPA else None,
            'is_student': user.is_student,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_banned': user.is_banned,
            'accepted_terms': user.accepted_terms,
            'publish_data': user.publish_data,
            'biography': getattr(user, 'biography', '') or '',
            'attending_college_hash': attending_college_hash,
            'decisions': decisions,
            'test_scores': test_scores,
            'last_modified': user.last_modified.isoformat() if user.last_modified else None
        }
    
    return user_data


def main():
    """Main function to export user data and save to JSON file."""
    try:
        user_data = export_users_to_json()
        
        # Save to JSON file
        output_file = 'users_export.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(user_data)} users to {output_file}")
        
        # Print summary statistics
        total_decisions = sum(len(user['decisions']) for user in user_data.values())
        total_test_scores = sum(len(user['test_scores']) for user in user_data.values())
        
        print(f"Total decisions: {total_decisions}")
        print(f"Total test scores: {total_test_scores}")
        
        # Print sample of the data
        if user_data:
            print("\nSample user entry:")
            first_user_id = next(iter(user_data))
            first_user = user_data[first_user_id]
            print(f"  User ID {first_user_id}:")
            print(f"    Name: {first_user['first_name']} {first_user['last_name']}")
            print(f"    Decisions: {len(first_user['decisions'])}")
            print(f"    Test Scores: {len(first_user['test_scores'])}")
        
    except Exception as e:
        print(f"Error exporting users: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()