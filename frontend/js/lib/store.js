'use strict'

import { SW_MESSAGE_TYPES, API_ENDPOINT } from "./constants.js";

const cache = {};

// This should be called before any storage operation, as we have both service worker and content scripts potentially modifying the store
export const refreshCache = async () => {
    const browserStore = await chrome.storage.local.get();

    // Initialise the storageCache if the required key doesn't exist
    if (browserStore.filterList === undefined
        || browserStore.lockInState === undefined
        || browserStore.user === undefined) {
        console.log('Extension local storage uninitialised, initialising...');

        await chrome.storage.local.clear();

        cache.filterList = [];
        cache.lockInState = {lockedIn: false, unlockTimeEpoch: 0};
        cache.user = {id: null, username: null, groupId: null};

        await chrome.storage.local.set(cache);

        return;
    }

    Object.assign(cache, browserStore);
}

// TYPES:
// filter: {id: number (greater than 0, integer), url: string}
// filterList: filter[]
// lockedInState: {lockedIn: boolean, unlockTimeEpoch: number (epoch second of unlock time)}
// user: {id: number, username: string, groupId: number}

// Returns boolean, whether user is logged in
export const isLoggedIn = async () => {
    await refreshCache();

    return (cache.user.id !== null) && (cache.user.username !== null);
}

// Returns boolean, whether user is in a group
export const isInGroup = async () => {
    await refreshCache();

    return cache.user.groupId !== null;
}

// Send credentials to server, update store and returns true if successful, returns false otherwise
export const attemptLoginOrRegister = async (username, password, register) => {
    await refreshCache();

    cache.user = {id: null, username: null, groupId: null};
    await chrome.storage.local.set(cache);

    let resp;
    try {
        resp = await fetch(register ? `${API_ENDPOINT}/user` : `${API_ENDPOINT}/user/login`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({username, password})
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }
    if (resp?.ok) {
        resp = await resp.json();
        cache.user.id = resp.id;
        cache.user.username = resp.username;
        await chrome.storage.local.set(cache);
    } else {
        // The login/register failed, stop here
        return false;
    }

    let groupResp;
    try {
        groupResp = await fetch(`${API_ENDPOINT}/users/${cache.user.id}`, {
            method: 'GET'
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }
    if (groupResp?.ok) {
        groupResp = await groupResp.json();
        cache.user.groupId = groupResp.groupId;
        await chrome.storage.local.set(cache);
    }

    return true;
}

// Attempt to create new group with user ID on server, returns false if failed, true if successful
export const attemptNewGroup = async () => {
    await refreshCache();

    let resp;
    try {
        resp = await fetch(`${API_ENDPOINT}/group`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({'initialUserId': cache.user.id})
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }
    if (resp?.ok) {
        resp = await resp.json();
        cache.user.groupId = resp.groupId;
        await chrome.storage.local.set(cache);

        return true;
    }

    return false;
}

// Attempt to join a group with user ID and group ID on server, returns false if failed, true if successful
export const attemptJoinGroup = async (groupId) => {
    await refreshCache();

    let resp;
    try {
        resp = await fetch(`${API_ENDPOINT}/users/${cache.user.id}/group`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({groupId})
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }
    if (resp?.ok) {
        resp = await resp.json();
        cache.user.groupId = resp.groupId;
        await chrome.storage.local.set(cache);

        return true;
    }

    return false;
}

// id of filterList object shall be provided
export const removeFilterById = async (filterId) => {
    await refreshCache();

    const newFilterList = cache.filterList.filter(f => f.id !== filterId);
    if (newFilterList.length === cache.filterList.length) {
        throw new Error('filterId provided does not exist');
    }

    cache.filterList = newFilterList;
    // TODO: sync with server
    await chrome.storage.local.set(cache);
}

// returns boolean based on if url is in filter list
export const isURLInFilterList = async (url) => {
    await refreshCache();

    const filtered = cache.filterList.filter(f => f.url == url);
    return filtered.length > 0;
}

// returns complete filter object
export const addFilter = async (url) => {
    if (!url) {
        throw new Error('Tried to add invalid or empty URL into filter list');
    }

    if (await isURLInFilterList(url)) {
        throw new Error('Tried to add duplicate URL into filter list');
    }

    // TODO: add filter into server so we get ID
    const newFilter = {id: Math.floor(Math.random() * (42000 - 69) + 69), url};

    await refreshCache();
    cache.filterList.push(newFilter);
    await chrome.storage.local.set(cache);

    return newFilter;
}

// Return lockedInState object
export const getLockedInState = async () => {
    await refreshCache();
    return JSON.parse(JSON.stringify(cache.lockInState));
}

// Set lock in state to true with duration
export const lockIn = async (lockInDurationSec) => {
    if (!lockInDurationSec || lockInDurationSec <= 0) {
        throw new Error('Invalid lock-in duration specified');
    }

    // TODO: set lock-in on server side, and get unlock epoch from server side
    // TODO: sync with web worker to unlock even when extension popup is not on

    await refreshCache();
    console.log(cache);
    if (cache.lockInState.lockedIn) {
        throw new Error('Cannot lock-in when already locked in!');
    }

    cache.lockInState.lockedIn = true;
    const unlockTimeEpoch = Math.floor((Date.now() / 1000) + (lockInDurationSec));
    cache.lockInState.unlockTimeEpoch = unlockTimeEpoch;

    await chrome.storage.local.set(cache);
    await chrome.runtime.sendMessage({type: SW_MESSAGE_TYPES.SW_SET_UNLOCK_ALARM, unlockTimeEpoch});
}

// Checks the current time, and compares it with the lock-in time
// Returns true, when current time is beyond unlock time
// TODO: come up with better method to do unlock when time is up
export const updateLockInState = async () => {
    await refreshCache();

    const epochSec = Date.now() / 1000;
    if ((cache.lockInState.unlockTimeEpoch - epochSec) <= 0) {
        cache.lockInState.lockedIn = false;
        await chrome.storage.local.set(cache);

        return true;
    }

    return false;
}

export const getServerFilterList = async () => {
    // TODO: replace local list with server filter list
}

export const getServerLockInState = async () => {
    // TODO: replace local state with server locked in state
}

// returns array of filter object
export const getFilterList = async () => {
    await refreshCache();

    // Return deep copy
    return JSON.parse(JSON.stringify(cache.filterList));
}
