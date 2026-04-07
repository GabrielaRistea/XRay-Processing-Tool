import streamlit as st
from PIL import Image
import numpy as np

from image_processing import rotate_image, crop_image

def render_ui():
    st.set_page_config(layout="wide", page_title="Medical Archive", initial_sidebar_state="collapsed")
    st.title("Medical Archive & X-Ray Analysis System 🏥")

    if "current_image" not in st.session_state:
        st.session_state.current_image = None
    if "original_image" not in st.session_state:
        st.session_state.original_image = None
    if "file_name" not in st.session_state:
        st.session_state.file_name = None

    col_tools, col_viewer, col_archive = st.columns([1.5, 2.5, 1], gap="large")

    with col_tools:
        st.subheader("📁 Upload")
        uploaded_file = st.file_uploader("Select X-Ray image", type=["png", "jpg", "jpeg"],
                                         label_visibility="collapsed")

        if uploaded_file and uploaded_file.name != st.session_state.file_name:
            image = Image.open(uploaded_file)
            img_array = np.array(image)
            st.session_state.original_image = img_array.copy()
            st.session_state.current_image = img_array.copy()
            st.session_state.file_name = uploaded_file.name

        if st.session_state.current_image is not None:
            st.subheader("🛠️ Tools")

            tab_filters, tab_geometry, tab_reset = st.tabs(["✨ Filters", "📐 Geometry", "🔄 Reset"])

            with tab_filters:
                st.write("Quick image adjustments:")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Invert Colors", use_container_width=True):
                        st.toast("Filter applied!")
                with col_btn2:
                    if st.button("Sharpen", use_container_width=True):
                        st.toast("Clarity increased!")

            with tab_geometry:
                st.markdown("**1. Rotation**")
                col_r1, col_r2 = st.columns([2, 1])
                with col_r1:
                    angle = st.number_input("Degrees", min_value=-180, max_value=180, value=0,
                                            label_visibility="collapsed")
                with col_r2:
                    if st.button("Apply", key="btn_rot", use_container_width=True):
                        st.session_state.current_image = rotate_image(st.session_state.current_image, angle)

                st.divider()

                st.markdown("**2. Crop**")
                h, w = st.session_state.current_image.shape[:2]
                x_range = st.slider("Width (X)", 0, w, (0, w))
                y_range = st.slider("Height (Y)", 0, h, (0, h))

                if st.button("✂️ Crop Selection", type="primary", use_container_width=True):
                    st.session_state.current_image = crop_image(st.session_state.current_image, y_range[0], y_range[1],
                                                                x_range[0], x_range[1])

            with tab_reset:
                st.write("Discard all changes:")
                if st.button("🗑️ Reset to Original", type="primary", use_container_width=True):
                    st.session_state.current_image = st.session_state.original_image.copy()

    with col_viewer:
        st.subheader("👁️ Medical Viewer")
        with st.container(border=True):
            if st.session_state.current_image is not None:
                st.image(st.session_state.current_image, use_container_width=True)
            else:
                st.info("Waiting for an image upload to begin analysis...")

    with col_archive:
        st.subheader("💾 Save / Archive")

        if st.session_state.current_image is not None:
            h, w = st.session_state.current_image.shape[:2]
            st.caption(f"**File:** {st.session_state.file_name}")
            st.caption(f"**Resolution:** {w} x {h} px")
            st.divider()

        st.markdown("**Lossless Archive (RLE)**")
        if st.button("📦 Compress & Save", type="primary", use_container_width=True):
            st.write("Compressing file...")