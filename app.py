import streamlit as st
import psycopg
import json

import streamlit as st
import psycopg

st.write("postgres secrets:", st.secrets["postgres"])

dsn = (
    f"postgresql://"
    f"{st.secrets['postgres']['user']}:"
    f"{st.secrets['postgres']['password']}@"
    f"{st.secrets['postgres']['host']}:"
    f"{st.secrets['postgres']['port']}/"
    f"{st.secrets['postgres']['database']}?"
    f"sslmode=require"
)

conn = psycopg.connect(dsn)


cur.execute("SELECT id, name FROM members ORDER BY name")
rows = cur.fetchall()

id_by_name = {name: mid for mid, name in rows}
names = [name for _, name in rows]
names_with_none = ["None (Founder)"] + names

st.title("recruiter tree editor (postgres)")


for mid, name in rows:
    cur.execute("SELECT recruited_by FROM members WHERE id = %s", (mid,))
    current_parent = cur.fetchone()[0]

    default = "None (Founder)"
    if current_parent:
        cur.execute("SELECT name FROM members WHERE id = %s", (current_parent,))
        default = cur.fetchone()[0]

    selected = st.selectbox(
        f"who recruited **{name}**?",
        names_with_none,
        index=names_with_none.index(default),
        key=name
    )

    parent_id = None if selected.startswith("None") else id_by_name[selected]

    cur.execute(
        "UPDATE members SET recruited_by = %s WHERE id = %s",
        (parent_id, mid)
    )
    conn.commit()

if st.button("export json"):
    cur.execute("SELECT id, name, recruited_by FROM members")
    data = cur.fetchall()

    nodes = {i: {"name": n, "children": []} for i, n, _ in data}
    root_nodes = []

    for i, n, parent in data:
        if parent:
            nodes[parent]["children"].append(nodes[i])
        else:
            root_nodes.append(nodes[i])

    st.code(json.dumps(root_nodes, indent=4), language="json")
