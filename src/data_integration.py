"""
Real data sources integration for school databases and external systems
"""

import requests
import pandas as pd
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import sqlite3
import os
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SchoolDataConfig:
    """Configuration for school data sources"""
    school_id: str
    api_base_url: str
    api_key: str
    database_connection: str
    sync_interval_hours: int = 24
    last_sync: Optional[datetime] = None

@dataclass
class StudentRecord:
    """Student record from school database"""
    student_id: str
    first_name: str
    last_name: str
    email: str
    grade: str
    enrollment_date: datetime
    subjects: List[str]
    performance_data: Dict[str, Any]
    attendance_data: Dict[str, Any]

@dataclass
class TeacherRecord:
    """Teacher record from school database"""
    teacher_id: str
    first_name: str
    last_name: str
    email: str
    subjects: List[str]
    department: str
    hire_date: datetime
    qualifications: List[str]

@dataclass
class PerformanceRecord:
    """Performance record from school system"""
    student_id: str
    subject: str
    assessment_type: str
    score: float
    max_score: float
    date: datetime
    teacher_id: str
    comments: Optional[str] = None

class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to data source"""
        pass
    
    @abstractmethod
    def fetch_students(self) -> List[StudentRecord]:
        """Fetch student data"""
        pass
    
    @abstractmethod
    def fetch_teachers(self) -> List[TeacherRecord]:
        """Fetch teacher data"""
        pass
    
    @abstractmethod
    def fetch_performance_data(self, student_id: str = None) -> List[PerformanceRecord]:
        """Fetch performance data"""
        pass

class SchoolDatabaseConnector(DataSource):
    """Connector for school database systems"""
    
    def __init__(self, config: SchoolDataConfig):
        self.config = config
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to school database"""
        try:
            # This would connect to actual school database
            # For demo, we'll use SQLite as a proxy
            self.connection = sqlite3.connect(self.config.database_connection)
            logger.info(f"Connected to school database: {self.config.school_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to school database: {e}")
            return False
    
    def fetch_students(self) -> List[StudentRecord]:
        """Fetch student data from school database"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            # Query student data (this would be actual SQL for school database)
            query = """
            SELECT student_id, first_name, last_name, email, grade, 
                   enrollment_date, subjects, performance_summary, attendance_summary
            FROM students 
            WHERE status = 'active'
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            students = []
            for row in rows:
                student = StudentRecord(
                    student_id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    email=row[3],
                    grade=row[4],
                    enrollment_date=datetime.fromisoformat(row[5]),
                    subjects=json.loads(row[6]) if row[6] else [],
                    performance_data=json.loads(row[7]) if row[7] else {},
                    attendance_data=json.loads(row[8]) if row[8] else {}
                )
                students.append(student)
            
            logger.info(f"Fetched {len(students)} students from school database")
            return students
            
        except Exception as e:
            logger.error(f"Error fetching students: {e}")
            return []
    
    def fetch_teachers(self) -> List[TeacherRecord]:
        """Fetch teacher data from school database"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT teacher_id, first_name, last_name, email, subjects, 
                   department, hire_date, qualifications
            FROM teachers 
            WHERE status = 'active'
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            teachers = []
            for row in rows:
                teacher = TeacherRecord(
                    teacher_id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    email=row[3],
                    subjects=json.loads(row[4]) if row[4] else [],
                    department=row[5],
                    hire_date=datetime.fromisoformat(row[6]),
                    qualifications=json.loads(row[7]) if row[7] else []
                )
                teachers.append(teacher)
            
            logger.info(f"Fetched {len(teachers)} teachers from school database")
            return teachers
            
        except Exception as e:
            logger.error(f"Error fetching teachers: {e}")
            return []
    
    def fetch_performance_data(self, student_id: str = None) -> List[PerformanceRecord]:
        """Fetch performance data from school database"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            if student_id:
                query = """
                SELECT student_id, subject, assessment_type, score, max_score, 
                       date, teacher_id, comments
                FROM performance_records 
                WHERE student_id = ? AND date >= ?
                ORDER BY date DESC
                """
                cursor.execute(query, (student_id, (datetime.now() - timedelta(days=365)).isoformat()))
            else:
                query = """
                SELECT student_id, subject, assessment_type, score, max_score, 
                       date, teacher_id, comments
                FROM performance_records 
                WHERE date >= ?
                ORDER BY date DESC
                """
                cursor.execute(query, ((datetime.now() - timedelta(days=365)).isoformat(),))
            
            rows = cursor.fetchall()
            
            performance_records = []
            for row in rows:
                record = PerformanceRecord(
                    student_id=row[0],
                    subject=row[1],
                    assessment_type=row[2],
                    score=row[3],
                    max_score=row[4],
                    date=datetime.fromisoformat(row[5]),
                    teacher_id=row[6],
                    comments=row[7]
                )
                performance_records.append(record)
            
            logger.info(f"Fetched {len(performance_records)} performance records")
            return performance_records
            
        except Exception as e:
            logger.error(f"Error fetching performance data: {e}")
            return []

class SchoolAPIConnector(DataSource):
    """Connector for school API systems"""
    
    def __init__(self, config: SchoolDataConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        })
    
    def connect(self) -> bool:
        """Test API connection"""
        try:
            response = self.session.get(f"{self.config.api_base_url}/health")
            if response.status_code == 200:
                logger.info(f"Connected to school API: {self.config.school_id}")
                return True
            else:
                logger.error(f"API health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to school API: {e}")
            return False
    
    def fetch_students(self) -> List[StudentRecord]:
        """Fetch student data from school API"""
        try:
            response = self.session.get(f"{self.config.api_base_url}/students")
            if response.status_code != 200:
                logger.error(f"Failed to fetch students: {response.status_code}")
                return []
            
            data = response.json()
            students = []
            
            for student_data in data.get('students', []):
                student = StudentRecord(
                    student_id=student_data['id'],
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    email=student_data['email'],
                    grade=student_data['grade'],
                    enrollment_date=datetime.fromisoformat(student_data['enrollment_date']),
                    subjects=student_data.get('subjects', []),
                    performance_data=student_data.get('performance_summary', {}),
                    attendance_data=student_data.get('attendance_summary', {})
                )
                students.append(student)
            
            logger.info(f"Fetched {len(students)} students from school API")
            return students
            
        except Exception as e:
            logger.error(f"Error fetching students from API: {e}")
            return []
    
    def fetch_teachers(self) -> List[TeacherRecord]:
        """Fetch teacher data from school API"""
        try:
            response = self.session.get(f"{self.config.api_base_url}/teachers")
            if response.status_code != 200:
                logger.error(f"Failed to fetch teachers: {response.status_code}")
                return []
            
            data = response.json()
            teachers = []
            
            for teacher_data in data.get('teachers', []):
                teacher = TeacherRecord(
                    teacher_id=teacher_data['id'],
                    first_name=teacher_data['first_name'],
                    last_name=teacher_data['last_name'],
                    email=teacher_data['email'],
                    subjects=teacher_data.get('subjects', []),
                    department=teacher_data.get('department', ''),
                    hire_date=datetime.fromisoformat(teacher_data['hire_date']),
                    qualifications=teacher_data.get('qualifications', [])
                )
                teachers.append(teacher)
            
            logger.info(f"Fetched {len(teachers)} teachers from school API")
            return teachers
            
        except Exception as e:
            logger.error(f"Error fetching teachers from API: {e}")
            return []
    
    def fetch_performance_data(self, student_id: str = None) -> List[PerformanceRecord]:
        """Fetch performance data from school API"""
        try:
            url = f"{self.config.api_base_url}/performance"
            params = {'date_from': (datetime.now() - timedelta(days=365)).isoformat()}
            
            if student_id:
                params['student_id'] = student_id
            
            response = self.session.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"Failed to fetch performance data: {response.status_code}")
                return []
            
            data = response.json()
            performance_records = []
            
            for record_data in data.get('performance_records', []):
                record = PerformanceRecord(
                    student_id=record_data['student_id'],
                    subject=record_data['subject'],
                    assessment_type=record_data['assessment_type'],
                    score=record_data['score'],
                    max_score=record_data['max_score'],
                    date=datetime.fromisoformat(record_data['date']),
                    teacher_id=record_data['teacher_id'],
                    comments=record_data.get('comments')
                )
                performance_records.append(record)
            
            logger.info(f"Fetched {len(performance_records)} performance records from API")
            return performance_records
            
        except Exception as e:
            logger.error(f"Error fetching performance data from API: {e}")
            return []

class DataSyncManager:
    """Manages data synchronization between school systems and roadmap system"""
    
    def __init__(self, data_sources: List[DataSource], local_db_path: str = "data/synced_data.db"):
        self.data_sources = data_sources
        self.local_db_path = local_db_path
        self._init_local_database()
    
    def _init_local_database(self):
        """Initialize local database for synced data"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synced_students (
                student_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                grade TEXT NOT NULL,
                enrollment_date TEXT NOT NULL,
                subjects TEXT,
                performance_data TEXT,
                attendance_data TEXT,
                last_updated TEXT NOT NULL,
                source TEXT NOT NULL
            )
        ''')
        
        # Teachers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synced_teachers (
                teacher_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                subjects TEXT,
                department TEXT,
                hire_date TEXT NOT NULL,
                qualifications TEXT,
                last_updated TEXT NOT NULL,
                source TEXT NOT NULL
            )
        ''')
        
        # Performance records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synced_performance (
                record_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                assessment_type TEXT NOT NULL,
                score REAL NOT NULL,
                max_score REAL NOT NULL,
                date TEXT NOT NULL,
                teacher_id TEXT,
                comments TEXT,
                last_updated TEXT NOT NULL,
                source TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def sync_all_data(self) -> Dict[str, Any]:
        """Sync data from all sources"""
        results = {
            'students_synced': 0,
            'teachers_synced': 0,
            'performance_records_synced': 0,
            'errors': [],
            'sync_time': datetime.now().isoformat()
        }
        
        for source in self.data_sources:
            try:
                if not source.connect():
                    results['errors'].append(f"Failed to connect to source: {type(source).__name__}")
                    continue
                
                # Sync students
                students = source.fetch_students()
                for student in students:
                    self._sync_student(student, type(source).__name__)
                    results['students_synced'] += 1
                
                # Sync teachers
                teachers = source.fetch_teachers()
                for teacher in teachers:
                    self._sync_teacher(teacher, type(source).__name__)
                    results['teachers_synced'] += 1
                
                # Sync performance data
                performance_records = source.fetch_performance_data()
                for record in performance_records:
                    self._sync_performance_record(record, type(source).__name__)
                    results['performance_records_synced'] += 1
                
            except Exception as e:
                results['errors'].append(f"Error syncing from {type(source).__name__}: {str(e)}")
                logger.error(f"Error syncing from {type(source).__name__}: {e}")
        
        logger.info(f"Data sync completed: {results}")
        return results
    
    def _sync_student(self, student: StudentRecord, source: str):
        """Sync individual student record"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO synced_students 
            (student_id, first_name, last_name, email, grade, enrollment_date,
             subjects, performance_data, attendance_data, last_updated, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student.student_id,
            student.first_name,
            student.last_name,
            student.email,
            student.grade,
            student.enrollment_date.isoformat(),
            json.dumps(student.subjects),
            json.dumps(student.performance_data),
            json.dumps(student.attendance_data),
            datetime.now().isoformat(),
            source
        ))
        
        conn.commit()
        conn.close()
    
    def _sync_teacher(self, teacher: TeacherRecord, source: str):
        """Sync individual teacher record"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO synced_teachers 
            (teacher_id, first_name, last_name, email, subjects, department,
             hire_date, qualifications, last_updated, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            teacher.teacher_id,
            teacher.first_name,
            teacher.last_name,
            teacher.email,
            json.dumps(teacher.subjects),
            teacher.department,
            teacher.hire_date.isoformat(),
            json.dumps(teacher.qualifications),
            datetime.now().isoformat(),
            source
        ))
        
        conn.commit()
        conn.close()
    
    def _sync_performance_record(self, record: PerformanceRecord, source: str):
        """Sync individual performance record"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        record_id = f"{record.student_id}_{record.date.isoformat()}_{record.subject}"
        
        cursor.execute('''
            INSERT OR REPLACE INTO synced_performance 
            (record_id, student_id, subject, assessment_type, score, max_score,
             date, teacher_id, comments, last_updated, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record_id,
            record.student_id,
            record.subject,
            record.assessment_type,
            record.score,
            record.max_score,
            record.date.isoformat(),
            record.teacher_id,
            record.comments,
            datetime.now().isoformat(),
            source
        ))
        
        conn.commit()
        conn.close()
    
    def get_synced_students(self) -> List[StudentRecord]:
        """Get all synced students"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM synced_students ORDER BY last_updated DESC')
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            student = StudentRecord(
                student_id=row[0],
                first_name=row[1],
                last_name=row[2],
                email=row[3],
                grade=row[4],
                enrollment_date=datetime.fromisoformat(row[5]),
                subjects=json.loads(row[6]) if row[6] else [],
                performance_data=json.loads(row[7]) if row[7] else {},
                attendance_data=json.loads(row[8]) if row[8] else {}
            )
            students.append(student)
        
        return students
    
    def get_synced_teachers(self) -> List[TeacherRecord]:
        """Get all synced teachers"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM synced_teachers ORDER BY last_updated DESC')
        rows = cursor.fetchall()
        conn.close()
        
        teachers = []
        for row in rows:
            teacher = TeacherRecord(
                teacher_id=row[0],
                first_name=row[1],
                last_name=row[2],
                email=row[3],
                subjects=json.loads(row[4]) if row[4] else [],
                department=row[5],
                hire_date=datetime.fromisoformat(row[6]),
                qualifications=json.loads(row[7]) if row[7] else []
            )
            teachers.append(teacher)
        
        return teachers
    
    def get_synced_performance_data(self, student_id: str = None) -> List[PerformanceRecord]:
        """Get synced performance data"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        if student_id:
            cursor.execute('''
                SELECT * FROM synced_performance 
                WHERE student_id = ? 
                ORDER BY date DESC
            ''', (student_id,))
        else:
            cursor.execute('SELECT * FROM synced_performance ORDER BY date DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            record = PerformanceRecord(
                student_id=row[1],
                subject=row[2],
                assessment_type=row[3],
                score=row[4],
                max_score=row[5],
                date=datetime.fromisoformat(row[6]),
                teacher_id=row[7],
                comments=row[8]
            )
            records.append(record)
        
        return records

class DataIntegrationManager:
    """Main manager for data integration"""
    
    def __init__(self, config_file: str = "config/data_sources.json"):
        self.config_file = config_file
        self.data_sources = []
        self.sync_manager = None
        self._load_configuration()
    
    def _load_configuration(self):
        """Load data source configurations"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Create data sources based on configuration
                for source_config in config_data.get('data_sources', []):
                    if source_config['type'] == 'database':
                        config = SchoolDataConfig(**source_config['config'])
                        source = SchoolDatabaseConnector(config)
                    elif source_config['type'] == 'api':
                        config = SchoolDataConfig(**source_config['config'])
                        source = SchoolAPIConnector(config)
                    else:
                        continue
                    
                    self.data_sources.append(source)
                
                # Initialize sync manager
                self.sync_manager = DataSyncManager(self.data_sources)
                
                logger.info(f"Loaded {len(self.data_sources)} data sources")
            else:
                logger.warning(f"Configuration file not found: {self.config_file}")
                self._create_default_configuration()
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default configuration file"""
        default_config = {
            "data_sources": [
                {
                    "type": "database",
                    "name": "Local School Database",
                    "config": {
                        "school_id": "demo_school",
                        "api_base_url": "",
                        "api_key": "",
                        "database_connection": "data/school_demo.db",
                        "sync_interval_hours": 24
                    }
                }
            ]
        }
        
        os.makedirs("config", exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info("Created default configuration file")
    
    def sync_all_data(self) -> Dict[str, Any]:
        """Sync data from all configured sources"""
        if not self.sync_manager:
            return {"error": "No sync manager available"}
        
        return self.sync_manager.sync_all_data()
    
    def get_students(self) -> List[StudentRecord]:
        """Get all students from synced data"""
        if not self.sync_manager:
            return []
        
        return self.sync_manager.get_synced_students()
    
    def get_teachers(self) -> List[TeacherRecord]:
        """Get all teachers from synced data"""
        if not self.sync_manager:
            return []
        
        return self.sync_manager.get_synced_teachers()
    
    def get_performance_data(self, student_id: str = None) -> List[PerformanceRecord]:
        """Get performance data from synced data"""
        if not self.sync_manager:
            return []
        
        return self.sync_manager.get_synced_performance_data(student_id)
