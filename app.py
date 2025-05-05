import streamlit as st
from config.config import get_logger

logger = get_logger()

upload_page = st.Page(page="pages/upload/upload.py", title="Upload", icon="⬆️")
validation_page = st.Page(
    page="pages/validation/validation.py", title="Validation", icon="🔒"
)
grouping_page = st.Page(page="pages/grouping/grouping.py", title="Grouping", icon="📦")
report_page = st.Page(page="pages/report/report.py", title="Report", icon="📊")

pg = st.navigation(pages=[upload_page, validation_page, grouping_page, report_page])

logger.info("Starting application")

pg.run()
