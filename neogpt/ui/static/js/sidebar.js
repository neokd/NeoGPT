const leftSidebar = document.getElementById('leftSidebar');
const mainContent = document.getElementById('mainContent');
const toggleLeftSidebarButton = document.getElementById('toggleLeftSidebarButton');

toggleLeftSidebarButton.addEventListener('click', function () {
    leftSidebar.classList.toggle('-translate-x-full');
    mainContent.classList.toggle('-ml-60');
});

// JavaScript to toggle right sidebar
const rightSidebar = document.getElementById('rightSidebar');
const toggleRightSidebarButton = document.getElementById('toggleRightSidebarButton');

toggleRightSidebarButton.addEventListener('click', function () {
    rightSidebar.classList.toggle('translate-x-full');
    mainContent.classList.toggle('-mr-60');
});


const clearChatButton = document.getElementById('clearChatButton');

clearChatButton.addEventListener('click', function () {
    const chatHistory = sessionStorage.getItem('chatMessageHistory');
    console.log(chatHistory);
    if (chatHistory) {
        sessionStorage.removeItem('chatMessageHistory');
    }
    location.reload();
});