#!/usr/bin/env python3
"""Injects the AI chat panel into index.html"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS (insert before </style>) ──────────────────────────────────────────
CHAT_CSS = r"""
/* ══ AI CHAT PANEL ══════════════════════════════════════════════════════════ */
#chat-fab {
  position: fixed; bottom: 28px; left: 28px; z-index: 900;
  width: 52px; height: 52px; border-radius: 50%;
  background: var(--surface); color: var(--text);
  border: 1px solid var(--border); font-size: 20px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, color 0.2s ease;
}
#chat-fab:hover, #chat-fab.active {
  background: var(--accent); color: #fff; border-color: var(--accent);
  transform: scale(1.08); box-shadow: 0 8px 28px rgba(0,113,227,0.45);
}
#chat-panel {
  position: fixed; bottom: 92px; left: 28px;
  width: 420px; max-width: calc(100vw - 56px);
  max-height: 600px; height: 600px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 24px 80px rgba(0,0,0,0.18), 0 4px 16px rgba(0,0,0,0.1);
  display: flex; flex-direction: column; overflow: hidden;
  z-index: 1001; opacity: 0; pointer-events: none;
  transform: translateY(16px) scale(0.97);
  transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.34,1.56,0.64,1);
}
#chat-panel.open { opacity: 1; transform: translateY(0) scale(1); pointer-events: all; }
.cp-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 15px 18px 13px; border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.cp-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: var(--text); }
.cp-title-icon { font-size: 16px; color: var(--accent); }
.cp-close {
  background: none; border: none; cursor: pointer; color: var(--text2);
  font-size: 16px; padding: 4px 6px; border-radius: 6px; line-height: 1;
  transition: background 0.15s, color 0.15s;
}
.cp-close:hover { background: var(--surface2); color: var(--text); }
#cp-messages {
  flex: 1; overflow-y: auto; padding: 16px; display: flex;
  flex-direction: column; gap: 10px; scroll-behavior: smooth;
}
#cp-messages::-webkit-scrollbar { width: 4px; }
#cp-messages::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
.cp-msg { max-width: 88%; display: flex; flex-direction: column; gap: 4px; }
.cp-msg-user { align-self: flex-end; align-items: flex-end; }
.cp-msg-agent { align-self: flex-start; }
.cp-msg-text {
  padding: 9px 13px; border-radius: 14px; font-size: 13.5px; line-height: 1.5;
  white-space: pre-wrap; word-break: break-word;
}
.cp-msg-user .cp-msg-text { background: var(--accent); color: #fff; border-bottom-right-radius: 4px; }
.cp-msg-agent .cp-msg-text { background: var(--surface2); color: var(--text); border-bottom-left-radius: 4px; }
.cp-msg-img { max-width: 180px; border-radius: 10px; border: 1px solid var(--border); margin-bottom: 4px; }
.cp-typing {
  display: flex; gap: 5px; padding: 11px 14px; background: var(--surface2);
  border-radius: 14px; border-bottom-left-radius: 4px; align-self: flex-start;
}
.cp-typing span {
  width: 6px; height: 6px; background: var(--text2); border-radius: 50%;
  animation: cpBounce 1.2s infinite ease-in-out;
}
.cp-typing span:nth-child(2) { animation-delay: 0.16s; }
.cp-typing span:nth-child(3) { animation-delay: 0.32s; }
@keyframes cpBounce { 0%,80%,100% { transform:translateY(0); } 40% { transform:translateY(-6px); } }
#cp-image-preview {
  padding: 8px 16px 0; display: flex; align-items: center; gap: 10px; flex-shrink: 0;
}
#cp-image-preview img { max-height: 72px; border-radius: 8px; border: 1px solid var(--border); }
#cp-image-preview button {
  background: var(--surface2); border: 1px solid var(--border); border-radius: 50%;
  width: 22px; height: 22px; cursor: pointer; color: var(--text2); font-size: 11px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
#cp-image-preview.cp-hidden, .cp-hidden { display: none !important; }
.cp-input-row {
  display: flex; align-items: flex-end; gap: 10px;
  padding: 12px 14px; border-top: 1px solid var(--border); flex-shrink: 0;
}
#cp-input {
  flex: 1; background: var(--surface2); border: 1px solid var(--border);
  border-radius: 12px; padding: 9px 12px; font-family: var(--font);
  font-size: 13.5px; color: var(--text); resize: none; line-height: 1.5;
  max-height: 110px; outline: none; overflow-y: auto;
  transition: border-color 0.2s;
}
#cp-input:focus { border-color: var(--accent); }
#cp-input::placeholder { color: var(--text2); }
#cp-send {
  width: 36px; height: 36px; border-radius: 50%; background: var(--accent);
  border: none; color: #fff; font-size: 17px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  transition: transform 0.15s, background 0.15s;
}
#cp-send:hover { transform: scale(1.08); }
#cp-send:disabled { background: var(--text2); cursor: not-allowed; transform: none; }
.cp-actions {
  display: flex; gap: 8px; padding: 0 14px 13px; flex-shrink: 0;
}
.cp-action-btn {
  flex: 1; padding: 8px 0; border-radius: 10px; border: 1px solid var(--border);
  font-family: var(--font); font-size: 12.5px; font-weight: 500; cursor: pointer;
  transition: transform 0.15s, opacity 0.15s;
}
.cp-action-btn:hover { transform: scale(1.03); }
.cp-btn-keep { background: var(--green); color: #fff; border-color: var(--green); }
.cp-btn-revert { background: var(--surface2); color: var(--text); }
.cp-btn-refine { background: var(--accent); color: #fff; border-color: var(--accent); }
.cp-status {
  padding: 0 14px 12px; font-size: 12px; color: var(--text2);
  display: flex; align-items: center; gap: 6px; flex-shrink: 0;
}
.cp-status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); flex-shrink: 0; }
.cp-status-dot.pushing { background: var(--orange); animation: cpPulse 1s infinite; }
@keyframes cpPulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
#cp-setup {
  position: absolute; inset: 0; background: var(--surface); border-radius: var(--radius);
  display: flex; align-items: center; justify-content: center; padding: 28px; z-index: 10;
}
.cp-setup-inner { display: flex; flex-direction: column; gap: 14px; width: 100%; }
.cp-setup-title { font-size: 17px; font-weight: 700; color: var(--text); }
.cp-setup-desc { font-size: 12.5px; color: var(--text2); line-height: 1.55; }
.cp-setup-inner input {
  background: var(--surface2); border: 1px solid var(--border); border-radius: 10px;
  padding: 11px 13px; font-family: var(--font); font-size: 13.5px;
  color: var(--text); outline: none; width: 100%; transition: border-color 0.2s;
}
.cp-setup-inner input:focus { border-color: var(--accent); }
.cp-setup-inner input::placeholder { color: var(--text2); }
#cp-setup-save {
  background: var(--accent); color: #fff; border: none; border-radius: 10px;
  padding: 12px; font-family: var(--font); font-size: 14px; font-weight: 600;
  cursor: pointer; transition: transform 0.15s;
}
#cp-setup-save:hover { transform: scale(1.02); }
@media (max-width: 500px) {
  #chat-panel { width: calc(100vw - 24px); left: 12px; bottom: 80px; }
  #chat-fab { bottom: 18px; left: 18px; }
}
"""

html = html.replace('</style>\n</head>', CHAT_CSS + '</style>\n</head>', 1)

# ── 2. HTML (insert before </body>) ──────────────────────────────────────────
CHAT_HTML = r"""
<!-- ══ AI CHAT PANEL ══════════════════════════════════════════════════════ -->
<button id="chat-fab" title="Edit with AI  (press C)">✦</button>

<div id="chat-panel">
  <!-- Setup overlay -->
  <div id="cp-setup">
    <div class="cp-setup-inner">
      <div class="cp-setup-title">Set up AI Editor</div>
      <div class="cp-setup-desc">Your keys stay in your browser (localStorage) and are sent only to Anthropic and GitHub — never stored on any server.</div>
      <input type="password" id="cp-anthropic-key" placeholder="Anthropic API key  (sk-ant-...)">
      <input type="password" id="cp-github-pat" placeholder="GitHub PAT with repo scope  (ghp_...)">
      <button id="cp-setup-save">Start editing →</button>
    </div>
  </div>

  <div class="cp-header">
    <div class="cp-title">
      <span class="cp-title-icon">✦</span>
      Edit This Page
    </div>
    <button class="cp-close" id="cp-close" title="Close (Esc)">✕</button>
  </div>

  <div id="cp-messages"></div>

  <div id="cp-image-preview" class="cp-hidden"></div>

  <div class="cp-input-row">
    <textarea id="cp-input" placeholder="Describe a change… or paste an image" rows="1"></textarea>
    <button id="cp-send" title="Send (Enter)">↑</button>
  </div>

  <div class="cp-actions cp-hidden" id="cp-actions">
    <button class="cp-action-btn cp-btn-keep" id="cp-keep">✓ Keep it</button>
    <button class="cp-action-btn cp-btn-revert" id="cp-revert">↩ Revert</button>
    <button class="cp-action-btn cp-btn-refine" id="cp-refine">✎ Refine</button>
  </div>

  <div class="cp-status cp-hidden" id="cp-status">
    <div class="cp-status-dot" id="cp-status-dot"></div>
    <span id="cp-status-text"></span>
  </div>
</div>
"""

html = html.replace('</body>\n</html>', CHAT_HTML + '\n</body>\n</html>', 1)

# ── 3. JavaScript (new <script> block before </body>) ────────────────────────
CHAT_JS = r"""
<script>
/* ══ AI CHAT PANEL AGENT ═══════════════════════════════════════════════════ */
(function () {
  'use strict';

  const REPO   = 'rousseaukazi/job-impact';
  const BRANCH = 'main';
  const RAW    = `https://raw.githubusercontent.com/${REPO}/${BRANCH}`;
  const GH_API = `https://api.github.com/repos/${REPO}/contents`;
  const ANT_API = 'https://api.anthropic.com/v1/messages';
  const MODEL   = 'claude-opus-4-5';

  /* ── state ── */
  let isOpen        = false;
  let chatMessages  = [];   // Anthropic conversation history
  let pendingPatches = null;
  let pendingMemory  = null;
  let previousContent = null; // HTML before last push (for revert)
  let pastedImage    = null;  // { mediaType, data } base64

  /* ── DOM refs ── */
  const fab       = document.getElementById('chat-fab');
  const panel     = document.getElementById('chat-panel');
  const cpSetup   = document.getElementById('cp-setup');
  const cpAKey    = document.getElementById('cp-anthropic-key');
  const cpGHKey   = document.getElementById('cp-github-pat');
  const cpSavBtn  = document.getElementById('cp-setup-save');
  const cpClose   = document.getElementById('cp-close');
  const cpMsgs    = document.getElementById('cp-messages');
  const cpInput   = document.getElementById('cp-input');
  const cpSend    = document.getElementById('cp-send');
  const cpActions = document.getElementById('cp-actions');
  const cpKeep    = document.getElementById('cp-keep');
  const cpRevert  = document.getElementById('cp-revert');
  const cpRefine  = document.getElementById('cp-refine');
  const cpStatus  = document.getElementById('cp-status');
  const cpStatusDot  = document.getElementById('cp-status-dot');
  const cpStatusText = document.getElementById('cp-status-text');
  const cpImgPrev = document.getElementById('cp-image-preview');

  /* ── storage ── */
  const sk = k => localStorage.getItem(`_aic_${k}`);
  const sw = (k, v) => localStorage.setItem(`_aic_${k}`, v);

  /* ── open / close ── */
  function openPanel() {
    isOpen = true;
    panel.classList.add('open');
    fab.classList.add('active');
    if (!sk('anthropic') || !sk('github')) {
      cpSetup.classList.remove('cp-hidden');
    } else {
      cpSetup.classList.add('cp-hidden');
      if (chatMessages.length === 0) greet();
      setTimeout(() => cpInput.focus(), 120);
    }
  }
  function closePanel() {
    isOpen = false;
    panel.classList.remove('open');
    fab.classList.remove('active');
  }

  fab.addEventListener('click', () => isOpen ? closePanel() : openPanel());
  cpClose.addEventListener('click', closePanel);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && isOpen) { closePanel(); return; }
    if (e.key === 'c' && !e.metaKey && !e.ctrlKey && !e.altKey) {
      const t = document.activeElement.tagName;
      if (t !== 'INPUT' && t !== 'TEXTAREA') {
        e.preventDefault();
        isOpen ? closePanel() : openPanel();
      }
    }
  });

  /* ── setup ── */
  cpSavBtn.addEventListener('click', () => {
    const ak = cpAKey.value.trim();
    const gh = cpGHKey.value.trim();
    if (!ak || !gh) { alert('Both keys are required.'); return; }
    sw('anthropic', ak);
    sw('github', gh);
    cpSetup.classList.add('cp-hidden');
    greet();
    setTimeout(() => cpInput.focus(), 120);
  });

  function greet() {
    addMsg('agent', "I'm your AI editor for this page. Describe any change — wording, data, design, layout — and I'll make it. You can also paste in an image as a reference.");
  }

  /* ── image paste ── */
  document.addEventListener('paste', e => {
    if (!isOpen) return;
    const items = e.clipboardData?.items || [];
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const blob = item.getAsFile();
        const reader = new FileReader();
        reader.onload = ev => {
          const match = ev.target.result.match(/^data:(.+);base64,(.+)$/);
          if (!match) return;
          pastedImage = { mediaType: match[1], data: match[2] };
          cpImgPrev.innerHTML = `<img src="${ev.target.result}" alt="pasted"><button id="cp-img-clear" title="Remove">✕</button>`;
          cpImgPrev.classList.remove('cp-hidden');
          document.getElementById('cp-img-clear').onclick = () => {
            pastedImage = null;
            cpImgPrev.classList.add('cp-hidden');
            cpImgPrev.innerHTML = '';
          };
        };
        reader.readAsDataURL(blob);
        e.preventDefault();
        break;
      }
    }
  });

  /* ── auto-resize textarea ── */
  cpInput.addEventListener('input', () => {
    cpInput.style.height = 'auto';
    cpInput.style.height = Math.min(cpInput.scrollHeight, 110) + 'px';
  });
  cpInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
  cpSend.addEventListener('click', send);

  /* ── send ── */
  async function send() {
    const text = cpInput.value.trim();
    if (!text && !pastedImage) return;
    if (!sk('anthropic') || !sk('github')) { cpSetup.classList.remove('cp-hidden'); return; }

    addMsg('user', text || '(image)', pastedImage ? `data:${pastedImage.mediaType};base64,${pastedImage.data}` : null);

    // Build user content for Anthropic
    const userContent = [];
    if (pastedImage) {
      userContent.push({ type: 'image', source: { type: 'base64', media_type: pastedImage.mediaType, data: pastedImage.data } });
    }
    if (text) userContent.push({ type: 'text', text });
    chatMessages.push({ role: 'user', content: userContent.length === 1 && userContent[0].type === 'text' ? text : userContent });

    cpInput.value = '';
    cpInput.style.height = 'auto';
    pastedImage = null;
    cpImgPrev.classList.add('cp-hidden');
    cpImgPrev.innerHTML = '';
    cpActions.classList.add('cp-hidden');
    cpSend.disabled = true;

    const tid = addTyping();

    try {
      const sys = await buildSystem();
      const raw = await callAnthropic(sys);
      removeTyping(tid);

      let parsed;
      try {
        const m = raw.match(/```json\s*([\s\S]+?)\s*```/) || raw.match(/(\{[\s\S]+\})/);
        parsed = JSON.parse(m ? m[1] : raw);
      } catch (_) {
        addMsg('agent', raw);
        chatMessages.push({ role: 'assistant', content: raw });
        return;
      }

      const { reply, patches, memory } = parsed;
      addMsg('agent', reply || '');
      chatMessages.push({ role: 'assistant', content: reply || '' });

      if (patches && patches.length > 0) {
        pendingPatches = patches;
        pendingMemory  = memory || null;
        cpActions.classList.remove('cp-hidden');
      }
    } catch (err) {
      removeTyping(tid);
      addMsg('agent', `⚠ ${err.message}`);
    } finally {
      cpSend.disabled = false;
    }
  }

  /* ── keep ── */
  cpKeep.addEventListener('click', async () => {
    if (!pendingPatches) return;
    cpActions.classList.add('cp-hidden');
    setStatus('Fetching current file…', true);

    try {
      const { content: curHtml, sha } = await ghGet('index.html');
      previousContent = curHtml;

      // Apply patches
      let newHtml = curHtml;
      for (const p of pendingPatches) {
        if (!newHtml.includes(p.find)) throw new Error(`Patch target not found:\n"${p.find.substring(0, 80)}…"`);
        newHtml = newHtml.split(p.find).join(p.replace);
      }

      setStatus('Pushing to GitHub…', true);
      const msg = `agent: ${pendingMemory || 'update via chat'}`;
      await ghPut('index.html', newHtml, sha, msg);

      // Update memory.md
      if (pendingMemory) {
        try {
          const today = new Date().toISOString().split('T')[0];
          let memContent = '', memSha = null;
          try { const r = await ghGet('memory.md'); memContent = r.content; memSha = r.sha; } catch (_) {}
          const newMem = memContent.trimEnd() + `\n- ${today}: ${pendingMemory}\n`;
          await ghPut('memory.md', newMem, memSha, 'agent: update memory');
        } catch (_) { /* non-fatal */ }
      }

      pendingPatches = null;
      pendingMemory  = null;
      setStatus('Pushed ✓ — live in ~60s', false);
      addMsg('agent', 'Done! The change is live on GitHub. Pages rebuilds in ~60 seconds — just refresh to see it. Hit Revert if you change your mind.');
    } catch (err) {
      clearStatus();
      cpActions.classList.remove('cp-hidden');
      addMsg('agent', `Push failed: ${err.message}`);
    }
  });

  /* ── revert ── */
  cpRevert.addEventListener('click', async () => {
    cpActions.classList.add('cp-hidden');
    if (!previousContent) { addMsg('agent', 'Nothing to revert — no previous version stored.'); return; }
    setStatus('Reverting…', true);
    try {
      const { sha } = await ghGet('index.html');
      await ghPut('index.html', previousContent, sha, 'agent: revert');
      previousContent = null;
      setStatus('Reverted ✓ — live in ~60s', false);
      addMsg('agent', 'Reverted. The previous version is pushing now.');
    } catch (err) {
      clearStatus();
      addMsg('agent', `Revert failed: ${err.message}`);
    }
  });

  /* ── refine ── */
  cpRefine.addEventListener('click', () => {
    cpActions.classList.add('cp-hidden');
    cpInput.placeholder = 'What would you like to adjust?';
    cpInput.focus();
  });

  /* ── GitHub helpers ── */
  async function ghGet(path) {
    const r = await fetch(`${GH_API}/${path}`, {
      headers: { Authorization: `token ${sk('github')}`, Accept: 'application/vnd.github.v3+json' }
    });
    if (!r.ok) throw new Error(`GitHub ${r.status} on GET ${path}`);
    const d = await r.json();
    const bin = atob(d.content.replace(/\n/g, ''));
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return { content: new TextDecoder().decode(bytes), sha: d.sha };
  }

  async function ghPut(path, content, sha, message) {
    const enc = new TextEncoder();
    const bytes = enc.encode(content);
    let bin = '';
    bytes.forEach(b => bin += String.fromCharCode(b));
    const body = { message, content: btoa(bin) };
    if (sha) body.sha = sha;
    const r = await fetch(`${GH_API}/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${sk('github')}`, 'Content-Type': 'application/json', Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify(body)
    });
    if (!r.ok) { const e = await r.json(); throw new Error(e.message || `GitHub ${r.status}`); }
  }

  /* ── Anthropic API ── */
  async function callAnthropic(system) {
    const r = await fetch(ANT_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': sk('anthropic'),
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true'
      },
      body: JSON.stringify({ model: MODEL, max_tokens: 8192, system, messages: chatMessages })
    });
    if (!r.ok) { const e = await r.json(); throw new Error(e.error?.message || `Anthropic ${r.status}`); }
    const d = await r.json();
    return d.content[0].text;
  }

  /* ── system prompt ── */
  async function buildSystem() {
    const [soul, user, memory, { content: curHtml }] = await Promise.all([
      fetch(`${RAW}/soul.md`).then(r => r.ok ? r.text() : '').catch(() => ''),
      fetch(`${RAW}/user.md`).then(r => r.ok ? r.text() : '').catch(() => ''),
      fetch(`${RAW}/memory.md`).then(r => r.ok ? r.text() : '').catch(() => ''),
      ghGet('index.html')
    ]);

    return `You are an AI assistant embedded in the "AI Displacement: America's Tech Workforce" infographic at https://rousseaukazi.github.io/job-impact/

<SOUL>
${soul}
</SOUL>

<USER>
${user}
</USER>

<MEMORY>
${memory}
</MEMORY>

<CURRENT_HTML>
${curHtml}
</CURRENT_HTML>

You help users modify this infographic through conversation. When the user requests a change, you analyze the current HTML and return precise patches.

RESPONSE FORMAT — always return valid JSON (no markdown wrapper):
{
  "reply": "Conversational description of what you're changing and why. Be specific about what will look different.",
  "patches": [
    { "find": "exact string from the HTML (character-perfect, including all whitespace)", "replace": "new string" }
  ],
  "memory": "one-line summary for memory.md, or null if no change"
}

RULES:
- patches[].find must be EXACT — copy-paste accurate from the HTML, including newlines and indentation
- patches = [] if no code change is needed (e.g., answering a question)
- Multiple patches allowed, applied in order
- Be conversational and visual in "reply" — tell the user what will look different, not just what HTML changed
- Never expose or discuss the API keys or GitHub token`;
  }

  /* ── UI helpers ── */
  function addMsg(role, text, imgSrc) {
    const d = document.createElement('div');
    d.className = `cp-msg cp-msg-${role}`;
    let inner = '';
    if (imgSrc) inner += `<img class="cp-msg-img" src="${imgSrc}" alt="">`;
    inner += `<div class="cp-msg-text">${esc(text)}</div>`;
    d.innerHTML = inner;
    cpMsgs.appendChild(d);
    cpMsgs.scrollTop = cpMsgs.scrollHeight;
    return d;
  }

  function addTyping() {
    const id = `cp-t-${Date.now()}`;
    const d = document.createElement('div');
    d.id = id; d.className = 'cp-typing';
    d.innerHTML = '<span></span><span></span><span></span>';
    cpMsgs.appendChild(d);
    cpMsgs.scrollTop = cpMsgs.scrollHeight;
    return id;
  }

  function removeTyping(id) { const el = document.getElementById(id); if (el) el.remove(); }

  function setStatus(text, pushing) {
    cpStatusText.textContent = text;
    cpStatusDot.className = 'cp-status-dot' + (pushing ? ' pushing' : '');
    cpStatus.classList.remove('cp-hidden');
  }
  function clearStatus() { cpStatus.classList.add('cp-hidden'); }

  function esc(s) {
    return String(s || '')
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;').replace(/\n/g,'<br>');
  }
})();
</script>
"""

html = html.replace('</body>\n</html>', CHAT_JS + '</body>\n</html>', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done. Lines:", html.count('\n'))
