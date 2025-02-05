import streamlit as st
import pandas as pd
from ifc_query.util.ifc import ifcx_to_df, df_to_ifcx
import io

def handle_data_editor_change():
    """Handle changes in the data editor"""
    if 'data_editor' in st.session_state:
        edited_rows = st.session_state.data_editor['edited_rows']
        current_df = st.session_state.current_df
        
        for idx, changes in edited_rows.items():
            if 'value' in changes:  # Only if value was changed
                current_id = current_df.iloc[idx]['id']
                current_property = current_df.iloc[idx]['property']
                
                # Check if we already have an edit for this id and property
                mask = (st.session_state.edits['id'] == current_id) & \
                       (st.session_state.edits['property'] == current_property)
                
                if mask.any():
                    # Update existing edit
                    st.session_state.edits.loc[mask, 'value'] = changes['value']
                else:
                    # Add new edit
                    new_edit = pd.DataFrame({
                        'id': [current_id],
                        'property': [current_property],
                        'value': [changes['value']]
                    })
                    st.session_state.edits = pd.concat([st.session_state.edits, new_edit], ignore_index=True)

def edit_page():
    st.title("Edit IFC Properties")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload IFCX file", type=['ifcx'])
    
    if uploaded_file is not None:
        # Initialize session state for edits if not exists
        if 'edits' not in st.session_state:
            st.session_state.edits = pd.DataFrame(columns=['id', 'property', 'value'])
            
        # Convert IFCX to dataframe
        df = ifcx_to_df(uploaded_file)
        
        # Store current df in session state for access in callback
        st.session_state.current_df = df
        
        # Create data editor with only value column editable
        edited_df = st.data_editor(
            df,
            disabled=['id', 'property'],
            hide_index=True,
            key='data_editor',
            on_change=handle_data_editor_change
        )
        
        # Show current edits
        if not st.session_state.edits.empty:
            st.subheader("Current Edits")
            st.dataframe(st.session_state.edits)
            
            # Download button for edits
            if st.button("Download Edits"):
                # Convert edits to IFCX
                ifcx_content = df_to_ifcx(st.session_state.edits)
                
                # Create download button
                st.download_button(
                    label="Download IFCX file",
                    data=ifcx_content,
                    file_name="edited.ifcx",
                    mime="text/plain"
                )

if __name__ == "__main__":
    edit_page()
