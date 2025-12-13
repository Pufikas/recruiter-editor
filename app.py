import os
import streamlit as st
import psycopg
import json

# remove PG env vars (safe)
for k in list(os.environ.keys()):
    if k.startswith("PG"):
        del os.environ[k]

conn = psycopg.connect(
    host=st.secrets["postgres"]["host"],
    dbname=st.secrets["postgres"]["database"],
    user=st.secrets["postgres"]["user"],
    password=st.secrets["postgres"]["password"],
    port=st.secrets["postgres"]["port"],
    sslmode="require",
)

cur = conn.cursor()

st.title("recruiter tree editor")

# --- load data once ---
cur.execute("SELECT id, name, recruited_by FROM members ORDER BY name")
rows = cur.fetchall()

id_by_name = {name: mid for mid, name, _ in rows}
name_by_id = {mid: name for mid, name, _ in rows}

names = [name for _, name, _ in rows]
choices = ["None (Founder)"] + names

# --- local state ---
if "changes" not in st.session_state:
    st.session_state.changes = {}

# --- UI ---
for mid, name, recruited_by in rows:
    default = "None (Founder)"
    if recruited_by:
        default = name_by_id[recruited_by]

    selected = st.selectbox(
        f"who recruited **{name}**?",
        choices,
        index=choices.index(default),
        key=f"select_{mid}"
    )

    if selected != default:
        st.session_state.changes[mid] = (
            None if selected.startswith("None") else id_by_name[selected]
        )

# --- save button ---
if st.button("save changes"):
    for mid, parent_id in st.session_state.changes.items():
        cur.execute(
            "UPDATE members SET recruited_by = %s WHERE id = %s",
            (parent_id, mid)
        )
    conn.commit()
    st.session_state.changes.clear()
    st.success("saved!")

# --- export ---
if st.button("export json"):
    cur.execute("SELECT id, name, recruited_by FROM members")
    data = cur.fetchall()

    nodes = {i: {"name": n, "children": []} for i, n, _ in data}
    roots = []

    for i, n, parent in data:
        if parent:
            nodes[parent]["children"].append(nodes[i])
        else:
            roots.append(nodes[i])

    st.code(json.dumps(roots, indent=4), language="json")
