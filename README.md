<div align="center">

<video width="720" height="405" controls>
  <source src="./.github/assets/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

<h1>Personalized Roadmap Generation System</h1>

</div>

---

## Overview

This repository contains a full-stack, production-ready system for generating personalized study roadmaps for students. It integrates AI-driven roadmap generation, agent-based monitoring, and a Human-in-the-Loop (HITL) framework, all accessible via a web application deployed using Streamlit.

The system enables students, teachers, and parents to interact dynamically with study plans, track performance, and collaboratively refine learning strategies.

---

## Features

### AI Roadmap Generator

* Generates **12-week personalized study roadmaps** based on student performance data.
* Maps **learning resources** (PDFs, videos, question banks) to each task.
* Performs **dynamic updates** weekly based on agent feedback.
* Supports **goal optimization** and **time allocation per subject**.

### Monitoring Agents

* **Progress Tracking Agent**: Tracks task completion and study adherence.
* **Performance Analysis Agent**: Predicts performance trends and highlights areas for improvement.
* **Study Habit Agent**: Monitors focus, distractions, and consistency.
* Generates **weekly reports** for students, teachers, and parents.

### Human-in-the-Loop (HITL) Framework

* Teachers review and validate AI-generated roadmaps.
* Parents provide feasibility feedback and monitor at-home progress.
* **Conflict resolution** mechanisms harmonize inputs between teachers and parents.
* Feedback loops improve future AI outputs.

### Web Application

* Built with **Streamlit**, compatible with HuggingFace Spaces.
* **Role-based dashboards** for Students, Teachers, Parents, and Admins.
* Secure **JWT-based authentication**.
* Integrates with LMS platforms such as Canvas and Moodle.
* **SMTP email notifications** for updates and reports.

### Deployment & Analytics

* Cloud-ready deployment using Streamlit/HuggingFace Spaces.
* Clickstream integration for user interaction analytics.
* Hacking Spaces integration for performance monitoring.

---

## Technical Stack

* **Frontend:** Streamlit (Python)
* **Backend:** Python with modular architecture (AI, Agents, HITL, Auth, Email)
* **Database:** SQLite (dev) / PostgreSQL or MySQL (prod)
* **Authentication:** JWT, Password Hashing (bcrypt)
* **Email:** SMTP integration
* **Deployment:** HuggingFace Spaces or cloud VM

---

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/sukanyaghosh74/sstudize_task.git
cd sstudize_task
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file with:

```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=youremail@gmail.com
SMTP_PASSWORD=yourpassword
```

### Run Locally

```bash
streamlit run app.py
```

Access the application at `http://localhost:8501`

---

## Code Snippets

### AI Roadmap Generation

```python
from roadmap_generator import RoadmapGenerator

student_data = load_student_data('data/student123.json')
generator = RoadmapGenerator()
roadmap = generator.generate(student_data)
roadmap.save('outputs/student123_roadmap.pdf')
```

### Monitoring Agent Example

```python
from agents.progress_agent import ProgressTrackingAgent

agent = ProgressTrackingAgent(student_id='123')
weekly_report = agent.generate_report()
print(weekly_report)
```

### HITL Feedback Integration

```python
from hitl import HITLSystem

hitl = HITLSystem()
hitl.submit_teacher_feedback(student_id='123', feedback='Increase math practice')
hitl.submit_parent_feedback(student_id='123', feedback='Reduce study load on weekends')
hitl.resolve_conflicts(student_id='123')
```

### Email Notification

```python
from notifications.email_service import EmailService

email_service = EmailService()
email_service.send_weekly_report(student_id='123')
```

---

## Demo Video

The demo video at the top showcases the system features including:

* Student roadmap creation
* Progress tracking
* Teacher and parent HITL feedback
* Dashboard navigation and analytics

---

## Contributing

Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Commit changes with clear messages
4. Open a pull request

---

## License

MIT License

---

## Contact

For queries, reach out to Sukanya Ghosh at [sukanya.ghosh2024@vitstudent.ac.in](mailto:sukanya.ghosh2024@vitstudent.ac.in)
