from decouple import config


def client(request):
    client_id = config('app_client_id')
    return dict(clientID=client_id)
