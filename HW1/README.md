# Tema 1 - Key Manager server and client

## Prezentare

Tema este compusa din 3 fisiere:</br> 
key_manager.py - server-ul care accepta conexiunile clientilor si le ofera chei/vectori pentru criptare</br>
client.py - clientul care se conecteaza la key manager, cere cheie si apoi trimite sau primeste un fisier criptat</br>
mycript.py - utilitar in care am scris functiile de criptare/decriptare CBC si CFB

### Rulare
Pentru a rula, trebuie rulate in terminale separate:</br>
Intai serverul cu comanda 
```python keymanager.py```, 
apoi doi clienti cu comanda
```python client.py```

### Parcursul complet al rularii va fi urmatorul:
1. Clientii se vor conecta automat la server si vor primi mesaje de conectare
2. Comunicarea se va face prin introducerea de comenzi la linia de comanda
3. Prima comanda trebuie sa exprime actiunea pe care o dorim. Aceasta poate fi ```send``` in cazul in care dorim ca clientul sa trimita date sau ```wait``` in cazul in care dorim sa asteptam sa ne trimita cineva un fisier.
4. Avand doi clienti, trebuie ca mai intai unul dintre ei sa trimita ```wait``` iar apoi cel de-al doilea sa trimita ```send```
5. Clientul care a trimis ```send``` va primi o lista cu partenerii disponibili (daca exista parteneri disponibili)
6. Acest client trebuie sa aleaga unul dintre partenerii disponibili scriind comanda ```conn <peer_id> <enc_mode>``` unde peer_id va fi id-ul partenerului, iar crypt_mode trebuie sa fie cbc sau cfb
7. Dupa alegerea unui partener, in background server-ul le va trimite celor doi modul, cheia si vectorul de initializare, cei doi clienti vor confirma primirea trimitand un mesaj criptat, iar apoi clientul <b>waiter</b> va deschide un socket unde clientul <b>sender</b> va trimite fisierul criptat.
8. Clientul <b>sender</b> va afisa un prompt in care cere user-ului introducerea unui nume de fisier care sa fie transferat
9. Clientul <b>waiter</b> va primi dimensiunea fisierului criptat si va cere confirmare de la user (y/n). Daca primeste confirmare, va cere un nume sub care sa salveze fisierul primit.
10. Dupa ce trimiterea si primirea s-au realizat cu succes, cei doi clienti vor trimite server-ului numarul de blocuri criptate/decriptate
11. Daca cele doua numere corespund, server-ul le trimite amandurora mesaje de confirmare.
12. Se poate reveni la pasul 3. sau se poate scrie ```end``` pentru a incheia comunicarea cu server-ul

Exemplu de rulare:
```
terminal server>>  python key_manager.py
terminal client1>> python client.py
output: Message from server: Hello client #1! Welcome to encrypted files sender! Type your commands to the command line!    
Introduce next command:
terminal client1>> wait

terminal client2>> python client.py
output: Message from server: Hello client #2! Welcome to encrypted files sender! Type your commands to the command line!
Introduce next command: 
terminal client2>> send
output: Message from server: select a peer to send a message  
your next command should be 'conn <peer_id> <enc_mode>
list of available waiters:
1

Introduce next command: 
terminal client2>> conn 1 cbc
output: Successfully connected to peer
Enter a filename to send to peer: 
terminal client2>> ./mycrypt.py

terminal client1>>
output: The size of the encrypted file is 4240 bytes
Do you wish to continue? (y/n)
terminal client1>> y
output: Type a name for your file: 
terminal client1>> ./mycrypt_copy.py
output: 
content of file:
from Crypto.Cipher import AES
from typing import
...
 dec_aes(tx3c)
    print(tx2d)
    print(tx3d)

Saved successfully
Message from server: I will notify your peer
Message from server: alles gut
terminal client1>> end
terminal client2>> end
```

## Detalii implementare

Functiile ce criptare si decriptare sunt
```py
def enc_cbc(message,key,iv):

def enc_cfb(message,key,iv):

def dec_cbc(cph_text,key,iv, is_string = False):

def dec_cfb(cph_text,key,iv, is_string = False):

def enc_aes(message: Union[str, bytes] ,key = _default_key):

def dec_aes(cph_text, key = _default_key, is_string = False):
# _default_key este acel K3 pe care il vor avea atat server-ul, cat si clientii
```

Functiile care privesc modurile cbc si cfb au urmatoarea structura:
1. Impart mesajul in blocuri apeland functia 
```py
def _get_blocks(content):
```
Care realizeaza si padding-ul. Padding-ul este realizat dupa metoda <a href=https://en.wikipedia.org/wiki/Padding_(cryptography)#PKCS#5_and_PKCS#7>PKCS#7</a>, adaugand p copii ale byte-ului cu valoare p la final, unde p este lungimea necesara a padding-ului (intre 1 si 16)
</br>

2. Intr-o bucla se repeta algoritmul care cripteaza/decripteaza fiecare bloc, actualizand la fiecare iteratie iv-ul pentru iteratia urmatoare conform diagramelor din curs.

In ```key_manager``` cheile si vectorii de initializare se genereaza folosind functia ```secrets.token_bytes(len: int)```

Comunicarea intre clienti si server se realizeaza prin intermediul socketilor disponibili in mod direct in python. Aceasta are structura: Welcome message -> *(client asks -> server answers)

Mesajul de confirmare care va fi criptat si trimis catre server este format dintr-un string concatenat cu un vector de bytes:
```py
confirmation_message = b'This message is to confirm key receival ' + bytes([10,100,200,15,17,19,5,4,3,2,1])
```
