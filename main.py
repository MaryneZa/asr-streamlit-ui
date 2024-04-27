import streamlit as st
import pandas as pd 
import io
import time
from database import get_csv_file, name_csv_list, upload_edited_csv_file


def convert_df():
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    df = st.session_state.dataframe
    return df.to_csv().encode('utf-8')

st.set_page_config(
    page_title="Editing CSV",
    page_icon="🧊",
    layout="centered",
)

def load_data_for_page(data_frame, page_number, rows_per_page):
    start_index = page_number * rows_per_page
    end_index = (page_number + 1) * rows_per_page
    return data_frame.iloc[start_index:end_index]

# Function to save edited CSV data
def save_edited_csv(data_frame, csv_path):
    edited_csv = data_frame.to_csv(index=False)
    upload_edited_csv_file(edited_csv, csv_path)
    st.toast(":green[Edited CSV file saved successfully.]", icon="🎉")

def handle_selected_file():
    st.session_state.clear()

def handle_next_page():
    save_edited_csv(
        st.session_state.dataframe, 
        f"{st.session_state.selected_csv_file}/{st.session_state.file}"
        )
    st.session_state.page_number += 1

def handle_previous_page():
    st.session_state.page_number -=1
    


def main():
    
    cols_head = st.columns([0.5,0.3,0.2], gap="small")
    with cols_head[0]:
        st.title(":blue[CSV TextEdit Hub]")
    with cols_head[1]:
        st.image("./assets/cat.png", caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="png")
    
    
    csv_list = name_csv_list("csv_files")

    cols_file = st.columns([0.6,0.4], gap="small")
    
    with cols_file[0]:
        selected_csv_file = st.selectbox(
            ":blue[Select Name]", 
            csv_list, 
            index=None,
            placeholder="please select ...",
            on_change=handle_selected_file
            )
    with cols_file[1]:
        file = st.selectbox(
            ":blue[Select File]", 
            ["train.csv", "val.csv"],
            index=None,
            placeholder="please select ...",
            on_change=handle_selected_file
            )
        
        if file and 'file' not in st.session_state:
            st.session_state.file = file
        
    if selected_csv_file and file:
        
        st.session_state.selected_csv_file = selected_csv_file
        
        csv, message = get_csv_file(st.session_state.selected_csv_file,file)
        
        if csv:
            data = pd.read_csv(io.BytesIO(csv))
            df = pd.DataFrame(data)
            
            selected_csv = "text"
            
            if selected_csv:
                if 'dataframe' not in st.session_state:
                    st.session_state.dataframe = df
                
                if 'edited_row' not in st.session_state:
                    st.session_state.edited_row = []
                
                if 'page_number' not in st.session_state:
                    st.session_state.page_number = 1
        
                
                
                selected_audio = "full_path"
                
                if selected_audio:
                    rows_per_page = 10
                    total_rows = len(df)
                    total_pages = total_rows // rows_per_page + 1 if total_rows % rows_per_page != 0 else total_rows // rows_per_page
                    selected_csv_data = load_data_for_page(st.session_state.dataframe, st.session_state.page_number - 1, rows_per_page)
                    # st.sidebar.write(selected_csv_data)
                    for index, row in selected_csv_data[[selected_csv]].iterrows():
                        st.write(f":blue[Index : {index}]")
                        with st.container(border=True):
                    
                            st.audio(df["audio_link"][index], format="audio/wav")
                            
                            st.text_input(f"Default {selected_csv}", value=df["raw_text"][index], disabled=True, autocomplete="off")
                            
                            text_input_key = f"text-{index}-{selected_csv}"
                            # Get the edited value from the user
                            edited_value = st.text_input(f"Edit {selected_csv}", value=row[selected_csv], key=text_input_key, autocomplete="off")
                            
                            if edited_value != row[selected_csv]:
                                with st.spinner('Updating...'):
                                    st.session_state.dataframe[selected_csv][index] = edited_value
                                    if index not in st.session_state.edited_row:
                                        st.session_state.edited_row.append(index)
                                    st.success(' Edited Successfully!')
                                    
                        st.divider()
                            
                    cols = st.columns([0.2,0.6,0.2], gap="large")
                    with cols[0]:
                        if st.session_state.page_number > 1:
                            st.button("Previous", type="primary", on_click=handle_previous_page)
                            
                    # with cols[1]:
                    #     st.write(st.session_state.page_number)
                        
                    with cols[2]:
                        if st.session_state.page_number <= total_pages:
                            st.button("Next Page", type="primary", on_click=handle_next_page)
                                # save_edited_csv(st.session_state.dataframe, f"{selected_csv_file}/{file}")
                        else:
                            st.download_button(
                                label=":blue[Download CSV]",
                                data=convert_df(),
                                file_name=f'{selected_csv_file}_{file}.csv',
                                mime='text/csv',
                                # type="primary",
                            )
        else :
            st.toast(message)                    
                            
if __name__ == "__main__":
    main()

