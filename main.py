import streamlit as st
import pandas as pd
import io
from database import (
    get_csv_file,
    name_csv_list,
    upload_edited_csv_file,
)

st.set_page_config(
    page_title="Editing CSV",
    page_icon="🧊",
    layout="centered",
)


def load_data_for_page(data_frame, page_number, rows_per_page, selected_set):
    df = data_frame[data_frame["group"] == selected_set].iloc[:]

    start_index = page_number * rows_per_page
    end_index = (page_number + 1) * rows_per_page
    return df.iloc[start_index:end_index]


def edit_status_done(selected_set):
    st.session_state.concatenated_df.loc[
        st.session_state.concatenated_df["group"] == selected_set, "edit_status"
    ] = True
    handle_next_page()
    st.session_state.clear()
    # st.switch_page("main.py")


# Function to save edited CSV data
def save_edited_csv(data_frame, csv_path):
    edited_csv = data_frame.to_csv(index=False)
    upload_edited_csv_file(edited_csv, csv_path)


def handle_selected_file():
    st.session_state.clear()


def handle_next_page():

    # Get the length of the original DataFrames
    len_df = len(st.session_state.train_df)

    # Split the concatenated DataFrame back into DataFrames with the same length
    t_df = st.session_state.concatenated_df.iloc[:len_df]
    v_df = st.session_state.concatenated_df.iloc[len_df:]

    save_edited_csv(t_df, f"{st.session_state.selected_csv_file}/train.csv")
    save_edited_csv(v_df, f"{st.session_state.selected_csv_file}/val.csv")
    st.toast(":green[Edited CSV file saved successfully.]", icon="🎉")
    st.session_state.page_number += 1


def get_group_numbers_with_edit_status_true(data_frame):
    # Filter the DataFrame to include only rows where edit_status is True
    df_edit_true = data_frame[data_frame["edit_status"] == True]

    # Get the unique values from the group column
    group_numbers_edit_true = df_edit_true["group"].unique()

    return group_numbers_edit_true


def handle_previous_page():
    st.session_state.page_number -= 1


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

            train_csv, _ = get_csv_file(st.session_state.selected_csv_file, "train.csv")
            train_data = pd.read_csv(io.BytesIO(train_csv))
            train_df = pd.DataFrame(train_data)

            if "train_df" not in st.session_state:
                st.session_state.train_df = train_df

            val_csv, _ = get_csv_file(st.session_state.selected_csv_file, "val.csv")
            val_data = pd.read_csv(io.BytesIO(val_csv))
            val_df = pd.DataFrame(val_data)

            if "val_df" not in st.session_state:
                st.session_state.val_df = val_df

            if "concatenated_df" not in st.session_state:
                st.session_state.concatenated_df = pd.concat(
                    [train_df, val_df], ignore_index=True
                )

            highest_value = st.session_state.concatenated_df["group"].max()

            done_set = get_group_numbers_with_edit_status_true(
                st.session_state.concatenated_df
            )

            set = list(range(1, highest_value + 1))

            # Generate the list of options with labels indicating whether they are done or not
            options = [
                (num, f"{num} (done)") if num in done_set else (num, num) for num in set
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

    if "selected_set" in st.session_state:
        if selected_csv_file and st.session_state.selected_set not in done_set:

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
                            st.session_state.concatenated_df["audio_link"][index],
                            format="audio/wav",
                        )
                        audio_cols = st.columns(2)
                        with audio_cols[0]:

                            multi_speaker = st.toggle(
                                ":blue[มีเสียงพูดหลายคน]",
                                key=f"{text_input_key}_m",
                                value=st.session_state.concatenated_df["multi_speaker"][
                                    index
                                ],
                            )
                            if multi_speaker:
                                st.session_state.concatenated_df["multi_speaker"][
                                    index
                                ] = True
                            else:
                                st.session_state.concatenated_df["multi_speaker"][
                                    index
                                ] = False

                            loud_noise = st.toggle(
                                ":blue[มี noise ดัง]",
                                key=f"{text_input_key}_l",
                                value=st.session_state.concatenated_df["loud_noise"][
                                    index
                                ],
                            )
                            if loud_noise:
                                st.session_state.concatenated_df["loud_noise"][
                                    index
                                ] = True
                            else:
                                st.session_state.concatenated_df["loud_noise"][
                                    index
                                ] = False
                        with audio_cols[1]:
                            unclear = st.toggle(
                                ":blue[ฟังไม่ออก/ไม่แน่ใจ]",
                                key=f"{text_input_key}_u",
                                value=st.session_state.concatenated_df["unclear"][
                                    index
                                ],
                            )
                            if unclear:
                                st.session_state.concatenated_df["unclear"][
                                    index
                                ] = True
                            else:
                                st.session_state.concatenated_df["unclear"][
                                    index
                                ] = False

                            incomplete_sentence = st.toggle(
                                ":blue[มีเสียงต้นท้ายประโยค / พูดไม่ครบประโยค]",
                                key=f"{text_input_key}_i",
                                value=st.session_state.concatenated_df[
                                    "incomplete_sentence"
                                ][index],
                            )
                            if incomplete_sentence:
                                st.session_state.concatenated_df["incomplete_sentence"][
                                    index
                                ] = True
                            else:
                                st.session_state.concatenated_df["incomplete_sentence"][
                                    index
                                ] = False

                    st.text_input(
                        f"Default {selected_csv}",
                        value=st.session_state.concatenated_df["raw_text"][index],
                        disabled=True,
                        autocomplete="off",
                    )

                    # Get the edited value from the user
                    edited_value = st.text_input(
                        f"Edit {selected_csv}",
                        value=row[selected_csv],
                        key=text_input_key,
                        autocomplete="off",
                    )

                    if edited_value != row[selected_csv]:
                        st.session_state.concatenated_df[selected_csv][
                            index
                        ] = edited_value
                        st.success(" Edited Successfully!")

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
