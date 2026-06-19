# ================= SAFE FIX PATCH (ADD ONLY - DO NOT REMOVE ANYTHING) =================

def safe_create_pdf(issue_type, location, image_path, timestamp=None):
    """
    Wrapper to prevent TypeError crashes from pdf_utils
    """
    try:
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # try full version first
        try:
            return create_pdf(issue_type, location, image_path, timestamp)
        except TypeError:
            # fallback old version
            return create_pdf(issue_type, location, image_path)

    except Exception as e:
        st.error(f"PDF Creation Failed: {e}")
        return None


def safe_generate_report(issue_type, location, image_path):
    """
    SAFE REPORT GENERATION (used for video + live + image)
    """
    pdf_path = safe_create_pdf(issue_type, location, image_path)

    if pdf_path is None:
        return

    try:
        st.success("🏛 Official Government Report Generated")

        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇ Download Official Report (Gov Format)",
                f,
                file_name="National_Urban_Report.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Download Error: {e}")
