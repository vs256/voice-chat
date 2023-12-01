import socket
import threading

class Server:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        while 1:
            try:
                self.port = 5000

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.bind((self.ip, self.port))

                break
            except:
                print("Couldn't bind to that port")

        self.connections = []
        self.accept_connections()

    def accept_connections(self):
        self.s.listen(100)

        print('Running on IP: ' + self.ip)
        print('Running on port: ' + str(self.port))

        while True:
            c, addr = self.s.accept()

            self.connections.append(c)

            threading.Thread(target=self.handle_client, args=(c, addr)).start()

    def broadcast(self, data):
        for client in self.connections:
            try:
                client.sendall(data)
            except:
                pass

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                if not data:
                    # Client disconnected
                    self.connections.remove(c)
                    c.close()
                    break

                self.broadcast(data)

            except socket.error:
                # Client encountered an error
                self.connections.remove(c)
                c.close()
                break

server = Server()
