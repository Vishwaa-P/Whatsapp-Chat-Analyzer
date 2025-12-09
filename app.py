import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tiny CSS for a cleaner look
st.markdown(
    """
    <style>
      .title {font-size:32px; font-weight:700; margin-bottom: -6px;}
      .subtitle {color:#6b7280; font-size:14px; margin-top: 0; margin-bottom: 18px;}
      .center {text-align:center}
      .muted {color:#6b7280}
      .metric-card {border-radius:10px; padding:10px; background: linear-gradient(180deg,#ffffff,#f8fbff);}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar: upload only ---
st.sidebar.header("🔧 Upload Chat File")
st.sidebar.write("Upload a WhatsApp export (.txt). Your file stays local — nothing is uploaded anywhere.")

uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp export (.txt)", type=["txt"])

# Helper: convert dataframe to CSV bytes for downloads
@st.cache_data
def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    buf.seek(0)
    return buf.getvalue()

# Determine input data
data = None
if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
    except Exception as e:
        st.sidebar.error("Failed to read uploaded file — please try a clean .txt WhatsApp export.")

# --- Main UI ---
if data:
    # Preprocess with defensive error handling
    try:
        df = preprocessor.preprocess(data)
    except Exception as e:
        st.error("Failed to parse the provided chat text. Check format or try another export.")
        st.exception(e)
        st.stop()

    # Basic validation
    if "message" not in df.columns or "user" not in df.columns:
        st.error("Processed data doesn't look right (missing 'message' or 'user' columns).")
        st.stop()

    # User chooser
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    # Download processed CSV
    csv_bytes = df_to_csv_bytes(df)
    st.sidebar.download_button("Download processed CSV 📥", data=csv_bytes, file_name="chat_processed.csv", mime="text/csv")

    # Get stats using helper
    num_messages, words_count, media_count, links_count = helper.fetch_stats(selected_user, df)

    # Header
    st.markdown('<div class="title">💬 WhatsApp Chat Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Private, fast and visual chat insights — upload your chat export. This runs locally on your machine.</div>', unsafe_allow_html=True)

    # Top metrics
    col_m1, col_m2, col_m3, col_m4 = st.columns(4, gap="large")
    col_m1.metric("Messages", f"{num_messages:,}")
    col_m2.metric("Words", f"{words_count:,}")
    col_m3.metric("Media Shared", f"{media_count:,}")
    col_m4.metric("Links", f"{links_count:,}")

    # Main navigation tabs
    tab_overview, tab_users, tab_text, tab_emoji, tab_heat = st.tabs(
        ["📈 Overview", "👥 Users", "📝 Text", "😊 Emojis", "📊 Heatmap"]
    )

    # ---------------- Overview ----------------
    with tab_overview:
        st.subheader("Monthly activity")
        try:
            timeline = helper.monthly_timeline(selected_user, df)
            if timeline.empty:
                st.info("Not enough data to build a monthly timeline.")
            else:
                fig, ax = plt.subplots(figsize=(11, 3))
                ax.plot(timeline['time'], timeline['message'], color="#2b8cbe", lw=2)
                ax.fill_between(timeline['time'], timeline['message'], alpha=0.07, color="#2b8cbe")
                ax.set_xticks(range(len(timeline['time'])))
                ax.set_xticklabels(timeline['time'], rotation=45, ha='right')
                ax.set_ylabel("Messages")
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
        except Exception as e:
            st.warning("Couldn't produce monthly timeline: " + str(e))

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Most active weekdays")
            try:
                busy_day = helper.week_activity_map(selected_user, df)
                if busy_day.empty:
                    st.info("No weekday activity available.")
                else:
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax.bar(busy_day.index, busy_day.values, color="#7b68ee")
                    ax.set_xticklabels(busy_day.index, rotation=45, ha='right')
                    st.pyplot(fig)
            except Exception as e:
                st.warning("Couldn't show weekday activity: " + str(e))

        with c2:
            st.subheader("Most active months")
            try:
                busy_month = helper.month_activity_map(selected_user, df)
                if busy_month.empty:
                    st.info("No monthly activity available.")
                else:
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax.bar(busy_month.index, busy_month.values, color="#f59e0b")
                    ax.set_xticklabels(busy_month.index, rotation=45, ha='right')
                    st.pyplot(fig)
            except Exception as e:
                st.warning("Couldn't show monthly activity: " + str(e))

    # ---------------- Users ----------------
    with tab_users:
        st.subheader("Most active users")
        if selected_user == "Overall":
            try:
                top_counts, percent_df = helper.most_busy_users(df)
                left, right = st.columns((2, 1))
                with left:
                    fig, ax = plt.subplots(figsize=(8, 3))
                    ax.bar(top_counts.index, top_counts.values, color="#ef4444")
                    ax.set_xticklabels(top_counts.index, rotation=45, ha='right')
                    st.pyplot(fig)
                with right:
                    st.dataframe(percent_df)
            except Exception as e:
                st.warning("Couldn't compute busy users: " + str(e))
        else:
            st.info("Viewing single-user stats. Switch to 'Overall' to see group-level comparisons.")

    # ---------------- Text ----------------
    with tab_text:
        st.subheader("Wordcloud")
        try:
            wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        except Exception as e:
            st.warning("Wordcloud unavailable: " + str(e))

        st.markdown("---")
        st.subheader("Top words")
        try:
            most_common_df = helper.most_common_words(selected_user, df)
            if most_common_df.empty:
                st.info("No text content (maybe mostly media/shared attachments).")
            else:
                df_words = most_common_df.rename(columns={0: "word", 1: "count"})
                st.dataframe(df_words)
                csv_wc = df_words.to_csv(index=False).encode("utf-8")
                st.download_button("Download words CSV", csv_wc, "top_words.csv", "text/csv")
        except Exception as e:
            st.warning("Couldn't compute most common words: " + str(e))

    # ---------------- Emojis ----------------
    with tab_emoji:
        st.subheader("Emoji analysis")
        try:
            emoji_df = helper.emoji_helper(selected_user, df)
            if emoji_df.empty:
                st.info("No emoji data found.")
            else:
                df_em = emoji_df.rename(columns={0: "emoji", 1: "count"})
                st.dataframe(df_em)
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.pie(df_em['count'].head(6), labels=df_em['emoji'].head(6), autopct="%0.1f%%", textprops={'fontsize': 10})
                ax.axis("equal")
                st.pyplot(fig)
        except Exception as e:
            st.warning("Emoji analysis failed: " + str(e))

    # ---------------- Heatmap ----------------
    with tab_heat:
        st.subheader("Weekly activity heatmap")
        try:
            user_heatmap = helper.activity_heatmap(selected_user, df)
            if user_heatmap.size == 0:
                st.info("No activity to show for heatmap.")
            else:
                fig, ax = plt.subplots(figsize=(12, 4))
                sns.heatmap(user_heatmap, cmap="YlGnBu", linewidths=.5, ax=ax)
                st.pyplot(fig, use_container_width=True)
        except Exception as e:
            st.warning("Heatmap could not be built: " + str(e))

    # Raw data (optional)
    with st.expander("🔎 Inspect processed data (first 200 rows)"):
        st.dataframe(df.head(200))

# --- No data UI ---
else:
    st.markdown('<div class="center" style="padding:56px 0;">', unsafe_allow_html=True)
    st.markdown('<h1>💬 WhatsApp Chat Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="muted">Upload your WhatsApp export (.txt) using the left sidebar. This app runs locally and does not send your data anywhere.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)