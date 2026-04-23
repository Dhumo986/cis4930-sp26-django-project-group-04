import json

import pandas as pd
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import TrackForm
from .models import Track


def track_list_view(request):
    query = request.GET.get('q', '').strip()
    tracks = Track.objects.select_related('genre').all()

    if query:
        tracks = tracks.filter(
            Q(track_name__icontains=query) | Q(artists__icontains=query)
        )

    context = {
        'tracks': tracks[:200],
        'query': query,
        'total_count': tracks.count(),
    }
    return render(request, 'spotifyapp/list.html', context)


def analytics_view(request):
    rows = list(
        Track.objects.select_related('genre').values(
            'genre__name',
            'popularity',
            'energy',
            'danceability',
            'explicit',
        )
    )

    if not rows:
        context = {
            'chart_json': json.dumps(
                {
                    'popularity_by_genre': {'labels': [], 'values': []},
                    'explicit_popularity': {'labels': ['Non-Explicit', 'Explicit'], 'values': [0, 0]},
                }
            ),
            'energy_dance_by_genre': [],
            'summary_stats': [],
        }
        return render(request, 'spotifyapp/analytics.html', context)

    df = pd.DataFrame(rows)

    # P1 RQ1: average popularity by genre
    pop_by_genre = (
        df.groupby('genre__name', as_index=False)['popularity']
        .mean()
        .sort_values('popularity', ascending=False)
    )

    # P1 RQ2: average energy + danceability by genre
    energy_dance = (
        df.groupby('genre__name', as_index=False)[['energy', 'danceability']]
        .mean()
        .sort_values('energy', ascending=False)
    )

    # P1 RQ4: explicit vs non-explicit popularity
    explicit_popularity = (
        df.groupby('explicit', as_index=False)['popularity']
        .mean()
        .sort_values('explicit')
    )

    # Summary stats table for popularity + energy
    summary_stats_df = df[['popularity', 'energy']].agg(['count', 'mean', 'min', 'max']).round(3)

    chart_payload = {
        'popularity_by_genre': {
            'labels': pop_by_genre['genre__name'].tolist(),
            'values': [round(v, 2) for v in pop_by_genre['popularity'].tolist()],
        },
        'explicit_popularity': {
            'labels': ['Non-Explicit', 'Explicit'],
            'values': [
                round(
                    float(
                        explicit_popularity.loc[
                            explicit_popularity['explicit'] == False, 'popularity'
                        ].mean()
                    )
                    if (explicit_popularity['explicit'] == False).any()
                    else 0,
                    2,
                ),
                round(
                    float(
                        explicit_popularity.loc[
                            explicit_popularity['explicit'] == True, 'popularity'
                        ].mean()
                    )
                    if (explicit_popularity['explicit'] == True).any()
                    else 0,
                    2,
                ),
            ],
        },
    }

    summary_stats = []
    for metric in ['popularity', 'energy']:
        summary_stats.append(
            {
                'metric': metric,
                'count': int(summary_stats_df.loc['count', metric]),
                'mean': float(summary_stats_df.loc['mean', metric]),
                'min': float(summary_stats_df.loc['min', metric]),
                'max': float(summary_stats_df.loc['max', metric]),
            }
        )

    context = {
        'chart_json': json.dumps(chart_payload),
        'energy_dance_by_genre': energy_dance.round(3).to_dict(orient='records'),
        'summary_stats': summary_stats,
    }
    return render(request, 'spotifyapp/analytics.html', context)


@staff_member_required
@require_POST
def fetch_data_view(request):
    call_command('fetch_data', limit=25)
    return redirect('/')


def home(request):
    stats = {
        'total_tracks': Track.objects.count(),
    }
    return render(request, 'spotifyapp/home.html', {'stats': stats})


def track_list(request):
    tracks = Track.objects.select_related('genre').all()
    paginator = Paginator(tracks, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'spotifyapp/records_list.html', {'page_obj': page_obj})


def track_detail(request, pk):
    track = get_object_or_404(Track.objects.select_related('genre'), pk=pk)
    return render(request, 'spotifyapp/detail.html', {'track': track})


def track_create(request):
    form = TrackForm(request.POST or None)
    if form.is_valid():
        track = form.save()
        return redirect(reverse('track_detail', args=[track.pk]))
    return render(request, 'spotifyapp/form.html', {'form': form, 'action': 'Add Track'})


def track_update(request, pk):
    track = get_object_or_404(Track, pk=pk)
    form = TrackForm(request.POST or None, instance=track)
    if form.is_valid():
        form.save()
        return redirect(reverse('track_detail', args=[track.pk]))
    return render(request, 'spotifyapp/form.html', {'form': form, 'action': 'Edit Track', 'track': track})


def track_delete(request, pk):
    track = get_object_or_404(Track, pk=pk)
    if request.method == 'POST':
        track.delete()
        return redirect('track_list')
    return render(request, 'spotifyapp/confirm_delete.html', {'track': track})


from django.http import JsonResponse

def api_records(request):
    genre = request.GET.get('genre', '').strip()
    tracks = Track.objects.select_related('genre').all()

    if genre:
        tracks = tracks.filter(genre__name__icontains=genre)

    tracks = tracks[:100]

    data = [
        {
            'id': t.id,
            'track_name': t.track_name,
            'artists': t.artists,
            'genre': t.genre.name,
            'popularity': t.popularity,
            'danceability': t.danceability,
            'energy': t.energy,
            'tempo': t.tempo,
            'loudness': t.loudness,
            'valence': t.valence,
            'duration_ms': t.duration_ms,
            'explicit': t.explicit,
            'source': t.source,
        }
        for t in tracks
    ]

    return JsonResponse({'count': len(data), 'results': data})
