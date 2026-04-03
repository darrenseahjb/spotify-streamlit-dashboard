import base64
import html
import os
from pathlib import Path

import altair as alt
import pandas as pd
import pg8000
import streamlit as st

alt.renderers.set_embed_options(actions=False)


st.set_page_config(
    page_title="Spotify Insights",
    page_icon="🎧",
    layout="wide",
)


def inject_styles():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=DM+Sans:wght@400;500;700&display=swap');

            :root {
                --bg-start: #09111f;
                --bg-end: #130a1c;
                --panel: rgba(14, 22, 38, 0.74);
                --panel-strong: rgba(18, 28, 47, 0.92);
                --line: rgba(255, 255, 255, 0.08);
                --text: #f6f7fb;
                --muted: #9ca6ba;
                --green: #1ed760;
                --pink: #ff5fa2;
                --blue: #7bdcff;
                --gold: #ffd166;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(30, 215, 96, 0.16), transparent 26%),
                    radial-gradient(circle at top right, rgba(123, 220, 255, 0.14), transparent 24%),
                    radial-gradient(circle at bottom center, rgba(255, 95, 162, 0.10), transparent 28%),
                    linear-gradient(140deg, var(--bg-start), var(--bg-end));
                color: var(--text);
            }

            .block-container {
                padding-top: 2.85rem;
                padding-bottom: 3rem;
                max-width: 1240px;
            }

            h1, h2, h3, h4, p, span, label, div {
                font-family: "DM Sans", sans-serif;
            }

            a[aria-label="Copy link to this element"],
            .stHeadingAnchor,
            [data-testid="stHeaderActionElements"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }

            .hero {
                position: relative;
                overflow: hidden;
                padding: 0.92rem 1.12rem 0.9rem 1.12rem;
                min-height: 226px;
                border: 1px solid var(--line);
                border-radius: 28px;
                background:
                    linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02)),
                    linear-gradient(120deg, rgba(30, 215, 96, 0.12), rgba(123, 220, 255, 0.08), rgba(255, 95, 162, 0.10));
                box-shadow: 0 24px 80px rgba(0, 0, 0, 0.30);
                margin-bottom: 0.7rem;
            }

            .hero-shell {
                position: relative;
                z-index: 1;
                display: grid;
                grid-template-columns: minmax(0, 1fr) 132px;
                gap: 1.05rem;
                align-items: center;
            }

            .hero-copy {
                min-width: 0;
                max-width: 430px;
            }

            .hero:before {
                content: "";
                position: absolute;
                inset: auto -3rem -4rem auto;
                width: 200px;
                height: 200px;
                border-radius: 999px;
                background: radial-gradient(circle, rgba(255, 95, 162, 0.28), transparent 70%);
            }

            .hero-title {
                font-family: "Space Grotesk", sans-serif;
                font-size: clamp(0.84rem, 0.92vw, 1.02rem);
                line-height: 1.02;
                font-weight: 700;
                margin: 0;
                max-width: 100%;
                white-space: nowrap;
                letter-spacing: -0.02em;
            }

            .hero-subtitle {
                color: var(--muted);
                margin-top: 0.42rem;
                max-width: 400px;
                font-size: 0.75rem;
                line-height: 1.3;
            }

            .hero-meta-row {
                display: flex;
                align-items: center;
                gap: 0.62rem;
                flex-wrap: wrap;
                margin-top: 0.5rem;
            }

            .hero-meta-separator {
                width: 16px;
                height: 1px;
                background: rgba(255, 255, 255, 0.16);
            }

            .hero-secondary-link {
                display: inline-flex;
                align-items: center;
                gap: 0.34rem;
                color: #d7deee;
                font-size: 0.74rem;
                font-weight: 600;
                text-decoration: none;
                transition: color 180ms ease, transform 180ms ease;
            }

            .hero-secondary-link:hover {
                color: #f6f7fb;
                transform: translateX(1px);
            }

            .hero-secondary-link::after {
                content: "↗";
                font-size: 0.78rem;
                line-height: 1;
            }

            .chip {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                padding: 0.34rem 0.62rem;
                border: 1px solid var(--line);
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.04);
                color: #e8ebf2;
                font-size: 0.76rem;
            }

            .hero-profile {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-width: 132px;
                gap: 0.24rem;
            }

            .hero-profile-link {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                text-decoration: none;
            }

            .hero-profile-link,
            .hero-profile-link:hover,
            .hero-profile-link:focus,
            .hero-profile-link:visited {
                text-decoration: none !important;
            }

            .hero-profile-link:hover .hero-avatar {
                transform: translateY(-2px) scale(1.015);
                box-shadow:
                    0 18px 50px rgba(0, 0, 0, 0.28),
                    0 0 0 1px rgba(255, 255, 255, 0.10),
                    0 0 0 8px rgba(255, 255, 255, 0.03);
            }

            .hero-profile-link:hover .hero-profile-cta {
                color: #f6f7fb;
            }

            .hero-avatar {
                width: 88px;
                height: 88px;
                border-radius: 999px;
                object-fit: cover;
                border: 1px solid rgba(255, 255, 255, 0.12);
                box-shadow:
                    0 14px 38px rgba(0, 0, 0, 0.24),
                    0 0 0 1px rgba(255, 255, 255, 0.05),
                    0 0 0 8px rgba(255, 255, 255, 0.025);
                transition: transform 180ms ease, box-shadow 180ms ease;
            }

            .hero-profile-cta {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 0;
                border: none;
                border-radius: 0;
                background: transparent;
                color: var(--green);
                font-size: 0.58rem;
                font-weight: 700;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                text-decoration: none;
                transition: color 180ms ease;
                white-space: nowrap;
                text-align: center;
            }

            .section-label {
                margin: 0.12rem 0 0.05rem 0;
                color: #dce3f4;
                font-size: 0.92rem;
                text-transform: uppercase;
                letter-spacing: 0.14em;
                font-weight: 700;
            }

            .section-label.patterns-section {
                margin-top: 0.02rem;
            }

            .top-grid {
                margin-bottom: -0.08rem;
            }

            .snapshot-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.98rem;
                align-content: start;
            }

            .stat-card {
                border: 1px solid var(--line);
                background: var(--panel);
                backdrop-filter: blur(14px);
                border-radius: 22px;
                padding: 1.15rem 1.15rem 1rem 1.15rem;
                height: 188px;
                display: flex;
                flex-direction: column;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
            }

            .stat-card.compact {
                height: 106px;
                padding: 0.68rem 0.84rem 0.66rem 0.84rem;
                border-radius: 18px;
            }

            .stat-kicker {
                color: var(--muted);
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 0.8rem;
            }

            .stat-value {
                font-family: "Space Grotesk", sans-serif;
                font-size: clamp(1.85rem, 2.3vw, 2.55rem);
                line-height: 0.95;
                margin-bottom: 0.45rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                overflow-wrap: anywhere;
            }

            .stat-value.long {
                font-size: clamp(1.55rem, 1.95vw, 2.1rem);
                line-height: 0.9;
                letter-spacing: -0.035em;
            }

            .stat-value.xlong {
                font-size: clamp(1.3rem, 1.65vw, 1.7rem);
                line-height: 0.88;
                letter-spacing: -0.04em;
            }

            .muted {
                color: var(--muted);
                font-size: 0.84rem;
                margin-top: auto;
            }

            .stat-card.compact .stat-kicker {
                font-size: 0.66rem;
                margin-bottom: 0.22rem;
            }

            .stat-card.compact .stat-value {
                font-size: clamp(1.26rem, 1.65vw, 1.64rem);
                margin-bottom: 0.06rem;
            }

            .stat-card.compact .stat-value.long {
                font-size: clamp(0.9rem, 1.08vw, 1.04rem);
            }

            .stat-card.compact .stat-value.xlong {
                font-size: clamp(0.84rem, 0.98vw, 0.94rem);
            }

            .stat-card.compact .muted {
                font-size: 0.68rem;
                line-height: 1.04;
            }

            .panel {
                border: 1px solid var(--line);
                background: var(--panel);
                backdrop-filter: blur(14px);
                border-radius: 24px;
                padding: 0.62rem 1.02rem 0.62rem 1.02rem;
                margin-top: 0.2rem;
            }

            .panel-title {
                font-family: "Space Grotesk", sans-serif;
                font-size: 1.08rem;
                margin-bottom: 0;
            }

            .panel-copy {
                color: var(--muted);
                font-size: 0.86rem;
                margin-bottom: 0.6rem;
            }

            .pattern-head {
                min-height: 108px;
                display: flex;
                flex-direction: column;
                justify-content: flex-start;
                margin-bottom: 0.72rem;
            }

            .pattern-head.hero-analytic {
                background:
                    linear-gradient(135deg, rgba(255, 209, 102, 0.10), rgba(123, 220, 255, 0.05)),
                    rgba(14, 22, 38, 0.88);
                border-color: rgba(255, 209, 102, 0.18);
                box-shadow:
                    inset 0 1px 0 rgba(255,255,255,0.04),
                    0 16px 48px rgba(0, 0, 0, 0.18);
            }

            .pattern-head.hero-analytic .panel-title {
                color: #fff3c4;
            }

            .pattern-head.hero-analytic .panel-copy {
                color: #dfe7f8;
            }

            .pattern-head .panel-title {
                min-height: 1.9rem;
            }

            .pattern-head .panel-copy {
                min-height: 1.95rem;
                margin-bottom: 0;
            }

            .leaderboard {
                display: grid;
                gap: 0.56rem;
                margin-top: 0.08rem;
            }

            .leaderboard-row {
                display: grid;
                grid-template-columns: 62px minmax(0, 1fr) auto;
                gap: 0.9rem;
                align-items: center;
                border: 1px solid var(--line);
                border-radius: 18px;
                padding: 0.58rem 0.82rem;
                min-height: 58px;
                background:
                    linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015)),
                    rgba(12, 19, 34, 0.92);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            }

            .leaderboard-rank {
                width: 46px;
                height: 46px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: "Space Grotesk", sans-serif;
                font-size: 1rem;
                font-weight: 700;
                color: #eff3fb;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.07);
            }

            .leaderboard-rank.rank-1 {
                background: linear-gradient(135deg, rgba(255, 209, 102, 0.28), rgba(255, 209, 102, 0.08));
                color: #ffe29c;
            }

            .leaderboard-rank.rank-2 {
                background: linear-gradient(135deg, rgba(123, 220, 255, 0.24), rgba(123, 220, 255, 0.08));
                color: #c5f1ff;
            }

            .leaderboard-rank.rank-3 {
                background: linear-gradient(135deg, rgba(255, 95, 162, 0.22), rgba(255, 95, 162, 0.08));
                color: #ffc0da;
            }

            .leaderboard-artist {
                min-width: 0;
            }

            .leaderboard-name {
                font-family: "Space Grotesk", sans-serif;
                font-size: 1rem;
                line-height: 1.05;
                font-weight: 700;
                color: #f5f7fb;
                overflow-wrap: anywhere;
            }

            .leaderboard-meta {
                color: var(--muted);
                font-size: 0.74rem;
                margin-top: 0.08rem;
                line-height: 1.1;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .leaderboard-plays {
                text-align: right;
                white-space: nowrap;
            }

            .leaderboard-plays strong {
                display: block;
                font-family: "Space Grotesk", sans-serif;
                font-size: 1.04rem;
                line-height: 1;
                color: #f5f7fb;
            }

            .leaderboard-plays span {
                color: var(--muted);
                font-size: 0.76rem;
            }

            div[data-testid="stMetric"] {
                border: 1px solid var(--line);
                border-radius: 18px;
                background: rgba(255,255,255,0.03);
                padding: 0.9rem 1rem;
            }

            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                border-radius: 18px;
                overflow: hidden;
            }

            .recent-details {
                margin-top: -0.46rem;
                border-top: 1px solid rgba(255, 255, 255, 0.06);
                padding-top: 0.18rem;
            }

            .recent-details summary {
                list-style: none;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 0.64rem;
                color: #b9c4d8;
                font-size: 0.88rem;
                text-transform: uppercase;
                letter-spacing: 0.14em;
                font-weight: 600;
                user-select: none;
                margin: 0;
                transition: color 180ms ease;
            }

            .recent-details summary:hover {
                color: #eef2fb;
            }

            .recent-details summary::-webkit-details-marker {
                display: none;
            }

            .recent-arrow {
                color: var(--green);
                font-size: 1.15rem;
                font-weight: 700;
                line-height: 1;
                transform: translateY(-1px) rotate(0deg);
                transition: transform 180ms ease;
            }

            .recent-details[open] .recent-arrow {
                transform: translateY(-1px) rotate(90deg);
            }

            .recent-table-wrap {
                margin-top: 0.42rem;
                border: 1px solid var(--line);
                border-radius: 18px;
                overflow: hidden;
                background: var(--panel-strong);
            }

            .recent-mobile-list {
                display: none;
                margin-top: 0.42rem;
                border: 1px solid var(--line);
                border-radius: 18px;
                overflow: hidden;
                background: var(--panel-strong);
            }

            .recent-mobile-item {
                padding: 0.82rem 0.92rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }

            .recent-mobile-item:last-child {
                border-bottom: none;
            }

            .recent-mobile-top {
                display: flex;
                align-items: baseline;
                justify-content: space-between;
                gap: 0.8rem;
                margin-bottom: 0.22rem;
            }

            .recent-mobile-track {
                font-family: "Space Grotesk", sans-serif;
                font-size: 0.98rem;
                line-height: 1.12;
                color: #f4f7fc;
                min-width: 0;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .recent-mobile-time {
                color: var(--muted);
                font-size: 0.72rem;
                white-space: nowrap;
                flex-shrink: 0;
            }

            .recent-mobile-meta {
                color: var(--muted);
                font-size: 0.82rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .recent-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.92rem;
                table-layout: fixed;
            }

            .recent-table thead th {
                text-align: left;
                padding: 0.78rem 0.88rem;
                color: #dce3f4;
                font-weight: 600;
                background: rgba(255, 255, 255, 0.04);
                border-bottom: 1px solid var(--line);
            }

            .recent-table tbody td {
                padding: 0.78rem 0.88rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                color: #eef2fb;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                vertical-align: middle;
            }

            .recent-table tbody tr:last-child td {
                border-bottom: none;
            }

            .recent-table th:nth-child(1),
            .recent-table td:nth-child(1) {
                width: 16%;
            }

            .recent-table th:nth-child(2),
            .recent-table td:nth-child(2) {
                width: 28%;
            }

            .recent-table th:nth-child(3),
            .recent-table td:nth-child(3) {
                width: 18%;
            }

            .recent-table th:nth-child(4),
            .recent-table td:nth-child(4) {
                width: 38%;
            }

            div[data-testid="stElementToolbar"] {
                display: none !important;
            }

            .stButton button {
                border-radius: 999px;
                border: 1px solid rgba(30, 215, 96, 0.32);
                background: linear-gradient(135deg, rgba(30, 215, 96, 0.22), rgba(123, 220, 255, 0.12));
                color: white;
                font-weight: 700;
                padding: 0.55rem 1rem;
            }

            @media (max-width: 1100px) {
                .hero-shell {
                    grid-template-columns: 1fr;
                }

                .hero-title {
                    white-space: normal;
                    font-size: clamp(1.8rem, 6vw, 2.2rem);
                }

                .hero {
                    min-height: unset;
                }

                .snapshot-grid {
                    grid-template-columns: 1fr;
                    gap: 0.86rem;
                    margin-bottom: 0.9rem;
                }

                .hero-profile {
                    justify-content: flex-start;
                    align-items: flex-start;
                }

                .hero-avatar {
                    width: 108px;
                    height: 108px;
                }

                .stat-card {
                    height: 176px;
                }

                .stat-card.compact {
                    min-height: 110px;
                    height: auto;
                }

                .stat-value.long,
                .stat-value.xlong {
                    font-size: clamp(1.45rem, 6vw, 2rem);
                }
            }

            @media (max-width: 720px) {
                .recent-table-wrap {
                    display: none;
                }

                .recent-mobile-list {
                    display: block;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_setting(name, default=None, required=False):
    value = os.getenv(name)
    if value is None:
        try:
            value = st.secrets.get(name)
        except Exception:
            value = None

    if value is None or str(value).strip() == "":
        value = default

    if required and (value is None or str(value).strip() == ""):
        raise RuntimeError(f"Missing required setting: {name}")

    return value


def get_db_config():
    return {
        "host": get_setting("DB_HOST", required=True),
        "database": get_setting("DB_NAME", required=True),
        "user": get_setting("DB_USER", required=True),
        "password": get_setting("DB_PASSWORD", required=True),
        "port": int(get_setting("DB_PORT", default="5432")),
    }


@st.cache_data(ttl=300, show_spinner=False)
def load_history(timezone_name):
    with pg8000.connect(**get_db_config()) as connection:
        history = pd.read_sql_query(
            """
            SELECT track_name, artist, album, played_at, duration_ms
            FROM spotify_history
            ORDER BY played_at DESC;
            """,
            connection,
        )

    if history.empty:
        return history

    history = history.copy()
    history["track_name"] = history["track_name"].fillna("Unknown track")
    history["artist"] = history["artist"].fillna("Unknown artist")
    history["album"] = history["album"].fillna("Unknown album")
    history["duration_ms"] = (
        pd.to_numeric(history["duration_ms"], errors="coerce").fillna(0).astype(int)
    )
    history["played_at_utc"] = pd.to_datetime(
        history["played_at"], utc=True, errors="coerce"
    )
    history = history.dropna(subset=["played_at_utc"]).copy()
    history["played_at_local"] = history["played_at_utc"].dt.tz_convert(timezone_name)
    history["played_date"] = history["played_at_local"].dt.floor("D").dt.tz_localize(
        None
    )
    history["played_hour"] = history["played_at_local"].dt.hour
    history["played_weekday"] = history["played_at_local"].dt.dayofweek
    return history.sort_values("played_at_utc", ascending=False).reset_index(drop=True)


def format_duration(total_duration_ms):
    total_minutes = total_duration_ms // 60000
    hours, minutes = divmod(total_minutes, 60)

    if hours and minutes:
        return f"{hours} hr {minutes} min"
    if hours:
        return f"{hours} hr"
    return f"{minutes} min"


def build_weekly_trend(history, timezone_name, days=7):
    end_date = pd.Timestamp.now(tz=timezone_name).floor("D").tz_localize(None)
    date_index = pd.date_range(end=end_date, periods=days, freq="D")
    daily_duration = (
        history.groupby("played_date")["duration_ms"].sum().reindex(date_index, fill_value=0)
    )
    trend = daily_duration.to_frame(name="total_duration_ms")
    trend["hours"] = (trend["total_duration_ms"] / 3600000).round(2)
    trend.index.name = "date"
    trend = trend.reset_index()
    trend["day_label"] = trend["date"].dt.strftime("%a").str.upper()
    return trend


def build_hourly_energy(history):
    weekday_order = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    frame_index = pd.MultiIndex.from_product(
        [range(7), range(9, 25)], names=["played_weekday", "played_hour"]
    )
    hourly = (
        history.groupby(["played_weekday", "played_hour"])["duration_ms"]
        .sum()
        .reindex(frame_index, fill_value=0)
        .reset_index()
    )
    energy = hourly.copy()
    energy["display_hour"] = energy["played_hour"] % 24
    energy["minutes"] = (energy["duration_ms"] / 60000).round(1)
    energy["day_label"] = energy["played_weekday"].map(lambda idx: weekday_order[idx])
    energy["hour_label"] = pd.to_datetime(
        energy["display_hour"], format="%H"
    ).dt.strftime("%I %p")
    return energy


@st.cache_data(show_spinner=False)
def get_profile_image_uri():
    candidate = Path(__file__).resolve().parent / "assets" / "profile.jpg"
    if not candidate.exists():
        return None

    encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def render_hero(timezone_name):
    profile_image_uri = get_profile_image_uri()
    profile_markup = ""

    if profile_image_uri and spotify_profile_url:
        profile_markup = (
            '<div class="hero-profile">'
            f'<a class="hero-profile-link" href="{spotify_profile_url}" target="_blank" rel="noopener noreferrer" aria-label="Open Spotify profile">'
            f'<img class="hero-avatar" src="{profile_image_uri}" alt="Spotify profile image" />'
            "</a>"
            f'<a class="hero-profile-link profile-copy" href="{spotify_profile_url}" target="_blank" rel="noopener noreferrer" aria-label="Visit Darren Spotify profile">'
            '<span class="hero-profile-cta">Visit My Spotify</span>'
            "</a>"
            "</div>"
        )
    elif profile_image_uri:
        profile_markup = (
            '<div class="hero-profile">'
            f'<img class="hero-avatar" src="{profile_image_uri}" alt="Profile image" />'
            '<span class="hero-profile-cta">Visit My Spotify</span>'
            "</div>"
        )

    hero_markup = (
        '<section class="hero">'
        '<div class="hero-shell">'
        '<div class="hero-copy">'
        '<h1 class="hero-title">Darren\'s Spotify</h1>'
        "<p class=\"hero-subtitle\">"
        "A moodier look at Darren's listening habits, tracing recent plays, long-term artist "
        "gravity, and the hours when his week sounds most alive."
        "</p>"
        '<div class="hero-meta-row">'
        f'<div class="chip">Timezone: {timezone_name}</div>'
        '<span class="hero-meta-separator" aria-hidden="true"></span>'
        '<a class="hero-secondary-link" href="https://github.com/darrenseahjb" target="_blank" rel="noopener noreferrer">Darren&#39;s Portfolio</a>'
        "</div>"
        "</div>"
        f"{profile_markup}"
        "</div>"
        "</section>"
    )

    st.markdown(hero_markup, unsafe_allow_html=True)


def build_stat_card_html(kicker, value, muted_text, compact=False, value_class_override=None):
    compact_class = ""
    if value_class_override is None:
        compact_measure = max(
            len(str(value)),
            max((len(part) for part in str(value).split()), default=0),
        )
        if compact_measure >= 20:
            compact_class = " xlong"
        elif compact_measure >= 12:
            compact_class = " long"
    else:
        compact_class = value_class_override
    card_class = "stat-card compact" if compact else "stat-card"

    return (
        f'<div class="{card_class}">'
        f'<div class="stat-kicker">{html.escape(str(kicker))}</div>'
        f'<div class="stat-value{compact_class}">{html.escape(str(value))}</div>'
        f'<div class="muted">{html.escape(str(muted_text))}</div>'
        f"</div>"
    )


def render_stat_card(kicker, value, muted_text, compact=False, value_class_override=None):
    st.markdown(
        build_stat_card_html(
            kicker,
            value,
            muted_text,
            compact=compact,
            value_class_override=value_class_override,
        ),
        unsafe_allow_html=True,
    )


def render_leaderboard(artists_df):
    medal_map = {1: "01", 2: "02", 3: "03", 4: "04", 5: "05"}
    caption_map = {
        1: "Most replayed artist",
        2: "Still near the top",
        3: "Heavy in rotation",
        4: "Back in the mix",
        5: "Still in the queue",
    }
    rows = []

    for row in artists_df.itertuples(index=False):
        rank = int(row.rank)
        play_count = int(row.play_count)
        play_label = "play" if play_count == 1 else "plays"
        meta = caption_map.get(rank, "A recurring favorite")
        rows.append(
            f'<div class="leaderboard-row">'
            f'<div class="leaderboard-rank rank-{rank}">{medal_map.get(rank, rank)}</div>'
            f'<div class="leaderboard-artist">'
            f'<div class="leaderboard-name">{row.artist}</div>'
            f'<div class="leaderboard-meta">{meta}</div>'
            f"</div>"
            f'<div class="leaderboard-plays">'
            f"<strong>{play_count}</strong>"
            f"<span>{play_label}</span>"
            f"</div>"
            f"</div>"
        )

    st.markdown(
        '<div class="leaderboard">' + "".join(rows) + "</div>",
        unsafe_allow_html=True,
    )


def render_recent_listens(history):
    recent_listens = history[
        ["played_at_local", "track_name", "artist", "album"]
    ].head(20).copy()
    recent_listens["played_at_display"] = recent_listens["played_at_local"].apply(
        lambda ts: f"{ts.day}/{ts.month} {ts.strftime('%I:%M %p')}"
    )
    recent_table_html = (
        recent_listens[["played_at_display", "track_name", "artist", "album"]]
        .rename(columns={"played_at_display": "played_at"})
        .to_html(index=False, classes="recent-table", border=0)
    )
    recent_mobile_rows = []

    for row in recent_listens.itertuples(index=False):
        recent_mobile_rows.append(
            '<div class="recent-mobile-item">'
            '<div class="recent-mobile-top">'
            f'<div class="recent-mobile-track">{html.escape(str(row.track_name))}</div>'
            f'<div class="recent-mobile-time">{html.escape(str(row.played_at_display))}</div>'
            "</div>"
            f'<div class="recent-mobile-meta">{html.escape(f"{row.artist} • {row.album}")}</div>'
            "</div>"
        )

    st.markdown(
        f"""
        <details class="recent-details">
            <summary><span class="recent-arrow">&#9656;</span>Recent Listening</summary>
            <div class="recent-table-wrap">
                {recent_table_html}
            </div>
            <div class="recent-mobile-list">
                {''.join(recent_mobile_rows)}
            </div>
        </details>
        """,
        unsafe_allow_html=True,
    )


inject_styles()

timezone_name = get_setting("APP_TIMEZONE", default="Asia/Singapore")
spotify_profile_url = get_setting("SPOTIFY_PROFILE_URL")

try:
    history = load_history(timezone_name)
except Exception as exc:
    st.error(f"Could not load dashboard data: {exc}")
    st.info(
        "Set DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, and APP_TIMEZONE "
        "through environment variables or Streamlit secrets."
    )
    st.stop()

if history.empty:
    st.warning("The spotify_history table is empty.")
    st.stop()

total_tracks = len(history)
unique_artists = history["artist"].nunique()
total_hours = round(history["duration_ms"].sum() / 3600000, 1)
today_local = pd.Timestamp.now(tz=timezone_name).date()
history_today = history[history["played_at_local"].dt.date == today_local]
total_duration_today = int(history_today["duration_ms"].sum())
today_track_count = len(history_today)
today_track_label = "track" if today_track_count == 1 else "tracks"

latest_track = history.iloc[0]
top_artists = (
    history.groupby("artist")
    .size()
    .reset_index(name="play_count")
    .sort_values(["play_count", "artist"], ascending=[False, True])
    .head(5)
    .reset_index(drop=True)
)
top_artists.insert(0, "rank", range(1, len(top_artists) + 1))
weekly_trend = build_weekly_trend(history, timezone_name)
hourly_energy = build_hourly_energy(history)
peak_day = weekly_trend.loc[weekly_trend["hours"].idxmax()]
peak_day_label = peak_day["date"].strftime("%a").upper()
peak_day_date = peak_day["date"].strftime("%d %b")
peak_day_hours = peak_day["hours"]
peak_day_value = f"{peak_day_label} • {peak_day_hours:.2f} hrs"

st.markdown('<div class="top-grid">', unsafe_allow_html=True)
hero_col, snapshot_col = st.columns([1.38, 1.02], gap="large")

with hero_col:
    render_hero(timezone_name)

with snapshot_col:
    snapshot_cards = [
        build_stat_card_html(
            "Today",
            format_duration(total_duration_today),
            f"{today_track_count} {today_track_label} logged today",
            compact=True,
        ),
        build_stat_card_html(
            "Artists Tracked",
            str(unique_artists),
            f"{total_tracks} total plays logged",
            compact=True,
        ),
    ]

    snapshot_cards.extend(
        [
            build_stat_card_html(
                "Latest Track",
                latest_track["track_name"],
                f"{latest_track['artist']} • {latest_track['played_at_local'].strftime('%d %b, %I:%M %p')}",
                compact=True,
            ),
            build_stat_card_html(
                "Peak Listening Day",
                peak_day_value,
                f"Tracked on {peak_day_date}",
                compact=True,
                value_class_override="",
            ),
        ]
    )
    st.markdown(
        '<div class="snapshot-grid">' + "".join(snapshot_cards) + "</div>",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-label patterns-section">Patterns</div>', unsafe_allow_html=True)

leaderboard_col, weekly_col, hourly_col = st.columns([0.9, 1.16, 0.94], gap="large")

with leaderboard_col:
    st.markdown(
        """
        <div class="panel pattern-head">
            <div class="panel-title">Repeat Artists</div>
            <div class="panel-copy">
                Darren's most replayed artists in his listening history.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_leaderboard(top_artists)

with weekly_col:
    st.markdown(
        """
        <div class="panel pattern-head hero-analytic">
            <div class="panel-title">Weekly Listening Flow</div>
            <div class="panel-copy">
                Darren's clearest listening signal, showing where this week peaked and where it fell quiet.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    weekly_sorted = weekly_trend.copy()
    peak_idx = weekly_sorted["hours"].idxmax()
    weekly_sorted["is_peak"] = weekly_sorted.index == peak_idx
    weekly_sorted["baseline"] = 0.0

    stem = (
        alt.Chart(weekly_sorted)
        .mark_rule(strokeCap="round", strokeWidth=6)
        .encode(
            x=alt.X(
                "day_label:N",
                sort=list(weekly_sorted["day_label"]),
                axis=alt.Axis(title=None, labelColor="#cfd6e6", labelPadding=10, labelAngle=0),
                scale=alt.Scale(paddingOuter=0.35, paddingInner=0.45),
            ),
            y=alt.Y("baseline:Q", axis=alt.Axis(title="Hours", labelColor="#cfd6e6")),
            y2=alt.Y2("hours:Q"),
            color=alt.condition(
                alt.datum.is_peak,
                alt.value("#ffd166"),
                alt.value("#355a7a"),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("hours:Q", title="Hours", format=".2f"),
            ],
        )
    )

    dots = (
        alt.Chart(weekly_sorted)
        .mark_circle(size=220, strokeWidth=2)
        .encode(
            x=alt.X(
                "day_label:N",
                sort=list(weekly_sorted["day_label"]),
                scale=alt.Scale(paddingOuter=0.35, paddingInner=0.45),
            ),
            y=alt.Y("hours:Q", axis=None),
            color=alt.condition(
                alt.datum.is_peak,
                alt.value("#ffd166"),
                alt.value("#7bdcff"),
            ),
            stroke=alt.condition(
                alt.datum.is_peak,
                alt.value("#fff2bf"),
                alt.value("#b8eeff"),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("hours:Q", title="Hours", format=".2f"),
            ],
        )
    )

    labels = (
        alt.Chart(weekly_sorted[weekly_sorted["hours"] > 0])
        .mark_text(
            dy=-16,
            font="DM Sans",
            fontSize=11,
            fontWeight="bold",
            color="#dfe7f8",
        )
        .encode(
            x=alt.X(
                "day_label:N",
                sort=list(weekly_sorted["day_label"]),
                scale=alt.Scale(paddingOuter=0.35, paddingInner=0.45),
            ),
            y=alt.Y("hours:Q"),
            text=alt.Text("hours:Q", format=".2f"),
        )
    )

    weekly_chart = (
        (stem + dots + labels)
        .properties(height=390)
        .configure_view(strokeOpacity=0)
        .configure(background="transparent")
        .configure_axis(gridColor="rgba(255,255,255,0.08)")
    )
    st.altair_chart(weekly_chart, use_container_width=True)

with hourly_col:
    st.markdown(
        """
        <div class="panel pattern-head">
            <div class="panel-title">Listening Hours</div>
            <div class="panel-copy">
                How Darren's listening clusters across the week, hour by hour.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    heatmap = (
        alt.Chart(hourly_energy)
        .mark_rect(cornerRadius=4)
        .encode(
            x=alt.X(
                "display_hour:O",
                sort=list(range(9, 24)) + [0],
                axis=alt.Axis(
                    title=None,
                    labelColor="#cfd6e6",
                    values=[9, 12, 15, 18, 21, 0],
                    labelExpr="datum.value === 0 ? '12AM' : datum.value < 12 ? datum.value + 'AM' : datum.value === 12 ? '12PM' : (datum.value - 12) + 'PM'",
                    labelPadding=8,
                ),
            ),
            y=alt.Y(
                "day_label:N",
                sort=["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
                axis=alt.Axis(title=None, labelColor="#cfd6e6", labelPadding=10),
            ),
            color=alt.Color(
                "minutes:Q",
                scale=alt.Scale(
                    domainMin=0,
                    range=[
                        "#121a2e",
                        "#1b2842",
                        "#214466",
                        "#1ed760",
                    ],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("day_label:N", title="Day"),
                alt.Tooltip("hour_label:N", title="Hour"),
                alt.Tooltip("minutes:Q", title="Minutes", format=".1f"),
            ],
        )
        .properties(height=390)
        .configure_view(strokeOpacity=0)
        .configure(background="transparent")
        .configure_axis(grid=False)
    )
    st.altair_chart(heatmap, use_container_width=True)

render_recent_listens(history)
