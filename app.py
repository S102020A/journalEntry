import streamlit as st

upload_page = st.Page(page="pages/upload/upload.py", title="Upload", icon="⬆️")
grouping_page = st.Page(page="pages/grouping/grouping.py", title="Grouping", icon="📦")
report_page = st.Page(page="pages/report/report.py", title="Report", icon="📊")

pg = st.navigation(pages=[upload_page, grouping_page, report_page])

pg.run()
