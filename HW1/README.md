### Tema 1 - Key Manager server and client

## Prezentare

Tema este compusa din 3 fisiere:</br> 
key_manager.py - server-ul care accepta conexiunile clientilor si le ofera chei/vectori pentru criptare</br>
client.py - clientul care se conecteaza la key manager, cere cheie si apoi trimite sau primeste un fisier criptat</br>
mycript.py - utilitar in care am scris functiile de criptare/decriptare CBC si CFB

# Rulare
Pentru a rula, trebuie rulate in terminale separate:</br>
Intai serverul cu comanda 
```python keymanager.py```, 
apoi doi clienti cu comanda
```python client.py```

# Parcursul complet al rularii va fi urmatorul:
1. Clientii se vor conecta automat la server si vor primi mesaje de conectare
2. Comunicarea se va face prin introducerea de comenzi la linia de comanda
3. Prima comanda trebuie sa exprime actiunea pe care o dorim. Aceasta poate fi ```send``` in cazul in care dorim ca clientul sa trimita date sau ```wait``` in cazul in care dorim sa asteptam sa ne trimita cineva un fisier.
4. Avand doi clienti, trebuie ca mai intai unul dintre ei sa trimita ```wait``` iar apoi cel de-al doilea sa trimita ```send```
5. Clientul care a trimis ```send``` va primi o lista cu partenerii disponibili (daca exista parteneri disponibili)
6. Acest client trebuie sa aleaga unul dintre partenerii disponibili scriind comanda ```conn <peer_id> <crypt_mode>``` unde peer_id va fi id-ul partenerului, iar crypt_mode trebuie sa fie cbc sau cfb
7. Dupa alegerea unui partener, in background server-ul le va trimite celor doi modul, cheia si vectorul de initializare, cei doi clienti vor confirma primirea trimitand un mesaj criptat, iar apoi clientul <b>waiter</b> va deschide un socket unde clientul <b>sender</b> va trimite fisierul criptat.
8. Clientul <b>sender</b> va afisa un prompt in care cere user-ului introducerea unui nume de fisier care sa fie transferat
9. Clientul <b>waiter</b> va primi dimensiunea fisierului criptat si va cere confirmare de la user (y/n). Daca primeste confirmare, va cere un nume sub care sa salveze fisierul primit.
10. Dupa ce trimiterea si primirea s-au realizat cu succes, cei doi clienti vor trimite server-ului numarul de blocuri criptate/decriptate
11. Daca cele doua numere corespund, server-ul le trimite amandurora mesaje de confirmare.
12. Se poate reveni la pasul 3. sau se poate scrie ```end``` pentru a incheia comunicarea cu server-ul
