import time
import socket
import select

TIMEOUT = 20

question = []
answer = []


def generate_questions():
    for i in range(100):
        question.append(str(i) + "+" + str(i + 1))
        answer.append(str(2 * i + 1))


generate_questions()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# server=socket.gethostbyname(socket.gethostname())
# print(server)
server = '0.0.0.0'
port = 5050

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(3)
print("Waiting for connections...Server started")

allconn = []
scores = []


def function():
    qno = -1
    while True:
        try:
            qno += 1
            if qno == 100:
                for i in allconn:
                    i.sendall(bytes("All Questions Exhausted...GAME OVER", "utf-8"))
                break
            print(f'Q{qno + 1} has been asked')
            for i in allconn:
                i.sendall(bytes(question[qno], "utf-8"))
            outputs = []
            t = time.perf_counter()
            read, write, er = select.select(allconn, outputs, allconn, TIMEOUT)
            diff = time.perf_counter() - t
            if diff < TIMEOUT:
                time.sleep(TIMEOUT - diff)

            if len(read) == 0:
                for conn in allconn:
                    conn.sendall(bytes("No one pressed the buzzer", "utf-8"))
                time.sleep(5)
                continue
            elif len(read) > 0:

                first_buzzer = read[0]
                msg = first_buzzer.recv(1024).decode("utf-8")
                pl = allconn.index(first_buzzer) + 1
                print(f'Buzzer received from player {pl}')
                if not msg:
                    first_buzzer.sendall(bytes("No answer received", "utf-8"))
                    time.sleep(5)
                    continue
                else:
                    first_buzzer.sendall(bytes(f'Buzzer received,You have {TIMEOUT} seconds to answer', "utf-8"))
                    inputs = [first_buzzer]
                    outputs = []
                    t2 = time.perf_counter()
                    read, write, exceptional = select.select(inputs, outputs, inputs, TIMEOUT)
                    dif = time.perf_counter() - t2
                    if dif < TIMEOUT:
                        time.sleep(TIMEOUT - dif)
                    if len(read) == 0:
                        first_buzzer.sendall(bytes("You did not answer the question...Timeout", "utf-8"))
                        time.sleep(5)
                        continue
                    else:
                        ans = first_buzzer.recv(1024).decode("utf-8")
                        if ans == answer[qno]:
                            scores[allconn.index(first_buzzer)] += 1
                            first_buzzer.sendall(bytes("Correct Answer", "utf-8"))
                        else:
                            scores[allconn.index(first_buzzer)] -= 0.5
                            first_buzzer.sendall(bytes("Wrong Answer", "utf-8"))
                        time.sleep(5)
            if max(scores) >= 5:
                windex = scores.index(max(scores))
                winner = allconn[windex]
                for conn in allconn:
                    if conn == winner:
                        conn.sendall(bytes("You have won the game!!", "utf-8"))
                    else:
                        conn.sendall(bytes("You lost.Better luck next time", "utf-8"))
                break
        except socket.error as e:
            print(str(e))


while True:
    if len(allconn) < 3:
        conn, address = s.accept()
        print("Connected to address: ", address)
        allconn.append(conn)
        scores.append(0)
        conn.sendall(bytes("You have joined the game", "utf-8"))
    else:
        function()
        print("GAME OVER")
        break
