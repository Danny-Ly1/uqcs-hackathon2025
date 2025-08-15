const userInput = document.getElementById("userInput");
const addWebsite = document.getElementById("addWebsite");
const myList = document.getElementById("myList");
const blockedWebsites = [];

// Save list
chrome.storage.sync.set({ blockedSites: ["facebook.com", "twitter.com"] });

// Get list
chrome.storage.sync.get(["blockedSites"], (result) => {
    console.log(result.blockedSites || []);
});


addWebsite.addEventListener("click", function() {
    const textValue = userInput.value;

    if (textValue.trim() !== "") { // Prevent adding empty items
        const newListItem = document.createElement("li");
        const textNode = document.createTextNode(textValue);
        newListItem.appendChild(textNode);
        myList.appendChild(newListItem);
        blockedWebsites.push(newListItem);

        userInput.value = ""; // Clear the input field after adding
    }
});