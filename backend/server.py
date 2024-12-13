import asyncio
import websockets
import json
import random
import time
import math

# Rocket simulation variables
altitude = 0
temperature = 15  # Starting temperature at ground level
velocity = 0
acceleration = 30  # Initial acceleration (m/s^2)
stage = "launch"  # Can be 'launch', 'ascent', 'coasting', 'descent'

# Orientation variables
bno_x, bno_y, bno_z = 0.0, 0.0, 0.0  # Initial orientation angles
time_passed = 0

def update_orientation(dt):
    global bno_x, bno_y, bno_z, time_passed, velocity, stage
    
    time_passed += dt
    
    # Base oscillation
    base_freq = 0.1
    base_amplitude = 0.2
    
    if stage == "launch":
        # During launch, rocket should be mostly straight with slight oscillations
        bno_x = base_amplitude * math.sin(base_freq * time_passed)
        bno_y = base_amplitude * math.cos(base_freq * time_passed)
        bno_z = random.uniform(-0.1, 0.1)  # Slight yaw changes
    
    elif stage == "ascent":
        # More pronounced oscillations during ascent
        bno_x = base_amplitude * 2 * math.sin(base_freq * 2 * time_passed)
        bno_y = base_amplitude * 2 * math.cos(base_freq * 2 * time_passed)
        bno_z = base_amplitude * math.sin(base_freq * 0.5 * time_passed)
    
    elif stage == "coasting":
        # Smoother, slower oscillations during coasting
        bno_x = base_amplitude * math.sin(base_freq * 0.5 * time_passed)
        bno_y = base_amplitude * math.cos(base_freq * 0.5 * time_passed)
        bno_z = base_amplitude * 0.5 * math.sin(base_freq * 0.25 * time_passed)
    
    elif stage == "descent":
        # More chaotic movements during descent
        bno_x = base_amplitude * 3 * math.sin(base_freq * 3 * time_passed) + random.uniform(-0.5, 0.5)
        bno_y = base_amplitude * 3 * math.cos(base_freq * 3 * time_passed) + random.uniform(-0.5, 0.5)
        bno_z = base_amplitude * math.sin(base_freq * time_passed) + random.uniform(-0.3, 0.3)
    
    # Add some velocity-based oscillation
    vel_factor = min(velocity / 1000, 1)  # Normalize velocity factor
    bno_x += vel_factor * math.sin(time_passed * 2)
    bno_y += vel_factor * math.cos(time_passed * 2)
    
    # Add some noise
    noise_factor = 0.05
    bno_x += random.uniform(-noise_factor, noise_factor)
    bno_y += random.uniform(-noise_factor, noise_factor)
    bno_z += random.uniform(-noise_factor, noise_factor)
    
    # Clamp values between -1 and 1
    bno_x = max(-1, min(1, bno_x))
    bno_y = max(-1, min(1, bno_y))
    bno_z = max(-1, min(1, bno_z))
    
    # Round to two decimal places
    bno_x = round(bno_x, 2)
    bno_y = round(bno_y, 2)
    bno_z = round(bno_z, 2)

async def send_data(websocket, path):
    global altitude, temperature, velocity, acceleration, stage
    global bno_x, bno_y, bno_z
    
    while True:
        # Update telemetry data based on rocket's flight stage
        if stage == "launch":
            velocity += acceleration * 0.1
            altitude += velocity * 0.1 + random.uniform(0, 2)  # Add randomness
            temperature -= 0.05 + random.uniform(-0.01, 0.01)  # Slight random drop

            if altitude > 10000:  # Example altitude for entering coasting phase
                stage = "ascent"
                acceleration = 5  # Less acceleration after initial launch

        elif stage == "ascent":
            velocity += acceleration * 0.1 + random.uniform(-1, 1)  # Add random variation
            altitude += velocity * 0.1 + random.uniform(-1, 1)  # Add random fluctuation
            temperature -= 0.02 + random.uniform(-0.01, 0.01)  # Further cooling

            if altitude > 30000:  # Coasting phase begins
                stage = "coasting"
                acceleration = 0  # No more thrust in coasting

        elif stage == "coasting":
            altitude += velocity * 0.1 + random.uniform(-1, 1)  # Random fluctuation
            temperature -= 0.01 + random.uniform(-0.005, 0.005)  # Slight drop in temperature

            if altitude > 80000:  # Descent phase begins
                stage = "descent"
                acceleration = -10  # Negative acceleration for descent

        elif stage == "descent":
            velocity += acceleration * 0.1 + random.uniform(-5, 5)  # Add more random variation
            altitude += velocity * 0.1 + random.uniform(-2, 2)  # Fluctuations while descending
            if altitude > 40000:
                temperature += 0.05 + random.uniform(0, 0.1)  # Warming up as it re-enters atmosphere

            if altitude <= 0:
                altitude = 0  # Landing
                velocity = 0
                stage = "landed"

        # Update orientation
        update_orientation(0.1)  # 0.1 is the time step

        # Prepare telemetry data
        data = {
            "temperature": round(temperature, 2),
            "altitude": round(altitude, 2),
            "v_horizontal": round(velocity, 2),
            "hdop": round(random.uniform(0.5, 1.5), 2),  # HDOP for more realism
            "bno_x": bno_x,
            "bno_y": bno_y,
            "bno_z": bno_z
        }

        # Send data to the WebSocket client
        await websocket.send(json.dumps(data))
        
        # Print to console (for debugging purposes)
        print(data)
        
        # Delay for simulation
        await asyncio.sleep(0.1)

# Start the WebSocket server
start_server = websockets.serve(send_data, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print("Server started at ws://localhost:8765")
asyncio.get_event_loop().run_forever()
