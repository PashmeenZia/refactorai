import streamlit as st
import black
import isort
import subprocess
import tempfile
import base64
import re
import random
import plotly.express as px
import ast
from radon.complexity import cc_visit
from streamlit_lottie import st_lottie
import requests

st.set_page_config(page_title="Refactor Pro Application", page_icon="🏷️", layout="wide")


@st.cache_data()
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


animation = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_j1adxtyb.json")

# Custom CSS
st.markdown("""
    <style>
    .big-title {text-align: center; font-size: 3em; color:#2575fc; font-weight: bold;}
    .subtitle {text-align: center; font-size: 20px; color: #444; font-style: italic;}
    .feature-box {background: linear-gradient(to right, #6a11cb, #2575fc); padding: 15px; border-radius: 8px; color: white; text-align: center; margin-bottom: 20px;}
    .doc-box {background : linear-gradient(to right, #6a11cb, #2575fc); padding: 15px; border-radius: 8px; color: white; text-align: center;}
    .score-box {background : linear-gradient(to right, #6a11cb, #2575fc); padding: 10px; border-radius: 8px; color: white; text-align: center; font-size: 24px; font-weight: bold;}
    .footer {text-align: center; font-size: 14px; color: #aaa; margin-top: 40px;}
    .social-icons img {width: 25px; margin: 0 5px; vertical-align: middle}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #6a11cb, #2575fc);
        color: white;
    }

    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Title and Animation
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("<div class='big-title'> AI-Powered Python Code Formatter & Optimizer 🚀</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Empower your Python code with AI-driven formatting, optimization, and analysis</div>", unsafe_allow_html=True)

with col2:
    if animation:
        st_lottie(animation, height=200, speed=1, loop=True)
    else:
        st.warning("⚠️ Failed to load animation")

# ---------- Sidebar ----------
def clear_code():
    st.session_state.input_code = ""

with st.sidebar:
    st.markdown("<div class='feature-box'><h2>🔧 Features</h2><p>Refactor, analyze data, optimized your given code.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='doc-box'><h3>📘 Documentation</h3><p>Get started with AI-driven optimization.</p></div>", unsafe_allow_html=True)
    st.button("🗑️ Clear Code", on_click=clear_code, help="Reset your code input")

# ---------- Code Input ----------
if "input_code" not in st.session_state:
    st.session_state.input_code = ""

tabs = st.tabs(["📝 Code Input", "⚙️ Refactored Output", "🎯 Scorecard", "📊 Module Graph", "✨ Code Optimization Suggestions"])

with tabs[0]:
    code_input = st.text_area("Paste your Python code here:", value=st.session_state.input_code, height=300, key="input_code")

# ---------- Functional Parts ----------
def refactor_code(code):
    sorted_code = isort.code(code)
    try:
        formatted_code = black.format_str(sorted_code, mode=black.Mode())
    except Exception as e:
        formatted_code = sorted_code + f"\n\n# Formatting Error: {e}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp_file:
        tmp_file.write(formatted_code)
        tmp_path = tmp_file.name
    result = subprocess.run(["flake8", tmp_path], capture_output=True, text=True)
    return formatted_code, result.stdout

def count_issues(output):
    return {
        "Unused Imports": len(re.findall(r"unused-import", output)),
        "Unused Variables": len(re.findall(r"unused-variable", output)),
        "Undefined Variables": len(re.findall(r"undefined-variable", output)),
    }

def quality_score(issue_count):
    total = sum(issue_count.values())
    return max(0, 100 - total * 10)

def extract_imports(code):
    tree = ast.parse(code)
    imports = [node.names[0].name for node in tree.body if isinstance(node, ast.Import)]
    return imports

def plot_import_usage(imports):
    import_counts = {imp: imports.count(imp) for imp in set(imports)}
    colors = [f"rgb({random.randint(50,255)}, {random.randint(50,255)}, {random.randint(50,255)})" for _ in import_counts]
    fig = px.bar(x=list(import_counts.keys()), y=list(import_counts.values()),
                 labels={'x': 'Used Modules', 'y': 'Usage Counts'},
                 title="📊 Module Usage",
                 color=list(import_counts.keys()),
                 color_discrete_sequence=colors)
    fig.update_layout(bargap=0.3)
    st.plotly_chart(fig, use_container_width=True)

def download_button(code):
    b64 = base64.b64encode(code.encode()).decode()
    return f"""
    <div style="text-align: center; padding: 10px;">
        <a href="data:file/txt;base64,{b64}" download="refactored.py"
           style="background: linear-gradient(to right, #6a11cb, #2575fc); padding: 12px 20px; border-radius: 8px; color: white; text-align: center; font-weight: bold; font-size:18px; text-decoration: none;">
           📅 Download Refactored Code
        </a>
    </div>
    """

def optimize_code_suggestions(code):
    suggestions = []
    if "for i in range(len(list))" in code:
        suggestions.append("Use 'for item in list' instead of 'for i in range(len(list))'.")
    if "== None" in code:
        suggestions.append("Use 'is None' instead of '== None'.")
    if len(re.findall(r"print\(", code)) > 3:
        suggestions.append("Avoid excessive 'print'. Use logging or debugger.")
    if "for i in range(len(" in code:
        suggestions.append("Use 'enumerate()' for cleaner loops.")
    if "list1 + list2" in code:
        suggestions.append("Use 'list.extend()' or 'append()' instead of '+' in loops.")
    if "list.remove(" in code:
        suggestions.append("Use 'set()' to remove duplicates instead of 'list.remove()'.")
    if "global " in code:
        suggestions.append("Avoid 'global' variables. Use arguments or return values.")
    if len(re.findall(r"\b[a-z]{1,2}\b", code)) > 5:
        suggestions.append("Use descriptive variable names.")
    if "open(" in code and "close()" in code:
        suggestions.append("Use 'with open(...) as file:' for file handling.")
    if "if x == None:" in code:
        suggestions.append("Use default arguments instead of manual 'None' checks.")
    if "lambda " in code and len(re.findall(r"lambda", code)) > 3:
        suggestions.append("Avoid excessive lambdas. Use functions.")
    if "list(map(" in code:
        suggestions.append("Use list comprehensions instead of 'map()'.")
    return suggestions

# ---------- Action Button ----------
if st.button("⚙️ Refactor Now"):
    if not code_input.strip():
        st.warning("Please paste some code to analyze.")
    else:
        cleaned_code, analysis = refactor_code(code_input)
        issues = count_issues(analysis)
        score = quality_score(issues)
        used_imports = extract_imports(code_input)

        with tabs[1]:
            st.markdown("#### Cleaned and Refactored Code")
            st.code(cleaned_code, language="python")
            st.markdown(download_button(cleaned_code), unsafe_allow_html=True)

        with tabs[2]:
            st.markdown(f"<div class='score-box'>📊 Code Quality Score: {score}</div>", unsafe_allow_html=True)
            st.progress(score)
            st.json(issues)

        with tabs[3]:
            if used_imports:
                plot_import_usage(used_imports)
            else:
                st.info("No modules found in the code.")

        with tabs[4]:
            suggestions = optimize_code_suggestions(code_input)
            if suggestions:
                st.markdown("#### 💡 Code Optimization Suggestions")
                for suggestion in suggestions:
                    st.markdown(f"- {suggestion}")
            else:
                st.info("No optimization suggestions available.")

# ---------- Footer ----------
st.markdown("""
    <div class='footer'>
        RefactorPro &copy; 2025 &mdash; Built with ❤️ by Pashmeen Zia<br>
        <div class='social-icons'>
            <a href="https://github.com/PashmeenZia"><img src="https://cdn-icons-png.flaticon.com/512/25/25231.png"></a>
            <a href="https://www.linkedin.com/in/pashmeen-zia-31884b2b5/"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png"></a>
        </div>
    </div>
""", unsafe_allow_html=True)
