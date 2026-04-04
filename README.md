# Spotify Listening Analytics Dashboard

Public Streamlit dashboard for the Spotify Listening Analytics project.

## Quick Links

- Live Demo: [Spotify Listening Analytics](https://spotify-listening-analytics.streamlit.app/)
- Source Code: [Spotify Listening Analytics Pipeline](https://github.com/darrenseahjb/spotify)
- Dashboard Repo: [spotify-streamlit-dashboard](https://github.com/darrenseahjb/spotify-streamlit-dashboard)

## What This Repo Is

This is the presentation-layer repo.

It reads listening history from `spotify_history` and turns it into a public dashboard focused on:
- current listening activity
- repeat artists
- weekly listening rhythm
- day/hour listening patterns

The emphasis here is UI, metric framing, and visual hierarchy rather than ingestion logic.

## Repo Split

This dashboard used to sit alongside the ingestion code in the main project repo.

It now lives separately on purpose:
- this repo owns the public dashboard experience and Streamlit deployment
- the main pipeline repo owns Spotify ingestion, scheduling, schema, and storage

That split keeps the public-facing app smaller and easier to iterate on without mixing it back into the AWS pipeline code.

## Why This Exists Separately

The dashboard changed faster than the ingestion code.

Keeping it in its own repo made it easier to iterate on:
- layout and styling
- chart design
- mobile behavior
- Streamlit Community Cloud deployment

## Stack

- Python
- Streamlit
- PostgreSQL
- Altair

## Repository Guide

- `app.py`
  Main Streamlit application, including layout, styling, queries, transforms, and charts.
- `requirements.txt`
  Runtime dependencies for the Streamlit deployment.
- `.streamlit/secrets.toml.example`
  Template for the dashboard's runtime secrets.

## What the Dashboard Shows

- hero section with identity and project context
- compact KPI cards for current activity and summary metrics
- repeat-artist leaderboard
- weekly listening trend
- weekly/hourly listening heatmap
- recent listening log

## Tradeoffs and Limitations

- The dashboard reads directly from PostgreSQL for simplicity. That is acceptable for a personal demo, but it is not the strongest architecture for a production-facing analytics product.
- The app is built in one Streamlit entry file, which is practical for a portfolio project but less ideal for long-term team maintenance.
- The quality of the insights depends on the depth of collected history. With shallow history, the visuals are still useful, but less representative.

## Streamlit Community Cloud Settings

- Repository: this repo
- Branch: `main`
- Main file path: `app.py`
- Python version: `3.11`

## Required Secrets

Copy `.streamlit/secrets.toml.example` into Streamlit Community Cloud secrets and replace the placeholder values.

Expected keys:
- `DB_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_PORT`
- `APP_TIMEZONE`
- `SPOTIFY_PROFILE_URL`

## Related Repository

- [Spotify Listening Analytics Pipeline](https://github.com/darrenseahjb/spotify)
