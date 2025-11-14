import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(page_title="Pageview Spike Taper", layout="wide")

st.title("Pageview Spike Taper Duration")
st.subheader("Shows the days from the peak of a major spike in interest until it's Z-score drops below a certain point")
st.text("Generated from the daily cc interest data. Default dates are the 5 main ones from the paper.")


data_path = "..\\data\\st13_data.csv"
df = pd.read_csv(data_path)

# convert date
df["date"] = pd.to_datetime(df["date"])

# filter 2017–2022
df = df[(df["date"].dt.year >= 2017) & (df["date"].dt.year <= 2022)]

#st.subheader("Filtered Daily Dataset (2017–2022)")
#st.write(df.head())


st.subheader("Spike Dates")

default_spike_string = "2017-06-01, 2019-09-23, 2020-01-24, 2021-01-20, 2022-10-02"

spike_input = st.text_input(
    "Enter spike dates (comma-separated):",
    value=default_spike_string
)

#
spike_dates = [pd.to_datetime(s.strip()) for s in spike_input.split(",")]


df_daily = df.groupby("date")["total_cc_pageview_counts"].sum().reset_index()
df_daily["rolling_mean"] = df_daily["total_cc_pageview_counts"].rolling(window=7, center=True).mean()

mean = df_daily["rolling_mean"].mean()
std = df_daily["rolling_mean"].std()

df_daily["z_score"] = (df_daily["rolling_mean"] - mean) / std


durations = []
for spike in spike_dates:
    after_spike = df_daily[df_daily["date"] > spike]
    below = after_spike[after_spike["z_score"] < 0.5]

    if not below.empty:
        drop_date = below.iloc[0]["date"]
        duration_days = (drop_date - spike).days
        durations.append({
            "spike_date": spike,
            "drop_date": drop_date,
            "duration_days": duration_days
        })
    else:
        durations.append({
            "spike_date": spike,
            "drop_date": None,
            "duration_days": None
        })

df_durations = pd.DataFrame(durations)

st.subheader("Computed Spike Durations")
st.write(df_durations)



event_colors = {
    2017: "#f0b639",
    2019: "green",
    2020: "blue",
    2021: "red",
    2022: "#ff3ab3"
}

df_durations["year"] = df_durations["spike_date"].dt.year
df_durations["spike_label"] = df_durations["spike_date"].dt.strftime('%Y-%m-%d')
df_durations["color"] = df_durations["year"].map(event_colors)

fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(
    df_durations['spike_label'],
    df_durations['duration_days'],
    color=df_durations['color']
)

ax.set_title("Duration of Pageview Spikes (Days until Z < 0.5)")
ax.set_ylabel("Days")
ax.set_xlabel("Spike Date")
plt.xticks(rotation=45)


'''
legend_handles = [
    matplotlib.patches.Patch(color=color, label=str(year))
    for year, color in event_colors.items()
]
ax.legend(handles=legend_handles, title="Event Year", loc="upper right")
'''

plt.tight_layout()

st.subheader("Spike Duration Plot")
st.pyplot(fig)
