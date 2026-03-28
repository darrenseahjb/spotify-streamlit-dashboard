# Spotify Listening Analytics Dashboard

Public-facing Streamlit dashboard for the Spotify Listening Analytics project.

## Quick Links

- Live Demo: [Spotify Listening Analytics](https://spotify-listening-analytics.streamlit.app/)
- Source Code: [Spotify Listening Analytics Pipeline](https://github.com/darrenseahjb/spotify)
- Dashboard Repo: [spotify-streamlit-dashboard](https://github.com/darrenseahjb/spotify-streamlit-dashboard)

## Overview

This is the frontend repo.

It reads from `spotify_history` and turns listening logs into a live dashboard focused on current activity, repeat artists, weekly flow, and listening-hour patterns.

## Stack

- Python
- Streamlit
- PostgreSQL
- `Altair`

## What Makes This Repo Different

This repo is focused on:
- dashboard UX
- visual hierarchy
- metric presentation
- chart design
- public deployment

## Repository Guide

- `app.py`
  Main Streamlit dashboard application.
- `requirements.txt`
  Python dependencies for the public dashboard deployment.
- `.streamlit/secrets.toml.example`
  Template for the dashboard's runtime secrets.

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

## Dashboard Focus

The dashboard is designed to feel less like a default analytics page and more like a small music product:
- a hero section with identity and context
- compact KPI cards
- a ranked repeat-artist module
- a dominant weekly behavior chart
- supporting hour-pattern analysis

## Related Repository

- [Spotify Listening Analytics Pipeline](https://github.com/darrenseahjb/spotify)
