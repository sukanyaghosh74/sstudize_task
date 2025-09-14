"""
API integration for learning management systems and external services
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API configuration"""
    base_url: str
    api_key: str
    api_secret: str = None
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit_per_minute: int = 100
    headers: Dict[str, str] = None

@dataclass
class LMSStudent:
    """Student data from LMS"""
    lms_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    courses: List[str]
    enrollment_date: datetime
    last_activity: datetime
    progress_data: Dict[str, Any]

@dataclass
class LMSCourse:
    """Course data from LMS"""
    course_id: str
    title: str
    description: str
    instructor: str
    start_date: datetime
    end_date: datetime
    modules: List[str]
    assessment_data: Dict[str, Any]

@dataclass
class LMSAssignment:
    """Assignment data from LMS"""
    assignment_id: str
    course_id: str
    title: str
    description: str
    due_date: datetime
    max_points: float
    submission_data: Dict[str, Any]

class LMSConnector(ABC):
    """Abstract base class for LMS connectors"""
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with LMS API"""
        pass
    
    @abstractmethod
    def get_students(self) -> List[LMSStudent]:
        """Get all students from LMS"""
        pass
    
    @abstractmethod
    def get_courses(self) -> List[LMSCourse]:
        """Get all courses from LMS"""
        pass
    
    @abstractmethod
    def get_assignments(self, course_id: str = None) -> List[LMSAssignment]:
        """Get assignments from LMS"""
        pass
    
    @abstractmethod
    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get student progress data"""
        pass

class CanvasConnector(LMSConnector):
    """Canvas LMS connector"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        })
        if self.config.headers:
            self.session.headers.update(self.config.headers)
    
    def authenticate(self) -> bool:
        """Authenticate with Canvas API"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/v1/users/self",
                timeout=self.config.timeout
            )
            if response.status_code == 200:
                logger.info("Successfully authenticated with Canvas")
                return True
            else:
                logger.error(f"Canvas authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Canvas authentication error: {e}")
            return False
    
    def get_students(self) -> List[LMSStudent]:
        """Get all students from Canvas"""
        try:
            students = []
            url = f"{self.config.base_url}/api/v1/accounts/self/users"
            params = {'enrollment_type': 'student', 'per_page': 100}
            
            while url:
                response = self.session.get(url, params=params, timeout=self.config.timeout)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch students: {response.status_code}")
                    break
                
                data = response.json()
                for user_data in data:
                    student = LMSStudent(
                        lms_id=str(user_data['id']),
                        username=user_data.get('login_id', ''),
                        email=user_data.get('email', ''),
                        first_name=user_data.get('first_name', ''),
                        last_name=user_data.get('last_name', ''),
                        courses=[],  # Will be populated separately
                        enrollment_date=datetime.fromisoformat(
                            user_data.get('created_at', datetime.now().isoformat())
                        ),
                        last_activity=datetime.fromisoformat(
                            user_data.get('last_login', datetime.now().isoformat())
                        ),
                        progress_data={}
                    )
                    students.append(student)
                
                # Handle pagination
                links = response.headers.get('Link', '')
                url = self._extract_next_url(links)
                params = None  # Next URL includes params
            
            logger.info(f"Fetched {len(students)} students from Canvas")
            return students
            
        except Exception as e:
            logger.error(f"Error fetching students from Canvas: {e}")
            return []
    
    def get_courses(self) -> List[LMSCourse]:
        """Get all courses from Canvas"""
        try:
            courses = []
            url = f"{self.config.base_url}/api/v1/courses"
            params = {'enrollment_type': 'teacher', 'per_page': 100}
            
            while url:
                response = self.session.get(url, params=params, timeout=self.config.timeout)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch courses: {response.status_code}")
                    break
                
                data = response.json()
                for course_data in data:
                    course = LMSCourse(
                        course_id=str(course_data['id']),
                        title=course_data.get('name', ''),
                        description=course_data.get('course_code', ''),
                        instructor='',  # Will be populated separately
                        start_date=datetime.fromisoformat(
                            course_data.get('start_at', datetime.now().isoformat())
                        ) if course_data.get('start_at') else datetime.now(),
                        end_date=datetime.fromisoformat(
                            course_data.get('end_at', datetime.now().isoformat())
                        ) if course_data.get('end_at') else datetime.now(),
                        modules=[],  # Will be populated separately
                        assessment_data={}
                    )
                    courses.append(course)
                
                # Handle pagination
                links = response.headers.get('Link', '')
                url = self._extract_next_url(links)
                params = None
            
            logger.info(f"Fetched {len(courses)} courses from Canvas")
            return courses
            
        except Exception as e:
            logger.error(f"Error fetching courses from Canvas: {e}")
            return []
    
    def get_assignments(self, course_id: str = None) -> List[LMSAssignment]:
        """Get assignments from Canvas"""
        try:
            assignments = []
            
            if course_id:
                courses = [course_id]
            else:
                # Get all courses first
                courses_data = self.get_courses()
                courses = [course.course_id for course in courses_data]
            
            for cid in courses:
                url = f"{self.config.base_url}/api/v1/courses/{cid}/assignments"
                params = {'per_page': 100}
                
                while url:
                    response = self.session.get(url, params=params, timeout=self.config.timeout)
                    if response.status_code != 200:
                        logger.warning(f"Failed to fetch assignments for course {cid}: {response.status_code}")
                        break
                    
                    data = response.json()
                    for assignment_data in data:
                        assignment = LMSAssignment(
                            assignment_id=str(assignment_data['id']),
                            course_id=cid,
                            title=assignment_data.get('name', ''),
                            description=assignment_data.get('description', ''),
                            due_date=datetime.fromisoformat(
                                assignment_data.get('due_at', datetime.now().isoformat())
                            ) if assignment_data.get('due_at') else datetime.now(),
                            max_points=assignment_data.get('points_possible', 0),
                            submission_data={}
                        )
                        assignments.append(assignment)
                    
                    # Handle pagination
                    links = response.headers.get('Link', '')
                    url = self._extract_next_url(links)
                    params = None
            
            logger.info(f"Fetched {len(assignments)} assignments from Canvas")
            return assignments
            
        except Exception as e:
            logger.error(f"Error fetching assignments from Canvas: {e}")
            return []
    
    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get student progress data from Canvas"""
        try:
            # Get student's courses
            url = f"{self.config.base_url}/api/v1/users/{student_id}/courses"
            response = self.session.get(url, timeout=self.config.timeout)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch student courses: {response.status_code}")
                return {}
            
            courses_data = response.json()
            progress_data = {
                'courses': [],
                'total_assignments': 0,
                'completed_assignments': 0,
                'average_grade': 0,
                'last_activity': None
            }
            
            for course_data in courses_data:
                course_id = course_data['id']
                
                # Get course progress
                progress_url = f"{self.config.base_url}/api/v1/courses/{course_id}/students/{student_id}/progress"
                progress_response = self.session.get(progress_url, timeout=self.config.timeout)
                
                if progress_response.status_code == 200:
                    course_progress = progress_response.json()
                    progress_data['courses'].append({
                        'course_id': course_id,
                        'course_name': course_data.get('name', ''),
                        'progress': course_progress.get('completion', 0),
                        'grade': course_progress.get('grade', 0)
                    })
            
            logger.info(f"Fetched progress data for student {student_id}")
            return progress_data
            
        except Exception as e:
            logger.error(f"Error fetching student progress from Canvas: {e}")
            return {}
    
    def _extract_next_url(self, link_header: str) -> Optional[str]:
        """Extract next URL from Link header"""
        if not link_header:
            return None
        
        links = link_header.split(',')
        for link in links:
            if 'rel="next"' in link:
                url = link.split(';')[0].strip('<>')
                return url
        return None

class MoodleConnector(LMSConnector):
    """Moodle LMS connector"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        if self.config.headers:
            self.session.headers.update(self.config.headers)
    
    def authenticate(self) -> bool:
        """Authenticate with Moodle API"""
        try:
            # Moodle uses token-based authentication
            response = self.session.get(
                f"{self.config.base_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.config.api_key,
                    'wsfunction': 'core_webservice_get_site_info',
                    'moodlewsrestformat': 'json'
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errorcode' not in data:
                    logger.info("Successfully authenticated with Moodle")
                    return True
                else:
                    logger.error(f"Moodle authentication failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                logger.error(f"Moodle authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Moodle authentication error: {e}")
            return False
    
    def get_students(self) -> List[LMSStudent]:
        """Get all students from Moodle"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.config.api_key,
                    'wsfunction': 'core_user_get_users',
                    'moodlewsrestformat': 'json'
                },
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch students: {response.status_code}")
                return []
            
            data = response.json()
            students = []
            
            for user_data in data.get('users', []):
                student = LMSStudent(
                    lms_id=str(user_data['id']),
                    username=user_data.get('username', ''),
                    email=user_data.get('email', ''),
                    first_name=user_data.get('firstname', ''),
                    last_name=user_data.get('lastname', ''),
                    courses=[],
                    enrollment_date=datetime.fromtimestamp(
                        user_data.get('timecreated', datetime.now().timestamp())
                    ),
                    last_activity=datetime.fromtimestamp(
                        user_data.get('lastaccess', datetime.now().timestamp())
                    ),
                    progress_data={}
                )
                students.append(student)
            
            logger.info(f"Fetched {len(students)} students from Moodle")
            return students
            
        except Exception as e:
            logger.error(f"Error fetching students from Moodle: {e}")
            return []
    
    def get_courses(self) -> List[LMSCourse]:
        """Get all courses from Moodle"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.config.api_key,
                    'wsfunction': 'core_course_get_courses',
                    'moodlewsrestformat': 'json'
                },
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch courses: {response.status_code}")
                return []
            
            data = response.json()
            courses = []
            
            for course_data in data:
                course = LMSCourse(
                    course_id=str(course_data['id']),
                    title=course_data.get('fullname', ''),
                    description=course_data.get('shortname', ''),
                    instructor='',
                    start_date=datetime.fromtimestamp(
                        course_data.get('startdate', datetime.now().timestamp())
                    ),
                    end_date=datetime.fromtimestamp(
                        course_data.get('enddate', datetime.now().timestamp())
                    ),
                    modules=[],
                    assessment_data={}
                )
                courses.append(course)
            
            logger.info(f"Fetched {len(courses)} courses from Moodle")
            return courses
            
        except Exception as e:
            logger.error(f"Error fetching courses from Moodle: {e}")
            return []
    
    def get_assignments(self, course_id: str = None) -> List[LMSAssignment]:
        """Get assignments from Moodle"""
        try:
            assignments = []
            
            if course_id:
                courses = [course_id]
            else:
                courses_data = self.get_courses()
                courses = [course.course_id for course in courses_data]
            
            for cid in courses:
                response = self.session.get(
                    f"{self.config.base_url}/webservice/rest/server.php",
                    params={
                        'wstoken': self.config.api_key,
                        'wsfunction': 'mod_assign_get_assignments',
                        'courseids[0]': cid,
                        'moodlewsrestformat': 'json'
                    },
                    timeout=self.config.timeout
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch assignments for course {cid}: {response.status_code}")
                    continue
                
                data = response.json()
                for assignment_data in data.get('courses', [{}])[0].get('assignments', []):
                    assignment = LMSAssignment(
                        assignment_id=str(assignment_data['id']),
                        course_id=cid,
                        title=assignment_data.get('name', ''),
                        description=assignment_data.get('intro', ''),
                        due_date=datetime.fromtimestamp(
                            assignment_data.get('duedate', datetime.now().timestamp())
                        ),
                        max_points=assignment_data.get('grade', 0),
                        submission_data={}
                    )
                    assignments.append(assignment)
            
            logger.info(f"Fetched {len(assignments)} assignments from Moodle")
            return assignments
            
        except Exception as e:
            logger.error(f"Error fetching assignments from Moodle: {e}")
            return []
    
    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get student progress data from Moodle"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.config.api_key,
                    'wsfunction': 'core_grades_get_grades',
                    'userids[0]': student_id,
                    'moodlewsrestformat': 'json'
                },
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch student progress: {response.status_code}")
                return {}
            
            data = response.json()
            progress_data = {
                'courses': [],
                'total_assignments': 0,
                'completed_assignments': 0,
                'average_grade': 0,
                'last_activity': None
            }
            
            for grade_data in data.get('usergrades', []):
                course_id = grade_data.get('courseid')
                if course_id:
                    progress_data['courses'].append({
                        'course_id': course_id,
                        'grade': grade_data.get('grade', 0),
                        'progress': 0  # Moodle doesn't provide direct progress
                    })
            
            logger.info(f"Fetched progress data for student {student_id}")
            return progress_data
            
        except Exception as e:
            logger.error(f"Error fetching student progress from Moodle: {e}")
            return {}

class APIIntegrationManager:
    """Main API integration manager"""
    
    def __init__(self, config_file: str = "config/api_config.json"):
        self.config_file = config_file
        self.connectors = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """Load API configurations"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                for service_name, service_config in config_data.get('services', {}).items():
                    config = APIConfig(**service_config['config'])
                    
                    if service_config['type'] == 'canvas':
                        connector = CanvasConnector(config)
                    elif service_config['type'] == 'moodle':
                        connector = MoodleConnector(config)
                    else:
                        continue
                    
                    self.connectors[service_name] = connector
                    logger.info(f"Loaded {service_config['type']} connector: {service_name}")
                
            else:
                self._create_default_configuration()
                
        except Exception as e:
            logger.error(f"Error loading API configuration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default API configuration"""
        default_config = {
            "services": {
                "canvas_demo": {
                    "type": "canvas",
                    "name": "Canvas Demo",
                    "config": {
                        "base_url": "https://demo.instructure.com",
                        "api_key": "your_canvas_api_key",
                        "timeout": 30,
                        "retry_attempts": 3,
                        "rate_limit_per_minute": 100
                    }
                },
                "moodle_demo": {
                    "type": "moodle",
                    "name": "Moodle Demo",
                    "config": {
                        "base_url": "https://demo.moodle.org",
                        "api_key": "your_moodle_token",
                        "timeout": 30,
                        "retry_attempts": 3,
                        "rate_limit_per_minute": 100
                    }
                }
            }
        }
        
        os.makedirs("config", exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info("Created default API configuration")
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all API connections"""
        results = {}
        
        for service_name, connector in self.connectors.items():
            try:
                success = connector.authenticate()
                results[service_name] = {
                    "status": "success" if success else "failed",
                    "message": "Connection successful" if success else "Authentication failed"
                }
            except Exception as e:
                results[service_name] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return results
    
    def sync_lms_data(self, service_name: str) -> Dict[str, Any]:
        """Sync data from specific LMS service"""
        if service_name not in self.connectors:
            return {"error": f"Service {service_name} not found"}
        
        connector = self.connectors[service_name]
        
        try:
            if not connector.authenticate():
                return {"error": "Authentication failed"}
            
            # Sync students
            students = connector.get_students()
            courses = connector.get_courses()
            assignments = connector.get_assignments()
            
            return {
                "status": "success",
                "students_synced": len(students),
                "courses_synced": len(courses),
                "assignments_synced": len(assignments),
                "sync_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_student_lms_data(self, student_id: str, service_name: str = None) -> Dict[str, Any]:
        """Get student data from LMS services"""
        results = {}
        
        services_to_check = [service_name] if service_name else self.connectors.keys()
        
        for service in services_to_check:
            if service not in self.connectors:
                continue
            
            connector = self.connectors[service]
            try:
                if connector.authenticate():
                    progress_data = connector.get_student_progress(student_id)
                    results[service] = progress_data
            except Exception as e:
                results[service] = {"error": str(e)}
        
        return results
