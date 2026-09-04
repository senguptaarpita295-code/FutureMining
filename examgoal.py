import time
import pandas as pd
import streamlit as st
import api_client

OPTION_LETTERS = ("A", "B", "C", "D")

# ============================================================
# EXAMGOAL PRACTICE MODE
# ============================================================
def render_practice_mode(question_frame: pd.DataFrame):
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 1.25rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #334155;">
            <h2 style="color: #38bdf8; margin: 0 0 0.5rem 0; font-size: 1.5rem;">📚 ExamGoal Practice Portal</h2>
            <p style="color: #94a3b8; margin: 0; font-size: 0.95rem;">
                Topic-wise GATE Mining questions with instant answer verification, explanations, and database review reporting.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Filter row
    f_col1, f_col2, f_col3 = st.columns([2, 1.2, 1.5])

    all_topics = ["All Topics"] + sorted([str(t) for t in question_frame["topic"].unique() if str(t).strip()])
    with f_col1:
        selected_topic = st.selectbox("📌 Select Subject / Topic", all_topics, index=0)

    with f_col2:
        diff_options = ["All Difficulties"] + [f"Level {i}" for i in range(1, 16)]
        selected_diff = st.selectbox("⚡ Difficulty Tier", diff_options, index=0)

    with f_col3:
        search_kw = st.text_input("🔍 Search Keyword", placeholder="e.g. eigenvalue, ventilation...")

    # Filter dataframe
    filtered = question_frame.copy()
    if selected_topic != "All Topics":
        filtered = filtered[filtered["topic"] == selected_topic]
    if selected_diff != "All Difficulties":
        level_num = int(selected_diff.split()[1])
        filtered = filtered[filtered["difficulty"] == level_num]
    if search_kw.strip():
        kw = search_kw.strip().lower()
        filtered = filtered[filtered["question"].astype(str).str.lower().str.contains(kw)]

    total_count = len(filtered)
    st.markdown(f"<p style='color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;'>Showing <strong>{min(total_count, 20)}</strong> of <strong>{total_count}</strong> matching questions</p>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No questions matched your filters. Try selecting 'All Topics' or clearing the search.")
        return

    # Pagination or display top 20
    display_rows = filtered.head(20)

    for idx, row in display_rows.iterrows():
        q_id = int(row.get("id", idx))
        correct_idx = int(row.get("correct", 0))

        with st.container(border=True):
            hdr_col, badge_col = st.columns([4, 1])
            with hdr_col:
                st.markdown(f"**Q{q_id}. {row.get('topic', 'General')}** &nbsp; <span style='color: #f59e0b; font-size: 0.85rem;'>[Level {row.get('difficulty', 1)}]</span>", unsafe_allow_html=True)
            with badge_col:
                if st.button("🚩 Flag", key=f"flag_prac_{q_id}", help="Report this question to database"):
                    if api_client.flag_question_server(q_id, "Flagged in practice mode"):
                        st.toast(f"Question #{q_id} flagged to Supabase review queue!", icon="✅")
                    else:
                        st.toast("Flag recorded locally.", icon="⚠️")

            st.markdown(f"<div style='font-size: 1.05rem; margin: 0.5rem 0 1rem 0; line-height: 1.5;'>{row['question']}</div>", unsafe_allow_html=True)

            opts = [str(row[f"option_{l.lower()}"]) for l in OPTION_LETTERS]

            user_choice = st.radio(
                "Choose your option:",
                options=list(range(4)),
                format_func=lambda i: f"{OPTION_LETTERS[i]}. {opts[i]}",
                key=f"prac_q_{q_id}",
                index=None
            )

            c_btn, c_res = st.columns([1.5, 3])
            with c_btn:
                check = st.button("Check Answer", key=f"check_btn_{q_id}")

            if check:
                with c_res:
                    if user_choice is None:
                        st.warning("Please select an option first.")
                    elif user_choice == correct_idx:
                        st.success(f"✅ Correct! Option {OPTION_LETTERS[correct_idx]} is the right answer.")
                    else:
                        st.error(f"❌ Incorrect. You selected {OPTION_LETTERS[user_choice]}, but the correct answer is {OPTION_LETTERS[correct_idx]}.")

            with st.expander("💡 View Solution & Correct Key"):
                st.markdown(f"**Correct Answer:** Option **{OPTION_LETTERS[correct_idx]}** ({opts[correct_idx]})")
                st.markdown(f"**Topic:** {row.get('topic', 'Mining Engineering')}")


# ============================================================
# EXAMGOAL GATE MOCK TEST MODE
# ============================================================
def render_mock_test_mode(question_frame: pd.DataFrame):
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 1.25rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #334155;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="color: #10b981; margin: 0 0 0.25rem 0; font-size: 1.5rem;">⏱️ ExamGoal GATE Mock Test</h2>
                    <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">
                        Official GATE pattern: +1.0 Mark for Correct, -0.33 Mark for Incorrect. Color-coded question palette.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Initialize Mock Test Session State
    if "mock_initialized" not in st.session_state or st.session_state.get("mock_reset", False):
        sample_pool = question_frame.sample(n=min(10, len(question_frame)), random_state=int(time.time()) % 10000)
        st.session_state.mock_questions = sample_pool.to_dict(orient="records")
        st.session_state.mock_answers = {}  # {q_idx: selected_opt}
        st.session_state.mock_marked_review = set()  # {q_idx}
        st.session_state.mock_current_idx = 0
        st.session_state.mock_submitted = False
        st.session_state.mock_start_time = time.time()
        st.session_state.mock_initialized = True
        st.session_state.mock_reset = False

    questions = st.session_state.mock_questions
    current_idx = st.session_state.mock_current_idx
    total_q = len(questions)

    # 1. SUMMARY VIEW AFTER SUBMISSION
    if st.session_state.mock_submitted:
        st.balloons()
        st.markdown("### 🏆 GATE Mock Test Performance Report")

        correct_count = 0
        incorrect_count = 0
        unattempted_count = 0

        for idx, q in enumerate(questions):
            ans = st.session_state.mock_answers.get(idx)
            corr = int(q.get("correct", 0))
            if ans is None:
                unattempted_count += 1
            elif ans == corr:
                correct_count += 1
            else:
                incorrect_count += 1

        total_score = round((correct_count * 1.0) - (incorrect_count * 0.33), 2)
        accuracy = round((correct_count / max(1, correct_count + incorrect_count)) * 100, 1)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Score", f"{total_score} / {total_q}", delta=f"{accuracy}% Accuracy")
        m2.metric("Correct Answers", f"{correct_count} (+{correct_count} marks)", delta_color="normal")
        m3.metric("Wrong Answers", f"{incorrect_count} (-{round(incorrect_count*0.33, 2)} marks)", delta_color="inverse")
        m4.metric("Unattempted", f"{unattempted_count}")

        if st.button("🔄 Take Another Mock Test", type="primary"):
            st.session_state.mock_reset = True
            st.rerun()

        st.divider()
        st.markdown("#### 📝 Question Review")
        for idx, q in enumerate(questions):
            user_ans = st.session_state.mock_answers.get(idx)
            corr = int(q.get("correct", 0))
            opts = [str(q[f"option_{l.lower()}"]) for l in OPTION_LETTERS]

            with st.expander(f"Question {idx+1}: {q['question'][:70]}... - {'✅ Correct' if user_ans == corr else ('❌ Incorrect' if user_ans is not None else '⚪ Unattempted')}"):
                st.markdown(f"**Question:** {q['question']}")
                for i in range(4):
                    prefix = f"{OPTION_LETTERS[i]}. {opts[i]}"
                    if i == corr:
                        st.markdown(f"<span style='color: #10b981; font-weight: bold;'>{prefix} (Correct Answer)</span>", unsafe_allow_html=True)
                    elif i == user_ans:
                        st.markdown(f"<span style='color: #ef4444;'>{prefix} (Your Choice)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #94a3b8;'>{prefix}</span>", unsafe_allow_html=True)
        return

    # 2. ACTIVE TEST INTERFACE
    cur_q = questions[current_idx]
    q_opts = [str(cur_q[f"option_{l.lower()}"]) for l in OPTION_LETTERS]

    q_col, pal_col = st.columns([3.2, 1.2], gap="large")

    with q_col:
        # Question Header
        t_col, m_col = st.columns([3, 1])
        with t_col:
            st.markdown(f"### Question {current_idx + 1} of {total_q}")
            st.caption(f"Topic: {cur_q.get('topic', 'Mining Engineering')} · Difficulty: Level {cur_q.get('difficulty', 1)}")
        with m_col:
            st.markdown("<div style='text-align: right; color: #10b981; font-weight: bold;'>+1.0 / -0.33</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown(f"<div style='font-size: 1.15rem; line-height: 1.6; margin-bottom: 1.5rem;'>{cur_q['question']}</div>", unsafe_allow_html=True)

        # Selected Option
        prev_ans = st.session_state.mock_answers.get(current_idx)
        selected_opt = st.radio(
            "Select Answer:",
            options=list(range(4)),
            format_func=lambda i: f"{OPTION_LETTERS[i]}. {q_opts[i]}",
            key=f"mock_opt_{current_idx}",
            index=prev_ans
        )

        st.divider()

        # Action Buttons
        b1, b2, b3, b4 = st.columns([1.5, 1.8, 1.2, 1.2])

        with b1:
            if st.button("💾 Save & Next", type="primary", use_container_width=True):
                if selected_opt is not None:
                    st.session_state.mock_answers[current_idx] = selected_opt
                st.session_state.mock_marked_review.discard(current_idx)
                if current_idx + 1 < total_q:
                    st.session_state.mock_current_idx += 1
                st.rerun()

        with b2:
            if st.button("🟣 Mark for Review", use_container_width=True):
                if selected_opt is not None:
                    st.session_state.mock_answers[current_idx] = selected_opt
                st.session_state.mock_marked_review.add(current_idx)
                if current_idx + 1 < total_q:
                    st.session_state.mock_current_idx += 1
                st.rerun()

        with b3:
            if st.button("🧹 Clear", use_container_width=True):
                st.session_state.mock_answers.pop(current_idx, None)
                st.session_state.mock_marked_review.discard(current_idx)
                st.rerun()

        with b4:
            if st.button("🚩 Flag", use_container_width=True, help="Report question to Supabase review queue"):
                api_client.flag_question_server(cur_q["id"], "Flagged during mock test")
                st.toast("Flagged to Supabase!", icon="🚩")

    # Question Palette (GATE Exam Style)
    with pal_col:
        with st.container(border=True):
            st.markdown("#### Question Palette")

            # Palette Legend
            st.markdown("""
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 0.8rem; margin-bottom: 0.75rem;">
                    <div>🟢 Answered</div>
                    <div>🟣 Review</div>
                    <div>⚪ Not Visited</div>
                    <div>🔴 Skipped</div>
                </div>
            """, unsafe_allow_html=True)

            # Palette Buttons Grid
            grid_cols = st.columns(5)
            for i in range(total_q):
                col_idx = i % 5
                is_ans = i in st.session_state.mock_answers
                is_rev = i in st.session_state.mock_marked_review
                is_cur = i == current_idx

                btn_label = f"{i+1}"
                if is_rev:
                    btn_label = f"🟣{i+1}"
                elif is_ans:
                    btn_label = f"🟢{i+1}"
                elif is_cur:
                    btn_label = f"▶{i+1}"

                with grid_cols[col_idx]:
                    if st.button(btn_label, key=f"pal_btn_{i}", use_container_width=True):
                        st.session_state.mock_current_idx = i
                        st.rerun()

            st.divider()

            # Submit Test Button
            if st.button("🏁 Submit Test", type="primary", use_container_width=True):
                st.session_state.mock_submitted = True
                st.rerun()
