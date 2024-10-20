let failCount = 0;
const maxAttempts = 5;

function startConversation() {
    const responseElement = document.getElementById("response");

    fetch('/voice-command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            responseElement.innerText = data.error;
            failCount++;
            if (failCount < maxAttempts) {
                setTimeout(startConversation, 1000);  // Retry after 1 second
            } else {
                responseElement.innerText = "Maximum attempts reached. Please refresh to try again.";
            }
        } else {
            responseElement.innerText = "Assistant: " + data.response;
            failCount = 0;  // Reset fail count if successful
            setTimeout(startConversation, 1000);  // Continue the conversation after 1 second
        }
    })
    .catch(error => {
        responseElement.innerText = "An error occurred.";
        console.error('Error:', error);
    });
}

document.getElementById('start-btn').addEventListener('click', function() {
    failCount = 0;  // Reset fail count on new conversation
    startConversation();  // Start the continuous conversation

    // Hide the button
    document.getElementById('start-btn').classList.add('hidden');

    // Show the balls to start the juggling animation
    const jugglingBalls = document.getElementById('juggling-balls');
    jugglingBalls.classList.remove('hidden');

    // Start the juggling animation by adding the animation class
    jugglingBalls.querySelectorAll('.ball').forEach(ball => {
        ball.style.animation = 'juggling 1s infinite ease-in-out'; // Add animation
    });

    document.getElementById('response').innerText = "";  // Clear response area
});
