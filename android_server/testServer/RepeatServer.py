import socket

server_address = ('localhost', 5000)

doQuit = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(server_address)
    s.listen()
    while not doQuit:
        conn, addr = s.accept()
        with conn:
            print("Connected to: ")
            print (addr)
            data = b''
            while True:
                while True:
                    new_data = conn.recv(1024)
                    if new_data.endswith(b"\n"):
                        data += new_data
                        doQuit = True
                        break
                    else:
                        data += new_data
                if (data == b"q\n"):
                    conn.sendall(b"quit\n")
                    break
                conn.sendall(data)
                print(data)
                data = b''
        print("connection closed")
print("finished")
            
             