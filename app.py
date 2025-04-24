import streamlit as st

upload_page = st.Page(page="pages/upload.py", title="Upload", icon="⬆️")
grouping_page = st.Page(page="pages/grouping.py", title="Grouping", icon="📦")
report_page = st.Page(page="pages/report.py", title="Report", icon="📊")

pg = st.navigation(pages=[upload_page, grouping_page, report_page])

pg.run()
