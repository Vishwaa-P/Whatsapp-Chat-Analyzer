from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(str(message).split())

    # fetch number of media messages (strip whitespace, case-insensitive)
    num_media_messages = df[df['message'].str.strip().str.lower().eq('<media omitted>')].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(str(message)))

    return num_messages,len(words),num_media_messages,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'user': 'person', 'count': 'percent_count'})
    return x,df

def create_wordcloud(selected_user,df):
    # load stopwords as a set (faster and safer)
    with open('stopwords_marathi_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification'].copy()
    # filter media rows robustly
    temp = temp[~temp['message'].str.strip().str.lower().eq('<media omitted>')].copy()

    def remove_stop_words(message):
        y = []
        for word in str(message).lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):
    with open('stopwords_marathi_hinglish.txt','r', encoding='utf-8') as f:
        stop_words = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification'].copy()
    temp = temp[~temp['message'].str.strip().str.lower().eq('<media omitted>')].copy()

    words = []
    for message in temp['message']:
        for word in str(message).lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        s = str(message)
        # Try emoji.emoji_list (works with modern emoji package)
        try:
            found = emoji.emoji_list(s)
            emojis.extend([d['emoji'] for d in found])
            continue
        except Exception:
            pass

        # Fallback: test characters for emoji using available helpers
        for ch in s:
            if getattr(emoji, 'is_emoji', None):
                try:
                    if emoji.is_emoji(ch):
                        emojis.append(ch)
                except Exception:
                    # If the installed emoji doesn't support is_emoji properly, fall back next
                    if ch in getattr(emoji, 'EMOJI_DATA', {}):
                        emojis.append(ch)
            else:
                if ch in getattr(emoji, 'EMOJI_DATA', {}):
                    emojis.append(ch)

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

# the rest of helper functions remain unchanged...
def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

# def daily_timeline(selected_user,df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     daily_timeline = df.groupby('only_date').count()['message'].reset_index()
#     return daily_timeline

def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap
