### Tema 1 - Key Manager server and client

## Prezentare

Tema este compusa din 3 fisiere:</br> 
key_manager.py - server-ul care accepta conexiunile clientilor si le ofera chei/vectori pentru criptare</br>
client.py - clientul care se conecteaza la key manager, cere cheie si apoi trimite sau primeste un fisier criptat</br>
mycript.py - utilitar in care am scris functiile de criptare/decriptare CBC si CFB

Pentru a rula, trebuie rulate in terminale separate:</br>
Intai serverul cu comanda 
```python keymanager.py```
Apoi doi clienti cu comanda
```python client.py```
