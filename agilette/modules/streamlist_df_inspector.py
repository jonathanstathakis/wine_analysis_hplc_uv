"""
Simple DF inspector built in streamlit
"""
import streamlit as st

def st_df_info(df : pd.DataFrame) -> pd.DataFrame:
    
    info_df = pd.DataFrame()
    info_df['types'] = df.dtypes
    info_df['NA'] = df.isnull().sum()

    st.title(df.attrs['name'])
    st.header('df shape and size')
    st.write(f"shape: {df.shape} | size: {df.size}")

    with st.container():
        st.header('df columns')
        st.table(info_df.astype(str))
            
    with st.container():
        st.header(f"{df.attrs['name']} head")
        st.write(df.head().astype(str))