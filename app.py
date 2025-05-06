import streamlit as st
from config.logger import logger

upload_page = st.Page(page="pages/upload/upload.py", title="Upload", icon="⬆️")
grouping_page = st.Page(page="pages/grouping/grouping.py", title="Grouping", icon="📦")
report_page = st.Page(page="pages/report/report.py", title="Report", icon="📊")

pg = st.navigation(pages=[upload_page, grouping_page, report_page])

logger.info("Starting application")

pg.run()
