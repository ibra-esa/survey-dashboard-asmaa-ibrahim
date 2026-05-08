import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob

st.set_page_config(page_title="SurveyPoint EDA", page_icon="📐", layout="wide")
st.title("📐 SurveyPoint — דשבורד EDA")
st.caption("ניתוח נתוני קואורדינטות מדידה")

DATA_DIR = "DATA"
COLORS = ["#3266ad", "#1D9E75", "#BA7517", "#A32D2D"]

folders = sorted([f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))])

def load_csv(folder):
    path = os.path.join(DATA_DIR, folder)
    files = glob.glob(os.path.join(path, "*.csv")) + glob.glob(os.path.join(path, "*.CSV"))
    if not files:
        return None
    for enc in ["utf-8-sig", "cp1255", "windows-1255", "utf-8", "latin-1"]:
        try:
            df = pd.read_csv(files[0], encoding=enc)
            df.columns = ["שם נקודה", "Y", "X"]
            df["Y"] = pd.to_numeric(df["Y"], errors="coerce")
            df["X"] = pd.to_numeric(df["X"], errors="coerce")
            return df.dropna(subset=["Y", "X"])
        except Exception:
            continue
    return None

with st.sidebar:
    st.header("⚙️ הגדרות")
    selected = st.selectbox("בחר תיקייה", folders, format_func=lambda x: f"תיקייה {x}")

df = load_csv(selected)

if df is None:
    st.error("לא נמצא קובץ CSV בתיקייה זו")
    st.stop()

color = COLORS[folders.index(selected) % len(COLORS)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("נקודות", len(df))
c2.metric("טווח Y", f"{df['Y'].max() - df['Y'].min():.2f}")
c3.metric("טווח X", f"{df['X'].max() - df['X'].min():.2f}")
c4.metric("ערכים חסרים", int(df.isnull().sum().sum()))

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("פיזור נקודות (כמו אוטוקד)")
    fig_scatter = px.scatter(df, x="Y", y="X", hover_name="שם נקודה", color_discrete_sequence=[color])
    fig_scatter.update_traces(marker=dict(size=5 if len(df) > 100 else 8))
    fig_scatter.update_layout(height=320, margin=dict(t=10, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("השוואת גדלי תיקיות")
    bar_data = []
    for f in folders:
        tmp = load_csv(f)
        if tmp is not None:
            bar_data.append({"תיקייה": f"תיקייה {f}", "נקודות": len(tmp)})
    fig_bar = px.bar(pd.DataFrame(bar_data), x="תיקייה", y="נקודות",
                     color="תיקייה", color_discrete_sequence=COLORS)
    fig_bar.update_layout(height=320, margin=dict(t=10, b=10), showlegend=False, xaxis_tickangle=-20)
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

st.subheader("10 נקודות ראשונות")
st.dataframe(df.head(10).reset_index(drop=True), use_container_width=True, hide_index=True)

st.divider()
csv_out = df.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ הורד CSV", data=csv_out, file_name=f"תיקייה_{selected}.csv", mime="text/csv")
