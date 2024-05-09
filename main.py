import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import io
import time
from database import (
    get_csv_file,
    name_csv_list,
    name_csv_group_list,
    upload_edited_csv_file,
)

st.set_page_config(
    page_title="Editing CSV",
    page_icon="🧊",
    layout="centered",
)


def load_data_for_page(data_frame, page_number, rows_per_page, selected_set):
    """
    Load data from a DataFrame for a specific page.

    Args:
        data_frame (DataFrame): The DataFrame containing the data to be loaded.
        page_number (int): The page number to load.
        rows_per_page (int): The number of rows per page.
        selected_set (int): The selected set/group number.

    Returns:
        DataFrame: A subset of the DataFrame containing data for the specified page.

    Raises:
        ValueError: If page_number or rows_per_page is negative, or if selected_set is not found in the DataFrame.
    """
    try:
        # Filter the DataFrame based on the selected set/group
        df = data_frame[data_frame["group"] == selected_set].iloc[:]

        # Calculate start and end indices for the specified page
        start_index = page_number * rows_per_page
        end_index = (page_number + 1) * rows_per_page

        # Return the subset of the DataFrame for the specified page
        return df.iloc[start_index:end_index]
    
    except Exception as e:
        print("An error occurred:", e)



def edit_status_done(selected_set):
    """
    Mark the edit status as done for a selected set/group and perform additional actions.

    Args:
        selected_set (int): The selected set/group number.

    Returns:
        None

    Raises:
        ValueError: If selected_set is not found in the session DataFrame.
    """
    try:
        # Mark the edit status as done for the selected set/group
        st.session_state.concatenated_df.loc[
            st.session_state.concatenated_df["group"] == selected_set, "edit_status"
        ] = True
        

        handle_next_page()

        # Clear session state 
        st.session_state.clear()
    
    except Exception as e:
        print("An error occurred:", e)



def save_edited_csv(data_frame, csv_path):
    """
    Save edited CSV data to Firebase Storage.

    Args:
        data_frame (DataFrame): The DataFrame containing the edited CSV data.
        csv_path (str): The path of the CSV file on Firebase Storage.

    Returns:
        None

    Raises:
        ValueError: If the CSV path is None or empty.
        IOError: If there are issues saving the edited CSV data to Firebase Storage.
    """
    try:
        edited_csv = data_frame.to_csv(index=False)

        upload_edited_csv_file(edited_csv, csv_path)
    
    except Exception as e:
        print("An error occurred:", e)



def handle_selected_file():
    """
    Handle the selection of a file by clearing the session state.

    Returns:
        None
    """
    try:
        # Clear session state
        st.session_state.clear()
    
    except Exception as e:
        print("An error occurred:", e)



def handle_next_page():
    """
    Handle the transition to the next page by saving edited CSV data and updating session state.

    Returns:
        None
    """
    try:

        csv_name = st.session_state.selected_csv_file
        df_group = st.session_state.concatenated_df[st.session_state.concatenated_df["group"] == st.session_state.selected_set].iloc[:]
        save_edited_csv(df_group, f"{csv_name}/group_{st.session_state.selected_set}.csv")
        

        # Display a success toast message
        st.toast(":green[Edited CSV files saved successfully.]", icon="🎉")

        # Update session state variables
        st.session_state.page_number += 1
        st.session_state.counter += 1
    
    except Exception as e:
        print("An error occurred:", e)



def get_group_numbers_with_edit_status_true(csv_group_list):
    """
    Get group numbers where the edit_status is True in the DataFrame.

    Args:
        data_frame (DataFrame): The DataFrame containing the data.

    Returns:
        numpy.ndarray: An array of unique group numbers with edit_status set to True.

    Raises:
        ValueError: If the DataFrame is empty or if the column edit_status is not found.
    """
    try:
        num = []
        # Filter the DataFrame to include only rows where edit_status is True
        for file in csv_group_list:
            csv_file = get_csv_file(st.session_state.selected_csv_file, file)
            df = pd.read_csv(io.BytesIO(csv_file))

            # Get the unique values from the group column
            group_numbers_edit_true = df["edit_status"].unique()
            if bool(group_numbers_edit_true[0]) :
                file = file.split(".csv")[0]
                num.append(int(file.split("_")[-1]))
                print("HI")
        return num
    
    except Exception as e:
        print("An error occurred:", e)



def handle_previous_page():
    """
    Handle the transition to the previous page by updating session state.

    Returns:
        None
    """
    try:
        # Update session state variables
        st.session_state.page_number -= 1
        st.session_state.counter += 1
    
    except Exception as e:
        print("An error occurred:", e)



def load_concat_data(csv_file):
    """
    Load and concatenate data from train and val CSV files.

    Args:
        csv_file (str): The name of the CSV file containing train and val data.

    Returns:
        DataFrame: Concatenated DataFrame containing train and val data.
        int: Length of the train data.

    Raises:
        ValueError: If the CSV file name is invalid or if train or val data is not found.
        IOError: If there are issues loading or concatenating the CSV data.
    """
    try:
        # Get train data from CSV
        train_csv = get_csv_file(csv_file, "train.csv")
        train_data = pd.read_csv(io.BytesIO(train_csv))

        # Get val data from CSV
        val_csv = get_csv_file(csv_file, "val.csv")
        val_data = pd.read_csv(io.BytesIO(val_csv))

        # Concatenate train and val data
        concatenated_df = pd.concat([train_data, val_data], ignore_index=True)

        # Return concatenated DataFrame and length of train data
        return concatenated_df, len(train_data)
    
    except Exception as e:
        print("An error occurred:", e)



def main():

    cols_head = st.columns([0.5, 0.3, 0.2], gap="small")
    with cols_head[0]:
        st.title(":blue[CSV TextEdit Hub]")
    with cols_head[1]:
        st.image(
            "./assets/cat.png",
            caption=None,
            width=None,
            use_column_width=None,
            clamp=False,
            channels="RGB",
            output_format="png",
        )

    csv_list = name_csv_list("csv_files")

    cols_file = st.columns([0.6, 0.4], gap="small")

    with cols_file[0]:
        selected_csv_file = st.selectbox(
            ":blue[Select Name]",
            csv_list,
            index=None,
            placeholder="please select ...",
            on_change=handle_selected_file,
        )

    with cols_file[1]:
        if selected_csv_file:
            st.session_state.selected_csv_file = selected_csv_file
            
            csv_group_list = name_csv_group_list(f"csv_files/{st.session_state.selected_csv_file}")            
            
            if "concatenated_df" not in st.session_state:
                st.session_state.concatenated_df, st.session_state.len_train_df = (
                    load_concat_data(st.session_state.selected_csv_file)
                )
                # st.sidebar.write("Hi")

            
            highest_value = st.session_state.concatenated_df["group"].max()

            if "done_set" not in st.session_state:
                st.session_state.done_set = get_group_numbers_with_edit_status_true(
                    csv_group_list
                )
                
            if "done_set" in st.session_state:
                
                set = list(range(1, highest_value + 1))

                # Generate the list of options with labels indicating whether they are done or not
                options = [
                    (num, f"{num} (done)") if num in st.session_state.done_set else (num, num) for num in set
                ]

                # Set up the selectbox with the modified list of options
                selected_set = st.selectbox(
                    ":blue[Select dataset]",
                    options,
                    index=None,
                    format_func=lambda x: x[1],
                    on_change=handle_selected_file,
                )

                if selected_set and "selected_set" not in st.session_state:
                    st.session_state.selected_set = selected_set[0]

                if "counter" not in st.session_state:
                    st.session_state.counter = 1

                components.html(
                    f"""
                        <p>{st.session_state.counter}</p>
                        <script>
                            window.parent.document.querySelector('section.main').scrollTo(0, 0);
                        </script>
                    """,
                    height=0,
                )

    if "selected_set" in st.session_state and "done_set" in st.session_state:
        if selected_csv_file and st.session_state.selected_set not in st.session_state.done_set:
            selected_csv = "text"

            if "page_number" not in st.session_state:
                st.session_state.page_number = 1

            rows_per_page = 10
            total_rows = len(
                st.session_state.concatenated_df[
                    st.session_state.concatenated_df["group"]
                    == st.session_state.selected_set
                ]
            )
            total_pages = (
                total_rows // rows_per_page + 1
                if total_rows % rows_per_page != 0
                else total_rows // rows_per_page
            )
            selected_csv_data = load_data_for_page(
                st.session_state.concatenated_df,
                st.session_state.page_number - 1,
                rows_per_page,
                st.session_state.selected_set,
            )

            
            for index, row in selected_csv_data[[selected_csv]].iterrows():
                st.write(f":blue[Index : {index%100}]")
                with st.container(border=True):
                    text_input_key = f"text-{index}-{selected_csv}"

                    with st.container(border=True):
                        st.audio(
                            st.session_state.concatenated_df.loc[index, "audio_link"],
                            format="audio/wav",
                        )
                        audio_cols = st.columns(2)
                        with audio_cols[0]:
                            multi_speaker = st.toggle(
                                ":blue[มีเสียงพูดหลายคน]",
                                key=f"{text_input_key}_m",
                                value=st.session_state.concatenated_df.loc[
                                    index, "multi_speaker"
                                ],
                            )
                            if (
                                multi_speaker
                                != st.session_state.concatenated_df.loc[
                                    index, "multi_speaker"
                                ]
                            ):
                                st.session_state.concatenated_df.loc[
                                    index, "multi_speaker"
                                ] = multi_speaker
                                st.experimental_rerun()

                            loud_noise = st.toggle(
                                ":blue[มี noise ดัง]",
                                key=f"{text_input_key}_l",
                                value=st.session_state.concatenated_df.loc[
                                    index, "loud_noise"
                                ],
                            )
                            if (
                                loud_noise
                                != st.session_state.concatenated_df.loc[
                                    index, "loud_noise"
                                ]
                            ):
                                st.session_state.concatenated_df.loc[
                                    index, "loud_noise"
                                ] = loud_noise
                                st.experimental_rerun()

                        with audio_cols[1]:
                            unclear = st.toggle(
                                ":blue[ฟังไม่ออก/ไม่แน่ใจ]",
                                key=f"{text_input_key}_u",
                                value=st.session_state.concatenated_df.loc[
                                    index, "unclear"
                                ],
                            )
                            if (
                                unclear
                                != st.session_state.concatenated_df.loc[
                                    index, "unclear"
                                ]
                            ):
                                st.session_state.concatenated_df.loc[
                                    index, "unclear"
                                ] = unclear
                                st.experimental_rerun()

                            incomplete_sentence = st.toggle(
                                ":blue[มีเสียงต้นท้ายประโยค / พูดไม่ครบประโยค]",
                                key=f"{text_input_key}_i",
                                value=st.session_state.concatenated_df.loc[
                                    index, "incomplete_sentence"
                                ],
                            )
                            if (
                                incomplete_sentence
                                != st.session_state.concatenated_df.loc[
                                    index, "incomplete_sentence"
                                ]
                            ):
                                st.session_state.concatenated_df.loc[
                                    index, "incomplete_sentence"
                                ] = incomplete_sentence
                                st.experimental_rerun()

                    st.text_input(
                        f"Default {selected_csv}",
                        value=st.session_state.concatenated_df.loc[index, "raw_text"],
                        disabled=True,
                        autocomplete="off",
                    )

                    # Get the edited value from the user
                    edited_value = st.text_input(
                        f"Edit {selected_csv}",
                        value=st.session_state.concatenated_df.loc[index, selected_csv],
                        key=text_input_key,
                        autocomplete="off",
                    )

                    # Check if the value has changed
                    if (
                        edited_value
                        != st.session_state.concatenated_df.loc[index, selected_csv]
                    ):
                        # Update the value in the DataFrame
                        st.session_state.concatenated_df.loc[index, selected_csv] = (
                            edited_value
                        )
                        st.success("Edited Successfully!")
                        time.sleep(1)
                        st.experimental_rerun()

                st.divider()

            if st.session_state.page_number > total_pages:
                st.warning(
                    "Caution: Once you confirm the editing as done, no further modifications will be permitted."
                )

            cols = st.columns([0.4, 0.4, 0.2], gap="large")
            with cols[0]:
                if st.session_state.page_number > 1:
                    st.button("Previous", type="primary", on_click=handle_previous_page)

            with cols[1]:
                if st.session_state.page_number <= total_pages:
                    st.write(
                        f":blue[Page {st.session_state.page_number}] of :blue[{total_pages}]"
                    )

            with cols[2]:
                if st.session_state.page_number <= total_pages:
                    st.button("Next Page", type="primary", on_click=handle_next_page)

                else:
                    st.button(
                        label=":blue[Editing Done]",
                        on_click=lambda: edit_status_done(
                            st.session_state.selected_set
                        ),
                    )
        else:
            st.warning(
                f"The edits for set {st.session_state.selected_set} have already been completed."
            )


if __name__ == "__main__":
    main()
