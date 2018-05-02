# import socket
#
# target_host = "www.duckduckgo.com"
# target_port = 443
#
# # create a socket object
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# # connect the client
# client.connect((target_host, target_port))
#
# # send some data
# client.send("GET / HTTPS/1.1\r\nHost: duckduckgo.com\r\n\r\n")
#
# # receive some data
# response = client.recv(4096)
#
# print(response)
import socket

target_host = "127.0.0.1"
target_port = 9999

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# send some data
client.send("test")

# receive some data
response = client.recv(4096)

print(response)
