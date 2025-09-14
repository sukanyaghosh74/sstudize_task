"""
Demo script for the Personalized Roadmap Generation System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta
from data_models import StudentProfile, Subject
from ai_roadmap_generator import AIRoadmapGenerator
from monitoring_agents import MonitoringSystem

def run_demo():
    """Run a comprehensive demo of the system"""
    print("🎓 Personalized Roadmap Generation System - Demo")
    print("=" * 60)
    
    # Create a sample student
    print("\n📝 Creating Sample Student Profile...")
    student = StudentProfile(
        student_id="demo_student_001",
        name="Alex Johnson",
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
    
    print(f"✓ Student: {student.name}")
    print(f"  - Grade: {student.grade}")
    print(f"  - Learning Style: {student.learning_style}")
    print(f"  - Available Hours/Day: {student.available_hours_per_day}")
    print(f"  - Weak Subjects: {[s.value for s in student.get_weak_subjects()]}")
    
    # Generate personalized roadmap
    print("\n🤖 Generating AI-Powered Roadmap...")
    generator = AIRoadmapGenerator()
    roadmap = generator.generate_roadmap(student, duration_weeks=12)
    
    print(f"✓ Roadmap Generated!")
    print(f"  - Duration: {roadmap.duration_weeks} weeks")
    print(f"  - Weekly Plans: {len(roadmap.weekly_plans)}")
    print(f"  - Overall Goals: {len(roadmap.overall_goals)}")
    
    # Show roadmap goals
    print("\n🎯 Learning Goals:")
    for i, goal in enumerate(roadmap.overall_goals, 1):
        print(f"  {i}. {goal}")
    
    # Show first week plan
    if roadmap.weekly_plans:
        week1 = roadmap.weekly_plans[0]
        print(f"\n📅 Week 1 Study Plan:")
        print(f"  - Total Hours: {week1.total_hours:.1f}")
        print(f"  - Tasks: {len(week1.tasks)}")
        print(f"  - Subject Breakdown:")
        for subject, hours in week1.subject_breakdown.items():
            if hours > 0:
                print(f"    • {subject.value}: {hours:.1f} hours")
    
    # Set up monitoring
    print("\n📊 Setting up Monitoring System...")
    monitoring = MonitoringSystem()
    
    # Add some sample performance data
    from data_models import PerformanceMetric, StudyHabit
    student.performance_history = [
        PerformanceMetric(Subject.MATHEMATICS, 75, 100, datetime.now() - timedelta(days=7), "quiz"),
        PerformanceMetric(Subject.MATHEMATICS, 78, 100, datetime.now() - timedelta(days=3), "assignment"),
        PerformanceMetric(Subject.PHYSICS, 70, 100, datetime.now() - timedelta(days=5), "quiz"),
    ]
    
    student.study_habits = [
        StudyHabit(Subject.MATHEMATICS, 2.0, datetime.now() - timedelta(days=1), 7.0, []),
        StudyHabit(Subject.PHYSICS, 1.5, datetime.now() - timedelta(days=2), 8.0, ["phone"]),
    ]
    
    # Generate monitoring report
    report = monitoring.generate_weekly_report(student, roadmap, current_week=1)
    
    print(f"✓ Monitoring Report Generated!")
    print(f"  - Tasks Completed: {report.tasks_completed}")
    print(f"  - Tasks Pending: {report.tasks_pending}")
    print(f"  - Adherence Rate: {report.adherence_rate:.1%}")
    print(f"  - Irregularities: {len(report.irregularities)}")
    print(f"  - Recommendations: {len(report.recommendations)}")
    
    if report.irregularities:
        print(f"\n⚠️  Irregularities Detected:")
        for irregularity in report.irregularities[:3]:
            print(f"    • {irregularity}")
    
    if report.recommendations:
        print(f"\n💡 Recommendations:")
        for recommendation in report.recommendations[:3]:
            print(f"    • {recommendation}")
    
    # Show SWOT analysis
    if student.swot_analysis:
        print(f"\n🔍 SWOT Analysis:")
        print(f"  Strengths: {len(student.swot_analysis.strengths)} identified")
        print(f"  Weaknesses: {len(student.swot_analysis.weaknesses)} identified")
        print(f"  Opportunities: {len(student.swot_analysis.opportunities)} identified")
        print(f"  Threats: {len(student.swot_analysis.threats)} identified")
        
        if student.swot_analysis.strengths:
            print(f"    Top Strength: {student.swot_analysis.strengths[0]}")
        if student.swot_analysis.weaknesses:
            print(f"    Main Weakness: {student.swot_analysis.weaknesses[0]}")
    
    print(f"\n🎉 Demo Complete!")
    print(f"\nTo run the full web application:")
    print(f"  streamlit run app.py")
    
    return True

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
