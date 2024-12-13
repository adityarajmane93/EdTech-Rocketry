// frontend/main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    fullscreen: true,
    webPreferences: {
      preload: path.join(__dirname, 'renderer.js'),
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  win.loadFile('index.html');

  // Listen for the 'close-app' signal and close the application
  ipcMain.on('close-app', () => {
    win.close();
  });
}

app.on('ready', createWindow);
