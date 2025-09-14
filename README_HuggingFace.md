# Personalized Roadmap Generation System

A comprehensive AI-driven study roadmap system with Human-in-the-Loop (HITL) architecture for personalized student learning.

## 🚀 Live Demo

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/your-username/personalized-roadmap-system)

## 📋 Features

- **🤖 AI-Driven Roadmap Generation**: Personalized study plans based on student performance data
- **👥 Human-in-the-Loop Integration**: Teacher and parent oversight with feedback mechanisms
- **📊 Agent-Based Monitoring**: Automated progress tracking and irregularity detection
- **📈 Real-time Analytics**: Comprehensive dashboards for all stakeholders
- **🎯 Personalized Learning**: Adaptive content and scheduling based on individual needs

## 🏗️ Architecture

### Core Components
1. **Data Collection & Analysis**: Student performance metrics, SWOT analysis, exam trends
2. **AI Roadmap Generation**: Custom algorithms for personalized study plans
3. **Monitoring Agents**: Progress tracking and anomaly detection
4. **HITL Framework**: Teacher and parent feedback integration
5. **Web Application**: Streamlit-based dashboard and interfaces

### Stakeholders
- **👨‍🎓 Students**: View and interact with personalized roadmaps
- **👨‍🏫 Teachers**: Review and validate AI-generated plans
- **👨‍👩‍👧‍👦 Parents**: Monitor progress and provide environmental feedback

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/your-username/personalized-roadmap-system.git
cd personalized-roadmap-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Access the application**
Open your browser and navigate to `http://localhost:8501`

### HuggingFace Spaces Deployment

1. **Fork this space**
2. **Update the configuration** in `README_HuggingFace.md`
3. **Deploy** - The space will automatically build and deploy

## 📁 Project Structure

```
├── app.py                          # Main Streamlit application
├── src/
│   ├── data_models.py             # Data structures and models
│   ├── ai_roadmap_generator.py    # AI-driven roadmap generation
│   ├── monitoring_agents.py       # Agent-based monitoring system
│   ├── hitl_framework.py          # Human-in-the-loop integration
│   └── utils.py                   # Utility functions
├── data/
│   ├── exam_trends.json          # Exam trend analysis data
│   └── learning_resources.json   # Learning resource database
├── requirements.txt               # Python dependencies
├── Research_Document.md          # Comprehensive research documentation
└── README_HuggingFace.md         # This file
```

## 🎯 Usage

### For Students
1. **Navigate to Student Management** to create your profile
2. **Set your target scores** and learning preferences
3. **Generate your personalized roadmap** using the AI Roadmap Generator
4. **Track your progress** through the monitoring dashboard

### For Teachers
1. **Access the Teacher Interface** to review student roadmaps
2. **Provide feedback** on AI-generated study plans
3. **Monitor student progress** through the analytics dashboard
4. **Collaborate with parents** through the shared feedback system

### For Parents
1. **Use the Parent Interface** to monitor your child's progress
2. **Submit observations** about study habits and home environment
3. **Receive notifications** about important updates and concerns
4. **Participate in feedback sessions** with teachers

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom database path
DATABASE_PATH=data/roadmap_system.db

# Optional: Set logging level
LOG_LEVEL=INFO
```

### Customization
- **Subjects**: Modify `Subject` enum in `data_models.py`
- **Learning Resources**: Update `data/learning_resources.json`
- **Exam Trends**: Modify `data/exam_trends.json`
- **UI Themes**: Customize Streamlit theme in `app.py`

## 📊 Monitoring & Analytics

### System Metrics
- **Active Students**: Number of students using the system
- **Roadmaps Generated**: Total personalized roadmaps created
- **Pending Reviews**: Teacher and parent feedback awaiting review
- **System Health**: Overall system performance and uptime

### Performance Tracking
- **Completion Rates**: Percentage of tasks completed on time
- **Adherence Rates**: How well students follow their roadmaps
- **Performance Trends**: Academic improvement over time
- **Engagement Metrics**: Student interaction and participation levels

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Documentation

- **Research Document**: [Research_Document.md](Research_Document.md) - Comprehensive analysis and methodology
- **API Documentation**: Available in the `/docs` directory
- **User Guides**: Built into the application interface

## 🐛 Troubleshooting

### Common Issues

**Issue**: Module not found errors
**Solution**: Ensure all dependencies are installed and Python path is correct

**Issue**: Database connection errors
**Solution**: Check database file permissions and path configuration

**Issue**: Performance issues with large datasets
**Solution**: Consider implementing data pagination and caching

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Email**: Contact the development team

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit Team** for the excellent web application framework
- **HuggingFace** for providing the deployment platform
- **Educational Research Community** for insights into personalized learning
- **Open Source Contributors** for various libraries and tools used

## 📞 Contact

- **Project Lead**: [Your Name]
- **Email**: your.email@example.com
- **GitHub**: [@your-username](https://github.com/your-username)
- **LinkedIn**: [Your LinkedIn Profile](https://linkedin.com/in/your-profile)

---

**Made with ❤️ for better education**
