import re
import pandas as pd

def preprocess(data):
    # 1. ROBUST REGEX
    # Matches dates with 2 or 4 digit years, and times with optional AM/PM
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?[aA][mM]|\s?[pP][mM])?\s-\s'
    
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # 2. DATE PARSING (Try all common formats)
    def parse_date(date_str):
        # List of potential formats to check
        # %Y = 2025, %y = 25
        # %H = 24hr, %I = 12hr
        formats = [
            '%d/%m/%Y, %H:%M - ',        # 24hr, 4-digit year
            '%d/%m/%y, %H:%M - ',        # 24hr, 2-digit year
            '%d/%m/%Y, %I:%M %p - ',     # 12hr, 4-digit year
            '%d/%m/%y, %I:%M %p - ',     # 12hr, 2-digit year (Your Case)
            '%m/%d/%y, %H:%M - ',        # US format fallback
            '%m/%d/%Y, %H:%M - '
        ]
        
        # Sometimes there is a hidden "narrow no-break space" before PM/AM
        # We replace it with a normal space just in case
        date_str = date_str.replace('\u202f', ' ')

        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError:
                continue
        return pd.NaT # Return "Not a Time" if all fail

    # Apply the parser to the whole column
    df['message_date'] = df['message_date'].apply(parse_date)
    
    # Drop rows where date parsing failed completely
    df.dropna(subset=['message_date'], inplace=True)

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df.reset_index(drop=True, inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour:02d}-{(hour+1):02d}")

    df['period'] = period

    return df
