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
# Function to send a message with a specified message type and payload
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
                print("Received Player Appearance packet")
                # Process Player Appearance packet
                unpacked_data = struct.unpack('<BBBB' + 'BBBBBB' * 4 + 'B25s', payload)
                player_slot = unpacked_data[0]
                hair_style = unpacked_data[1]
                gender = unpacked_data[2]
                colors = unpacked_data[3:27]
                difficulty = unpacked_data[27]
                player_name = unpacked_data[28].rstrip(b'\x00').decode()
                
                hair_color = unpack_color(colors[0:3])
                skin_color = unpack_color(colors[3:6])
                eye_color = unpack_color(colors[6:9])
                shirt_color = unpack_color(colors[9:12])
                undershirt_color = unpack_color(colors[12:15])
                pants_color = unpack_color(colors[15:18])
                shoe_color = unpack_color(colors[18:21])
                
                print("Player Slot:", player_slot)
                print("Hair Style:", hair_style)
                print("Gender:", "Male" if gender == 1 else "Female")
                print("Hair Color:", hair_color)
                print("Skin Color:", skin_color)
                print("Eye Color:", eye_color)
                print("Shirt Color:", shirt_color)
                print("Undershirt Color:", undershirt_color)
                print("Pants Color:", pants_color)
                print("Shoe Color:", shoe_color)
                print("Difficulty:", difficulty)
                print("Player Name:", player_name)
            else:
                print("Unknown message type:", message_type)
    except Exception as e:
        print("Error in message handling:", e)
        client_socket.close()

# Function to send the Player Appearance packet to the server
def send_player_appearance(client_socket, player_slot, hair_style, gender, hair_color, skin_color, eye_color, shirt_color, undershirt_color, pants_color, shoe_color, difficulty, player_name):
    # Pack the player appearance data
    payload = struct.pack('<BBBB' + 'BBBBBB' * 4 + 'B25s',
                          player_slot,
                          hair_style,
                          gender,
                          *hair_color,
                          *skin_color,
                          *eye_color,
                          *shirt_color,
                          *undershirt_color,
                          *pants_color,
                          *shoe_color,
                          difficulty,
                          player_name.encode())
    
    # Send the Player Appearance packet
    send_message(client_socket, 4, payload)

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
        message_type = receive_message(client_socket)
        
        # Start a new thread for handling messages
        message_thread = threading.Thread(target=handle_messages, args=(client_socket,))
        message_thread.start()
        
        # Example of sending Player Appearance packet
        player_slot = 1
        hair_style = 2
        gender = 1  # Male
        hair_color = pack_color(255, 0, 0)  # Red
        skin_color = pack_color(255, 255, 255)  # White
        eye_color = pack_color(0, 0, 255)  # Blue
        shirt_color = pack_color(0, 128, 0)  # Green
        undershirt_color = pack_color(0, 128, 0)  # Green
        pants_color = pack_color(0, 0, 128)  # Dark Blue
        shoe_color = pack_color(128, 128, 128)  # Gray
        difficulty = 0  # Normal
        player_name = "Player1"
        send_player_appearance(client_socket, player_slot, hair_style, gender, hair_color, skin_color, eye_color, shirt_color, undershirt_color, pants_color, shoe_color, difficulty, player_name)
        
        # Your game logic goes here...
        
    except Exception as e:
        print("Error:", e)
        client_socket.close()  # Close the connection

if __name__ == "__main__":
    main()