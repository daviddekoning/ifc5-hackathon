import streamlit as st
from ..db import get_db_connection
import pandas as pd
from ..pages.auth import require_auth

require_auth(lambda : st.markdown("## Please return to the main page to login."))

st.title("Query Database")

# Query input
query = st.text_area("Enter your SQL query:", height=150)

# Execute button
if st.button("Execute Query"):
    if not query:
        st.warning("Please enter a query")
        st.stop()
        
    try:
        # Execute query
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) == 0:
            st.info("Query returned no results")
        else:
            # Display results
            st.write("Query Results:")
            st.dataframe(df)
            
            # Add download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
