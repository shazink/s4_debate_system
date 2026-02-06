// S4 Multi-Agent Debate System - LIVE STREAMING
// Shows agents debating in real-time in 3 columns

const queryInput = document.getElementById('queryInput');
const charCount = document.getElementById('charCount');
const submitBtn = document.getElementById('submitBtn');
const debateSection = document.getElementById('debateSection');
const currentRound = document.getElementById('currentRound');
const resultSection = document.getElementById('resultSection');
const finalDecision = document.getElementById('finalDecision');
const finalReasoning = document.getElementById('finalReasoning');
const resultMetadata = document.getElementById('resultMetadata');

// Agent message containers
const utilityMessages = document.getElementById('utilityMessages');
const accuracyMessages = document.getElementById('accuracyMessages');
const safetyMessages = document.getElementById('safetyMessages');

// Character counter
queryInput.addEventListener('input', () => {
    const count = queryInput.value.length;
    charCount.textContent = count;
    charCount.style.color = count > 4500 ? 'var(--red-primary)' : 'var(--cyan)';
});

// Submit button
submitBtn.addEventListener('click', () => {
    const query = queryInput.value.trim();
    if (!query) {
        alert('Please enter a query');
        return;
    }

    startLiveDebate(query);
});

function startLiveDebate(query) {
    // Reset UI
    utilityMessages.innerHTML = '';
    accuracyMessages.innerHTML = '';
    safetyMessages.innerHTML = '';
    resultSection.style.display = 'none';
    debateSection.style.display = 'block';

    // Disable button
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.5';
    submitBtn.querySelector('.btn-text').textContent = 'DEBATING...';

    // Create EventSource for Server-Sent Events
    const eventSource = new EventSource('/api/debate/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
    });

    // Use fetch with streaming instead
    fetch('/api/debate/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function processStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    submitBtn.querySelector('.btn-text').textContent = 'START DEBATE';
                    return;
                }

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.substring(6));
                        handleEvent(data);
                    }
                });

                processStream();
            });
        }

        processStream();
    }).catch(error => {
        console.error('Stream error:', error);
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
        submitBtn.querySelector('.btn-text').textContent = 'START DEBATE';
        alert('Error: ' + error.message);
    });
}

function handleEvent(event) {
    console.log('Event:', event);

    switch (event.type) {
        case 'start':
            console.log('Debate started:', event.query);
            break;

        case 'round_start':
            currentRound.textContent = `ROUND ${event.round}: ${event.name.toUpperCase()}`;
            break;

        case 'agent_thinking':
            showThinking(event.agent);
            break;

        case 'agent_response':
            addAgentMessage(event.agent, 'analysis', {
                decision: event.decision,
                confidence: event.confidence,
                risk: event.risk,
                reasoning: event.reasoning
            });
            break;

        case 'challenge':
            addAgentMessage(event.challenger, 'challenge', {
                target: event.challenged,
                challenge: event.challenge
            });
            addAgentMessage(event.challenged, 'challenged', {
                from: event.challenger,
                challenge: event.challenge
            });
            break;

        case 'revision':
            addAgentMessage(event.agent, 'revision', {
                old_decision: event.old_decision,
                new_decision: event.new_decision,
                confidence_change: event.new_confidence - event.old_confidence,
                reasoning: event.reasoning
            });
            break;

        case 'final_vote':
            addAgentMessage(event.agent, 'final_vote', {
                decision: event.decision,
                confidence: event.confidence,
                risk: event.risk,
                reasoning: event.reasoning
            });
            break;

        case 'final_decision':
            showFinalDecision(event);
            break;

        case 'complete':
            console.log('Debate complete');
            break;

        case 'error':
            alert('Error: ' + event.error);
            break;
    }
}

function showThinking(agentName) {
    const container = getAgentContainer(agentName);
    const thinking = document.createElement('div');
    thinking.className = 'thinking';
    thinking.textContent = '💭 Thinking...';
    thinking.id = 'thinking-' + agentName.replace(/\s/g, '');
    container.appendChild(thinking);
    container.scrollTop = container.scrollHeight;
}

function addAgentMessage(agentName, type, data) {
    const container = getAgentContainer(agentName);

    // Remove thinking indicator
    const thinking = container.querySelector('.thinking');
    if (thinking) thinking.remove();

    const message = document.createElement('div');
    message.className = 'agent-message';

    let content = '';

    switch (type) {
        case 'analysis':
            content = `
                <div class="message-header">
                    <span>INITIAL ANALYSIS</span>
                    <span style="color: var(--cyan);">${data.decision}</span>
                </div>
                <div class="message-content">
                    <strong>Confidence:</strong> ${data.confidence.toFixed(0)}% | <strong>Risk:</strong> ${data.risk.toFixed(0)}%<br><br>
                    ${data.reasoning}
                </div>
            `;
            break;

        case 'challenge':
            content = `
                <div class="message-header">
                    <span>CHALLENGING ${data.target}</span>
                    <span style="color: var(--red-primary);">⚔️</span>
                </div>
                <div class="message-content">${data.challenge}</div>
            `;
            break;

        case 'challenged':
            content = `
                <div class="message-header">
                    <span>CHALLENGED BY ${data.from}</span>
                    <span style="color: var(--red-primary);">⚠️</span>
                </div>
                <div class="message-content" style="opacity: 0.7; font-size: 13px;">${data.challenge}</div>
            `;
            break;

        case 'revision':
            const changeIcon = data.confidence_change >= 0 ? '📈' : '📉';
            const changeColor = data.confidence_change >= 0 ? 'lime' : 'orange';
            content = `
                <div class="message-header">
                    <span>REVISION</span>
                    <span style="color: ${changeColor};">${data.old_decision} → ${data.new_decision}</span>
                </div>
                <div class="message-content">
                    <strong>Confidence Change:</strong> ${changeIcon} ${data.confidence_change >= 0 ? '+' : ''}${data.confidence_change.toFixed(0)}%<br><br>
                    ${data.reasoning}
                </div>
            `;
            break;

        case 'final_vote':
            content = `
                <div class="message-header">
                    <span>FINAL VOTE</span>
                    <span style="color: var(--cyan); font-weight: bold;">${data.decision}</span>
                </div>
                <div class="message-content">
                    <strong>Confidence:</strong> ${data.confidence.toFixed(0)}% | <strong>Risk:</strong> ${data.risk.toFixed(0)}%<br><br>
                    ${data.reasoning}
                </div>
            `;
            break;
    }

    message.innerHTML = content;
    container.appendChild(message);
    container.scrollTop = container.scrollHeight;
}

function getAgentContainer(agentName) {
    if (agentName.includes('Utility')) return utilityMessages;
    if (agentName.includes('Accuracy')) return accuracyMessages;
    if (agentName.includes('Safety')) return safetyMessages;
    return utilityMessages;
}

function showFinalDecision(event) {
    resultSection.style.display = 'block';

    finalDecision.textContent = event.decision;
    finalDecision.className = `result-decision decision-${event.decision.toLowerCase()}`;

    finalReasoning.textContent = event.reasoning;

    // Metadata
    resultMetadata.innerHTML = '';
    const metadata = event.metadata || {};
    const items = [
        { label: 'Agreement', value: `${metadata.agreement_percentage || 0}%` },
        { label: 'Max Risk', value: `${metadata.max_risk || 0}%` },
        { label: 'Veto Used', value: metadata.veto_agent ? 'YES' : 'NO' }
    ];

    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'metadata-item';
        div.innerHTML = `
            <div class="metadata-label">${item.label}</div>
            <div class="metadata-value">${item.value}</div>
        `;
        resultMetadata.appendChild(div);
    });

    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

console.log('S4 Live Debate System - Ready! 🚀');
