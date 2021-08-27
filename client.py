import socket
from threading import Thread
import time

TIMEOUT = 20
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = socket.gethostbyname(socket.gethostname())  # If using 2 diff. systems over LAN enter local ip of server here
client.connect((server, 5050))


def send_ans(client):
    t = time.perf_counter()
    ans = input()
    # print("Got the answer from console")
    client.sendall(bytes(ans, "utf-8"))
    dif = time.perf_counter() - t
    if dif < TIMEOUT:
        time.sleep(TIMEOUT - dif)


def send_buzzer(client):
    t = time.perf_counter()
    print("Do you want to answer the question(y/n)?")
    choice = input()
    if choice == 'y':
        client.sendall(bytes("Buzz", "utf-8"))
    diff = time.perf_counter() - t
    if diff < TIMEOUT:
        time.sleep(TIMEOUT - diff)


msg_count = 0
while True:
    msg_received = str(client.recv(1024).decode("utf-8"))
    if not msg_received:
        print("Lost connection")
        client.close()
        break
    print(msg_received)
    if msg_received == "You have joined the game":
        msg_count += 1
        continue
    if msg_received in ["No one pressed the buzzer", "No answer received", "You did not answer the question...Timeout", "Correct Answer", "Wrong Answer"]:
        continue
    if msg_received in ["All Questions Exhausted...GAME OVER", "You have won the game!!","You lost.Better luck next time"]:
        client.close()
        break
    if msg_received == f'Buzzer received,You have {TIMEOUT} seconds to answer':
        print("Enter your answer: ")
        p = Thread(target=send_ans, args=(client,))
        p.daemon = True
        p.start()
        p.join(timeout=TIMEOUT)
        print("Time over for giving answer")
        continue
    if msg_count > 0:
        p = Thread(target=send_buzzer, args=(client,))
        p.daemon = True
        p.start()
        p.join(timeout=TIMEOUT)
        print("Time over for pressing buzzer")
