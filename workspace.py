import streamlit as st
from streamlit_ace import st_ace
import io, contextlib, traceback

st.title("Mini Python Playground")

code = st_ace(
    language="python",
    theme="monokai",
    height=300,
    value="print('hello')",
    key="editor",
)

if st.button("Run"):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {})   # fresh namespace each run
        st.code(buf.getvalue() or "(no output)")
    except Exception:
        st.error(traceback.format_exc())