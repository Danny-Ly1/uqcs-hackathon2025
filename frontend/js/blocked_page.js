'use strict'

import * as store from './lib/store.js';
import { API_ENDPOINT } from './lib/constants.js';

const params = new URLSearchParams(window.location.search);
const hostname = params.get('host');

document.getElementById('blockedHostname').textContent = hostname;

(async () => {
    // Allow redirect to actual domain when lock in expires
    const inter = setInterval(async () => {
        const lockedInState2 = await store.getLockedInState();
        if (!lockedInState2.lockedIn) {
            window.location.replace(`http://${hostname}`);
            clearInterval(inter);
        }
    }, 100);

    const lockedInState = await store.getLockedInState();
    if (lockedInState.lockedIn) {
        // Snitch on user for shame if needed
        try {
            await fetch(`${API_ENDPOINT}/groups/${await store.getGroupId()}/infraction`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({userID: (await store.getUserId()), offending_url: hostname})
            });
        } catch (err) {
            // lol
        }
    }
})()
