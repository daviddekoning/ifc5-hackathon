import json
import pandas as pd
import io

import streamlit as st


def ifcx_to_df(ifcx_file: io.BytesIO) -> pd.DataFrame:
    """
    Dummy function that converts an IFCX file to a pandas DataFrame.
    In a real implementation, this would parse the IFCX file and extract properties.
    
    Args:
        ifcx_file: A BytesIO object containing the IFCX file contents
        
    Returns:
        DataFrame with columns ['id', 'property', 'value']
    """
    # Dummy data for testing
    
    data = json.load(ifcx_file)

    filtered_data = [
        obj for obj in data 
        if obj.get("def") == "over" and "attributes" in obj
    ]

    ignore_attrs = ['UsdGeom:Mesh', 'xfromOp', 'UsdShade:Material']

    flattened_data = []

    for obj in filtered_data:
        for prop, value in obj.get('attributes', {}).items():
            if prop in ignore_attrs:
                continue
            flattened_data.append({
                'id': obj.get('name'),
                'property': prop,
                'value': json.dumps(value)
            })
    
    return pd.DataFrame(flattened_data)

def df_to_ifcx(df: pd.DataFrame) -> str:
    """
    Dummy function that converts a DataFrame of edits back to IFCX format.
    In a real implementation, this would generate valid IFCX content.
    
    Args:
        df: DataFrame containing the edits with columns ['id', 'property', 'value']
        
    Returns:
        String containing the IFCX file content
    """
    # Dummy IFCX content for testing
    over_template = """{
     "def": "over",
     "name": "{0}",
     "attributes": {
        "{1}": "{2}"
        }
    }"""

    overs = []

    # Check if the DataFrame has the required columns
    required_columns = {'id', 'property', 'value'}
    if not required_columns.issubset(df.columns):
        raise KeyError(f"DataFrame is missing one of the required columns: {required_columns}")

    for index, row in df.iterrows():
        # Ensure each row has the required keys
        try:
            id_value = row['id']
            property_value = row['property']
            value_value = row['value']
        except KeyError as e:
            raise KeyError(f"Missing key in row {index}: {e}")

        st.write(id_value)
        st.write(property_value)
        st.write(value_value)
        overs.append(f"""{{
     "def": "over",
     "name": "{id_value}",
     "attributes": {{
        "{property_value}": {value_value}
     }}
    }}""")

    return "[" + ",".join(overs) + "]" 