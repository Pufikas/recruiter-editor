import streamlit as st
from st_supabase_connection import SupabaseConnection

FOUNDER_NAME = "Naimul"
ADD_MEMBER_OPTION = "➕ add new member"

st.set_page_config(
    page_title="recruiter editor",
    layout="wide"
)

conn = st.connection("supabase", type=SupabaseConnection)

st.title("recruiter tree editor")

# =========================================================
# load members
# =========================================================
resp = conn.table("members").select(
    "id,name,recruited_by,pfp_url"
).order("name").execute()

rows = resp.data

id_by_name = {r["name"]: r["id"] for r in rows}
id_to_name = {r["id"]: r["name"] for r in rows}
names = [r["name"] for r in rows]

# =========================================================
# tabs
# =========================================================
tab_assign, tab_manage = st.tabs([
    "assign recruiters",
    "manage members"
])

# =========================================================
# TAB 1 — ASSIGN RECRUITERS (guided flow)
# =========================================================
with tab_assign:
    st.subheader("assign recruiters")

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

        recruiter_choices = [FOUNDER_NAME] + [
            r["name"] for r in rows if r["name"] != name
        ]

        selected = st.selectbox(
            "start typing a name:",
            recruiter_choices,
            key="recruiter_assign"
        )

        if st.button("save & next"):
            parent_id = id_by_name[selected]

            res = conn.table("members").update(
                {"recruited_by": parent_id}
            ).eq("id", mid).is_("recruited_by", None).execute()

            if res.count == 0:
                st.warning("someone else already assigned this member")
            else:
                st.session_state.pop("recruiter_assign", None)

            st.rerun()

    # -------------------------
    # read-only table
    # -------------------------
    st.divider()
    st.subheader("full members table (read-only)")

    table_rows = []
    for r in rows:
        table_rows.append({
            "name": r["name"],
            "recruited_by": id_to_name.get(
                r["recruited_by"],
                f"{FOUNDER_NAME} (Founder)"
            )
        })

    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# TAB 2 — MANAGE MEMBERS
# =========================================================
with tab_manage:
    st.subheader("edit existing member")

    member_choices = names + [ADD_MEMBER_OPTION]

    selected_member = st.selectbox(
        "select member",
        member_choices
    )

    # -------------------------
    # EDIT MEMBER
    # -------------------------
    if selected_member != ADD_MEMBER_OPTION:
        member_id = id_by_name[selected_member]
        current_parent = next(
            r["recruited_by"] for r in rows if r["id"] == member_id
        )

        recruiter_choices = [FOUNDER_NAME] + [
            n for n in names if n != selected_member
        ]

        default_recruiter = (
            FOUNDER_NAME
            if current_parent is None
            else id_to_name[current_parent]
        )

        recruiter = st.selectbox(
            "who recruited them?",
            recruiter_choices,
            index=recruiter_choices.index(default_recruiter)
        )

        if st.button("save changes"):
            parent_id = None if recruiter == FOUNDER_NAME else id_by_name[recruiter]

            conn.table("members").update(
                {"recruited_by": parent_id}
            ).eq("id", member_id).execute()

            st.success("member updated")
            st.rerun()

    else:
        st.info("select a member above or add a new one below")

    # =====================================================
    # ADD MEMBER (SEPARATE)
    # =====================================================
    st.divider()
    st.subheader("add new member")

    new_name = st.text_input("member name")

    recruiter_mode = st.radio(
        "recruiter selection",
        ["select existing", "recruiter not listed"],
        horizontal=True
    )

    recruiter_id = None

    if recruiter_mode == "select existing":
        recruiter = st.selectbox(
            "recruited by",
            [FOUNDER_NAME] + names
        )
        recruiter_id = None if recruiter == FOUNDER_NAME else id_by_name[recruiter]

    else:
        new_recruiter_name = st.text_input("new recruiter name")

    if st.button("add member"):
        if not new_name.strip():
            st.error("name cannot be empty")
            st.stop()

        if new_name in id_by_name:
            st.error("member already exists")
            st.stop()

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
            "name": new_name,
            "recruited_by": recruiter_id
        }).execute()

        st.success(f"added {new_name}")
        st.rerun()
