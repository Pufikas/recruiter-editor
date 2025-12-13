import streamlit as st
from st_supabase_connection import SupabaseConnection
from contextlib import contextmanager

FOUNDER_NAME = "Naimul"

st.set_page_config(
    page_title="recruiter editor",
    layout="wide",
)

# ---------- styling ----------
st.markdown("""
<style>
.panel {
    background:#0e1117;
    border:1px solid #30363d;
    border-radius:12px;
    padding:16px;
    margin-bottom:20px;
}
.muted {
    opacity:0.6;
    font-size:0.9rem;
}
</style>
""", unsafe_allow_html=True)

@contextmanager
def panel(title=None):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if title:
        st.markdown(f"### {title}")
    yield
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- db ----------
conn = st.connection("supabase", type=SupabaseConnection)

# always fresh (important for multi-user)
resp = (
    conn.table("members")
    .select("id,name,recruited_by")
    .order("name")
    .execute()
)

rows = resp.data or []

if not rows:
    st.warning("no members in database")
    st.stop()

id_by_name = {r["name"]: r["id"] for r in rows}
id_to_name = {r["id"]: r["name"] for r in rows}

# ---------- header ----------
st.markdown("""
<h1 style="margin-bottom:0;">recruiter tree editor</h1>
""", unsafe_allow_html=True)


tab_assign, tab_edit, tab_add = st.tabs(
    ["assign recruiters", "edit members", "add member"]
)

# =====================================================
# ASSIGN RECRUITERS (editor flow)
# =====================================================
with tab_assign:
    with panel("assignment"):
        assignable = [
            r for r in rows
            if r["name"] != FOUNDER_NAME
        ]

        unassigned = [
            r for r in assignable
            if r["recruited_by"] is None
        ]

        assigned = len(assignable) - len(unassigned)
        total = len(assignable)

        st.progress(assigned / total if total else 1)
        st.caption(f"{assigned} / {total} assigned")

        if not unassigned:
            st.success("all members assigned 🎉")
        else:
            current = unassigned[0]
            mid = current["id"]
            name = current["name"]

            st.markdown(f"""
            <h2>
                who recruited <span style="color:#7c7cff">{name}</span>?
            </h2>
            <p class="muted">start typing to search</p>
            """, unsafe_allow_html=True)

            choices = [FOUNDER_NAME] + [
                r["name"] for r in rows
                if r["name"] != name
            ]

            selected = st.selectbox(
                "recruiter",
                choices,
                label_visibility="collapsed",
                key="assign_select",
            )

            if st.button("save & next", use_container_width=True):
                parent_id = id_by_name[selected]

                # concurrency-safe update
                res = (
                    conn.table("members")
                    .update({"recruited_by": parent_id})
                    .eq("id", mid)
                    .is_("recruited_by", None)
                    .execute()
                )

                if res.count == 0:
                    st.warning("already assigned by someone else")
                else:
                    st.session_state.pop("assign_select", None)

                st.rerun()

    with panel("members (read-only)"):
        table = []
        for r in rows:
            table.append({
                "name": r["name"],
                "recruited_by": id_to_name.get(
                    r["recruited_by"], "founder"
                )
            })

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
            height=350
        )

# =====================================================
# EDIT MEMBERS
# =====================================================
with tab_edit:
    with panel("edit member"):
        member_name = st.selectbox(
            "member",
            [r["name"] for r in rows],
        )

        member = next(
            r for r in rows if r["name"] == member_name
        )

        new_name = st.text_input(
            "rename",
            value=member["name"]
        )

        recruiter_choices = [FOUNDER_NAME] + [
            r["name"] for r in rows
            if r["name"] != member["name"]
        ]

        current_recruiter = (
            id_to_name.get(member["recruited_by"], FOUNDER_NAME)
        )

        new_recruiter = st.selectbox(
            "recruited by",
            recruiter_choices,
            index=recruiter_choices.index(current_recruiter)
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("save changes", use_container_width=True):
                conn.table("members").update({
                    "name": new_name.strip(),
                    "recruited_by": id_by_name[new_recruiter]
                }).eq("id", member["id"]).execute()

                st.success("updated")
                st.rerun()

        with col2:
            if st.button("delete member", use_container_width=True):
                conn.table("members").delete().eq(
                    "id", member["id"]
                ).execute()

                st.warning("deleted")
                st.rerun()

# =====================================================
# ADD MEMBER
# =====================================================
with tab_add:
    with panel("add member"):
        new_name = st.text_input("member name")

        recruiter = st.selectbox(
            "recruited by",
            [FOUNDER_NAME] + [r["name"] for r in rows]
        )

        if st.button("add member", use_container_width=True):
            if not new_name.strip():
                st.error("name required")
                st.stop()

            conn.table("members").insert({
                "name": new_name.strip(),
                "recruited_by": id_by_name[recruiter]
            }).execute()

            st.success(f"added {new_name}")
            st.rerun()
