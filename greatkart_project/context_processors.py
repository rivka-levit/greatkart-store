from .secrets import app_client_id


def client(request):
    client_id = app_client_id
    return dict(clientID=client_id)
