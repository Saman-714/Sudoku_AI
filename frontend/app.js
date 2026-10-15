const API_BASE = "http://localhost:8000";
const labels = { easy: "Easy", medium: "Medium", hard: "Hard", expert: "Expert" };
const algoLabels = { backtracking: "Backtracking", ac3_mrv: "AC-3 + MRV", forward_checking: "Forward Checking", simulated_annealing: "Simulated Annealing" };

let board = Array(81).fill(0), solution = Array(81).fill(0), prefilled = new Set(), timerId = null, startedAt = 0, busy = false;
const grid = document.getElementById("grid"), timerEl = document.getElementById("timer"), badgeEl = document.getElementById("difficultyBadge"), errorEl = document.getElementById("errorMessage"), metricsEl = document.getElementById("metrics"), timeEl = document.getElementById("metricTime"), statesEl = document.getElementById("metricStates"), backsEl = document.getElementById("metricBacktracks"), difficultyEl = document.getElementById("difficultySelect"), algoEl = document.getElementById("algorithmSelect"), newBtn = document.getElementById("newPuzzleBtn"), solveBtn = document.getElementById("solveBtn");

const sleep = ms => new Promise(r => setTimeout(r, ms));
const setError = msg => { errorEl.textContent = msg || ""; };
const setBusy = value => { busy = value; newBtn.disabled = value; algoEl.disabled = value; difficultyEl.disabled = value; if (value) solveBtn.disabled = true; };
const setSolvedState = value => { solveBtn.disabled = value; };
const fmt = s => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
function tick() { timerEl.textContent = fmt(Math.floor((Date.now() - startedAt) / 1000)); }
function startTimer() { stopTimer(); startedAt = Date.now(); timerEl.textContent = "00:00"; timerId = setInterval(tick, 1000); }
function stopTimer() { if (timerId) clearInterval(timerId); timerId = null; }
function renderGrid(values, locked) { grid.innerHTML = ""; prefilled = new Set(locked); values.forEach((n, i) => { const c = document.createElement("div"); c.className = "cell"; const r = Math.floor(i / 9), col = i % 9; if (r % 3 === 0) c.classList.add("box-top"); if (col % 3 === 0) c.classList.add("box-left"); if (r === 8) c.classList.add("box-bottom"); if (col === 8) c.classList.add("box-right"); if (prefilled.has(i)) c.classList.add("prefilled"); if (n) { c.textContent = n; if (!prefilled.has(i)) c.classList.add("solved"); } grid.appendChild(c); }); }
function resetMetrics() { metricsEl.classList.add("hidden"); timeEl.textContent = "0.00s"; statesEl.textContent = "0"; backsEl.textContent = "0"; }
async function loadPuzzle() { if (busy) return; setBusy(true); setSolvedState(true); setError(""); resetMetrics(); const difficulty = difficultyEl.value; badgeEl.textContent = labels[difficulty] || "Easy"; try { const res = await fetch(`${API_BASE}/puzzle?difficulty=${difficulty}`); if (!res.ok) throw new Error("Failed to fetch puzzle"); const data = await res.json(); board = data.board.slice(); solution = data.solution.slice(); renderGrid(board, board.map((v, i) => v ? i : -1).filter(i => i >= 0)); startTimer(); setSolvedState(false); } catch (e) { setError(e.message); } finally { setBusy(false); } }
async function solveBoard() { if (busy || solveBtn.disabled) return; setBusy(true); setError(""); try { const res = await fetch(`${API_BASE}/solve`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ board, algorithm: algoEl.value }) }); const data = await res.json(); if (!res.ok) throw new Error(data.detail || "Failed to solve puzzle"); if (data.solved === false) throw new Error("Simulated annealing did not converge. Try another algorithm."); const cells = [...grid.children]; for (let i = 0; i < 81; i++) { if (!prefilled.has(i)) { board[i] = data.solution[i]; cells[i].textContent = data.solution[i]; cells[i].classList.add("solved"); await sleep(30); } } stopTimer(); metricsEl.classList.remove("hidden"); timeEl.textContent = `${Number(data.time).toFixed(2)}s`; statesEl.textContent = data.states_explored ?? 0; backsEl.textContent = data.backtracks ?? 0; setSolvedState(true); } catch (e) { setError(e.message); setSolvedState(false); } finally { setBusy(false); } }

difficultyEl.addEventListener("change", e => badgeEl.textContent = labels[e.target.value] || "Easy");
newBtn.addEventListener("click", loadPuzzle);
solveBtn.addEventListener("click", solveBoard);
renderGrid(Array(81).fill(0), []);
loadPuzzle();