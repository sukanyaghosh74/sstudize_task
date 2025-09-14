"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all required imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import streamlit as st
        print("✓ streamlit imported")
        
        import pandas as pd
        print("✓ pandas imported")
        
        import numpy as np
        print("✓ numpy imported")
        
        import plotly.express as px
        print("✓ plotly imported")
        
        # Test our custom modules
        from data_models import StudentProfile, Subject
        print("✓ data_models imported")
        
        from ai_roadmap_generator import AIRoadmapGenerator
        print("✓ ai_roadmap_generator imported")
        
        from monitoring_agents import MonitoringSystem
        print("✓ monitoring_agents imported")
        
        from hitl_framework import HITLFramework, Teacher, Parent
        print("✓ hitl_framework imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ System ready for deployment!")
    else:
        print("\n❌ Please fix import issues before deployment")
