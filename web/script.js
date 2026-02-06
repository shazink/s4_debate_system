// S4 Multi-Agent Debate System - Frontend JavaScript
// Dark Red Cyberpunk UI

// State
let threatsBlocked = 0;

// DOM Elements
const queryInput = document.getElementById('queryInput');
const charCount = document.getElementById('charCount');
const submitBtn = document.getElementById('submitBtn');
const loadingOverlay = document.getElementById('loadingOverlay');

// Defense Section
const defenseSection = document.getElementById('defenseSection');
const riskScore = document.getElementById('riskScore');
const validationStatus = document.getElementById('validationStatus');
const threatsBlockedEl = document.getElementById('threatsBlocked');

// Agent Section
const agentsSection = document.getElementById('agentsSection');
const utilityStatus = document.getElementById('utilityStatus');
const accuracyStatus = document.getElementById('accuracyStatus');
const safetyStatus = document.getElementById('safetyStatus');
const utilityDecision = document.getElementById('utilityDecision');
const accuracyDecision = document.getElementById('accuracyDecision');
const safetyDecision = document.getElementById('safetyDecision');

// Debate Section
const debateSection = document.getElementById('debateSection');
const debateRounds = document.getElementById('debateRounds');

// Result Section
const resultSection = document.getElementById('resultSection');
const finalDecision = document.getElementById('finalDecision');
const finalReasoning = document.getElementById('finalReasoning');
const resultMetadata = document.getElementById('resultMetadata');

// Character Counter
queryInput.addEventListener('input', () => {
    const count = queryInput.value.length;
    charCount.textContent = count;

    if (count > 4500) {
        charCount.style.color = 'var(--red-primary)';
    } else {
        charCount.style.color = 'var(--cyan)';
    }
});

// Submit Button
submitBtn.addEventListener('click', async () => {
    const query = queryInput.value.trim();

    if (!query) {
        alert('Please enter a query');
        return;
    }

    // Reset UI
    resetUI();

    // Show inline loading (no overlay)
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.5';
    submitBtn.querySelector('.btn-text').textContent = 'ANALYZING...';

    // Show agents as active/analyzing
    document.querySelectorAll('.agent-card').forEach(card => {
        card.classList.add('active');
    });

    try {
        // Call API
        const response = await fetch('/api/debate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
        submitBtn.querySelector('.btn-text').textContent = 'ANALYZE';

        if (data.success) {
            displayResults(data);
        } else {
            // Show error in UI instead of alert
            displayErrorInUI(data.error, data.type);
        }

    } catch (error) {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
        submitBtn.querySelector('.btn-text').textContent = 'ANALYZE';

        displayErrorInUI(error.message, 'Network Error');
    }
});

// Reset UI
function resetUI() {
    // Reset agents
    utilityStatus.textContent = 'ANALYZING';
    accuracyStatus.textContent = 'ANALYZING';
    safetyStatus.textContent = 'ANALYZING';
    utilityDecision.textContent = '';
    accuracyDecision.textContent = '';
    safetyDecision.textContent = '';

    // Reset defense
    riskScore.textContent = '0%';
    validationStatus.textContent = 'VALIDATING';

    // Hide sections
    debateSection.style.display = 'none';
    resultSection.style.display = 'none';
    debateRounds.innerHTML = '';

    // Activate agent cards
    document.querySelectorAll('.agent-card').forEach(card => {
        card.classList.add('active');
    });
}

// Display Results
function displayResults(data) {
    console.log('Debate Results:', data);

    // Update defense
    const risk = data.metadata?.risk_score || 0;
    riskScore.textContent = `${risk}%`;
    validationStatus.textContent = risk > 50 ? 'BLOCKED' : 'PASSED';

    if (data.metadata?.security_block) {
        threatsBlocked++;
        threatsBlockedEl.textContent = threatsBlocked;
    }

    // Update agents
    updateAgentStatuses(data);

    // Show debate (if available)
    if (data.debate_summary && data.debate_summary.rounds) {
        displayDebate(data.debate_summary);
    }

    // Show final decision
    displayFinalDecision(data);

    // Deactivate agent cards
    document.querySelectorAll('.agent-card').forEach(card => {
        card.classList.remove('active');
    });
}

// Update Agent Statuses
function updateAgentStatuses(data) {
    // Try to extract agent decisions from debate summary
    const summary = data.debate_summary;

    if (summary && summary.rounds && summary.rounds.length > 0) {
        const lastRound = summary.rounds[summary.rounds.length - 1];

        // Update based on final votes
        if (lastRound.votes) {
            lastRound.votes.forEach(vote => {
                const agentName = vote.agent || '';
                const decision = vote.decision || 'UNKNOWN';
                const confidence = vote.confidence || 0;
                const risk = vote.risk || 0;

                if (agentName.includes('Utility')) {
                    utilityStatus.textContent = decision;
                    utilityDecision.textContent = `${decision} (${confidence.toFixed(0)}% confidence, ${risk.toFixed(0)}% risk)`;
                    utilityDecision.className = `agent-decision decision-${decision.toLowerCase()}`;
                } else if (agentName.includes('Accuracy')) {
                    accuracyStatus.textContent = decision;
                    accuracyDecision.textContent = `${decision} (${confidence.toFixed(0)}% confidence, ${risk.toFixed(0)}% risk)`;
                    accuracyDecision.className = `agent-decision decision-${decision.toLowerCase()}`;
                } else if (agentName.includes('Safety')) {
                    safetyStatus.textContent = decision;
                    safetyDecision.textContent = `${decision} (${confidence.toFixed(0)}% confidence, ${risk.toFixed(0)}% risk)`;
                    safetyDecision.className = `agent-decision decision-${decision.toLowerCase()}`;
                }
            });
        }
    }
}

// Display Debate Rounds
function displayDebate(summary) {
    debateSection.style.display = 'block';
    debateRounds.innerHTML = '';

    if (!summary.rounds) return;

    summary.rounds.forEach((round, index) => {
        const roundCard = document.createElement('div');
        roundCard.className = 'round-card';
        roundCard.style.animationDelay = `${index * 0.1}s`;

        const roundHeader = document.createElement('div');
        roundHeader.className = 'round-header';
        roundHeader.innerHTML = `
            <div class="round-number">ROUND ${round.number}</div>
            <div class="round-title">${round.name}</div>
        `;

        const roundContent = document.createElement('div');
        roundContent.className = 'round-content';

        // Format content based on round type
        if (round.type === 'votes' && round.votes) {
            // Show final votes nicely
            roundContent.innerHTML = round.votes.map(vote => `
                <div style="margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                    <strong style="color: var(--red-primary);">${vote.agent}</strong><br>
                    <span style="color: var(--cyan);">Decision:</span> ${vote.decision} 
                    (${vote.confidence.toFixed(0)}% confidence, ${vote.risk.toFixed(0)}% risk)<br>
                    <span style="color: var(--text-muted); font-size: 14px; white-space: pre-wrap;">${vote.reasoning}</span>
                </div>
            `).join('');
        } else if (round.data && round.data.length > 0) {
            // Show other round data
            roundContent.innerHTML = round.data.map(item => {
                if (round.type === 'analysis') {
                    return `
                        <div style="margin-bottom: 15px; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 6px;">
                            <strong style="color: var(--cyan);">${item.agent}:</strong> ${item.decision} 
                            (${item.confidence}% confidence)<br>
                            <span style="font-size: 14px; color: var(--text-secondary); white-space: pre-wrap;">${item.reasoning}</span>
                        </div>
                    `;
                } else if (round.type === 'challenges') {
                    return `
                        <div style="margin-bottom: 15px; padding: 10px; background: rgba(255,0,64,0.1); border-radius: 6px;">
                            <span style="color: var(--red-primary); font-weight: bold;">${item.challenger}</span> → 
                            <span style="color: var(--cyan); font-weight: bold;">${item.challenged_agent}</span><br>
                            <span style="font-size: 14px; color: var(--text-secondary); white-space: pre-wrap;">${item.challenge}</span>
                        </div>
                    `;
                } else if (round.type === 'revisions') {
                    const confChange = item.changes.confidence.new - item.changes.confidence.old;
                    const confChangeStr = confChange >= 0 ? `+${confChange.toFixed(0)}` : confChange.toFixed(0);
                    return `
                        <div style="margin-bottom: 15px; padding: 10px; background: rgba(0,255,157,0.1); border-radius: 6px;">
                            <strong style="color: var(--cyan);">${item.agent}:</strong> 
                            ${item.changes.decision.old} → ${item.changes.decision.new}
                            (confidence ${confChangeStr}%)<br>
                            <span style="font-size: 14px; color: var(--text-secondary); white-space: pre-wrap;">${item.reason}</span>
                        </div>
                    `;
                }
                return '';
            }).join('');
        } else {
            roundContent.textContent = 'No data available for this round';
        }

        roundCard.appendChild(roundHeader);
        roundCard.appendChild(roundContent);
        debateRounds.appendChild(roundCard);
    });

    // Scroll to debate section
    debateSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display Final Decision
function displayFinalDecision(data) {
    resultSection.style.display = 'block';

    // Decision
    const decision = data.decision || 'UNKNOWN';
    finalDecision.textContent = decision;
    finalDecision.className = `result-decision decision-${decision.toLowerCase()}`;

    // Reasoning
    finalReasoning.textContent = data.reasoning || 'No reasoning provided';

    // Metadata
    resultMetadata.innerHTML = '';

    const metadata = data.metadata || {};
    const metadataItems = [
        { label: 'Agreement', value: `${metadata.agreement_percentage || 0}%` },
        { label: 'Max Risk', value: `${metadata.max_risk || 0}%` },
        { label: 'Veto Used', value: metadata.veto_agent ? 'YES' : 'NO' }
    ];

    metadataItems.forEach(item => {
        const metadataItem = document.createElement('div');
        metadataItem.className = 'metadata-item';
        metadataItem.innerHTML = `
            <div class="metadata-label">${item.label}</div>
            <div class="metadata-value">${item.value}</div>
        `;
        resultMetadata.appendChild(metadataItem);
    });

    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display Error in UI (not alert)
function displayErrorInUI(errorMsg, errorType) {
    console.error('Error:', errorMsg);

    // Show result section with error
    resultSection.style.display = 'block';

    // Check if quota error
    const isQuotaError = errorMsg.includes('429') || errorMsg.includes('quota') || errorMsg.includes('RESOURCE_EXHAUSTED');

    if (isQuotaError) {
        finalDecision.textContent = 'QUOTA EXCEEDED';
        finalDecision.className = 'result-decision decision-warn';
        finalReasoning.innerHTML = `
            <strong style="color: var(--red-primary);">⚠️ API Quota Limit Reached</strong><br><br>
            The Google Gemini API free tier has a limit of <strong>20 requests per minute</strong>.<br><br>
            <strong>Please wait 60 seconds and try again.</strong><br><br>
            <span style="color: var(--text-muted); font-size: 14px;">
            Error: ${errorMsg.substring(0, 200)}...
            </span>
        `;

        validationStatus.textContent = 'QUOTA LIMIT';
        riskScore.textContent = 'N/A';
        utilityStatus.textContent = 'WAITING';
        accuracyStatus.textContent = 'WAITING';
        safetyStatus.textContent = 'WAITING';
    } else {
        finalDecision.textContent = 'ERROR';
        finalDecision.className = 'result-decision decision-refuse';
        finalReasoning.innerHTML = `
            <strong style="color: var(--red-primary);">❌ System Error</strong><br><br>
            <strong>Error Type:</strong> ${errorType || 'Unknown'}<br>
            <strong>Message:</strong> ${errorMsg}<br><br>
            <span style="color: var(--text-muted); font-size: 14px;">
            Please check the terminal for more details or try again.
            </span>
        `;
    }

    // Clear metadata
    resultMetadata.innerHTML = '';

    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display Error (old function - kept for compatibility)
function displayError(errorMsg) {
    displayErrorInUI(errorMsg, 'Unknown');
}

// Initialize
console.log('S4 Multi-Agent Debate System - UI Loaded');
console.log('🛡️ Attack Defense: ACTIVE');
console.log('🤖 Agents: 3 (Utility, Accuracy, Safety)');
