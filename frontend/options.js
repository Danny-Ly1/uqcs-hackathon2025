const siteInput = document.getElementById('siteInput');
const siteList = document.getElementById('siteList');

// Save list
chrome.storage.sync.set({ blockedSites: ["facebook.com", "twitter.com"] });

// Get list
chrome.storage.sync.get(["blockedSites"], (result) => {
    console.log(result.blockedSites || []);
});

function renderList(sites) {
    siteList.innerHTML = '';
    sites.forEach(site => {
        let li = document.createElement('li');
        li.textContent = site;
        siteList.appendChild(li);
    });
}

chrome.storage.sync.get(["blockedSites"], (result) => {
    renderList(result.blockedSites || []);
});

document.getElementById('addSite').addEventListener('click', () => {
    const site = siteInput.value.trim();
    if (!site) return;

    chrome.storage.sync.get(["blockedSites"], (result) => {
        let sites = result.blockedSites || [];
        if (!sites.includes(site)) {
            sites.push(site);
            chrome.storage.sync.set({ blockedSites: sites }, () => {
                renderList(sites);
                siteInput.value = '';
            });
        }
    });
});

siteInput.addEventListener('input', () => {
    const query = siteInput.value;
    chrome.history.search({ text: query, maxResults: 5 }, (results) => {
        // Display suggestions in a dropdown
        console.log(results.map(r => new URL(r.url).hostname));
    });
});
