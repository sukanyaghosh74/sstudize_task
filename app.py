"""
Main Streamlit application for the Personalized Roadmap Generation System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import uuid
from typing import Dict, List, Optional
import io
from src.pdf_utils import generate_roadmap_pdf

# Import our modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_models import (
    StudentProfile, Subject, Priority, TaskStatus, PerformanceMetric,
    StudyHabit, SWOTAnalysis
)
from ai_roadmap_generator import AIRoadmapGenerator
from monitoring_agents import MonitoringSystem
from hitl_framework import HITLFramework, FeedbackType, DashboardManager, Teacher, Parent
from auth_system import AuthenticationSystem, StreamlitAuthManager, UserRole
from email_service import EmailService, EmailTemplateManager
from database_manager import ProductionDatabaseManager
from data_integration import DataIntegrationManager
from api_integration import APIIntegrationManager

# Page configuration
st.set_page_config(
    page_title="Personalized Roadmap Generation System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'roadmap_generator' not in st.session_state:
    st.session_state.roadmap_generator = AIRoadmapGenerator()
if 'monitoring_system' not in st.session_state:
    st.session_state.monitoring_system = MonitoringSystem()
if 'hitl_framework' not in st.session_state:
    st.session_state.hitl_framework = HITLFramework()
if 'dashboard_manager' not in st.session_state:
    st.session_state.dashboard_manager = DashboardManager(st.session_state.hitl_framework)

# Initialize production services
if 'auth_system' not in st.session_state:
    st.session_state.auth_system = AuthenticationSystem()
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = StreamlitAuthManager(st.session_state.auth_system)
if 'email_service' not in st.session_state:
    st.session_state.email_service = EmailService()
if 'database_manager' not in st.session_state:
    st.session_state.database_manager = ProductionDatabaseManager()
if 'data_integration' not in st.session_state:
    st.session_state.data_integration = DataIntegrationManager()
if 'api_integration' not in st.session_state:
    st.session_state.api_integration = APIIntegrationManager()

def main():
    """Main application function"""
    # Check authentication
    current_user = st.session_state.auth_manager.get_current_user()
    
    if not current_user:
        # Show login/register page
        st.title("🔐 Login to Personalized Roadmap System")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            user = st.session_state.auth_manager.login_form()
            if user:
                st.rerun()
        
        with tab2:
            if st.session_state.auth_manager.register_form():
                st.rerun()
        
        return
    
    # User is authenticated, show main interface
    st.title("📚 Personalized Roadmap Generation System")
    st.markdown(f"Welcome back, **{current_user.username}**! ({current_user.role.value.title()})")
    
    # Sidebar navigation
    navigation_options = ["🏠 Dashboard", "👨‍🎓 Student Management", "🤖 AI Roadmap Generator", "📊 Monitoring & Analytics"]
    
    # Add role-specific pages
    if current_user.role in [UserRole.TEACHER, UserRole.ADMIN]:
        navigation_options.append("👨‍🏫 Teacher Interface")
    if current_user.role in [UserRole.PARENT, UserRole.ADMIN]:
        navigation_options.append("👨‍👩‍👧‍👦 Parent Interface")
    if current_user.role == UserRole.ADMIN:
        navigation_options.extend(["⚙️ System Settings", "🔧 Data Integration", "📧 Email Management"])
    
    # Add logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.auth_manager.logout()
    
    # Role-based navigation
    user_role = st.session_state.get('user_role', 'student')  # Default to student
    
    # Role-based navigation options
    if user_role == 'student':
        navigation_options = [
            "🏠 My Dashboard",
            "🤖 My Roadmap",
            "📈 My Progress Tracker"
        ]
    elif user_role == 'teacher':
        navigation_options = [
            "🏠 Teacher Dashboard",
            "📋 Roadmap Reviews",
            "📊 Student Progress",
            "⚖️ Conflict Resolution"
        ]
    elif user_role == 'parent':
        navigation_options = [
            "🏠 Parent Dashboard",
            "📊 Child Progress",
            "⏰ Study Hours Adjustment",
            "💬 Feedback & Concerns"
        ]
    elif user_role == 'admin':
        navigation_options = [
            "🏠 Admin Dashboard",
            "👥 User Management",
            "⚙️ System Settings",
            "🔧 Data Integration",
            "📧 Email Management",
            "📊 System Analytics",
            "🏗️ System Architecture"
        ]
    else:
        # Fallback for unknown roles
        navigation_options = [
            "🏠 Dashboard",
            "👨‍🎓 Student Management", 
            "🤖 AI Roadmap Generator",
            "📈 Student Progress Tracker",
            "👨‍🏫 Teacher Interface",
            "👨‍👩‍👧‍👦 Parent Interface",
            "📊 Monitoring & Analytics",
            "⚙️ System Settings",
            "🔧 Data Integration",
            "📧 Email Management"
        ]
    
    # Role selector (for demo purposes)
    st.sidebar.subheader("🔐 Role Selection")
    new_role = st.sidebar.selectbox("Switch Role:", 
                                  ["student", "teacher", "parent", "admin"],
                                  index=["student", "teacher", "parent", "admin"].index(user_role))
    
    if new_role != user_role:
        st.session_state['user_role'] = new_role
        st.rerun()
    
    st.sidebar.write(f"**Current Role:** {user_role.title()}")
    
    page = st.sidebar.selectbox("Navigate to:", navigation_options)
    
    # Role-based page routing
    if user_role == 'student':
        if page == "🏠 My Dashboard":
            show_student_dashboard()
        elif page == "🤖 My Roadmap":
            show_student_roadmap()
        elif page == "📈 My Progress Tracker":
            show_student_progress_tracker()
    
    elif user_role == 'teacher':
        if page == "🏠 Teacher Dashboard":
            show_teacher_dashboard()
        elif page == "📋 Roadmap Reviews":
            show_teacher_roadmap_reviews()
        elif page == "📊 Student Progress":
            show_teacher_student_progress()
        elif page == "⚖️ Conflict Resolution":
            show_teacher_conflict_resolution()
    
    elif user_role == 'parent':
        if page == "🏠 Parent Dashboard":
            show_parent_dashboard()
        elif page == "📊 Child Progress":
            show_parent_child_progress()
        elif page == "⏰ Study Hours Adjustment":
            show_parent_study_hours_adjustment()
        elif page == "💬 Feedback & Concerns":
            show_parent_feedback_concerns()
    
    elif user_role == 'admin':
        if page == "🏠 Admin Dashboard":
            show_admin_dashboard()
        elif page == "👥 User Management":
            show_user_management()
        elif page == "⚙️ System Settings":
            show_system_settings()
        elif page == "🔧 Data Integration":
            show_data_integration()
        elif page == "📧 Email Management":
            show_email_management()
        elif page == "📊 System Analytics":
            show_monitoring_analytics()
        elif page == "🏗️ System Architecture":
            show_system_architecture()
    
    # Fallback for legacy pages (for development/testing)
    else:
        if page == "🏠 Dashboard":
            show_dashboard()
        elif page == "👨‍🎓 Student Management":
            show_student_management()
        elif page == "🤖 AI Roadmap Generator":
            show_roadmap_generator()
        elif page == "👨‍🏫 Teacher Interface":
            show_teacher_interface()
        elif page == "👨‍👩‍👧‍👦 Parent Interface":
            show_parent_interface()
        elif page == "📊 Monitoring & Analytics":
            show_monitoring_analytics()
        elif page == "⚙️ System Settings":
            show_system_settings()
        elif page == "🔧 Data Integration":
            show_data_integration()
        elif page == "📧 Email Management":
            show_email_management()
        elif page == "📈 Student Progress Tracker":
            show_student_progress_tracker()

# =============================================================================
# ROLE-BASED DASHBOARD FUNCTIONS
# =============================================================================

def show_student_dashboard():
    """Student-only dashboard with roadmap and progress overview"""
    st.header("🏠 My Dashboard")
    
    # Student info
    student_name = st.session_state.get('current_student', {}).get('name', 'Alex Johnson')
    st.write(f"**Welcome back, {student_name}!**")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Week", "3", "Week 3 of 12")
    with col2:
        st.metric("Tasks Completed", "18", "+3 this week")
    with col3:
        st.metric("Study Hours", "24", "+2 hours")
    with col4:
        st.metric("Performance", "85%", "+5%")
    
    # Recent activity
    st.subheader("📅 Recent Activity")
    activities = [
        "✅ Completed Mathematics practice test - 88%",
        "📚 Finished Physics chapter 5 exercises",
        "⏰ Studied Chemistry for 2 hours",
        "📝 Submitted English essay draft"
    ]
    
    for activity in activities:
        st.info(activity)
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📖 View My Roadmap", type="primary"):
            st.session_state['current_page'] = "🤖 My Roadmap"
            st.rerun()
    
    with col2:
        if st.button("📊 Track Progress"):
            st.session_state['current_page'] = "📈 My Progress Tracker"
            st.rerun()
    
    with col3:
        if st.button("📋 Today's Tasks"):
            st.info("Today's tasks will be displayed here")

def show_student_roadmap():
    """Student-only roadmap view"""
    st.header("🤖 My Roadmap")
    
    # Get current roadmap
    if 'current_roadmap' in st.session_state:
        roadmap = st.session_state['current_roadmap']
        student = st.session_state.get('current_student')
        
        st.write(f"**Your Personalized Study Roadmap**")
        st.write(f"Duration: {roadmap.duration_weeks} weeks")
        
        # Week selector
        current_week = st.slider("Select Week", 1, roadmap.duration_weeks, 1)
        
        if current_week <= len(roadmap.weekly_plans):
            week_plan = roadmap.weekly_plans[current_week - 1]
            
            st.subheader(f"Week {current_week} Plan")
            st.write(f"**Period:** {week_plan.start_date.strftime('%Y-%m-%d')} to {week_plan.end_date.strftime('%Y-%m-%d')}")
            st.write(f"**Total Study Hours:** {week_plan.total_hours}")
            
            # Subject breakdown
            if hasattr(week_plan, 'subject_breakdown') and week_plan.subject_breakdown:
                st.subheader("📚 Subject Breakdown")
                for subject, hours in week_plan.subject_breakdown.items():
                    st.write(f"- **{subject.value}:** {hours} hours")
            
            # Tasks for the week
            st.subheader("📋 This Week's Tasks")
            for i, task in enumerate(week_plan.tasks, 1):
                status_icon = "✅" if task.status.value == 'completed' else "⏳" if task.status.value == 'in_progress' else "📝"
                st.write(f"{status_icon} **{i}. {task.title}**")
                st.write(f"   Subject: {task.subject.value} | Priority: {task.priority.value.title()}")
                st.write(f"   Due: {task.due_date.strftime('%Y-%m-%d')}")
                if task.description:
                    st.write(f"   Description: {task.description}")
                st.write("---")
    else:
        st.info("No roadmap available. Please generate a roadmap first.")

def show_teacher_dashboard():
    """Teacher-only dashboard"""
    st.header("🏠 Teacher Dashboard")
    
    # Teacher metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Students Assigned", "15", "2")
    with col2:
        st.metric("Pending Reviews", "3", "-1")
    with col3:
        st.metric("Feedback Submitted", "12", "3")
    with col4:
        st.metric("Response Time", "2.3 days", "-0.5 days")
    
    # Recent notifications
    st.subheader("🔔 Recent Notifications")
    notifications = [
        "🔴 New roadmap requires review - Alice Johnson",
        "⚠️ Student performance alert - Bob Smith", 
        "📝 Parent feedback received - Carol Davis",
        "📊 Weekly report available - David Wilson",
        "⚖️ Conflict detected - Math study hours - Emma Wilson"
    ]
    
    for notification in notifications:
        st.info(notification)
    
    # Quick actions
    st.subheader("🎯 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Review Roadmaps", type="primary"):
            st.session_state['current_page'] = "📋 Roadmap Reviews"
            st.rerun()
    
    with col2:
        if st.button("📊 Check Progress"):
            st.session_state['current_page'] = "📊 Student Progress"
            st.rerun()
    
    with col3:
        if st.button("⚖️ Resolve Conflicts"):
            st.session_state['current_page'] = "⚖️ Conflict Resolution"
            st.rerun()

def show_teacher_roadmap_reviews():
    """Teacher roadmap review interface"""
    st.header("📋 Roadmap Reviews")
    
    # Get current roadmap for review
    if 'current_roadmap' in st.session_state:
        roadmap = st.session_state['current_roadmap']
        student = st.session_state.get('current_student')
        
        st.write(f"**Reviewing Roadmap for: {student.name if student else 'Alex Johnson'}**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Current Roadmap Structure:**")
            
            # Show weekly breakdown
            for i, week in enumerate(roadmap.weekly_plans[:4]):  # Show first 4 weeks
                with st.expander(f"Week {week.week_number}: {week.start_date.strftime('%Y-%m-%d')} to {week.end_date.strftime('%Y-%m-%d')}"):
                    st.write(f"**Total Hours: {week.total_hours}**")
                    
                    # Subject breakdown
                    if hasattr(week, 'subject_breakdown') and week.subject_breakdown:
                        for subject, hours in week.subject_breakdown.items():
                            st.write(f"- {subject.value}: {hours} hours")
                    
                    # Key tasks
                    st.write("**Key Tasks:**")
                    for task in week.tasks[:3]:  # Show first 3 tasks
                        st.write(f"• {task.title} ({task.subject.value}) - {task.priority.value.title()}")
        
        with col2:
            st.write("**Review Actions:**")
            
            # Approval status
            approval_status = st.selectbox("Approval Status", 
                                         ["Pending Review", "Approved", "Needs Adjustment", "Rejected"],
                                         key="teacher_approval")
            
            # Study hours adjustments
            st.write("**Study Hours Adjustments:**")
            math_adjustment = st.number_input("Math Hours Adjustment", 
                                            min_value=-5.0, max_value=5.0, value=0.0, step=0.5,
                                            help="Positive = increase hours, Negative = decrease hours")
            
            physics_adjustment = st.number_input("Physics Hours Adjustment", 
                                               min_value=-5.0, max_value=5.0, value=0.0, step=0.5)
            
            chemistry_adjustment = st.number_input("Chemistry Hours Adjustment", 
                                                 min_value=-5.0, max_value=5.0, value=0.0, step=0.5)
            
            # Overall feedback
            overall_feedback = st.text_area("Overall Recommendations", 
                                          placeholder="General feedback and suggestions...",
                                          height=100)
            
            if st.button("Submit Review", type="primary"):
                st.success("✅ Review submitted successfully!")
    else:
        st.info("No roadmap available for review.")

def show_teacher_student_progress():
    """Teacher student progress monitoring"""
    st.header("📊 Student Progress")
    
    # Student selection
    student = st.selectbox("Select Student", ["Alex Johnson", "Alice Smith", "Bob Wilson"])
    
    # Progress metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Completion Rate", "78%", "5%")
    with col2:
        st.metric("Adherence Rate", "85%", "2%")
    with col3:
        st.metric("Performance Trend", "↗️ Improving", "8%")
    
    # Performance chart
    performance_data = pd.DataFrame({
        'Week': [f"Week {i}" for i in range(1, 9)],
        'Mathematics': [70, 72, 75, 78, 80, 82, 85, 87],
        'Physics': [65, 67, 70, 72, 75, 77, 80, 82],
        'Chemistry': [68, 70, 72, 74, 76, 78, 80, 82]
    })
    
    fig = px.line(performance_data, x='Week', y=['Mathematics', 'Physics', 'Chemistry'],
                 title="Student Performance Over Time")
    st.plotly_chart(fig, use_container_width=True)

def show_teacher_conflict_resolution():
    """Teacher conflict resolution interface"""
    st.header("⚖️ Conflict Resolution")
    
    # Show conflicts
    st.write("**Active Conflicts:**")
    
    conflicts = [
        {
            'student': 'Alex Johnson',
            'subject': 'Mathematics',
            'teacher_adjustment': '+2 hours',
            'parent_adjustment': '-1 hour',
            'status': 'Pending Resolution',
            'conflict_type': 'Study Hours'
        }
    ]
    
    for conflict in conflicts:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**{conflict['student']} - {conflict['subject']}**")
                st.write(f"Type: {conflict['conflict_type']}")
            
            with col2:
                st.write(f"Teacher: {conflict['teacher_adjustment']}")
                st.write(f"Parent: {conflict['parent_adjustment']}")
            
            with col3:
                if conflict['status'] == 'Pending Resolution':
                    st.warning("⚠️ Pending")
                    if st.button("Resolve", key=f"resolve_{conflict['student']}"):
                        st.success("Conflict resolved!")
                else:
                    st.success("✅ Resolved")
            
            st.divider()

def show_parent_dashboard():
    """Parent-only dashboard"""
    st.header("🏠 Parent Dashboard")
    
    # Child progress overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Study Hours This Week", "28", "5")
    with col2:
        st.metric("Tasks Completed", "15/20", "3")
    with col3:
        st.metric("Performance Trend", "↗️ Improving", "5%")
    
    # Recent updates
    st.subheader("📅 Recent Updates")
    updates = [
        "📊 Child completed Mathematics practice test - 85%",
        "👨‍🏫 Teacher provided feedback on study schedule",
        "📋 Weekly progress report available",
        "📅 Upcoming exam reminder - Physics",
        "⚖️ Study hours conflict detected - Math subject"
    ]
    
    for update in updates:
        st.info(update)
    
    # Quick actions
    st.subheader("🎯 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Progress", type="primary"):
            st.session_state['current_page'] = "📊 Child Progress"
            st.rerun()
    
    with col2:
        if st.button("⏰ Adjust Hours"):
            st.session_state['current_page'] = "⏰ Study Hours Adjustment"
            st.rerun()
    
    with col3:
        if st.button("💬 Send Feedback"):
            st.session_state['current_page'] = "💬 Feedback & Concerns"
            st.rerun()

def show_parent_child_progress():
    """Parent child progress view"""
    st.header("📊 Child Progress")
    
    # Get current roadmap if available
    if 'current_roadmap' in st.session_state:
        roadmap = st.session_state['current_roadmap']
        student = st.session_state.get('current_student')
        
        st.write(f"**Progress for: {student.name if student else 'Alex Johnson'}**")
        
        # Current week selection
        current_week = st.slider("View Week", 1, roadmap.duration_weeks, 1, key="parent_week")
        
        if current_week <= len(roadmap.weekly_plans):
            current_plan = roadmap.weekly_plans[current_week - 1]
            
            # Progress metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_tasks = len(current_plan.tasks)
            completed_tasks = len([t for t in current_plan.tasks if t.status.value == 'completed'])
            pending_tasks = len([t for t in current_plan.tasks if t.status.value == 'pending'])
            overdue_tasks = len([t for t in current_plan.tasks if t.status.value == 'overdue'])
            
            with col1:
                st.metric("Total Tasks", total_tasks)
            with col2:
                st.metric("Completed", completed_tasks)
            with col3:
                st.metric("Pending", pending_tasks)
            with col4:
                if overdue_tasks > 0:
                    st.metric("Overdue", overdue_tasks, delta=None, delta_color="inverse")
                else:
                    st.metric("Overdue", overdue_tasks)
            
            # Progress visualization
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.progress(completion_rate / 100)
            st.write(f"**Overall Completion Rate: {completion_rate:.1f}%**")
    
    # Progress chart
    st.subheader("📈 Academic Progress Over Time")
    progress_data = pd.DataFrame({
        'Week': [f"Week {i}" for i in range(1, 9)],
        'Mathematics': [70, 72, 75, 78, 80, 82, 85, 87],
        'Physics': [65, 67, 70, 72, 75, 77, 80, 82],
        'Chemistry': [68, 70, 72, 74, 76, 78, 80, 82]
    })
    
    fig = px.line(progress_data, x='Week', y=['Mathematics', 'Physics', 'Chemistry'],
                 title="Academic Progress Over Time")
    st.plotly_chart(fig, use_container_width=True)

def show_parent_study_hours_adjustment():
    """Parent study hours adjustment interface"""
    st.header("⏰ Study Hours Adjustment")
    
    st.write("**Adjust your child's study hours for different subjects:**")
    
    with st.form("study_hours_adjustment"):
        st.write("**Current Study Hours (per week):**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_math = st.number_input("Mathematics Hours", 
                                         min_value=0.0, max_value=20.0, value=8.0, step=0.5,
                                         help="Current: 8 hours/week")
            
            current_physics = st.number_input("Physics Hours", 
                                            min_value=0.0, max_value=20.0, value=6.0, step=0.5,
                                            help="Current: 6 hours/week")
        
        with col2:
            current_chemistry = st.number_input("Chemistry Hours", 
                                              min_value=0.0, max_value=20.0, value=5.0, step=0.5,
                                              help="Current: 5 hours/week")
            
            current_biology = st.number_input("Biology Hours", 
                                            min_value=0.0, max_value=20.0, value=4.0, step=0.5,
                                            help="Current: 4 hours/week")
        
        with col3:
            current_english = st.number_input("English Hours", 
                                            min_value=0.0, max_value=20.0, value=3.0, step=0.5,
                                            help="Current: 3 hours/week")
        
        # Adjustment reasoning
        adjustment_reason = st.text_area("Reason for Adjustment", 
                                       placeholder="Please explain why you want to adjust these study hours...",
                                       height=100)
        
        if st.form_submit_button("Submit Study Hours Adjustment", type="primary"):
            st.success("✅ Study hours adjustment submitted successfully!")
            st.info("📧 Teacher will be notified and may need to approve the changes.")

def show_parent_feedback_concerns():
    """Parent feedback and concerns interface"""
    st.header("💬 Feedback & Concerns")
    
    with st.form("parent_feedback"):
        concern_type = st.selectbox("Type", 
                                  ["Observation", "Concern", "Suggestion", "Question", "Study Hours Request"])
        
        subject = st.selectbox("Subject", 
                             ["Mathematics", "Physics", "Chemistry", "Biology", "English", "General", "Study Schedule"])
        
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
        
        content = st.text_area("Your feedback or concern", 
                             placeholder="Please provide detailed feedback about your child's progress, concerns, or suggestions...",
                             height=120)
        
        if st.form_submit_button("Submit Feedback", type="primary"):
            st.success("✅ Your feedback has been submitted to the teacher!")
            st.info("📧 You will receive a response within 2-3 business days.")

def show_admin_dashboard():
    """Admin-only dashboard"""
    st.header("🏠 Admin Dashboard")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", "156", "12")
    with col2:
        st.metric("Active Students", "89", "5")
    with col3:
        st.metric("Teachers", "12", "1")
    with col4:
        st.metric("Parents", "55", "6")
    
    # System status
    st.subheader("🔧 System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Database: Online")
    with col2:
        st.success("✅ Email Service: Active")
    with col3:
        st.warning("⚠️ Backup: Pending")
    
    # Recent activity
    st.subheader("📊 Recent Activity")
    activities = [
        "👤 New student registered - Sarah Wilson",
        "👨‍🏫 Teacher John Smith updated roadmap for 3 students",
        "📧 Email notification sent to 15 parents",
        "💾 System backup completed successfully",
        "🔧 Database maintenance scheduled for tonight"
    ]
    
    for activity in activities:
        st.info(activity)
    
    # Quick actions
    st.subheader("🎯 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👥 Manage Users", type="primary"):
            st.session_state['current_page'] = "👥 User Management"
            st.rerun()
    
    with col2:
        if st.button("⚙️ System Settings"):
            st.session_state['current_page'] = "⚙️ System Settings"
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics"):
            st.session_state['current_page'] = "📊 System Analytics"
            st.rerun()

def show_user_management():
    """Admin user management interface"""
    st.header("👥 User Management")
    
    # User statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", "156")
    with col2:
        st.metric("Students", "89")
    with col3:
        st.metric("Teachers", "12")
    with col4:
        st.metric("Parents", "55")
    
    # User management tabs
    tab1, tab2, tab3 = st.tabs(["All Users", "Add New User", "User Roles"])
    
    with tab1:
        st.subheader("All Users")
        
        # Sample user data
        users_data = pd.DataFrame({
            'Name': ['Alex Johnson', 'Alice Smith', 'Bob Wilson', 'Carol Davis', 'David Brown'],
            'Role': ['Student', 'Student', 'Teacher', 'Parent', 'Parent'],
            'Status': ['Active', 'Active', 'Active', 'Active', 'Inactive'],
            'Last Login': ['2 hours ago', '1 day ago', '3 hours ago', '5 hours ago', '1 week ago'],
            'Actions': ['Edit', 'Edit', 'Edit', 'Edit', 'Edit']
        })
        
        st.dataframe(users_data, use_container_width=True)
    
    with tab2:
        st.subheader("Add New User")
        
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                role = st.selectbox("Role", ["Student", "Teacher", "Parent", "Admin"])
            
            with col2:
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                status = st.selectbox("Status", ["Active", "Inactive"])
            
            if st.form_submit_button("Add User", type="primary"):
                st.success("User added successfully!")
    
    with tab3:
        st.subheader("User Roles & Permissions")
        
        st.write("**Role Permissions:**")
        
        roles_data = pd.DataFrame({
            'Role': ['Student', 'Teacher', 'Parent', 'Admin'],
            'View Roadmap': ['✅', '✅', '❌', '✅'],
            'Edit Roadmap': ['❌', '✅', '❌', '✅'],
            'View Progress': ['✅', '✅', '✅', '✅'],
            'Manage Users': ['❌', '❌', '❌', '✅'],
            'System Settings': ['❌', '❌', '❌', '✅']
        })
        
        st.dataframe(roles_data, use_container_width=True)

def show_dashboard():
    """Display main dashboard"""
    st.header("📊 System Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Students", "12", "3")
    with col2:
        st.metric("Roadmaps Generated", "8", "2")
    with col3:
        st.metric("Pending Reviews", "5", "-1")
    with col4:
        st.metric("System Health", "98%", "2%")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    # Sample activity data
    activity_data = pd.DataFrame({
        'Time': [datetime.now() - timedelta(hours=i) for i in range(10, 0, -1)],
        'Activity': [
            'New roadmap generated for Student A',
            'Teacher feedback submitted',
            'Parent validation completed',
            'Performance alert triggered',
            'Roadmap updated for Student B',
            'New student registered',
            'Weekly report generated',
            'Teacher feedback submitted',
            'Parent validation completed',
            'System maintenance completed'
        ],
        'Type': ['Success', 'Info', 'Success', 'Warning', 'Info', 'Success', 'Info', 'Info', 'Success', 'Info']
    })
    
    for _, row in activity_data.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.write(row['Time'].strftime("%H:%M"))
            with col2:
                st.write(row['Activity'])
            with col3:
                if row['Type'] == 'Success':
                    st.success("✓")
                elif row['Type'] == 'Warning':
                    st.warning("⚠")
                else:
                    st.info("ℹ")

def show_student_management():
    """Student management interface"""
    st.header("👨‍🎓 Student Management")
    
    tab1, tab2, tab3 = st.tabs(["Add New Student", "View Students", "Performance Tracking"])
    
    with tab1:
        st.subheader("Add New Student")
        
        with st.form("student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Student Name")
                age = st.number_input("Age", min_value=10, max_value=25, value=16)
                grade = st.selectbox("Grade", ["9th", "10th", "11th", "12th", "College"])
                learning_style = st.selectbox("Learning Style", ["Visual", "Auditory", "Kinesthetic", "Reading"])
            
            with col2:
                available_hours = st.slider("Available Study Hours/Day", 1.0, 8.0, 4.0)
                preferred_times = st.multiselect("Preferred Study Times", 
                                               ["Morning", "Afternoon", "Evening", "Night"])
            
            st.subheader("Target Scores")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                math_target = st.number_input("Mathematics", min_value=0, max_value=100, value=85)
                physics_target = st.number_input("Physics", min_value=0, max_value=100, value=80)
            
            with col2:
                chemistry_target = st.number_input("Chemistry", min_value=0, max_value=100, value=80)
                biology_target = st.number_input("Biology", min_value=0, max_value=100, value=75)
            
            with col3:
                english_target = st.number_input("English", min_value=0, max_value=100, value=85)
            
            if st.form_submit_button("Add Student"):
                # Create student profile
                student = StudentProfile(
                    student_id=str(uuid.uuid4()),
                    name=name,
                    age=age,
                    grade=grade,
                    target_scores={
                        Subject.MATHEMATICS: math_target,
                        Subject.PHYSICS: physics_target,
                        Subject.CHEMISTRY: chemistry_target,
                        Subject.BIOLOGY: biology_target,
                        Subject.ENGLISH: english_target
                    },
                    current_scores={
                        Subject.MATHEMATICS: 70,
                        Subject.PHYSICS: 65,
                        Subject.CHEMISTRY: 68,
                        Subject.BIOLOGY: 72,
                        Subject.ENGLISH: 75
                    },
                    learning_style=learning_style.lower(),
                    available_hours_per_day=available_hours,
                    preferred_study_times=preferred_times
                )
                
                st.success(f"Student {name} added successfully!")
                st.json({
                    "Student ID": student.student_id,
                    "Name": student.name,
                    "Grade": student.grade,
                    "Learning Style": student.learning_style
                })
    
    with tab2:
        st.subheader("Student List")
        
        # Sample student data
        students_data = pd.DataFrame({
            'Name': ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson'],
            'Grade': ['11th', '12th', '10th', '11th'],
            'Learning Style': ['Visual', 'Auditory', 'Kinesthetic', 'Reading'],
            'Study Hours/Day': [4.0, 5.5, 3.5, 4.5],
            'Overall Progress': [78, 85, 72, 80],
            'Last Active': ['2 hours ago', '1 day ago', '3 hours ago', '5 hours ago']
        })
        
        st.dataframe(students_data, use_container_width=True)
    
    with tab3:
        st.subheader("Performance Tracking")
        
        # Performance chart
        performance_data = pd.DataFrame({
            'Subject': ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English'],
            'Current Score': [75, 68, 72, 70, 78],
            'Target Score': [85, 80, 80, 75, 85]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Current Score', x=performance_data['Subject'], 
                           y=performance_data['Current Score'], marker_color='lightblue'))
        fig.add_trace(go.Bar(name='Target Score', x=performance_data['Subject'], 
                           y=performance_data['Target Score'], marker_color='darkblue'))
        
        fig.update_layout(title="Performance vs Target Scores", barmode='group')
        st.plotly_chart(fig, use_container_width=True)

def show_roadmap_generator():
    """AI Roadmap Generator interface"""
    st.header("🤖 AI Roadmap Generator")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuration")
        # Student selection and input fields
        name = st.text_input("Student Name", value="Alex Johnson")
        age = st.number_input("Age", min_value=10, max_value=25, value=16)
        grade = st.selectbox("Grade", ["9th", "10th", "11th", "12th", "College"], index=2)
        learning_style = st.selectbox("Learning Style", ["Visual", "Auditory", "Kinesthetic", "Reading"])
        available_hours = st.slider("Available Study Hours/Day", 1.0, 8.0, 4.0)
        preferred_times = st.multiselect("Preferred Study Times", ["Morning", "Afternoon", "Evening", "Night"], default=["Morning", "Evening"])
        # Target scores
        math_target = st.number_input("Mathematics Target", min_value=0, max_value=100, value=85)
        physics_target = st.number_input("Physics Target", min_value=0, max_value=100, value=80)
        chemistry_target = st.number_input("Chemistry Target", min_value=0, max_value=100, value=80)
        biology_target = st.number_input("Biology Target", min_value=0, max_value=100, value=75)
        english_target = st.number_input("English Target", min_value=0, max_value=100, value=85)
        duration_weeks = st.slider("Roadmap Duration (weeks)", 4, 16, 12)
        
        if st.button("Generate Roadmap", type="primary"):
            with st.spinner("Generating personalized roadmap..."):
                # Create student profile
                student = StudentProfile(
                    student_id="student_demo",
                    name=name,
                    age=age,
                    grade=grade,
                    target_scores={
                        Subject.MATHEMATICS: math_target,
                        Subject.PHYSICS: physics_target,
                        Subject.CHEMISTRY: chemistry_target,
                        Subject.BIOLOGY: biology_target,
                        Subject.ENGLISH: english_target
                    },
                    current_scores={
                        Subject.MATHEMATICS: 70,
                        Subject.PHYSICS: 65,
                        Subject.CHEMISTRY: 68,
                        Subject.BIOLOGY: 72,
                        Subject.ENGLISH: 75
                    },
                    learning_style=learning_style.lower(),
                    available_hours_per_day=available_hours,
                    preferred_study_times=preferred_times
                )
                # Generate roadmap
                roadmap = st.session_state.roadmap_generator.generate_roadmap(student, duration_weeks=duration_weeks)
                # Store in session
                st.session_state['roadmap_obj'] = roadmap
                st.session_state['roadmap_student'] = student
                st.success("Roadmap generated successfully!")
    
    with col2:
        st.subheader("Generated Roadmap Preview")
        roadmap = st.session_state.get('roadmap_obj')
        student = st.session_state.get('roadmap_student')
        if roadmap and student:
            # Show a summary (optional)
            st.write(f"**Student:** {student.name} | **Grade:** {student.grade}")
            st.write(f"**Duration:** {roadmap.duration_weeks} weeks")
            st.write("**Overall Goals:**")
            for goal in getattr(roadmap, 'overall_goals', []):
                st.write(f"- {goal}")
            # PDF download
            pdf_buffer = io.BytesIO()
            generate_roadmap_pdf(student, roadmap, filename_or_buffer=pdf_buffer)
            pdf_buffer.seek(0)
            st.download_button(
                label="Download Roadmap as PDF",
                data=pdf_buffer,
                file_name=f"{student.name}_roadmap.pdf",
                mime="application/pdf"
            )
        else:
            st.info("No roadmap object found. Please generate a roadmap first.")

def show_teacher_interface():
    """Enhanced Teacher interface with HITL roadmap review and approval system"""
    st.header("👨‍🏫 Teacher Interface - Human-in-the-Loop")
    
    # Teacher login simulation
    teacher_id = st.selectbox("Select Teacher", ["teacher_1", "teacher_2", "teacher_3"])
    
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Roadmap Reviews", "Student Progress", "Conflict Resolution"])
    
    with tab1:
        st.subheader("Teacher Dashboard")
        
        # Teacher info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Students Assigned", "15", "2")
            st.metric("Pending Reviews", "3", "-1")
        with col2:
            st.metric("Feedback Submitted", "12", "3")
            st.metric("Response Time", "2.3 days", "-0.5 days")
        
        # Recent notifications
        st.subheader("Recent Notifications")
        notifications = [
            "🔴 New roadmap requires review - Alice Johnson",
            "⚠️ Student performance alert - Bob Smith", 
            "📝 Parent feedback received - Carol Davis",
            "📊 Weekly report available - David Wilson",
            "⚖️ Conflict detected - Math study hours - Emma Wilson"
        ]
        
        for notification in notifications:
            st.info(notification)
    
    with tab2:
        st.subheader("📋 Roadmap Review & Approval System")
        
        # Get current roadmap for review
        if 'current_roadmap' in st.session_state:
            roadmap = st.session_state['current_roadmap']
            student = st.session_state.get('current_student')
            
            st.write(f"**Reviewing Roadmap for: {student.name if student else 'Alex Johnson'}**")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Current Roadmap Structure:**")
                
                # Show weekly breakdown
                for i, week in enumerate(roadmap.weekly_plans[:4]):  # Show first 4 weeks
                    with st.expander(f"Week {week.week_number}: {week.start_date.strftime('%Y-%m-%d')} to {week.end_date.strftime('%Y-%m-%d')}"):
                        st.write(f"**Total Hours: {week.total_hours}**")
                        
                        # Subject breakdown
                        if hasattr(week, 'subject_breakdown') and week.subject_breakdown:
                            for subject, hours in week.subject_breakdown.items():
                                st.write(f"- {subject.value}: {hours} hours")
                        
                        # Key tasks
                        st.write("**Key Tasks:**")
                        for task in week.tasks[:3]:  # Show first 3 tasks
                            st.write(f"• {task.title} ({task.subject.value}) - {task.priority.value.title()}")
            
            with col2:
                st.write("**Review Actions:**")
                
                # Approval status
                approval_status = st.selectbox("Approval Status", 
                                             ["Pending Review", "Approved", "Needs Adjustment", "Rejected"],
                                             key="teacher_approval")
                
                # Detailed feedback
                st.write("**Feedback Categories:**")
                
                # Subject-specific feedback
                math_feedback = st.text_area("Mathematics Feedback", 
                                           placeholder="Comments on Math study plan...",
                                           height=60)
                
                physics_feedback = st.text_area("Physics Feedback", 
                                              placeholder="Comments on Physics study plan...",
                                              height=60)
                
                chemistry_feedback = st.text_area("Chemistry Feedback", 
                                                placeholder="Comments on Chemistry study plan...",
                                                height=60)
                
                # Overall recommendations
                overall_feedback = st.text_area("Overall Recommendations", 
                                              placeholder="General feedback and suggestions...",
                                              height=100)
                
                # Study hours adjustments
                st.write("**Study Hours Adjustments:**")
                math_adjustment = st.number_input("Math Hours Adjustment", 
                                                min_value=-5.0, max_value=5.0, value=0.0, step=0.5,
                                                help="Positive = increase hours, Negative = decrease hours")
                
                physics_adjustment = st.number_input("Physics Hours Adjustment", 
                                                   min_value=-5.0, max_value=5.0, value=0.0, step=0.5)
                
                chemistry_adjustment = st.number_input("Chemistry Hours Adjustment", 
                                                     min_value=-5.0, max_value=5.0, value=0.0, step=0.5)
                
                # Priority level
                priority = st.selectbox("Review Priority", ["Low", "Medium", "High", "Urgent"])
                
                if st.button("Submit Review", type="primary"):
                    # Store teacher feedback
                    teacher_feedback = {
                        'teacher_id': teacher_id,
                        'approval_status': approval_status,
                        'math_feedback': math_feedback,
                        'physics_feedback': physics_feedback,
                        'chemistry_feedback': chemistry_feedback,
                        'overall_feedback': overall_feedback,
                        'math_adjustment': math_adjustment,
                        'physics_adjustment': physics_adjustment,
                        'chemistry_adjustment': chemistry_adjustment,
                        'priority': priority,
                        'timestamp': datetime.now()
                    }
                    
                    st.session_state['teacher_feedback'] = teacher_feedback
                    st.success("✅ Review submitted successfully!")
                    
                    if approval_status == "Needs Adjustment":
                        st.warning("⚠️ Roadmap flagged for adjustment. Student and parent will be notified.")
                    elif approval_status == "Rejected":
                        st.error("❌ Roadmap rejected. New roadmap generation required.")
        else:
            st.info("No roadmap available for review. Please generate a roadmap first.")
    
    with tab3:
        st.subheader("📊 Student Progress Monitoring")
        
        # Student selection
        student = st.selectbox("Select Student", ["Alex Johnson", "Alice Smith", "Bob Wilson"], key="teacher_student_select")
        
        # Progress metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Completion Rate", "78%", "5%")
        with col2:
            st.metric("Adherence Rate", "85%", "2%")
        with col3:
            st.metric("Performance Trend", "↗️ Improving", "8%")
        
        # Performance chart
        performance_data = pd.DataFrame({
            'Week': [f"Week {i}" for i in range(1, 9)],
            'Mathematics': [70, 72, 75, 78, 80, 82, 85, 87],
            'Physics': [65, 67, 70, 72, 75, 77, 80, 82],
            'Chemistry': [68, 70, 72, 74, 76, 78, 80, 82]
        })
        
        fig = px.line(performance_data, x='Week', y=['Mathematics', 'Physics', 'Chemistry'],
                     title="Student Performance Over Time")
        st.plotly_chart(fig, use_container_width=True)
        
        # Teacher interventions
        st.subheader("🎯 Teacher Interventions")
        
        with st.form("teacher_intervention"):
            intervention_type = st.selectbox("Intervention Type", 
                                           ["Additional Support", "Schedule Adjustment", "Resource Recommendation", "Parent Meeting"])
            subject = st.selectbox("Subject", ["Mathematics", "Physics", "Chemistry", "Biology", "English", "General"])
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Urgent"])
            description = st.text_area("Intervention Description", height=100)
            
            if st.form_submit_button("Submit Intervention"):
                st.success("Intervention submitted successfully!")
    
    with tab4:
        st.subheader("⚖️ Conflict Resolution")
        
        # Show conflicts between teacher and parent feedback
        st.write("**Active Conflicts:**")
        
        conflicts = [
            {
                'student': 'Alex Johnson',
                'subject': 'Mathematics',
                'teacher_adjustment': '+2 hours',
                'parent_adjustment': '-1 hour',
                'status': 'Pending Resolution',
                'conflict_type': 'Study Hours'
            },
            {
                'student': 'Alice Smith', 
                'subject': 'Physics',
                'teacher_adjustment': 'Increase difficulty',
                'parent_adjustment': 'Reduce workload',
                'status': 'Resolved',
                'conflict_type': 'Difficulty Level'
            }
        ]
        
        for conflict in conflicts:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**{conflict['student']} - {conflict['subject']}**")
                    st.write(f"Type: {conflict['conflict_type']}")
                
                with col2:
                    st.write(f"Teacher: {conflict['teacher_adjustment']}")
                    st.write(f"Parent: {conflict['parent_adjustment']}")
                
                with col3:
                    if conflict['status'] == 'Pending Resolution':
                        st.warning("⚠️ Pending")
                        if st.button("Resolve", key=f"resolve_{conflict['student']}"):
                            st.success("Conflict resolved!")
                    else:
                        st.success("✅ Resolved")
                
                st.divider()
        
        # Conflict resolution interface
        st.subheader("🔧 Manual Conflict Resolution")
        
        with st.form("conflict_resolution"):
            student_name = st.selectbox("Student", ["Alex Johnson", "Alice Smith", "Bob Wilson"], key="conflict_student")
            conflict_subject = st.selectbox("Subject", ["Mathematics", "Physics", "Chemistry", "Biology", "English"])
            
            st.write("**Resolution Options:**")
            resolution_type = st.radio("Resolution Type", 
                                     ["Accept Teacher Recommendation", 
                                      "Accept Parent Recommendation", 
                                      "Compromise Solution", 
                                      "Manual Override"])
            
            if resolution_type == "Compromise Solution":
                compromise_hours = st.number_input("Compromise Study Hours", 
                                                 min_value=0.0, max_value=10.0, value=2.0, step=0.5)
                compromise_reason = st.text_area("Compromise Reasoning", height=80)
            elif resolution_type == "Manual Override":
                manual_hours = st.number_input("Manual Study Hours", 
                                             min_value=0.0, max_value=10.0, value=2.0, step=0.5)
                override_reason = st.text_area("Override Reasoning", height=80)
            
            if st.form_submit_button("Apply Resolution"):
                st.success("Conflict resolution applied successfully!")
                st.info("All parties will be notified of the resolution.")

def show_parent_interface():
    """Enhanced Parent interface with HITL progress viewing and study hours adjustment"""
    st.header("👨‍👩‍👧‍👦 Parent Interface - Human-in-the-Loop")
    
    # Parent login simulation
    parent_id = st.selectbox("Select Parent", ["parent_1", "parent_2", "parent_3"])
    
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Child Progress", "Study Hours Adjustment", "Feedback & Concerns"])
    
    with tab1:
        st.subheader("Parent Dashboard")
        
        # Child progress overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Study Hours This Week", "28", "5")
        with col2:
            st.metric("Tasks Completed", "15/20", "3")
        with col3:
            st.metric("Performance Trend", "↗️ Improving", "5%")
        
        # Recent updates
        st.subheader("Recent Updates")
        updates = [
            "📊 Child completed Mathematics practice test - 85%",
            "👨‍🏫 Teacher provided feedback on study schedule",
            "📋 Weekly progress report available",
            "📅 Upcoming exam reminder - Physics",
            "⚖️ Study hours conflict detected - Math subject"
        ]
        
        for update in updates:
            st.info(update)
    
    with tab2:
        st.subheader("📊 Child Progress Tracking")
        
        # Get current roadmap if available
        if 'current_roadmap' in st.session_state:
            roadmap = st.session_state['current_roadmap']
            student = st.session_state.get('current_student')
            
            st.write(f"**Progress for: {student.name if student else 'Alex Johnson'}**")
            
            # Current week selection
            current_week = st.slider("View Week", 1, roadmap.duration_weeks, 1, key="parent_week")
            
            if current_week <= len(roadmap.weekly_plans):
                current_plan = roadmap.weekly_plans[current_week - 1]
                
                # Progress metrics
                col1, col2, col3, col4 = st.columns(4)
                
                total_tasks = len(current_plan.tasks)
                completed_tasks = len([t for t in current_plan.tasks if t.status.value == 'completed'])
                pending_tasks = len([t for t in current_plan.tasks if t.status.value == 'pending'])
                overdue_tasks = len([t for t in current_plan.tasks if t.status.value == 'overdue'])
                
                with col1:
                    st.metric("Total Tasks", total_tasks)
                with col2:
                    st.metric("Completed", completed_tasks)
                with col3:
                    st.metric("Pending", pending_tasks)
                with col4:
                    if overdue_tasks > 0:
                        st.metric("Overdue", overdue_tasks, delta=None, delta_color="inverse")
                    else:
                        st.metric("Overdue", overdue_tasks)
                
                # Progress visualization
                completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                st.progress(completion_rate / 100)
                st.write(f"**Overall Completion Rate: {completion_rate:.1f}%**")
                
                # Subject breakdown
                st.subheader("📚 Subject Breakdown")
                if hasattr(current_plan, 'subject_breakdown') and current_plan.subject_breakdown:
                    subject_data = []
                    for subject, hours in current_plan.subject_breakdown.items():
                        subject_data.append({
                            'Subject': subject.value,
                            'Study Hours': hours,
                            'Completion': f"{completed_tasks}/{total_tasks}"
                        })
                    
                    subject_df = pd.DataFrame(subject_data)
                    st.dataframe(subject_df, use_container_width=True)
        
        # Progress chart
        st.subheader("📈 Academic Progress Over Time")
        progress_data = pd.DataFrame({
            'Week': [f"Week {i}" for i in range(1, 9)],
            'Mathematics': [70, 72, 75, 78, 80, 82, 85, 87],
            'Physics': [65, 67, 70, 72, 75, 77, 80, 82],
            'Chemistry': [68, 70, 72, 74, 76, 78, 80, 82]
        })
        
        fig = px.line(progress_data, x='Week', y=['Mathematics', 'Physics', 'Chemistry'],
                     title="Academic Progress Over Time")
        st.plotly_chart(fig, use_container_width=True)
        
        # Study habits
        st.subheader("📅 Study Habits")
        habits_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Study Hours': [4, 3.5, 5, 4.5, 3, 2, 1],
            'Focus Quality': [8, 7, 9, 8, 6, 7, 5]
        })
        
        fig2 = px.bar(habits_data, x='Day', y='Study Hours', 
                     title="Daily Study Hours")
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.subheader("⏰ Study Hours Adjustment")
        
        st.write("**Adjust your child's study hours for different subjects:**")
        
        # Get current roadmap for adjustment
        if 'current_roadmap' in st.session_state:
            roadmap = st.session_state['current_roadmap']
            
            with st.form("study_hours_adjustment"):
                st.write("**Current Study Hours (per week):**")
                
                # Show current hours
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    current_math = st.number_input("Mathematics Hours", 
                                                 min_value=0.0, max_value=20.0, value=8.0, step=0.5,
                                                 help="Current: 8 hours/week")
                    
                    current_physics = st.number_input("Physics Hours", 
                                                    min_value=0.0, max_value=20.0, value=6.0, step=0.5,
                                                    help="Current: 6 hours/week")
                
                with col2:
                    current_chemistry = st.number_input("Chemistry Hours", 
                                                      min_value=0.0, max_value=20.0, value=5.0, step=0.5,
                                                      help="Current: 5 hours/week")
                    
                    current_biology = st.number_input("Biology Hours", 
                                                    min_value=0.0, max_value=20.0, value=4.0, step=0.5,
                                                    help="Current: 4 hours/week")
                
                with col3:
                    current_english = st.number_input("English Hours", 
                                                    min_value=0.0, max_value=20.0, value=3.0, step=0.5,
                                                    help="Current: 3 hours/week")
                
                # Adjustment reasoning
                adjustment_reason = st.text_area("Reason for Adjustment", 
                                               placeholder="Please explain why you want to adjust these study hours...",
                                               height=100)
                
                # Priority level
                priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "Urgent"])
                
                if st.form_submit_button("Submit Study Hours Adjustment", type="primary"):
                    # Store parent adjustment
                    parent_adjustment = {
                        'parent_id': parent_id,
                        'math_hours': current_math,
                        'physics_hours': current_physics,
                        'chemistry_hours': current_chemistry,
                        'biology_hours': current_biology,
                        'english_hours': current_english,
                        'reason': adjustment_reason,
                        'priority': priority,
                        'timestamp': datetime.now()
                    }
                    
                    st.session_state['parent_adjustment'] = parent_adjustment
                    st.success("✅ Study hours adjustment submitted successfully!")
                    st.info("📧 Teacher will be notified and may need to approve the changes.")
                    
                    # Check for conflicts with teacher feedback
                    if 'teacher_feedback' in st.session_state:
                        teacher_feedback = st.session_state['teacher_feedback']
                        
                        # Simple conflict detection
                        conflicts = []
                        if abs(teacher_feedback.get('math_adjustment', 0) - (current_math - 8.0)) > 1.0:
                            conflicts.append("Mathematics hours conflict detected")
                        if abs(teacher_feedback.get('physics_adjustment', 0) - (current_physics - 6.0)) > 1.0:
                            conflicts.append("Physics hours conflict detected")
                        
                        if conflicts:
                            st.warning("⚠️ **Conflicts Detected:**")
                            for conflict in conflicts:
                                st.warning(f"- {conflict}")
                            st.info("🔧 Manual resolution may be required.")
        else:
            st.info("No roadmap available. Please generate a roadmap first to adjust study hours.")
    
    with tab4:
        st.subheader("💬 Feedback & Concerns")
        
        with st.form("parent_feedback"):
            concern_type = st.selectbox("Type", 
                                      ["Observation", "Concern", "Suggestion", "Question", "Study Hours Request"],
                                      help="Select the type of feedback you want to provide")
            
            subject = st.selectbox("Subject", 
                                 ["Mathematics", "Physics", "Chemistry", "Biology", "English", "General", "Study Schedule"])
            
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
            
            content = st.text_area("Your feedback or concern", 
                                 placeholder="Please provide detailed feedback about your child's progress, concerns, or suggestions...",
                                 height=120)
            
            # Additional options for study-related feedback
            if concern_type == "Study Hours Request":
                st.write("**Study Hours Adjustment Request:**")
                col1, col2 = st.columns(2)
                with col1:
                    increase_subject = st.selectbox("Increase hours for", 
                                                  ["Mathematics", "Physics", "Chemistry", "Biology", "English"])
                    increase_hours = st.number_input("Additional hours", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
                
                with col2:
                    decrease_subject = st.selectbox("Decrease hours for", 
                                                  ["None", "Mathematics", "Physics", "Chemistry", "Biology", "English"])
                    if decrease_subject != "None":
                        decrease_hours = st.number_input("Reduce hours", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
            
            if st.form_submit_button("Submit Feedback", type="primary"):
                st.success("✅ Your feedback has been submitted to the teacher!")
                st.info("📧 You will receive a response within 2-3 business days.")
                
                # Store parent feedback
                parent_feedback = {
                    'parent_id': parent_id,
                    'concern_type': concern_type,
                    'subject': subject,
                    'priority': priority,
                    'content': content,
                    'timestamp': datetime.now()
                }
                
                if concern_type == "Study Hours Request":
                    parent_feedback.update({
                        'increase_subject': increase_subject,
                        'increase_hours': increase_hours,
                        'decrease_subject': decrease_subject,
                        'decrease_hours': decrease_hours if decrease_subject != "None" else 0
                    })
                
                st.session_state['parent_feedback'] = parent_feedback

def show_monitoring_analytics():
    """Monitoring and analytics interface"""
    st.header("📊 Monitoring & Analytics")
    
    tab1, tab2, tab3 = st.tabs(["System Overview", "Agent Status", "Performance Analytics"])
    
    with tab1:
        st.subheader("System Overview")
        
        # System metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Agents", "3", "0")
        with col2:
            st.metric("Roadmaps Monitored", "12", "2")
        with col3:
            st.metric("Alerts Generated", "8", "-2")
        with col4:
            st.metric("System Uptime", "99.8%", "0.1%")
        
        # Recent alerts
        st.subheader("Recent Alerts")
        alerts = [
            {"time": "2 hours ago", "type": "Warning", "message": "Low completion rate detected for Student A"},
            {"time": "4 hours ago", "type": "Info", "message": "Weekly report generated for Student B"},
            {"time": "6 hours ago", "type": "Success", "message": "Performance improvement detected for Student C"},
            {"time": "1 day ago", "type": "Warning", "message": "Study habit irregularity detected for Student D"}
        ]
        
        for alert in alerts:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.write(alert["time"])
                with col2:
                    st.write(alert["message"])
                with col3:
                    if alert["type"] == "Warning":
                        st.warning("⚠")
                    elif alert["type"] == "Success":
                        st.success("✓")
                    else:
                        st.info("ℹ")
    
    with tab2:
        st.subheader("Agent Status")
        
        # Agent status table
        agent_data = pd.DataFrame({
            'Agent': ['Progress Tracking', 'Performance Analysis', 'Study Habits'],
            'Status': ['Active', 'Active', 'Active'],
            'Last Run': ['2 minutes ago', '5 minutes ago', '3 minutes ago'],
            'Tasks Processed': [156, 89, 234],
            'Errors': [0, 0, 1]
        })
        
        st.dataframe(agent_data, use_container_width=True)
        
        # Agent controls
        st.subheader("Agent Controls")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Restart All Agents"):
                st.success("All agents restarted!")
        
        with col2:
            if st.button("Generate Reports"):
                st.success("Reports generated!")
        
        with col3:
            if st.button("Clear Alerts"):
                st.success("Alerts cleared!")
    
    with tab3:
        st.subheader("Performance Analytics")
        
        # Performance trends
        performance_trends = pd.DataFrame({
            'Week': [f"Week {i}" for i in range(1, 13)],
            'Average Score': [72, 74, 76, 78, 79, 81, 82, 83, 84, 85, 86, 87],
            'Completion Rate': [0.65, 0.68, 0.72, 0.75, 0.78, 0.80, 0.82, 0.84, 0.85, 0.87, 0.88, 0.90]
        })
        
        fig = px.line(performance_trends, x='Week', y=['Average Score', 'Completion Rate'],
                     title="System Performance Trends")
        st.plotly_chart(fig, use_container_width=True)
        
        # Subject performance
        subject_performance = pd.DataFrame({
            'Subject': ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English'],
            'Improvement': [15, 12, 18, 10, 8],
            'Students': [12, 10, 8, 6, 9]
        })
        
        fig2 = px.bar(subject_performance, x='Subject', y='Improvement',
                     title="Subject-wise Performance Improvement")
        st.plotly_chart(fig2, use_container_width=True)

def show_system_settings():
    """System settings page for admins"""
    st.header("⚙️ System Settings")
    
    tab1, tab2, tab3 = st.tabs(["Database", "Authentication", "System Info"])
    
    with tab1:
        st.subheader("Database Configuration")
        
        # Test database connection
        if st.button("Test Database Connection"):
            with st.spinner("Testing connection..."):
                result = st.session_state.database_manager.test_connection()
                if result["status"] == "success":
                    st.success("✅ Database connection successful!")
                    st.json(result["connection_info"])
                else:
                    st.error(f"❌ Database connection failed: {result['error']}")
        
        # Create tables
        if st.button("Create/Update Database Tables"):
            with st.spinner("Creating tables..."):
                success = st.session_state.database_manager.create_tables()
                if success:
                    st.success("✅ Database tables created successfully!")
                else:
                    st.error("❌ Failed to create database tables")
    
    with tab2:
        st.subheader("Authentication Settings")
        
        # User management
        st.write("**User Management**")
        if st.button("View All Users"):
            # This would show all users in a table
            st.info("User management interface would be implemented here")
        
        # Password reset
        st.write("**Password Reset**")
        email = st.text_input("User Email for Password Reset")
        if st.button("Send Password Reset"):
            if email:
                token = st.session_state.auth_system.create_password_reset_token(email)
                if token:
                    st.success(f"Password reset token created: {token}")
                else:
                    st.error("Failed to create password reset token")
    
    with tab3:
        st.subheader("System Information")
        
        # System metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Users", "12", "3")
        with col2:
            st.metric("Database Status", "Connected", "✅")
        with col3:
            st.metric("Email Service", "Configured", "✅")
        
        # System logs
        st.write("**Recent System Logs**")
        st.text_area("Logs", "System logs would be displayed here", height=200)

def show_data_integration():
    """Data integration page for admins"""
    st.header("🔧 Data Integration")
    
    tab1, tab2, tab3 = st.tabs(["School Data", "LMS Integration", "Sync Status"])
    
    with tab1:
        st.subheader("School Data Sources")
        
        # Test data sources
        if st.button("Test All Data Sources"):
            with st.spinner("Testing data sources..."):
                results = st.session_state.data_integration.sync_all_data()
                st.json(results)
        
        # Manual sync
        if st.button("Sync All Data"):
            with st.spinner("Syncing data..."):
                results = st.session_state.data_integration.sync_all_data()
                if "error" not in results:
                    st.success(f"✅ Synced {results['students_synced']} students, {results['teachers_synced']} teachers")
                else:
                    st.error(f"❌ Sync failed: {results['error']}")
    
    with tab2:
        st.subheader("🔗 LMS Integration")
        
        # LMS status overview
        st.write("**Learning Management System Integration**")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Canvas", "Connected", "✅")
        with col2:
            st.metric("Moodle", "Connected", "✅")
        with col3:
            st.metric("Blackboard", "Pending", "⚠️")
        with col4:
            st.metric("Schoology", "Not Configured", "❌")
        
        # LMS Integration Cards
        st.subheader("📚 Available LMS Platforms")
        
        # Canvas Integration
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write("**🎨 Canvas by Instructure**")
                st.write("Connect to Canvas LMS for seamless grade and assignment synchronization")
                st.write("• Sync student grades and assignments")
                st.write("• Import course materials and resources")
                st.write("• Export progress reports to Canvas")
            
            with col2:
                canvas_status = "Connected" if True else "Disconnected"
                st.write(f"**Status:** {canvas_status}")
                if canvas_status == "Connected":
                    st.success("✅ Active")
                else:
                    st.error("❌ Inactive")
            
            with col3:
                if st.button("🔧 Configure Canvas", key="canvas_config"):
                    st.info("Canvas configuration panel would open here")
                if st.button("📊 Test Connection", key="canvas_test"):
                    st.success("✅ Canvas connection successful!")
        
        st.divider()
        
        # Moodle Integration
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write("**🌙 Moodle LMS**")
                st.write("Integrate with Moodle for comprehensive learning management")
                st.write("• Import course structures and content")
                st.write("• Sync student progress and grades")
                st.write("• Export roadmaps to Moodle courses")
            
            with col2:
                moodle_status = "Connected" if True else "Disconnected"
                st.write(f"**Status:** {moodle_status}")
                if moodle_status == "Connected":
                    st.success("✅ Active")
                else:
                    st.error("❌ Inactive")
            
            with col3:
                if st.button("🔧 Configure Moodle", key="moodle_config"):
                    st.info("Moodle configuration panel would open here")
                if st.button("📊 Test Connection", key="moodle_test"):
                    st.success("✅ Moodle connection successful!")
        
        st.divider()
        
        # Blackboard Integration
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write("**📋 Blackboard Learn**")
                st.write("Connect to Blackboard Learn for enterprise-level integration")
                st.write("• Import student rosters and courses")
                st.write("• Sync grades and assignments")
                st.write("• Export analytics and reports")
            
            with col2:
                blackboard_status = "Pending" if True else "Connected"
                st.write(f"**Status:** {blackboard_status}")
                if blackboard_status == "Connected":
                    st.success("✅ Active")
                else:
                    st.warning("⚠️ Pending Setup")
            
            with col3:
                if st.button("🔧 Configure Blackboard", key="blackboard_config"):
                    st.info("Blackboard configuration panel would open here")
                if st.button("📊 Test Connection", key="blackboard_test"):
                    st.warning("⚠️ Blackboard connection failed. Please check credentials.")
        
        st.divider()
        
        # Schoology Integration
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write("**🎓 Schoology**")
                st.write("Integrate with Schoology for K-12 focused learning management")
                st.write("• Import student and parent accounts")
                st.write("• Sync grades and attendance")
                st.write("• Export progress reports to parents")
            
            with col2:
                schoology_status = "Not Configured"
                st.write(f"**Status:** {schoology_status}")
                st.error("❌ Not Set Up")
            
            with col3:
                if st.button("🔧 Configure Schoology", key="schoology_config"):
                    st.info("Schoology configuration panel would open here")
                if st.button("📊 Test Connection", key="schoology_test"):
                    st.error("❌ Schoology not configured yet")
        
        # Integration Settings
        st.subheader("⚙️ Integration Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Global Settings:**")
            auto_sync = st.checkbox("Enable Auto-Sync", value=True, help="Automatically sync data every hour")
            sync_frequency = st.selectbox("Sync Frequency", ["Every 15 minutes", "Every hour", "Every 6 hours", "Daily"], index=1)
            backup_data = st.checkbox("Backup Data Before Sync", value=True)
            notify_errors = st.checkbox("Notify on Sync Errors", value=True)
        
        with col2:
            st.write("**Data Mapping:**")
            grade_mapping = st.selectbox("Grade Mapping", ["A-F Scale", "0-100 Scale", "Custom Scale"], index=1)
            date_format = st.selectbox("Date Format", ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"], index=2)
            timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "CST"], index=0)
        
        # Integration Actions
        st.subheader("🚀 Integration Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Sync All Data", type="primary"):
                with st.spinner("Syncing data from all LMS platforms..."):
                    st.success("✅ Canvas: 45 students synced")
                    st.success("✅ Moodle: 32 students synced")
                    st.warning("⚠️ Blackboard: Sync failed")
                    st.info("📊 Total: 77 students synced successfully")
        
        with col2:
            if st.button("📊 Generate Report"):
                st.info("📋 Integration report generated")
                st.download_button("📄 Download Report", "integration_report.pdf", "application/pdf")
        
        with col3:
            if st.button("🔍 Check Status"):
                st.info("🔍 Checking all LMS connections...")
                st.success("✅ Canvas: Online")
                st.success("✅ Moodle: Online")
                st.error("❌ Blackboard: Offline")
                st.error("❌ Schoology: Not configured")
        
        with col4:
            if st.button("⚙️ Advanced Settings"):
                st.info("🔧 Advanced integration settings would open here")
    
    with tab3:
        st.subheader("Sync Status")
        
        # Show sync statistics
        st.write("**Last Sync Information**")
        st.info("Sync status information would be displayed here")

def show_email_management():
    """Email management page for admins"""
    st.header("📧 Email Management")
    
    tab1, tab2, tab3 = st.tabs(["Email Settings", "Send Test Email", "Email Templates"])
    
    with tab1:
        st.subheader("Email Service Configuration")
        
        # Test email service
        if st.button("Test Email Service"):
            with st.spinner("Testing email service..."):
                # This would test the email service configuration
                st.info("Email service test would be implemented here")
        
        # Email statistics
        st.write("**Email Statistics**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Emails Sent Today", "24", "5")
        with col2:
            st.metric("Success Rate", "98%", "2%")
        with col3:
            st.metric("Pending Queue", "3", "-1")
    
    with tab2:
        st.subheader("Send Test Email")
        
        with st.form("test_email_form"):
            to_email = st.text_input("To Email")
            subject = st.text_input("Subject", "Test Email from Roadmap System")
            message = st.text_area("Message", "This is a test email from the Personalized Roadmap Generation System.")
            
            if st.form_submit_button("Send Test Email"):
                if to_email and subject and message:
                    success = st.session_state.email_service.send_email(to_email, subject, message)
                    if success:
                        st.success("✅ Test email sent successfully!")
                    else:
                        st.error("❌ Failed to send test email")
                else:
                    st.error("Please fill in all fields")
    
    with tab3:
        st.subheader("Email Templates")
        
        # Template management
        st.write("**Available Templates**")
        templates = ["Welcome", "Roadmap Created", "Progress Report", "Teacher Feedback", "Parent Notification", "Weekly Report"]
        
        selected_template = st.selectbox("Select Template", templates)
        if selected_template:
            st.write(f"**{selected_template} Template**")
            st.text_area("Template Content", f"Template content for {selected_template} would be displayed here", height=200)
    
    with tab4:
        st.subheader("📧 Weekly Report Notifications")
        
        st.write("**Automated Weekly Report Distribution**")
        
        # Weekly report settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Notification Settings:**")
            
            # Enable/disable notifications
            enable_weekly_reports = st.checkbox("Enable Weekly Report Notifications", value=True)
            
            # Day of week selection
            report_day = st.selectbox("Send Reports On", 
                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                    index=0)
            
            # Time selection
            report_time = st.time_input("Send Time", value=datetime.now().time())
            
            # Recipients
            st.write("**Recipients:**")
            send_to_teachers = st.checkbox("Send to Teachers", value=True)
            send_to_parents = st.checkbox("Send to Parents", value=True)
            send_to_students = st.checkbox("Send to Students", value=False)
        
        with col2:
            st.write("**Report Content:**")
            
            # Report content options
            include_progress = st.checkbox("Include Progress Metrics", value=True)
            include_tasks = st.checkbox("Include Task Completion", value=True)
            include_irregularities = st.checkbox("Include Irregularities", value=True)
            include_recommendations = st.checkbox("Include Recommendations", value=True)
            
            # Email template selection
            template_choice = st.selectbox("Email Template", 
                                         ["Standard Report", "Detailed Report", "Summary Report", "Custom Template"])
        
        # Test and send buttons
        st.subheader("📤 Send Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Send Test Email", type="secondary"):
                # Test email functionality
                test_email = st.text_input("Test Email Address", placeholder="Enter email address")
                if test_email:
                    # Simulate sending test email
                    st.success(f"✅ Test email sent to {test_email}")
                    st.info("📧 Test email contains sample weekly report data")
        
        with col2:
            if st.button("📊 Send Weekly Reports Now", type="primary"):
                # Send weekly reports to all recipients
                with st.spinner("Sending weekly reports..."):
                    # Simulate sending reports
                    if send_to_teachers:
                        st.success("✅ Weekly reports sent to 12 teachers")
                    if send_to_parents:
                        st.success("✅ Weekly reports sent to 55 parents")
                    if send_to_students:
                        st.success("✅ Weekly reports sent to 89 students")
                    
                    st.info("📧 All weekly reports have been sent successfully!")
        
        with col3:
            if st.button("📅 Schedule Reports", type="secondary"):
                st.success("✅ Weekly reports scheduled!")
                st.info(f"📅 Reports will be sent every {report_day} at {report_time}")
        
        # Report history
        st.subheader("📋 Report History")
        
        # Sample report history
        report_history = pd.DataFrame({
            'Date': ['2025-09-14', '2025-09-07', '2025-08-31', '2025-08-24'],
            'Recipients': ['Teachers: 12, Parents: 55', 'Teachers: 12, Parents: 55', 'Teachers: 12, Parents: 55', 'Teachers: 12, Parents: 55'],
            'Status': ['✅ Sent', '✅ Sent', '✅ Sent', '⚠️ Failed'],
            'Template': ['Standard Report', 'Standard Report', 'Detailed Report', 'Standard Report']
        })
        
        st.dataframe(report_history, use_container_width=True)
        
        # Email delivery status
        st.subheader("📊 Email Delivery Status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sent", "156", "12")
        with col2:
            st.metric("Delivered", "152", "8")
        with col3:
            st.metric("Failed", "4", "-4")
        with col4:
            st.metric("Delivery Rate", "97.4%", "2.1%")

def show_student_progress_tracker():
    """Student progress tracking interface with task completion and monitoring"""
    st.header("📈 Student Progress Tracker")
    
    # Student selection
    student_name = st.selectbox("Select Student", ["Alex Johnson", "Alice Smith", "Bob Wilson", "Carol Davis"])
    
    # Get or create roadmap for the student
    if 'current_roadmap' not in st.session_state:
        # Create a sample roadmap for demonstration
        from src.ai_roadmap_generator import AIRoadmapGenerator
        from src.data_models import StudentProfile, Subject
        
        # Create sample student
        student = StudentProfile(
            student_id="demo_student",
            name=student_name,
            age=16,
            grade="11th",
            target_scores={
                Subject.MATHEMATICS: 85,
                Subject.PHYSICS: 80,
                Subject.CHEMISTRY: 80,
                Subject.BIOLOGY: 75,
                Subject.ENGLISH: 85
            },
            current_scores={
                Subject.MATHEMATICS: 70,
                Subject.PHYSICS: 65,
                Subject.CHEMISTRY: 68,
                Subject.BIOLOGY: 72,
                Subject.ENGLISH: 75
            },
            learning_style="visual",
            available_hours_per_day=4.0,
            preferred_study_times=["morning", "evening"]
        )
        
        # Generate roadmap
        roadmap_generator = AIRoadmapGenerator()
        roadmap = roadmap_generator.generate_roadmap(student, duration_weeks=12)
        st.session_state['current_roadmap'] = roadmap
        st.session_state['current_student'] = student
    
    roadmap = st.session_state['current_roadmap']
    student = st.session_state['current_student']
    
    # Current week selection
    current_week = st.slider("Current Week", 1, roadmap.duration_weeks, 1)
    
    if current_week <= len(roadmap.weekly_plans):
        current_plan = roadmap.weekly_plans[current_week - 1]
        
        # Progress Overview
        st.subheader(f"📊 Week {current_week} Progress Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_tasks = len(current_plan.tasks)
        completed_tasks = len([t for t in current_plan.tasks if t.status.value == 'completed'])
        pending_tasks = len([t for t in current_plan.tasks if t.status.value == 'pending'])
        overdue_tasks = len([t for t in current_plan.tasks if t.status.value == 'overdue'])
        
        with col1:
            st.metric("Total Tasks", total_tasks)
        with col2:
            st.metric("Completed", completed_tasks, f"+{completed_tasks - pending_tasks}")
        with col3:
            st.metric("Pending", pending_tasks)
        with col4:
            if overdue_tasks > 0:
                st.metric("Overdue", overdue_tasks, delta=None, delta_color="inverse")
            else:
                st.metric("Overdue", overdue_tasks)
        
        # Progress Visualization
        st.subheader("📈 Progress Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Progress Bar
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.progress(completion_rate / 100)
            st.write(f"**Completion Rate: {completion_rate:.1f}%**")
        
        with col2:
            # Pie Chart
            if total_tasks > 0:
                import plotly.express as px
                
                task_data = {
                    'Status': ['Completed', 'Pending', 'Overdue'],
                    'Count': [completed_tasks, pending_tasks, overdue_tasks],
                    'Color': ['#28a745', '#ffc107', '#dc3545']
                }
                
                fig = px.pie(values=task_data['Count'], names=task_data['Status'], 
                           title="Task Status Distribution",
                           color_discrete_sequence=task_data['Color'])
                st.plotly_chart(fig, use_container_width=True)
        
        # Task Management Interface
        st.subheader("✅ Task Management")
        
        # Task completion interface
        for i, task in enumerate(current_plan.tasks):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    # Task details
                    status_color = {
                        'completed': '🟢',
                        'pending': '🟡', 
                        'overdue': '🔴',
                        'in_progress': '🔵'
                    }
                    
                    status_icon = status_color.get(task.status.value, '⚪')
                    st.write(f"{status_icon} **{task.title}**")
                    st.write(f"   Subject: {task.subject.value} | Priority: {task.priority.value.title()}")
                    st.write(f"   Due: {task.due_date.strftime('%Y-%m-%d')}")
                    
                    if task.description:
                        st.write(f"   Description: {task.description}")
                
                with col2:
                    # Status selector
                    new_status = st.selectbox(
                        "Status", 
                        ["pending", "in_progress", "completed", "overdue"],
                        index=["pending", "in_progress", "completed", "overdue"].index(task.status.value),
                        key=f"status_{i}"
                    )
                    
                    if new_status != task.status.value:
                        task.status = type(task.status)(new_status)
                        st.rerun()
                
                with col3:
                    # Time tracking
                    if task.status.value == 'completed':
                        actual_time = st.number_input(
                            "Actual Time (min)", 
                            min_value=1, 
                            value=task.actual_duration or task.estimated_duration,
                            key=f"time_{i}"
                        )
                        task.actual_duration = actual_time
                
                with col4:
                    # Notes
                    notes = st.text_area(
                        "Notes", 
                        value=task.notes or "",
                        height=50,
                        key=f"notes_{i}"
                    )
                    task.notes = notes
                
                st.divider()
        
        # Irregularity Detection
        st.subheader("⚠️ Irregularity Detection")
        
        irregularities = []
        warnings = []
        
        # Check for overdue tasks
        if overdue_tasks > 0:
            irregularities.append(f"🔴 {overdue_tasks} overdue tasks detected")
        
        # Check completion rate
        if completion_rate < 70:
            warnings.append(f"⚠️ Low completion rate: {completion_rate:.1f}% (below 70% threshold)")
        
        # Check for consistency issues
        if pending_tasks >= 3:
            warnings.append(f"⚠️ {pending_tasks} pending tasks - consider reviewing schedule")
        
        # Display irregularities and warnings
        if irregularities:
            for irregularity in irregularities:
                st.error(irregularity)
        
        if warnings:
            for warning in warnings:
                st.warning(warning)
        
        if not irregularities and not warnings:
            st.success("✅ No irregularities detected! Great progress!")
        
        # Weekly Report Generator
        st.subheader("📋 Weekly Report Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Generate Weekly Report", type="primary"):
                # Generate monitoring report
                from src.monitoring_agents import MonitoringSystem
                
                monitoring_system = MonitoringSystem()
                report = monitoring_system.generate_weekly_report(student, roadmap, current_week)
                
                st.session_state['weekly_report'] = report
                st.success("Weekly report generated successfully!")
        
        with col2:
            if 'weekly_report' in st.session_state:
                report = st.session_state['weekly_report']
                
                # Display report summary
                st.write("**Report Summary:**")
                st.write(f"- Tasks Completed: {report.tasks_completed}")
                st.write(f"- Tasks Pending: {report.tasks_pending}")
                st.write(f"- Adherence Rate: {report.adherence_rate:.1%}")
                
                if report.irregularities:
                    st.write("**Irregularities:**")
                    for irregularity in report.irregularities:
                        st.write(f"- {irregularity}")
                
                # Download options
                col_download1, col_download2 = st.columns(2)
                
                with col_download1:
                    # CSV Download
                    import io
                    import csv
                    
                    csv_buffer = io.StringIO()
                    writer = csv.writer(csv_buffer)
                    
                    # Write report data to CSV
                    writer.writerow(['Metric', 'Value'])
                    writer.writerow(['Week', current_week])
                    writer.writerow(['Tasks Completed', report.tasks_completed])
                    writer.writerow(['Tasks Pending', report.tasks_pending])
                    writer.writerow(['Tasks Overdue', report.tasks_overdue])
                    writer.writerow(['Adherence Rate', f"{report.adherence_rate:.1%}"])
                    
                    for i, irregularity in enumerate(report.irregularities):
                        writer.writerow([f'Irregularity {i+1}', irregularity])
                    
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv_data,
                        file_name=f"weekly_report_week_{current_week}.csv",
                        mime="text/csv"
                    )
                
                with col_download2:
                    # PDF Download
                    if st.button("📄 Download PDF"):
                        # Generate PDF report
                        from src.pdf_utils import generate_roadmap_pdf
                        import io
                        
                        pdf_buffer = io.BytesIO()
                        generate_roadmap_pdf(student, roadmap, pdf_buffer)
                        pdf_buffer.seek(0)
                        
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_buffer,
                            file_name=f"weekly_report_week_{current_week}.pdf",
                            mime="application/pdf"
                        )

def show_system_architecture():
    """System architecture diagram showing AI + Agents + HITL interaction"""
    st.header("🏗️ System Architecture")
    
    st.write("**Personalized Roadmap Generation System - Architecture Overview**")
    
    # System overview
    st.subheader("🎯 System Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Core Components:**
        - 🤖 AI Roadmap Generator
        - 👥 Monitoring Agents
        - 🔄 Human-in-the-Loop (HITL)
        - 📊 Progress Tracking
        - 📧 Email Notifications
        - 🔗 LMS Integration
        """)
    
    with col2:
        st.info("""
        **Key Features:**
        - Role-based access control
        - Real-time progress monitoring
        - Automated conflict resolution
        - SMTP email notifications
        - Multi-LMS integration
        - PDF report generation
        """)
    
    # Architecture Diagram
    st.subheader("🏗️ System Architecture Diagram")
    
    # Create a visual representation using Streamlit components
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <h3>System Architecture Flow</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Main system flow
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4 style="text-align: center; color: #1f77b4;">🏗️ System Architecture Flow</h4>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin: 20px 0;">
            <div style="background-color: #ff9999; padding: 15px; border-radius: 8px; text-align: center; margin: 5px; flex: 1; min-width: 150px;">
                <strong>👤 Student</strong><br>
                Inputs: Goals, Preferences<br>
                Outputs: Study Roadmap
            </div>
            <div style="font-size: 24px; margin: 0 10px;">→</div>
            <div style="background-color: #66b3ff; padding: 15px; border-radius: 8px; text-align: center; margin: 5px; flex: 1; min-width: 150px;">
                <strong>🤖 AI Generator</strong><br>
                Analyzes: Performance, Trends<br>
                Creates: Personalized Plan
            </div>
            <div style="font-size: 24px; margin: 0 10px;">→</div>
            <div style="background-color: #99ff99; padding: 15px; border-radius: 8px; text-align: center; margin: 5px; flex: 1; min-width: 150px;">
                <strong>👥 Monitoring Agents</strong><br>
                Tracks: Progress, Irregularities<br>
                Generates: Reports, Alerts
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin: 20px 0;">
            <div style="background-color: #ffcc99; padding: 15px; border-radius: 8px; text-align: center; margin: 5px; flex: 1; min-width: 150px;">
                <strong>👨‍🏫 Teacher</strong><br>
                Reviews: Roadmaps<br>
                Provides: Feedback, Approval
            </div>
            <div style="font-size: 24px; margin: 0 10px;">↕️</div>
            <div style="background-color: #ff99cc; padding: 15px; border-radius: 8px; text-align: center; margin: 5px; flex: 1; min-width: 150px;">
                <strong>👨‍👩‍👧‍👦 Parent</strong><br>
                Monitors: Progress<br>
                Adjusts: Study Hours
            </div>
            <div style="font-size: 24px; margin: 0 10px;">↕️</div>
            <div style="background-color: #cc99ff; padding: 15px; border-radius: 8px; text-align: center; margin: 5px; flex: 1; min-width: 150px;">
                <strong>⚖️ Conflict Resolution</strong><br>
                Detects: Conflicts<br>
                Resolves: Disagreements
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Component Details
    st.subheader("🔧 Component Details")
    
    # AI Roadmap Generator
    with st.expander("🤖 AI Roadmap Generator", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Inputs:**")
            st.write("• Student profile and preferences")
            st.write("• Current academic performance")
            st.write("• Target scores and goals")
            st.write("• Available study time")
            st.write("• Learning style preferences")
            st.write("• Exam trends and patterns")
        
        with col2:
            st.write("**Processing:**")
            st.write("• Machine learning algorithms")
            st.write("• Performance analysis")
            st.write("• Goal optimization")
            st.write("• Time allocation algorithms")
            st.write("• Resource matching")
            st.write("• Progress prediction")
        
        st.write("**Outputs:**")
        st.write("• Personalized weekly study plans")
        st.write("• Subject-specific task breakdowns")
        st.write("• Learning resource recommendations")
        st.write("• Progress milestones and checkpoints")
    
    # Monitoring Agents
    with st.expander("👥 Monitoring Agents"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**📊 Progress Tracking Agent**")
            st.write("• Monitors task completion")
            st.write("• Tracks study adherence")
            st.write("• Calculates performance metrics")
            st.write("• Identifies progress patterns")
        
        with col2:
            st.write("**📈 Performance Analysis Agent**")
            st.write("• Analyzes academic trends")
            st.write("• Predicts performance outcomes")
            st.write("• Identifies improvement areas")
            st.write("• Generates performance insights")
        
        with col3:
            st.write("**📚 Study Habit Agent**")
            st.write("• Monitors study patterns")
            st.write("• Tracks focus quality")
            st.write("• Identifies distractions")
            st.write("• Suggests habit improvements")
    
    # Human-in-the-Loop
    with st.expander("🔄 Human-in-the-Loop (HITL) Framework"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**👨‍🏫 Teacher Involvement:**")
            st.write("• Roadmap review and approval")
            st.write("• Academic feedback provision")
            st.write("• Study plan adjustments")
            st.write("• Performance interventions")
            st.write("• Conflict resolution authority")
        
        with col2:
            st.write("**👨‍👩‍👧‍👦 Parent Involvement:**")
            st.write("• Progress monitoring")
            st.write("• Study hours adjustment")
            st.write("• Feedback and concerns")
            st.write("• Home environment optimization")
            st.write("• Motivation and support")
        
        st.write("**⚖️ Conflict Resolution Process:**")
        st.write("1. **Detection:** System identifies conflicts between teacher and parent feedback")
        st.write("2. **Notification:** All parties are notified of the conflict")
        st.write("3. **Resolution:** Teacher has authority to resolve conflicts")
        st.write("4. **Implementation:** Resolved changes are applied to the roadmap")
        st.write("5. **Communication:** All parties are informed of the resolution")
    
    # Data Flow
    st.subheader("📊 Data Flow Architecture")
    
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4 style="text-align: center; color: #28a745;">📊 Data Flow Diagram</h4>
        <div style="text-align: center; margin: 20px 0;">
            <div style="display: inline-block; background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px;">
                <strong>📥 Data Sources</strong><br>
                Student Profiles<br>
                Performance History<br>
                LMS Data<br>
                Exam Trends
            </div>
            <div style="display: inline-block; font-size: 24px; margin: 0 20px;">→</div>
            <div style="display: inline-block; background-color: #f3e5f5; padding: 15px; border-radius: 8px; margin: 10px;">
                <strong>🔄 Processing Layer</strong><br>
                AI Algorithms<br>
                Monitoring Agents<br>
                HITL Framework<br>
                Conflict Resolution
            </div>
            <div style="display: inline-block; font-size: 24px; margin: 0 20px;">→</div>
            <div style="display: inline-block; background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px;">
                <strong>📤 Outputs</strong><br>
                Study Roadmaps<br>
                Progress Reports<br>
                Email Notifications<br>
                PDF Downloads
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Technology Stack
    st.subheader("💻 Technology Stack")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Frontend:**")
        st.write("• Streamlit (Web Interface)")
        st.write("• Plotly (Data Visualization)")
        st.write("• HTML/CSS (Custom Styling)")
        st.write("• JavaScript (Interactive Elements)")
    
    with col2:
        st.write("**Backend:**")
        st.write("• Python (Core Logic)")
        st.write("• SQLite/PostgreSQL (Database)")
        st.write("• SMTP (Email Service)")
        st.write("• REST APIs (LMS Integration)")
    
    with col3:
        st.write("**AI/ML:**")
        st.write("• Scikit-learn (ML Algorithms)")
        st.write("• NumPy (Numerical Computing)")
        st.write("• Pandas (Data Processing)")
        st.write("• Custom Algorithms (Roadmap Generation)")
    
    # System Metrics
    st.subheader("📈 System Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Users", "156", "12")
    with col2:
        st.metric("Roadmaps Generated", "89", "5")
    with col3:
        st.metric("Monitoring Agents", "3", "0")
    with col4:
        st.metric("System Uptime", "99.8%", "0.1%")
    
    # Integration Points
    st.subheader("🔗 Integration Points")
    
    st.write("**External Systems:**")
    
    integration_data = pd.DataFrame({
        'System': ['Canvas LMS', 'Moodle LMS', 'Blackboard Learn', 'Schoology', 'SMTP Server', 'Database'],
        'Status': ['✅ Connected', '✅ Connected', '⚠️ Pending', '❌ Not Configured', '✅ Active', '✅ Online'],
        'Purpose': ['Grade Sync', 'Course Import', 'Roster Management', 'K-12 Integration', 'Email Notifications', 'Data Storage'],
        'Last Sync': ['2 hours ago', '1 hour ago', 'Never', 'Never', 'Real-time', 'Real-time']
    })
    
    st.dataframe(integration_data, use_container_width=True)
    
    # Security & Privacy
    st.subheader("🔒 Security & Privacy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Security Measures:**")
        st.write("• Role-based access control")
        st.write("• JWT authentication")
        st.write("• Password hashing")
        st.write("• Session management")
        st.write("• API rate limiting")
        st.write("• Data encryption")
    
    with col2:
        st.write("**Privacy Protection:**")
        st.write("• FERPA compliance")
        st.write("• Data anonymization")
        st.write("• Secure data transmission")
        st.write("• Access logging")
        st.write("• Data retention policies")
        st.write("• User consent management")

if __name__ == "__main__":
    main()
