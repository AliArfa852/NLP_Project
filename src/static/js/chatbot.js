/**
 * Multilingual Emotion Chatbot JavaScript
 * Additional functionality for the chatbot frontend
 */

// Keep track of chat history for potential export
const chatHistory = [];

// Track emotion statistics 
const emotionStats = {
    happy: 0,
    sad: 0,
    neutral: 0,
    angry: 0
};

// Function to initialize speech recognition if available
function initSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        // Speech recognition not supported, hide the button
        const speechButton = document.getElementById('speechButton');
        if (speechButton) {
            speechButton.style.display = 'none';
        }
        return null;
    }

    // Create speech recognition object
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // Configure recognition
    recognition.continuous = false;
    recognition.interimResults = false;
    
    // Set language based on the selected language
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        // Map our language codes to speech recognition language codes
        const languageMap = {
            'english': 'en-US',
            'urdu': 'ur-PK',  // Fallback to English if Urdu not available
            'hindi': 'hi-IN',
            'punjabi': 'pa-IN'
        };
        
        recognition.lang = languageMap[languageSelect.value] || 'en-US';
        
        // Update language when selection changes
        languageSelect.addEventListener('change', function() {
            recognition.lang = languageMap[this.value] || 'en-US';
        });
    }
    
    return recognition;
}

// Function to export chat history as a text file
function exportChatHistory() {
    if (chatHistory.length === 0) {
        alert('No chat history to export.');
        return;
    }
    
    let content = "Multilingual Emotion Chatbot - Chat History\n";
    content += "=" + "=".repeat(40) + "\n\n";
    
    chatHistory.forEach((entry, index) => {
        content += `[${entry.timestamp}]\n`;
        content += `${entry.sender === 'user' ? 'You' : 'Bot'}: ${entry.message}\n`;
        
        if (entry.emotions && entry.emotions.length > 0) {
            content += `Emotions: ${entry.emotions.join(', ')}\n`;
        }
        
        if (entry.personality) {
            content += `Personality: ${entry.personality}\n`;
        }
        
        if (entry.language) {
            content += `Language: ${entry.language}\n`;
        }
        
        content += "\n";
    });
    
    // Create a download link
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_history_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Function to generate an emotion chart
function generateEmotionChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Only generate chart if we have emotions
    if (Object.values(emotionStats).reduce((a, b) => a + b, 0) === 0) {
        container.innerHTML = '<p>No emotion data available yet.</p>';
        return;
    }
    
    // Create canvas for chart
    container.innerHTML = '<canvas id="emotionChart"></canvas>';
    const ctx = document.getElementById('emotionChart').getContext('2d');
    
    // Create the chart using Chart.js (if available)
    if (typeof Chart !== 'undefined') {
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(emotionStats).map(emotion => 
                    emotion.charAt(0).toUpperCase() + emotion.slice(1)
                ),
                datasets: [{
                    data: Object.values(emotionStats),
                    backgroundColor: [
                        '#FFD700',  // happy - gold
                        '#6495ED',  // sad - blue
                        '#A9A9A9',  // neutral - gray
                        '#FF6347'   // angry - red
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Detected Emotions'
                }
            }
        });
    } else {
        // Fallback if Chart.js is not available
        let html = '<div class="emotion-stats">';
        for (const [emotion, count] of Object.entries(emotionStats)) {
            if (count > 0) {
                const percentage = Math.round(count / Object.values(emotionStats).reduce((a, b) => a + b, 0) * 100);
                html += `
                    <div class="emotion-stat-item">
                        <div class="emotion-name">${emotion.charAt(0).toUpperCase() + emotion.slice(1)}</div>
                        <div class="emotion-bar">
                            <div class="emotion-bar-fill emotion-${emotion}" style="width: ${percentage}%"></div>
                        </div>
                        <div class="emotion-count">${count} (${percentage}%)</div>
                    </div>
                `;
            }
        }
        html += '</div>';
        container.innerHTML = html;
    }
}

// Function to save settings to localStorage
function saveSettings() {
    const settings = {
        language: document.getElementById('languageSelect').value,
        personality: document.getElementById('personalitySelect').value,
        learningEnabled: document.getElementById('rlToggle').checked
    };
    
    localStorage.setItem('chatbotSettings', JSON.stringify(settings));
}

// Function to load settings from localStorage
function loadSettings() {
    const savedSettings = localStorage.getItem('chatbotSettings');
    if (!savedSettings) return;
    
    try {
        const settings = JSON.parse(savedSettings);
        
        // Apply saved settings
        const languageSelect = document.getElementById('languageSelect');
        const personalitySelect = document.getElementById('personalitySelect');
        const rlToggle = document.getElementById('rlToggle');
        
        if (languageSelect && settings.language) {
            languageSelect.value = settings.language;
        }
        
        if (personalitySelect && settings.personality) {
            personalitySelect.value = settings.personality;
            
            // Update description
            const personalityDescription = document.getElementById('personalityDescription');
            if (personalityDescription) {
                const personalities = JSON.parse(personalitySelect.getAttribute('data-personalities'));
                const selectedPersonality = personalities.find(p => p.id === settings.personality);
                if (selectedPersonality) {
                    personalityDescription.textContent = selectedPersonality.description;
                }
            }
        }
        
        if (rlToggle && settings.learningEnabled !== undefined) {
            rlToggle.checked = settings.learningEnabled;
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize speech recognition
    const recognition = initSpeechRecognition();
    
    // Add speech button if speech recognition is available
    if (recognition) {
        const inputGroup = document.querySelector('.input-group');
        if (inputGroup) {
            const speechButton = document.createElement('button');
            speechButton.id = 'speechButton';
            speechButton.className = 'btn btn-outline-secondary';
            speechButton.innerHTML = '<i class="bi bi-mic"></i>';
            speechButton.title = 'Speak';
            
            // Insert before send button
            const sendButton = document.getElementById('sendButton');
            if (sendButton) {
                inputGroup.insertBefore(speechButton, sendButton);
            }
            
            // Add speech recognition event handlers
            speechButton.addEventListener('click', function() {
                const userInput = document.getElementById('userInput');
                
                if (this.classList.contains('recording')) {
                    // Stop recording
                    recognition.stop();
                    this.classList.remove('recording');
                    this.innerHTML = '<i class="bi bi-mic"></i>';
                } else {
                    // Start recording
                    recognition.start();
                    this.classList.add('recording');
                    this.innerHTML = '<i class="bi bi-mic-fill"></i>';
                    userInput.placeholder = 'Listening...';
                }
            });
            
            recognition.onresult = function(event) {
                const userInput = document.getElementById('userInput');
                const speechButton = document.getElementById('speechButton');
                
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
                
                // Reset button
                speechButton.classList.remove('recording');
                speechButton.innerHTML = '<i class="bi bi-mic"></i>';
                userInput.placeholder = 'Type a message...';
            };
            
            recognition.onend = function() {
                const speechButton = document.getElementById('speechButton');
                const userInput = document.getElementById('userInput');
                
                // Reset button
                if (speechButton) {
                    speechButton.classList.remove('recording');
                    speechButton.innerHTML = '<i class="bi bi-mic"></i>';
                }
                
                if (userInput) {
                    userInput.placeholder = 'Type a message...';
                }
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                
                const speechButton = document.getElementById('speechButton');
                const userInput = document.getElementById('userInput');
                
                // Reset button
                if (speechButton) {
                    speechButton.classList.remove('recording');
                    speechButton.innerHTML = '<i class="bi bi-mic"></i>';
                }
                
                if (userInput) {
                    userInput.placeholder = 'Type a message...';
                }
                
                // Show error message
                alert('Speech recognition error: ' + event.error);
            };
        }
    }
    
    // Add export button
    const statsTab = document.getElementById('stats');
    if (statsTab) {
        const exportButton = document.createElement('button');
        exportButton.id = 'exportChatBtn';
        exportButton.className = 'btn btn-outline-secondary mt-3 ms-2';
        exportButton.innerHTML = '<i class="bi bi-download"></i> Export Chat';
        exportButton.addEventListener('click', exportChatHistory);
        
        // Add after refresh button
        const refreshButton = document.getElementById('refreshStatsBtn');
        if (refreshButton) {
            refreshButton.parentNode.insertBefore(exportButton, refreshButton.nextSibling);
        }
    }
    
    // Add settings save functionality
    const settingsElements = ['languageSelect', 'personalitySelect', 'rlToggle'];
    settingsElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', saveSettings);
        }
    });
    
    // Load saved settings
    loadSettings();
});