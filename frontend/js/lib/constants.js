// number enum
export const SW_MESSAGE_TYPES = Object.freeze({
    // SW_* implies msg intended for service worker
    // CS_* implies msg intended for content script

    // Get the SW to set a Chrome alarm and unlock the lockInState in the future
    SW_SET_UNLOCK_ALARM: 0,

    // Notify the content script that the store/cache has changed
    CS_STORE_CHANGED: 1,
});

export const API_ENDPOINT = 'http://10.89.76.206:5001';
