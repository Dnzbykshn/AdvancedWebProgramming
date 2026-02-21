/**
 * Career Assistant AI Agent — Frontend Logic
 */

const API_BASE = window.location.origin;

// ========== Form Submission ==========
async function handleSubmit(event) {
    event.preventDefault();

    const form = document.getElementById('messageForm');
    const submitBtn = document.getElementById('submitBtn');

    const payload = {
        sender_name: document.getElementById('senderName').value.trim(),
        sender_email: document.getElementById('senderEmail').value.trim(),
        subject: document.getElementById('subject').value.trim(),
        message: document.getElementById('message').value.trim(),
    };

    // Validate
    if (!payload.sender_name || !payload.sender_email || !payload.subject || !payload.message) {
        return;
    }

    // Show loading
    showLoading();
    submitBtn.disabled = true;

    try {
        // Animate pipeline steps
        animatePipeline();

        const response = await fetch(`${API_BASE}/api/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();
        showResponse(data);
        refreshLogs();
    } catch (error) {
        console.error('Error:', error);
        showErrorResponse(error.message);
    } finally {
        submitBtn.disabled = false;
    }
}

// ========== Loading Animation ==========
function showLoading() {
    document.getElementById('formSection').classList.add('hidden');
    document.getElementById('responseSection').classList.add('hidden');
    document.getElementById('loadingSection').classList.remove('hidden');

    // Reset pipeline steps
    for (let i = 1; i <= 5; i++) {
        const step = document.getElementById(`step${i}`);
        step.classList.remove('active', 'done');
    }
}

function animatePipeline() {
    const delays = [300, 1500, 3000, 5000, 7000];
    const doneDelays = [1400, 2900, 4900, 6900, 9000];

    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            document.getElementById(`step${i + 1}`).classList.add('active');
        }, delays[i]);

        setTimeout(() => {
            document.getElementById(`step${i + 1}`).classList.remove('active');
            document.getElementById(`step${i + 1}`).classList.add('done');
        }, doneDelays[i]);
    }
}

// ========== Show Response ==========
function showResponse(data) {
    document.getElementById('loadingSection').classList.add('hidden');
    document.getElementById('responseSection').classList.remove('hidden');

    // Always show confidence gauge
    showConfidenceGauge(data.confidence);

    // Show conversation thread if history exists
    showConversationThread(data.conversation_history);

    if (data.status === 'flagged_unknown') {
        showUnknownResponse(data);
        return;
    }

    // Response text
    document.getElementById('responseTitle').textContent = 'Response Generated';
    document.getElementById('responseSubtitle').textContent =
        'Evaluated and approved by the critic agent';
    document.getElementById('responseBody').textContent = data.response_text;
    document.getElementById('responseBody').classList.remove('hidden');

    // Evaluation scores
    const evalSection = document.getElementById('evalSection');
    evalSection.classList.remove('hidden');

    if (data.evaluation) {
        const eval_ = data.evaluation;
        animateScore('tone', eval_.tone_score);
        animateScore('clarity', eval_.clarity_score);
        animateScore('completeness', eval_.completeness_score);
        animateScore('safety', eval_.safety_score);
        animateScore('relevance', eval_.relevance_score);

        document.getElementById('overallScore').textContent =
            eval_.overall_score.toFixed(1) + '/10';
        document.getElementById('evalFeedback').textContent = eval_.feedback;
    }

    // Revision count
    document.getElementById('revisionBadge').textContent =
        `${data.revision_count} revision${data.revision_count !== 1 ? 's' : ''}`;

    // Email status
    const emailEl = document.getElementById('emailStatus');
    if (data.email_result) {
        if (data.email_result.success) {
            emailEl.textContent = '✓ Email sent';
            emailEl.className = 'email-status success';
        } else {
            emailEl.textContent = '✗ Email failed';
            emailEl.className = 'email-status error';
        }
    }

    // Hide unknown alert
    document.getElementById('unknownAlert').classList.add('hidden');
}

function showUnknownResponse(data) {
    document.getElementById('responseTitle').textContent = 'Question Flagged';
    document.getElementById('responseSubtitle').textContent =
        'This question requires human intervention';

    // Hide normal response elements
    document.getElementById('responseBody').classList.add('hidden');
    document.getElementById('evalSection').classList.add('hidden');

    // Show unknown alert
    const alert = document.getElementById('unknownAlert');
    alert.classList.remove('hidden');

    if (data.unknown_detection) {
        document.getElementById('unknownReason').textContent = data.unknown_detection.reason;
        document.getElementById('unknownCategory').textContent =
            data.unknown_detection.category || 'unknown';
    }
}

function showErrorResponse(message) {
    document.getElementById('loadingSection').classList.add('hidden');
    document.getElementById('responseSection').classList.remove('hidden');

    document.getElementById('responseTitle').textContent = 'Error Occurred';
    document.getElementById('responseSubtitle').textContent = message;
    document.getElementById('responseBody').textContent =
        'An error occurred while processing the message. Please try again.';
    document.getElementById('responseBody').classList.remove('hidden');
    document.getElementById('evalSection').classList.add('hidden');
    document.getElementById('unknownAlert').classList.add('hidden');
    document.getElementById('confidenceSection').classList.add('hidden');
    document.getElementById('conversationThread').classList.add('hidden');
}

// ========== Confidence Gauge ==========
function showConfidenceGauge(confidence) {
    const section = document.getElementById('confidenceSection');
    if (!confidence) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');

    const value = confidence.confidence;
    const pct = Math.round(value * 100);
    const arcLength = 251.2; // total arc length of the semicircle
    const filledLength = value * arcLength;

    // Animate the gauge arc
    const gaugeArc = document.getElementById('gaugeArc');
    setTimeout(() => {
        gaugeArc.setAttribute('stroke-dasharray', `${filledLength} ${arcLength}`);
    }, 100);

    // Animate the needle (rotate from -90 to the target angle)
    // -90 = far left (0%), +90 = far right (100%)
    const needleAngle = -90 + (value * 180);
    const gaugeNeedle = document.getElementById('gaugeNeedle');
    setTimeout(() => {
        gaugeNeedle.setAttribute('transform', `rotate(${needleAngle}, 100, 100)`);
        gaugeNeedle.style.transition = 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)';
    }, 100);

    // Value text
    document.getElementById('confidenceValue').textContent = `${pct}%`;

    // Label
    const label = document.getElementById('confidenceLabel');
    if (confidence.is_unknown) {
        label.textContent = confidence.reason || 'Flagged for human review';
    } else {
        label.textContent = confidence.reason || 'Message classified as safe';
    }

    // Category badge
    const cat = document.getElementById('confidenceCategory');
    const category = confidence.category || 'unknown';
    cat.textContent = category;
    cat.className = 'gauge-category';

    if (category === 'safe') {
        cat.classList.add('safe');
    } else if (['ambiguous', 'out_of_domain'].includes(category)) {
        cat.classList.add('warning');
    } else {
        cat.classList.add('danger');
    }
}

// ========== Conversation Thread ==========
function showConversationThread(history) {
    const section = document.getElementById('conversationThread');
    const container = document.getElementById('threadContainer');

    if (!history || history.length === 0) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');
    container.innerHTML = '';

    history.forEach((entry, index) => {
        const time = new Date(entry.timestamp).toLocaleString();

        // Employer message bubble
        const employerDiv = document.createElement('div');
        employerDiv.className = 'thread-msg employer';
        employerDiv.innerHTML = `
            <div class="thread-msg-label">Employer</div>
            <div>${escapeHtml(entry.employer_message)}</div>
            <div class="thread-msg-time">${time}</div>
        `;
        container.appendChild(employerDiv);

        // Agent response bubble
        if (entry.agent_response) {
            const agentDiv = document.createElement('div');
            agentDiv.className = 'thread-msg agent';
            agentDiv.innerHTML = `
                <div class="thread-msg-label">Deniz (AI Agent)</div>
                <div>${escapeHtml(entry.agent_response)}</div>
                <div class="thread-msg-time">${time}</div>
            `;
            container.appendChild(agentDiv);
        } else {
            const flaggedDiv = document.createElement('div');
            flaggedDiv.className = 'thread-msg flagged';
            flaggedDiv.innerHTML = `
                <div class="thread-msg-label">⚠ Flagged for human review</div>
                <div>No automated response was sent for this message.</div>
                <div class="thread-msg-time">${time}</div>
            `;
            container.appendChild(flaggedDiv);
        }
    });

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function animateScore(name, score) {
    const bar = document.getElementById(`${name}Bar`);
    const value = document.getElementById(`${name}Score`);

    value.textContent = `${score}/10`;

    // Animate bar fill after a small delay
    setTimeout(() => {
        bar.style.width = `${score * 10}%`;

        // Color based on score
        if (score >= 8) {
            bar.style.background = 'linear-gradient(90deg, #10b981, #34d399)';
        } else if (score >= 6) {
            bar.style.background = 'var(--accent-gradient)';
        } else {
            bar.style.background = 'linear-gradient(90deg, #ef4444, #f59e0b)';
        }
    }, 200);
}

// ========== Reset ==========
function resetForm() {
    document.getElementById('responseSection').classList.add('hidden');
    document.getElementById('loadingSection').classList.add('hidden');
    document.getElementById('formSection').classList.remove('hidden');

    // Reset score bars
    ['tone', 'clarity', 'completeness', 'safety', 'relevance'].forEach(name => {
        document.getElementById(`${name}Bar`).style.width = '0%';
        document.getElementById(`${name}Score`).textContent = '-';
    });

    // Reset gauge
    const gaugeArc = document.getElementById('gaugeArc');
    if (gaugeArc) {
        gaugeArc.setAttribute('stroke-dasharray', '0 251.2');
    }
    const gaugeNeedle = document.getElementById('gaugeNeedle');
    if (gaugeNeedle) {
        gaugeNeedle.setAttribute('transform', 'rotate(-90, 100, 100)');
    }
}

// ========== Conversation History Panel ==========
function toggleHistory() {
    const historySection = document.getElementById('historySection');
    historySection.classList.toggle('hidden');

    if (!historySection.classList.contains('hidden')) {
        refreshHistory();
    }
}

async function refreshHistory() {
    try {
        const resp = await fetch(`${API_BASE}/api/conversations`);
        const data = await resp.json();

        const container = document.getElementById('historyContainer');

        if (data.total_employers === 0) {
            container.innerHTML = `
                <div class="empty-logs">
                    <p>No conversations yet. Process a message to start tracking.</p>
                </div>`;
            return;
        }

        container.innerHTML = Object.entries(data.conversations).map(([email, entries]) => {
            const exchangesHtml = entries.map(entry => {
                const time = new Date(entry.timestamp).toLocaleString();
                const snippet = entry.employer_message.length > 80
                    ? entry.employer_message.substring(0, 80) + '...'
                    : entry.employer_message;
                const statusIcon = entry.status === 'approved' ? '✓' : '⚠';

                return `
                    <div class="history-exchange">
                        <div class="history-exchange-time">${time} ${statusIcon}</div>
                        <div class="history-exchange-snippet">${escapeHtml(snippet)}</div>
                    </div>`;
            }).join('');

            return `
                <div class="history-employer">
                    <div class="history-employer-header">
                        <span class="history-employer-email">${escapeHtml(email)}</span>
                        <span class="history-employer-count">${entries.length} message${entries.length !== 1 ? 's' : ''}</span>
                    </div>
                    ${exchangesHtml}
                </div>`;
        }).join('');
    } catch (error) {
        console.error('Failed to refresh history:', error);
    }
}

async function clearHistory() {
    try {
        await fetch(`${API_BASE}/api/conversations`, { method: 'DELETE' });
        refreshHistory();
    } catch (error) {
        console.error('Failed to clear history:', error);
    }
}

// ========== Logs ==========
function toggleLogs() {
    const logsSection = document.getElementById('logsSection');
    logsSection.classList.toggle('hidden');

    if (!logsSection.classList.contains('hidden')) {
        refreshLogs();
    }
}

async function refreshLogs() {
    try {
        const resp = await fetch(`${API_BASE}/api/logs`);
        const data = await resp.json();

        document.getElementById('logCount').textContent = data.total;
        const container = document.getElementById('logsContainer');

        if (data.total === 0) {
            container.innerHTML = `
                <div class="empty-logs">
                    <p>No logs yet. Process a message to see evaluation history.</p>
                </div>`;
            return;
        }

        container.innerHTML = data.logs.map(log => {
            const time = new Date(log.timestamp).toLocaleString();
            const statusClass = log.status === 'approved' ? 'approved' : 'flagged';
            const statusLabel = log.status === 'approved' ? 'Approved' : 'Flagged';
            const scoreText = log.evaluation
                ? `Score: ${log.evaluation.overall_score.toFixed(1)}/10`
                : '';
            const confText = log.confidence
                ? `Conf: ${Math.round(log.confidence.confidence * 100)}%`
                : '';

            return `
                <div class="log-entry">
                    <div class="log-header">
                        <span class="log-sender">${escapeHtml(log.sender_name)}</span>
                        <span class="log-time">${time}</span>
                    </div>
                    <div class="log-subject">${escapeHtml(log.subject)}</div>
                    <div class="log-meta">
                        <span class="log-badge ${statusClass}">${statusLabel}</span>
                        ${scoreText ? `<span class="log-badge score">${scoreText}</span>` : ''}
                        ${confText ? `<span class="log-badge score">${confText}</span>` : ''}
                        ${log.revision_count > 0
                    ? `<span class="log-badge score">${log.revision_count} revision(s)</span>`
                    : ''}
                    </div>
                </div>`;
        }).join('');
    } catch (error) {
        console.error('Failed to refresh logs:', error);
    }
}

async function clearLogs() {
    try {
        await fetch(`${API_BASE}/api/logs`, { method: 'DELETE' });
        refreshLogs();
    } catch (error) {
        console.error('Failed to clear logs:', error);
    }
}

// ========== Utils ==========
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function closeArchModal(event) {
    if (event.target.id === 'archModal') {
        document.getElementById('archModal').classList.add('hidden');
    }
}

// Load log count on page load
document.addEventListener('DOMContentLoaded', () => {
    refreshLogs();
});
