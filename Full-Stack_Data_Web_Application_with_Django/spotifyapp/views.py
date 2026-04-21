from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.views.decorators.http import require_POST
from .models import Track, Genre, DataRun


@staff_member_required
@require_POST
def fetch_data_view(request):
    call_command('fetch_data', limit=25)
    return redirect('/')
