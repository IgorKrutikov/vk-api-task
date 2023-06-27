import json
import socket
import ssl


def get_host_and_port():
    return "api.vk.com", 443


def request(_socket, request):
    _socket.send((request + '\n').encode())
    _socket.settimeout(1)
    recv_data = _socket.recv(255)
    while True:
        try:
            buf = _socket.recv(255)
            recv_data += buf
        except socket.timeout:
            break
    return recv_data.decode()


def prepare_message(data: dict):
    message = data['method'] + ' ' + data['url'] + '?'

    parameters = '&'.join(
        (f'{arg}={value}' for arg, value in data['get_params'].items()))
    message += parameters

    message += ' ' + 'HTTP/' + data['version'] + '\n'
    for header, value in data['headers'].items():
        message += f'{header}: {value}\n'
    message += '\n'

    return message


def get_friends(token, user):
    HOST, PORT = get_host_and_port()

    request_data = {
        'method': 'GET',
        'url': '/method/friends.get',
        'get_params': {
            'access_token': f"{token}",
            'user_id': f"{user}",
            'fields': 'nickname',
            'v': '5.131',
        },
        'version': '1.1',
        'headers': {'host': HOST},
    }

    ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_contex.check_hostname = False
    ssl_contex.verify_mode = ssl.CERT_NONE

    with socket.create_connection((HOST, PORT)) as sock:
        with ssl_contex.wrap_socket(sock, server_hostname=HOST) as client:
            return [f"{friend['first_name']} {friend['last_name']}" for friend in
                        json.loads(request(client, prepare_message(request_data)).split('\r\n').pop())['response'][
                            'items']]

def main():
    with open("settings.json") as f:
        settings = json.load(f)
        app_access_token = settings["ACCESS_TOKEN"]

    user = input("Введите идентификатор пользователя: ")
    for friend in get_friends(app_access_token, user):
        print(friend, end='\n')


if __name__ == '__main__':
    main()
