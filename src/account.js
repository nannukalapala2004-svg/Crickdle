// Wicketle account panel, shared by the home page and every game.
// Adds a profile button to the header and a panel with: sign in (Google, Apple, email link), sign out,
// delete saved history, and a "Support Wicketle" donate section. Settings come from config.js.
// Games listen for sign-in with WicketleAccount.onChange(user => ...) and use WicketleAccount.load() for Firebase.
(() => {
  const CFG = window.WICKETLE_CONFIG || {};
  const SDK = "https://www.gstatic.com/firebasejs/13.2.0/";
  const ON = !!CFG.firebase;
  const D = CFG.donate || {};
  const HAS_DONATE = !!(D.upi || D.url);
  const listeners = [];
  let fb = null, loading = null, user = null, known = false;

  function load(){
    if (!ON) return Promise.reject(new Error("Sign-in is not switched on"));
    return loading ||= Promise.all(["firebase-app.js", "firebase-auth.js", "firebase-firestore.js"].map(f => import(SDK + f)))
      .then(([app, auth, fs]) => {
        const a = app.initializeApp(CFG.firebase);
        fb = {auth, fs, A: auth.getAuth(a), db: fs.getFirestore(a)};
        return fb;
      });
  }
  window.WicketleAccount = {
    enabled: ON, load,
    get user(){return user;},
    onChange(fn){listeners.push(fn); if (known) fn(user);}
  };

  // ---------- styles ----------
  const css = document.createElement("style");
  css.textContent = `
#bAcct{position:relative;overflow:hidden}#bAcct img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:50%}
#bAcct .dotin{position:absolute;right:7px;bottom:7px;width:9px;height:9px;border-radius:50%;background:#1fa463;box-shadow:0 0 0 2px var(--surface,#fff)}
#dAccount{border:1px solid var(--line);border-radius:22px;padding:0;max-width:min(440px,92vw);width:100%;background:var(--surface);color:var(--ink);box-shadow:var(--shadow)}
#dAccount::backdrop{background:rgb(4 7 24/.6);backdrop-filter:blur(4px)}
#dAccount .wa{padding:24px 22px 20px;position:relative}
#dAccount h2{margin:0 0 6px;font-size:22px;font-weight:700}
#dAccount h3{margin:0 0 4px;font-size:16px;font-weight:600}
#dAccount p{margin:0 0 14px;color:var(--muted);font-size:14px;line-height:1.5}
#dAccount .wx{position:absolute;top:14px;right:14px;width:38px;height:38px;border-radius:50%;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;font-size:20px}
#dAccount .wb{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;min-height:46px;margin:0 0 8px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;font-weight:600;cursor:pointer;text-decoration:none}
#dAccount .wb:hover{border-color:var(--gold)}
#dAccount .wb svg{width:18px;height:18px}
#dAccount .wb.gold{background:linear-gradient(180deg,var(--gold-hi),var(--gold));color:var(--gold-ink);border:0}
#dAccount .wor{display:flex;align-items:center;gap:10px;margin:8px 0 10px;color:var(--muted);font-size:12.5px}
#dAccount .wor::before,#dAccount .wor::after{content:"";flex:1;height:1px;background:var(--line)}
#dAccount input{width:100%;min-height:46px;padding:0 14px;border-radius:12px;border:1px solid var(--line);background:var(--surface-2,var(--surface));color:var(--ink);font:inherit;margin:0 0 8px}
#dAccount input:focus{outline:none;border-color:var(--gold);box-shadow:0 0 0 3px rgb(217 174 91/.2)}
#dAccount .wsec{margin-top:18px;padding-top:18px;border-top:1px solid var(--line)}
#dAccount .who{display:flex;align-items:center;gap:12px;margin:6px 0 14px}
#dAccount .av{width:46px;height:46px;border-radius:50%;flex:none;display:grid;place-items:center;font-weight:700;font-size:19px;color:var(--gold-ink);background:linear-gradient(180deg,var(--gold-hi),var(--gold));overflow:hidden}
#dAccount .av img{width:100%;height:100%;object-fit:cover}
#dAccount .who b{display:block}#dAccount .who small{color:var(--muted)}
#dAccount .wlink{font:inherit;font-size:13px;color:var(--muted);background:none;border:0;padding:0;margin-top:6px;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
#dAccount .upi{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px;border-radius:12px;background:var(--surface-2,var(--surface));border:1px solid var(--line);margin:0 0 8px;font-size:14px}
#dAccount .upi code{font:600 14px/1.3 Poppins,system-ui,sans-serif;color:var(--ink);word-break:break-all}
#dAccount .upi button{font:inherit;font-size:13px;font-weight:600;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:6px 12px;cursor:pointer}
#dAccount .wnote{font-size:12.5px;margin:6px 0 0}
#dAccount a{color:inherit;text-decoration-color:var(--gold);text-underline-offset:3px}
.wtoast{position:fixed;left:50%;bottom:24px;transform:translate(-50%,20px);opacity:0;pointer-events:none;transition:.25s;background:var(--surface);color:var(--ink);border:1px solid var(--gold);padding:10px 18px;border-radius:999px;font-weight:600;box-shadow:var(--shadow);z-index:60;max-width:90vw;text-align:center}
.wtoast.on{opacity:1;transform:translate(-50%,0)}`;
  document.head.appendChild(css);

  // ---------- markup ----------
  const ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8.5" r="4"/><path d="M4.5 20.5c1.4-3.6 4.2-5.4 7.5-5.4s6.1 1.8 7.5 5.4"/></svg>';
  const G = '<svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>';
  const APPLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.6 2.1-3.8 2.2-3.9-1.2-1.8-3.1-2-3.7-2-1.6-.2-3.1.9-3.9.9-.8 0-2-.9-3.4-.9-1.7 0-3.3 1-4.2 2.6-1.8 3.1-.5 7.7 1.3 10.2.9 1.2 1.9 2.6 3.2 2.6 1.3-.1 1.8-.8 3.4-.8 1.5 0 2 .8 3.4.8 1.4 0 2.3-1.3 3.1-2.5 1-1.4 1.4-2.8 1.4-2.9-.1 0-2.8-1.1-2.8-4.1zM13.9 5c.7-.9 1.2-2 1.1-3.2-1 0-2.3.7-3 1.6-.7.8-1.2 2-1.1 3.1 1.1.1 2.3-.6 3-1.5z"/></svg>';
  const HEART = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 21s-7.5-4.6-9.6-9.3C.9 8.3 3 4.5 6.7 4.5c2.1 0 3.6 1.2 4.3 2.4h2c.7-1.2 2.2-2.4 4.3-2.4 3.7 0 5.8 3.8 4.3 7.2C19.5 16.4 12 21 12 21z"/></svg>';
  const esc = s => String(s || "").replace(/[&<>"]/g, c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;"}[c]));
  const onHome = !!document.getElementById("privacy");
  const PRIV = onHome ? "#privacy" : "../#privacy";

  let btn = document.getElementById("bAcct");
  if (!btn) {
    const icons = document.querySelector("header .icons");
    btn = document.createElement("button");
    btn.className = "ib"; btn.id = "bAcct"; btn.type = "button";
    if (icons) icons.prepend(btn); else document.querySelector("header").appendChild(btn);
  }
  btn.hidden = false;
  btn.innerHTML = ICON;
  btn.setAttribute("aria-label", "Account and support"); btn.title = ON ? "Sign in" : "Account and support";

  const dlg = document.createElement("dialog");
  dlg.id = "dAccount"; dlg.setAttribute("aria-labelledby", "waTitle");
  dlg.innerHTML = '<div class="wa"><button class="wx" type="button" aria-label="Close">×</button><div id="waBody"></div></div>';
  document.body.appendChild(dlg);
  dlg.querySelector(".wx").onclick = () => dlg.close();
  dlg.addEventListener("click", e => {if (e.target === dlg) dlg.close();});
  const tst = document.createElement("div"); tst.className = "wtoast"; tst.setAttribute("role", "status"); document.body.appendChild(tst);
  let tt; const toast = m => {tst.textContent = m; tst.classList.add("on"); clearTimeout(tt); tt = setTimeout(() => tst.classList.remove("on"), 2800);};

  function donateHTML(){
    if (!HAS_DONATE) return "";
    const name = D.name || "Wicketle";
    const upiLink = D.upi ? `upi://pay?pa=${encodeURIComponent(D.upi).replace("%40", "@")}&pn=${encodeURIComponent(name)}&cu=INR&tn=${encodeURIComponent("Support Wicketle")}` : "";
    const mobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    return `<div class="wsec"><h3>Support Wicketle</h3>
      <p>${esc(D.message || "Wicketle is free, with no ads. If you enjoy it, a small donation helps keep it running.")}</p>
      ${D.upi ? (mobile ? `<a class="wb gold" href="${upiLink}">${HEART}Donate with UPI</a>` : "") + `<div class="upi"><span>UPI ID: <code>${esc(D.upi)}</code></span><button type="button" id="waCopy">Copy</button></div>` : ""}
      ${D.url ? `<a class="wb${D.upi ? "" : " gold"}" href="${esc(D.url)}" target="_blank" rel="noopener">${D.upi ? "" : HEART}${esc(D.urlLabel || "Donate online")}</a>` : ""}
      <p class="wnote">Payments go straight to Wicketle through your UPI app or the payment site. Wicketle never sees your bank or card details.</p></div>`;
  }
  function draw(){
    const b = document.getElementById("waBody");
    let h;
    if (!ON) {
      h = `<h2 id="waTitle">Your account</h2><p>Accounts are coming soon. For now, your guesses, streaks and stats are saved on this device.</p>`;
    } else if (!user) {
      h = `<h2 id="waTitle">Sign in</h2><p>Save your streaks and history and play on any device.</p>
        <button class="wb" id="waGoogle" type="button">${G}Continue with Google</button>
        ${CFG.appleSignIn ? `<button class="wb" id="waApple" type="button">${APPLE}Continue with Apple</button>` : ""}
        <div class="wor">or use your email</div>
        <form id="waEmailForm"><input id="waEmail" type="email" autocomplete="email" placeholder="you@example.com" aria-label="Email address" required><button class="wb gold" type="submit">Email me a sign-in link</button></form>
        <p class="wnote">No password needed: we email you a link that signs you in. We only use your name, email and photo to show who's signed in. See <a href="${PRIV}">Privacy</a>.</p>`;
    } else {
      const name = user.displayName || user.email || "Signed in";
      h = `<h2 id="waTitle">Your account</h2>
        <div class="who"><span class="av">${user.photoURL ? `<img src="${esc(user.photoURL)}" alt="" referrerpolicy="no-referrer">` : esc(name.charAt(0).toUpperCase())}</span><span><b>${esc(user.displayName || "")}</b><small>${esc(user.email || "")}</small></span></div>
        <p>Your history is saved to your account and syncs when you open each game.</p>
        <button class="wb" id="waOut" type="button">Sign out</button>
        <button class="wlink" id="waDel" type="button">Delete my saved history from my account</button>`;
    }
    b.innerHTML = h + donateHTML();
    const on = (id, f) => {const el = document.getElementById(id); if (el) el.onclick = f;};
    on("waGoogle", () => popup(fb => new fb.auth.GoogleAuthProvider()));
    on("waApple", () => popup(fb => {const p = new fb.auth.OAuthProvider("apple.com"); p.addScope("email"); p.addScope("name"); return p;}));
    const form = document.getElementById("waEmailForm");
    if (form) form.onsubmit = async e => {
      e.preventDefault();
      const email = document.getElementById("waEmail").value.trim(); if (!email) return;
      try {
        const f = await load();
        await f.auth.sendSignInLinkToEmail(f.A, email, {url: location.origin + location.pathname, handleCodeInApp: true});
        try {localStorage.setItem("crickdle:emailForSignIn", email);} catch (x) {}
        b.innerHTML = `<h2 id="waTitle">Check your email</h2><p>We sent a sign-in link to <b>${esc(email)}</b>. Open it on this device to finish signing in. It can take a minute; check your spam folder too.</p>` + donateHTML();
        bindCopy();
      } catch (x) {console.warn(x); toast("Couldn't send the link. Check the address and try again.");}
    };
    on("waOut", async () => {const f = await load(); await f.auth.signOut(f.A); dlg.close(); toast("Signed out. Your progress stays on this device.");});
    on("waDel", async () => {
      if (!confirm("Delete your Wicketle history from your account? It stays on this device.")) return;
      try {const f = await load(); await f.fs.deleteDoc(f.fs.doc(f.db, "users", user.uid)); await f.auth.signOut(f.A); dlg.close(); toast("Deleted from your account and signed out");}
      catch (x) {console.warn(x); toast("Couldn't delete. Please try again.");}
    });
    bindCopy();
  }
  function bindCopy(){
    const c = document.getElementById("waCopy"); if (!c) return;
    c.onclick = async () => {try {await navigator.clipboard.writeText(D.upi); toast("UPI ID copied");} catch (x) {toast(D.upi);}};
  }
  async function popup(make){
    try {const f = await load(); await f.auth.signInWithPopup(f.A, make(f)); dlg.close();}
    catch (x) {if (!/popup-closed|cancelled-popup/.test(x.code || "")) toast("Sign-in didn't work. Please try again."); console.warn(x);}
  }
  btn.onclick = () => {draw(); dlg.showModal();};

  if (!ON) {known = true; return;}
  load().then(async f => {
    // finishing an email-link sign-in
    if (f.auth.isSignInWithEmailLink(f.A, location.href)) {
      let email = null; try {email = localStorage.getItem("crickdle:emailForSignIn");} catch (x) {}
      if (!email) email = prompt("Please confirm your email address to finish signing in");
      try {if (email) {await f.auth.signInWithEmailLink(f.A, email, location.href); try {localStorage.removeItem("crickdle:emailForSignIn");} catch (x) {}}}
      catch (x) {console.warn(x); toast("That sign-in link has expired or was already used. Please request a new one.");}
      history.replaceState(null, "", location.pathname + location.hash);
    }
    f.auth.onAuthStateChanged(f.A, u => {
      const was = user; user = u; known = true;
      btn.innerHTML = ICON + (u && u.photoURL ? `<img src="${esc(u.photoURL)}" alt="" referrerpolicy="no-referrer">` : "") + (u ? '<span class="dotin" aria-hidden="true"></span>' : "");
      btn.setAttribute("aria-label", u ? `Account: signed in as ${u.displayName || u.email}` : "Sign in, account and support");
      btn.title = u ? "Your account" : "Sign in";
      if (u && !was) toast(`Signed in as ${u.displayName || u.email}`);
      for (const fn of listeners) fn(u);
      if (dlg.open) draw();
    });
  }).catch(x => {console.warn("Wicketle: sign-in unavailable", x); known = true;});
})();
