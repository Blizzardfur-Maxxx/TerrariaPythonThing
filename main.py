import socket
import struct
import threading

# Function to pack color components into the Color Struct
def pack_color(r, g, b):
    return struct.pack('<BBB', r, g, b)

# Function to unpack the Color Struct into individual RGB components
def unpack_color(color):
    return struct.unpack('<BBB', color)

# Function to send a message with a specified message type and payload
def send_message(client_socket, message_type, payload):
    # Calculate message length
    message_length = len(payload) + 5  # Adding 5 for the length of the header (4 bytes) and the message type (1 byte)

    # Pack the message length and type
    header = struct.pack('<IB', message_length, message_type)

    # Send the header and payload
    client_socket.sendall(header + payload)

# Function to receive a message from the server
def receive_message(client_socket):
    header = client_socket.recv(5)  # 4 bytes for length + 1 byte for type
    if not header:  # Check if header is empty
        print("Empty header received")
        return None, None
    print("Received header:", header)
    message_length, message_type = struct.unpack('<IB', header)
    payload = b''
    remaining_bytes = message_length - 5  # Subtract 5 for the header length
    while remaining_bytes > 0:
        chunk = client_socket.recv(remaining_bytes)
        if not chunk:
            print("Incomplete payload received")
            return None, None  # Incomplete payload received
        payload += chunk
        remaining_bytes -= len(chunk)
    print("Received payload:", payload)
    return message_type, payload

def handle_messages(client_socket):
    try:
        while True:
            message_type, payload = receive_message(client_socket)
            if message_type is None:  # Handle empty header or incomplete payload
                continue
            if message_type == 1:  # Fatal Error
                print("Fatal Error:", payload)
                client_socket.close()  # Close the connection
                break
            elif message_type == 3:  # Connection Approved
                player_slot = payload[0]  # Assuming player slot is a byte
                print("Connection Approved. Assigned player slot:", player_slot)
                break
            elif message_type == 0x10:  # Player Life packet
                print("Received Player Life packet")
                player_slot, current_health, max_health = struct.unpack('<Bhh', payload)
                print("Player Slot:", player_slot)
                print("Current Health:", current_health)
                print("Max Health:", max_health)
            elif message_type == 0x2A:  # Player Mana packet
                print("Received Player Mana packet")
                player_slot, mana_level, max_mana = struct.unpack('<Bhh', payload)
                print("Player Slot:", player_slot)
                print("Mana Level:", mana_level)
                print("Max Mana:", max_mana)
            elif message_type == 4:  # Player Appearance packet
                print("Received Player Appearance packet")
                player_slot, hair_style, gender, \
                hair_color, skin_color, eye_color, \
                shirt_color, undershirt_color, pants_color, \
                shoe_color, difficulty, player_name_length = struct.unpack('<BBBBBB3s3s3s3s3s3s3s3sB', payload[:28])
                
                player_name = payload[28:].decode('ascii')[:player_name_length]
                
                print("Player Slot:", player_slot)
                print("Hair Style:", hair_style)
                print("Gender:", "Male" if gender == 1 else "Female")
                print("Hair Color:", unpack_color(hair_color))
                print("Skin Color:", unpack_color(skin_color))
                print("Eye Color:", unpack_color(eye_color))
                print("Shirt Color:", unpack_color(shirt_color))
                print("Undershirt Color:", unpack_color(undershirt_color))
                print("Pants Color:", unpack_color(pants_color))
                print("Shoe Color:", unpack_color(shoe_color))
                print("Difficulty:", difficulty)
                print("Player Name:", player_name)
                pass
            else:
                print("Unknown message type:", message_type)
    except Exception as e:
        print("Error in message handling:", e)
        client_socket.close()


# Function to send the Player Appearance packet to the server
def send_player_appearance(client_socket, player_slot, hair_style, gender, hair_color, skin_color, eye_color, shirt_color, undershirt_color, pants_color, shoe_color, difficulty, player_name):
    # Pack the player appearance data
    payload = struct.pack('<BBBB' + '3s3s3s3s3s3s3s3sB', player_slot, hair_style, gender,
                        pack_color(*hair_color), pack_color(*skin_color), pack_color(*eye_color),
                        pack_color(*shirt_color), pack_color(*undershirt_color), pack_color(*pants_color),
                        pack_color(*shoe_color), difficulty, len(player_name)) + player_name.encode('ascii')
    
    # Send the Player Appearance packet
    send_message(client_socket, 4, payload)

# Function to send the Set Player Life packet to the server
def send_player_life(client_socket, player_slot, current_health, max_health):
    # Pack the player life data
    payload = struct.pack('<Bhh', player_slot, current_health, max_health)
    
    # Send the Set Player Life packet
    send_message(client_socket, 0x10, payload)

# Function to send the Set Player Mana packet to the server
def send_player_mana(client_socket, player_slot, mana_level, max_mana):
    # Pack the player mana data
    payload = struct.pack('<Bhh', player_slot, mana_level, max_mana)
    
    # Send the Set Player Mana packet
    send_message(client_socket, 0x2A, payload)
    
# Function to initialize the client and connect to the server
def main():
    # Server address and port
    server_address = '6.tcp.us-cal-1.ngrok.io'
    server_port = 17344
    
    # Server version
    server_version = "Terraria49"  # Example server version
    
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        client_socket.connect((server_address, server_port))
        print("Connected to server at {}:{}".format(server_address, server_port))
        
        # Send server version as payload for authentication
        send_message(client_socket, 1, server_version.encode('utf-8'))
        
        # Receive authentication response
        receive_message(client_socket)
        
        # Start a new thread for handling messages
        message_thread = threading.Thread(target=handle_messages, args=(client_socket,))
        message_thread.start()
        
        # Example of sending Player Appearance packet
        player_slot = 1
        hair_style = 2
        gender = 1  # Male
        hair_color = (255, 0, 0)  # Red
        skin_color = (255, 255, 255)  # White
        eye_color = (0, 0, 255)  # Blue
        shirt_color = (0, 128, 0)  # Green
        undershirt_color = (0, 128, 0)  # Green
        pants_color = (0, 0, 128)  # Dark Blue
        shoe_color = (128, 128, 128)  # Gray
        difficulty = 0  # Normal
        player_name = "Player1"
        send_player_appearance(client_socket, player_slot, hair_style, gender, hair_color, skin_color, eye_color, shirt_color, undershirt_color, pants_color, shoe_color, difficulty, player_name)
        
        # Example of sending Set Player Life packet
        current_health = 100
        max_health = 200
        send_player_life(client_socket, player_slot, current_health, max_health)

        # Example of sending Set Player Mana packet
        mana_level = 50
        max_mana = 100
        send_player_mana(client_socket, player_slot, mana_level, max_mana)
        
        # Your game logic goes here...
        
    except Exception as e:
        print("Error:", e)
        client_socket.close()  # Close the connection

if __name__ == "__main__":
    main()
