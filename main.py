import streamlit as st
import pandas as pd 
import io
from database import get_file_in_folder, list_files_in_folder, upload_audio_file, upload_csv_file, get_last_string
# st.sidebar.write(':rainbow[selected_csv]')



# file_path = st.sidebar.file_uploader("Select CSV file to upload", type=["csv"])
# st.sidebar.write(file_path)
# if file_path:
#     edit_btn = st.sidebar.button("save")
#     if edit_btn:
#         upload_csv_file(file_path.name)



audio_list = list_files_in_folder("audio_files")


csv_list = list_files_in_folder("csv_files")
selected_csv = st.sidebar.selectbox(
    ":rainbow[Select a CSV ...]", 
    csv_list, 
    index=None,
    placeholder="please select ...")



csv, message, csv_path = get_file_in_folder(selected_csv)



if csv:
    data = pd.read_csv(io.BytesIO(csv))
    
    df = pd.DataFrame(data)
    
    # selected_csv = []
    
    # for col in df.columns:
    #     if st.sidebar.selectbox(col):
    #         selected_csv.append(col)
    selected_csv = st.sidebar.selectbox(
                        ':rainbow[Select a Column ( Text )]', 
                        df.columns, 
                        index=None,
                        placeholder="please select ...")
    
    if selected_csv:
        selected_audio = st.sidebar.selectbox(
            ":rainbow[Select a Column (Audio path)]", 
            df.columns, 
            index=None,
            placeholder="please select ...")
        
        
    if selected_csv and selected_audio:
        # Filter DataFrame based on selected columns
        selected_csv_data = df[[selected_csv]]
        selected_audio_data = df[[selected_audio]]
        # Display filtered DataFrame
        # Iterate through rows
        # if filtered_df is not None and not filtered_df.empty:

        if selected_csv_data is not None and not selected_csv_data.empty:
            # Iterate over each row of the DataFrame
            for index, row in selected_csv_data.iterrows():
                with st.container(border=True):
                    st.write(f"Row {index + 1}:")
                    # Display the original value of the cell
                    st.write(f"{selected_csv}: {row[selected_csv]}")
                    audio_path = get_last_string(df[selected_audio][index])
                    audio, message, audio_path = get_file_in_folder(f"audio_files/{audio_path}")
                    if audio:
                        st.audio(audio, format="audio/wav")
                    text_input_key = f"text-{index}-{selected_csv}"
                    # Get the edited value from the user
                    edited_value = st.text_input(f"Edit {selected_csv}", value=row[selected_csv], key=text_input_key)
                    if edited_value != row[selected_csv]:
                        selected_csv_data.at[index, selected_csv] = edited_value
                        
                    # Store the edited value in the dictionary
                    # edited_row[column] = edited_value
                        
                # Append the edited row to the edited DataFrame
                # edited_df.loc[len(edited_df)] = edited_row
                
            # Display a button to save the edited CSV file
        if st.button("Save edited CSV") :
            # Convert the edited DataFrame to CSV format
            df[selected_csv] = selected_csv_data
            edited_csv = df.to_csv(index=False)
            # Upload the edited CSV file to Firebase Storage
            upload_csv_file(edited_csv, csv_path[1])
            st.write("Edited CSV file saved successfully.")




