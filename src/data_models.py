"""
Data models for the Personalized Roadmap Generation System
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json

class Subject(Enum):
    PHYSICS = "Physics"
    CHEMISTRY = "Chemistry"
    MATHEMATICS = "Mathematics"
    BIOLOGY = "Biology"
    ENGLISH = "English"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    SKIPPED = "skipped"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    subject: Subject
    score: float
    max_score: float
    date: datetime
    test_type: str  # "quiz", "assignment", "exam", "practice"
    
    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100

@dataclass
class StudyHabit:
    subject: Subject
    hours_studied: float
    date: datetime
    focus_quality: float  # 1-10 scale
    distractions: List[str] = field(default_factory=list)

@dataclass
class SWOTAnalysis:
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    recommendations: List[str]

@dataclass
class ExamTrend:
    subject: Subject
    topic: str
    frequency: int
    difficulty_level: float  # 1-10 scale
    weightage: float  # percentage of total exam
    last_asked: datetime

@dataclass
class LearningResource:
    resource_id: str
    title: str
    resource_type: str  # "video", "pdf", "practice_test", "textbook"
    subject: Subject
    topic: str
    difficulty_level: float
    estimated_time: int  # minutes
    url: Optional[str] = None
    description: str = ""

@dataclass
class StudyTask:
    task_id: str
    title: str
    subject: Subject
    topic: str
    description: str
    priority: Priority
    estimated_duration: int  # minutes
    due_date: datetime
    status: TaskStatus = TaskStatus.PENDING
    resources: List[LearningResource] = field(default_factory=list)
    completion_percentage: float = 0.0
    actual_duration: Optional[int] = None
    notes: str = ""

@dataclass
class WeeklyPlan:
    week_number: int
    start_date: datetime
    end_date: datetime
    tasks: List[StudyTask]
    total_hours: float
    subject_breakdown: Dict[Subject, float]
    
    def get_completion_rate(self) -> float:
        if not self.tasks:
            return 0.0
        completed = sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)
        return (completed / len(self.tasks)) * 100

@dataclass
class StudentProfile:
    student_id: str
    name: str
    age: int
    grade: str
    target_scores: Dict[Subject, float]
    current_scores: Dict[Subject, float]
    performance_history: List[PerformanceMetric] = field(default_factory=list)
    study_habits: List[StudyHabit] = field(default_factory=list)
    swot_analysis: Optional[SWOTAnalysis] = None
    learning_style: str = "visual"  # visual, auditory, kinesthetic, reading
    available_hours_per_day: float = 4.0
    preferred_study_times: List[str] = field(default_factory=lambda: ["morning", "evening"])
    
    def get_weak_subjects(self, threshold: float = 70.0) -> List[Subject]:
        """Get subjects where current score is below threshold"""
        return [subject for subject, score in self.current_scores.items() 
                if score < threshold]
    
    def get_strong_subjects(self, threshold: float = 80.0) -> List[Subject]:
        """Get subjects where current score is above threshold"""
        return [subject for subject, score in self.current_scores.items() 
                if score >= threshold]

@dataclass
class Roadmap:
    roadmap_id: str
    student_id: str
    created_date: datetime
    duration_weeks: int
    weekly_plans: List[WeeklyPlan]
    overall_goals: List[str]
    success_metrics: Dict[str, float]
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_overall_progress(self) -> float:
        """Calculate overall progress across all weeks"""
        if not self.weekly_plans:
            return 0.0
        total_progress = sum(plan.get_completion_rate() for plan in self.weekly_plans)
        return total_progress / len(self.weekly_plans)

@dataclass
class TeacherFeedback:
    feedback_id: str
    teacher_id: str
    student_id: str
    roadmap_id: str
    feedback_type: str  # "roadmap_review", "progress_assessment", "recommendation"
    content: str
    priority: Priority
    created_date: datetime = field(default_factory=datetime.now)
    is_addressed: bool = False

@dataclass
class ParentFeedback:
    feedback_id: str
    parent_id: str
    student_id: str
    feedback_type: str  # "observation", "concern", "suggestion"
    content: str
    priority: Priority
    created_date: datetime = field(default_factory=datetime.now)
    is_addressed: bool = False

@dataclass
class MonitoringReport:
    report_id: str
    student_id: str
    week_number: int
    generated_date: datetime
    tasks_completed: int
    tasks_pending: int
    tasks_overdue: int
    adherence_rate: float
    irregularities: List[str]
    recommendations: List[str]
    performance_trends: Dict[str, Any]

class DataManager:
    """Manages data persistence and retrieval"""
    
    def __init__(self, db_path: str = "data/roadmap_system.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                grade TEXT,
                target_scores TEXT,
                current_scores TEXT,
                learning_style TEXT,
                available_hours_per_day REAL,
                preferred_study_times TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                subject TEXT,
                score REAL,
                max_score REAL,
                date TEXT,
                test_type TEXT,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmaps (
                roadmap_id TEXT PRIMARY KEY,
                student_id TEXT,
                created_date TEXT,
                duration_weeks INTEGER,
                overall_goals TEXT,
                success_metrics TEXT,
                last_updated TEXT,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_tasks (
                task_id TEXT PRIMARY KEY,
                roadmap_id TEXT,
                title TEXT,
                subject TEXT,
                topic TEXT,
                description TEXT,
                priority TEXT,
                estimated_duration INTEGER,
                due_date TEXT,
                status TEXT,
                completion_percentage REAL,
                actual_duration INTEGER,
                notes TEXT,
                FOREIGN KEY (roadmap_id) REFERENCES roadmaps (roadmap_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_feedback (
                feedback_id TEXT PRIMARY KEY,
                teacher_id TEXT,
                student_id TEXT,
                roadmap_id TEXT,
                feedback_type TEXT,
                content TEXT,
                priority TEXT,
                created_date TEXT,
                is_addressed BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parent_feedback (
                feedback_id TEXT PRIMARY KEY,
                parent_id TEXT,
                student_id TEXT,
                feedback_type TEXT,
                content TEXT,
                priority TEXT,
                created_date TEXT,
                is_addressed BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_student_profile(self, profile: StudentProfile):
        """Save student profile to database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO students 
            (student_id, name, age, grade, target_scores, current_scores, 
             learning_style, available_hours_per_day, preferred_study_times)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.student_id,
            profile.name,
            profile.age,
            profile.grade,
            json.dumps({s.value: v for s, v in profile.target_scores.items()}),
            json.dumps({s.value: v for s, v in profile.current_scores.items()}),
            profile.learning_style,
            profile.available_hours_per_day,
            json.dumps(profile.preferred_study_times)
        ))
        
        conn.commit()
        conn.close()
    
    def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """Retrieve student profile from database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Convert JSON strings back to dictionaries
        target_scores = {Subject(k): v for k, v in json.loads(row[4]).items()}
        current_scores = {Subject(k): v for k, v in json.loads(row[5]).items()}
        preferred_times = json.loads(row[8])
        
        profile = StudentProfile(
            student_id=row[0],
            name=row[1],
            age=row[2],
            grade=row[3],
            target_scores=target_scores,
            current_scores=current_scores,
            learning_style=row[6],
            available_hours_per_day=row[7],
            preferred_study_times=preferred_times
        )
        
        conn.close()
        return profile
