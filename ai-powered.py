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
@st.cache_data
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()  
animation = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_j1adxtyb.json")

st.markdown("""
            <style>
            .big-title {text-align: center; font-size: 3em; color:#2575fc; font-weight: bold;}
            .subtitle {text-align: center; font-size: 20px; color: #444; font-style: italic;}
            .feature-box {background: linear-gradient(to right, #6a11cb, #2575fc); padding: 15px; border-radius: 8px; color: white; text-align: center; margin-bottom: 20px;}
            .doc-box {background : linear-gradient(to right, #6a11cb, #2575fc); padding: 15px; border-radius: 8px; color: white; text-align: center;}
            .score-box {background : linear-gradient(to right, #6a11cb, #2575fc); padding: 10px; border-radius: 8px; color: white; text-align: center; font-size: 24px; font-weight: bold;}
            .footer {text-align: center; font-size: 14px; color: #aaa; marging-top: 40px;}
            .social-icons img {width: 25px; margin: 0 5px; vertical-align: middle}
            </style>
        """, unsafe_allow_html= True)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("<div class='big-title'> AI_Powered Python Code Formatter & Optimizer 🚀</div>",unsafe_allow_html= True)
    st.markdown("<div class='subtitle'>Empower your Python code with AI-driven formatting, optimization, and analysis</div>",unsafe_allow_html= True)

with col2:
    if animation:
        st_lottie(animation, height=200, speed=1, loop=True)  
    else:
        st.warning(" ⚠️ Failed to load animation")

with st.sidebar:
    st.markdown("<div class='feature-box'><h2> 🔧 Features </h2><p> Refactor, analyze data, optimized your given code. </p></div>",
                unsafe_allow_html= True)
    st.markdown("<div class='doc-box'><h3> 📘 Documentation </h3><p> Get started with AI-driven optimization. </p></div>",
                unsafe_allow_html= True)
    if st.button("🗑️ Clear Code", help="Reset your code input"):
        st.session_state.code_input = ""

if "code_input" not in st.session_state:
    st.session_state.code_input = ""

tabs = st.tabs(["📝 Code Input", "⚙️ Refactored Output", "🎯 Scorecard", "📊 Module Graph", "✨ Code Optimization Suggestions"])

with tabs[0]:
    code_input = st.text_area("Paste your Python code here:", value=st.session_state.code_input, height=300, key="input_code")

def refactor_code(code):
    sorted_code = isort.code(code)  
    formatted_code = black.format_file_contents(sorted_code, fast=False, mode=black.Mode()) 
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp_file: 
        tmp_file.write(formatted_code) 
        tmp_path = tmp_file.name  
    result = subprocess.run(["flake8", tmp_path], capture_output=True, text=True)  
    return formatted_code, result.stdout 

def count_issues(output):
    return{
        "Unused Imports": len(re.findall(r"unused-import", output)),
        "Unused Variables": len(re.findall(r"unused-variable", output)),
        "Undefined Variables": len(re.findall(r"undefined-variable", output)),
    }

def quality_score(issue_count):
    total = sum(issue_count.values())
    return max(0, 100 - total*10)
    
def extract_imports(code):
    tree = ast.parse(code)  
    imports = [node.names[0].name for node in tree.body if isinstance(node, ast.Import)]  
    return imports 

# Module usage ko plot karna
def plot_import_usage(imports):
    import_counts = {imp: imports.count(imp) for imp in set(imports)}  
    colors = [f"rgb({random.randint(50,255)}, {random.randint(50,255)}, {random.randint(50,255)})" for _ in import_counts]  
    fig = px.bar(x=list(import_counts.keys()), y=list(import_counts.values()), 
                 labels={'x':'Used Modules', 'y':'Usage Counts'},
                 title="📊 Module Usage", color=list(import_counts.keys()),  
                 color_discrete_sequence=colors)  
    fig.update_layout(bargap=0.3) 
    st.plotly_chart(fig, use_container_width=True) 

def download_button(code):
    b64 = base64.b64encode(code.encode()).decode()
    return f"""
    <div class = "download-btn" style="text-align: center; padding: 10px;">
    <a href ="data:file/txt;base64,{b64}" download="refactored.py" "style="
    background: linear=gradient(to right, #6a11cb, #2575fc); padding: 12px 20px; border-radius: 8px; color: white; text-align: center; font-weight: bold; 
    font-size:18px text-decoration: none;> 📅 Download Refactored Code </a> </div> 
    """

def optimize_code_suggestions(code):
    suggestions = [] 

    # Specific code patterns ke liye suggestions dena
    if "for i in range(len(list))" in code:
        suggestions.append("Use 'for item in list' instead of 'for i in range(len(list))' for better readability.")
    if "== None" in code:
        suggestions.append("Use 'is None' instead of '== None' for better performance and readability.")
    if len(re.findall(r"print\(", code)) > 3:
        suggestions.append("Avoid excessive 'print' statements. Consider logging or using a debugger for better performance.")
    if "for i in range(len(" in code:
        suggestions.append("Consider using 'enumerate()' for cleaner loops, e.g., 'for i, item in enumerate(list):'")
    if "list1 + list2" in code:
        suggestions.append("Avoid concatenating lists inside loops, as it's inefficient. Use 'list.extend()' or 'append()'.")
    if "list.remove(" in code:
        suggestions.append("If you're removing duplicates, consider using 'set()' instead of repeatedly removing elements from a list.")
    if "global " in code:
        suggestions.append("Avoid using 'global' variables. It's better to pass variables as function arguments or return values.")
    if len(re.findall(r"\b[a-z]{1,2}\b", code)) > 5: 
        suggestions.append("Use descriptive variable names instead of single-letter variables (e.g., 'x', 'y').")
    if "open(" in code and "close()" in code:
        suggestions.append("Use 'with open(...) as file' to automatically handle file closing and exceptions.")
    if "if x == None:" in code:
        suggestions.append("Use default arguments instead of manual 'None' checks in function definitions, e.g., 'def func(x=None):'")
    if "lambda " in code and len(re.findall(r"lambda", code)) > 3:
        suggestions.append("Consider replacing redundant lambda functions with regular function definitions.")
    if "list(map(" in code:
        suggestions.append("Consider using list comprehensions instead of 'map()' for better readability and performance.")

    return suggestions 

if st.button(" ⚙️ Refactored Now"):
    if not code_input.strip():
        st.warning("Please paste some code to analyze.")
    else:
        cleaned_code, analysis = refactor_code(code_input)
        issues = count_issues(analysis)
        score = quality_score(issues)
        used_imports = extract_imports(code_input)

        with tabs[1]:
            st.markdown("#### Cleaned And Refactores Code")
            st.code(cleaned_code, language="python")
            st.markdown(download_button(cleaned_code), unsafe_allow_html=True)

        with tabs[2]:
            st.markdown(f"<div class = 'score-box'> 📊 Code Quality Score: {score}</div>")
            st.progress(score)
            st.json(issues)

        with tabs[3]:
            if used_imports:
                plot_import_usage(used_imports)
            else:
                st.info("No modules found in code.")

        with tabs[4]:
            suggestions = optimize_code_suggestions(code_input)
            if suggestions:
                st.markdown("#### 💡 Code Optimization Suggestions")
                for suggestion in suggestions:
                    st.markdown(f"- {suggestion}")
                else:
                    st.info("No optimization suggestions available.")            



# Footer with Social Icons
st.markdown("""
    <div class='footer'>
        RefactorPro &copy; 2025 &mdash; Built with ❤️ by Pashmeen Zia<br>
        <div class='social-icons'>
            <a href="https://github.com/PashmeenZia"><img src="https://cdn-icons-png.flaticon.com/512/25/25231.png"></a>
            <a href="https://www.linkedin.com/in/pashmeen-zia-31884b2b5/"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png"></a>
            
        </div>
    </div>
""", unsafe_allow_html=True)









