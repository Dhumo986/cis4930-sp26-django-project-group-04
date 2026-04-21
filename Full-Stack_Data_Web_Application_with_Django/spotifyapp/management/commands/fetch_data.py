import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from spotifyapp.models import Genre, Track, DataRun

DEEZER_SEARCH_URL = "https://api.deezer.com/search"

GENRES = [
    "pop", "rock", "hip-hop", "jazz", "classical",
    "electronic", "r&b", "country", "latin", "metal"
]


class Command(BaseCommand):
    help = 'Fetch track data from the Deezer API and save to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=25,
            help='Number of tracks to fetch per genre (default: 25)',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        run = DataRun.objects.create(status='pending')
        total = 0

        for genre_name in GENRES:
            self.stdout.write(f'Fetching genre: {genre_name} ...')
            index = 0

            while index < limit:
                try:
                    resp = requests.get(
                        DEEZER_SEARCH_URL,
                        params={
                            'q': genre_name,
                            'limit': min(25, limit - index),
                            'index': index,
                        },
                        timeout=10
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    tracks = data.get('data', [])
                    if not tracks:
                        break

                    with transaction.atomic():
                        for item in tracks:
                            genre_obj, _ = Genre.objects.get_or_create(name=genre_name)

                            Track.objects.update_or_create(
                                track_id=str(item['id']),
                                defaults={
                                    'track_name': str(item.get('title', ''))[:255],
                                    'artists': str(item.get('artist', {}).get('name', ''))[:255],
                                    'genre': genre_obj,
                                    'popularity': min(int(item.get('rank', 0)) // 1000, 100),
                                    'danceability': 0.5,
                                    'energy': 0.5,
                                    'tempo': 120.0,
                                    'loudness': -5.0,
                                    'valence': 0.5,
                                    'duration_ms': int(item.get('duration', 0)) * 1000,
                                    'explicit': bool(item.get('explicit_lyrics', False)),
                                    'source': 'api',
                                }
                            )
                            total += 1

                    index += len(tracks)
                    self.stdout.write(f'  Fetched {total} tracks so far...')

                    if len(tracks) < 25:
                        break

                except requests.exceptions.RequestException as e:
                    self.stderr.write(f'Error fetching {genre_name}: {e}')
                    break

        run.status = 'success'
        run.records_fetched = total
        run.save()
        self.stdout.write(self.style.SUCCESS(f'Done! Fetched {total} tracks from Deezer API.'))
