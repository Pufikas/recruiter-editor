import streamlit as st
from st_supabase_connection import SupabaseConnection

FOUNDER_NAME = "Naimul"

st.set_page_config(page_title="recruiter editor", layout="wide")

conn = st.connection("supabase", type=SupabaseConnection)

st.title("recruiter tree editor")

# ----------------------------
# load members (fresh every run)
# ----------------------------
resp = conn.table("members").select(
    "id,name,recruited_by,pfp_url"
).order("name").execute()

rows = resp.data

id_by_name = {r["name"]: r["id"] for r in rows}
id_to_name = {r["id"]: r["name"] for r in rows}

# ----------------------------
# tabs
# ----------------------------
tab_assign, tab_manage = st.tabs([
    "assign recruiters",
    "add / edit members"
])

# =========================================================
# TAB 1 — ASSIGN RECRUITERS
# =========================================================
with tab_assign:
    st.subheader("assign recruiters")

    # exclude founder from assignment flow
    assignable = [r for r in rows if r["name"] != FOUNDER_NAME]
    unassigned = [r for r in assignable if r["recruited_by"] is None]

    assigned_count = len(assignable) - len(unassigned)
    total = len(assignable)

    st.progress(assigned_count / total if total else 1)
    st.caption(f"{assigned_count} / {total} recruiters assigned")

    if not unassigned:
        st.success("all members have recruiters assigned 🎉")
    else:
        current = unassigned[0]
        mid = current["id"]
        name = current["name"]

        st.markdown(f"### who recruited **{name}**?")

        choices = [FOUNDER_NAME] + [
            r["name"] for r in rows if r["name"] != name
        ]

        selected = st.selectbox(
            "start typing a name:",
            choices,
            key="recruiter_select"
        )

        if st.button("save & next"):
            parent_id = id_by_name[selected]

            # concurrency-safe update
            res = conn.table("members").update(
                {"recruited_by": parent_id}
            ).eq("id", mid).is_("recruited_by", None).execute()

            if res.count == 0:
                st.warning("someone else already assigned this member")
            else:
                st.session_state.pop("recruiter_select", None)

            st.rerun()

    # -------- read-only table --------
    st.divider()
    st.subheader("full members table (read-only)")

    table = []
    for r in rows:
        table.append({
            "name": r["name"],
            "recruited_by": (
                id_to_name.get(r["recruited_by"], f"{FOUNDER_NAME} (Founder)")
            )
        })

    st.dataframe(table, use_container_width=True, hide_index=True)

# =========================================================
# TAB 2 — ADD / EDIT MEMBERS
# =========================================================
with tab_manage:
    st.subheader("add new member")

    name = st.text_input("member name")

    recruiter_mode = st.radio(
        "recruiter selection",
        ["select existing", "recruiter not listed"],
        horizontal=True
    )

    recruiter_id = None

    if recruiter_mode == "select existing":
        recruiter = st.selectbox(
            "recruited by",
            [FOUNDER_NAME] + [r["name"] for r in rows]
        )
        recruiter_id = id_by_name[recruiter]

    else:
        new_recruiter_name = st.text_input("new recruiter name")

    if st.button("add member"):
        if not name.strip():
            st.error("name cannot be empty")
            st.stop()

        # create recruiter first if needed
        if recruiter_mode == "recruiter not listed":
            if not new_recruiter_name.strip():
                st.error("recruiter name cannot be empty")
                st.stop()

            res = conn.table("members").insert({
                "name": new_recruiter_name,
                "recruited_by": None
            }).execute()

            recruiter_id = res.data[0]["id"]

        conn.table("members").insert({
            "name": name,
            "recruited_by": recruiter_id
        }).execute()

        st.success(f"added {name}")
        st.rerun()
