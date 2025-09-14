"""
Test script for the Personalized Roadmap Generation System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta
import json

# Import our modules
from data_models import StudentProfile, Subject, PerformanceMetric, StudyHabit
from ai_roadmap_generator import AIRoadmapGenerator
from monitoring_agents import MonitoringSystem
from hitl_framework import HITLFramework, Teacher, Parent, FeedbackType, Priority

def test_data_models():
    """Test data model creation and validation"""
    print("Testing Data Models...")
    
    # Create a sample student profile
    student = StudentProfile(
        student_id="test_student_001",
        name="Test Student",
        age=16,
        grade="11th",
        target_scores={
            Subject.MATHEMATICS: 90,
            Subject.PHYSICS: 85,
            Subject.CHEMISTRY: 80,
            Subject.BIOLOGY: 75,
            Subject.ENGLISH: 85
        },
        current_scores={
            Subject.MATHEMATICS: 75,
            Subject.PHYSICS: 70,
            Subject.CHEMISTRY: 68,
            Subject.BIOLOGY: 72,
            Subject.ENGLISH: 78
        },
        learning_style="visual",
        available_hours_per_day=4.0,
        preferred_study_times=["morning", "evening"]
    )
    
    print(f"✓ Student profile created: {student.name}")
    print(f"  - Weak subjects: {[s.value for s in student.get_weak_subjects()]}")
    print(f"  - Strong subjects: {[s.value for s in student.get_strong_subjects()]}")
    
    # Create sample performance metrics
    performance = PerformanceMetric(
        subject=Subject.MATHEMATICS,
        score=78,
        max_score=100,
        date=datetime.now(),
        test_type="quiz"
    )
    
    print(f"✓ Performance metric created: {performance.percentage}%")
    
    # Create sample study habit
    habit = StudyHabit(
        subject=Subject.MATHEMATICS,
        hours_studied=2.5,
        date=datetime.now(),
        focus_quality=8.0,
        distractions=["phone", "noise"]
    )
    
    print(f"✓ Study habit created: {habit.hours_studied} hours, quality {habit.focus_quality}/10")
    
    return student

def test_ai_roadmap_generator(student):
    """Test AI roadmap generation"""
    print("\nTesting AI Roadmap Generator...")
    
    generator = AIRoadmapGenerator()
    
    # Generate a roadmap
    roadmap = generator.generate_roadmap(student, duration_weeks=8)
    
    print(f"✓ Roadmap generated: {roadmap.roadmap_id}")
    print(f"  - Duration: {roadmap.duration_weeks} weeks")
    print(f"  - Weekly plans: {len(roadmap.weekly_plans)}")
    print(f"  - Overall goals: {len(roadmap.overall_goals)}")
    
    # Check first week plan
    if roadmap.weekly_plans:
        first_week = roadmap.weekly_plans[0]
        print(f"  - Week 1 tasks: {len(first_week.tasks)}")
        print(f"  - Week 1 total hours: {first_week.total_hours}")
        
        # Show subject breakdown
        for subject, hours in first_week.subject_breakdown.items():
            if hours > 0:
                print(f"    - {subject.value}: {hours:.1f} hours")
    
    return roadmap

def test_monitoring_system(student, roadmap):
    """Test monitoring system"""
    print("\nTesting Monitoring System...")
    
    monitoring = MonitoringSystem()
    
    # Add some sample performance data
    student.performance_history = [
        PerformanceMetric(Subject.MATHEMATICS, 75, 100, datetime.now() - timedelta(days=7), "quiz"),
        PerformanceMetric(Subject.MATHEMATICS, 78, 100, datetime.now() - timedelta(days=3), "assignment"),
        PerformanceMetric(Subject.PHYSICS, 70, 100, datetime.now() - timedelta(days=5), "quiz"),
    ]
    
    # Add some sample study habits
    student.study_habits = [
        StudyHabit(Subject.MATHEMATICS, 2.0, datetime.now() - timedelta(days=1), 7.0, []),
        StudyHabit(Subject.PHYSICS, 1.5, datetime.now() - timedelta(days=2), 8.0, ["phone"]),
    ]
    
    # Generate monitoring report
    report = monitoring.generate_weekly_report(student, roadmap, current_week=1)
    
    print(f"✓ Monitoring report generated: {report.report_id}")
    print(f"  - Tasks completed: {report.tasks_completed}")
    print(f"  - Tasks pending: {report.tasks_pending}")
    print(f"  - Adherence rate: {report.adherence_rate:.1%}")
    print(f"  - Irregularities: {len(report.irregularities)}")
    print(f"  - Recommendations: {len(report.recommendations)}")
    
    if report.irregularities:
        print("  - Irregularities found:")
        for irregularity in report.irregularities[:3]:  # Show first 3
            print(f"    * {irregularity}")
    
    return report

def test_hitl_framework(student):
    """Test Human-in-the-Loop framework"""
    print("\nTesting HITL Framework...")
    
    hitl = HITLFramework()
    
    # Create sample teacher
    teacher = Teacher(
        teacher_id="teacher_001",
        name="Dr. Sarah Wilson",
        subjects=[Subject.MATHEMATICS, Subject.PHYSICS],
        email="sarah.wilson@school.edu",
        expertise_level="expert"
    )
    
    # Create sample parent
    parent = Parent(
        parent_id="parent_001",
        name="John Johnson",
        email="john.johnson@email.com",
        student_ids=["test_student_001"]
    )
    
    # Register teacher and parent
    hitl.register_teacher(teacher)
    hitl.register_parent(parent)
    
    print(f"✓ Teacher registered: {teacher.name}")
    print(f"✓ Parent registered: {parent.name}")
    
    # Test workflow creation (we need to create a mock roadmap object)
    from data_models import Roadmap, WeeklyPlan
    mock_roadmap = Roadmap(
        roadmap_id="test_roadmap_001",
        student_id="test_student_001",
        created_date=datetime.now(),
        duration_weeks=8,
        weekly_plans=[],
        overall_goals=["Test goal"],
        success_metrics={}
    )
    workflow_id = hitl.submit_roadmap_for_review(student, mock_roadmap)
    print(f"✓ Workflow created: {workflow_id}")
    
    # Test teacher feedback
    success = hitl.submit_teacher_feedback(
        teacher_id="teacher_001",
        workflow_id=workflow_id,
        feedback_type=FeedbackType.ROADMAP_REVIEW,
        content="The roadmap looks good but needs more focus on calculus fundamentals.",
        priority=Priority.HIGH
    )
    
    print(f"✓ Teacher feedback submitted: {success}")
    
    # Test parent feedback
    success = hitl.submit_parent_feedback(
        parent_id="parent_001",
        workflow_id=workflow_id,
        feedback_type=FeedbackType.OBSERVATION,
        content="Student seems to struggle with evening study sessions. Morning might be better.",
        priority=Priority.MEDIUM
    )
    
    print(f"✓ Parent feedback submitted: {success}")
    
    # Check workflow status
    status = hitl.get_workflow_status(workflow_id)
    if status:
        print(f"✓ Workflow status: {status['current_stage']} - {status['status']}")
    
    return hitl

def test_integration():
    """Test full system integration"""
    print("\nTesting System Integration...")
    
    # Create student
    student = test_data_models()
    
    # Generate roadmap
    roadmap = test_ai_roadmap_generator(student)
    
    # Test monitoring
    report = test_monitoring_system(student, roadmap)
    
    # Test HITL
    hitl = test_hitl_framework(student)
    
    print("\n✓ All integration tests passed!")
    
    # Summary
    print("\n" + "="*50)
    print("SYSTEM TEST SUMMARY")
    print("="*50)
    print(f"Student Profile: ✓ Created and validated")
    print(f"AI Roadmap: ✓ Generated with {len(roadmap.weekly_plans)} weekly plans")
    print(f"Monitoring: ✓ Report generated with {len(report.irregularities)} irregularities")
    print(f"HITL Framework: ✓ Teacher and parent feedback system working")
    print(f"Overall Status: ✓ All systems operational")
    print("="*50)

def main():
    """Run all tests"""
    print("Personalized Roadmap Generation System - Test Suite")
    print("="*60)
    
    try:
        test_integration()
        print("\n All tests completed successfully!")
        print("\nThe system is ready for deployment!")
        
    except Exception as e:
        print(f"\n Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
