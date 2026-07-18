/**
 * Frontend app logic for the Fan Journey Concierge (FIFA 2026 Ops Center).
 * Handles API calls, state updates, UI rendering, and accessibility controls.
 */

// Global State Object
const state = {
    selectedPersona: "fan",
    selectedStadium: "",
    selectedLanguage: "en",
    selectedAccessibility: "none",
    minutesToKickoff: null,
    crowdIntervalId: null
};

// Safe helper to grab DOM nodes dynamically (averts timing/missing element script crashes)
function getEl(id) {
    return document.getElementById(id);
}

// UI Elements with dynamic getters
const el = {
    stadiumSelect: getEl("select-stadium"),
    get languageSelect() { return getEl("select-language"); },
    get accessibilitySelect() { return getEl("select-accessibility"); },
    get kickoffInput() { return getEl("input-kickoff"); },
    
    get chatForm() { return getEl("chat-form"); },
    get chatInput() { return getEl("chat-input"); },
    get chatLog() { return getEl("chat-log"); },
    get suggestedActions() { return getEl("suggested-actions"); },
    
    get crowdContainer() { return getEl("crowd-container"); },
    get crowdLastUpdated() { return getEl("crowd-last-updated"); },
    get crowdAlert() { return getEl("crowd-alert"); },
    
    get transportRecommendation() { return getEl("transport-recommendation"); },
    get transportOptionsList() { return getEl("transport-options-list"); },
    
    get nearestRecycling() { return getEl("nearest-recycling"); },
    get nearestWater() { return getEl("nearest-water"); },
    get sustainabilityTips() { return getEl("sustainability-tips"); },
    
    get toggleContrastBtn() { return getEl("toggle-contrast"); },
    get personaButtons() { return document.querySelectorAll(".btn-persona"); },
    
    // Bottom metric cards and interactive elements
    get btnReport() { return getEl("btn-report"); },
    get hotspotGateA() { return getEl("hotspot-gate-a"); },
    get hotspotPlazaB() { return getEl("hotspot-plaza-b"); },
    get metricSentiment() { return getEl("metric-sentiment"); },
    get metricTranslators() { return getEl("metric-translators"); },
    get metricTransit() { return getEl("metric-transit"); },
    
    // Header action buttons
    get btnNotifications() { return getEl("btn-notifications"); },
    get btnLangFocus() { return getEl("btn-lang-focus"); },
    get btnProfile() { return getEl("btn-profile"); }
};

// HTML Escaper to prevent XSS injections when inserting model replies into DOM
function escapeHtml(unsafe) {
    if (!unsafe) return "";
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Safe event binding utility that won't throw when elements are missing/null
function safeBind(element, event, handler) {
    if (element) {
        element.addEventListener(event, handler);
    }
}

// Add core initialization when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

function initApp() {
    // 1. Set up high-contrast toggle
    initContrastMode();

    // 2. Set up persona switcher
    initPersonaButtons();

    // 3. Load stadiums
    fetchStadiums();

    // 4. Attach event listeners for config options
    safeBind(el.stadiumSelect, "change", handleStadiumChange);
    safeBind(el.languageSelect, "change", handleLanguageChange);
    safeBind(el.accessibilitySelect, "change", handleAccessibilityChange);
    safeBind(el.kickoffInput, "input", handleKickoffChange);

    // 5. Attach chat form submission
    safeBind(el.chatForm, "submit", handleChatSubmit);

    // 6. Bind interactive hotspots and Generate Briefing report buttons
    safeBind(el.btnReport, "click", () => {
        if (el.chatInput && el.chatForm) {
            el.chatInput.value = "Generate complete operational concierge briefing for this stadium";
            el.chatForm.dispatchEvent(new Event("submit"));
        }
    });
    safeBind(el.hotspotGateA, "click", () => {
        if (el.chatInput && el.chatForm) {
            el.chatInput.value = "Is Gate A congested? What are the gate entry instructions?";
            el.chatForm.dispatchEvent(new Event("submit"));
        }
    });
    safeBind(el.hotspotPlazaB, "click", () => {
        if (el.chatInput && el.chatForm) {
            el.chatInput.value = "What is the status of Plaza B? Tell me about the crowd flow.";
            el.chatForm.dispatchEvent(new Event("submit"));
        }
    });

    // 7. Bind header actions
    safeBind(el.btnNotifications, "click", () => {
        appendChatMessage("bot", "📢 Operations Announcement: The transport shuttle service B is currently running on-time with zero bottlenecks reported.");
    });
    safeBind(el.btnLangFocus, "click", () => {
        const select = el.languageSelect;
        if (select) {
            select.focus();
            select.classList.add("ring-2", "ring-secondary-fixed");
            setTimeout(() => {
                select.classList.remove("ring-2", "ring-secondary-fixed");
            }, 1500);
        }
    });
    safeBind(el.btnProfile, "click", () => {
        appendChatMessage("bot", "👤 Active Profile: Command Director (Global Admin). Connected to 2026 Stadium Control Center network.");
    });

    // 8. Pulse status indicator simulation
    setInterval(() => {
        const indicators = document.querySelectorAll('.pulse-indicator');
        indicators.forEach(ind => {
            ind.style.opacity = Math.random() > 0.5 ? '1' : '0.5';
        });
    }, 1000);
}

// --- INITIALIZATION HELPERS ---

function initContrastMode() {
    const btn = el.toggleContrastBtn;
    if (!btn) return;
    
    // Check local storage for preference persistence
    const savedContrast = localStorage.getItem("highContrast") === "true";
    if (savedContrast) {
        document.body.classList.add("high-contrast");
        btn.setAttribute("aria-pressed", "true");
    }
    
    btn.addEventListener("click", () => {
        const isContrast = document.body.classList.toggle("high-contrast");
        btn.setAttribute("aria-pressed", isContrast ? "true" : "false");
        localStorage.setItem("highContrast", isContrast ? "true" : "false");
    });
}

function initPersonaButtons() {
    const buttons = el.personaButtons;
    if (!buttons || buttons.length === 0) return;
    
    buttons.forEach(btn => {
        btn.addEventListener("click", (event) => {
            const clickedBtn = event.currentTarget;
            
            // Update active state in DOM
            buttons.forEach(b => {
                b.classList.remove("active", "bg-secondary-container/10", "text-secondary-fixed", "border-l-4", "border-secondary-fixed", "font-semibold");
                b.classList.add("text-on-surface-variant");
                b.setAttribute("aria-pressed", "false");
            });
            clickedBtn.classList.add("active", "bg-secondary-container/10", "text-secondary-fixed", "border-l-4", "border-secondary-fixed", "font-semibold");
            clickedBtn.classList.remove("text-on-surface-variant");
            clickedBtn.setAttribute("aria-pressed", "true");
            
            // Save state
            state.selectedPersona = clickedBtn.getAttribute("data-persona");
            
            // Re-fetch transport and chat context parameters if stadium is active
            if (state.selectedStadium) {
                fetchTransport();
            }
        });
    });
}

// --- API ACTIONS ---

async function fetchStadiums() {
    try {
        const response = await fetch("/api/stadiums");
        if (!response.ok) throw new Error("Failed to load stadium list");
        
        const stadiums = await response.json();
        
        const select = el.stadiumSelect;
        if (!select) return;
        
        // Clear loading options
        select.innerHTML = "";
        
        if (stadiums.length === 0) {
            select.innerHTML = '<option value="" disabled>No stadiums available</option>';
            return;
        }
        
        // Populate dropdown
        stadiums.forEach((stadium, index) => {
            const opt = document.createElement("option");
            opt.value = stadium.id;
            opt.textContent = `${stadium.name}`;
            select.appendChild(opt);
            
            // Set first stadium as active default
            if (index === 0) {
                state.selectedStadium = stadium.id;
                select.value = stadium.id;
            }
        });
        
        // Load initial stadium metrics
        triggerStadiumRefresh();
        
    } catch (err) {
        if (el.stadiumSelect) {
            showError(el.stadiumSelect, "Error loading stadiums");
        }
        console.error(err);
    }
}

async function fetchCrowdStatus() {
    if (!state.selectedStadium) return;
    
    try {
        const response = await fetch(`/api/crowd/${state.selectedStadium}`);
        if (!response.ok) throw new Error("Failed to load crowd status");
        
        const data = await response.json();
        
        // Render timestamp
        if (el.crowdLastUpdated) {
            const timeStr = new Date(data.generated_at).toLocaleTimeString();
            el.crowdLastUpdated.textContent = `Last simulated sync: ${timeStr}`;
        }
        
        // Clear container
        const container = el.crowdContainer;
        if (!container) return;
        container.innerHTML = "";
        
        // Check if there is an operational warning
        let hasAlert = false;
        
        data.zones.forEach(zone => {
            const row = document.createElement("div");
            row.className = "crowd-row-wrapper";
            
            // Decide icon or pattern based on severity
            let statusIcon = "🟢";
            let dotColor = "bg-success";
            if (zone.density_level === "medium") {
                statusIcon = "🟡";
                dotColor = "bg-warning";
            }
            if (zone.density_level === "high") {
                statusIcon = "🟠";
                dotColor = "bg-danger";
            }
            if (zone.density_level === "critical") {
                statusIcon = "🔴";
                dotColor = "bg-error";
                hasAlert = true;
            }
            
            let trendIcon = "➡️";
            let trendText = "stable";
            if (zone.trend === "rising") {
                trendIcon = "📈";
                trendText = "rising";
            } else if (zone.trend === "falling") {
                trendIcon = "📉";
                trendText = "falling";
            }

            row.innerHTML = `
                <div class="flex justify-between items-center text-xs mb-1">
                    <span class="font-bold text-on-surface">${escapeHtml(zone.name)}</span>
                    <span class="flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full ${dotColor}"></span>
                        <span class="text-[9px] font-label-sm uppercase tracking-wider text-on-surface-variant">${statusIcon} ${escapeHtml(zone.density_level)}</span>
                    </span>
                </div>
                <div class="crowd-progress-track mb-1">
                    <div class="crowd-progress-fill ${zone.density_level}" style="width: ${zone.density_pct}%"></div>
                </div>
                <div class="text-[9px] text-on-surface-variant flex justify-between gap-2">
                    <span>${zone.density_pct}% Density (${trendIcon} ${trendText})</span>
                    <span class="text-right truncate max-w-[150px]">${escapeHtml(zone.recommendation)}</span>
                </div>
            `;
            container.appendChild(row);
        });
        
        // Update operational narrative alert banner
        if (el.crowdAlert) {
            if (hasAlert || data.overall_recommendation.toLowerCase().includes("bottleneck") || data.overall_recommendation.toLowerCase().includes("congest")) {
                el.crowdAlert.innerHTML = `<span class="font-bold">⚠️ OPS ADVISORY:</span> ${escapeHtml(data.overall_recommendation)}`;
                el.crowdAlert.classList.remove("hidden");
            } else {
                el.crowdAlert.classList.add("hidden");
            }
        }
        
        // Update dynamic sentiment based on crowd levels (Less congestion -> higher satisfaction)
        if (data.zones && data.zones.length > 0 && el.metricSentiment) {
            const avgPct = data.zones.reduce((sum, z) => sum + z.density_pct, 0) / data.zones.length;
            const satisfaction = Math.max(50, Math.min(99, Math.round(105 - (avgPct * 0.4))));
            el.metricSentiment.textContent = `${satisfaction}.4%`;
        }
        
    } catch (err) {
        if (el.crowdContainer) {
            el.crowdContainer.innerHTML = `<p class="error-msg text-xs text-center col-span-2">Error loading crowd data: ${escapeHtml(err.message)}</p>`;
        }
        console.error(err);
    }
}

async function fetchTransport() {
    if (!state.selectedStadium) return;
    
    try {
        let url = `/api/transport/${state.selectedStadium}?accessibility_need=${state.selectedAccessibility}`;
        if (state.minutesToKickoff !== null) {
            url += `&minutes_to_kickoff=${state.minutesToKickoff}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to load transport details");
        
        const data = await response.json();
        
        // Render recommendation box
        if (el.transportRecommendation) {
            el.transportRecommendation.innerHTML = `
                <div class="flex items-center gap-1 mb-1 text-[10px] font-label-sm text-secondary-fixed uppercase">
                    <span class="material-symbols-outlined text-xs">auto_awesome</span> Route suggestion (${data.mode})
                </div>
                <p class="text-xs text-on-surface leading-normal">${escapeHtml(data.recommendation)}</p>
            `;
        }
        
        // Render list options
        const list = el.transportOptionsList;
        if (list) {
            list.innerHTML = "";
            data.options.forEach(opt => {
                const card = document.createElement("div");
                card.className = "p-3 rounded-lg bg-surface-container-high border border-white/5 flex justify-between items-center text-xs";
                
                const adaBadge = opt.accessibility_friendly ? '<span class="px-1.5 py-0.5 rounded bg-secondary-container/10 text-secondary-fixed text-[8px] font-label-sm uppercase ml-1.5">♿ Step-Free</span>' : "";
                
                card.innerHTML = `
                    <div class="space-y-1">
                        <h4 class="font-bold text-on-surface flex items-center gap-1.5">${escapeHtml(opt.mode)} ${adaBadge}</h4>
                        <p class="text-[10px] text-on-surface-variant">${escapeHtml(opt.notes)}</p>
                    </div>
                    <div class="font-bold text-secondary-fixed text-right">
                        ${opt.eta_minutes > 0 ? `${opt.eta_minutes}m` : "Ready"}
                    </div>
                `;
                list.appendChild(card);
            });
        }
        
        // Update transit wait metric card (Average wait time of Metro/Shuttle/Transit routes)
        if (data.options && data.options.length > 0 && el.metricTransit) {
            const avgMinutes = data.options.reduce((sum, o) => sum + o.eta_minutes, 0) / data.options.length;
            const minPart = Math.floor(avgMinutes);
            const secPart = Math.round((avgMinutes - minPart) * 60);
            const minStr = minPart.toString().padStart(2, "0");
            const secStr = secPart.toString().padStart(2, "0");
            el.metricTransit.textContent = `${minStr}:${secStr}`;
        }
        
    } catch (err) {
        if (el.transportOptionsList) {
            el.transportOptionsList.innerHTML = `<p class="error-msg text-xs text-center">Error fetching transit routes: ${escapeHtml(err.message)}</p>`;
        }
        console.error(err);
    }
}

async function fetchSustainability() {
    if (!state.selectedStadium) return;
    
    try {
        const response = await fetch(`/api/sustainability/${state.selectedStadium}`);
        if (!response.ok) throw new Error("Failed to load sustainability station");
        
        const data = await response.json();
        
        // Render locations
        if (el.nearestRecycling) el.nearestRecycling.textContent = data.nearest_recycling_zone;
        if (el.nearestWater) el.nearestWater.textContent = data.nearest_water_refill;
        
        // Render tips list
        const tipsList = el.sustainabilityTips;
        if (tipsList) {
            tipsList.innerHTML = "";
            data.tips.forEach(tip => {
                const item = document.createElement("div");
                item.className = "flex items-start gap-2 text-[11px] text-on-surface-variant";
                item.innerHTML = `<span class="text-secondary-fixed">•</span> <span>${escapeHtml(tip)}</span>`;
                tipsList.appendChild(item);
            });
        }
        
    } catch (err) {
        if (el.sustainabilityTips) {
            el.sustainabilityTips.innerHTML = `<p class="error-msg text-xs text-center">Error loading eco tips: ${escapeHtml(err.message)}</p>`;
        }
        console.error(err);
    }
}

async function handleChatSubmit(event) {
    event.preventDefault();
    
    const input = el.chatInput;
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    // Clear input field immediately for UX responsiveness
    input.value = "";
    
    // Append user message to log
    appendChatMessage("user", message);
    
    // Show typing state indicator
    const typingEl = appendChatMessage("bot", "...", "typing-msg");
    
    try {
        const chatReq = {
            message: message,
            context: {
                persona: state.selectedPersona,
                stadium_id: state.selectedStadium,
                gate: "Gate A", // Simulated default locations
                seat_section: "Section 114",
                language: state.selectedLanguage,
                accessibility_need: state.selectedAccessibility,
                minutes_to_kickoff: state.minutesToKickoff
            }
        };
        
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(chatReq)
        });
        
        if (response.status === 429) {
            if (typingEl) typingEl.remove();
            appendChatMessage("bot", "⚠️ Rate limit exceeded. Please wait a minute before posting again.");
            return;
        }
        
        if (!response.ok) throw new Error("Connection lost. Failed to send chat message.");
        
        const data = await response.json();
        
        // Remove typing indicator and render real response
        if (typingEl) typingEl.remove();
        
        // Add note indicating mode if helpful for debug
        const originNote = data.mode === "mock" ? " (Offline Assist)" : "";
        appendChatMessage("bot", data.reply + originNote);
        
        // Update suggested action chips
        renderSuggestedActions(data.suggested_actions);
        
    } catch (err) {
        if (typingEl) typingEl.remove();
        appendChatMessage("bot", `❌ Error: ${err.message}. Running in offline fallback.`);
        console.error(err);
    }
}

// --- STATE CHANGE HANDLERS ---

function handleStadiumChange(event) {
    state.selectedStadium = event.currentTarget.value;
    triggerStadiumRefresh();
}

function handleLanguageChange(event) {
    state.selectedLanguage = event.currentTarget.value;
    // Vary translator helpers count slightly to show dynamic updates
    if (el.metricTranslators) {
        const baseTranslators = 1200 + Math.floor(Math.random() * 20);
        el.metricTranslators.textContent = baseTranslators.toLocaleString();
    }
}

function handleAccessibilityChange(event) {
    state.selectedAccessibility = event.currentTarget.value;
    // Re-trigger transit since path calculations are accessibility dependent
    if (state.selectedStadium) {
        fetchTransport();
    }
}

function handleKickoffChange(event) {
    const val = parseInt(event.currentTarget.value, 10);
    state.minutesToKickoff = isNaN(val) ? null : val;
    // Re-trigger transit since kickoff timing influences recommendation
    if (state.selectedStadium) {
        fetchTransport();
    }
}

function triggerStadiumRefresh() {
    // Immediate pull
    fetchCrowdStatus();
    fetchTransport();
    fetchSustainability();
    
    // Reset automatic interval monitoring (60 seconds)
    if (state.crowdIntervalId) {
        clearInterval(state.crowdIntervalId);
    }
    state.crowdIntervalId = setInterval(fetchCrowdStatus, 60000);
}

// --- UTILITY RENDERERS ---

function appendChatMessage(sender, text, extraClass = "") {
    const log = el.chatLog;
    if (!log) return null;
    
    const bubble = document.createElement("div");
    
    if (sender === "user") {
        bubble.className = `chat-message user bg-secondary-container/10 border-l-4 border-secondary-fixed text-secondary-fixed text-xs rounded p-2.5 max-w-[85%] self-end ${extraClass}`;
    } else {
        bubble.className = `chat-message bot bg-surface-container-high border border-white/5 text-on-surface text-xs rounded p-2.5 max-w-[85%] self-start ${extraClass}`;
    }
    
    const content = document.createElement("div");
    content.className = "message-content";
    content.innerHTML = escapeHtml(text).replace(/\n/g, "<br>");
    
    bubble.appendChild(content);
    log.appendChild(bubble);
    
    // Auto-scroll chat log to bottom
    log.scrollTop = log.scrollHeight;
    
    return bubble;
}

function renderSuggestedActions(actions) {
    const container = el.suggestedActions;
    if (!container) return;
    container.innerHTML = "";
    if (!actions) return;
    
    actions.forEach(action => {
        const pill = document.createElement("button");
        pill.type = "button";
        pill.className = "bg-primary-container hover:bg-surface-container-high border border-white/10 rounded px-2.5 py-1 text-[10px] font-label-sm text-on-surface-variant hover:text-on-surface transition-all active:scale-95";
        pill.textContent = action;
        
        // Formulate a message based on the click
        pill.addEventListener("click", () => {
            const input = el.chatInput;
            const form = el.chatForm;
            if (!input || !form) return;
            
            let messageText = "";
            if (action === "View Transport Options") {
                messageText = "How do I get home? Tell me about the transport options.";
            } else if (action === "Locate Concessions") {
                messageText = "Where can I buy food or a snack?";
            } else if (action === "Find Nearest Restroom") {
                messageText = "Where is the nearest restroom?";
            } else if (action === "View Sustainability Tips") {
                messageText = "Tell me about sustainability in the stadium.";
            } else if (action === "Check Crowd Levels") {
                messageText = "Which zones are crowded right now?";
            } else {
                messageText = `Tell me about: ${action}`;
            }
            
            input.value = messageText;
            form.dispatchEvent(new Event("submit"));
        });
        
        container.appendChild(pill);
    });
}

function showError(element, message) {
    if (!element) return;
    const errorSpan = document.createElement("div");
    errorSpan.className = "error-msg text-xs text-center py-2";
    errorSpan.textContent = message;
    element.parentNode.insertBefore(errorSpan, element.nextSibling);
    
    setTimeout(() => {
        errorSpan.remove();
    }, 5000);
}
