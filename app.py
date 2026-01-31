import streamlit as st
from st_supabase_connection import SupabaseConnection
from contextlib import contextmanager
import base64
import streamlit.components.v1 as components
import json

FOUNDER_NAME = "Naimul"

st.set_page_config(page_title="recruiter editor", layout="wide")

# ===============================
# background image
# ===============================
def load_bg(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = load_bg("assets/background.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background:
          linear-gradient(rgba(14,17,23,0.85), rgba(14,17,23,0.85)),
          url("data:image/jpg;base64,{bg}");
        background-size: cover;
        background-attachment: fixed;
    }}

    .panel {{
        background: rgba(14,17,23,0.92);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 24px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

@contextmanager
def panel(title=None):
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    if title:
        st.markdown(f"### {title}")
    yield
    st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# database
# ===============================
conn = st.connection("supabase", type=SupabaseConnection)

rows = (
    conn.table("members")
    .select("id,name,recruited_by")
    .order("name")
    .execute()
).data or []

if not rows:
    st.stop()

id_by_name = {r["name"]: r["id"] for r in rows}
row_by_id = {r["id"]: r for r in rows}

founder_id = id_by_name[FOUNDER_NAME]

# ===============================
# session state
# ===============================
if "assign_order" not in st.session_state:
    st.session_state.assign_order = [
        r["id"] for r in rows if r["id"] != founder_id
    ]

    start_idx = 0
    for i, mid in enumerate(st.session_state.assign_order):
        if row_by_id[mid]["recruited_by"] is None:
            start_idx = i
            break

    st.session_state.assign_idx = start_idx

if "assign_history" not in st.session_state:
    st.session_state.assign_history = []

if "manual_nav" not in st.session_state:
    st.session_state.manual_nav = False

# ===============================
# header
# ===============================
st.markdown("<h1>recruiter tree editor</h1>", unsafe_allow_html=True)

tab_assign, tab_edit, tab_add = st.tabs(
    ["assign recruiters", "edit members", "add member"]
)

# =====================================================
# ASSIGN RECRUITERS
# =====================================================
with tab_assign:
    with panel("assignment"):
        order = st.session_state.assign_order
        idx = st.session_state.assign_idx

        # auto-skip ONLY if not manually navigating
        if not st.session_state.manual_nav:
            while idx < len(order) and row_by_id[order[idx]]["recruited_by"] is not None:
                idx += 1
            st.session_state.assign_idx = idx

        st.session_state.manual_nav = False

        if idx >= len(order):
            st.success("all members assigned")
            st.stop()

        current = row_by_id[order[idx]]
        name = current["name"]

        assigned = sum(
            1 for r in rows
            if r["id"] != founder_id and r["recruited_by"] is not None
        )

        st.progress(assigned / len(order))
        st.caption(f"{assigned} / {len(order)} assigned")

        st.markdown(
            f"<h2>who recruited <span style='color:#7c7cff'>{name}</span>?</h2>",
            unsafe_allow_html=True,
        )

        # ===============================
        # copy button (styled like streamlit)
        components.html(
            f"""
            <button
                onclick='navigator.clipboard.writeText({json.dumps(name)})'
                style="
                    background: rgba(124,124,255,0.15);
                    color: #e6e8ff;
                    border: 1px solid rgba(124,124,255,0.4);
                    border-radius: 14px;
                    padding: 6px 16px;
                    font-size: 0.8rem;
                    font-weight: 500;
                    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
                                'Liberation Mono', 'Courier New', monospace;
                    cursor: pointer;
                    backdrop-filter: blur(6px);
                    transition: all 0.15s ease;
                "
                onmouseover="
                    this.style.background='rgba(124,124,255,0.25)';
                    this.style.transform='translateY(-1px)';
                "
                onmouseout="
                    this.style.background='rgba(124,124,255,0.15)';
                    this.style.transform='translateY(0)';
                "
            >
                copy name
            </button>
            """,
            height=44,
        )

        choices = [r["name"] for r in rows if r["name"] != name]

        selected = st.selectbox(
            "recruiter",
            choices,
            label_visibility="collapsed",
            key=f"assign_{current['id']}",
        )

        col_save, col_skip = st.columns([1, 1])

        with col_save:
            if st.button("save & next", use_container_width=True):
                conn.table("members").update(
                    {
                        "recruited_by": id_by_name[selected],
                        "updated_at": "now()",
                    }
                ).eq("id", current["id"]).execute()

                st.session_state.assign_history.append(
                    st.session_state.assign_idx
                )
                st.session_state.assign_idx += 1
                st.session_state.manual_nav = True
                st.rerun()

        with col_skip:
            if st.button("skip", use_container_width=True):
                st.session_state.assign_history.append(
                    st.session_state.assign_idx
                )
                st.session_state.assign_idx += 1
                st.session_state.manual_nav = True
                st.rerun()


    with panel("members (read-only)"):
        st.dataframe(
            [
                {
                    "name": r["name"],
                    "recruited_by": (
                        "unassigned"
                        if r["recruited_by"] is None
                        else row_by_id[r["recruited_by"]]["name"]
                    ),
                }
                for r in rows
            ],
            use_container_width=True,
            hide_index=True,
            height=350,
        )

# =====================================================
# EDIT MEMBERS
# =====================================================
with tab_edit:
    with panel("edit member"):
        member_name = st.selectbox("member", [r["name"] for r in rows])
        member = next(r for r in rows if r["name"] == member_name)

        new_name = st.text_input("rename", value=member["name"])

        recruiter = st.selectbox(
            "recruited by",
            [r["name"] for r in rows if r["name"] != member["name"]],
        )

        if st.button("save changes", use_container_width=True):
            conn.table("members").update(
                {
                    "name": new_name.strip(),
                    "recruited_by": id_by_name[recruiter],
                    "updated_at": "now()",
                }
            ).eq("id", member["id"]).execute()
            st.rerun()

# =====================================================
# ADD MEMBER
# =====================================================
with tab_add:
    with panel("add member"):
        new_name = st.text_input("member name")

        recruiter = st.selectbox(
            "recruited by",
            [r["name"] for r in rows],
        )

        if st.button("add member", use_container_width=True):
            conn.table("members").insert(
                {
                    "name": new_name.strip(),
                    "recruited_by": id_by_name[recruiter],
                }
            ).execute()
            st.rerun()
