"""
Production database manager with PostgreSQL/MySQL support
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_type: str  # 'postgresql', 'mysql', 'sqlite'
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = 'prefer'
    connection_pool_size: int = 10
    max_overflow: int = 20

class DatabaseManager(ABC):
    """Abstract database manager"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to database"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        """Execute query and return results"""
        pass
    
    @abstractmethod
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute update query and return affected rows"""
        pass
    
    @abstractmethod
    def close(self):
        """Close database connection"""
        pass

class PostgreSQLManager(DatabaseManager):
    """PostgreSQL database manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
        self.engine = None
        self._init_engine()
    
    def _init_engine(self):
        """Initialize SQLAlchemy engine"""
        try:
            import psycopg2
            from sqlalchemy import create_engine
            from sqlalchemy.pool import QueuePool
            
            connection_string = (
                f"postgresql://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.database}"
                f"?sslmode={self.config.ssl_mode}"
            )
            
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.config.connection_pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True
            )
            
            logger.info("PostgreSQL engine initialized")
            
        except ImportError:
            logger.error("psycopg2 and sqlalchemy required for PostgreSQL support")
            raise
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL engine: {e}")
            raise
    
    def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            self.connection = self.engine.connect()
            logger.info("Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        """Execute query and return results"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            result = self.connection.execute(query, params or ())
            columns = result.keys()
            rows = result.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute update query and return affected rows"""
        try:
            if not self.connection:
                if not self.connect():
                    return 0
            
            result = self.connection.execute(query, params or ())
            return result.rowcount
            
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

class MySQLManager(DatabaseManager):
    """MySQL database manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
        self.engine = None
        self._init_engine()
    
    def _init_engine(self):
        """Initialize SQLAlchemy engine"""
        try:
            import pymysql
            from sqlalchemy import create_engine
            from sqlalchemy.pool import QueuePool
            
            connection_string = (
                f"mysql+pymysql://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.database}"
                f"?charset=utf8mb4"
            )
            
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.config.connection_pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True
            )
            
            logger.info("MySQL engine initialized")
            
        except ImportError:
            logger.error("pymysql and sqlalchemy required for MySQL support")
            raise
        except Exception as e:
            logger.error(f"Error initializing MySQL engine: {e}")
            raise
    
    def connect(self) -> bool:
        """Connect to MySQL database"""
        try:
            self.connection = self.engine.connect()
            logger.info("Connected to MySQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            return False
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        """Execute query and return results"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            result = self.connection.execute(query, params or ())
            columns = result.keys()
            rows = result.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute update query and return affected rows"""
        try:
            if not self.connection:
                if not self.connect():
                    return 0
            
            result = self.connection.execute(query, params or ())
            return result.rowcount
            
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

class SQLiteManager(DatabaseManager):
    """SQLite database manager (fallback)"""
    
    def __init__(self, db_path: str = "data/production.db"):
        self.db_path = db_path
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            import sqlite3
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        """Execute query and return results"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute update query and return affected rows"""
        try:
            if not self.connection:
                if not self.connect():
                    return 0
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.rowcount
            
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

class ProductionDatabaseManager:
    """Main production database manager"""
    
    def __init__(self, config_file: str = "config/database_config.json"):
        self.config_file = config_file
        self.db_manager = None
        self.config = None
        self._load_configuration()
        self._init_database_manager()
    
    def _load_configuration(self):
        """Load database configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self.config = DatabaseConfig(**config_data)
            else:
                self._create_default_configuration()
                
        except Exception as e:
            logger.error(f"Error loading database configuration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default configuration"""
        self.config = DatabaseConfig(
            db_type=os.getenv('DB_TYPE', 'sqlite'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'roadmap_system'),
            username=os.getenv('DB_USER', 'roadmap_user'),
            password=os.getenv('DB_PASSWORD', 'roadmap_password'),
            ssl_mode=os.getenv('DB_SSL_MODE', 'prefer'),
            connection_pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20'))
        )
        
        # Save configuration
        os.makedirs("config", exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config.__dict__, f, indent=2)
        
        logger.info("Created default database configuration")
    
    def _init_database_manager(self):
        """Initialize appropriate database manager"""
        try:
            if self.config.db_type.lower() == 'postgresql':
                self.db_manager = PostgreSQLManager(self.config)
            elif self.config.db_type.lower() == 'mysql':
                self.db_manager = MySQLManager(self.config)
            else:
                # Fallback to SQLite
                self.db_manager = SQLiteManager("data/production.db")
            
            logger.info(f"Initialized {self.config.db_type} database manager")
            
        except Exception as e:
            logger.error(f"Error initializing database manager: {e}")
            # Fallback to SQLite
            self.db_manager = SQLiteManager("data/production.db")
    
    def connect(self) -> bool:
        """Connect to database"""
        if not self.db_manager:
            return False
        return self.db_manager.connect()
    
    def create_tables(self) -> bool:
        """Create all required tables"""
        try:
            if not self.connect():
                return False
            
            # Define table schemas
            tables = {
                'users': '''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id VARCHAR(255) PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        last_login TIMESTAMP,
                        profile_data JSON,
                        permissions JSON
                    )
                ''',
                'students': '''
                    CREATE TABLE IF NOT EXISTS students (
                        student_id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        age INTEGER,
                        grade VARCHAR(50),
                        target_scores JSON,
                        current_scores JSON,
                        learning_style VARCHAR(50),
                        available_hours_per_day DECIMAL(5,2),
                        preferred_study_times JSON,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    )
                ''',
                'teachers': '''
                    CREATE TABLE IF NOT EXISTS teachers (
                        teacher_id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        subjects JSON,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        expertise_level VARCHAR(50),
                        max_students INTEGER,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP NOT NULL
                    )
                ''',
                'parents': '''
                    CREATE TABLE IF NOT EXISTS parents (
                        parent_id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        student_ids JSON,
                        notification_preferences JSON,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP NOT NULL
                    )
                ''',
                'roadmaps': '''
                    CREATE TABLE IF NOT EXISTS roadmaps (
                        roadmap_id VARCHAR(255) PRIMARY KEY,
                        student_id VARCHAR(255) NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        duration_weeks INTEGER NOT NULL,
                        overall_goals JSON,
                        success_metrics JSON,
                        last_updated TIMESTAMP NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES students (student_id)
                    )
                ''',
                'weekly_plans': '''
                    CREATE TABLE IF NOT EXISTS weekly_plans (
                        plan_id VARCHAR(255) PRIMARY KEY,
                        roadmap_id VARCHAR(255) NOT NULL,
                        week_number INTEGER NOT NULL,
                        start_date TIMESTAMP NOT NULL,
                        end_date TIMESTAMP NOT NULL,
                        total_hours DECIMAL(5,2),
                        subject_breakdown JSON,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (roadmap_id) REFERENCES roadmaps (roadmap_id)
                    )
                ''',
                'study_tasks': '''
                    CREATE TABLE IF NOT EXISTS study_tasks (
                        task_id VARCHAR(255) PRIMARY KEY,
                        plan_id VARCHAR(255) NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        subject VARCHAR(50) NOT NULL,
                        topic VARCHAR(255) NOT NULL,
                        description TEXT,
                        priority VARCHAR(20) NOT NULL,
                        estimated_duration INTEGER NOT NULL,
                        due_date TIMESTAMP NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        completion_percentage DECIMAL(5,2) DEFAULT 0,
                        actual_duration INTEGER,
                        notes TEXT,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (plan_id) REFERENCES weekly_plans (plan_id)
                    )
                ''',
                'performance_metrics': '''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        metric_id VARCHAR(255) PRIMARY KEY,
                        student_id VARCHAR(255) NOT NULL,
                        subject VARCHAR(50) NOT NULL,
                        score DECIMAL(5,2) NOT NULL,
                        max_score DECIMAL(5,2) NOT NULL,
                        date TIMESTAMP NOT NULL,
                        test_type VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES students (student_id)
                    )
                ''',
                'monitoring_reports': '''
                    CREATE TABLE IF NOT EXISTS monitoring_reports (
                        report_id VARCHAR(255) PRIMARY KEY,
                        student_id VARCHAR(255) NOT NULL,
                        week_number INTEGER NOT NULL,
                        generated_date TIMESTAMP NOT NULL,
                        tasks_completed INTEGER NOT NULL,
                        tasks_pending INTEGER NOT NULL,
                        tasks_overdue INTEGER NOT NULL,
                        adherence_rate DECIMAL(5,2) NOT NULL,
                        irregularities JSON,
                        recommendations JSON,
                        performance_trends JSON,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES students (student_id)
                    )
                ''',
                'feedback_workflows': '''
                    CREATE TABLE IF NOT EXISTS feedback_workflows (
                        workflow_id VARCHAR(255) PRIMARY KEY,
                        student_id VARCHAR(255) NOT NULL,
                        roadmap_id VARCHAR(255) NOT NULL,
                        current_stage VARCHAR(50) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        last_updated TIMESTAMP NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES students (student_id),
                        FOREIGN KEY (roadmap_id) REFERENCES roadmaps (roadmap_id)
                    )
                ''',
                'teacher_feedback': '''
                    CREATE TABLE IF NOT EXISTS teacher_feedback (
                        feedback_id VARCHAR(255) PRIMARY KEY,
                        teacher_id VARCHAR(255) NOT NULL,
                        student_id VARCHAR(255) NOT NULL,
                        roadmap_id VARCHAR(255) NOT NULL,
                        workflow_id VARCHAR(255) NOT NULL,
                        feedback_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        priority VARCHAR(20) NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        is_addressed BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id),
                        FOREIGN KEY (student_id) REFERENCES students (student_id),
                        FOREIGN KEY (roadmap_id) REFERENCES roadmaps (roadmap_id),
                        FOREIGN KEY (workflow_id) REFERENCES feedback_workflows (workflow_id)
                    )
                ''',
                'parent_feedback': '''
                    CREATE TABLE IF NOT EXISTS parent_feedback (
                        feedback_id VARCHAR(255) PRIMARY KEY,
                        parent_id VARCHAR(255) NOT NULL,
                        student_id VARCHAR(255) NOT NULL,
                        workflow_id VARCHAR(255) NOT NULL,
                        feedback_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        priority VARCHAR(20) NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        is_addressed BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (parent_id) REFERENCES parents (parent_id),
                        FOREIGN KEY (student_id) REFERENCES students (student_id),
                        FOREIGN KEY (workflow_id) REFERENCES feedback_workflows (workflow_id)
                    )
                '''
            }
            
            # Create tables
            for table_name, schema in tables.items():
                try:
                    self.db_manager.execute_update(schema)
                    logger.info(f"Created table: {table_name}")
                except Exception as e:
                    logger.error(f"Error creating table {table_name}: {e}")
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_students_grade ON students(grade)",
                "CREATE INDEX IF NOT EXISTS idx_roadmaps_student ON roadmaps(student_id)",
                "CREATE INDEX IF NOT EXISTS idx_tasks_plan ON study_tasks(plan_id)",
                "CREATE INDEX IF NOT EXISTS idx_performance_student ON performance_metrics(student_id)",
                "CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date)",
                "CREATE INDEX IF NOT EXISTS idx_reports_student ON monitoring_reports(student_id)",
                "CREATE INDEX IF NOT EXISTS idx_feedback_teacher ON teacher_feedback(teacher_id)",
                "CREATE INDEX IF NOT EXISTS idx_feedback_parent ON parent_feedback(parent_id)"
            ]
            
            for index_sql in indexes:
                try:
                    self.db_manager.execute_update(index_sql)
                except Exception as e:
                    logger.warning(f"Error creating index: {e}")
            
            logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        """Execute query and return results"""
        if not self.db_manager:
            return []
        return self.db_manager.execute_query(query, params)
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute update query and return affected rows"""
        if not self.db_manager:
            return 0
        return self.db_manager.execute_update(query, params)
    
    def close(self):
        """Close database connection"""
        if self.db_manager:
            self.db_manager.close()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        if not self.config:
            return {}
        
        return {
            "database_type": self.config.db_type,
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database,
            "username": self.config.username,
            "connection_pool_size": self.config.connection_pool_size,
            "max_overflow": self.config.max_overflow
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status"""
        try:
            if not self.connect():
                return {"status": "failed", "error": "Could not connect to database"}
            
            # Test with simple query
            result = self.execute_query("SELECT 1 as test")
            if result and result[0].get('test') == 1:
                return {
                    "status": "success",
                    "message": "Database connection successful",
                    "connection_info": self.get_connection_info()
                }
            else:
                return {"status": "failed", "error": "Query test failed"}
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
        finally:
            self.close()
