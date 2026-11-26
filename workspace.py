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
    ss.api_msgs.append({"role": "user", "content": user_text})
    for _ in range(8):
        resp = client.chat.completions.create(
            model=MODEL, messages=ss.api_msgs, tools=TOOLS,
        )
        msg = resp.choices[0].message
        # store the assistant message (including any tool calls) in history
        ss.api_msgs.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content or ""

        for call in msg.tool_calls:
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = handle_tool(call.function.name, args)
            ss.api_msgs.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
    return "Stopped after reaching the step limit."

# ---------- UI ----------
left, right = st.columns(2)

with left:
    st.subheader("Editor")
    ss.code = st_ace(
        value=ss.code, language="python", theme="monokai", height=350,
        auto_update=True, key=f"ace_{ss.ver}",
    ) or ""
    if st.button("Run"):
        ss.output = run_code(ss.code)
    st.subheader("Output")
    st.code(ss.output or "(nothing run yet)")

with right:
    st.subheader("Assistant")
    for role, text in ss.chat:
        st.chat_message(role).write(text)
    if prompt := st.chat_input("Ask the assistant to write or fix code..."):
        ss.chat.append(("user", prompt))
        with st.spinner("Working..."):
            reply = agent_turn(prompt)
        ss.chat.append(("assistant", reply))
        st.rerun()