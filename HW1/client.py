import socket
import mycrypt

SERVER_HOST = '192.168.100.6'   # The server's hostname or IP address
SERVER_PORT = 65432             # The port used by the server

TRANS_HOST = '192.168.100.6'
TRANS_PORT = 65431

trans_key = None
trans_iv = None

trans_enc = None
trans_dec = None

buffer_size = 1<<16

def debug(var_name):
    instr = "print(f'Debug: " + f"{var_name}" +" = {" + f"{var_name}" +"}')"
    exec(instr)

def debug_msg(txt):
    #print("Debug: " + txt)
    pass

def send_message(message, sock, enc = None):

    if enc is None:
        sock.sendall(bytes(message,'ascii'))
    elif enc is 'default':
        sock.sendall(mycrypt.enc_aes(message))
    elif enc is 'cbc':
        sock.sendall(mycrypt.enc_cbc(message,trans_key,trans_iv))    
    elif enc is 'cfb':
        sock.sendall(mycrypt.enc_cfb(message,trans_key,trans_iv))
    else:
        raise ValueError("No suitable enc form")    

def get_command():

    msg = input("Introduce next command: ")

    if msg == 'end':
        fin = True

    else:
        fin = False

    return msg, fin

def receive_key_iv(sock, mode):

    global trans_key, trans_iv, trans_enc, trans_dec

    sock.sendall(b'get key')
    cr_key = sock.recv(128)
    # debug_msg("cr_key")
    # print(cr_key)
    # print(len(cr_key))

    sock.sendall(b'get iv')
    cr_iv = sock.recv(128)
    # debug_msg("cr_iv")
    # print(cr_iv)
    # print(len(cr_iv))

    trans_key = mycrypt.dec_aes(cr_key)
    trans_iv = mycrypt.dec_aes(cr_iv)
    debug_msg("le-am decriptat")

    enc_func = mycrypt.enc_cbc if mode is 'cbc' else mycrypt.enc_cfb
    dec_func = mycrypt.dec_cbc if mode is 'cbc' else mycrypt.dec_cfb
    trans_enc = lambda x: enc_func(x,trans_key,trans_iv)
    trans_dec = lambda x: dec_func(x,trans_key,trans_iv)

    confirm = trans_enc(mycrypt.confirmation_message)

    sock.sendall(confirm)
    ans = sock.recv(128)

    return ans

def upload_file(confirm_sock):

    us = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    us.connect((TRANS_HOST,TRANS_PORT))

    print("Successfully connected to peer")
    f = None
    while f is None:
        try:
            filename = input("Enter a filename to send to peer: ")
            f = open(filename,"rb")
        except:
            print("Not good!")
            f = None

    dec_file = f.read()

    dec_size = len(dec_file)//16 + 1

    enc_file = trans_enc(dec_file)

    enc_size = len(enc_file).to_bytes(8,'big')
    enc_enc_size = trans_enc(enc_size)

    us.sendall(enc_enc_size)
    confirm = us.recv(128)
    if confirm == b'no':
        print("peer refused the file")
        return -1

    us.sendall(enc_file)
    confirm_sock.sendall(bytes(f"size {dec_size}",'ascii'))

    return dec_size

def download_file(confirm_sock):

    ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ds.bind( (TRANS_HOST,TRANS_PORT) )
    ds.listen(1)
    confirm_sock.sendall(b'start')
    peer_s, peer_add = ds.accept()

    next_size_cr = peer_s.recv(128)
    next_size = int.from_bytes(trans_dec(next_size_cr),'big')

    ans = input(f"The size of the encrypted file is {next_size} bytes\nDo you wish to continue? (y/n) ")

    if 'n' in ans or 'N' in ans:
        print("Connection with peer aborted")
        peer_s.sendall(b'no')
        peer_s.close()
        return -1

    filename = None
    f = None

    while f is None:
        try:
            filename = input("Type a name for your file: ")
            f = open(filename,"wb")
        except:
            print("Not okay!")
            f = None

    peer_s.sendall(b'yes')
    enc_file = peer_s.recv(next_size + 128)
    peer_s.close()
    ds.close()

    dec_file = trans_dec(enc_file)
    print("content of file:")
    try:
        if len(dec_file) <= 100:
            print(dec_file.decode('ascii'))
        else:
            print(dec_file[:50].decode('ascii'))
            print("...")
            print(dec_file[-50:].decode('ascii'))
    except:
        print("File is not ascii-encoded, cannot display preview")

    f.write(dec_file)
    f.close()

    print("Saved successfully")

    return len(dec_file)//16 + 1

def process_message(msg,sock):

    msg = msg.decode('ascii')

    de_afisat = msg

    debug_msg("Am primit mesajul " + msg)

    if msg == 'cbc' or msg == 'cfb':
        debug_msg("Incepem receive key iv")
        ans = receive_key_iv(sock,msg)
        if ans == b'start':
            debug_msg("Am primit ans = start, incepem download")
            size = download_file(confirm_sock = sock)
            print("Message from server: " + sock.recv(128).decode('ascii'))
            sock.sendall(bytes(f"size {size}",'ascii'))
            de_afisat = sock.recv(128).decode('ascii')
        elif ans == b'send_data':
            debug_msg("Am primit ans = send_data, incepem upload")
            size = upload_file(confirm_sock = sock)
            de_afisat = sock.recv(128).decode('ascii')
            

    return "Message from server: " + de_afisat

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER_HOST, SERVER_PORT))

    fin = False    
    while not fin:

        r_msg = s.recv(buffer_size)

        de_afisat = process_message(r_msg,s)

        print(de_afisat)
        #print(f"Message from server: {r_msg.decode('ascii')}")

        msg, fin = get_command()
        send_message(msg,s)
