const userInput = document.getElementById("userInput");
const addWebsite = document.getElementById("addWebsite");
const myList = document.getElementById("myList");

addWebsite.addEventListener('click', function() {
    const textValue = userInput.value;

    if (textValue.trim() !== '') { // Prevent adding empty items
        const newListItem = document.createElement('li');
        const textNode = document.createTextNode(textValue);
        newListItem.appendChild(textNode);
        myList.appendChild(newListItem);

        userInput.value = ''; // Clear the input field after adding
    }
});