"""
Upload Page UI - Upload books, syllabus, and previous papers
"""

import streamlit as st
import os
from utils.config import get_subject, get_subjects, get_syllabus, DATA_DIR
from utils.helpers import ensure_data_dirs
import utils.database as db
from modules.ocr_engine import extract_text_from_file, extract_chapters_from_text, save_processed_content, get_ocr_status
from modules.ai_engine import analyze_exam_paper


def render_upload():
    """Render the upload page."""
    st.markdown('<div class="page-title">📤 Upload Study Materials</div>', unsafe_allow_html=True)

    ensure_data_dirs()

    st.markdown("""
    <div class="upload-banner">
        📁 Upload your textbooks, syllabus, and previous year papers here.
        The AI Tutor will read and learn from them!
    </div>
    """, unsafe_allow_html=True)

    # OCR status
    with st.expander("🔧 System Status", expanded=False):
        status = get_ocr_status()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            icon = "✅" if status["pdfplumber"] else "❌"
            st.markdown(f"{icon} PDF Reader (pdfplumber)")
        with col2:
            icon = "✅" if status["PyPDF2"] else "⚠️"
            st.markdown(f"{icon} PDF Fallback (PyPDF2)")
        with col3:
            icon = "✅" if status["PIL"] else "❌"
            st.markdown(f"{icon} Image Support (PIL)")
        with col4:
            icon = "✅" if status["pytesseract"] else "❌"
            st.markdown(f"{icon} OCR (pytesseract)")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Textbooks", "📋 Syllabus", "📝 Past Papers & Answer Sheets", "📂 View Uploads"
    ])

    with tab1:
        _render_book_upload()
    with tab2:
        _render_syllabus_upload()
    with tab3:
        _render_paper_upload()
    with tab4:
        _render_uploaded_files()


def _render_book_upload():
    """Upload textbook pages."""
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)

    st.markdown("### 📚 Upload Textbook Pages")
    st.info(
        "📌 **How to organize your uploads:**\n"
        "1. Select the subject\n"
        "2. Upload PDF or scanned image pages of your textbook\n"
        "3. The AI will extract text and make it available for learning"
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        subject_names = [f"{s['icon']} {s['name']}" for s in SUBJECTS]
        subject_ids = [s["id"] for s in SUBJECTS]
        sel = st.selectbox("📚 Subject", subject_names, key="book_subject")
        subject_id = subject_ids[subject_names.index(sel)]

    with col2:
        content_type_options = ["Chapter Content", "Notes", "Summary", "Other"]
        content_type = st.selectbox("📑 Content Type", content_type_options, key="book_content_type")

    uploaded_files = st.file_uploader(
        "📁 Upload Files (PDF, JPG, PNG, TXT)",
        accept_multiple_files=True,
        type=["pdf", "jpg", "jpeg", "png", "txt"],
        key="book_uploader"
    )

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) selected")

    if st.button("⬆️ Upload & Process", key="upload_book", use_container_width=True,
                 disabled=not uploaded_files):
        if uploaded_files:
            progress_bar = st.progress(0, text="Processing files...")
            success_count = 0

            for i, file in enumerate(uploaded_files):
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress, text=f"Processing {file.name}...")

                try:
                    # Extract text
                    extracted_text, file_type = extract_text_from_file(file)

                    if not extracted_text.startswith("["):  # Not an error message
                        # Save to processed directory
                        processed_dir = os.path.join(DATA_DIR, "processed")
                        file_path = save_processed_content(
                            subject_id, file.name, extracted_text, processed_dir
                        )

                        # Save to database
                        db.save_uploaded_content(
                            filename=file.name,
                            subject=subject_id,
                            content_type=content_type,
                            extracted_text=extracted_text,
                            file_path=file_path
                        )
                        success_count += 1
                    else:
                        st.warning(f"⚠️ {file.name}: {extracted_text}")

                except Exception as e:
                    st.error(f"❌ Error processing {file.name}: {str(e)}")

            progress_bar.progress(1.0, text="Done!")

            if success_count > 0:
                db.award_badge("upload_hero", "Upload Hero", "📤")
                db.add_points(25 * success_count)
                st.success(
                    f"✅ Successfully processed **{success_count}** file(s)! "
                    f"The AI Tutor has learned from your books! +{25*success_count} points!"
                )
                st.balloons()
            else:
                st.warning("No files were successfully processed. Check the file formats.")


def _render_syllabus_upload():
    """Upload syllabus files."""
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)

    st.markdown("### 📋 Upload Syllabus")
    st.info(
        "Upload your ICSE Class 6 syllabus here. The tutor will use it to:\n"
        "- Generate questions based on exact syllabus topics\n"
        "- Track which topics have been covered\n"
        "- Suggest study plans aligned to syllabus"
    )

    col1, col2 = st.columns(2)
    with col1:
        subject_names = ["📚 All Subjects"] + [f"{s['icon']} {s['name']}" for s in SUBJECTS]
        subject_ids = ["all"] + [s["id"] for s in SUBJECTS]
        sel = st.selectbox("📚 Subject", subject_names, key="syl_subject")
        subject_id = subject_ids[subject_names.index(sel)]

    syllabus_file = st.file_uploader(
        "📁 Upload Syllabus (PDF or TXT)",
        type=["pdf", "txt"],
        key="syllabus_uploader"
    )

    if st.button("⬆️ Upload Syllabus", key="upload_syllabus", use_container_width=True,
                 disabled=not syllabus_file):
        if syllabus_file:
            with st.spinner("Processing syllabus..."):
                extracted_text, file_type = extract_text_from_file(syllabus_file)

                if not extracted_text.startswith("["):
                    # Save to syllabus directory
                    syllabus_dir = os.path.join(DATA_DIR, "syllabus")
                    os.makedirs(syllabus_dir, exist_ok=True)
                    save_path = os.path.join(syllabus_dir, syllabus_file.name)
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(extracted_text)

                    db.save_uploaded_content(
                        filename=syllabus_file.name,
                        subject=subject_id,
                        content_type="syllabus",
                        extracted_text=extracted_text,
                        file_path=save_path
                    )
                    db.add_points(20)
                    st.success(f"✅ Syllabus uploaded successfully! +20 points!")
                    with st.expander("📋 Preview Extracted Content"):
                        st.text_area("", extracted_text[:2000], height=200)
                else:
                    st.error(extracted_text)

    # Auto-fetch ICSE syllabus info
    st.markdown("---")
    st.markdown("### 🌐 Built-in ICSE Class 6 Syllabus")
    st.info(
        "The app already includes the ICSE Class 6 syllabus for all subjects. "
        "Click below to see the built-in syllabus topics."
    )

    if st.button("📋 View Built-in ICSE Syllabus", key="view_builtin_syllabus"):
        SYLLABUS = get_syllabus()      # 🧠 Live curriculum (Phase 4)
        for subject in SUBJECTS:
            sid = subject["id"]
            if sid in SYLLABUS:
                with st.expander(f"{subject['icon']} {subject['name']}"):
                    chapters = SYLLABUS[sid].get("chapters", [])
                    for ch in chapters:
                        st.markdown(f"**Chapter {ch['id']}: {ch['title']}**")
                        if ch.get("topics"):
                            for t in ch["topics"]:
                                st.markdown(f"  • {t}")


def _render_paper_upload():
    """Upload previous year papers and answer sheets."""
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)

    st.markdown("### 📝 Upload Question Papers & Answer Sheets")
    st.info(
        "Upload these types of documents:\n"
        "- 📄 Previous Year Exam Papers\n"
        "- 📝 Class Test Papers\n"
        "- ✍️ Answer Sheets (your written answers) — AI will identify mistakes!\n"
        "- 📑 School Test Papers"
    )

    student = db.get_student()
    api_key = student.get("api_key", "") or ""

    col1, col2 = st.columns(2)
    with col1:
        subject_names = [f"{s['icon']} {s['name']}" for s in SUBJECTS]
        subject_ids = [s["id"] for s in SUBJECTS]
        sel = st.selectbox("📚 Subject", subject_names, key="paper_subject")
        subject_id = subject_ids[subject_names.index(sel)]

    with col2:
        paper_types = [
            "Previous Year Paper",
            "Class Test Paper",
            "Answer Sheet",
            "School Test Paper",
            "Practice Paper"
        ]
        paper_type = st.selectbox("📑 Paper Type", paper_types, key="paper_type")

    uploaded_files = st.file_uploader(
        "📁 Upload Files (PDF, JPG, PNG)",
        accept_multiple_files=True,
        type=["pdf", "jpg", "jpeg", "png"],
        key="paper_uploader"
    )

    analyze = st.checkbox("🤖 Analyze paper with AI (identify topics & generate similar questions)",
                          value=bool(api_key), key="paper_analyze")

    if st.button("⬆️ Upload & Analyze", key="upload_paper", use_container_width=True,
                 disabled=not uploaded_files):
        if uploaded_files:
            for file in uploaded_files:
                with st.spinner(f"Processing {file.name}..."):
                    try:
                        extracted_text, file_type = extract_text_from_file(file)

                        if not extracted_text.startswith("["):
                            processed_dir = os.path.join(DATA_DIR, "previous_papers")
                            os.makedirs(processed_dir, exist_ok=True)
                            file_path = save_processed_content(
                                subject_id, file.name, extracted_text, processed_dir
                            )
                            db.save_uploaded_content(
                                filename=file.name,
                                subject=subject_id,
                                content_type=paper_type.lower().replace(" ", "_"),
                                extracted_text=extracted_text,
                                file_path=file_path
                            )
                            db.add_points(15)
                            st.success(f"✅ {file.name} uploaded! +15 points!")

                            if analyze:
                                with st.spinner("🤖 AI is analyzing the paper..."):
                                    analysis = analyze_exam_paper(extracted_text, api_key)

                                with st.expander(f"🤖 AI Analysis of {file.name}"):
                                    st.markdown(analysis)

                            # Show preview
                            with st.expander(f"📄 Preview: {file.name}"):
                                st.text_area("Extracted text (first 1000 chars):",
                                             extracted_text[:1000], height=200)
                        else:
                            st.warning(f"⚠️ {file.name}: {extracted_text}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")


def _render_uploaded_files():
    """View all uploaded files."""
    SUBJECTS = get_subjects()         # 🧠 Live curriculum (Phase 4)

    st.markdown("### 📂 Uploaded Files")

    uploaded = db.get_uploaded_content()

    if not uploaded:
        st.info("No files uploaded yet. Go to the other tabs to upload your study materials!")
        return

    # Filter by subject
    subject_filter_names = ["All Subjects"] + [f"{s['icon']} {s['name']}" for s in SUBJECTS]
    subject_filter_ids = [None] + [s["id"] for s in SUBJECTS]
    sel = st.selectbox("Filter by Subject:", subject_filter_names, key="upload_filter")
    filter_id = subject_filter_ids[subject_filter_names.index(sel)]

    if filter_id:
        uploaded = [u for u in uploaded if u["subject"] == filter_id]

    st.markdown(f"**{len(uploaded)} file(s) found**")

    for item in uploaded:
        subj = get_subject(item["subject"])
        with st.expander(
            f"{subj['icon']} {item['filename']} | {item['content_type']} | {item['upload_date']}"
        ):
            col1, col2 = st.columns([3, 1])
            with col1:
                text = item.get("extracted_text", "")
                if text:
                    st.text_area(
                        "Content Preview:",
                        text[:500] + ("..." if len(text) > 500 else ""),
                        height=150,
                        key=f"file_preview_{item['id']}"
                    )
                    st.caption(f"Total characters: {len(text):,}")

            with col2:
                st.markdown(f"**Subject:** {subj['name']}")
                st.markdown(f"**Type:** {item['content_type']}")
                st.markdown(f"**Date:** {item['upload_date']}")

                if st.button("🗑️ Delete", key=f"del_{item['id']}", type="secondary"):
                    db.delete_uploaded_content(item['id'])
                    st.success("Deleted!")
                    st.rerun()
