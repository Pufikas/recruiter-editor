import streamlit as st
import json
from st_supabase_connection import SupabaseConnection

conn = st.connection("supabase", type=SupabaseConnection)

st.title("recruiter tree editor")

# load members
resp = conn.table("members").select("id,name,recruited_by").order("name").execute()
rows = resp.data

# split assigned / unassigned
unassigned = [r for r in rows if r["recruited_by"] is None]
assigned_count = len(rows) - len(unassigned)
total = len(rows)

# progress bar
st.progress(assigned_count / total)
st.caption(f"{assigned_count} / {total} recruiters assigned")

if not unassigned:
    st.success("all members have recruiters assigned 🎉")
    st.stop()

# build lookup tables
id_by_name = {r["name"]: r["id"] for r in rows}
names = [r["name"] for r in rows]
choices = ["None (Founder)"] + names

# current target (always first unassigned)
current = unassigned[0]
mid = current["id"]
name = current["name"]

st.markdown(f"## who recruited **{name}**?")

selected = st.selectbox(
    "start typing a name:",
    choices,
    index=0,
    key="recruiter_select"
)

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("save & next"):
        parent_id = None if selected.startswith("None") else id_by_name[selected]

        conn.table("members").update(
            {"recruited_by": parent_id}
        ).eq("id", mid).execute()

        # clear selection and move on
        st.session_state.pop("recruiter_select", None)
        st.rerun()

with col2:
    st.caption("tip: type a few letters to search")
