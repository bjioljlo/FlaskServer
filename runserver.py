import server
from server.router import Router


if __name__ == '__main__':
    server.server_flask.run(debug=True)

