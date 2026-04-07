import json
import streamlit as st
from PIL import Image
import numpy as np
import time
import os

from compression import compress_universal, save_compressed_file, decompress_universal
from image_processing import rotate_image, crop_image, apply_median_blur, apply_otsu_threshold, calculate_bone_mass, \
    apply_canny_edge_detection


def render_ui():
    st.set_page_config(layout="wide", page_title="Medical Archive", initial_sidebar_state="collapsed")
    st.title("Medical Archive & X-Ray Analysis System 🏥")

    if "current_image" not in st.session_state:
        st.session_state.current_image = None
    if "original_image" not in st.session_state:
        st.session_state.original_image = None
    if "file_name" not in st.session_state:
        st.session_state.file_name = None

    if "patient_name" not in st.session_state: st.session_state.patient_name = ""
    if "patient_id" not in st.session_state: st.session_state.patient_id = ""
    if "patient_age" not in st.session_state: st.session_state.patient_age = 30
    if "patient_gender" not in st.session_state: st.session_state.patient_gender = "Male"
    if "patient_notes" not in st.session_state: st.session_state.patient_notes = ""

    col_tools, col_viewer, col_archive = st.columns([1.5, 2.5, 1], gap="large")

    with col_tools:
        st.subheader("📁 Upload")

        uploaded_file = st.file_uploader("Select X-Ray image or Archive", type=["png", "jpg", "jpeg", "huff"],
                                         label_visibility="collapsed")

        if uploaded_file and uploaded_file.name != st.session_state.file_name:

            if uploaded_file.name.endswith('.huff'):
                try:
                    with st.spinner("Reconstructing image and medical records..."):
                        img_array, patient_data = decompress_universal(uploaded_file)

                        st.session_state.original_image = img_array.copy()
                        st.session_state.current_image = img_array.copy()
                        st.session_state.file_name = uploaded_file.name

                        st.session_state.patient_name = patient_data.get("name", "")
                        st.session_state.patient_id = patient_data.get("id", "")
                        st.session_state.patient_age = patient_data.get("age", 30)
                        st.session_state.patient_gender = patient_data.get("gender", "Male")
                        st.session_state.patient_notes = patient_data.get("notes", "")

                    st.success("Archive restored successfully!")
                except Exception as e:
                    st.error(f"Error reading archive: {e}")

            else:
                image = Image.open(uploaded_file)
                img_array = np.array(image)
                st.session_state.original_image = img_array.copy()
                st.session_state.current_image = img_array.copy()
                st.session_state.file_name = uploaded_file.name

                st.session_state.patient_name = ""
                st.session_state.patient_id = ""
                st.session_state.patient_age = 30
                st.session_state.patient_gender = "Male"
                st.session_state.patient_notes = ""

        if st.session_state.current_image is not None:
            st.subheader("🛠️ Tools")

            tab_patient, tab_medical, tab_geometry, tab_reset = st.tabs(
                ["📋 Patient", "🧬 Filters", "📐 Geometry", "🔄 Reset"])

            with tab_patient:
                st.markdown("**Patient Demographics**")
                st.text_input("Full Name", key="patient_name", placeholder="e.g., John Doe")
                st.text_input("Patient ID (SSN)", key="patient_id", placeholder="e.g., 19028374")

                col_age, col_gen = st.columns(2)
                with col_age:
                    st.number_input("Age", key="patient_age", min_value=0, max_value=120)
                with col_gen:
                    st.selectbox("Gender", ["Male", "Female", "Other"], key="patient_gender")

                st.text_area("Clinical Notes", key="patient_notes", placeholder="Enter initial observations here...")

            with tab_medical:
                st.write("Medical AI Analysis:")

                if st.button("🧼 Median Blur (Denoise)", use_container_width=True):
                    progress_text = "Loading..."
                    my_bar = st.progress(0, text=progress_text)
                    for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=f"{progress_text} {percent_complete}%")
                    st.session_state.current_image = apply_median_blur(st.session_state.current_image)
                    my_bar.empty()
                    st.toast("Noise removed!")

                if st.button("🦴 Otsu (Bone Segmentation)", use_container_width=True):
                    progress_text = "Analyzing density..."
                    my_bar = st.progress(0, text=progress_text)
                    for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=f"{progress_text} {percent_complete}%")

                    binary_result = apply_otsu_threshold(st.session_state.current_image)
                    st.session_state.current_image = binary_result
                    st.session_state.bone_mass = calculate_bone_mass(binary_result)

                    my_bar.empty()
                    st.toast("Segmentation complete!")

                if st.button("✏️ Edge Detection (Fracture Highlight)", use_container_width=True):
                    progress_text = "Tracing structural lines..."
                    my_bar = st.progress(0, text=progress_text)
                    for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=f"{progress_text} {percent_complete}%")

                    st.session_state.current_image = apply_canny_edge_detection(st.session_state.current_image)
                    my_bar.empty()
                    st.toast("Edges detected!")

                if "bone_mass" in st.session_state and st.session_state.bone_mass is not None:
                    st.divider()
                    st.metric(label="Estimated Bone Mass Density", value=f"{st.session_state.bone_mass}%")
                    st.caption("Note: This is a 2D area calculation based on pixel density.")

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
        viewer_placeholder = st.empty()

        with viewer_placeholder.container(border=True):
            if st.session_state.current_image is not None:
                st.image(st.session_state.current_image, use_container_width=True)
            else:
                st.info("Waiting for an image upload to begin analysis...")

    with col_archive:
        st.subheader("💾 Save / Archive")

        if st.session_state.current_image is not None:
            h, w = st.session_state.current_image.shape[:2]
            display_name = st.session_state.patient_name if st.session_state.patient_name else "Unknown"
            st.caption(f"**Patient:** {display_name}")
            st.caption(f"**File:** {st.session_state.file_name}")
            st.caption(f"**Resolution:** {w} x {h} px")
            st.divider()

        st.markdown("**Lossless Archive (Huffman)**")

        if st.button("📦 Compress & Archive", type="primary", use_container_width=True):
            if st.session_state.current_image is not None:
                with st.spinner("Applying Huffman compression..."):
                    img_to_compress = st.session_state.current_image
                    original_shape = img_to_compress.shape
                    original_dtype = img_to_compress.dtype

                    compressed_bytes = compress_universal(img_to_compress)

                    current_patient_meta = {
                        "name": st.session_state.patient_name,
                        "id": st.session_state.patient_id,
                        "age": st.session_state.patient_age,
                        "gender": st.session_state.patient_gender,
                        "notes": st.session_state.patient_notes
                    }

                    timestamp = int(time.time())
                    safe_patient_name = st.session_state.patient_name.replace(" ", "_").strip()
                    if not safe_patient_name:
                        safe_patient_name = "Unknown_Patient"

                    file_name = f"{safe_patient_name}_Medical_Record_{timestamp}.huff"

                    archive_dir = "medical_archives"
                    os.makedirs(archive_dir, exist_ok=True)

                    file_path = os.path.join(archive_dir, file_name)

                    save_compressed_file(compressed_bytes, original_shape, original_dtype, file_path,
                                         current_patient_meta)

                    original_size = img_to_compress.nbytes
                    compressed_size = os.path.getsize(file_path)
                    compression_ratio = 100 - ((compressed_size / original_size) * 100)

                st.success("Archive generated successfully!")

                st.write("**📊 Compression Report:**")
                st.write(f"- Original Size: `{original_size / 1024:.2f} KB`")
                st.write(f"- Archive Size: `{compressed_size / 1024:.2f} KB`")
                st.metric("Storage Saved", f"{compression_ratio:.1f}%")

                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download .huff Archive",
                        data=f,
                        file_name=file_name,
                        mime="application/octet-stream",
                        use_container_width=True
                    )
            else:
                st.error("Please upload an image first!")