document.addEventListener("DOMContentLoaded", function() {
    animateStatistics();
    changeGlowingText();
    
    const sections = document.querySelectorAll("section");

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("section-animate");
            }
        });
    });

    sections.forEach(section => {
        observer.observe(section);
    });
});

// Animation for statistics counter
function animateStatistics() {
    const counters = [
        { id: "obesityCount", target: 150 },
        { id: "unhealthyCount", target: 200 },
        { id: "healthTipsCount", target: 300 }
    ];

    counters.forEach(counter => {
        let count = 0;
        const target = counter.target;
        const element = document.getElementById(counter.id);

        const interval = setInterval(() => {
            count++;
            element.textContent = count;
            if (count === target) {
                clearInterval(interval);
            }
        }, 10);
    });
}

// Glowing text effect
function changeGlowingText() {
    const messages = [
        "Obesity is a serious health concern!",
        "Stay active for a healthy life!",
        "Nutrition is key to wellness!",
        "Regular check-ups are essential!",
    ];

    let index = 0;
    setInterval(() => {
        document.getElementById('glowing-text').textContent = messages[index];
        index = (index + 1) % messages.length;
    }, 600); // Change every 2 seconds
}

// Toggle Chatbot Visibility
function toggleChatbot() {
    const chatbotWindow = document.getElementById("chatbotWindow");
    chatbotWindow.style.display = chatbotWindow.style.display === "none" || chatbotWindow.style.display === "" ? "flex" : "none";
}

// Handle User Message Input
function handleUserMessage(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

// Display User's Message and Send Bot's Response
function sendMessage() {
    const userInput = document.getElementById("userInput");
    const messageText = userInput.value.trim();

    if (messageText !== "") {
        addMessage("user", messageText);
        userInput.value = "";

        // Simulate bot response
        setTimeout(() => {
            addMessage("bot", "Thank you for reaching out! How can I assist you?");
        }, 1000); // 1-second delay for a more realistic response
    }
}

// Add Message to Chat Window
function addMessage(sender, message) {
    const chatbotMessages = document.getElementById("chatbotMessages");
    const messageElement = document.createElement("div");
    messageElement.classList.add(sender === "bot" ? "bot-message" : "user-message");
    messageElement.textContent = message;

    chatbotMessages.appendChild(messageElement);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}





function toggleChatbot() {
    const chatbot = document.getElementById("chatbot");
    chatbot.style.display = chatbot.style.display === "none" ? "block" : "none";
}

async function handleUserInput() {
    const userInput = document.getElementById("userInput").value.toLowerCase();
    const responseDiv = document.getElementById("response");
    responseDiv.innerHTML = "";  // Clear previous responses

    // Check if user input is "fitness plan"
    if (userInput.includes("fitness plan")) {
        window.location.href = '/fit';
    } else {
        responseDiv.innerHTML = "I'm here to help! Ask me about fitness plans or other health-related questions.";
    }

    // Clear the input field
    document.getElementById("userInput").value = "";
}

async function startExercise() {
    // Make an AJAX request to trigger the run-exercise endpoint
    const response = await fetch('/run-exercise', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const data = await response.json();
    alert(data.message); // Show the result in an alert (you can change this to update the UI)
}
    function handleUserInput() {
        const userInput = document.getElementById("userInput").value;
        const responseDiv = document.getElementById("response");
        
        // Add user message to the chat
        const userMessage = document.createElement("div");
        userMessage.className = "user-message";
        userMessage.textContent = userInput;
        responseDiv.appendChild(userMessage);

        // Clear input
        document.getElementById("userInput").value = "";

        // Simulate a bot response
        const botMessage = document.createElement("div");
        botMessage.className = "bot-message";
        botMessage.textContent = "I'm here to help!";
        responseDiv.appendChild(botMessage);

        // Scroll to the bottom
        responseDiv.scrollTop = responseDiv.scrollHeight;
    }

