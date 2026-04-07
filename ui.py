import streamlit as st
from PIL import Image
import numpy as np

from image_processing import rotate_image, crop_image, apply_clahe, apply_sharpening, get_histogram_data

def render_ui():
    # initializam istoricul daca nu exista
    if "history" not in st.session_state:
        st.session_state.history = []

    def apply_action(func, *args, **kwargs):
        """Executa procesarea si inregistreaza automat pasul"""
        if st.session_state.current_image is not None:
            # aplicam algoritmul
            result = func(st.session_state.current_image, *args, **kwargs)
            # actualizam imaginea pe ecran
            st.session_state.current_image = result
            # salvam in timeline pentru video
            st.session_state.history.append(result.copy())
            st.toast("Step recorded in workflow!")
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
            st.session_state.history = []

        if st.session_state.current_image is not None:
            st.subheader("🛠️ Tools")

            tab_filters, tab_geometry, tab_reset = st.tabs(["✨ Filters", "📐 Geometry", "🔄 Reset"])

            with tab_filters:
                st.write("Quick image adjustments:")

                if st.button("Sharpen (Unsharp Masking)", use_container_width=True):
                    apply_action(apply_sharpening)
                    st.toast("Clarity increased with Unsharp Masking!")
                if st.button("✨ Apply CLAHE (Contrast)", use_container_width=True):
                    apply_action(apply_clahe)
                    st.toast("CLAHE contrast applied!")

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

                    st.session_state.history = []

    with col_viewer:
        st.subheader("👁️ Medical Viewer")
        with st.container(border=True):
            if st.session_state.current_image is not None:
                st.image(st.session_state.current_image, use_container_width=True)

                # --- histograma live ---
                st.divider()
                st.markdown("##### 📊 Image Intensity Histogram")

                # obtinem datele
                hist_values = get_histogram_data(st.session_state.current_image)

                # afisam folosind graficul nativ Streamlit (line chart)
                st.line_chart(hist_values, height=150, use_container_width=True)
                st.caption("Distribution of pixel intensities (0 = Black, 255 = White)")
            else:
                st.info("Waiting for an image upload to begin analysis...")

        st.divider()

        with st.expander("📺 Dynamic Examination Viewer (Ultrasound / 3D CT)"):
            st.write("This section allows for the visualization of the patient's dynamic recordings.")

            video_url = "https://www.youtube.com/watch?v=_XkP76YKraw"

            st.video(video_url)

    with col_archive:
        st.subheader("💾 Save / Archive")

        if st.session_state.current_image is not None:
            h, w = st.session_state.current_image.shape[:2]
            st.caption(f"**File:** {st.session_state.file_name}")
            st.caption(f"**Resolution:** {w} x {h} px")
            st.divider()

            # --- video generat ---
            with st.expander("🎬 Workflow Video Generator"):
                st.write(f"Steps recorded: **{len(st.session_state.history)}**")

                if st.button("Generate Diagnostic Video", use_container_width=True):
                    if len(st.session_state.history) > 0:
                        from image_processing import create_diagnostic_video
                        import os
                        with st.spinner("Rendering video..."):
                            folder = "video"
                            # trimitem istoricul si imaginea originala catre functia din image_processing
                            success = create_diagnostic_video(
                                st.session_state.history,
                                st.session_state.original_image
                            )
                            if success:
                                video_path = os.path.join(folder, "workflow_summary.mp4")
                                # Streamlit va reda fisierul generat local pe disc
                                with open(video_path, "rb") as v_file:
                                    video_bytes = v_file.read()

                                st.video(video_bytes)
                                st.success("Analysis sequence generated!")
                                st.download_button(
                                    label="📥 Download Diagnostic Video",
                                    data=video_bytes,
                                    file_name=f"diagnostic_{st.session_state.file_name}.mp4",
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                    else:
                        st.warning("Apply some filters first to record steps.")

            st.divider()

        st.markdown("**Lossless Archive (RLE)**")
        if st.button("📦 Compress & Save", type="primary", use_container_width=True):
            st.write("Compressing file...")