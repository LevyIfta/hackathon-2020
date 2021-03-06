import socket
import struct
import select
import time
import threading

HEADERSIZE = 10
LISTENTIME = 10
reciveing_timer = 10.0
game_timer = 10.0
port_tcp = 11134
encoding = 'utf-8'

udp_host = '127.0.0.1'
udp_port = 13117	
local_port = port_tcp

print(udp_host)
socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

socketTCP.bind((udp_host, port_tcp))
socketTCP.listen(LISTENTIME)

# data
socket_list = [socketTCP]
players = {}
group1_score = 0
group2_score = 0
group_list_1 = []
group_list_2 = []



def receive_msg(client_socket):
    try:
        byte_message = client_socket.recv(2048)
        string_message =    byte_message.decode(encoding)
        string_message = string_message.split("\n")[0]

        return { "data" : string_message}
    except:
        return False

def print_group_players(i): 
    ans = ""
    if i == 1:
        for player in group_list_1:
            ans += player + "\n"
    if i == 2:
        for player in group_list_2:
            ans += player + "\n"
    return ans

def user_in_group_1(username): # check if the user is from group 1
    for player in group_list_1:
        if player == username:
            return True
    return False



def end_of_the_game():
    end = "Game over!\n"
    end += "Group 1 typed in " + str(group1_score) + ". \nGroup 2 typed in " + str(group2_score) + ".\n"
    if group1_score > group2_score: # score
        end += "Group 1 wins!\n\nCongratulations to the winners:\n==\n" + print_group_players(1)
    else:
        end += "Group 2 wins!\n\nCongratulations to the winners:\n==\n" + print_group_players(2)
    #print(x)
    print(end)
    end = end.encode(encoding)
    
    for player in players:
        player.send( end)
    #print(end)


def start_of_the_game():
    global group1_score
    global group2_score
    timer = threading.Timer(game_timer, end_of_the_game)
    timer.start()
    print("start of the game")
    while timer.is_alive():
        read_socket, _, exception_socket = select.select(socket_list, [], socket_list, 1)
    
        for noti_socket in read_socket:
            message = receive_msg(noti_socket)
            if message is False: # get the message from players
                print(f"close connection from {players[noti_socket]['data']}")
                socket_list.remove(noti_socket)
                del players[noti_socket]
                continue

            user = players[noti_socket]
            print(user)
            if user_in_group_1(user['data']): # calculate from which group he is
                group1_score += 1
            else:
                group2_score += 1

        for noti_socket in exception_socket:
            socket_list.remove(noti_socket)
            del players[noti_socket]

def end_registration_time():
    #print("timer finish")
    flag = True
    message = "Welcome to Keyboard Spamming Battle Royale.\n"
    group_str_1 = "Group 1:\n==\n"
    group_str_2 = "Group 2:\n==\n"
    for player in players:
        if flag: # divide to groups
            group_list_1.append(players[player]['data'])
            group_str_1 += players[player]['data'] + "\n"
            flag = False
        else:
            flag = True
            group_list_2.append(players[player]['data'])
            group_str_2 += players[player]['data'] + "\n"
    message += group_str_1 + group_str_2
    message += "\n"
    message += "\n\nStart pressing keys on your keyboard as fast as you can!!"

    message = message.encode(encoding) # send the players message
    for player in players:
        player.send( message)
    start_of_the_game()
    
# start reciving players
def reciving_players():
    timer = threading.Timer(reciveing_timer, end_registration_time)
    timer.start()

    while timer.is_alive():
        read_socket, _, exception_socket = select.select(socket_list, [], socket_list, 1)
        
        for noti_socket in read_socket: # all the message that the client send
            if noti_socket == socketTCP:
                client_socket, client_address = socketTCP.accept()
                
                user = receive_msg(client_socket)
                if user is False:
                    continue
                socket_list.append(client_socket)
                players[client_socket] = user # save users

                print(f"accept new connection from {client_address[0]}:{client_address[1]} username :{user['data']}")
            
        for noti_socket in exception_socket:
            socket_list.remove(noti_socket)
            del players[noti_socket]
    


# server UDP 
def start_server() :
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)   	           
    print("Server started, listening on IP address 172.1.0.134")
    msg = struct.pack('Ibh', 0xfeedbeef, 0x2, local_port)
    for _ in range(10) :
        sock.sendto(msg,(udp_host,udp_port))
        time.sleep(1)
    sock.close()


def main() :
    global socket_list
    global players
    global group1_score
    global group2_score
    global group_list_1
    global group_list_2
    try: 
        socket_list = [socketTCP]
        players = {}
        group1_score = 0
        group2_score = 0
        group_list_1 = []
        group_list_2 = []

        threading.Thread(target=start_server).start()
        threading.Thread(target=reciving_players).start()
    except Exception as e :
        print ('unkonw exception: ', str(e))
        
    


main()