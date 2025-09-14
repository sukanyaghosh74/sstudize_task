"""
AI-driven roadmap generation system with personalization algorithms
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import logging

from data_models import (
    StudentProfile, Roadmap, WeeklyPlan, StudyTask, Subject, 
    Priority, TaskStatus, LearningResource, ExamTrend, SWOTAnalysis
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIRoadmapGenerator:
    """
    AI-driven system for generating personalized study roadmaps
    """
    
    def __init__(self):
        self.exam_trends = self._load_exam_trends()
        self.learning_resources = self._load_learning_resources()
        self.subject_weights = {
            Subject.MATHEMATICS: 0.25,
            Subject.PHYSICS: 0.20,
            Subject.CHEMISTRY: 0.20,
            Subject.BIOLOGY: 0.15,
            Subject.ENGLISH: 0.20
        }
    
    def _load_exam_trends(self) -> List[ExamTrend]:
        """Load exam trend data from JSON file"""
        try:
            with open('data/exam_trends.json', 'r') as f:
                trends_data = json.load(f)
            return [ExamTrend(**trend) for trend in trends_data]
        except FileNotFoundError:
            logger.warning("Exam trends file not found, using default data")
            return self._get_default_exam_trends()
    
    def _load_learning_resources(self) -> List[LearningResource]:
        """Load learning resources from JSON file"""
        try:
            with open('data/learning_resources.json', 'r') as f:
                resources_data = json.load(f)
            return [LearningResource(**resource) for resource in resources_data]
        except FileNotFoundError:
            logger.warning("Learning resources file not found, using default data")
            return self._get_default_learning_resources()
    
    def _get_default_exam_trends(self) -> List[ExamTrend]:
        """Default exam trends data"""
        return [
            ExamTrend(Subject.MATHEMATICS, "Calculus", 15, 8.5, 25.0, datetime.now()),
            ExamTrend(Subject.MATHEMATICS, "Algebra", 12, 7.0, 20.0, datetime.now()),
            ExamTrend(Subject.PHYSICS, "Mechanics", 10, 8.0, 30.0, datetime.now()),
            ExamTrend(Subject.PHYSICS, "Thermodynamics", 8, 7.5, 20.0, datetime.now()),
            ExamTrend(Subject.CHEMISTRY, "Organic Chemistry", 12, 9.0, 35.0, datetime.now()),
            ExamTrend(Subject.CHEMISTRY, "Physical Chemistry", 9, 8.0, 25.0, datetime.now()),
        ]
    
    def _get_default_learning_resources(self) -> List[LearningResource]:
        """Default learning resources data"""
        return [
            LearningResource(
                "res_001", "Calculus Fundamentals", "video", Subject.MATHEMATICS,
                "Calculus", 7.0, 120, "https://example.com/calc-fundamentals",
                "Comprehensive video series on calculus basics"
            ),
            LearningResource(
                "res_002", "Physics Mechanics Problems", "practice_test", Subject.PHYSICS,
                "Mechanics", 8.0, 90, "https://example.com/mechanics-problems",
                "Practice problems with solutions"
            ),
            LearningResource(
                "res_003", "Organic Chemistry Textbook", "pdf", Subject.CHEMISTRY,
                "Organic Chemistry", 8.5, 180, "https://example.com/org-chem-textbook",
                "Complete textbook on organic chemistry"
            ),
        ]
    
    def generate_roadmap(self, student: StudentProfile, duration_weeks: int = 12) -> Roadmap:
        """
        Generate a personalized study roadmap for a student
        
        Args:
            student: Student profile with performance data
            duration_weeks: Duration of the roadmap in weeks
            
        Returns:
            Personalized roadmap object
        """
        logger.info(f"Generating roadmap for student {student.student_id}")
        
        # Analyze student's current state
        swot_analysis = self._perform_swot_analysis(student)
        student.swot_analysis = swot_analysis
        
        # Calculate subject priorities based on performance gaps
        subject_priorities = self._calculate_subject_priorities(student)
        
        # Generate weekly plans
        weekly_plans = []
        start_date = datetime.now()
        
        for week in range(duration_weeks):
            week_start = start_date + timedelta(weeks=week)
            week_end = week_start + timedelta(days=6)
            
            weekly_plan = self._generate_weekly_plan(
                student, week + 1, week_start, week_end, subject_priorities
            )
            weekly_plans.append(weekly_plan)
        
        # Create roadmap
        roadmap = Roadmap(
            roadmap_id=str(uuid.uuid4()),
            student_id=student.student_id,
            created_date=datetime.now(),
            duration_weeks=duration_weeks,
            weekly_plans=weekly_plans,
            overall_goals=self._generate_overall_goals(student, subject_priorities),
            success_metrics=self._calculate_success_metrics(student)
        )
        
        logger.info(f"Roadmap generated successfully with {len(weekly_plans)} weekly plans")
        return roadmap
    
    def _perform_swot_analysis(self, student: StudentProfile) -> SWOTAnalysis:
        """Perform SWOT analysis based on student's performance data"""
        
        # Analyze strengths and weaknesses from performance data
        strengths = []
        weaknesses = []
        
        for subject, score in student.current_scores.items():
            if score >= 80:
                strengths.append(f"Strong performance in {subject.value}")
            elif score < 60:
                weaknesses.append(f"Needs improvement in {subject.value}")
        
        # Add learning style strengths
        if student.learning_style == "visual":
            strengths.append("Visual learner - benefits from diagrams and charts")
        elif student.learning_style == "auditory":
            strengths.append("Auditory learner - benefits from discussions and lectures")
        
        # Identify opportunities
        opportunities = []
        for subject in student.get_weak_subjects():
            opportunities.append(f"Significant improvement potential in {subject.value}")
        
        # Identify threats
        threats = []
        if student.available_hours_per_day < 3:
            threats.append("Limited study time may impact progress")
        
        # Generate recommendations
        recommendations = []
        if weaknesses:
            recommendations.append("Focus on weak subjects with additional practice")
        if student.available_hours_per_day < 4:
            recommendations.append("Optimize study schedule for maximum efficiency")
        
        return SWOTAnalysis(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            recommendations=recommendations
        )
    
    def _calculate_subject_priorities(self, student: StudentProfile) -> Dict[Subject, float]:
        """Calculate priority scores for each subject based on performance gaps and exam trends"""
        priorities = {}
        
        for subject in Subject:
            # Base priority from performance gap
            current_score = student.current_scores.get(subject, 0)
            target_score = student.target_scores.get(subject, 100)
            performance_gap = target_score - current_score
            
            # Weight by exam trend frequency and difficulty
            trend_weight = 1.0
            for trend in self.exam_trends:
                if trend.subject == subject:
                    trend_weight = trend.frequency * trend.difficulty_level / 100
            
            # Calculate final priority
            priority = performance_gap * trend_weight * self.subject_weights.get(subject, 0.2)
            priorities[subject] = max(0, priority)
        
        # Normalize priorities to 0-1 range
        max_priority = max(priorities.values()) if priorities.values() else 1
        if max_priority > 0:
            priorities = {k: v / max_priority for k, v in priorities.items()}
        
        return priorities
    
    def _generate_weekly_plan(self, student: StudentProfile, week_number: int, 
                            start_date: datetime, end_date: datetime,
                            subject_priorities: Dict[Subject, float]) -> WeeklyPlan:
        """Generate a weekly study plan"""
        
        tasks = []
        total_hours = 0
        subject_breakdown = {subject: 0.0 for subject in Subject}
        
        # Calculate hours per subject based on priorities
        available_hours = student.available_hours_per_day * 7  # Weekly hours
        total_priority = sum(subject_priorities.values())
        
        if total_priority > 0:
            for subject, priority in subject_priorities.items():
                subject_hours = (priority / total_priority) * available_hours
                subject_breakdown[subject] = subject_hours
                
                # Generate tasks for this subject
                subject_tasks = self._generate_subject_tasks(
                    subject, subject_hours, week_number, start_date, end_date
                )
                tasks.extend(subject_tasks)
                total_hours += subject_hours
        
        return WeeklyPlan(
            week_number=week_number,
            start_date=start_date,
            end_date=end_date,
            tasks=tasks,
            total_hours=total_hours,
            subject_breakdown=subject_breakdown
        )
    
    def _generate_subject_tasks(self, subject: Subject, hours: float, week_number: int,
                              start_date: datetime, end_date: datetime) -> List[StudyTask]:
        """Generate study tasks for a specific subject"""
        tasks = []
        
        # Get relevant exam trends for this subject
        subject_trends = [t for t in self.exam_trends if t.subject == subject]
        
        # Get relevant learning resources
        subject_resources = [r for r in self.learning_resources if r.subject == subject]
        
        # Generate tasks based on trends and available time
        task_hours = 0
        task_id_counter = 1
        
        for trend in subject_trends[:3]:  # Focus on top 3 trends
            if task_hours >= hours:
                break
                
            # Calculate task duration (1-3 hours per task)
            task_duration = min(2.0, hours - task_hours)
            if task_duration < 0.5:
                break
            
            # Find relevant resources
            relevant_resources = [r for r in subject_resources 
                                if trend.topic.lower() in r.topic.lower()]
            
            # Create task
            task = StudyTask(
                task_id=f"task_{week_number}_{subject.value}_{task_id_counter}",
                title=f"Study {trend.topic} - {subject.value}",
                subject=subject,
                topic=trend.topic,
                description=f"Focus on {trend.topic} concepts and practice problems. "
                           f"Difficulty level: {trend.difficulty_level}/10",
                priority=Priority.HIGH if trend.frequency > 10 else Priority.MEDIUM,
                estimated_duration=int(task_duration * 60),  # Convert to minutes
                due_date=start_date + timedelta(days=task_id_counter * 2),
                resources=relevant_resources[:2]  # Limit to 2 resources per task
            )
            
            tasks.append(task)
            task_hours += task_duration
            task_id_counter += 1
        
        return tasks
    
    def _generate_overall_goals(self, student: StudentProfile, 
                              subject_priorities: Dict[Subject, float]) -> List[str]:
        """Generate overall learning goals for the roadmap"""
        goals = []
        
        # Performance improvement goals
        for subject, priority in subject_priorities.items():
            if priority > 0.5:  # High priority subjects
                current = student.current_scores.get(subject, 0)
                target = student.target_scores.get(subject, 100)
                goals.append(f"Improve {subject.value} score from {current} to {target}")
        
        # Study habit goals
        if student.available_hours_per_day < 4:
            goals.append("Establish consistent daily study routine")
        
        # Learning style goals
        if student.learning_style == "visual":
            goals.append("Utilize visual learning techniques for better retention")
        
        return goals
    
    def _calculate_success_metrics(self, student: StudentProfile) -> Dict[str, float]:
        """Calculate success metrics for the roadmap"""
        metrics = {}
        
        # Target score improvements
        for subject in Subject:
            current = student.current_scores.get(subject, 0)
            target = student.target_scores.get(subject, 100)
            improvement = target - current
            metrics[f"{subject.value}_improvement"] = improvement
        
        # Overall performance target
        current_avg = np.mean(list(student.current_scores.values()))
        target_avg = np.mean(list(student.target_scores.values()))
        metrics["overall_improvement"] = target_avg - current_avg
        
        return metrics
    
    def update_roadmap(self, roadmap: Roadmap, student: StudentProfile, 
                      performance_data: List[Dict]) -> Roadmap:
        """
        Update roadmap based on new performance data and feedback
        
        Args:
            roadmap: Current roadmap
            student: Updated student profile
            performance_data: New performance metrics
            
        Returns:
            Updated roadmap
        """
        logger.info(f"Updating roadmap {roadmap.roadmap_id}")
        
        # Analyze new performance data
        performance_improvements = self._analyze_performance_trends(performance_data)
        
        # Adjust subject priorities based on progress
        updated_priorities = self._recalculate_priorities(
            student, performance_improvements
        )
        
        # Update remaining weekly plans
        current_week = len([p for p in roadmap.weekly_plans 
                           if p.get_completion_rate() > 80])
        
        for i in range(current_week, len(roadmap.weekly_plans)):
            plan = roadmap.weekly_plans[i]
            updated_plan = self._regenerate_weekly_plan(
                student, plan, updated_priorities
            )
            roadmap.weekly_plans[i] = updated_plan
        
        roadmap.last_updated = datetime.now()
        logger.info("Roadmap updated successfully")
        
        return roadmap
    
    def _analyze_performance_trends(self, performance_data: List[Dict]) -> Dict[Subject, float]:
        """Analyze performance trends from new data"""
        trends = {}
        
        for data in performance_data:
            subject = Subject(data['subject'])
            score = data['score']
            max_score = data['max_score']
            percentage = (score / max_score) * 100
            
            if subject not in trends:
                trends[subject] = []
            trends[subject].append(percentage)
        
        # Calculate average improvement
        improvements = {}
        for subject, scores in trends.items():
            if len(scores) > 1:
                improvement = scores[-1] - scores[0]
                improvements[subject] = improvement
        
        return improvements
    
    def _recalculate_priorities(self, student: StudentProfile, 
                              performance_improvements: Dict[Subject, float]) -> Dict[Subject, float]:
        """Recalculate subject priorities based on performance improvements"""
        base_priorities = self._calculate_subject_priorities(student)
        
        # Adjust priorities based on improvements
        for subject, improvement in performance_improvements.items():
            if improvement > 0:
                # Reduce priority for subjects showing improvement
                base_priorities[subject] *= 0.8
            else:
                # Increase priority for subjects not improving
                base_priorities[subject] *= 1.2
        
        return base_priorities
    
    def _regenerate_weekly_plan(self, student: StudentProfile, plan: WeeklyPlan,
                              updated_priorities: Dict[Subject, float]) -> WeeklyPlan:
        """Regenerate a weekly plan with updated priorities"""
        # This would implement the same logic as _generate_weekly_plan
        # but with updated priorities
        return plan  # Simplified for now
