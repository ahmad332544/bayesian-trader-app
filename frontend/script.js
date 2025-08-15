document.addEventListener("DOMContentLoaded", () => {
    // --- Element Definitions ---
    const tableBody = document.getElementById("table-body");
    const connectionStatus = document.getElementById("connection-status");
    const settingsBtn = document.getElementById("settings-btn");
    const settingsModal = document.getElementById("settings-modal");
    const closeSettingsBtn = document.getElementById("close-settings-btn");
    const saveSettingsBtn = document.getElementById("save-settings-btn");
    const thresholdSlider = document.getElementById("evidence-threshold");
    const thresholdValueSpan = document.getElementById("threshold-value");
    const addSymbolBtn = document.getElementById("add-symbol-btn");
    const symbolInput = document.getElementById("symbol-input");
    const statusBar = document.getElementById("status-bar");

    let socket;

    // --- UI Control Functions ---
    function showStatusMessage(message, isPersistent = false) {
        statusBar.textContent = message;
        statusBar.style.display = 'block';
        if (!isPersistent) {
            setTimeout(hideStatusMessage, 5000); // Hide after 5 seconds if not persistent
        }
    }

    function hideStatusMessage() {
        statusBar.style.display = 'none';
    }

    // --- WebSocket Connection ---
    function connect() {
        socket = new WebSocket(`ws://${window.location.host}/ws`);

        socket.onopen = () => {
            console.log("WebSocket connected.");
            connectionStatus.textContent = "● Connected";
            connectionStatus.className = "status-connected";
            hideStatusMessage();
        };

        socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleServerMessage(message);
        };

        socket.onclose = () => {
            console.log("Reconnecting...");
            connectionStatus.textContent = "● Disconnected";
            connectionStatus.className = "status-disconnected";
            showStatusMessage("Connection lost. Attempting to reconnect...", true);
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            socket.close();
        };
    }

    function handleServerMessage(message) {
        if (message.type === "initial_config") {
            const config = message.payload;
            updateSettingsUI(config.settings);
            rebuildTable(config.watchlist);
        } else if (message.type === "data_update") {
            hideStatusMessage();
            updateTableData(message.payload);
        } else if (message.type === "status_update") {
            showStatusMessage(message.payload);
        }
    }

    // --- Table Building and Updating ---
    function rebuildTable(watchlist) {
        tableBody.innerHTML = '';
        if (watchlist.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="8" class="empty-watchlist">Watchlist is empty. Add a symbol to begin.</td></tr>`;
        } else {
            watchlist.forEach(symbol => {
                const row = document.createElement("tr");
                row.id = `row-${symbol}`;
                const timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];
                row.innerHTML = `
                    <td class="symbol-cell">
                        <span class="symbol-name">${symbol}</span>
                        <span id="daily-status-${symbol}" class="daily-status"></span>
                    </td>
                    ${timeframes.map(tf => `<td id="cell-${symbol}-${tf}" class="prediction-cell loading-cell"></td>`).join('')}
                `;
                tableBody.appendChild(row);
            });
        }
    }

    function updateTableData(data) {
        Object.keys(data).forEach(symbol => {
            const row = document.getElementById(`row-${symbol}`);
            if (!row) return;

            const dailyStatusSpan = document.getElementById(`daily-status-${symbol}`);
            if (data[symbol].daily_status === 'up') {
                dailyStatusSpan.innerHTML = '🔼';
                dailyStatusSpan.style.color = 'var(--green-color)';
            } else if (data[symbol].daily_status === 'down') {
                dailyStatusSpan.innerHTML = '🔽';
                dailyStatusSpan.style.color = 'var(--red-color)';
            }

            const timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];
            timeframes.forEach(tf => {
                const cell = document.getElementById(`cell-${symbol}-${tf}`);
                if (cell) {
                    cell.classList.remove("loading-cell");
                    const prediction = data[symbol][tf];
                    if (prediction && !prediction.error) {
                        cell.innerHTML = `
                            <div class="prob-container">
                                <span class="prob-up">${prediction.up_prob.toFixed(1)}%</span>
                                <span class="prob-down">${prediction.down_prob.toFixed(1)}%</span>
                            </div>
                            <span class="evidence-count">${prediction.used_evidence}/${prediction.used_evidence + prediction.ignored_evidence}</span>
                        `;
                    } else {
                        cell.textContent = "N/A";
                    }
                }
            });
        });
    }
    
    // --- Settings and Event Handlers ---
    function updateSettingsUI(settings) {
        const thresholdPercent = settings.evidenceThreshold * 100;
        thresholdSlider.value = thresholdPercent;
        thresholdValueSpan.textContent = `${thresholdPercent.toFixed(1)}%`;
    }

    function sendMessage(type, payload) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type, payload }));
        }
    }

    settingsBtn.onclick = () => settingsModal.style.display = 'flex';
    closeSettingsBtn.onclick = () => settingsModal.style.display = 'none';
    
    thresholdSlider.oninput = () => {
        thresholdValueSpan.textContent = `${parseFloat(thresholdSlider.value).toFixed(1)}%`;
    };

    saveSettingsBtn.onclick = () => {
        const newSettings = { threshold: parseFloat(thresholdSlider.value) / 100 };
        sendMessage('update_settings', newSettings);
        settingsModal.style.display = 'none';
        showStatusMessage("Settings updated. Changes will apply on next data refresh.");
    };

    addSymbolBtn.onclick = () => {
        const symbol = symbolInput.value.trim().toUpperCase();
        if (symbol) {
            sendMessage('add_symbol', symbol);
            symbolInput.value = '';
            showStatusMessage(`Adding symbol ${symbol}...`);
        }
    };
    
    symbolInput.onkeyup = (event) => {
        if (event.key === 'Enter') addSymbolBtn.click();
    };

    // --- Initial Kickstart ---
    connect();
});