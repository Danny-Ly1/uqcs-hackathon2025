'use strict'
let browserStoreInit = false;
const cache = {};

// This should be called in every imported function first
export const waitForBrowserStoreInit = async () => {
    if (browserStoreInit) return;
    browserStoreInit = true;

    const browserStore = await chrome.storage.local.get();

    // Initialise the storageCache if the required key doesn't exist
    if (!browserStore.filterList) {
        console.log('Extension local storage uninitialised, initialising...');

        chrome.storage.local.clear();

        cache.filterList = [];
        chrome.storage.local.set(cache);

        return;
    }

    Object.assign(cache, browserStore);
}

// TYPES:
// filter: {id: number (greater than 0, integer), url: string}
// filterList: filter[]

// id of filterList object shall be provided
export const removeFilterById = async (filterId) => {
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
    console.log(cache);
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
    cache.filterList.push(newFilter);
    await chrome.storage.local.set(cache);

    return newFilter;
}

export const getServerFilterList = async () => {
    // TODO: replace local list with server filter list
}

// returns array of filter object
export const getFilterList = async () => {
    // Return deep copy
    return JSON.parse(JSON.stringify(cache.filterList));
}
