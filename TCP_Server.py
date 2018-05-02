import socket, threading, time

bind_IP = "0.0.0.0"
bind_Port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_IP, bind_Port))

server.listen(5)

print("[*] Listening on %s:%d" % (bind_IP, bind_Port))


# client handling thread
def handle_Client(client_socket):
    # get data from client
    request = client_socket.recv(1024)
    print("[*] Received: %s" %request)

    # send back a packet
    response = 'ACK ' + str(time.time()) + '\n\n'
    client_socket.send(response)

    client_socket.close()


while True:

    client, address = server.accept()
    print("[*] Connection accepted from: %s:%d" %(address[0], address[1]))

    # spin up client thread to handle incoming data
    client_handler = threading.Thread(target=handle_Client, args=(client,))
    client_handler.start()
