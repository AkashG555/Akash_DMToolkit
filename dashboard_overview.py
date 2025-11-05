import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from typing import Dict
from .utils import get_recent_logs, format_file_size

def show_dashboard(credentials: Dict):
    """Display the main dashboard overview"""
    
    # Welcome section
    st.markdown("## 🏠 Welcome to DM Toolkit")
    st.markdown("Your comprehensive data migration and validation platform")
    
    # Current status
    if st.session_state.current_org:
        st.success(f"🏢 Currently working with: **{st.session_state.current_org}**")
        if st.session_state.current_object:
            st.info(f"📋 Active object: **{st.session_state.current_object}**")
    else:
        st.warning("⚠️ Please select an organization from the sidebar to get started")
    
    st.divider()
    
    # Quick metrics in a cleaner layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🏢 Organizations</h4>
            <h2>{}</h2>
            <small>Available Salesforce orgs</small>
        </div>
        """.format(len(credentials)), unsafe_allow_html=True)
    
    with col2:
        recent_logs = get_recent_logs(limit=20)
        st.markdown("""
        <div class="metric-card">
            <h4>📋 Recent Activities</h4>
            <h2>{}</h2>
            <small>Log entries today</small>
        </div>
        """.format(len(recent_logs)), unsafe_allow_html=True)
    
    with col3:
        processed_files = count_processed_files()
        st.markdown("""
        <div class="metric-card">
            <h4>📁 Processed Files</h4>
            <h2>{}</h2>
            <small>Total data files</small>
        </div>
        """.format(processed_files), unsafe_allow_html=True)
    
    st.divider()
    
    # Current session status
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🎯 Current Session Status")
        
        if st.session_state.current_org:
            st.success(f"**Connected Organization:** {st.session_state.current_org}")
            
            if st.session_state.current_object:
                st.info(f"**Selected Object:** {st.session_state.current_object}")
            else:
                st.warning("No Salesforce object selected")
        else:
            st.warning("**No organization connected.** Please select an organization from the sidebar.")
        
        # Recent processing status
        if st.session_state.processing_status:
            st.markdown("#### 📊 Recent Processing")
            for key, status in list(st.session_state.processing_status.items())[-3:]:
                try:
                    timestamp = status.get('timestamp', datetime.now()).strftime("%H:%M")
                    message = status.get('message', 'No message')
                    log_type = status.get('type', 'info')
                    
                    if log_type == 'error':
                        st.error(f"🕒 {timestamp} - {message}")
                    elif log_type == 'warning':
                        st.warning(f"🕒 {timestamp} - {message}")
                    else:
                        st.success(f"🕒 {timestamp} - {message}")
                except Exception:
                    continue
    
    st.divider()
    
    # Quick actions section
    st.markdown("### 🚀 Quick Actions")
    
    # Only show actions if org is selected
    # Note: Page names must match exactly with navigation menu in streamlit_app.py
    if st.session_state.current_org:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("1️⃣ Validation", use_container_width=True, key="dash_validation"):
                st.session_state.active_page = "1️⃣ Validation"
                st.rerun()
        
        with col2:
            if st.button("2️⃣ Data Operations", use_container_width=True, key="dash_data_ops"):
                st.session_state.active_page = "2️⃣ Data Operations"
                st.rerun()
        
        with col3:
            if st.button("3️⃣ Unit Testing", use_container_width=True, key="dash_testing"):
                st.session_state.active_page = "3️⃣ Unit Testing"
                st.rerun()
        
        with col4:
            if st.button("🗺️ Mapping", use_container_width=True, key="dash_mapping"):
                st.session_state.active_page = "🗺️ Mapping"
                st.rerun()
    else:
        st.info("👈 Select an organization from the sidebar to enable quick actions")
    
    st.divider()
    
    # Recent activity in a simplified view
    st.markdown("### 📋 Recent Activity")
    recent_logs = get_recent_logs(limit=5)
    if recent_logs:
        for log in recent_logs[:3]:  # Show only last 3
            try:
                if isinstance(log, dict):
                    timestamp = log.get('timestamp', datetime.now()).strftime("%H:%M")
                    message = log.get('message', 'No message')
                    log_type = log.get('type', 'info')
                    
                    if log_type == 'error':
                        st.error(f"🕒 {timestamp} - {message}")
                    elif log_type == 'warning':
                        st.warning(f"🕒 {timestamp} - {message}")
                    else:
                        st.info(f"🕒 {timestamp} - {message}")
                else:
                    st.info(f"📝 {str(log)[:100]}...")
            except Exception:
                continue
    else:
        st.info("No recent activity found")
    
    # Simple workflow guide
    with st.expander("📖 Getting Started Guide"):
        st.markdown("""
        **Quick Start:**
        1. 🏢 Select an organization from the sidebar
        2. 📥 Use **Data Operations** to extract or load data
        3. 🗺️ Generate **Mapping** for field transformations  
        4. ✅ Run **Validation** to check data quality
        5. 🧪 Create **Unit Tests** for validation
        6. 📋 Review **Logs & Reports** for results
        """)
        
        if not st.session_state.current_org:
            st.info("👈 Start by selecting an organization!")
        else:
            st.success(f"✅ Ready to work with {st.session_state.current_org}")

def count_processed_files() -> int:
    """Count total processed files across all operations"""
    count = 0
    try:
        # Count files in DataFiles folder
        datafiles_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'DataFiles')
        if os.path.exists(datafiles_path):
            for root, dirs, files in os.walk(datafiles_path):
                count += len([f for f in files if f.endswith(('.csv', '.xlsx', '.xls'))])
        
        # Count files in DataLoader_Logs
        logs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'DataLoader_Logs')
        if os.path.exists(logs_path):
            for root, dirs, files in os.walk(logs_path):
                count += len([f for f in files if f.endswith(('.csv', '.xlsx', '.xls'))])
    except:
        pass
    
    return count