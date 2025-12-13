import streamlit as st
import json
from st_supabase_connection import SupabaseConnection

conn = st.connection("supabase", type=SupabaseConnection)

st.title("recruiter tree editor")

# load members
resp = conn.table("members").select("id,name,recruited_by").order("name").execute()
rows = resp.data

id_by_name = {r["name"]: r["id"] for r in rows}
name_by_id = {r["id"]: r["name"] for r in rows}

names = [r["name"] for r in rows]
choices = ["None (Founder)"] + names

if "changes" not in st.session_state:
    st.session_state.changes = {}

# ui
for r in rows:
    mid = r["id"]
    name = r["name"]
    parent = r["recruited_by"]

    default = "None (Founder)"
    if parent:
        default = name_by_id[parent]

    selected = st.selectbox(
        f"who recruited **{name}**?",
        choices,
        index=choices.index(default),
        key=f"select_{mid}",
    )

    if selected != default:
        st.session_state.changes[mid] = (
            None if selected.startswith("None") else id_by_name[selected]
        )

# save button
if st.button("save changes"):
    for mid, parent_id in st.session_state.changes.items():
        conn.table("members").update(
            {"recruited_by": parent_id}
        ).eq("id", mid).execute()

    st.session_state.changes.clear()
    st.success("saved!")

# export json
if st.button("export json"):
    resp = conn.table("members").select("id,name,recruited_by").execute()
    data = resp.data

    nodes = {r["id"]: {"name": r["name"], "children": []} for r in data}
    roots = []

    for r in data:
        if r["recruited_by"]:
            nodes[r["recruited_by"]]["children"].append(nodes[r["id"]])
        else:
            roots.append(nodes[r["id"]])

    st.code(json.dumps(roots, indent=2), language="json")
