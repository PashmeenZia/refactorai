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

# Page settings
st.set_page_config(page_title="Refactor Pro Application", page_icon="🏷️", layout="wide")

# Load Lottie Animation
@st.cache_data
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()  # ✅ Fix: parentheses added

animation = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_j1adxtyb.json")

# Tabs for layout
tabs = st.tabs([
    "📝 Code Input",
    "⚙️ Refactored Output",
    "🎯 Scorecard",
    "📊 Module Graph",
    "✨ Code Optimization Suggestions"
])

# Input area
with tabs[0]:
    code_input = st.text_area("Paste your Python code here:", height=300)

# Refactor function
def refactor_code(code):
    sorted_code = isort.code(code)
    formatted_code = black.format_file_contents(sorted_code, fast=False, mode=black.Mode())
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp_file:
        tmp_file.write(formatted_code)
        tmp_path = tmp_file.name
    result = subprocess.run(["flake8", tmp_path], capture_output=True, text=True)
    return formatted_code, result.stdout

# Count issues from flake8
def count_issues(output):
    return {
        "Unused Imports": len(re.findall(r"unused-import", output)),
        "Unused Variables": len(re.findall(r"unused-variable", output)),
        "Undefined Variables": len(re.findall(r"undefined-variable", output)),
    }

# Score calculation
def quality_score(issue_count):
    total = sum(issue_count.values())
    return max(0, 100 - total * 10)

# Extract imports
def extract_imports(code):
    try:
        tree = ast.parse(code)
        imports = [node.names[0].name for node in tree.body if isinstance(node, ast.Import)]
        return imports
    except:
        return []

# Plot module usage
def plot_import_usage(imports):
    import_counts = {imp: imports.count(imp) for imp in set(imports)}
    colors = [f"rgb({random.randint(50,255)}, {random.randint(50,255)}, {random.randint(50,255)})" for _ in import_counts]
    fig = px.bar(
        x=list(import_counts.keys()), y=list(import_counts.values()),
        labels={'x': 'Used Modules', 'y': 'Usage Counts'},
        title="📊 Module Usage", color=list(import_counts.keys()),
        color_discrete_sequence=colors
    )
    fig.update_layout(bargap=0.3)
    st.plotly_chart(fig, use_container_width=True)

# Suggest optimization tips
def optimize_code_suggestions(code):
    suggestions = []
    if "for i in range(len(list))" in code:
        suggestions.append("Use 'for item in list' instead of 'for i in range(len(list))'.")
    if "== None" in code:
        suggestions.append("Use 'is None' instead of '== None'.")
    if len(re.findall(r"print\(", code)) > 3:
        suggestions.append("Avoid too many print statements. Use logging.")
    if "for i in range(len(" in code:
        suggestions.append("Use 'enumerate()' instead of range(len()).")
    if "list1 + list2" in code:
        suggestions.append("Avoid list concatenation in loops; use extend().")
    if "list.remove(" in code:
        suggestions.append("Use set() to remove duplicates instead of remove().")
    if "global " in code:
        suggestions.append("Avoid global variables; use function arguments.")
    if len(re.findall(r"\b[a-z]{1,2}\b", code)) > 5:
        suggestions.append("Use descriptive variable names.")
    if "open(" in code and "close()" in code:
        suggestions.append("Use 'with open() as file' to handle files safely.")
    if "if x == None:" in code:
        suggestions.append("Use default arguments instead of manual None check.")
    if "lambda " in code and len(re.findall(r"lambda", code)) > 3:
        suggestions.append("Use regular functions instead of many lambdas.")
    if "list(map(" in code:
        suggestions.append("Use list comprehensions instead of map().")
    return suggestions

# Button and execution
if st.button("⚙️ Refactor Now"):
    if not code_input.strip():
        st.warning("Please paste some code.")
    else:
        cleaned_code, analysis = refactor_code(code_input)
        issues = count_issues(analysis)
        score = quality_score(issues)
        used_imports = extract_imports(code_input)

        with tabs[1]:
            st.markdown("#### Cleaned And Refactored Code")
            st.code(cleaned_code, language="python")

        with tabs[2]:
            st.markdown(f"### 📊 Code Quality Score: {score}")
            st.progress(score)
            st.json(issues)

        with tabs[3]:
            if used_imports:
                plot_import_usage(used_imports)
            else:
                st.info("No modules found.")

        with tabs[4]:
            suggestions = optimize_code_suggestions(code_input)
            if suggestions:
                st.markdown("#### 💡 Code Optimization Suggestions")
                for s in suggestions:
                    st.markdown(f"- {s}")
            else:
                st.info("No suggestions found.")

# Footer
st.markdown("""
    <div class='footer' style='text-align: center; margin-top: 40px; color: grey;'>
        RefactorPro &copy; 2025 &mdash; Built with ❤️ by Pashmeen Zia<br>
        <div class='social-icons'>
            <a href="https://github.com/PashmeenZia"><img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="25"></a>
            <a href="https://www.linkedin.com/in/pashmeen-zia-31884b2b5/"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25"></a>
        </div>
    </div>
""", unsafe_allow_html=True)
