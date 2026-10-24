// ─── GITHUB UNIVERSE INTERACTIVE PARTICLE CONSTELLATION ─────────────────────
const canvas = document.getElementById("github-canvas");
const ctx = canvas.getContext("2d");
let particles = [];

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

class Particle {
  constructor() {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.vx = (Math.random() - 0.5) * 0.55;
    this.vy = (Math.random() - 0.5) * 0.55;
    this.radius = Math.random() * 1.8 + 0.8;
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
    if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
  }
  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(0, 242, 254, 0.65)";
    ctx.fill();
  }
}

function initParticles() {
  const count = window.innerWidth < 600 ? 40 : 75;
  particles = Array.from({ length: count }, () => new Particle());
}
initParticles();

function animateCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let i = 0; i < particles.length; i++) {
    particles[i].update();
    particles[i].draw();
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 125) {
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.strokeStyle = `rgba(138, 43, 226, ${1 - dist / 125})`;
        ctx.lineWidth = 0.7;
        ctx.stroke();
      }
    }
  }
  requestAnimationFrame(animateCanvas);
}
animateCanvas();

// ─── NAVIGATION & TOAST HELPERS ─────────────────────────────────────────────
function getAdminKey() {
  return document.getElementById("admin-key").value.trim();
}

function showToast(msg, isError = false) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.style.background = isError ? "rgba(239, 68, 68, 0.92)" : "rgba(16, 185, 129, 0.92)";
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2600);
}

function switchTab(tabName) {
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
  document.getElementById(`tab-${tabName}`).classList.add("active");
  const navBtn = document.getElementById(`nav-${tabName}`);
  if (navBtn) navBtn.classList.add("active");
  if (tabName === "texts") loadCategoryTexts();
}

// ─── FETCH LIVE OVERVIEW ────────────────────────────────────────────────────
async function fetchOverview() {
  try {
    const res = await fetch("/api/overview");
    const data = await res.json();

    document.getElementById("stat-running").textContent = data.running_count;
    document.getElementById("stat-hosted").textContent = `of ${data.hosted_count} hosted (Max ${data.max_slots})`;
    document.getElementById("stat-users").textContent = data.total_users;
    document.getElementById("stat-texts").textContent = data.total_texts;
    document.getElementById("stat-uptime").textContent = data.uptime;

    const badge = document.getElementById("live-badge");
    badge.textContent = data.bot_on ? "● ENGINE ON" : "● ENGINE OFF";
    badge.className = `status-pill ${data.bot_on ? "online" : "offline"}`;

    // Bank Pills
    const pillBox = document.getElementById("bank-pills");
    pillBox.innerHTML = "";
    const select = document.getElementById("text-category");
    const currentCat = select.value;
    select.innerHTML = "";

    Object.entries(data.text_counts).forEach(([cat, count]) => {
      const pill = document.createElement("div");
      pill.className = "bank-pill";
      pill.innerHTML = `<strong>${cat}</strong>: ${count}`;
      pill.onclick = () => {
        select.value = cat;
        switchTab("texts");
      };
      pillBox.appendChild(pill);

      const opt = document.createElement("option");
      opt.value = cat;
      opt.textContent = `${cat} (${count})`;
      select.appendChild(opt);
    });
    if (currentCat) select.value = currentCat;

    // Accounts List
    const accBox = document.getElementById("accounts-list");
    if (!data.accounts.length) {
      accBox.innerHTML = `<div class="glass-card"><p>No userbots hosted yet. Tap <strong>Deploy</strong> below to add one!</p></div>`;
    } else {
      accBox.innerHTML = data.accounts.map(a => `
        <div class="account-item">
          <div>
            <strong>${a.running ? "🟢" : "🔴"} ${a.name} (Slot #${a.slot + 1})</strong>
            <div style="font-size:0.78rem;color:#94a3b8;">Phone: ${a.phone} • Uptime: ${a.uptime}</div>
          </div>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-glass btn-sm" onclick="accountAction('${a.uid}', ${a.slot}, 'restart')">🔄 Restart</button>
            <button class="btn btn-glass btn-sm" onclick="accountAction('${a.uid}', ${a.slot}, '${a.running ? "stop" : "start"}')">${a.running ? "⏸ Stop" : "▶️ Start"}</button>
            <button class="btn btn-danger btn-sm" onclick="accountAction('${a.uid}', ${a.slot}, 'delete')">🗑️</button>
          </div>
        </div>
      `).join("");
    }

    // Sudo & Blocked Lists
    document.getElementById("sudo-list").innerHTML = data.sudo_users.map(u => `
      <li><span>👑 ${u}</span><button class="btn btn-danger btn-sm" onclick="removeUser('del_sudo', ${u})">Remove</button></li>
    `).join("") || "<li>No Sudo users added</li>";

    document.getElementById("block-list").innerHTML = data.blocked_users.map(u => `
      <li><span>🚫 ${u}</span><button class="btn btn-success btn-sm" onclick="removeUser('unblock_user', ${u})">Unblock</button></li>
    `).join("") || "<li>No Blocked users</li>";

  } catch (err) {
    console.error("Overview error:", err);
  }
}

// ─── TEXT BANK MANAGER ──────────────────────────────────────────────────────
async function loadCategoryTexts() {
  const cat = document.getElementById("text-category").value || "RAID_TEXTS";
  const res = await fetch(`/api/texts?category=${encodeURIComponent(cat)}`);
  const data = await res.json();
  const box = document.getElementById("texts-container");
  box.innerHTML = data.texts.map((t, idx) => `
    <div class="text-item">
      <span><strong>#${idx + 1}</strong> ${t}</span>
      <button class="btn btn-danger btn-sm" onclick="deleteTextFromBank('${cat}', ${idx})">Delete</button>
    </div>
  `).join("");
}

async function addTextToBank() {
  const cat = document.getElementById("text-category").value || "RAID_TEXTS";
  const input = document.getElementById("new-text-input");
  const text = input.value.trim();
  if (!text) return;
  const res = await fetch("/api/texts/add", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Key": getAdminKey() },
    body: JSON.stringify({ category: cat, text })
  });
  if (res.ok) {
    input.value = "";
    showToast("Added to Dipeshxmarco DB!");
    loadCategoryTexts();
    fetchOverview();
  } else {
    showToast("Invalid Admin Key!", true);
  }
}

async function deleteTextFromBank(cat, index) {
  const res = await fetch("/api/texts/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Key": getAdminKey() },
    body: JSON.stringify({ category: cat, index })
  });
  if (res.ok) {
    showToast("Text Removed!");
    loadCategoryTexts();
    fetchOverview();
  } else {
    showToast("Invalid Admin Key!", true);
  }
}

// ─── ACCOUNT & SYSTEM ACTIONS ───────────────────────────────────────────────
async function accountAction(uid, slot, action) {
  const res = await fetch("/api/account/action", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Key": getAdminKey() },
    body: JSON.stringify({ uid, slot, action })
  });
  if (res.ok) {
    showToast(`Account ${action} executed!`);
    setTimeout(fetchOverview, 900);
  } else {
    showToast("Unauthorized: Check Admin Key", true);
  }
}

async function systemAction(action) {
  const res = await fetch("/api/system/action", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Key": getAdminKey() },
    body: JSON.stringify({ action })
  });
  if (res.ok) {
    showToast(`System action: ${action}`);
    fetchOverview();
    if (action === "reset_texts") loadCategoryTexts();
  } else {
    showToast("Unauthorized: Check Admin Key", true);
  }
}

async function manageUser(action, inputId) {
  const val = document.getElementById(inputId).value.trim();
  if (!val) return;
  const res = await fetch("/api/system/action", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Key": getAdminKey() },
    body: JSON.stringify({ action, target_uid: val })
  });
  if (res.ok) {
    document.getElementById(inputId).value = "";
    showToast("User Updated!");
    fetchOverview();
  } else {
    showToast("Check Admin Key", true);
  }
}

async function removeUser(action, target_uid) {
  await fetch("/api/system/action", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Key": getAdminKey() },
    body: JSON.stringify({ action, target_uid })
  });
  showToast("Updated!");
  fetchOverview();
}

// ─── WEB OTP DEPLOY FLOW ────────────────────────────────────────────────────
async function sendWebOTP() {
  const uid = document.getElementById("host-uid").value.trim();
  const phone = document.getElementById("host-phone").value.trim();
  if (!phone) return showToast("Enter phone number!", true);
  showToast("Sending OTP...");
  const res = await fetch("/api/webhost/send_code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid, phone })
  });
  const data = await res.json();
  if (res.ok && data.ok) {
    showToast("OTP Sent! Check Telegram.");
  } else {
    showToast(data.error || "Failed to send OTP", true);
  }
}

async function verifyWebOTP() {
  const phone = document.getElementById("host-phone").value.trim();
  const code = document.getElementById("host-code").value.trim();
  const password = document.getElementById("host-2fa").value.trim();
  showToast("Verifying & Deploying...");
  const res = await fetch("/api/webhost/verify_code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, code, password })
  });
  const data = await res.json();
  if (data.need_2fa) {
    showToast("2FA Required! Enter your 2FA password above and click Verify again.", true);
  } else if (res.ok && data.ok) {
    showToast(`Deployed Slot #${data.slot}!`);
    fetchOverview();
    switchTab("accounts");
  } else {
    showToast(data.error || "Verification failed", true);
  }
}

fetchOverview();
setInterval(fetchOverview, 6000);
