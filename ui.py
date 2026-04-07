import streamlit as st

def render_ui():
    st.set_page_config(layout="wide", page_title="Medical Archive")
    st.title("Medical Archive & X-Ray Analysis System 🏥")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.header("X-Ray Analysis")
        uploaded_file = st.file_uploader("Upload an X-Ray image", type=["png", "jpg", "jpeg"])

        if uploaded_file:
            st.image(uploaded_file, caption="Original Image", use_container_width=True)

            b1, b2, b3 = st.columns(3)
            if b1.button("Invert Colors"):
                st.success("Invert filter applied!")
            if b2.button("Sharpen"):
                st.info("Sharpen filter applied!")
            if b3.button("Zoom"):
                st.warning("Zoom applied!")

    with col_right:
        st.header("Live Monitoring")
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")

        st.divider()

        st.header("Archiving")
        if st.button("Archive Lossless (RLE)", type="primary"):
            st.write("Compressing file...")