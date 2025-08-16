'use strict'

// SW is responsible for
// - heartbeat to keep the extension active 24/7
// - lockedinstate updates from server
//      - client side lockedinstate transitions after timer elapse
// - filter list updates

import { SW_MESSAGE_TYPES, WS_ENDPOINT } from "./js/lib/constants.js";
import * as store from './js/lib/store.js';

chrome.runtime.onMessage.addListener((message, _sender, _sendResponse) => {
    if(message.type === undefined) {
        return;
    }

    switch (message.type) {
        case SW_MESSAGE_TYPES.SW_SET_UNLOCK_ALARM:
            const unlockEpochMs = (message.unlockTimeEpoch * 1000) + 150;
            chrome.alarms.create('unlock_alarm', {when: unlockEpochMs});
            break;
        default:
            throw new Error('unknown msg type')
    }
});

chrome.alarms.onAlarm.addListener(async alarm => {
    if (alarm.name === 'unlock_alarm') {
        await store.updateLockInState();
        try {
            await chrome.runtime.sendMessage({type: SW_MESSAGE_TYPES.CS_STORE_CHANGED});
        } catch (err) {
            // Popup might not be open, so just catch this potential error
            if (err.message === "Could not establish connection. Receiving end does not exist.") {
                return;
            }

            throw err;
        }

        return;
    }

    throw new Error('Unknown Chrome alarm fired');
});

chrome.runtime.onInstalled.addListener(({ reason }) => {
    if (reason === 'install') {
        // Initialise store on extension install
        store.refreshCache();
    }
});

let socket = null;
let socketKeepaliveInterval = null;

async function handleSocketOpen(e) {
    socket.send('ping');

    socketKeepaliveInterval = setInterval(() => {
        socket.send('ping');
    }, 15*1000);
}

async function handleSocketClose(e) {
    console.log("WebSocket closed: ", e);
    socket = null;
    clearInterval(socketKeepaliveInterval);
}

async function handleSocketError(e) {
    console.log("WebSocket closed due to error: ", e);
    socket = null;
    clearInterval(socketKeepaliveInterval);
}

async function handleSocketMessage(e) {
    console.log("Received WebSocket message from server: ", e.data)
}

const socketConnect = () => {
    if (socket) { return; }
    socket = new WebSocket(WS_ENDPOINT);

    socket.addEventListener('open', handleSocketOpen);
    socket.addEventListener('close', handleSocketClose);
    socket.addEventListener('error', handleSocketError);
    socket.addEventListener('message', handleSocketMessage);
}
socketConnect();
