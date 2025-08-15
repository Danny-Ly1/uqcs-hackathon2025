const siteInput = document.getElementById("siteInput");
const siteList = document.getElementById("siteList");
const suggestionsBox = document.getElementById("suggestions");

// Common sites for suggestion
const commonSites = [
    "facebook.com", "twitter.com", "instagram.com", "tiktok.com",
    "reddit.com", "youtube.com", "netflix.com", "discord.com",
    "pinterest.com", "tumblr.com", "roblox.com", "twitch.tv"
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
