document.addEventListener("DOMContentLoaded", () => {
    // --- Element Definitions ---
    const connectionStatus = document.getElementById("connection-status");
    const settingsBtn = document.getElementById("settings-btn");
    const settingsModal = document.getElementById("settings-modal");
    const closeSettingsBtn = document.getElementById("close-settings-btn");
    const saveSettingsBtn = document.getElementById("save-settings-btn");
    const thresholdSlider = document.getElementById("evidence-threshold");
    const thresholdValueSpan = document.getElementById("threshold-value");
    const historyLookbackInput = document.getElementById("history-lookback");
    
    // Tab Elements
    const tabLinks = document.querySelectorAll(".tab-link");
    const tabContents = document.querySelectorAll(".tab-content");

    // Next Candle Tab Elements
    const addSymbolBtn = document.getElementById("add-symbol-btn");
    const symbolInput = document.getElementById("symbol-input");
    const statusBar = document.getElementById("status-bar");
    const tableBody = document.getElementById("table-body");

    // Future Prediction Tab Elements
    const predictFutureBtn = document.getElementById("predict-future-btn");
    const horizonInput = document.getElementById("horizon-input");
    const statusBarFuture = document.getElementById("status-bar-future");
    const futureTableBody = document.getElementById("future-table-body");
    
    let socket;

    // --- UI Control Functions ---
    function showStatusMessage(message, isFutureTab = false) {
        const bar = isFutureTab ? statusBarFuture : statusBar;
        bar.textContent = message;
        bar.style.display = 'block';
    }

    function hideStatusMessage(isFutureTab = false) {
        const bar = isFutureTab ? statusBarFuture : statusBar;
        bar.style.display = 'none';
    }

    // --- WebSocket Connection ---
    function connect() {
        socket = new WebSocket(`ws://${window.location.host}/ws`);

        socket.onopen = () => {
            console.log("WebSocket connected.");
            connectionStatus.textContent = "● Connected";
            connectionStatus.className = "status-connected";
        };

        socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleServerMessage(message);
        };

        socket.onclose = () => {
            console.log("Reconnecting...");
            connectionStatus.textContent = "● Disconnected";
            connectionStatus.className = "status-disconnected";
            setTimeout(connect, 3000);
        };
    }

    function handleServerMessage(message) {
        if (message.type === "initial_config") {
            const config = message.payload;
            updateSettingsUI(config.settings);
            rebuildTable(config.watchlist, tableBody);
            // Also build the future table structure
            rebuildTable(config.watchlist, futureTableBody);
        } else if (message.type === "data_update") {
            hideStatusMessage();
            updateTableData(message.payload, tableBody);
        } else if (message.type === "future_data_update") {
            hideStatusMessage(true);
            updateTableData(message.payload, futureTableBody);
        } else if (message.type === "status_update") {
            showStatusMessage(message.payload);
        }
    }

    // --- Table Building and Updating ---
    function rebuildTable(watchlist, tbody) {
        tbody.innerHTML = '';
        if (watchlist.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="empty-watchlist">Watchlist is empty. Add a symbol to begin.</td></tr>`;
        } else {
            watchlist.forEach(symbol => {
                const row = document.createElement("tr");
                row.id = `${tbody.id}-row-${symbol}`;
                const timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];
                row.innerHTML = `
                    <td class="symbol-cell">
                        <span class="symbol-name">${symbol}</span>
                        <span id="${tbody.id}-daily-status-${symbol}" class="daily-status"></span>
                    </td>
                    ${timeframes.map(tf => `<td id="${tbody.id}-cell-${symbol}-${tf}" class="prediction-cell loading-cell"></td>`).join('')}
                `;
                tbody.appendChild(row);
            });
        }
    }

    function updateTableData(data, tbody) {
        Object.keys(data).forEach(symbol => {
            const row = document.getElementById(`${tbody.id}-row-${symbol}`);
            if (!row) {
                 rebuildTable(Object.keys(data), tbody);
                 return;
            }

            const dailyStatusSpan = document.getElementById(`${tbody.id}-daily-status-${symbol}`);
            if (data[symbol].daily_status === 'up') {
                dailyStatusSpan.innerHTML = '🔼';
                dailyStatusSpan.style.color = 'var(--green-color)';
            } else if (data[symbol].daily_status === 'down') {
                dailyStatusSpan.innerHTML = '🔽';
                dailyStatusSpan.style.color = 'var(--red-color)';
            }

            const timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];
            timeframes.forEach(tf => {
                const cell = document.getElementById(`${tbody.id}-cell-${symbol}-${tf}`);
                if (cell) {
                    cell.classList.remove("loading-cell");
                    const prediction = data[symbol][tf];
                    if (prediction && !prediction.error) {
                        const ignored_reasons = prediction.ignored_details || [];
                        const ignored_title = ignored_reasons.length > 0
                            ? `Ignored Reasons:\n- ${ignored_reasons.join('\n- ')}`
                            : 'All available evidence was used.';

                        cell.innerHTML = `
                            <div class="prob-container">
                                <span class="prob-up">${prediction.up_prob.toFixed(1)}%</span>
                                <span class="prob-down">${prediction.down_prob.toFixed(1)}%</span>
                            </div>
                            <span class="evidence-count" title="${ignored_title}">
                                ${prediction.used_evidence}/${prediction.used_evidence + prediction.ignored_evidence}
                            </span>
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
        historyLookbackInput.value = settings.history_lookback;
        const thresholdPercent = settings.evidence_threshold * 100;
        thresholdSlider.value = thresholdPercent;
        thresholdValueSpan.textContent = `${thresholdPercent.toFixed(1)}%`;
    }

    function sendMessage(type, payload) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type, payload }));
        }
    }
    
    // Tab switching logic
    tabLinks.forEach(link => {
        link.addEventListener("click", () => {
            tabLinks.forEach(l => l.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));
            link.classList.add("active");
            document.getElementById(link.dataset.tab).classList.add("active");
        });
    });

    settingsBtn.onclick = () => settingsModal.style.display = 'flex';
    closeSettingsBtn.onclick = () => settingsModal.style.display = 'none';
    
    thresholdSlider.oninput = () => {
        thresholdValueSpan.textContent = `${parseFloat(thresholdSlider.value).toFixed(1)}%`;
    };

    saveSettingsBtn.onclick = () => {
        const newSettings = {
            evidence_threshold: parseFloat(thresholdSlider.value) / 100,
            history_lookback: parseInt(historyLookbackInput.value)
        };
        sendMessage('update_settings', newSettings);
        settingsModal.style.display = 'none';
        showStatusMessage("Settings saved. Retraining with new parameters...", true);
    };

    addSymbolBtn.onclick = () => {
        const symbol = symbolInput.value.trim().toUpperCase();
        if (symbol) {
            sendMessage('add_symbol', symbol);
            symbolInput.value = '';
        }
    };
    
    symbolInput.onkeyup = (event) => { if (event.key === 'Enter') addSymbolBtn.click(); };

    predictFutureBtn.onclick = () => {
        const horizon = parseInt(horizonInput.value);
        if (horizon > 1) {
            sendMessage('predict_future', { horizon: horizon });
            showStatusMessage(`Requesting future prediction for ${horizon} candles...`, true);
        }
    };

    // --- Initial Kickstart ---
    connect();
});