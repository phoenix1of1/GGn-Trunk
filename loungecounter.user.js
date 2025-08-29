// ==UserScript==
// @name         The Lounge Line Counter (Progress Bar)
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  Count lines you send in The Lounge with persistence, reset, target changer, and progress bar.
// @match        http://localhost:(add port)/*
// @grant        none
// ==/UserScript==


(function() {
    'use strict';


    // Only activate on #/chan-5
    function isValidChannel() {
        return window.location.hash === '#/chan-5';
    }

    // Observe hash changes to enable/disable counter
    function onHashChange() {
        if (isValidChannel()) {
            if (!window.__lineCounterActive) {
                window.__lineCounterActive = true;
                activateCounter();
            }
        } else {
            if (window.__lineCounterActive) {
                window.__lineCounterActive = false;
                removeCounter();
            }
        }
    }

    // Global references for cleanup
    let observer = null;
    let inputBox = null;
    let inputListener = null;

    function removeCounter() {
        const el = document.getElementById('thelounge-line-counter-container');
        if (el) el.remove();
        if (inputBox && inputListener) {
            inputBox.removeEventListener("keydown", inputListener);
            inputBox = null;
            inputListener = null;
        }
        if (observer) {
            observer.disconnect();
            observer = null;
        }
    }

    function activateCounter() {
        const STORAGE_KEY = "thelounge_line_counter";
        let state = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {
            count: 0,
            target: 100
        };

            function saveState() {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
            }

            function exportState() {
                const data = btoa(unescape(encodeURIComponent(JSON.stringify(state))));
                prompt("Copy your counter backup:", data);
            }

            function importState() {
                const data = prompt("Paste your counter backup:");
                if (!data) return;
                try {
                    const obj = JSON.parse(decodeURIComponent(escape(atob(data))));
                    if (typeof obj.count === 'number' && typeof obj.target === 'number') {
                        state = obj;
                        saveState();
                        updateDisplay();
                    } else {
                        alert("Invalid backup data.");
                    }
                } catch (e) {
                    alert("Failed to import: " + e);
                }
            }

            // --- UI Setup ---
            const container = document.createElement('div');
            container.id = 'thelounge-line-counter-container';
            container.style.position = 'fixed';
            container.style.bottom = '10px';
            container.style.right = '10px';
            container.style.padding = '8px 12px';
            container.style.background = 'rgba(0,0,0,0.75)';
            container.style.color = '#fff';
            container.style.fontFamily = 'monospace';
            container.style.borderRadius = '6px';
            container.style.zIndex = '9999';
            container.style.display = 'flex';
            container.style.flexDirection = 'column';
            container.style.gap = '4px';
            container.style.minWidth = '150px';
            container.style.userSelect = 'none';

            // Top row: counter + buttons
            const topRow = document.createElement('div');
            topRow.style.display = 'flex';
            topRow.style.justifyContent = 'space-between';
            topRow.style.alignItems = 'center';

            const counter = document.createElement('span');
            counter.innerText = `Lines: ${state.count} / ${state.target}`;
            topRow.appendChild(counter);

            const btnContainer = document.createElement('div');
            btnContainer.style.display = 'flex';
            btnContainer.style.gap = '4px';

            const resetBtn = document.createElement('button');
            resetBtn.innerText = "⟲";
            resetBtn.title = "Reset counter";
            resetBtn.setAttribute('aria-label', 'Reset counter');
            styleBtn(resetBtn);
            resetBtn.onclick = () => {
                state.count = 0;
                saveState();
                updateDisplay();
            };
            btnContainer.appendChild(resetBtn);

            const targetBtn = document.createElement('button');
            targetBtn.innerText = "⚙️";
            targetBtn.title = "Set target";
            targetBtn.setAttribute('aria-label', 'Set target');
            styleBtn(targetBtn);
            targetBtn.onclick = () => {
                const newTarget = prompt("Set new target:", state.target);
                if (newTarget && !isNaN(newTarget)) {
                    state.target = parseInt(newTarget, 10);
                    saveState();
                    updateDisplay();
                }
            };
            btnContainer.appendChild(targetBtn);

            const exportBtn = document.createElement('button');
            exportBtn.innerText = "⬆️";
            exportBtn.title = "Export counter state";
            exportBtn.setAttribute('aria-label', 'Export counter state');
            styleBtn(exportBtn);
            exportBtn.onclick = exportState;
            btnContainer.appendChild(exportBtn);

            const importBtn = document.createElement('button');
            importBtn.innerText = "⬇️";
            importBtn.title = "Import counter state";
            importBtn.setAttribute('aria-label', 'Import counter state');
            styleBtn(importBtn);
            importBtn.onclick = importState;
            btnContainer.appendChild(importBtn);

            topRow.appendChild(btnContainer);
            container.appendChild(topRow);

            // Progress bar wrapper
            const progressWrapper = document.createElement('div');
            progressWrapper.style.width = '100%';
            progressWrapper.style.height = '8px';
            progressWrapper.style.background = 'rgba(255,255,255,0.2)';
            progressWrapper.style.borderRadius = '4px';
            progressWrapper.style.overflow = 'hidden';

            const progressBar = document.createElement('div');
            progressBar.style.height = '100%';
            progressBar.style.width = '0%';
            progressBar.style.background = 'limegreen';
            progressBar.style.transition = 'width 0.3s ease';

            progressWrapper.appendChild(progressBar);
            container.appendChild(progressWrapper);

            document.body.appendChild(container);

            function updateDisplay() {
                counter.innerText = `Lines: ${state.count} / ${state.target}`;
                const pct = Math.min(100, (state.count / state.target) * 100);
                progressBar.style.width = pct + "%";
            }

            function styleBtn(btn) {
                btn.style.cursor = "pointer";
                btn.style.background = "transparent";
                btn.style.color = "#fff";
                btn.style.border = "none";
                btn.style.fontSize = "14px";
                btn.style.borderRadius = "3px";
                btn.style.padding = "2px 6px";
                btn.style.transition = "background 0.2s, color 0.2s";
                btn.onmouseenter = () => {
                    btn.style.background = "#fff";
                    btn.style.color = "#222";
                };
                btn.onmouseleave = () => {
                    btn.style.background = "transparent";
                    btn.style.color = "#fff";
                };
                btn.onfocus = btn.onmouseenter;
                btn.onblur = btn.onmouseleave;
            }

            updateDisplay();

            // --- Robust input box selection and dynamic DOM handling ---
            function findInputBox() {
                // Try common selectors for TheLounge input box
                let el = document.querySelector("#input");
                if (el) return el;
                // Try by placeholder
                el = document.querySelector("input[placeholder='Message…'], input[placeholder='Message...']");
                if (el) return el;
                // Try by class (TheLounge uses .input for the message box)
                el = document.querySelector("input.input");
                return el;
            }

        function attachListenerToInputBox() {
            const newInputBox = findInputBox();
            if (!newInputBox) return false;
            if (inputBox === newInputBox && inputListener) return true;
            if (inputBox && inputListener) {
                inputBox.removeEventListener("keydown", inputListener);
            }
            inputListener = function(e) {
                if (e.key === "Enter" && newInputBox.value.trim() !== "") {
                    const lines = newInputBox.value.split(/\r?\n/).length;
                    state.count += lines;
                    saveState();
                    updateDisplay();
                    if (state.count >= state.target) {
                        alert("🎉 Target reached!");
                    }
                }
            };
            newInputBox.addEventListener("keydown", inputListener);
            inputBox = newInputBox;
            return true;
        }

        // Attach immediately and set up observer if not already
        attachListenerToInputBox();
        if (!observer) {
            observer = new MutationObserver(() => {
                attachListenerToInputBox();
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
        }

    // Initial check and listen for hash changes
    window.addEventListener('hashchange', onHashChange);
    onHashChange();

})();
