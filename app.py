import streamlit as st
import json
from st_supabase_connection import SupabaseConnection

FOUNDER_NAME = "Naimul"

conn = st.connection("supabase", type=SupabaseConnection)

st.title("recruiter tree editor")

# always fetch fresh data
resp = conn.table("members").select(
    "id,name,recruited_by"
).order("name").execute()

rows = resp.data

# build lookup
id_by_name = {r["name"]: r["id"] for r in rows}

# force founder rule (one-time safety)
founder = next(r for r in rows if r["name"] == FOUNDER_NAME)
if founder["recruited_by"] is not None:
    conn.table("members").update(
        {"recruited_by": None}
    ).eq("id", founder["id"]).execute()

# exclude founder from assignment flow
assignable = [r for r in rows if r["name"] != FOUNDER_NAME]

unassigned = [r for r in assignable if r["recruited_by"] is None]
assigned_count = len(assignable) - len(unassigned)
total = len(assignable)

# progress
st.progress(assigned_count / total if total else 1)
st.caption(f"{assigned_count} / {total} recruiters assigned")



if not unassigned:
    st.success("all members have recruiters assigned 🎉")
    st.stop()

# current target
current = unassigned[0]
mid = current["id"]
name = current["name"]

# dropdown choices (founder allowed only as recruiter)
choices = [FOUNDER_NAME] + [
    r["name"] for r in rows if r["name"] != name
]

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
        parent_id = id_by_name[selected]

        conn.table("members").update(
            {"recruited_by": parent_id}
        ).eq("id", mid).execute()

        st.session_state.pop("recruiter_select", None)
        st.rerun()

with col2:
    st.caption("tip: type a few letters to search")


st.divider()
st.subheader("full members table (read-only)")

resp = conn.table("members").select(
    "id,name,recruited_by"
).order("name").execute()

data = resp.data

# map id → name
id_to_name = {r["id"]: r["name"] for r in data}

table_rows = []
for r in data:
    table_rows.append({
        "name": r["name"],
        "recruited_by": (
            id_to_name[r["recruited_by"]]
            if r["recruited_by"] is not None
            else "Naimul (Founder)"
        )
    })

st.dataframe(
    table_rows,
    use_container_width=True,
    hide_index=True
)
