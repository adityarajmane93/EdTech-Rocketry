# EdTech Rocketry
 Submission as a part of Telemetry Odyssey


Electron apps follow the same general structure as other Node.js projects. Start by creating a folder and initializing an npm package.

npm
Yarn
mkdir my-electron-app && cd my-electron-app
npm init

The interactive init command will prompt you to set some fields in your config. There are a few rules to follow for the purposes of this tutorial:

entry point should be main.js.
author and description can be any value, but are necessary for app packaging.
Your package.json file should look something like this:

{
  "name": "my-electron-app",
  "version": "1.0.0",
  "description": "Hello World!",
  "main": "main.js",
  "author": "Jane Doe",
  "license": "MIT"
}

Then, install the electron package into your app's devDependencies.

npm
Yarn
npm install --save-dev electron

Note: If you're encountering any issues with installing Electron, please refer to the Advanced Installation guide.

Finally, you want to be able to execute Electron. In the scripts field of your package.json config, add a start command like so:

{
  "scripts": {
    "start": "electron ."
  }
}

This start command will let you open your app in development mode.

npm
Yarn
npm start

Note: This script tells Electron to run on your project's root folder. At this stage, your app will immediately throw an error telling you that it cannot find an app to run.

Run the main process
The entry point of any Electron application is its main script. This script controls the main process, which runs in a full Node.js environment and is responsible for controlling your app's lifecycle, displaying native interfaces, performing privileged operations, and managing renderer processes (more on that later).
