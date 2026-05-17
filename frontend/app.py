import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="MSRA — Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ──────────────────────────────────────────────
for key, default in [
    ("paper_indexed", False),
    ("paper_info", {}),
    ("history", []),
    ("use_agent", True),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Global CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #F4F7FB !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid rgba(24,95,165,0.10) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown { color: #1A2D3D !important; }

/* ── BUTTONS ── */
div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.01em !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: #185FA5 !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(24,95,165,0.20) !important;
    padding: 10px 22px !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #0C447C !important;
    box-shadow: 0 4px 14px rgba(24,95,165,0.30) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: #F4F7FB !important;
    color: #185FA5 !important;
    border: 1px solid rgba(24,95,165,0.18) !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #EBF4FF !important;
    border-color: rgba(24,95,165,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── TEXT INPUT ── */
div[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    border: 1.5px solid rgba(24,95,165,0.18) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    color: #0F1C2E !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #185FA5 !important;
    box-shadow: 0 0 0 3px rgba(24,95,165,0.10) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #8AAAC9 !important; }
div[data-testid="stTextInput"] > label { display: none !important; }

/* ── TOGGLE ── */
div[data-testid="stToggle"] > label > span { color: #1A2D3D !important; font-size: 13px !important; }

/* ── EXPANDER ── */
div[data-testid="stExpander"] {
    border: 1px solid rgba(24,95,165,0.12) !important;
    border-radius: 10px !important;
    background: #FAFCFF !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] summary {
    font-size: 12px !important;
    color: #185FA5 !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
}

/* ── FILE UPLOADER ── */
div[data-testid="stFileUploader"] {
    border: 2px dashed rgba(24,95,165,0.22) !important;
    border-radius: 14px !important;
    background: #FAFCFF !important;
    padding: 24px !important;
}
div[data-testid="stFileUploader"] label { color: #185FA5 !important; font-weight: 500 !important; }

/* ── SPINNER ── */
div[data-testid="stSpinner"] { color: #185FA5 !important; }

/* ── ALERTS ── */
div[data-testid="stAlert"] { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="padding:20px 16px 16px;border-bottom:1px solid rgba(24,95,165,0.10);margin-bottom:4px;">
      <div style="display:flex;align-items:center;gap:11px;">
        <div style="width:36px;height:36px;background:#185FA5;border-radius:10px;
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          <span style="color:#fff;font-size:18px;">🔬</span>
        </div>
        <div>
          <div style="font-size:15px;font-weight:600;color:#0F1C2E;letter-spacing:-0.02em;">MSRA</div>
          <div style="font-size:11px;color:#8AAAC9;margin-top:1px;">Scientific Research Assistant</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.paper_indexed:
        st.markdown("""
        <div style="margin:16px;padding:12px 14px;background:#F4F7FB;border:1px solid rgba(24,95,165,0.12);
                    border-radius:10px;font-size:12px;color:#4A6480;">
          Upload a paper on the main page to begin.
        </div>
        """, unsafe_allow_html=True)
    else:
        info = st.session_state.paper_info
        title = info.get("title", "Untitled paper")

        # Paper card
        st.markdown(f"""
        <div style="margin:12px 12px 0;padding:11px 13px;background:#EBF4FF;
                    border:1px solid rgba(24,95,165,0.18);border-radius:10px;cursor:default;">
          <div style="font-size:12px;font-weight:600;color:#0C447C;line-height:1.45;margin-bottom:4px;">
            {title[:60]}{"…" if len(title)>60 else ""}
          </div>
          <div style="font-size:11px;color:#5B8DB8;display:flex;align-items:center;gap:4px;">
            📄 &nbsp;Indexed
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Stats grid
        pages = info.get("pages", 0)
        chunks = info.get("text_chunks", 0)
        figures = info.get("figures_captioned", 0)
        total = info.get("total_indexed", 0)

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:10px 12px 4px;">
          {"".join(
            f'<div style="background:#F4F7FB;border:1px solid rgba(24,95,165,0.10);border-radius:9px;'
            f'padding:10px;text-align:center;">'
            f'<div style="font-size:20px;font-weight:600;color:#185FA5;letter-spacing:-0.03em;">{v}</div>'
            f'<div style="font-size:10px;color:#8AAAC9;margin-top:2px;font-weight:500;">{l}</div>'
            f'</div>'
            for v, l in [(pages,"Pages"),(chunks,"Chunks"),(figures,"Figures"),(total,"Indexed")]
          )}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr style="border:none;border-top:1px solid rgba(24,95,165,0.10);margin:10px 12px;">', unsafe_allow_html=True)

        # Settings
        st.markdown('<div style="padding:0 12px;font-size:10px;font-weight:600;letter-spacing:0.09em;'
                    'text-transform:uppercase;color:#8AAAC9;margin-bottom:8px;">Settings</div>', unsafe_allow_html=True)

        st.session_state.use_agent = st.toggle(
            "Agent mode (sub-question decomposition)",
            value=st.session_state.use_agent,
        )
        st.markdown('<div style="padding:0 2px;font-size:11px;color:#8AAAC9;line-height:1.5;margin-top:-4px;margin-bottom:10px;">'
                    'Agent decomposes complex questions for deeper answers. Slower but more thorough.'
                    '</div>', unsafe_allow_html=True)

        st.markdown('<hr style="border:none;border-top:1px solid rgba(24,95,165,0.10);margin:4px 12px 10px;">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear history", type="secondary", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        with col2:
            if st.button("New paper", type="secondary", use_container_width=True):
                st.session_state.paper_indexed = False
                st.session_state.paper_info = {}
                st.session_state.history = []
                st.rerun()

    st.markdown('<div style="flex:1;min-height:40px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:12px 14px;border-top:1px solid rgba(24,95,165,0.10);
                font-size:11px;color:#8AAAC9;display:flex;align-items:center;gap:5px;margin-top:auto;">
      ℹ️ &nbsp;Multimodal RAG · Claude
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN — UPLOAD STATE
# ═══════════════════════════════════════════════════════════════
if not st.session_state.paper_indexed:

    # Hero
    st.markdown("""
    <div style="padding:40px 40px 0;">
      <div style="font-size:28px;font-weight:600;color:#0F1C2E;letter-spacing:-0.03em;margin-bottom:5px;">
        Research workspace
      </div>
      <div style="font-size:14px;color:#8AAAC9;">
        Multimodal RAG — upload a scientific PDF and ask questions about text, tables, and figures
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload card
    st.markdown("""
    <div style="margin:28px 40px 0;padding:44px 32px;background:#FFFFFF;
                border:2px dashed rgba(24,95,165,0.20);border-radius:18px;text-align:center;">
      <div style="width:68px;height:68px;background:#EBF4FF;border:1px solid rgba(24,95,165,0.18);
                  border-radius:16px;display:flex;align-items:center;justify-content:center;
                  font-size:30px;margin:0 auto 18px;">📂</div>
      <div style="font-size:18px;font-weight:600;color:#0F1C2E;letter-spacing:-0.02em;margin-bottom:7px;">
        Upload a paper to get started
      </div>
      <div style="font-size:13px;color:#8AAAC9;max-width:340px;margin:0 auto;line-height:1.65;">
        The system extracts text, tables, and figures automatically and indexes everything for semantic search.
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:18px;">
        %s
      </div>
    </div>
    """ % "".join(
        f'<span style="background:#EBF4FF;border:1px solid rgba(24,95,165,0.18);border-radius:20px;'
        f'padding:5px 14px;font-size:12px;color:#0C447C;font-weight:500;">{t}</span>'
        for t in ["arXiv papers", "IEEE articles", "Research reports", "Conference papers", "Nature / Science"]
    ), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    _, col_up, _ = st.columns([1, 2, 1])
    with col_up:
        uploaded = st.file_uploader("Choose a PDF", type="pdf", label_visibility="collapsed")
        if uploaded:
            progress_bar = st.progress(0, text="Parsing document…")
            for pct in [15, 35, 55, 75, 90]:
                time.sleep(0.3)
                progress_bar.progress(pct, text=f"Indexing… {pct}%")
            try:
                resp = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded.name, uploaded, "application/pdf")},
                )
            except Exception as e:
                st.error(f"Could not reach the backend: {e}")
                st.stop()
            progress_bar.progress(100, text="Complete!")
            time.sleep(0.4)
            if resp.status_code == 200:
                st.session_state.paper_indexed = True
                st.session_state.paper_info = resp.json()
                st.rerun()
            else:
                st.error(f"Upload failed ({resp.status_code}): {resp.text}")


# ═══════════════════════════════════════════════════════════════
#  MAIN — Q&A STATE
# ═══════════════════════════════════════════════════════════════
else:
    # ── Header ────────────────────────────────────────────────
    mode_icon = "🤖" if st.session_state.use_agent else "⚡"
    mode_text = "Agent mode active" if st.session_state.use_agent else "Direct RAG mode"
    mode_color = "#185FA5" if st.session_state.use_agent else "#1D9E75"
    mode_bg = "#EBF4FF" if st.session_state.use_agent else "#E1F5EE"
    mode_border = "rgba(24,95,165,0.20)" if st.session_state.use_agent else "rgba(29,158,117,0.20)"

    st.markdown(f"""
    <div style="padding:24px 40px 0;background:#FFFFFF;border-bottom:1px solid rgba(24,95,165,0.09);">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:18px;">
        <div>
          <div style="font-size:24px;font-weight:600;color:#0F1C2E;letter-spacing:-0.03em;">Research workspace</div>
          <div style="font-size:13px;color:#8AAAC9;margin-top:3px;">Ask anything about text, tables, and figures</div>
        </div>
        <div style="display:flex;align-items:center;gap:7px;background:{mode_bg};
                    border:1px solid {mode_border};border-radius:20px;padding:7px 16px;
                    font-size:12px;color:{mode_color};font-weight:500;">
          <span style="width:7px;height:7px;border-radius:50%;background:{mode_color};display:inline-block;"></span>
          {mode_icon} {mode_text}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Question input ─────────────────────────────────────────
    st.markdown('<div style="padding:18px 40px 0;background:#FFFFFF;">', unsafe_allow_html=True)
    col_q, col_btn = st.columns([7, 1])
    with col_q:
        question = st.text_input(
            "q",
            placeholder="Ask a question about this paper… (Enter to submit)",
            label_visibility="collapsed",
            key="q_input",
        )
    with col_btn:
        ask = st.button("Ask →", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Example chips ──────────────────────────────────────────
    st.markdown('<div style="padding:10px 40px 14px;background:#FFFFFF;border-bottom:1px solid rgba(24,95,165,0.09);">', unsafe_allow_html=True)

    examples = [
        "What methodology did they use?",
        "What are the key results?",
        "What does figure 1 show?",
        "What are the limitations?",
    ]
    chip_cols = st.columns(4)
    for i, ex in enumerate(examples):
        with chip_cols[i]:
            if st.button(ex, key=f"chip_{i}", type="secondary", use_container_width=True):
                question = ex
                ask = True
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Process question ───────────────────────────────────────
    if ask and question:
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(f"""
        <div style="margin:18px 40px 0;padding:14px 20px;background:#FFFFFF;
                    border:1px solid rgba(24,95,165,0.12);border-radius:12px;
                    display:flex;align-items:center;gap:12px;">
          <div style="display:flex;gap:4px;align-items:center;">
            {"".join(
                f'<div style="width:7px;height:7px;border-radius:50%;background:#378ADD;'
                f'animation:blink 1.2s {d}s infinite;opacity:0.3;"></div>'
                for d in ["0","0.2","0.4"]
            )}
          </div>
          <div style="font-size:13px;color:#8AAAC9;">
            {"Decomposing question into sub-queries…" if st.session_state.use_agent else "Retrieving relevant chunks…"}
          </div>
          <div style="margin-left:auto;display:flex;gap:5px;">
            {"".join(
                f'<span style="font-size:11px;color:{mode_color};background:{mode_bg};'
                f'border:1px solid {mode_border};border-radius:20px;padding:2px 9px;">{s}</span>'
                for s in ["Retrieve","Reason","Synthesize"]
            )}
          </div>
        </div>
        <style>
        @keyframes blink {{ 0%,80%,100% {{ opacity:0.2;transform:scale(0.8); }} 40% {{ opacity:1;transform:scale(1); }} }}
        </style>
        """, unsafe_allow_html=True)

        try:
            resp = requests.post(
                f"{API_URL}/ask",
                json={"question": question, "use_agent": st.session_state.use_agent},
            )
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Backend error: {e}")
            st.stop()

        thinking_placeholder.empty()

        if resp.status_code == 200:
            data = resp.json()
            st.session_state.history.insert(0, {
                "question": question,
                "answer": data["answer"],
                "sources": data["sources"],
                "agent_mode": st.session_state.use_agent,
            })
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")

    # ── Q&A History ────────────────────────────────────────────
    st.markdown('<div style="padding:18px 40px;display:flex;flex-direction:column;gap:14px;">', unsafe_allow_html=True)

    for idx, item in enumerate(st.session_state.history):
        was_agent = item.get("agent_mode", False)
        badge_color = "#185FA5" if was_agent else "#1D9E75"
        badge_bg = "#EBF4FF" if was_agent else "#E1F5EE"
        badge_border = "rgba(24,95,165,0.20)" if was_agent else "rgba(29,158,117,0.20)"
        badge_icon = "🤖" if was_agent else "⚡"
        badge_label = "Agent" if was_agent else "Direct RAG"

        answer_html = item["answer"].replace("\n", "<br>")

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid rgba(24,95,165,0.10);border-radius:14px;
                    overflow:hidden;margin-bottom:2px;
                    animation:cardIn 0.35s cubic-bezier(0.22,1,0.36,1);">
          <style>@keyframes cardIn {{ from {{ opacity:0;transform:translateY(12px); }} to {{ opacity:1;transform:translateY(0); }} }}</style>

          <!-- Card header -->
          <div style="padding:16px 20px 0;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
              <span style="display:inline-flex;align-items:center;gap:5px;
                           background:{badge_bg};border:1px solid {badge_border};
                           border-radius:20px;padding:3px 11px;font-size:11px;
                           color:{badge_color};font-weight:600;">
                {badge_icon} {badge_label}
              </span>
            </div>
            <div style="font-size:15px;font-weight:600;color:#0F1C2E;line-height:1.4;
                        padding-bottom:13px;border-bottom:1px solid rgba(24,95,165,0.08);
                        letter-spacing:-0.01em;">
              {item['question']}
            </div>
          </div>

          <!-- Answer body -->
          <div style="padding:14px 20px 16px;">
            <div style="font-size:13px;color:#2D4460;line-height:1.80;">{answer_html}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Expandable sources / sub-questions
        if item["sources"]:
            sources = item["sources"]
            if was_agent:
                with st.expander(f"🧠 View agent reasoning — {len(sources)} sub-question(s)"):
                    for i, src in enumerate(sources):
                        st.markdown(f"""
                        <div style="background:#F4F7FB;border:1px solid rgba(24,95,165,0.10);
                                    border-radius:9px;padding:11px 14px;margin-bottom:8px;">
                          <div style="font-size:10px;font-weight:700;color:#185FA5;
                                      text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px;">
                            Sub-question {i+1}
                          </div>
                          <div style="font-size:13px;font-weight:500;color:#0F1C2E;margin-bottom:4px;">
                            {src.get('question', '')}
                          </div>
                          <div style="font-size:12px;color:#4A6480;line-height:1.65;">
                            {src.get('answer', '')[:500]}{"…" if len(src.get('answer','')) > 500 else ""}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                with st.expander(f"📄 View retrieved sources — {len(sources)} chunk(s)"):
                    for i, src in enumerate(sources):
                        meta = src.get("metadata", {})
                        page = meta.get("page_num", "?")
                        chunk_type = meta.get("type", "text").capitalize()
                        st.markdown(f"""
                        <div style="background:#F4F7FB;border:1px solid rgba(24,95,165,0.10);
                                    border-radius:9px;padding:11px 14px;margin-bottom:8px;">
                          <div style="font-size:10px;font-weight:700;color:#378ADD;
                                      text-transform:uppercase;letter-spacing:0.06em;margin-bottom:5px;
                                      display:flex;align-items:center;gap:6px;">
                            📄 Source {i+1} &nbsp;·&nbsp; Page {page} &nbsp;·&nbsp; {chunk_type}
                          </div>
                          <div style="font-size:12px;color:#4A6480;line-height:1.65;font-style:italic;">
                            "{src.get('text', '')[:350]}{"…" if len(src.get('text',''))>350 else ""}"
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    # Empty state (no history yet)
    if not st.session_state.history:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    padding:52px 28px;text-align:center;">
          <div style="width:64px;height:64px;background:#EBF4FF;
                      border:1px solid rgba(24,95,165,0.18);border-radius:16px;
                      display:flex;align-items:center;justify-content:center;
                      font-size:28px;margin-bottom:16px;">💬</div>
          <div style="font-size:16px;font-weight:600;color:#0F1C2E;margin-bottom:6px;">
            Start asking questions
          </div>
          <div style="font-size:13px;color:#8AAAC9;max-width:280px;line-height:1.65;">
            Type a question above or pick one of the example chips to explore this paper.
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)