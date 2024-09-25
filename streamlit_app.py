import streamlit as st
from datetime import datetime
import pandas as pd
from pbixray.core import PBIXRay
import time
import threading
from pygwalker.api.streamlit import StreamlitRenderer

# ------------------------------
# Streamlit Page Configuration
# ------------------------------
st.set_page_config(
    page_title="Power BI Scanner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Power BI Scanner allows you to upload and analyze your PBIX files efficiently."
    },
)

# ------------------------------
# Custom CSS for Enhanced Styling
# ------------------------------
def local_css():
    st.markdown("""
        <style>
            body {background-color: #F5F5F5;}
            .title {font-size: 48px; font-weight: bold; color: #2E86C1; text-align: center;}
            .subtitle {font-size: 20px; color: #555555; text-align: center; margin-bottom: 30px;}
            .datetime {font-size: 16px; color: #888888; text-align: center; margin-bottom: 20px;}
            .sidebar-header {font-size: 24px; color: #2E86C1; margin-bottom: 10px;}
            .stButton>button {background-color: #2E86C1; color: white; padding: 10px 24px; border-radius: 5px; border: none; cursor: pointer; font-size: 16px;}
            .stButton>button:hover {background-color: #1B4F72;}
            .streamlit-expanderHeader {font-size: 18px; color: #2E86C1;}
            .streamlit-tab {font-size: 16px; font-weight: bold; color: #2E86C1;}
        </style>
    """, unsafe_allow_html=True)

# Apply the custom CSS
local_css()

# ------------------------------
# Utility Functions
# ------------------------------
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"

# Function to display dynamic date and time
def display_datetime(main_placeholder):
    while True:
        now = datetime.now().strftime('%B %d, %Y %H:%M:%S')
        main_placeholder.markdown(
            f"<div class='datetime'>{now}</div>", unsafe_allow_html=True
        )
        time.sleep(1)

# Sidebar
with st.sidebar:
    st.markdown("<div class='sidebar-header'>Web Links</div>", unsafe_allow_html=True)
    st.markdown(
        """
        - [Power BI](https://app.powerbi.com)
        - [Microsoft Fabric Blog](https://blog.fabric.microsoft.com/en-US/blog/)
        - [Google](https://www.google.com)
        """,
        unsafe_allow_html=False
    )
    st.markdown("---")
    st.markdown(
        """
        <div style='font-size:14px; color:#888888;'>
            © 2024 Power BI Scanner. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------------------
# Dynamic Date and Time Display
# ------------------------------
main_time_placeholder = st.empty()

datetime_thread = threading.Thread(
    target=display_datetime, 
    args=(main_time_placeholder,), 
    daemon=True
)
datetime_thread.start()

# ------------------------------
# Caching PBIX Data with @st.cache_resource
# ------------------------------
@st.cache_resource
def load_pbix_data(uploaded_file):
    try:
        model = PBIXRay(uploaded_file)
        return model
    except Exception as e:
        st.error(f"❌ An error occurred while processing the file: {e}")
        return None

# ------------------------------
# Function to Initialize Pygwalker with caching
# ------------------------------
@st.cache_resource
def get_pyg_renderer(df):
    return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")

# ------------------------------
# Function to Run Pygwalker Visualization
# ------------------------------
def pygwalker_visualization(df):
    try:
        pyg_renderer = get_pyg_renderer(df)
        pyg_renderer.explorer()  # Correct method to render the Pygwalker UI
    except Exception as e:
        st.error(f"An error occurred while rendering Pygwalker: {e}")

# ------------------------------
# Main Application Function
# ------------------------------
def app():
    st.markdown("<div class='title'>Power BI Scanner</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'> </div>", unsafe_allow_html=True)
    
    st.subheader('Start Scanning Your PBIX File')
    
    uploaded_file = st.file_uploader("📂 Upload a PBIX file", type="pbix")
    
    if uploaded_file:
        with st.spinner('🔄 Processing your PBIX file...'):
            model = load_pbix_data(uploaded_file)
            if not model:
                return
        
        st.success('✅ File processed successfully!')
        
        with st.expander("📋 Metadata", expanded=False):
            st.json(model.metadata)
        
        met1, met2 = st.columns(2)
        met1.metric(label='📦 Model Size', value=sizeof_fmt(model.size))
        met2.metric(label='📊 Number of Tables', value=model.tables.size)
        
        tabs = st.tabs(["📚 Schema", "📈 Statistics", "🔧 Power Query", "📄 DAX Tables", "📏 DAX Measures"])
        
        for i, tab in enumerate(tabs):
            with tab:
                if i == 0:
                    st.subheader("📚 Schema")
                    st.write(model.schema)
                elif i == 1:
                    st.subheader("📈 Statistics")
                    st.dataframe(model.statistics)
                elif i == 2:
                    if model.power_query.size:
                        st.subheader("🔧 Power Query Code")
                        st.code(model.power_query.to_string(), language='python')
                    else:
                        st.info("ℹ️ No Power Query code found.")
                elif i == 3:
                    if model.tables.size:
                        st.subheader("📄 DAX Tables")
                        st.dataframe(model.dax_tables)
                    else:
                        st.info("ℹ️ No DAX tables found.")
                elif i == 4:
                    if model.dax_measures.size:
                        st.subheader("📏 DAX Measures")
                        st.dataframe(model.dax_measures)
                    else:
                        st.info("ℹ️ No DAX measures found.")

        st.divider()
        
        st.subheader("🔍 Explore Table Details")
        le_name_input = st.selectbox(
            "🗂️ Select a table to peek at its contents:", sorted(model.tables)
        )
        
        if st.button("🔍 View Table Details"):
            try:
                table_details = model.get_table(le_name_input)
                if isinstance(table_details, pd.DataFrame):
                    st.dataframe(table_details, use_container_width=True)
                    st.subheader("📊 Analyze Table Data")
                    pygwalker_visualization(table_details)
                else:
                    st.error("❌ The retrieved table details are not in a valid DataFrame format.")
            except Exception as e:
                st.error(f"❌ Unable to retrieve table details: {e}")

# ------------------------------
# Run the Application
# ------------------------------
if __name__ == '__main__':
    app()

# Add a footer
st.markdown(
    """
    <div style="text-align: center; color: #888888; font-size: 12px; margin-top: 20px;">
        © 2024 Power BI Scanner. All rights reserved.
        Powered by PBIXRay
    </div>
    """,
    unsafe_allow_html=True
)























#--------------- original code -- dont change--------------
# import datetime
# import streamlit as st
# from datetime import datetime
# import pandas as pd
# from pbixray.core import PBIXRay

# from streamlit_observable import observable

# st.set_page_config(
#     page_title="Power BI Scanner",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="auto",
#     menu_items={
        
#     },
#     #toolbarmode = 'Standard'
# )

# st.markdown(
#    f" Date "
#    f"<div style='text-align: left; font-size: 26px;'>{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}</div>", unsafe_allow_html=True)  
# with st.sidebar.expander("WebLinks"):
#     st.markdown(
#         """
#         <style>
#             .blink {
#                 animation: blink 1s infinite;
#             }
#             @keyframes blink {
#                 0% { opacity: 0; }
#                 50% { opacity: 1; }
#                 100% { opacity: 0; }
#             }
#         </style>
#         <ul>
#             <li><a href="https://app.powerbi.com" class="blink">Power BI</a></li>
#             <li><a href="https://blog.fabric.microsoft.com/en-US/blog/" class="blink">Microsoft Fabric Blog</a></li>
#             <li><a href="https://www.google.com" class="blink">Google</a></li>
#         </ul>
#         """,
#         unsafe_allow_html=True
#     )


# def sizeof_fmt(num, suffix="B"):
#     for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
#         if abs(num) < 1024.0:
#             return f"{num:3.1f}{unit}{suffix}"
#         num /= 1024.0
#     return f"{num:.1f}Yi{suffix}"


# def app():
#     st.title('Power BI :blue[Scanner]')
#     st.divider()
#     st.subheader('Start Scanning your PBIX file')
#     #today = datetime.datetime.now()
#     #st.subheader(today)
#     uploaded_file = st.file_uploader("Upload a PBIX file", type="pbix")
#     if uploaded_file:
#         # Unpack the PBIX file to get the schema_df
#         model = PBIXRay(uploaded_file)
#         st.write(model.metadata)
#         met1, met2 = st.columns(2)
#         met1.metric(label='Model size', value=sizeof_fmt(model.size))
#         met2.metric(label='tables', value=model.tables.size)
#         st.divider()
#         st.write("Schema:")
#         st.write(model.schema)
#         st.divider()
#         st.write("Statistics:")
#         st.dataframe(model.statistics)
#         st.divider()
#         if model.power_query.size:
#             st.write("Power Query code:")
#             st.dataframe(model.power_query)
#         st.divider()
#         if model.tables.size:
#             st.write("DAX tables:")
#             st.dataframe(model.dax_tables)
#         st.divider()
#         if model.dax_measures.size:
#             st.write("DAX measures:")
#             st.dataframe(model.dax_measures)
#         st.divider()
#         # Let the user select a le name
#         le_name_input = st.selectbox(
#             "Select a table to peek at its contents:", model.tables )
        
#         if st.button("Un-VertiPaq"):
#             st.dataframe(model.get_le(le_name_input),
#                          use_container_width=True)

# st.divider()

# # observers = observable("City Brush", 
# #     notebook="d/4f9aa5feff9761c9",
# #     targets=["viewof countyCodes"], 
# #     observe=["selectedCounties"]
# # )

# # selectedCounties = observers.get("selectedCounties")

# if __name__ == '__main__':
#     app()




