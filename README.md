# Personalized Roadmap Generation System

A comprehensive AI-driven study roadmap system with Human-in-the-Loop (HITL) architecture for personalized student learning.

## Features

- **AI-Driven Roadmap Generation**: Personalized study plans based on student performance data
- **Agent-Based Monitoring**: Automated progress tracking and irregularity detection
- **Human-in-the-Loop Integration**: Teacher and parent oversight with feedback mechanisms
- **Real-time Dashboard**: Web-based interface for all stakeholders
- **Performance Analytics**: Comprehensive tracking and reporting

## Architecture

### Core Components
1. **Data Collection & Analysis**: Student performance metrics, SWOT analysis, exam trends
2. **AI Roadmap Generation**: Custom algorithms for personalized study plans
3. **Monitoring Agents**: Progress tracking and anomaly detection
4. **HITL Framework**: Teacher and parent feedback integration
5. **Web Application**: Streamlit-based dashboard and interfaces

### Stakeholders
- **Students**: View and interact with personalized roadmaps
- **Teachers**: Review and validate AI-generated plans
- **Parents**: Monitor progress and provide environmental feedback

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## Project Structure

```
├── app.py                          # Main Streamlit application
├── src/
│   ├── data_models.py             # Data structures and models
│   ├── ai_roadmap_generator.py    # AI-driven roadmap generation
│   ├── monitoring_agents.py       # Agent-based monitoring system
│   ├── hitl_framework.py          # Human-in-the-loop integration
│   └── utils.py                   # Utility functions
├── data/
│   ├── student_profiles.json      # Sample student data
│   └── exam_trends.json          # Exam trend analysis data
├── requirements.txt               # Python dependencies
└── README.md                     # Project documentation
```

## Deployment

The application is designed to be deployed on HuggingFace Spaces with integrated monitoring tools.
