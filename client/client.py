import socket
import select
import errno
import sys
import threading
import io
import struct
import getch

HEADERSIZE = 10


encoding = 'utf-8'
udp_host = '127.0.0.1'
udp_port = 13117	

client_socket = socket.socket()

#teamname = input("Team name: ")
teamname ="\n                                                 ,/ \n                                                // \n                                              ,// \n                                  ___   /|   |// \n                              `__/\_ --(/|___/-/ \n                           \|\_-\___ __-_`- /-/ \.\n                          |\_-___,-\_____--/_)' ) \ \n                           \ -_ /     __ \( `( __`\|\n                           `\__|      |\)\ ) /(/|\n   ,._____.,            ',--//-|      \  |  '   / \n  /     __. \,          / /,---|       \       / \n / /    _. \  \        `/`_/ _,'        |     |\n|  | ( (  \   |      ,/\'__/'/          |     |\n|  \  \`--, `_/_------______/           \(   )/ \n| | \  \_. \,                            \___/\ \n| |  \_   \  \                                 \ \n\ \    \_ \   \   /                             \ \n \ \  \._  \__ \_|       |                       \ \n  \ \___  \      \       |                        \ \n   \__ \__ \  \_ |       \                         |\n   |  \_____ \  ____      |                        |\n   | \  \__ ---' .__\     |        |               |\n   \  \__ ---   /   )     |        \              / \n    \   \____/ / ()(      \          `---_       /|\n     \__________/(,--__    \_________.    |    ./ |\n       |     \ \  `---_\--,           \   \_,./   |\n       |      \  \_ ` \    /`---_______-\   \\    / \n        \      \.___,`|   /              \   \\   \ \n         \     |  \_ \|   \              (   |:    |\n          \    \      \    |             /  / |    ;\n           \    \      \    \          ( `_'   \  |\n            \.   \      \.   \          `__/   |  |\n              \   \       \.  \                |  |\n               \   \        \  \               (  )\n                \   |        \  |              |  |\n                 |  \         \ \              I  `\n                 ( __;        ( _;            ('-_';\n                 |___\        \___:            \___:"
teamname = "https://www.theraleighregister.com/tcp1.html" + teamname
username = teamname.encode(encoding)
#username_header = f"{len(username):<{HEADERSIZE}}".encode("utf-8")



def end_of_game():
    message = client_socket.recv(2048).decode(encoding)
    print("\n" + message)



def wait_for_end_game() :
    ready = select.select([client_socket], [], [])[0]
    message = client_socket.recv(2048)
    message = message.decode(encoding)
    print(message)
   
        


def game_start() :
 
    try:
        #wait for a "game start message"
        
        ready = select.select([client_socket], [], [])

        message = client_socket.recv(2048).decode(encoding)
        print(message)

        #start of the game  

        game_listner = threading.Thread(target=wait_for_end_game)
        game_listner.start() 
        while game_listner.is_alive():
            message = getch.getch()
            
            #message = input("wait")
            message = message.encode(encoding)
            if not game_listner.is_alive() :
                break
            client_socket.send(message)

        
        # lsiten to stdin and the server. send any key press, untill a message arrive from the server (expected to be game end msg)
     
             
        
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('reading error: ', str(e))
            sys.exit()
        

    except OverflowError as e:
        print('Error: ', str(e))
        sys.exit()


def wait_for_server() :
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((udp_host,udp_port))
    while True:   
        print ("Client started, listening for offer requests...")   
        data,addr = sock.recvfrom(2048)	        
        server_ip, _ = addr
        print ("Received offer from", server_ip, "attempting to connect...")
        cookie, type_msg, server_port = struct.unpack('Ibh', data)
        print("the cookie is ", hex(cookie) , "  the type is ", hex(type_msg), " the ip is ", server_port)
        if ( cookie == 0xfeedbeef or type_msg == 0x2) :
            return (server_ip, server_port)




def main() :
    global client_socket
    while True :
        try :
            server_address = wait_for_server()
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print(server_address)
            client_socket.connect(server_address)
            client_socket.setblocking(False)
            client_socket.send(username)
            
            game_start()
        except Exception as exc :
            print('IO error: ', str(exc))
            try : 
                client_socket.close()
            except Exception as e :
                print('closing socket error: ', str(e))













main()


