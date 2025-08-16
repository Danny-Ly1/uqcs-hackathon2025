import { SW_MESSAGE_TYPES } from './lib/constants.js';
import * as store from './lib/store.js';

const siteInputTextbox = document.getElementById("siteInput");
const siteList = document.getElementById("siteList");
const suggestionsBox = document.getElementById("suggestions");
const powerButton = document.getElementById("powerButton");
const powerButtonImg = document.getElementById("powerButtonImg");
const filterButton = document.getElementById("filterButton");
const returnButton = document.getElementById("returnButton");
const loginButton = document.getElementById("loginButton");
const newUserButton = document.getElementById("newUserButton");

const loginUsernameInputTextbox = document.getElementById("loginUsernameInput");
const loginPasswordInputTextbox = document.getElementById("loginPasswordInput");
const registerUsernameInputTextbox = document.getElementById("registerUsernameInput");
const registerPasswordInputTextbox = document.getElementById("registerPasswordInput");

const groupIdInputTextbox = document.getElementById("groupIdInput");
const joinGroupBtn = document.getElementById('joinGroupBtn');
const newGroupBtn = document.getElementById('newGroupBtn');

// Common sites for suggestion
// Should all be lowercase for comparison against user input
const commonSites = [
    // Social Media
    "facebook.com",
    "twitter.com",
    "x.com",            // new Twitter domain
    "instagram.com",
    "tiktok.com",
    "snapchat.com",
    "pinterest.com",
    "tumblr.com",
    "threads.net",
    "mastodon.social",

    // Video & Streaming
    "youtube.com",
    "netflix.com",
    "twitch.tv",
    "hulu.com",
    "disneyplus.com",
    "primevideo.com",
    "hbomax.com",
    "crunchyroll.com",
    "vimeo.com",

    // News & Clickbait
    "buzzfeed.com",
    "huffpost.com",
    "dailymail.co.uk",
    "theguardian.com",
    "nytimes.com",
    "washingtonpost.com",
    "cnn.com",
    "bbc.com",

    // Shopping & Deals
    "amazon.com",
    "ebay.com",
    "etsy.com",
    "aliexpress.com",
    "walmart.com",
    "target.com",
    "bestbuy.com",
    "wish.com",

    // Forums & Communities
    "reddit.com",
    "quora.com",
    "stackexchange.com",
    "4chan.org",
    "9gag.com",
    "imgur.com",

    // Gaming
    "roblox.com",
    "epicgames.com",
    "store.steampowered.com",
    "battle.net",
    "minecraft.net",
    "leagueoflegends.com",

    // Messaging
    "discord.com",
    "messenger.com",
    "whatsapp.com",
    "telegram.org",
    "signal.org",

    // Misc Time Wasters
    "boredpanda.com",
    "theonion.com",
    "knowyourmeme.com",
    "popcrush.com"
];

const makeVisibleById = id => document.getElementById(id).classList.remove("hidden");
const makeInvisibleById = id => document.getElementById(id).classList.add("hidden");

const render = async () => {
    if (await store.isLoggedIn()) {
        if (await store.isInGroup()) {
            // render home screen
            makeInvisibleById('groupDetailsContainer');
            makeInvisibleById('userDetailsContainer');
            makeInvisibleById('filterScreenContainer');
            makeVisibleById('mainScreenContainer');
            return renderHomeScreen();
        }

        // render group on-boarding page
        makeInvisibleById('mainScreenContainer');
        makeInvisibleById('filterScreenContainer');
        makeInvisibleById('userDetailsContainer');
        makeVisibleById('groupDetailsContainer');
        return;
    }

    // render user on-boarding page
    makeInvisibleById('groupDetailsContainer');
    makeInvisibleById('mainScreenContainer');
    makeInvisibleById('filterScreenContainer');
    makeVisibleById('userDetailsContainer');
    return;
}

// Render filter list and button state
const renderHomeScreen = async () => {
    // Render filter list
    siteList.innerHTML = "";
    (await store.getFilterList()).forEach(filter => {
        const li = document.createElement("li");

        const textSpan = document.createElement("span");
        textSpan.textContent = filter.url;
        textSpan.style.marginRight = "10px";

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "✖";
        removeBtn.style.cursor = "pointer";
        removeBtn.addEventListener("click", async (e) => {
            // Implement remove button logic
            await store.removeFilterById(filter.id);
            render();
            updateChromeBlocklist();
        });

        li.appendChild(textSpan);
        li.appendChild(removeBtn);
        siteList.appendChild(li);
    });

    // Render button state
    const lockInState = await store.getLockedInState();
    powerButtonImg.src = lockInState.lockedIn ?
        "assets/Powerbutton-Green.png" : "assets/Powerbutton-Red.png";
}

// Handle siteInputTextbox input events to show suggestions as you type
const provideSuggestions = async (e) => {
    // Clear suggestion box of previous input
    suggestionsBox.innerHTML = "";

    // Clean up user input
    const query = siteInputTextbox.value.trim().toLowerCase();
    if (!query) return;

    const siteSuggestions = commonSites.filter(site => site.toLowerCase().includes(query));
    for (const suggestion of siteSuggestions) {
        // Populate suggestionsBox with filtered suggestions
        const suggestionDiv = document.createElement("div");
        suggestionDiv.className = "suggestion-item";
        suggestionDiv.textContent = suggestion;
        suggestionDiv.addEventListener("click", () => {
            siteInputTextbox.value = suggestion;
            suggestionsBox.innerHTML = "";
        });

        suggestionsBox.appendChild(suggestionDiv);
    }
}

siteInputTextbox.addEventListener("input", provideSuggestions);

// Add site button logic
const handleAddSiteBtnClick = async (e) => {
    // Ensure we're not dealing trying to add plain whitespace
    const siteUrl = siteInputTextbox.value.trim();
    if (!siteUrl) return;

    // Only add site when the site isn't in our filter list
    if (await store.isURLInFilterList(siteUrl)) {
        siteInputTextbox.value = "";
        suggestionsBox.innerHTML = "";

        return;
    }

    await store.addFilter(siteUrl);

    // Update shown list and ruleset
    await Promise.all([render(), updateChromeBlocklist()]);

    // Cleanup user input
    siteInputTextbox.value = "";
    suggestionsBox.innerHTML = "";
}

const handlePowerBtnClick = async () => {
    // TODO: CHANGE ME
    // Lock-in for 5 seconds
    await store.lockIn(5);
    await render();
}

function handleFilterButton() {
    document.getElementById('mainScreenContainer').classList.add("hidden");
    document.getElementById('filterScreenContainer').classList.remove("hidden");
}

function handleReturnButton() {
    document.getElementById('filterScreenContainer').classList.add("hidden");
    document.getElementById('mainScreenContainer').classList.remove("hidden");
}

document.getElementById("addSite").addEventListener("click", handleAddSiteBtnClick);
powerButton.addEventListener("click", handlePowerBtnClick);
filterButton.addEventListener("click", handleFilterButton);
returnButton.addEventListener("click", handleReturnButton);

// User Details Page
// attempt login
async function handleLoginBtnClick (e) {
    const res = await store.attemptLoginOrRegister(loginUsernameInputTextbox.value, loginPasswordInputTextbox.value, false);
    if (res) {
        console.log('DEBUG: is in group?', await store.isInGroup());
        console.log('DEBUG: logged in?', await store.isLoggedIn());
        await render();
    }
}

async function handleNewUserBtnClick (e) {
    const res = await store.attemptLoginOrRegister(registerUsernameInputTextbox.value, registerPasswordInputTextbox.value, true);
    if (res) {
        console.log('DEBUG: is in group?', await store.isInGroup());
        console.log('DEBUG: logged in?', await store.isLoggedIn());
        await render();
    }
}
loginButton.addEventListener("click", handleLoginBtnClick);
newUserButton.addEventListener("click", handleNewUserBtnClick);

// Group Sign-on Page
newGroupBtn.addEventListener("click", async function (e) {
    const res = await store.attemptNewGroup();
    if (res) {
        console.log('DEBUG: created new group');
        console.log('DEBUG: is in group?', await store.isInGroup());
        await render();
    }
});

joinGroupBtn.addEventListener("click", async function (e) {
    const res = await store.attemptJoinGroup(groupIdInputTextbox.value);
    if (res) {
        console.log('DEBUG: joined existing group');
        console.log('DEBUG: is in group?', await store.isInGroup());
        await render();
    }
});

// Populates Chrome blacklist with list from storage cache
const updateChromeBlocklist = async () => {
    // Find all old rule IDs so we can clear them
    const oldRules = await chrome.declarativeNetRequest.getDynamicRules();
    const oldRuleIds = oldRules.map((rule) => rule.id);

    const ruleSet = [];
    const filterList = await store.getFilterList();
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

    await chrome.declarativeNetRequest.updateDynamicRules({
        removeRuleIds: oldRuleIds,
        addRules: ruleSet,
    });
}

// Mainline
(async () => {
    // Render page elements and update Chrome ruleset
    await render();
    await updateChromeBlocklist();
})();

chrome.runtime.onMessage.addListener((message, _sender, _sendResponse) => {
    if(message.type === undefined) {
        return;
    }

    switch(message.type) {
        case SW_MESSAGE_TYPES.CS_STORE_CHANGED:
            render();
            break;
        default:
            throw new Error('unknown msg type')
    }
});
