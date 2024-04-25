import streamlit as st
import pandas as pd 
import io
import time
from database import get_file_in_folder, list_files_in_folder, upload_audio_file, upload_csv_file, get_last_string

st.set_page_config(
    page_title="Editing CSV",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="expanded",
)

def load_data_for_page(data_frame, page_number, rows_per_page):
    start_index = page_number * rows_per_page
    end_index = (page_number + 1) * rows_per_page
    return data_frame.iloc[start_index:end_index]

# Function to save edited CSV data
def save_edited_csv(data_frame, csv_path):
    edited_csv = data_frame.to_csv(index=False)
    upload_csv_file(edited_csv, csv_path)
    st.toast(":green[Edited CSV file saved successfully.]", icon="🎉")

def main():
    csv_list = list_files_in_folder("csv_files")

    st.sidebar.title(":blue[EDITING CSV] 🧊")

    selected_csv_file = st.sidebar.selectbox(
        ":blue[Select a CSV ...]", 
        csv_list, 
        index=None,
        placeholder="please select ...")

    if selected_csv_file:
        st.session_state.selected_csv_file = selected_csv_file
        
        csv, _, csv_path = get_file_in_folder(st.session_state.selected_csv_file)
        
        if csv:
            data = pd.read_csv(io.BytesIO(csv))
            df = pd.DataFrame(data)
            
            selected_csv = st.sidebar.selectbox(
                                ':blue[Select a Column ( Text )]', 
                                data.columns, 
                                index=None,
                                placeholder="please select ...")
            
            if selected_csv:
                if 'dataframe' not in st.session_state:
                    st.session_state.dataframe = df
                
                if 'edited_row' not in st.session_state:
                    st.session_state.edited_row = []
        
                selected_audio = st.sidebar.selectbox(
                    ":blue[Select a Column (Audio path)]", 
                    data.columns, 
                    index=None,
                    placeholder="please select ...")
                
                if selected_audio:
                    
                    rows_per_page = 5
                    total_rows = len(df)
                    total_pages = total_rows // rows_per_page + 1 if total_rows % rows_per_page != 0 else total_rows // rows_per_page
                    tabs = st.radio(":blue[Pages]", ("ALL DATA", "Edited DATA (unsaved)"), horizontal=True)
                    st.divider()
                    if tabs == "ALL DATA":
                        page_number = st.sidebar.number_input(":blue[Page Number]", min_value=1, max_value=total_pages, value=1)
                        selected_csv_data = load_data_for_page(st.session_state.dataframe, page_number - 1, rows_per_page)
                        for index, row in selected_csv_data[[selected_csv]].iterrows():
                            st.write(f":blue[Index : {index}]")
                            with st.container(border=True):
                        
                                audio_path = get_last_string(df[selected_audio][index])
                                audio, _, _ = get_file_in_folder(f"audio_files/{audio_path}")
                                if audio:
                                    st.audio(audio, format="audio/wav")
                                
                                st.text_input(f"Default {selected_csv}", value=df[selected_csv][index], disabled=True, autocomplete="off")
                                
                                text_input_key = f"text-{index}-{selected_csv}"
                                # Get the edited value from the user
                                edited_value = st.text_input(f"Edit {selected_csv}", value=row[selected_csv], key=text_input_key, autocomplete="off")
                                
                                if edited_value != row[selected_csv]:
                                    with st.spinner('Updating...'):
                                        time.sleep(2)
                                        st.session_state.dataframe[selected_csv][index] = edited_value
                                        if index not in st.session_state.edited_row:
                                            st.session_state.edited_row.append(index)
                                        st.success(' Edited Successfully!')
                            st.divider()
                            
                    if tabs == "Edited DATA (unsaved)":
                        st.write(f":blue[Edited Index : {' , '.join(map(str, st.session_state.edited_row))}]")
                        st.divider()

                        selected_rows = st.session_state.dataframe.loc[st.session_state.edited_row, [selected_csv]]
                        for index, row in selected_rows.iterrows():
                            st.write(f":blue[Index : {index}]")
                            with st.container(border=True):
                                                
                                audio_path = get_last_string(df[selected_audio][index])
                                audio, _, _ = get_file_in_folder(f"audio_files/{audio_path}")
                                if audio:
                                    st.audio(audio, format="audio/wav")
                                    
                                st.text_input(f"Default {selected_csv}", value=df[selected_csv][index], disabled=True, autocomplete="off")
                                
                                text_input_key = f"edited-text-{index}-{selected_csv}"
                                # Get the edited value from the user
                                edited_value = st.text_input(f"Edit {selected_csv}", value=row[selected_csv], key=text_input_key, autocomplete="off")
                                
                                if edited_value != row[selected_csv]:
                                    with st.spinner('Updating...'):
                                        time.sleep(2)
                                        st.session_state.dataframe[selected_csv][index] = edited_value
                                        st.success(' Edited Successfully!')
                            st.divider()

                    save_edited_csv_btn = st.sidebar.button("Save edited CSV",type="primary")
                    if save_edited_csv_btn:
                        save_edited_csv(st.session_state.dataframe, csv_path)
                        time.sleep(2)
                        st.session_state.clear()
                        st.switch_page("main.py")

                            
if __name__ == "__main__":
    main()

