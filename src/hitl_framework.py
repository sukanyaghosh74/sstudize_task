"""
Human-in-the-Loop (HITL) framework for teacher and parent oversight
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging
from enum import Enum

from data_models import (
    StudentProfile, Roadmap, WeeklyPlan, StudyTask, Subject, 
    Priority, TaskStatus, TeacherFeedback, ParentFeedback, MonitoringReport
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    ROADMAP_REVIEW = "roadmap_review"
    PROGRESS_ASSESSMENT = "progress_assessment"
    RECOMMENDATION = "recommendation"
    OBSERVATION = "observation"
    CONCERN = "concern"
    SUGGESTION = "suggestion"

class FeedbackStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"

@dataclass
class Teacher:
    teacher_id: str
    name: str
    subjects: List[Subject]
    email: str
    expertise_level: str  # "beginner", "intermediate", "expert"
    max_students: int = 50
    is_active: bool = True

@dataclass
class Parent:
    parent_id: str
    name: str
    email: str
    student_ids: List[str]
    notification_preferences: Dict[str, bool] = field(default_factory=lambda: {
        "daily_updates": False,
        "weekly_reports": True,
        "urgent_alerts": True,
        "performance_changes": True
    })
    is_active: bool = True

@dataclass
class FeedbackWorkflow:
    workflow_id: str
    student_id: str
    roadmap_id: str
    current_stage: str  # "teacher_review", "parent_validation", "ai_integration", "implementation"
    teacher_feedback: Optional[TeacherFeedback] = None
    parent_feedback: Optional[ParentFeedback] = None
    ai_response: Optional[Dict[str, Any]] = None
    status: FeedbackStatus = FeedbackStatus.PENDING
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

class HITLFramework:
    """
    Human-in-the-Loop framework for integrating teacher and parent oversight
    """
    
    def __init__(self):
        self.teachers = {}
        self.parents = {}
        self.feedback_workflows = {}
        self.notification_system = NotificationSystem()
    
    def register_teacher(self, teacher: Teacher) -> bool:
        """Register a new teacher in the system"""
        try:
            self.teachers[teacher.teacher_id] = teacher
            logger.info(f"Teacher {teacher.name} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Error registering teacher: {str(e)}")
            return False
    
    def register_parent(self, parent: Parent) -> bool:
        """Register a new parent in the system"""
        try:
            self.parents[parent.parent_id] = parent
            logger.info(f"Parent {parent.name} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Error registering parent: {str(e)}")
            return False
    
    def submit_roadmap_for_review(self, student: StudentProfile, roadmap: Roadmap) -> str:
        """Submit a roadmap for teacher and parent review"""
        workflow_id = str(uuid.uuid4())
        
        workflow = FeedbackWorkflow(
            workflow_id=workflow_id,
            student_id=student.student_id,
            roadmap_id=roadmap.roadmap_id,
            current_stage="teacher_review"
        )
        
        self.feedback_workflows[workflow_id] = workflow
        
        # Notify teachers
        self._notify_teachers_for_review(workflow)
        
        logger.info(f"Roadmap {roadmap.roadmap_id} submitted for review")
        return workflow_id
    
    def submit_teacher_feedback(self, teacher_id: str, workflow_id: str, 
                              feedback_type: FeedbackType, content: str, 
                              priority: Priority) -> bool:
        """Submit teacher feedback for a workflow"""
        try:
            if workflow_id not in self.feedback_workflows:
                logger.error(f"Workflow {workflow_id} not found")
                return False
            
            workflow = self.feedback_workflows[workflow_id]
            
            # Create teacher feedback
            teacher_feedback = TeacherFeedback(
                feedback_id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                student_id=workflow.student_id,
                roadmap_id=workflow.roadmap_id,
                feedback_type=feedback_type.value,
                content=content,
                priority=priority
            )
            
            workflow.teacher_feedback = teacher_feedback
            workflow.current_stage = "parent_validation"
            workflow.last_updated = datetime.now()
            
            # Notify parents
            self._notify_parents_for_validation(workflow)
            
            logger.info(f"Teacher feedback submitted for workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting teacher feedback: {str(e)}")
            return False
    
    def submit_parent_feedback(self, parent_id: str, workflow_id: str,
                             feedback_type: FeedbackType, content: str,
                             priority: Priority) -> bool:
        """Submit parent feedback for a workflow"""
        try:
            if workflow_id not in self.feedback_workflows:
                logger.error(f"Workflow {workflow_id} not found")
                return False
            
            workflow = self.feedback_workflows[workflow_id]
            
            # Create parent feedback
            parent_feedback = ParentFeedback(
                feedback_id=str(uuid.uuid4()),
                parent_id=parent_id,
                student_id=workflow.student_id,
                feedback_type=feedback_type.value,
                content=content,
                priority=priority
            )
            
            workflow.parent_feedback = parent_feedback
            workflow.current_stage = "ai_integration"
            workflow.last_updated = datetime.now()
            
            # Process feedback integration
            self._process_feedback_integration(workflow)
            
            logger.info(f"Parent feedback submitted for workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting parent feedback: {str(e)}")
            return False
    
    def _notify_teachers_for_review(self, workflow: FeedbackWorkflow):
        """Notify relevant teachers about roadmap review"""
        # Find teachers who teach subjects in the roadmap
        relevant_teachers = []
        for teacher in self.teachers.values():
            if teacher.is_active:
                # For now, notify all active teachers since we don't have the roadmap object
                # In a real implementation, we would fetch the roadmap by roadmap_id
                relevant_teachers.append(teacher)
        
        # Send notifications
        for teacher in relevant_teachers:
            self.notification_system.send_notification(
                recipient_id=teacher.teacher_id,
                notification_type="roadmap_review",
                title="New Roadmap for Review",
                message=f"Student roadmap requires your review and feedback",
                priority=Priority.MEDIUM
            )
    
    def _notify_parents_for_validation(self, workflow: FeedbackWorkflow):
        """Notify parents about feedback validation"""
        # Find parents of the student
        student_parents = [parent for parent in self.parents.values() 
                          if workflow.student_id in parent.student_ids and parent.is_active]
        
        for parent in student_parents:
            if parent.notification_preferences.get("weekly_reports", True):
                self.notification_system.send_notification(
                    recipient_id=parent.parent_id,
                    notification_type="feedback_validation",
                    title="Teacher Feedback Available",
                    message=f"Teacher has provided feedback on your child's roadmap",
                    priority=Priority.MEDIUM
                )
    
    def _process_feedback_integration(self, workflow: FeedbackWorkflow):
        """Process and integrate teacher and parent feedback"""
        try:
            # Analyze feedback for conflicts
            conflicts = self._analyze_feedback_conflicts(workflow)
            
            if conflicts:
                # Handle conflicts
                resolution = self._resolve_conflicts(workflow, conflicts)
                workflow.ai_response = resolution
            else:
                # Integrate feedback directly
                integration_plan = self._create_integration_plan(workflow)
                workflow.ai_response = integration_plan
            
            workflow.current_stage = "implementation"
            workflow.status = FeedbackStatus.APPROVED
            workflow.last_updated = datetime.now()
            
            logger.info(f"Feedback integration completed for workflow {workflow.workflow_id}")
            
        except Exception as e:
            logger.error(f"Error processing feedback integration: {str(e)}")
            workflow.status = FeedbackStatus.REJECTED
    
    def _analyze_feedback_conflicts(self, workflow: FeedbackWorkflow) -> List[Dict[str, Any]]:
        """Analyze potential conflicts between teacher and parent feedback"""
        conflicts = []
        
        if not workflow.teacher_feedback or not workflow.parent_feedback:
            return conflicts
        
        teacher_content = workflow.teacher_feedback.content.lower()
        parent_content = workflow.parent_feedback.content.lower()
        
        # Check for conflicting recommendations
        conflict_keywords = {
            "more_time": ["less_time", "reduce", "decrease"],
            "less_time": ["more_time", "increase", "extend"],
            "difficult": ["easy", "simple", "basic"],
            "easy": ["difficult", "challenging", "advanced"]
        }
        
        for keyword, opposites in conflict_keywords.items():
            if keyword in teacher_content and any(opp in parent_content for opp in opposites):
                conflicts.append({
                    "type": "time_difficulty_conflict",
                    "teacher_concern": keyword,
                    "parent_concern": next(opp for opp in opposites if opp in parent_content),
                    "description": f"Conflicting views on {keyword} vs {next(opp for opp in opposites if opp in parent_content)}"
                })
        
        return conflicts
    
    def _resolve_conflicts(self, workflow: FeedbackWorkflow, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts between teacher and parent feedback"""
        resolution = {
            "conflicts_detected": len(conflicts),
            "resolution_strategy": "balanced_approach",
            "recommendations": []
        }
        
        for conflict in conflicts:
            if conflict["type"] == "time_difficulty_conflict":
                resolution["recommendations"].append({
                    "action": "gradual_adjustment",
                    "description": "Implement gradual changes to accommodate both perspectives",
                    "timeline": "2-3 weeks",
                    "monitoring": "Weekly progress review"
                })
        
        return resolution
    
    def _create_integration_plan(self, workflow: FeedbackWorkflow) -> Dict[str, Any]:
        """Create integration plan for non-conflicting feedback"""
        plan = {
            "integration_type": "direct_implementation",
            "teacher_recommendations": [],
            "parent_recommendations": [],
            "implementation_steps": []
        }
        
        if workflow.teacher_feedback:
            plan["teacher_recommendations"].append({
                "type": workflow.teacher_feedback.feedback_type,
                "content": workflow.teacher_feedback.content,
                "priority": workflow.teacher_feedback.priority.value
            })
        
        if workflow.parent_feedback:
            plan["parent_recommendations"].append({
                "type": workflow.parent_feedback.feedback_type,
                "content": workflow.parent_feedback.content,
                "priority": workflow.parent_feedback.priority.value
            })
        
        # Create implementation steps
        plan["implementation_steps"] = [
            "Update roadmap based on feedback",
            "Adjust task priorities and timelines",
            "Notify student of changes",
            "Monitor implementation progress"
        ]
        
        return plan
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a feedback workflow"""
        if workflow_id not in self.feedback_workflows:
            return None
        
        workflow = self.feedback_workflows[workflow_id]
        
        return {
            "workflow_id": workflow.workflow_id,
            "student_id": workflow.student_id,
            "roadmap_id": workflow.roadmap_id,
            "current_stage": workflow.current_stage,
            "status": workflow.status.value,
            "has_teacher_feedback": workflow.teacher_feedback is not None,
            "has_parent_feedback": workflow.parent_feedback is not None,
            "created_date": workflow.created_date.isoformat(),
            "last_updated": workflow.last_updated.isoformat()
        }
    
    def get_pending_workflows(self, user_id: str, user_type: str) -> List[Dict[str, Any]]:
        """Get pending workflows for a teacher or parent"""
        pending = []
        
        for workflow in self.feedback_workflows.values():
            if user_type == "teacher" and workflow.current_stage == "teacher_review":
                pending.append(self.get_workflow_status(workflow.workflow_id))
            elif user_type == "parent" and workflow.current_stage == "parent_validation":
                pending.append(self.get_workflow_status(workflow.workflow_id))
        
        return pending

class NotificationSystem:
    """System for managing notifications to teachers and parents"""
    
    def __init__(self):
        self.notifications = []
        self.email_service = EmailService()
    
    def send_notification(self, recipient_id: str, notification_type: str, 
                         title: str, message: str, priority: Priority):
        """Send notification to a user"""
        notification = {
            "notification_id": str(uuid.uuid4()),
            "recipient_id": recipient_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "priority": priority.value,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        
        self.notifications.append(notification)
        
        # Send email if high priority
        if priority in [Priority.HIGH, Priority.CRITICAL]:
            self.email_service.send_email(recipient_id, title, message)
        
        logger.info(f"Notification sent to {recipient_id}: {title}")

class EmailService:
    """Mock email service for sending notifications"""
    
    def send_email(self, recipient_id: str, subject: str, body: str):
        """Send email notification"""
        # In a real implementation, this would integrate with an email service
        logger.info(f"Email sent to {recipient_id}: {subject}")
        logger.info(f"Email body: {body}")

class DashboardManager:
    """Manages dashboard data for teachers and parents"""
    
    def __init__(self, hitl_framework: HITLFramework):
        self.hitl = hitl_framework
    
    def get_teacher_dashboard_data(self, teacher_id: str) -> Dict[str, Any]:
        """Get dashboard data for a teacher"""
        # Get students assigned to this teacher
        teacher = self.hitl.teachers.get(teacher_id)
        if not teacher:
            return {"error": "Teacher not found"}
        
        # Get pending workflows
        pending_workflows = self.hitl.get_pending_workflows(teacher_id, "teacher")
        
        # Get recent feedback
        recent_feedback = self._get_recent_feedback(teacher_id, "teacher")
        
        return {
            "teacher_info": {
                "name": teacher.name,
                "subjects": [s.value for s in teacher.subjects],
                "expertise_level": teacher.expertise_level
            },
            "pending_workflows": pending_workflows,
            "recent_feedback": recent_feedback,
            "total_students": len([w for w in self.hitl.feedback_workflows.values() 
                                 if w.teacher_feedback and w.teacher_feedback.teacher_id == teacher_id])
        }
    
    def get_parent_dashboard_data(self, parent_id: str) -> Dict[str, Any]:
        """Get dashboard data for a parent"""
        parent = self.hitl.parents.get(parent_id)
        if not parent:
            return {"error": "Parent not found"}
        
        # Get pending workflows
        pending_workflows = self.hitl.get_pending_workflows(parent_id, "parent")
        
        # Get recent feedback
        recent_feedback = self._get_recent_feedback(parent_id, "parent")
        
        return {
            "parent_info": {
                "name": parent.name,
                "student_ids": parent.student_ids,
                "notification_preferences": parent.notification_preferences
            },
            "pending_workflows": pending_workflows,
            "recent_feedback": recent_feedback
        }
    
    def _get_recent_feedback(self, user_id: str, user_type: str) -> List[Dict[str, Any]]:
        """Get recent feedback for a user"""
        recent = []
        
        for workflow in self.hitl.feedback_workflows.values():
            if user_type == "teacher" and workflow.teacher_feedback and workflow.teacher_feedback.teacher_id == user_id:
                recent.append({
                    "workflow_id": workflow.workflow_id,
                    "student_id": workflow.student_id,
                    "feedback_type": workflow.teacher_feedback.feedback_type,
                    "content": workflow.teacher_feedback.content[:100] + "...",
                    "created_date": workflow.teacher_feedback.created_date.isoformat()
                })
            elif user_type == "parent" and workflow.parent_feedback and workflow.parent_feedback.parent_id == user_id:
                recent.append({
                    "workflow_id": workflow.workflow_id,
                    "student_id": workflow.student_id,
                    "feedback_type": workflow.parent_feedback.feedback_type,
                    "content": workflow.parent_feedback.content[:100] + "...",
                    "created_date": workflow.parent_feedback.created_date.isoformat()
                })
        
        return sorted(recent, key=lambda x: x["created_date"], reverse=True)[:5]
