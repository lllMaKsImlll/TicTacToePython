import socket
import threading

def print_board(board):
    for row in board:
        print("|".join(row))
    print("")

def check_winner(board, mark):
    for i in range(3):
        if all([board[i][j] == mark for j in range(3)]) or all([board[j][i] == mark for j in range(3)]):
            return True
    if all([board[i][i] == mark for i in range(3)]) or all([board[i][2-i] == mark for i in range(3)]):
            return True
    return False

def handle_client(conn, addr, player_id, board, players, lock):
    conn.send(f"You are player {player_id} ({'X' if player_id == 1 else 'O'})\n".encode())
    while True:
        try:
            message = conn.recv(1024).decode()
            if "Your move" in message:
                conn.send(message.encode())
                move = conn.recv(1024).decode().strip().split()
                row, col = int(move[0]), int(move[1])

                with lock:
                    if board[row][col] != " ":
                        conn.send("Invalid move, try again".encode())
                        continue

                    mark = "X" if player_id == 1 else "O"
                    board[row][col] = mark
                    print_board(board)

                    board_str = "\n".join(["|".join(row) for row in board]) + "\n"
                    for p_conn in players:
                        p_conn.send(board_str.encode())

                    if check_winner(board, mark):
                        conn.send("You win!".encode())
                        for p_conn in players:
                            if p_conn != conn:
                                p_conn.send("You lose!".encode())
                        return

                    if all([board[i][j] != " " for i in range(3) for j in range(3)]):
                        for p_conn in players:
                            p_conn.send("It's a draw!".encode())
                        return

                    current_player_index = (players.index(conn) + 1) % len(players)
                    players[current_player_index].send("Your move (row col): ".encode())
        except:
            conn.close()
            return

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.0.103", 8888))
    server_socket.listen(5)

    print("Waiting for players...")

    players = []
    board = [[" "]*3 for _ in range(3)]
    lock = threading.Lock()

    while True:
        conn, addr = server_socket.accept()
        player_id = len(players) + 1
        players.append(conn)
        print(f"Player {player_id} connected from", addr)
        
        if player_id == 1:
            conn.send("Waiting for other players...\n".encode())

        threading.Thread(target=handle_client, args=(conn, addr, player_id, board, players, lock)).start()

        if player_id == 1:
            conn.send("Your move (row col): ".encode())
        elif player_id > 1:
            conn.send("Waiting for your turn...\n".encode())

if __name__ == "__main__":
    main()
