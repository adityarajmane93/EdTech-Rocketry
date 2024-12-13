const { ipcRenderer } = require('electron');

let scene, camera, renderer, rocket;
let ws;
let streaming = true;

// Data arrays for graphs
const timeData = [];
const altitudeData = [];
const temperatureData = [];
const velocityData = [];

document.addEventListener("DOMContentLoaded", () => {
    const temperatureElement = document.getElementById("temperature");
    const altitudeElement = document.getElementById("altitude");
    const vHorizontalElement = document.getElementById("v_horizontal");
    const hdopElement = document.getElementById("hdop");
    const toggleStreamButton = document.getElementById("toggle-stream");
    const closeAppButton = document.getElementById("close-app");
    const altitudeProgressBar = document.getElementById('altitude-progress-bar');
    const altitudeDisplay = document.getElementById('altitude-display');

    // Set up the Plotly thermometer (gauge) for temperature
    const temperatureThermometer = document.getElementById('temperature-thermometer');

    const temperatureGaugeData = {
        type: "indicator",
        mode: "gauge+number",
        value: 0,
        title: { text: "Temperature (°C)", font: { size: 24 } },
        gauge: {
            axis: { range: [-30, 50], tickwidth: 1, tickcolor: "black" },
            bar: { color: "red" },
            bgcolor: "white",
            borderwidth: 2,
            bordercolor: "gray",
            steps: [
                { range: [-30, 0], color: "#d9f0ff" },
                { range: [0, 25], color: "#f5f5dc" },
                { range: [25, 50], color: "#ffcccb" }
            ],
            threshold: {
                line: { color: "red", width: 4 },
                thickness: 0.75,
                value: 50
            }
        }
    };

    Plotly.newPlot(temperatureThermometer, [temperatureGaugeData]);

    // Initialize 3D Rocket
    init3DRocket();

    // Initialize line graphs
    const altitudeGraph = document.getElementById('altitude-graph');
    const temperatureGraph = document.getElementById('temperature-graph');
    const velocityGraph = document.getElementById('velocity-graph');

    const altitudeTrace = {
        x: timeData,
        y: altitudeData,
        mode: 'lines',
        name: 'Altitude',
        line: { color: 'blue' }
    };

    const temperatureTrace = {
        x: timeData,
        y: temperatureData,
        mode: 'lines',
        name: 'Temperature',
        line: { color: 'red' }
    };

    const velocityTrace = {
        x: timeData,
        y: velocityData,
        mode: 'lines',
        name: 'Velocity',
        line: { color: 'green' }
    };

    Plotly.newPlot(altitudeGraph, [altitudeTrace], { title: 'Altitude vs Time' });
    Plotly.newPlot(temperatureGraph, [temperatureTrace], { title: 'Temperature vs Time' });
    Plotly.newPlot(velocityGraph, [velocityTrace], { title: 'Velocity vs Time' });

    function init3DRocket() {
        const container = document.getElementById('rocket-container');
        
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xffffff);  // Set background to white

        camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        camera.position.set(0, 2, 5);
        camera.lookAt(0, 0, 0);

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        // Add grid
        const gridHelper = new THREE.GridHelper(10, 10, 0xaaaaaa, 0xdddddd);
        scene.add(gridHelper);

        // Add ambient light
        const ambientLight = new THREE.AmbientLight(0x404040);
        scene.add(ambientLight);

        // Add directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(1, 1, 1).normalize();
        scene.add(directionalLight);

        // Create a single cone-shaped geometry for the rocket
        const geometry = new THREE.ConeGeometry(0.3, 1.5, 32);
        const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        rocket = new THREE.Mesh(geometry, material);
        
        // Position the rocket above the grid
        rocket.position.y = 0.75;
        
        scene.add(rocket);

        window.addEventListener('resize', onWindowResize, false);

        animate();
    }

    function onWindowResize() {
        const container = document.getElementById('rocket-container');
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }

    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }

    function connectWebSocket() {
        ws = new WebSocket("ws://localhost:8765");

        ws.onopen = () => {
            console.log("Connected to WebSocket server");
        };

        ws.onmessage = (event) => {
            const telemetryData = JSON.parse(event.data);
            const currentTime = new Date(); // Get current time for the x-axis

            if (streaming) {
                temperatureElement.textContent = telemetryData.temperature;
                altitudeElement.textContent = telemetryData.altitude;
                vHorizontalElement.textContent = telemetryData.v_horizontal;
                hdopElement.textContent = telemetryData.hdop;

                Plotly.update(temperatureThermometer, {
                    value: telemetryData.temperature,
                }, [0]);

                const maxAltitude = 100000;
                const altitudePercentage = (telemetryData.altitude / maxAltitude) * 100;
                altitudeProgressBar.style.height = altitudePercentage + '%';
                altitudeDisplay.textContent = telemetryData.altitude + ' m';

                rocket.rotation.x = telemetryData.bno_x * (Math.PI / 180);
                rocket.rotation.z = -telemetryData.bno_y * (Math.PI / 180);  // Negative to match right-hand rule
                rocket.rotation.y = telemetryData.bno_z * (Math.PI / 180);

                // Update graph data arrays
                timeData.push(currentTime);
                altitudeData.push(telemetryData.altitude);
                temperatureData.push(telemetryData.temperature);
                velocityData.push(telemetryData.v_horizontal);

                // Update plots (maintaining historical data)
                Plotly.update(altitudeGraph, {
                    x: [timeData],
                    y: [altitudeData]
                }, [0]);

                Plotly.update(temperatureGraph, {
                    x: [timeData],
                    y: [temperatureData]
                }, [0]);

                Plotly.update(velocityGraph, {
                    x: [timeData],
                    y: [velocityData]
                }, [0]);
            }
        };

        ws.onclose = () => {
            console.log("WebSocket connection closed");
        };
    }

    connectWebSocket();

    toggleStreamButton.addEventListener("click", () => {
        streaming = !streaming;
        toggleStreamButton.textContent = streaming ? "Stop Streaming" : "Start Streaming";

        if (!streaming && ws) {
            ws.close();
        } else if (streaming) {
            connectWebSocket();
        }
    });

    closeAppButton.addEventListener("click", () => {
        ipcRenderer.send('close-app');
    });
});
