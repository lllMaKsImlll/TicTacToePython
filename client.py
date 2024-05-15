import socket

def print_board(board):
    for row in board:
        print(row)
    print("")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("192.168.0.103", 8888))

    player_number = client_socket.recv(1024).decode()
    print(player_number)

    while True:
        message = client_socket.recv(1024).decode()
        if "Your move" in message:
            print(message)
            move = input("Enter your move (row col): ").strip().split()
            client_socket.send(" ".join(move).encode())
        elif "win" in message or "lose" in message or "draw" in message:
            print(message)
            break
        else:
            board = message.split("\n")
            print_board(board)

    client_socket.close()

if __name__ == "__main__":
    main()
