const API_BASE = "http://localhost:8000";
const labels = { easy: "Easy", medium: "Medium", hard: "Hard", expert: "Expert" };
const el = id => document.getElementById(id);
const grid = el("grid"), errorEl = el("errorMessage"), stepCounter = el("stepCounter"), metrics = el("metrics"), timeEl = el("metricTime"), statesEl = el("metricStates"), backsEl = el("metricBacktracks");
const difficultyEl = el("difficultySelect"), algoEl = el("algorithmSelect"), speedEl = el("speedSlider"), loadBtn = el("loadBtn"), solveBtn = el("solveBtn"), playBtn = el("playBtn"), resetBtn = el("resetBtn"), backBtn = el("backBtn"), fwdBtn = el("fwdBtn"), endBtn = el("endBtn");
let board = Array(81).fill(0), prefilled = new Set(), steps = [], currentStep = 0, isPlaying = false, intervalId = null, speed = 250;

const sleep = ms => new Promise(r => setTimeout(r, ms));
const setError = msg => { errorEl.textContent = msg || ""; };
const setControls = enabled => [solveBtn, playBtn, resetBtn, backBtn, fwdBtn, endBtn].forEach(b => b.disabled = !enabled);
const delayFromSpeed = () => 500 - (Number(speedEl.value) / 100) * 450;
function stop() { if (intervalId) clearInterval(intervalId); intervalId = null; isPlaying = false; playBtn.textContent = "▶"; }

function renderGrid(values, locked) { prefilled = new Set(locked); grid.innerHTML = ""; values.forEach((n, i) => { const c = document.createElement("div"); c.className = "cell"; const r = Math.floor(i / 9), col = i % 9; if (r % 3 === 0) c.classList.add("box-top"); if (col % 3 === 0) c.classList.add("box-left"); if (r === 8) c.classList.add("box-bottom"); if (col === 8) c.classList.add("box-right"); if (prefilled.has(i)) c.classList.add("prefilled"); c.textContent = n || ""; grid.appendChild(c); }); }
function conflicts(values) { const bad = new Set(); const scan = groups => groups.forEach(group => { const seen = new Map(); group.forEach(i => { const v = values[i]; if (!v) return; if (seen.has(v)) { bad.add(i); bad.add(seen.get(v)); } else seen.set(v, i); }); }); scan([...Array(9)].map((_, r) => [...Array(9)].map((_, c) => r * 9 + c))); scan([...Array(9)].map((_, c) => [...Array(9)].map((_, r) => r * 9 + c))); for (let br = 0; br < 3; br++) for (let bc = 0; bc < 3; bc++) { const box = []; for (let r = br * 3; r < br * 3 + 3; r++) for (let c = bc * 3; c < bc * 3 + 3; c++) box.push(r * 9 + c); scan([box]); } return bad; }
function renderStep(index) { if (!steps.length) return; currentStep = Math.max(0, Math.min(index, steps.length - 1)); const values = steps[currentStep]; const prev = steps[currentStep - 1] || Array(81).fill(0); const changed = values.findIndex((v, i) => v !== prev[i]); const bad = conflicts(values); [...grid.children].forEach((cell, i) => { cell.textContent = values[i] || ""; cell.classList.toggle("prefilled", prefilled.has(i)); cell.classList.toggle("changed", i === changed && changed !== -1); cell.classList.toggle("conflict", bad.has(i)); }); stepCounter.textContent = `Step ${currentStep + 1} / ${steps.length}`; }
function updateMetrics(data) { metrics.classList.remove("hidden"); timeEl.textContent = `${Number(data.time).toFixed(2)}s`; statesEl.textContent = data.states_explored; backsEl.textContent = data.backtracks; }

async function loadPuzzle() { stop(); setError(""); steps = []; currentStep = 0; metrics.classList.add("hidden"); renderGrid(Array(81).fill(0), []); setControls(false); try { const res = await fetch(`${API_BASE}/puzzle?difficulty=${difficultyEl.value}`); if (!res.ok) throw new Error("Failed to load puzzle"); const data = await res.json(); board = data.board.slice(); renderGrid(board, board.map((v, i) => v ? i : -1).filter(i => i >= 0)); stepCounter.textContent = "Step 0 / 0"; } catch (e) { setError(e.message); } }

async function solveSteps() { stop(); setError(""); try { const res = await fetch(`${API_BASE}/solve/steps`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ board, algorithm: algoEl.value }) }); const data = await res.json(); if (!res.ok) throw new Error(data.detail || "Failed to solve"); steps = data.steps; currentStep = 0; updateMetrics(data.metrics); renderStep(0); setControls(true); } catch (e) { setError(e.message); } }

function playPause() { if (!steps.length) return; if (isPlaying) return stop(); isPlaying = true; playBtn.textContent = "⏸"; intervalId = setInterval(() => { if (currentStep >= steps.length - 1) return stop(); renderStep(currentStep + 1); }, delayFromSpeed()); }
function stepBack() { if (steps.length) renderStep(currentStep - 1); }
function stepFwd() { if (steps.length) renderStep(currentStep + 1); }

loadBtn.onclick = loadPuzzle; solveBtn.onclick = solveSteps; playBtn.onclick = playPause; resetBtn.onclick = () => { stop(); renderStep(0); }; backBtn.onclick = stepBack; fwdBtn.onclick = stepFwd; endBtn.onclick = () => { stop(); renderStep(steps.length - 1); };
difficultyEl.value = "easy"; algoEl.value = "backtracking"; setControls(false); loadPuzzle();