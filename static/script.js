let failCount = 0;
const maxAttempts = 5;

function startConversation() {
    const statusElement = document.getElementById("status");
    const responseElement = document.getElementById("response");

    statusElement.innerText = "Listening...";

    fetch('/voice-command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            statusElement.innerText = "Error: " + data.error;
            failCount++;
            if (failCount < maxAttempts) {
                setTimeout(startConversation, 1000);  // Retry after 1 second
            } else {
                statusElement.innerText = "Maximum attempts reached. Please refresh to try again.";
            }
        } else {
            statusElement.innerText = "You said: " + data.command;
            responseElement.innerText = "Assistant: " + data.response;
            failCount = 0;  // Reset fail count if successful
            setTimeout(startConversation, 1000);  // Continue the conversation after 1 second
        }
    })
    .catch(error => {
        statusElement.innerText = "An error occurred.";
        console.error('Error:', error);
    });
}

document.getElementById("start-btn").addEventListener("click", function () {
    failCount = 0;  // Reset fail count on new conversation
    startConversation();  // Start the continuous conversation
});
