const siteInputTextbox = document.getElementById("siteInput");
const siteList = document.getElementById("siteList");
const suggestionsBox = document.getElementById("suggestions");

const storageCache = {};
// Returns a promise until the storageCache is initialised
const initStorageCache = chrome.storage.local.get().then((items) => {
    // Initialise the storageCache if the required key doesn't exist
    if (!items.blockedSites) {
        console.log('Extension local storage uninitialised, initialising...');

        storageCache.blockedSites = [];
        chrome.storage.local.set(storageCache);

        return;
    }

    Object.assign(storageCache, items);
});

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

// Render saved sites in the blocked list
const renderList = async () => {
    siteList.innerHTML = "";
    storageCache.blockedSites.forEach(site => {
        const li = document.createElement("li");

        const textSpan = document.createElement("span");
        textSpan.textContent = site;
        textSpan.style.marginRight = "10px";

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "✖";
        removeBtn.style.cursor = "pointer";
        removeBtn.addEventListener("click", async (e) => {
            // Implement remove button logic
            storageCache.blockedSites = storageCache.blockedSites.filter(s => s !== site);
            await chrome.storage.local.set(storageCache);
            renderList();
        });

        li.appendChild(textSpan);
        li.appendChild(removeBtn);
        siteList.appendChild(li);
    });
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
    const site = siteInputTextbox.value.trim();
    if (!site) return;

    // Only add site when the site isn't in our existing list
    if (!storageCache.blockedSites.includes(site)) {
        storageCache.blockedSites.push(site);
    } else {
        // Cleanup
        siteInputTextbox.value = "";
        suggestionsBox.innerHTML = "";

        return;
    }

    await chrome.storage.local.set(storageCache);

    // Update shown list and ruleset
    await Promise.all([renderList(), updateChromeBlocklist()]);

    // Cleanup user input
    siteInputTextbox.value = "";
    suggestionsBox.innerHTML = "";
}

document.getElementById("addSite").addEventListener("click", handleAddSiteBtnClick);

// Populates Chrome blacklist with list from storage cache
const updateChromeBlocklist = async () => {
    // Find all old rule IDs so we can clear them
    const oldRules = await chrome.declarativeNetRequest.getDynamicRules();
    const oldRuleIds = oldRules.map((rule) => rule.id);

    const ruleSet = [];
    for(let i = 0; i < storageCache.blockedSites.length; i++) {
        ruleSet.push({
            id: i + 1, // Ruleset ID cannot equal 0
            priority: 1,
            action: {
              type: "redirect",
              redirect: { extensionPath: `/blocked.html?host=${storageCache.blockedSites[i]}` },
            },
            condition: {
              urlFilter: `||${storageCache.blockedSites[i]}/`,
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
    // Render saved sites, and load them into Chrome ruleset
    await initStorageCache;
    renderList();
    updateChromeBlocklist();

    document.getElementById('mainScreenContainer').style.visibility = 'visible';
})();
