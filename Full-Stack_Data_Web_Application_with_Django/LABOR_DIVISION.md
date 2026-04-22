# 👥 Labor Division — Group 04

**Project:** Full-Stack Data Web Application with Django  
**Course:** CIS 4930 — Introduction to Python | Spring 2026  
**Team:** Dhruv Upadhyay, Thomas Schmidt, Imran Ahmed

---

## 📋 Task Overview

| Branch | Person | Status |
|--------|--------|--------|
| `models-orm` | Dhruv | ✅ Done |
| `settings-deploy` | Dhruv | ✅ Done |
| `api-integration` | Dhruv | ⏳ In Progress |
| `crud-views` | Thomas | ✅ Done |
| `bootstrap-ui` | Thomas | ⏳ In Progress |
| `analytics-dashboard` | Imran | ❌ Not Started |
| Search bar bonus | Imran | ❌ Not Started |

---

## 🟢 Dhruv Upadhyay — Models, Settings, API

### ✅ Completed
- `spotifyapp/models.py` — `Track`, `Genre`, `DataRun` models with ForeignKey, validators, choices
- `spotifyapp/migrations/` — migrations tracked
- `spotifyapp/admin.py` — Admin customized with `list_display`, `search_fields`, `list_filter`
- `spotifyapp/management/commands/seed_data.py` — loads `data/raw/spotify_tracks.csv` into DB
- `config/settings/base.py`, `dev.py`, `prod.py` — split settings with python-decouple
- `.env.example`, `Procfile`, `runtime.txt`, `requirements.txt`

### ⏳ Remaining
- `spotifyapp/management/commands/fetch_data.py` — API fetch command
- `/fetch/` view — POST-only, staff-only trigger for fetch_data
- Railway deployment + live URL in README

---

## 🔵 Thomas Schmidt — Views, URLs, Bootstrap UI

### Branch: `crud-views` + `bootstrap-ui`

### ✅ Completed (`crud-views`)
- `spotifyapp/forms.py` — `TrackForm` (ModelForm, Bootstrap-styled widgets via `__init__`)
- `spotifyapp/views.py` — `home`, `track_list` (paginated 20/page), `track_detail`, `track_create`, `track_update`, `track_delete`
- `spotifyapp/urls.py` — all 6 CRUD routes wired; Imran's search view preserved at `/search/`

### ⏳ In Progress (`bootstrap-ui`)
- `spotifyapp/templates/spotifyapp/base.html` — Bootstrap 5 CDN, responsive navbar, blocks
- `spotifyapp/templates/spotifyapp/home.html` — extends base, Bootstrap card
- `spotifyapp/templates/spotifyapp/records_list.html` — extends base, `table-striped table-hover`, Paginator controls
- `spotifyapp/templates/spotifyapp/detail.html` — extends base, info card
- `spotifyapp/templates/spotifyapp/form.html` — extends base, shared by create/update
- `spotifyapp/templates/spotifyapp/confirm_delete.html` — extends base, Bootstrap alert
- `spotifyapp/static/css/style.css` — 5+ overrides (navbar, brand accent, card shadow, row hover, pagination)
- **Remaining:** Imran's `list.html` and `analytics.html` do not yet extend `base.html` — left untouched to avoid overwriting his work; needs a merge-conversation before conversion

### What you need to build:

**`spotifyapp/views.py`** — implement these views:
- `home` → `/` — homepage with dataset description and nav links
- `track_list` → `/records/` — paginated list (20 per page) using Django `Paginator`
- `track_detail` → `/records/<pk>/` — single track detail using `get_object_or_404`
- `track_create` → `/records/add/` — ModelForm with validation
- `track_update` → `/records/<pk>/edit/` — update form
- `track_delete` → `/records/<pk>/delete/` — confirmation page

**`spotifyapp/urls.py`** — wire up all 6 URLs above

**`spotifyapp/forms.py`** — `TrackForm` using `ModelForm` for `Track`

**`spotifyapp/templates/spotifyapp/`** — create these templates:
- `base.html` — Bootstrap 5 CDN, responsive navbar, block tags
- `home.html` — extends base, Bootstrap card component
- `list.html` — extends base, `table-striped table-hover`, pagination controls
- `detail.html` — extends base, track info in a card
- `form.html` — extends base, Bootstrap form classes
- `confirm_delete.html` — extends base, delete confirmation
- `analytics.html` — extends base (Imran will fill the chart content)

**`spotifyapp/static/css/style.css`** — at least 5 meaningful CSS overrides

### Models reference (already defined by Dhruv):
```python
# Track fields available to you:
track_id, track_name, artists, genre (FK to Genre),
popularity, danceability, energy, tempo, loudness,
valence, duration_ms, explicit, source, created_at
```

### How to get started:
```bash
git fetch --all
git checkout -b crud-views
cd Full-Stack_Data_Web_Application_with_Django
export DJANGO_SETTINGS_MODULE=config.settings.dev
python3 manage.py runserver
```

---

## 🟡 Imran Ahmed — Analytics Dashboard + Search

### Branch: `analytics-dashboard`

### What you need to build:

**`spotifyapp/views.py`** — add `analytics` view at `/analytics/`:
- Use `pandas` to compute at least 3 aggregations from the DB:
  1. Average popularity by genre (answers P1 Research Question 1)
  2. Average energy and danceability by genre (answers P1 Research Question 2)
  3. Explicit vs non-explicit popularity comparison (answers P1 Research Question 4)
- Render at least 2 Chart.js charts:
  - Bar or line chart (popularity by genre)
  - Pie or doughnut chart (explicit vs non-explicit)
- Summary stats table: count, mean, min, max for `popularity` and `energy`

**`spotifyapp/templates/spotifyapp/analytics.html`** — Chart.js charts using `{{ chart_json|safe }}`

**Search bar bonus** — add `?q=` GET filter on the list view:
- Filter by `track_name` or `artists` using Django `Q` objects
- Add a search input to `list.html`

### P1 Research Questions to reuse:
1. What audio features are most strongly correlated with popularity?
2. Which genres have the highest average energy and danceability?
3. How has tempo distribution changed over release years?
4. Do explicit tracks score higher in popularity than non-explicit ones?

### How to get started:
```bash
git fetch --all
git checkout -b analytics-dashboard
cd Full-Stack_Data_Web_Application_with_Django
pip3 install pandas
export DJANGO_SETTINGS_MODULE=config.settings.dev
python3 manage.py runserver
```

### Example analytics view pattern:
```python
import json
import pandas as pd
from django.shortcuts import render
from .models import Track

def analytics(request):
    qs = Track.objects.values('genre__name', 'popularity', 'energy', 'danceability', 'explicit')
    df = pd.DataFrame(list(qs))

    # Aggregation 1 — avg popularity by genre
    pop_by_genre = df.groupby('genre__name')['popularity'].mean().sort_values(ascending=False).head(10)
    chart_data = {
        'labels': pop_by_genre.index.tolist(),
        'values': pop_by_genre.values.tolist(),
    }

    return render(request, 'spotifyapp/analytics.html', {
        'chart_json': json.dumps(chart_data),
    })
```

---

## 🔁 Dependency Order

```
Dhruv finishes models-orm (DONE)
    → Thomas starts crud-views NOW
    → Imran starts analytics-dashboard NOW
Dhruv finishes api-integration
    → Imran wires fetch results into analytics
Thomas finishes crud-views
    → Imran adds search bar on list view
Dhruv does Railway deploy last
```

---

## 🚀 Setup Instructions (everyone)

```bash
git clone https://github.com/Dhumo986/cis4930-sp26-project-group-04.git
cd cis4930-sp26-project-group-04/Full-Stack_Data_Web_Application_with_Django
pip3 install -r requirements.txt
cp .env.example .env
# Edit .env and add a SECRET_KEY
export DJANGO_SETTINGS_MODULE=config.settings.dev
python3 manage.py migrate
python3 manage.py seed_data --limit 2000
python3 manage.py runserver
```

---

## 📅 Suggested Timeline

| Day | Goal |
|-----|------|
| Today | Thomas + Imran clone repo and start their branches |
| Day 2 | Thomas: all 6 views + templates working; Imran: analytics view + 2 charts |
| Day 3 | Thomas: Bootstrap UI polished; Imran: search bar done |
| Day 4 | Dhruv: fetch_data done + Railway deploy; everyone: final polish |
| Day 5 | README screenshots, `manage.py check --deploy`, final push |
