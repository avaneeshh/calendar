from django.shortcuts import render, redirect
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings

def google_calendar_init(request):
    flow = Flow.from_client_config(
        settings.GOOGLE_CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri='http://localhost:8000/google-auth/callback',
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)


def google_calendar_redirect(request):
    state = request.session.pop('oauth_state', '')
    flow = Flow.from_client_config(
        settings.GOOGLE_CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri='http://localhost:8000/google-auth/callback',
    )

    authorization_code = request.GET.get('code')
    absolute_url = request.build_absolute_uri()
    print("Absolute URL:", absolute_url)

    flow.fetch_token(
        authorization_response=request.build_absolute_uri(),
        code=authorization_code,
        state=state,
    )
    credentials = flow.credentials

    # Retrieve the access token
    access_token = credentials.token

    # Store the access token securely for future API calls
    # Add your code here to store the access token securely

    # Use the access token to access the Google Calendar API and get the list of events
    service = build('calendar', 'v3', credentials=credentials)
    events_result = service.events().list(calendarId='primary', maxResults=10).execute()
    events = events_result.get('items', [])

    # Render a template with the list of events
    return render(request, 'events.html', {'events': events})
