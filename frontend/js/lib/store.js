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

// Returns stored user groupId, may be null
export const getGroupId = async () => {
    await refreshCache();

    return cache.user.groupId;
}

// Returns stored userId, may be null
export const getUserId = async () => {
    await refreshCache();

    return cache.user.id;
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

    // TODO: more error handling?
    try {
        await fetch(`${API_ENDPOINT}/groups/${cache.user.groupId}/filter_list/${filterId}`, {
            method: 'DELETE'
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }

    await chrome.storage.local.set(cache);
}

// returns boolean based on if url is in filter list
export const isURLInFilterList = async (url) => {
    await refreshCache();

    const filtered = cache.filterList.filter(f => f.url == url);
    return filtered.length > 0;
}

// attempts to add to server, returns an empty object if there are errors
export const addFilter = async (url) => {
    if (!url) {
        throw new Error('Tried to add invalid or empty URL into filter list');
    }

    if (await isURLInFilterList(url)) {
        throw new Error('Tried to add duplicate URL into filter list');
    }

    let resp;

    try {
        resp = await fetch(`${API_ENDPOINT}/groups/${cache.user.groupId}/filter_list`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({url})
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }
    if (resp?.ok) {
        resp = await resp.json();

        const newFilter = JSON.parse(JSON.stringify(resp));

        await refreshCache();
        cache.filterList.push(newFilter);
        await chrome.storage.local.set(cache);

        return newFilter;
    }

    return {};
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

    await refreshCache();
    if (cache.lockInState.lockedIn) {
        return;
    }

    let resp;
    try {
        resp = await fetch(`${API_ENDPOINT}/group/${cache.user.groupId}/locked_in`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({timer_duration: lockInDurationSec})
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }
    if (resp?.ok) {
        resp = await resp.json();

        cache.lockInState.lockedIn = true;
        const unlockTimeEpoch = resp.unlock_time_epoch;
        cache.lockInState.unlockTimeEpoch = unlockTimeEpoch;

        await chrome.runtime.sendMessage({type: SW_MESSAGE_TYPES.SW_SET_UNLOCK_ALARM, unlockTimeEpoch});
        await chrome.storage.local.set(cache);

        return true;
    }

    return false;
}

// Checks the current time, and compares it with the lock-in time and updates the state accordingly
// Also, configures the appropriate extension icon
// Returns true, when current time is beyond unlock time
export const updateLockInState = async () => {
    await refreshCache();

    const epochSec = Date.now() / 1000;
    if ((cache.lockInState.unlockTimeEpoch - epochSec) <= 0) {
        await chrome.action.setIcon({
            path: {
                "16": "assets/icon/red/16.png",
                "48": "assets/icon/red/48.png",
                "128": "assets/icon/red/128.png" 
            }
        });
        cache.lockInState.lockedIn = false;
        await chrome.storage.local.set(cache);

        return true;
    }

    await chrome.action.setIcon({
        path: {
            "16": "assets/icon/green/16.png",
            "48": "assets/icon/green/48.png",
            "128": "assets/icon/green/128.png" 
        }
    });
    cache.lockInState.lockedIn = true;
    await chrome.storage.local.set(cache);

    return false;
}

// Attempts to pull filter list from server, returns true if successful, false if not.
export const pullFilterList = async () => {
    await refreshCache();
    let resp;

    try {
        resp = await fetch(`${API_ENDPOINT}/groups/${cache.user.groupId}/filter_list`, {
            method: 'GET'
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }
    if (resp?.ok) {
        resp = await resp.json();

        cache.filterList = JSON.parse(JSON.stringify(resp));
        await chrome.storage.local.set(cache);

        return true;
    }

    return false;
}

// Retrieve server lock in state, return true if successful, false otherwise
export const pullServerLockInState = async () => {
    await refreshCache();

    let resp;
    try {
        resp = await fetch(`${API_ENDPOINT}/group/${cache.user.groupId}/locked_in`, {
            method: 'GET'
        });
    } catch (err) {
        console.log("Request error occurred:", err);
    }
    if (resp?.ok) {
        resp = await resp.json();

        cache.lockInState.unlockTimeEpoch = resp.unlock_time_epoch;
        await chrome.storage.local.set(cache);

        await updateLockInState();

        return true;
    }

    return false;
}

// returns array of filter object
export const getFilterList = async () => {
    await refreshCache();

    // Return deep copy
    return JSON.parse(JSON.stringify(cache.filterList));
}

export const updateChromeBlocklist = async () => {
    // Find all old rule IDs so we can clear them
    const oldRules = await chrome.declarativeNetRequest.getDynamicRules();
    const oldRuleIds = oldRules.map((rule) => rule.id);

    const ruleSet = [];
    const filterList = await getFilterList();
    const lockedInState = await getLockedInState();
    if (lockedInState.lockedIn) {
        for(let i = 0; i < filterList.length; i++) {
            ruleSet.push({
                id: filterList[i].id,
                priority: 1,
                action: {
                  type: "redirect",
                  redirect: { extensionPath: `/blocked.html?host=${filterList[i].url}` },
                },
                condition: {
                  urlFilter: `||${filterList[i].url}/`,
                  resourceTypes: ["main_frame"],
                },
            });
        }
    }

    await chrome.declarativeNetRequest.updateDynamicRules({
        removeRuleIds: oldRuleIds,
        addRules: ruleSet,
    });
}
