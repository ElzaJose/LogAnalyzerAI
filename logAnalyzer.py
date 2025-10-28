import streamlit as st
import google.generativeai as genai
import os

# --- API CONFIG ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found in environment variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-pro")

# --- PAGE SETUP ---
st.set_page_config(page_title="AI Log Analyzer", page_icon="🧠", layout="centered")

st.title("🧠 AI Log Analyzer")
st.markdown(
    """
    Upload a **.txt log file** below to know about the test failure.
    """
)

uploaded_file = st.file_uploader("📂 Choose a test log file", type=["txt"])

if uploaded_file:
    log_text = uploaded_file.read().decode("utf-8")

    with st.spinner("🔍 Analyzing log file..."):
        prompt = (
            "You are a helpful assistant that summarizes log files clearly, so that the user can understand why the test failed. "
            "Also try suggesting possible fixes or next steps. Make it simple in the below format:\n\n"
            "TESTNAME: <testname>\n"
            "DEVICE : <Device>\n"
            "STATUS : <Status>\n"
            "ROOT CAUSE : <Explain why the test failed in simple terms. Not more than 2 sentences>\n"
            "SOLUTION : <Suggest a fix. If not sure give the solution as 'Reach out to support@rdkcentral.com'>"
            "If any of the above parameters are not available in the log file, skip that line. "
            "The only mandatory parameters are ROOT CAUSE and SOLUTION\n\n"
            f"{log_text}"
        )

        response = model.generate_content(prompt)
        summary = response.text

    # --- Display Styled Summary ---
    st.markdown("### 📋 Summary Report")
    formatted_summary = summary.replace("\n", "<br>")
    import re
    formatted_summary = re.sub(r"\b(TESTNAME|DEVICE|STATUS|ROOT CAUSE|SOLUTION)\s*:", 
                               r"<b>\1:</b>", formatted_summary)
    formatted_summary = formatted_summary.replace(
        "PASS", '<span style="background-color:#16a34a;color:white;padding:2px 6px;border-radius:4px;">PASS</span>'
    )
    formatted_summary = formatted_summary.replace(
        "PASSED", '<span style="background-color:#16a34a;color:white;padding:2px 6px;border-radius:4px;">PASSED</span>'
    )
    formatted_summary = formatted_summary.replace(
        "SUCCESS", '<span style="background-color:#16a34a;color:white;padding:2px 6px;border-radius:4px;">SUCCESS</span>'
    )
    formatted_summary = formatted_summary.replace(
        "FAILED", '<span style="background-color:#dc2626;color:white;padding:2px 6px;border-radius:4px;">FAILED</span>'
    )
    formatted_summary = formatted_summary.replace(
        "FAILURE", '<span style="background-color:#dc2626;color:white;padding:2px 6px;border-radius:4px;">FAILURE</span>'
    )

    # Try to extract individual fields (optional styling)
    def extract_field(label):
        for line in summary.splitlines():
            if line.strip().startswith(label):
                return line.split(":", 1)[-1].strip()
        return None

    testname = extract_field("TESTNAME")
    device = extract_field("DEVICE")
    status = extract_field("STATUS")
    root_cause = extract_field("Root cause")
    solution = extract_field("Solution")

    # Create a nice visual layout
    st.markdown(
        f"""
        <div style="
            background-color:#f9fafb;
            border:1px solid #e5e7eb;
            border-radius:12px;
            padding:24px;
            box-shadow:0 2px 6px rgba(0,0,0,0.05);
            font-family: 'Inter', sans-serif;
        ">
            {formatted_summary}
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.info("Please upload a `.txt` test log file to get the summary report.")
