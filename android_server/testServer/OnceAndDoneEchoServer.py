import socket

server_address = ('localhost', 5000)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(server_address)
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected to: ")
        print (addr)
        data = b''
        while True:
            new_data = conn.recv(1024)
            if new_data.endswith(b"\n"):
                data += new_data
                break
            else:
                data += new_data
        conn.sendall(data)
        print(data)
    print("connection closed")
print("finished")
            
             