"""
Agent-based monitoring system for progress tracking and irregularity detection
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod

from data_models import (
    StudentProfile, Roadmap, WeeklyPlan, StudyTask, Subject, 
    TaskStatus, MonitoringReport, PerformanceMetric
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringAgent(ABC):
    """Abstract base class for monitoring agents"""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.is_active = True
    
    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """Analyze data and return insights"""
        pass
    
    @abstractmethod
    def detect_irregularities(self, data: Any) -> List[str]:
        """Detect irregularities in the data"""
        pass

class ProgressTrackingAgent(MonitoringAgent):
    """Agent for tracking student progress and task completion"""
    
    def __init__(self):
        super().__init__("progress_agent", "Progress Tracking Agent")
        self.thresholds = {
            'completion_rate': 0.8,  # 80% completion rate threshold
            'adherence_rate': 0.7,   # 70% adherence rate threshold
            'time_deviation': 0.3    # 30% time deviation threshold
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze progress data and return insights"""
        student_id = data.get('student_id')
        roadmap = data.get('roadmap')
        current_week = data.get('current_week', 1)
        
        if not roadmap or current_week > len(roadmap.weekly_plans):
            return {'error': 'Invalid roadmap or week data'}
        
        # Get current week plan
        current_plan = roadmap.weekly_plans[current_week - 1]
        
        # Calculate completion metrics
        total_tasks = len(current_plan.tasks)
        completed_tasks = len([t for t in current_plan.tasks if t.status == TaskStatus.COMPLETED])
        pending_tasks = len([t for t in current_plan.tasks if t.status == TaskStatus.PENDING])
        overdue_tasks = len([t for t in current_plan.tasks if t.status == TaskStatus.OVERDUE])
        
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        # Calculate adherence rate (tasks completed on time)
        on_time_tasks = len([t for t in current_plan.tasks 
                           if t.status == TaskStatus.COMPLETED and 
                           t.actual_duration and 
                           t.actual_duration <= t.estimated_duration * 1.2])
        adherence_rate = on_time_tasks / total_tasks if total_tasks > 0 else 0
        
        # Calculate time efficiency
        total_estimated = sum(t.estimated_duration for t in current_plan.tasks)
        total_actual = sum(t.actual_duration for t in current_plan.tasks 
                          if t.actual_duration is not None)
        time_efficiency = total_actual / total_estimated if total_estimated > 0 else 1
        
        return {
            'completion_rate': completion_rate,
            'adherence_rate': adherence_rate,
            'time_efficiency': time_efficiency,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'on_time_tasks': on_time_tasks
        }
    
    def detect_irregularities(self, data: Dict[str, Any]) -> List[str]:
        """Detect irregularities in progress data"""
        irregularities = []
        analysis = self.analyze(data)
        
        # Check completion rate
        if analysis['completion_rate'] < self.thresholds['completion_rate']:
            irregularities.append(
                f"Low completion rate: {analysis['completion_rate']:.1%} "
                f"(threshold: {self.thresholds['completion_rate']:.1%})"
            )
        
        # Check adherence rate
        if analysis['adherence_rate'] < self.thresholds['adherence_rate']:
            irregularities.append(
                f"Low adherence rate: {analysis['adherence_rate']:.1%} "
                f"(threshold: {self.thresholds['adherence_rate']:.1%})"
            )
        
        # Check time efficiency
        if analysis['time_efficiency'] > 1 + self.thresholds['time_deviation']:
            irregularities.append(
                f"Tasks taking longer than estimated: "
                f"{analysis['time_efficiency']:.1%} of estimated time"
            )
        
        # Check for overdue tasks
        if analysis['overdue_tasks'] > 0:
            irregularities.append(
                f"{analysis['overdue_tasks']} overdue tasks detected"
            )
        
        return irregularities

class PerformanceAnalysisAgent(MonitoringAgent):
    """Agent for analyzing academic performance trends"""
    
    def __init__(self):
        super().__init__("performance_agent", "Performance Analysis Agent")
        self.performance_thresholds = {
            'improvement_rate': 0.05,  # 5% improvement per week
            'consistency_threshold': 0.8,  # 80% consistency in scores
            'decline_threshold': -0.1  # 10% decline threshold
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance data and return insights"""
        student_id = data.get('student_id')
        performance_history = data.get('performance_history', [])
        current_week = data.get('current_week', 1)
        
        if not performance_history:
            return {'error': 'No performance history available'}
        
        # Group performance by subject
        subject_performance = {}
        for metric in performance_history:
            subject = metric.subject
            if subject not in subject_performance:
                subject_performance[subject] = []
            subject_performance[subject].append(metric.percentage)
        
        # Calculate trends for each subject
        subject_trends = {}
        for subject, scores in subject_performance.items():
            if len(scores) >= 2:
                # Calculate improvement rate
                recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
                earlier_avg = np.mean(scores[:-3]) if len(scores) >= 6 else scores[0]
                improvement_rate = (recent_avg - earlier_avg) / earlier_avg if earlier_avg > 0 else 0
                
                # Calculate consistency (coefficient of variation)
                consistency = 1 - (np.std(scores) / np.mean(scores)) if np.mean(scores) > 0 else 0
                
                subject_trends[subject] = {
                    'improvement_rate': improvement_rate,
                    'consistency': consistency,
                    'recent_avg': recent_avg,
                    'earlier_avg': earlier_avg,
                    'trend': 'improving' if improvement_rate > 0 else 'declining'
                }
        
        # Calculate overall performance metrics
        all_scores = [metric.percentage for metric in performance_history]
        overall_avg = np.mean(all_scores)
        overall_consistency = 1 - (np.std(all_scores) / np.mean(all_scores)) if np.mean(all_scores) > 0 else 0
        
        return {
            'subject_trends': subject_trends,
            'overall_avg': overall_avg,
            'overall_consistency': overall_consistency,
            'total_assessments': len(performance_history),
            'recent_performance': all_scores[-5:] if len(all_scores) >= 5 else all_scores
        }
    
    def detect_irregularities(self, data: Dict[str, Any]) -> List[str]:
        """Detect irregularities in performance data"""
        irregularities = []
        analysis = self.analyze(data)
        
        if 'error' in analysis:
            return [analysis['error']]
        
        # Check overall performance trends
        if analysis['overall_consistency'] < self.performance_thresholds['consistency_threshold']:
            irregularities.append(
                f"Inconsistent performance: {analysis['overall_consistency']:.1%} "
                f"consistency (threshold: {self.performance_thresholds['consistency_threshold']:.1%})"
            )
        
        # Check subject-specific trends
        for subject, trends in analysis['subject_trends'].items():
            if trends['improvement_rate'] < self.performance_thresholds['decline_threshold']:
                irregularities.append(
                    f"Performance declining in {subject.value}: "
                    f"{trends['improvement_rate']:.1%} change"
                )
            elif trends['consistency'] < self.performance_thresholds['consistency_threshold']:
                irregularities.append(
                    f"Inconsistent performance in {subject.value}: "
                    f"{trends['consistency']:.1%} consistency"
                )
        
        return irregularities

class StudyHabitAgent(MonitoringAgent):
    """Agent for monitoring study habits and patterns"""
    
    def __init__(self):
        super().__init__("habit_agent", "Study Habit Agent")
        self.habit_thresholds = {
            'min_daily_hours': 2.0,
            'max_daily_hours': 8.0,
            'consistency_threshold': 0.7,
            'focus_quality_threshold': 6.0
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze study habit data and return insights"""
        student_id = data.get('student_id')
        study_habits = data.get('study_habits', [])
        current_week = data.get('current_week', 1)
        
        if not study_habits:
            return {'error': 'No study habit data available'}
        
        # Filter recent habits (last 2 weeks)
        recent_habits = [h for h in study_habits 
                        if h.date >= datetime.now() - timedelta(weeks=2)]
        
        if not recent_habits:
            return {'error': 'No recent study habit data available'}
        
        # Calculate daily study hours
        daily_hours = {}
        for habit in recent_habits:
            date_key = habit.date.date()
            if date_key not in daily_hours:
                daily_hours[date_key] = 0
            daily_hours[date_key] += habit.hours_studied
        
        # Calculate habit metrics
        avg_daily_hours = np.mean(list(daily_hours.values()))
        study_consistency = len(daily_hours) / 14  # 14 days in 2 weeks
        
        # Calculate focus quality
        focus_scores = [h.focus_quality for h in recent_habits]
        avg_focus_quality = np.mean(focus_scores)
        
        # Calculate subject distribution
        subject_hours = {}
        for habit in recent_habits:
            subject = habit.subject
            if subject not in subject_hours:
                subject_hours[subject] = 0
            subject_hours[subject] += habit.hours_studied
        
        # Calculate distraction patterns
        all_distractions = []
        for habit in recent_habits:
            all_distractions.extend(habit.distractions)
        
        distraction_counts = {}
        for distraction in all_distractions:
            distraction_counts[distraction] = distraction_counts.get(distraction, 0) + 1
        
        return {
            'avg_daily_hours': avg_daily_hours,
            'study_consistency': study_consistency,
            'avg_focus_quality': avg_focus_quality,
            'subject_distribution': subject_hours,
            'common_distractions': distraction_counts,
            'study_days': len(daily_hours),
            'total_study_hours': sum(daily_hours.values())
        }
    
    def detect_irregularities(self, data: Dict[str, Any]) -> List[str]:
        """Detect irregularities in study habits"""
        irregularities = []
        analysis = self.analyze(data)
        
        if 'error' in analysis:
            return [analysis['error']]
        
        # Check daily study hours
        if analysis['avg_daily_hours'] < self.habit_thresholds['min_daily_hours']:
            irregularities.append(
                f"Low daily study hours: {analysis['avg_daily_hours']:.1f}h "
                f"(minimum: {self.habit_thresholds['min_daily_hours']}h)"
            )
        
        if analysis['avg_daily_hours'] > self.habit_thresholds['max_daily_hours']:
            irregularities.append(
                f"Excessive daily study hours: {analysis['avg_daily_hours']:.1f}h "
                f"(maximum: {self.habit_thresholds['max_daily_hours']}h)"
            )
        
        # Check study consistency
        if analysis['study_consistency'] < self.habit_thresholds['consistency_threshold']:
            irregularities.append(
                f"Inconsistent study schedule: {analysis['study_consistency']:.1%} "
                f"consistency (threshold: {self.habit_thresholds['consistency_threshold']:.1%})"
            )
        
        # Check focus quality
        if analysis['avg_focus_quality'] < self.habit_thresholds['focus_quality_threshold']:
            irregularities.append(
                f"Low focus quality: {analysis['avg_focus_quality']:.1f}/10 "
                f"(threshold: {self.habit_thresholds['focus_quality_threshold']}/10)"
            )
        
        # Check for excessive distractions
        if analysis['common_distractions']:
            most_common = max(analysis['common_distractions'].items(), key=lambda x: x[1])
            if most_common[1] > 5:  # More than 5 occurrences
                irregularities.append(
                    f"Frequent distraction: {most_common[0]} ({most_common[1]} times)"
                )
        
        return irregularities

class MonitoringSystem:
    """Main monitoring system that coordinates all agents"""
    
    def __init__(self):
        self.agents = {
            'progress': ProgressTrackingAgent(),
            'performance': PerformanceAnalysisAgent(),
            'habits': StudyHabitAgent()
        }
        self.reports = []
    
    def generate_weekly_report(self, student: StudentProfile, roadmap: Roadmap, 
                             current_week: int) -> MonitoringReport:
        """Generate comprehensive weekly monitoring report"""
        logger.info(f"Generating weekly report for student {student.student_id}, week {current_week}")
        
        # Prepare data for agents
        data = {
            'student_id': student.student_id,
            'roadmap': roadmap,
            'current_week': current_week,
            'performance_history': student.performance_history,
            'study_habits': student.study_habits
        }
        
        # Run all agents
        agent_results = {}
        all_irregularities = []
        
        for agent_name, agent in self.agents.items():
            if agent.is_active:
                try:
                    analysis = agent.analyze(data)
                    irregularities = agent.detect_irregularities(data)
                    
                    agent_results[agent_name] = {
                        'analysis': analysis,
                        'irregularities': irregularities
                    }
                    all_irregularities.extend(irregularities)
                except Exception as e:
                    logger.error(f"Error in {agent_name} agent: {str(e)}")
                    agent_results[agent_name] = {
                        'analysis': {'error': str(e)},
                        'irregularities': [f"Agent error: {str(e)}"]
                    }
        
        # Calculate overall metrics
        progress_data = agent_results.get('progress', {}).get('analysis', {})
        tasks_completed = progress_data.get('completed_tasks', 0)
        tasks_pending = progress_data.get('pending_tasks', 0)
        tasks_overdue = progress_data.get('overdue_tasks', 0)
        adherence_rate = progress_data.get('adherence_rate', 0)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(agent_results, all_irregularities)
        
        # Create monitoring report
        report = MonitoringReport(
            report_id=str(uuid.uuid4()),
            student_id=student.student_id,
            week_number=current_week,
            generated_date=datetime.now(),
            tasks_completed=tasks_completed,
            tasks_pending=tasks_pending,
            tasks_overdue=tasks_overdue,
            adherence_rate=adherence_rate,
            irregularities=all_irregularities,
            recommendations=recommendations,
            performance_trends=agent_results
        )
        
        self.reports.append(report)
        logger.info(f"Weekly report generated successfully with {len(all_irregularities)} irregularities")
        
        return report
    
    def _generate_recommendations(self, agent_results: Dict[str, Dict], 
                                irregularities: List[str]) -> List[str]:
        """Generate recommendations based on agent analysis"""
        recommendations = []
        
        # Progress-based recommendations
        progress_data = agent_results.get('progress', {}).get('analysis', {})
        if progress_data.get('completion_rate', 0) < 0.8:
            recommendations.append(
                "Consider breaking down large tasks into smaller, manageable chunks"
            )
        
        if progress_data.get('adherence_rate', 0) < 0.7:
            recommendations.append(
                "Improve time management by setting realistic deadlines and using timers"
            )
        
        # Performance-based recommendations
        performance_data = agent_results.get('performance', {}).get('analysis', {})
        if 'subject_trends' in performance_data:
            for subject, trends in performance_data['subject_trends'].items():
                if trends.get('improvement_rate', 0) < -0.1:
                    recommendations.append(
                        f"Focus on additional practice and review for {subject.value}"
                    )
        
        # Habit-based recommendations
        habit_data = agent_results.get('habits', {}).get('analysis', {})
        if habit_data.get('avg_daily_hours', 0) < 2:
            recommendations.append(
                "Increase daily study time gradually to meet learning goals"
            )
        
        if habit_data.get('avg_focus_quality', 0) < 6:
            recommendations.append(
                "Improve study environment and minimize distractions"
            )
        
        # General recommendations based on irregularities
        if len(irregularities) > 5:
            recommendations.append(
                "Consider scheduling a consultation with academic advisor"
            )
        
        return recommendations
    
    def get_agent_status(self) -> Dict[str, bool]:
        """Get status of all monitoring agents"""
        return {name: agent.is_active for name, agent in self.agents.items()}
    
    def toggle_agent(self, agent_name: str) -> bool:
        """Toggle agent active status"""
        if agent_name in self.agents:
            self.agents[agent_name].is_active = not self.agents[agent_name].is_active
            return self.agents[agent_name].is_active
        return False
    
    def get_recent_reports(self, student_id: str, limit: int = 5) -> List[MonitoringReport]:
        """Get recent monitoring reports for a student"""
        student_reports = [r for r in self.reports if r.student_id == student_id]
        return sorted(student_reports, key=lambda x: x.generated_date, reverse=True)[:limit]
