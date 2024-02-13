import socket
import struct
import threading

def pack_color(r, g, b):
    return struct.pack('<BBB', r, g, b)

# Function to send a message with a specified message type and payload
def send_message(client_socket, message_type, payload):
    # Calculate message length
    message_length = len(payload) + 1  # Adding 1 for the message type
    
    # Pack the message length and type
    header = struct.pack('<IB', message_length, message_type)
    
    # Encode the payload string to bytes
    if isinstance(payload, str):
        payload = payload.encode()
    
    # Send the header and payload
    client_socket.sendall(header + payload)

# Function to receive a message from the server
def receive_message(client_socket):
    # Receive the header containing message length and type
    header = client_socket.recv(5)  # 4 bytes for length + 1 byte for type
    
    # Unpack the header
    message_length, message_type = struct.unpack('<IB', header)
    
    # Receive the payload
    payload = client_socket.recv(message_length - 1)  # Subtract 1 for the type
    
    # Extract offset and error message
    offset = payload[0]
    error_message = payload[1:]
    
    print(message_type, offset, error_message)
    return message_type, (offset, error_message)

# Function to handle incoming messages from the server
def handle_messages(client_socket):
    try:
        while True:
            message_type, payload = receive_message(client_socket)
            if message_type == 1:  # Fatal Error
                print("Fatal Error:", payload)
                client_socket.close()  # Close the connection
                break
            elif message_type == 3:  # Connection Approved
                player_slot = ord(payload[0])  # Assuming player slot is a byte
                print("Connection Approved. Assigned player slot:", player_slot)
                break
            elif message_type == 4:  # Player Appearance packet
                player_slot, hair_style, gender, hair_color, skin_color, eye_color, shirt_color, undershirt_color, pants_color, shoe_color, difficulty, player_name = unpack_player_appearance(payload)
                print("Player Appearance - Slot:", player_slot, "Hair Style:", hair_style, "Gender:", gender, "Hair Color:", hair_color, "Skin Color:", skin_color, "Eye Color:", eye_color, "Shirt Color:", shirt_color, "Undershirt Color:", undershirt_color, "Pants Color:", pants_color, "Shoe Color:", shoe_color, "Difficulty:", difficulty, "Player Name:", player_name)
            else:
                print("Unknown message type:", message_type)
    except Exception as e:
        print("Error in message handling:", e)
        client_socket.close()

# Function to send player appearance message
# Function to send player appearance message
def send_player_appearance(client_socket):
    # Dummy player appearance data, replace with actual data
    player_slot = 1
    hair_style = 1
    gender = 1
    hair_color = (255, 0, 0)  # Red
    skin_color = (255, 255, 255)  # White
    eye_color = (0, 0, 255)  # Blue
    shirt_color = (0, 255, 0)  # Green
    undershirt_color = (0, 255, 255)  # Cyan
    pants_color = (255, 0, 255)  # Magenta
    shoe_color = (255, 255, 0)  # Yellow
    difficulty = 0  # Normal
    player_name = "PlayerName"
    
    # Pack colors
    packed_hair_color = pack_color(*hair_color)
    packed_skin_color = pack_color(*skin_color)
    packed_eye_color = pack_color(*eye_color)
    packed_shirt_color = pack_color(*shirt_color)
    packed_undershirt_color = pack_color(*undershirt_color)
    packed_pants_color = pack_color(*pants_color)
    packed_shoe_color = pack_color(*shoe_color)
    
    # Construct payload
    payload = struct.pack('<BBB', player_slot, hair_style, gender) \
            + packed_hair_color \
            + packed_skin_color \
            + packed_eye_color \
            + packed_shirt_color \
            + packed_undershirt_color \
            + packed_pants_color \
            + packed_shoe_color \
            + struct.pack('<B', difficulty) \
            + player_name.encode()
    
    # Calculate message length
    message_length = len(payload) + 1  # Adding 1 for the message type
    
    # Pack the message length and type
    header = struct.pack('<IB', message_length, 4)  # Message type 4 for Player Appearance
    
    # Send the header and payload
    client_socket.sendall(header + payload)


# Function to unpack player appearance message
def unpack_player_appearance(payload):
    # Unpack payload
    player_slot, hair_style, gender, *colors_and_difficulty, player_name_bytes = struct.unpack('<BBBBBBBBBBBB', payload)
    
    # Extract colors and difficulty
    hair_color = colors_and_difficulty[:3]
    skin_color = colors_and_difficulty[3:6]
    eye_color = colors_and_difficulty[6:9]
    shirt_color = colors_and_difficulty[9:12]
    undershirt_color = colors_and_difficulty[12:15]
    pants_color = colors_and_difficulty[15:18]
    shoe_color = colors_and_difficulty[18:21]
    difficulty = colors_and_difficulty[21]
    
    # Convert player_name_bytes to string
    player_name = player_name_bytes.decode()
    
    return player_slot, hair_style, gender, hair_color, skin_color, eye_color, shirt_color, undershirt_color, pants_color, shoe_color, difficulty, player_name

# Function to initialize the client and connect to the server
def main():
    # Server address and port
    server_address = '127.0.0.1'
    server_port = 7777
    
    # Server version
    server_version = "Terraria37"  # Example server version
    
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        client_socket.connect((server_address, server_port))
        print("Connected to server at {}:{}".format(server_address, server_port))
        
        # Send server version as payload for authentication
        send_message(client_socket, 1, server_version)
        
        # Receive authentication response
        message_type, payload = receive_message(client_socket)
        
        # Start a new thread for handling messages
        message_thread = threading.Thread(target=handle_messages, args=(client_socket,))
        message_thread.start()
        
        # Send player appearance message to the server
        send_player_appearance(client_socket)
        
    except Exception as e:
        print("Error:", e)
        client_socket.close()  # Close the connection

if __name__ == "__main__":
    main()
