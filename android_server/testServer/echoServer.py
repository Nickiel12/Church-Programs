import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('10.0.0.170', 5000)
print("binding socket")
my_socket.bind(server_address)

my_socket.setblocking(True)

my_socket.listen(1)

while True:
    print("in the loop!")
    connection, address = my_socket.accept()
    infile = my_socket.makefile()
    print("connection from: ", address)
    data = b''
    print("ding")
    while True:
        print("dong")
        new_data = connection.recv(4096)
        
        if (new_data.endswith(b'\n')):
            data += new_data
            break
        else:
            data += new_data

    data = data.strip(b'\n')
    
    if data == b'close':
        break

    print(data)
    print("done!")

connection.close()