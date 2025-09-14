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

def main():
    """Main application function"""
    st.title("📚 Personalized Roadmap Generation System")
    st.markdown("AI-driven study roadmap system with Human-in-the-Loop oversight")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Dashboard", "👨‍🎓 Student Management", "🤖 AI Roadmap Generator", 
         "👨‍🏫 Teacher Interface", "👨‍👩‍👧‍👦 Parent Interface", "📊 Monitoring & Analytics"]
    )
    
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
        
        # Student selection
        student_id = st.selectbox("Select Student", ["student_1", "student_2", "student_3"])
        
        # Roadmap parameters
        duration_weeks = st.slider("Roadmap Duration (weeks)", 4, 16, 12)
        
        # Advanced options
        with st.expander("Advanced Options"):
            focus_subjects = st.multiselect("Focus Subjects", 
                                          ["Mathematics", "Physics", "Chemistry", "Biology", "English"])
            difficulty_level = st.select_slider("Difficulty Level", 
                                              options=["Beginner", "Intermediate", "Advanced"], 
                                              value="Intermediate")
            study_intensity = st.select_slider("Study Intensity", 
                                            options=["Light", "Moderate", "Intensive"], 
                                            value="Moderate")
        
        if st.button("Generate Roadmap", type="primary"):
            with st.spinner("Generating personalized roadmap..."):
                # Simulate roadmap generation
                import time
                time.sleep(2)
                st.success("Roadmap generated successfully!")
    
    with col2:
        st.subheader("Generated Roadmap Preview")
        
        # Sample roadmap data
        roadmap_data = pd.DataFrame({
            'Week': [f"Week {i}" for i in range(1, 13)],
            'Mathematics': [4, 4, 3, 4, 3, 4, 4, 3, 4, 3, 4, 4],
            'Physics': [3, 3, 4, 3, 4, 3, 3, 4, 3, 4, 3, 3],
            'Chemistry': [2, 2, 2, 3, 2, 2, 3, 2, 2, 3, 2, 2],
            'Biology': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            'English': [2, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2]
        })
        
        # Create heatmap
        fig = px.imshow(roadmap_data.set_index('Week').T, 
                       aspect="auto", 
                       title="Weekly Study Hours Distribution",
                       color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)
        
        # Weekly breakdown
        st.subheader("Week 1 Detailed Plan")
        week1_tasks = pd.DataFrame({
            'Task': [
                'Calculus Fundamentals - Video Study',
                'Mechanics Problems - Practice',
                'Organic Chemistry - Reading',
                'Essay Writing - Practice',
                'Biology Review - Notes'
            ],
            'Subject': ['Mathematics', 'Physics', 'Chemistry', 'English', 'Biology'],
            'Duration (hrs)': [2, 1.5, 1, 1, 0.5],
            'Priority': ['High', 'High', 'Medium', 'Medium', 'Low'],
            'Due Date': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        })
        
        st.dataframe(week1_tasks, use_container_width=True)

def show_teacher_interface():
    """Teacher interface for feedback and oversight"""
    st.header("👨‍🏫 Teacher Interface")
    
    # Teacher login simulation
    teacher_id = st.selectbox("Select Teacher", ["teacher_1", "teacher_2", "teacher_3"])
    
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Roadmap Reviews", "Student Progress"])
    
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
            "New roadmap requires review - Alice Johnson",
            "Student performance alert - Bob Smith",
            "Parent feedback received - Carol Davis",
            "Weekly report available - David Wilson"
        ]
        
        for notification in notifications:
            st.info(notification)
    
    with tab2:
        st.subheader("Roadmap Reviews")
        
        # Pending reviews
        st.write("**Pending Reviews:**")
        pending_reviews = pd.DataFrame({
            'Student': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
            'Subject': ['Mathematics', 'Physics', 'Chemistry'],
            'Submitted': ['2 hours ago', '1 day ago', '3 hours ago'],
            'Priority': ['High', 'Medium', 'High']
        })
        
        for _, review in pending_reviews.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{review['Student']}** - {review['Subject']}")
                with col2:
                    st.write(review['Submitted'])
                with col3:
                    if review['Priority'] == 'High':
                        st.error(review['Priority'])
                    else:
                        st.warning(review['Priority'])
                with col4:
                    if st.button(f"Review", key=f"review_{review['Student']}"):
                        st.success("Review opened!")
        
        # Feedback form
        st.subheader("Submit Feedback")
        with st.form("teacher_feedback"):
            student = st.selectbox("Student", ["Alice Johnson", "Bob Smith", "Carol Davis"])
            feedback_type = st.selectbox("Feedback Type", 
                                       ["Roadmap Review", "Progress Assessment", "Recommendation"])
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            content = st.text_area("Feedback Content", height=100)
            
            if st.form_submit_button("Submit Feedback"):
                st.success("Feedback submitted successfully!")

def show_parent_interface():
    """Parent interface for monitoring and feedback"""
    st.header("👨‍👩‍👧‍👦 Parent Interface")
    
    # Parent login simulation
    parent_id = st.selectbox("Select Parent", ["parent_1", "parent_2", "parent_3"])
    
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Child Progress", "Feedback & Concerns"])
    
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
            "Child completed Mathematics practice test - 85%",
            "Teacher provided feedback on study schedule",
            "Weekly progress report available",
            "Upcoming exam reminder - Physics"
        ]
        
        for update in updates:
            st.info(update)
    
    with tab2:
        st.subheader("Child Progress Tracking")
        
        # Progress chart
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
        st.subheader("Study Habits")
        habits_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Study Hours': [4, 3.5, 5, 4.5, 3, 2, 1],
            'Focus Quality': [8, 7, 9, 8, 6, 7, 5]
        })
        
        fig2 = px.bar(habits_data, x='Day', y='Study Hours', 
                     title="Daily Study Hours")
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.subheader("Submit Feedback or Concerns")
        
        with st.form("parent_feedback"):
            concern_type = st.selectbox("Type", 
                                      ["Observation", "Concern", "Suggestion", "Question"])
            subject = st.selectbox("Subject", 
                                 ["Mathematics", "Physics", "Chemistry", "Biology", "English", "General"])
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
            content = st.text_area("Your feedback or concern", height=100)
            
            if st.form_submit_button("Submit"):
                st.success("Your feedback has been submitted to the teacher!")

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

if __name__ == "__main__":
    main()
