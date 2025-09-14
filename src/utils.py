"""
Utility functions for the Personalized Roadmap Generation System
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from data_models import (
    StudentProfile, Subject, PerformanceMetric, StudyHabit, 
    LearningResource, ExamTrend, Teacher, Parent
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample data for demonstration purposes"""
    
    # Sample exam trends
    exam_trends = [
        {
            "subject": "Mathematics",
            "topic": "Calculus",
            "frequency": 15,
            "difficulty_level": 8.5,
            "weightage": 25.0,
            "last_asked": datetime.now().isoformat()
        },
        {
            "subject": "Mathematics", 
            "topic": "Algebra",
            "frequency": 12,
            "difficulty_level": 7.0,
            "weightage": 20.0,
            "last_asked": datetime.now().isoformat()
        },
        {
            "subject": "Physics",
            "topic": "Mechanics",
            "frequency": 10,
            "difficulty_level": 8.0,
            "weightage": 30.0,
            "last_asked": datetime.now().isoformat()
        },
        {
            "subject": "Physics",
            "topic": "Thermodynamics", 
            "frequency": 8,
            "difficulty_level": 7.5,
            "weightage": 20.0,
            "last_asked": datetime.now().isoformat()
        },
        {
            "subject": "Chemistry",
            "topic": "Organic Chemistry",
            "frequency": 12,
            "difficulty_level": 9.0,
            "weightage": 35.0,
            "last_asked": datetime.now().isoformat()
        },
        {
            "subject": "Chemistry",
            "topic": "Physical Chemistry",
            "frequency": 9,
            "difficulty_level": 8.0,
            "weightage": 25.0,
            "last_asked": datetime.now().isoformat()
        }
    ]
    
    # Sample learning resources
    learning_resources = [
        {
            "resource_id": "res_001",
            "title": "Calculus Fundamentals Video Series",
            "resource_type": "video",
            "subject": "Mathematics",
            "topic": "Calculus",
            "difficulty_level": 7.0,
            "estimated_time": 120,
            "url": "https://example.com/calc-fundamentals",
            "description": "Comprehensive video series covering calculus basics"
        },
        {
            "resource_id": "res_002",
            "title": "Physics Mechanics Practice Problems",
            "resource_type": "practice_test",
            "subject": "Physics",
            "topic": "Mechanics",
            "difficulty_level": 8.0,
            "estimated_time": 90,
            "url": "https://example.com/mechanics-problems",
            "description": "Practice problems with detailed solutions"
        },
        {
            "resource_id": "res_003",
            "title": "Organic Chemistry Textbook",
            "resource_type": "pdf",
            "subject": "Chemistry",
            "topic": "Organic Chemistry",
            "difficulty_level": 8.5,
            "estimated_time": 180,
            "url": "https://example.com/org-chem-textbook",
            "description": "Complete textbook on organic chemistry concepts"
        },
        {
            "resource_id": "res_004",
            "title": "Biology Cell Structure Interactive",
            "resource_type": "interactive",
            "subject": "Biology",
            "topic": "Cell Biology",
            "difficulty_level": 6.0,
            "estimated_time": 60,
            "url": "https://example.com/cell-structure",
            "description": "Interactive 3D model of cell structure"
        },
        {
            "resource_id": "res_005",
            "title": "English Essay Writing Guide",
            "resource_type": "pdf",
            "subject": "English",
            "topic": "Essay Writing",
            "difficulty_level": 6.5,
            "estimated_time": 45,
            "url": "https://example.com/essay-guide",
            "description": "Step-by-step guide for essay writing"
        }
    ]
    
    # Sample student profiles
    students = [
        {
            "student_id": "student_001",
            "name": "Alice Johnson",
            "age": 16,
            "grade": "11th",
            "target_scores": {
                "Mathematics": 90,
                "Physics": 85,
                "Chemistry": 80,
                "Biology": 75,
                "English": 85
            },
            "current_scores": {
                "Mathematics": 75,
                "Physics": 70,
                "Chemistry": 68,
                "Biology": 72,
                "English": 78
            },
            "learning_style": "visual",
            "available_hours_per_day": 4.0,
            "preferred_study_times": ["morning", "evening"]
        },
        {
            "student_id": "student_002",
            "name": "Bob Smith",
            "age": 17,
            "grade": "12th",
            "target_scores": {
                "Mathematics": 95,
                "Physics": 90,
                "Chemistry": 85,
                "Biology": 80,
                "English": 90
            },
            "current_scores": {
                "Mathematics": 85,
                "Physics": 80,
                "Chemistry": 75,
                "Biology": 78,
                "English": 82
            },
            "learning_style": "auditory",
            "available_hours_per_day": 5.5,
            "preferred_study_times": ["afternoon", "evening"]
        },
        {
            "student_id": "student_003",
            "name": "Carol Davis",
            "age": 15,
            "grade": "10th",
            "target_scores": {
                "Mathematics": 85,
                "Physics": 80,
                "Chemistry": 75,
                "Biology": 70,
                "English": 80
            },
            "current_scores": {
                "Mathematics": 70,
                "Physics": 65,
                "Chemistry": 68,
                "Biology": 72,
                "English": 75
            },
            "learning_style": "kinesthetic",
            "available_hours_per_day": 3.5,
            "preferred_study_times": ["morning"]
        }
    ]
    
    # Sample teachers
    teachers = [
        {
            "teacher_id": "teacher_001",
            "name": "Dr. Sarah Wilson",
            "subjects": ["Mathematics", "Physics"],
            "email": "sarah.wilson@school.edu",
            "expertise_level": "expert",
            "max_students": 50,
            "is_active": True
        },
        {
            "teacher_id": "teacher_002",
            "name": "Prof. Michael Brown",
            "subjects": ["Chemistry", "Biology"],
            "email": "michael.brown@school.edu",
            "expertise_level": "expert",
            "max_students": 45,
            "is_active": True
        },
        {
            "teacher_id": "teacher_003",
            "name": "Ms. Jennifer Lee",
            "subjects": ["English"],
            "email": "jennifer.lee@school.edu",
            "expertise_level": "intermediate",
            "max_students": 40,
            "is_active": True
        }
    ]
    
    # Sample parents
    parents = [
        {
            "parent_id": "parent_001",
            "name": "John Johnson",
            "email": "john.johnson@email.com",
            "student_ids": ["student_001"],
            "notification_preferences": {
                "daily_updates": False,
                "weekly_reports": True,
                "urgent_alerts": True,
                "performance_changes": True
            },
            "is_active": True
        },
        {
            "parent_id": "parent_002",
            "name": "Mary Smith",
            "email": "mary.smith@email.com",
            "student_ids": ["student_002"],
            "notification_preferences": {
                "daily_updates": True,
                "weekly_reports": True,
                "urgent_alerts": True,
                "performance_changes": True
            },
            "is_active": True
        },
        {
            "parent_id": "parent_003",
            "name": "Robert Davis",
            "email": "robert.davis@email.com",
            "student_ids": ["student_003"],
            "notification_preferences": {
                "daily_updates": False,
                "weekly_reports": True,
                "urgent_alerts": True,
                "performance_changes": False
            },
            "is_active": True
        }
    ]
    
    return {
        "exam_trends": exam_trends,
        "learning_resources": learning_resources,
        "students": students,
        "teachers": teachers,
        "parents": parents
    }

def save_sample_data():
    """Save sample data to JSON files"""
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    sample_data = create_sample_data()
    
    # Save each data type to separate files
    with open("data/exam_trends.json", "w") as f:
        json.dump(sample_data["exam_trends"], f, indent=2)
    
    with open("data/learning_resources.json", "w") as f:
        json.dump(sample_data["learning_resources"], f, indent=2)
    
    with open("data/students.json", "w") as f:
        json.dump(sample_data["students"], f, indent=2)
    
    with open("data/teachers.json", "w") as f:
        json.dump(sample_data["teachers"], f, indent=2)
    
    with open("data/parents.json", "w") as f:
        json.dump(sample_data["parents"], f, indent=2)
    
    logger.info("Sample data saved successfully")

def load_sample_data():
    """Load sample data from JSON files"""
    try:
        with open("data/exam_trends.json", "r") as f:
            exam_trends = json.load(f)
        
        with open("data/learning_resources.json", "r") as f:
            learning_resources = json.load(f)
        
        with open("data/students.json", "r") as f:
            students = json.load(f)
        
        with open("data/teachers.json", "r") as f:
            teachers = json.load(f)
        
        with open("data/parents.json", "r") as f:
            parents = json.load(f)
        
        return {
            "exam_trends": exam_trends,
            "learning_resources": learning_resources,
            "students": students,
            "teachers": teachers,
            "parents": parents
        }
    
    except FileNotFoundError as e:
        logger.warning(f"Data file not found: {e}")
        return None

def create_sample_performance_data(student_id: str, weeks: int = 8) -> List[Dict]:
    """Create sample performance data for a student"""
    import random
    
    performance_data = []
    subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "English"]
    test_types = ["quiz", "assignment", "exam", "practice"]
    
    for week in range(weeks):
        for subject in subjects:
            # Create 1-2 performance metrics per subject per week
            num_tests = random.randint(1, 2)
            for _ in range(num_tests):
                score = random.randint(60, 95)
                max_score = 100
                test_type = random.choice(test_types)
                
                performance_data.append({
                    "student_id": student_id,
                    "subject": subject,
                    "score": score,
                    "max_score": max_score,
                    "test_type": test_type,
                    "date": (datetime.now() - timedelta(weeks=weeks-week)).isoformat()
                })
    
    return performance_data

def create_sample_study_habits(student_id: str, weeks: int = 8) -> List[Dict]:
    """Create sample study habit data for a student"""
    import random
    
    study_habits = []
    subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "English"]
    distractions = ["phone", "social_media", "noise", "family", "friends", "tv"]
    
    for week in range(weeks):
        for day in range(7):
            # Create 1-3 study sessions per day
            num_sessions = random.randint(1, 3)
            for _ in range(num_sessions):
                subject = random.choice(subjects)
                hours = random.uniform(0.5, 3.0)
                focus_quality = random.randint(4, 10)
                session_distractions = random.sample(distractions, random.randint(0, 2))
                
                study_habits.append({
                    "student_id": student_id,
                    "subject": subject,
                    "hours_studied": round(hours, 1),
                    "focus_quality": focus_quality,
                    "distractions": session_distractions,
                    "date": (datetime.now() - timedelta(weeks=weeks-week, days=6-day)).isoformat()
                })
    
    return study_habits

def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M")

def calculate_time_remaining(due_date: datetime) -> str:
    """Calculate time remaining until due date"""
    now = datetime.now()
    if due_date > now:
        delta = due_date - now
        if delta.days > 0:
            return f"{delta.days} days remaining"
        else:
            hours = delta.seconds // 3600
            return f"{hours} hours remaining"
    else:
        return "Overdue"

def get_performance_trend(scores: List[float]) -> str:
    """Get performance trend from a list of scores"""
    if len(scores) < 2:
        return "Insufficient data"
    
    recent_avg = sum(scores[-3:]) / len(scores[-3:])
    earlier_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]
    
    if recent_avg > earlier_avg + 2:
        return "Improving"
    elif recent_avg < earlier_avg - 2:
        return "Declining"
    else:
        return "Stable"

def validate_student_data(student_data: Dict) -> List[str]:
    """Validate student data and return list of errors"""
    errors = []
    
    required_fields = ["name", "age", "grade", "target_scores", "current_scores"]
    for field in required_fields:
        if field not in student_data:
            errors.append(f"Missing required field: {field}")
    
    if "age" in student_data and (student_data["age"] < 10 or student_data["age"] > 25):
        errors.append("Age must be between 10 and 25")
    
    if "target_scores" in student_data:
        for subject, score in student_data["target_scores"].items():
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                errors.append(f"Invalid target score for {subject}: {score}")
    
    if "current_scores" in student_data:
        for subject, score in student_data["current_scores"].items():
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                errors.append(f"Invalid current score for {subject}: {score}")
    
    return errors

def export_data_to_csv(data: List[Dict], filename: str):
    """Export data to CSV file"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    logger.info(f"Data exported to {filename}")

def import_data_from_csv(filename: str) -> List[Dict]:
    """Import data from CSV file"""
    import pandas as pd
    
    df = pd.read_csv(filename)
    return df.to_dict('records')

def generate_report_summary(report_data: Dict) -> str:
    """Generate a summary of monitoring report"""
    summary = f"""
    Monitoring Report Summary:
    - Tasks Completed: {report_data.get('tasks_completed', 0)}
    - Tasks Pending: {report_data.get('tasks_pending', 0)}
    - Tasks Overdue: {report_data.get('tasks_overdue', 0)}
    - Adherence Rate: {report_data.get('adherence_rate', 0):.1%}
    - Irregularities: {len(report_data.get('irregularities', []))}
    - Recommendations: {len(report_data.get('recommendations', []))}
    """
    return summary.strip()
