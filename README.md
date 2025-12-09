# 📊 WhatsApp Chat Analyzer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://whatsapp-chat-analyzer-v.streamlit.app/)

> **🔴 [Click here to view the Live Demo](https://whatsapp-chat-analyzer-v.streamlit.app/)**

A comprehensive tool to analyze WhatsApp chat exports, providing insights into user activity, communication patterns, and linguistic trends without compromising privacy.

## 🚀 Features

* **Top Statistics**: Total messages, words, media shared, and links shared.
* **Activity Timelines**: Track chat volume over months and years.
* **Activity Maps**:
    * **Busy Days**: Identify which day of the week is most active.
    * **Busy Months**: See which months have the highest engagement.
    * **Weekly Heatmap**: Visual distribution of activity by day and time.
* **User Analysis**: Identify the most active users in group chats.
* **Text Analysis & WordCloud**:
    * **Multi-Language Support**: Uses a **custom-built stopword list** combining **English, Hindi, and Marathi (Hinglish)** to filter out common chat fillers (like *kay, kuthe, pan, aani*).
    * *Note: Since regional slang and spelling variations are endless, this list is a constant work in progress. Some stopwords might still appear, and the list will be updated over time.*
* **Emoji Analysis**: Statistical breakdown of emoji usage.

## 🛠️ Tech Stack

* **Language**: Python 3.13
* **Framework**: Streamlit
* **Data Manipulation**: Pandas, NumPy
* **Visualization**: Matplotlib, Seaborn
* **Text Processing**: Regex (re), urlextract, emoji, WordCloud

## 📂 Project Structure

```text
Whatsapp-Chat-Analyzer/
├── app.py                      # Main Streamlit application
├── preprocessor.py             # Data cleaning and extraction logic
├── helper.py                   # Statistical analysis functions
├── stopwords_marathi_hinglish.txt # Custom stopwords file (Eng + Hin + Mar)
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation


## ⚙️ Installation & Run Locally

If you want to run this on your own machine:

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/Vishwaa-P/Whatsapp-Chat-Analyzer.git](https://github.com/Vishwaa-P/Whatsapp-Chat-Analyzer.git)
    cd Whatsapp-Chat-Analyzer
    ```

2.  **Create a Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the App**
    ```bash
    streamlit run app.py
    ```

## 📱 How to Use

1.  Open WhatsApp on your mobile device.
2.  Open the chat (individual or group) you want to analyze.
3.  Tap on **More options** (three dots) > **More** > **Export chat**.
4.  Select **Without Media**.
5.  Upload the generated `.txt` file to the sidebar of the application.

## 🔒 Privacy Note

This application processes data locally (or in memory on the cloud server) and does not store any of your chat data. The analysis is performed on the fly, and the data is discarded immediately after you close the tab.

## 🎓 Acknowledgements

* **Guidance**: Special thanks to **[CampusX](https://www.youtube.com/@campusx-official)** for their guidance.
* **Datasets**: Data used for testing was generated from personal WhatsApp exports.


**Vishwajeet Padole**
* [GitHub Profile](https://github.com/Vishwaa-P)
