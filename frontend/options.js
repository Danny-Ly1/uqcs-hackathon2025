const siteInput = document.getElementById("siteInput");
const siteList = document.getElementById("siteList");
const suggestionsBox = document.getElementById("suggestions");

// Common sites for suggestion
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
function renderList(sites) {
    siteList.innerHTML = "";
    sites.forEach(site => {
        const li = document.createElement("li");

        const textSpan = document.createElement("span");
        textSpan.textContent = site;
        textSpan.style.marginRight = "10px";

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "✖";
        removeBtn.style.cursor = "pointer";
        removeBtn.addEventListener("click", () => {
            chrome.storage.sync.get(["blockedSites"], (result) => {
                let updatedSites = (result.blockedSites || []).filter(s => s !== site);
                chrome.storage.sync.set({ blockedSites: updatedSites }, () => {
                    renderList(updatedSites);
                });
            });
        });

        li.appendChild(textSpan);
        li.appendChild(removeBtn);
        siteList.appendChild(li);
    });
}


// Load saved sites
chrome.storage.sync.get(["blockedSites"], (result) => {
    renderList(result.blockedSites || []);
});

// Show suggestions as you type
siteInput.addEventListener("input", () => {
    const query = siteInput.value.toLowerCase();
    suggestionsBox.innerHTML = "";

    if (!query) return;

    const filtered = commonSites.filter(site => site.toLowerCase().includes(query));
    filtered.forEach(site => {
        const div = document.createElement("div");
        div.className = "suggestion-item";
        div.textContent = site;
        div.addEventListener("click", () => {
            siteInput.value = site;
            suggestionsBox.innerHTML = "";
        });
        suggestionsBox.appendChild(div);
    });
});

// Add site button logic
document.getElementById("addSite").addEventListener("click", () => {
    const site = siteInput.value.trim();
    if (!site) return;

    chrome.storage.sync.get(["blockedSites"], (result) => {
        let sites = result.blockedSites || [];
        if (!sites.includes(site)) {
            sites.push(site);
            chrome.storage.sync.set({ blockedSites: sites }, () => {
                renderList(sites);
                siteInput.value = "";
                suggestionsBox.innerHTML = "";
            });
        }
    });
});
