import sys, socket, getopt, threading, subprocess

# Globals
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("BHP netcat tool\n")
    print("Usage: netcat.py -t target_host -p port")
    print("-l --listen                  - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run     - execute the given file upon receiving a connection")
    print("-c --command                 - initialize a command shell")
    print("-u --upload=destination      - upload a file and write to [destination] upon receiving connection\n\n")
    print("Examples:")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -c")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -u=C:\\target.exe")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./netcat.py -t 192.168.11.12 -p 135")
    sys.exit(0)


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:
            # wait for data response
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response)

            # wait for more input
            buffer = raw_input("")
            buffer += "\n"

            # send buffer
            client.send(buffer)

    except:
        print("[*] Exception! Exiting.")

        # close the connection
        client.close()


def server_loop():
    global target

    # if no target is defined, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((target, port))
        server.listen(5)

        while True:
            client_socket, addr = server.accept()
            # spin off a new thread to handle the socket
            client_thread = threading.Thread(target=client_handler, args=(client_socket,))
            client_thread.start()


def run_command(command):
    # trim newline from 'command'
    command = command.rstrip()

    # run the command and get the output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

    except:
        output = "Failed to execute command.\r\n"

    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # check for upload
    if len(upload_destination):

        # read in all the bytes and write to our destination
        file_buffer = ""

        # read available data
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            else:
                file_buffer += data

        # write the bytes to a file
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # acknowledge file written successfully
            client_socket.send("Succcessfully saved the file to %s\r\n" % upload_destination)

        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    # check for command execution
    if len(execute):

        # run command
        output = run_command(execute)
        client_socket.send(output)

    # loop if command shell was requested
    if command:

        while True:
            # show a simple prompt
            client_socket.send("<:#> ")

            # receive until newline
            cmd_buffer = ""
            while not "\n" in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # send back the command output
            response = run_command(cmd_buffer)

            # send back the response
            client_socket.send(response)


def main():
    global listen
    global command
    global upload
    global execute
    global target
    global upload_destination
    global port

    if not len(sys.argv[1:]):
        usage()

    # read in commands
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])

    except getopt.GetoptError as err:
        print(str(err))
        usage()


    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # listen or just send data from stdin??
    if not listen and len(target) and port > 0:

        # read in the buffer from commandline
        # this will block, send CTRL-D if not sending input to stdin
        buffer = sys.stdin.read()

        # send data
        client_sender(buffer) # need to create function definition

    # listen and potentially upload data, execute commands, and drop shell back depending on options
    if listen:
        server_loop() # need to create function definition



if __name__ == "__main__":
    main()
