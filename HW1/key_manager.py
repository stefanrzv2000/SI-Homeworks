import socket
import mycrypt
import threading
import time
import secrets

HOST = '1127.0.0.1' # Standard loopback interface address (localhost)
PORT = 65432           # Port to listen on (non-privileged ports are > 1023)

buffer_size = 1<<16
threads = []
client_count = 0 
waiting = []
client_info = dict()

keys = dict()
ivs = dict()

def get_new_key(length = 16):

    return secrets.token_bytes(length)

def get_new_iv(length = 16):

    return secrets.token_bytes(length)

def get_key(id1,id2,mode):

    if (id1,id2,mode) not in keys:
        keys[(id1,id2,mode)] = get_new_key()
    
    return keys[(id1,id2,mode)]

def get_iv(id1,id2,mode):

    if (id1,id2,mode) not in ivs:
        ivs[(id1,id2,mode)] = get_new_iv()
    
    return ivs[(id1,id2,mode)]

class cinfo:
    
    def __init__(self,tid,addr):
        global client_info
        
        self.id = tid
        self.addr = addr
        client_info[tid] = self
        self.waiting = False
        self.listening = None
        self.mode = None
        self.peer = None
        self.received = 0
        self.started = 0
        self.size = None

def get_waiters_list():

    global waiting

    if len(waiting) == 0:
        return "No waiters at the moment. Try again later."
    else:
        ans = "select a peer to send a message\nyour next command should be 'conn <peer_id> <enc_mode>\nlist of available waiters:\n"
        for w in waiting:
            ans += str(w) + "\n"
        return ans

def get_waiting(message,tid,sock):

    _,peer_id,mode = message.split(" ")

    peer_id = int(peer_id)

    client_info[peer_id].mode = mode
    client_info[peer_id].peer = tid
    client_info[tid].peer = peer_id

    ans = send_key_iv(tid,peer_id,mode,sock)

    if ans == 'key okay':
        client_info[tid].received = 1
    else:
        client_info[tid].received = -1
        return bytes(ans,'ascii')

    while client_info[peer_id].started == 0:
        time.sleep(1)

    if client_info[peer_id].started < 0:
        return b'peer error'

    return b'send_data'


def send_key_iv(id1,id2,mode,sock):

    dec_func = mycrypt.dec_cbc if mode is 'cbc' else mycrypt.dec_cfb

    key = get_key(id1,id2,mode)
    iv = get_iv(id1,id2,mode)

    sock.sendall(bytes(mode,'ascii'))
    sock.recv(128)
    #print("key",key)
    sock.sendall(mycrypt.enc_aes(key))
    sock.recv(128)
    sock.sendall(mycrypt.enc_aes(iv))

    confirm = sock.recv(1024)
    confirm = dec_func(confirm,key,iv)

    if confirm == mycrypt.confirmation_message:
        ans = 'key okay'
    else:
        ans = 'key error'

    return ans

def wait_for_peer(tid,sock):

    while client_info[tid].mode is None or client_info[tid].peer is None:
        time.sleep(1)

    mode = client_info[tid].mode
    peer = client_info[tid].peer

    ans = send_key_iv(peer,tid,mode,sock)

    if ans == 'key okay':
        client_info[tid].received = 1
    else:
        client_info[tid].received = -1
        client_info[tid].started = -1
        return bytes(ans,'ascii')

    while client_info[peer].received == 0:
        time.sleep(10)

    if client_info[peer].received < 0:
        return b'peer key error'
    
    sock.send(b'start')
    confirm = sock.recv(1024)
    if confirm == b'start':
        client_info[tid].started = 1
    else:
        client_info[tid].started = -1

    return b'I will notify your peer'

def compare_size(msg,tid):

    #print("Comparing size:",msg)
    _,sz = msg.split(" ")
    sz = int(sz)

    client_info[tid].size = sz

    while client_info[client_info[tid].peer].size is None:
        time.sleep(1)

    if sz == client_info[client_info[tid].peer].size:
        return 'alles gut'
    else:
        return "sizes don't match"


def process_message(msg,tid,sock):

    global waiting, client_count, client_info

    msg = msg.decode('ascii')

    fin = False

    if msg == "wait":
        print(f"tid {tid} is waiting")
        waiting.append(tid)
        msg = wait_for_peer(tid,sock)
        client_info[tid].size = None
        return msg, False

    elif msg.startswith("conn"):
        msg = get_waiting(msg,tid,sock)
        return msg, False
    
    elif msg == "send":
        client_info[tid].size = None
        msg = get_waiters_list()

    elif msg.startswith("size"):
        msg = compare_size(msg,tid)

    elif msg == "end":
        fin = True

    return bytes(msg,'ascii'), fin

def manage_client(cs):

    global client_count

    my_idcount=client_count
    print(f'client #{client_count} from: {cs.getpeername()}' )
    message=f'Hello client #{client_count}! Welcome to encrypted files sender! Type your commands to the command line!'
    cs.sendall(bytes(message,'ascii'))

    client_info[my_idcount] = cinfo(my_idcount,cs.getpeername())

    fin = False
    while not fin:

        try:
            r_msg = cs.recv(buffer_size)
            ans, fin = process_message(r_msg,my_idcount,cs)
            if not fin: cs.sendall(ans)
        except socket.error as e_msg:
            print('Error:',e_msg.strerror)
            break    

    print(f"Thread {my_idcount} finished job")

if __name__ == "__main__":
    
    try:
        ss=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.bind( (HOST,PORT) )
        ss.listen(5)
    except socket.error as e_msg:
        print(e_msg.strerror)
        exit(-1)
    
    while True:

        c_sock, c_addr = ss.accept()

        t = threading.Thread(target=manage_client, args=(c_sock,) )
        threads.append(t)
        client_count+=1
        t.start()