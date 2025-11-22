import pandas as pd
import streamlit as st

st.title("ChatBot Evaluation Questions")

st.write("### Trick Questions")

trick_df = pd.read_csv("questions/trick_questions_metro_german.csv", sep=";")
edited_trick_df = st.data_editor(
    trick_df,
    num_rows="dynamic",
    use_container_width=True,
)

# Button to save the edited dataframe to a CSV file
if st.button("Save Changes for Trick Questions"):
    edited_trick_df.to_csv("questions/trick_questions_metro_german.csv", index=False)
    st.success("Trick questions saved successfully!")
    

st.write("### AugmentedFAQ Questions")

augmented_faq_df = pd.read_csv("questions/test_fragen.csv")
edited_augmented_faq_df = st.data_editor(
    augmented_faq_df,
    num_rows="dynamic",
    use_container_width=True,
    column_order=["modifiert question", "FAQ questions", "type change", "FAQ answers"]  # Specify your desired column order
)

# Button to save the edited dataframe to a CSV file
if st.button("Save Changes for Augmented FAQ Questions"):
    edited_augmented_faq_df.to_csv("questions/faqs_metro_german.csv", index=False)
    st.success("Augmented FAQ questions saved successfully!")



st.write("### FAQ Questions")

faq_df = pd.read_csv("questions/faqs_metro_german.csv")
edited_faq_df = st.data_editor(
    faq_df,
    num_rows="dynamic",
    use_container_width=True,
)

# Button to save the edited dataframe to a CSV file
if st.button("Save Changes for FAQ Questions"):
    edited_faq_df.to_csv("questions/faqs_metro_german.csv", index=False)
    st.success("FAQ questions saved successfully!")
