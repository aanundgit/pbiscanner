import datetime
import streamlit as st
from datetime import datetime
import pandas as pd
from pbixray.core import PBIXRay

from streamlit_observable import observable

st.set_page_config(
    page_title="Power BI Scanner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        
    },
    #toolbarmode = 'Standard'
)

st.markdown(
   f" Date "
   f"<div style='text-align: left; font-size: 26px;'>{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}</div>", unsafe_allow_html=True)  
with st.sidebar.expander("WebLinks"):
    st.markdown(
        """
        <style>
            .blink {
                animation: blink 1s infinite;
            }
            @keyframes blink {
                0% { opacity: 0; }
                50% { opacity: 1; }
                100% { opacity: 0; }
            }
        </style>
        <ul>
            <li><a href="https://app.powerbi.com" class="blink">Power BI</a></li>
            <li><a href="https://blog.fabric.microsoft.com/en-US/blog/" class="blink">Microsoft Fabric Blog</a></li>
            <li><a href="https://www.google.com" class="blink">Google</a></li>
        </ul>
        """,
        unsafe_allow_html=True
    )


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def app():
    st.title('Power BI :blue[Scanner]')
    st.divider()
    st.subheader('Start Scanning your PBIX file')
    #today = datetime.datetime.now()
    #st.subheader(today)
    uploaded_file = st.file_uploader("Upload a PBIX file", type="pbix")
    if uploaded_file:
        # Unpack the PBIX file to get the schema_df
        model = PBIXRay(uploaded_file)
        st.write(model.metadata)
        met1, met2 = st.columns(2)
        met1.metric(label='Model size', value=sizeof_fmt(model.size))
        met2.metric(label='tables', value=model.tables.size)
        st.divider()
        st.write("Schema:")
        st.write(model.schema)
        st.divider()
        st.write("Statistics:")
        st.dataframe(model.statistics)
        st.divider()
        if model.power_query.size:
            st.write("Power Query code:")
            st.dataframe(model.power_query)
        st.divider()
        if model.tables.size:
            st.write("DAX tables:")
            st.dataframe(model.dax_tables)
        st.divider()
        if model.dax_measures.size:
            st.write("DAX measures:")
            st.dataframe(model.dax_measures)
        st.divider()
        # Let the user select a le name
        le_name_input = st.selectbox(
            "Select a table to peek at its contents:", model.tables )
        
        if st.button("Un-VertiPaq"):
            st.dataframe(model.get_le(le_name_input),
                         use_container_width=True)

st.divider()

# observers = observable("City Brush", 
#     notebook="d/4f9aa5feff9761c9",
#     targets=["viewof countyCodes"], 
#     observe=["selectedCounties"]
# )

# selectedCounties = observers.get("selectedCounties")

if __name__ == '__main__':
    app()




