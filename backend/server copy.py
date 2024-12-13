# server.py
import asyncio
import websockets
import json
import socket
import struct

# Server settings
PI_HOST = 'raspberrypi.local'  # Change this to your Raspberry Pi's IP or hostname
PI_PORT = 5005  # Port to receive data from Raspberry Pi

# WebSocket settings
WS_HOST = "localhost"
WS_PORT = 8765

# Rocket simulation variables (default values)
altitude = 0
temperature = 15
velocity = 0
stage = "launch"

async def receive_pi_data():
    """ Connect to the Raspberry Pi and receive real-time sensor data. """
    global altitude, temperature, velocity, stage

    # Set up TCP connection with Raspberry Pi
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((PI_HOST, PI_PORT))
        print("Connected to Raspberry Pi")

        while True:
            # Receive structured data (example assumes altitude, temperature, velocity, stage as floats)
            data = s.recv(16)  # Adjust buffer size based on data structure from Pi
            if not data:
                break
            altitude, temperature, velocity, stage_val = struct.unpack('ffff', data)
            stage = interpret_stage(stage_val)  # Convert stage value to a meaningful label
            await asyncio.sleep(0.1)

def interpret_stage(stage_val):
    """ Convert numeric stage value to text """
    if stage_val == 1.0:
        return "launch"
    elif stage_val == 2.0:
        return "ascent"
    elif stage_val == 3.0:
        return "coasting"
    elif stage_val == 4.0:
        return "descent"
    else:
        return "landed"

async def send_data(websocket, path):
    """ Send data to WebSocket client """
    global altitude, temperature, velocity, stage

    while True:
        # Prepare telemetry data
        data = {
            "temperature": round(temperature, 2),
            "altitude": round(altitude, 2),
            "v_horizontal": round(velocity, 2),
            "stage": stage
        }

        # Send data to the WebSocket client
        await websocket.send(json.dumps(data))
        
        # Print to console (for debugging purposes)
        print(data)
        
        # Delay for simulation
        await asyncio.sleep(0.1)

# Start the WebSocket server and Raspberry Pi data receiver
async def main():
    pi_task = asyncio.create_task(receive_pi_data())
    ws_task = websockets.serve(send_data, WS_HOST, WS_PORT)

    await asyncio.gather(pi_task, ws_task)
    print(f"Server started at ws://{WS_HOST}:{WS_PORT}")

asyncio.run(main())
