
#import streamlit as st
#from streamlit_ace import st_ace
#import io, contextlib, traceback

st.title("Mini Python Playground")

#code = st_ace(
#    language="python",
#    theme="monokai",
#    height=300,
#    value="print('hello')",
#    key="editor",
#)
#
#if st.button("Run"):
#    buf = io.StringIO()
#    try:
#        with contextlib.redirect_stdout(buf):
#            exec(code, {})   # fresh namespace each run
#        st.code(buf.getvalue() or "(no output)")
#    except Exception:
#        st.error(traceback.format_exc())
    
from turtle import st

from jupyter_client.manager import start_new_kernel

if "kernel" not in st.session_state:
    km, kc = start_new_kernel(kernel_name="python3")
    st.session_state.kernel = (km, kc)

km, kc = st.session_state.kernel
msg_id = kc.execute(code)
# then poll kc.get_iopub_msg() and render stream / display_data / error messages