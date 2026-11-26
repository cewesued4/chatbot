import io, json, contextlib, traceback
import streamlit as st
from openai import OpenAI
from streamlit_ace import st_ace

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MODEL = "gpt-4o"   # use any tool-calling model you have access to
SYSTEM = (
    "You are a coding assistant with a shared Python editor. Use write_editor to put "
    "code in the editor, run_editor to execute it, and read_editor to see what the user "
    "has typed. If a run fails, fix the code and run again. Keep replies short."
)

ss = st.session_state
ss.setdefault("code", "")
ss.setdefault("ns", {})
ss.setdefault("ver", 0)
ss.setdefault("output", "")
ss.setdefault("api_msgs", [{"role": "system", "content": SYSTEM}])
ss.setdefault("chat", [])

# ---------- execution ----------
def run_code(code: str) -> str:
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            exec(code, ss.ns)
        out = buf.getvalue() or "(no output)"
    except Exception:
        out = buf.getvalue() + traceback.format_exc()
    return out[-4000:]

# ---------- tools ----------
TOOLS = [
    {"type": "function", "function": {
        "name": "read_editor",
        "description": "Return the current editor contents.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "write_editor",
        "description": "Replace the editor contents with new code.",
        "parameters": {
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"],
        },
    }},
    {"type": "function", "function": {
        "name": "run_editor",
        "description": "Run the editor contents and return stdout/stderr or the traceback.",
        "parameters": {"type": "object", "properties": {}},
    }},
]

def handle_tool(name, args):
    if name == "read_editor":
        return ss.code or "(editor is empty)"
    if name == "write_editor":
        ss.code = args["code"]
        ss.ver += 1
        return "Editor updated."
    if name == "run_editor":
        ss.output = run_code(ss.code)
        return ss.output
    return "Unknown tool."

# ---------- agent loop ----------
def agent_turn(user_text: str) -> str:
    ss.api_msgs.append({"role": "user",