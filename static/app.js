/* Udyam Digital: mobile web app. Plain JS, no build step.
   The server decides every product, price and "no". This file only draws it. */
"use strict";

const UI = {
  en: {
    sub: "Accel Business · online", ph: "Type a message…", steps: ["Chat", "Plan", "Papers", "Track"],
    month: "month", setup: "one-time setup", months: "{n}-month plan", live: "live in about {n} days", liveSame: "live right away",
    recommended: "Recommended", smaller: "Smaller option", included: "What's included", extras: "Add extras", notIncluded: "Not included",
    nearest: "Nearest option", cont: "Continue to paperwork →", ask: "Prices are calculated live from the catalogue.",
    handoffNote: "A sales expert will follow up with this chat.", contAnyway: "Continue online anyway →", save: "You save {x}/month compared with the {y} you pay today",
    more: "{x}/month more than the {y} you pay today", same: "Same as the {y} you pay today", added: "added: needed to work", locked: "🔒",
    people: "People who work with you", peopleSub: "Including you", branches: "Shops or branches", branchesSub: "How many places?",
    go: "Continue", youSaid: "{a} staff · {b} branch(es)", dMenu: "Demo tools", handTitle: "Sales team will follow up",
    handSub: "They get this whole chat, so you won't repeat anything.", orderId: "Order", expected: "Expected live by", advance: "Demo: simulate next step",
    done: "All done. Your service is live! 🎉", reset: "Start over", tryCase: "Try a test case", tryCaseSub: "Each plays the PRD's test conversation.",
    staff: "Open staff view ↗", hood: "Under the hood", hoodSub: "What the code decided on each turn. The AI only talks; prices, eligibility and every “no” come from the rules engine.",
    know: "What the advisor knows", llmOn: "LLM: on (OpenRouter)", llmOff: "LLM: off, keyword advisor", noTrace: "Nothing yet. Say hello!",
    pw: "Paperwork", consentT: "Before we start", consentLead: "We check your business papers only to start your service.",
    c1: ["What we collect", "GST and Udyam numbers, and photos of 4 documents: GST certificate, Udyam certificate, your ID and an address proof."],
    c2: ["Why", "Only to verify your business and set up your connection. Never for marketing."],
    c3: ["How long", "Photos are deleted right after the checks. We keep only the pass or fail result."],
    c4: ["Your rights", "See, correct or delete your data any time."],
    agree: "I agree to this", agreeBtn: "Agree and continue", consentOk: "Consent recorded", withdraw: "Withdraw and delete my data", withdrawn: "Your paperwork data has been deleted.",
    locked2: "Nothing is uploaded until you agree.", idsT: "Business numbers", idsSub: "We fill in your business details from the registry.",
    haveGst: "Do you have a GST number?", yes: "Yes", no: "No", gstin: "GST NUMBER", udyam: "UDYAM NUMBER", check: "Check", chars: "{n}/15",
    docsT: "Documents", docsSub: "A clear photo or a PDF works. All four corners should be visible.", upload: "Upload or take photo", takePhoto: "Photo", uploadFile: "PDF / file", openKyc: "📄 Open paperwork", pdfFail: "Could not open that PDF. Please upload a photo or screenshot instead.", read: "Read", hard: "Hard to read, a reviewer will check",
    remove: "Remove", checkBtn: "Check my papers", checkAgain: "Check again", checking: "Checking…", fix: "Fix", place: "Place my order · {x}/month", placing: "Placing…",
    allGood: "All set!", allGoodSub: "Your papers are verified.", failT: "A few things to fix", failSub: "Fix these, then check again.", reviewT: "A reviewer will take a look", reviewSub: "One photo was hard to read.",
    warnT: "Verified, with a change to your plan", warnSub: "Your GST is not active, so products that need GST were removed.",
    demoT: "🧪 Demo: try a sample applicant", demoSub: "Pick one of the 12 test applicants. We fill everything in.", fill: "Fill it for me",
    docNames: { gst_certificate: "GST certificate", udyam_certificate: "Udyam certificate", signatory_id: "Your ID (signatory)", address_proof: "Address proof (recent bill)" },
    docHints: { gst_certificate: "Registration certificate", udyam_certificate: "Udyam registration", signatory_id: "Aadhaar, PAN or licence", address_proof: "Bill from the last 3 months" },
    placed: "Order placed", err: "Something went wrong. Please try again.", lang: "Language: English", whereBtn: "📦 Where is my order?",
    gstActive: "Active GST registration", plan2: "Your plan was updated", sampleNote: "Sample data",
    liveT: "Your plan, live", estimate: "Estimate", confirmed: "Your plan", noPlanYet: "Tell me about your business and your plan builds here as we talk.",
    assumeLead: "Estimate assumes", assumeFoot: "Answer my questions and this updates.", staffW: "{n} staff", sitesW: "{n} branch(es)", tierW: "Tier {n} city", noGstW: "no GST",
    listening: "Listening… speak now", speaking: "Speaking…", voiceNo: "Voice needs Chrome or Edge. You can still type.", micDenied: "Please allow the microphone to talk.",
    voiceNet: "Voice service not reachable. You can still type.", noHiVoice: "No Hindi voice installed, so replies stay as text.", pillEmpty: "Your plan builds here as we talk",
    spokenPlan: "{plan}: {price} rupees per month, {setup} rupees one-time setup, {months} month plan.", back: "Welcome back. I remember our chat.", micTip: "Talk instead of typing",
    needsT: "What do you need?", needsSub: "Tap to add or remove. The price updates instantly.", gnet: "Internet", gphone: "Phones", gsafe: "Safety and backup", ggrow: "Grow online", gteam: "Team tools",
    pendingGst: "needs GST, to confirm", waitFor: "Still to confirm", w_city: "your city", w_staff: "team size", w_gst: "GST", picked: "Your picks are in the plan.", lockedPre: "Not available: ",
    listenFree: "Listening… just talk, I'll understand"
  },
  hi: {
    sub: "Accel Business · ऑनलाइन", ph: "संदेश लिखें…", steps: ["चैट", "प्लान", "कागज़ात", "ट्रैक"],
    month: "महीना", setup: "एक बार का सेटअप", months: "{n} महीने का प्लान", live: "लगभग {n} दिन में चालू", liveSame: "तुरंत चालू",
    recommended: "सुझाया गया", smaller: "छोटा विकल्प", included: "इसमें क्या है", extras: "एक्स्ट्रा जोड़ें", notIncluded: "शामिल नहीं",
    nearest: "सबसे नज़दीकी विकल्प", cont: "कागज़ी कार्रवाई शुरू करें →", ask: "भाव कैटलॉग से लाइव निकाले जाते हैं।",
    handoffNote: "सेल्स विशेषज्ञ इस चैट के साथ आपसे संपर्क करेंगे।", contAnyway: "फिर भी ऑनलाइन आगे बढ़ें →", save: "आज के {y} के मुकाबले हर महीने {x} की बचत", more: "आज के {y} से हर महीने {x} ज़्यादा", same: "आज के {y} के बराबर",
    added: "जोड़ा गया: चलने के लिए ज़रूरी", locked: "🔒",
    people: "आपके साथ काम करने वाले", peopleSub: "आप समेत", branches: "दुकानें या शाखाएँ", branchesSub: "कितनी जगह?",
    go: "आगे बढ़ें", youSaid: "{a} कर्मचारी · {b} शाखा", dMenu: "डेमो टूल", handTitle: "सेल्स टीम संपर्क करेगी",
    handSub: "उन्हें पूरी चैट मिलती है, आपको कुछ दोहराना नहीं पड़ेगा।", orderId: "ऑर्डर", expected: "चालू होने की उम्मीद", advance: "डेमो: अगला कदम",
    done: "सब हो गया। आपकी सर्विस चालू है! 🎉", reset: "फिर से शुरू करें", tryCase: "टेस्ट केस आज़माएँ", tryCaseSub: "हर एक PRD की टेस्ट बातचीत चलाता है।",
    staff: "स्टाफ व्यू खोलें ↗", hood: "पर्दे के पीछे", hoodSub: "हर बार कोड ने क्या तय किया। AI सिर्फ़ बात करता है; भाव, पात्रता और हर “ना” नियम इंजन से आती है।",
    know: "सहायक को क्या पता है", llmOn: "LLM: चालू (OpenRouter)", llmOff: "LLM: बंद, कीवर्ड सहायक", noTrace: "अभी कुछ नहीं। नमस्ते कहें!",
    pw: "कागज़ात", consentT: "शुरू करने से पहले", consentLead: "हम आपके बिज़नेस के कागज़ सिर्फ़ आपकी सर्विस शुरू करने के लिए जाँचते हैं।",
    c1: ["हम क्या लेते हैं", "GST और Udyam नंबर, और 4 दस्तावेज़ों की फ़ोटो: GST प्रमाणपत्र, Udyam प्रमाणपत्र, आपकी ID और पते का प्रमाण।"],
    c2: ["क्यों", "सिर्फ़ आपका बिज़नेस जाँचने और कनेक्शन शुरू करने के लिए। मार्केटिंग के लिए कभी नहीं।"],
    c3: ["कितने समय तक", "जाँच के तुरंत बाद फ़ोटो मिटा दी जाती हैं। सिर्फ़ पास या फेल का नतीजा रखते हैं।"],
    c4: ["आपके अधिकार", "अपना डेटा कभी भी देखें, सुधारें या मिटाएँ।"],
    agree: "मैं सहमत हूँ", agreeBtn: "सहमत हूँ, आगे बढ़ें", consentOk: "सहमति दर्ज", withdraw: "सहमति वापस लें और मेरा डेटा मिटाएँ", withdrawn: "आपका कागज़ी डेटा मिटा दिया गया है।",
    locked2: "आपके सहमत होने तक कुछ अपलोड नहीं होता।", idsT: "बिज़नेस नंबर", idsSub: "बिज़नेस की जानकारी हम रजिस्ट्री से भर देते हैं।",
    haveGst: "क्या आपके पास GST नंबर है?", yes: "हाँ", no: "नहीं", gstin: "GST नंबर", udyam: "UDYAM नंबर", check: "जाँचें", chars: "{n}/15",
    docsT: "दस्तावेज़", docsSub: "साफ़ फ़ोटो या PDF चलेगा। चारों कोने दिखने चाहिए।", upload: "अपलोड करें या फ़ोटो लें", takePhoto: "फ़ोटो", uploadFile: "PDF / फ़ाइल", openKyc: "📄 कागज़ात खोलें", pdfFail: "वह PDF नहीं खुल सका। कृपया फ़ोटो या स्क्रीनशॉट अपलोड करें।", read: "पढ़ लिया", hard: "पढ़ने में मुश्किल, रिव्यूअर देखेगा",
    remove: "हटाएँ", checkBtn: "मेरे कागज़ात जाँचें", checkAgain: "फिर से जाँचें", checking: "जाँच हो रही है…", fix: "ठीक करें", place: "मेरा ऑर्डर दें · {x}/महीना", placing: "ऑर्डर हो रहा है…",
    allGood: "सब ठीक!", allGoodSub: "आपके कागज़ात सत्यापित हो गए।", failT: "कुछ चीज़ें ठीक करनी हैं", failSub: "इन्हें ठीक करके फिर जाँचें।", reviewT: "रिव्यूअर देखेगा", reviewSub: "एक फ़ोटो पढ़ने में मुश्किल थी।",
    warnT: "सत्यापित, पर प्लान बदला है", warnSub: "आपका GST चालू नहीं है, इसलिए GST वाले प्रोडक्ट हटा दिए गए।",
    demoT: "🧪 डेमो: एक सैंपल आवेदक आज़माएँ", demoSub: "12 टेस्ट आवेदकों में से चुनें। सब हम भर देंगे।", fill: "मेरे लिए भर दो",
    docNames: { gst_certificate: "GST प्रमाणपत्र", udyam_certificate: "Udyam प्रमाणपत्र", signatory_id: "आपकी ID (हस्ताक्षरकर्ता)", address_proof: "पते का प्रमाण (हाल का बिल)" },
    docHints: { gst_certificate: "रजिस्ट्रेशन प्रमाणपत्र", udyam_certificate: "Udyam रजिस्ट्रेशन", signatory_id: "आधार, PAN या लाइसेंस", address_proof: "पिछले 3 महीने का बिल" },
    placed: "ऑर्डर हो गया", err: "कुछ गड़बड़ हुई। कृपया फिर कोशिश करें।", lang: "भाषा: हिंदी", whereBtn: "📦 मेरा ऑर्डर कहाँ है?",
    gstActive: "चालू GST रजिस्ट्रेशन", plan2: "आपका प्लान बदला गया", sampleNote: "सैंपल डेटा",
    liveT: "आपका प्लान, लाइव", estimate: "अनुमान", confirmed: "आपका प्लान", noPlanYet: "अपने बिज़नेस के बारे में बताइए, आपका प्लान बातचीत के साथ यहाँ बनता जाएगा।",
    assumeLead: "अनुमान में माना गया", assumeFoot: "मेरे सवालों के जवाब दें, यह अपडेट होगा।", staffW: "{n} कर्मचारी", sitesW: "{n} शाखा", tierW: "टियर {n} शहर", noGstW: "GST नहीं",
    listening: "सुन रहा हूँ… बोलिए", speaking: "बोल रहा हूँ…", voiceNo: "वॉइस के लिए Chrome या Edge चाहिए। आप टाइप कर सकते हैं।", micDenied: "बात करने के लिए माइक्रोफ़ोन की अनुमति दें।",
    voiceNet: "वॉइस सेवा नहीं मिली। आप टाइप कर सकते हैं।", noHiVoice: "हिंदी आवाज़ इंस्टॉल नहीं है, इसलिए जवाब टेक्स्ट में रहेंगे।", pillEmpty: "आपका प्लान बातचीत के साथ यहाँ बनता है",
    spokenPlan: "{plan}: {price} रुपये प्रति माह, {setup} रुपये एक बार का सेटअप, {months} महीने का प्लान।", back: "वापसी पर स्वागत है। मुझे हमारी बातचीत याद है।", micTip: "टाइप करने की जगह बोलिए",
    needsT: "आपको क्या चाहिए?", needsSub: "जोड़ने या हटाने के लिए टैप करें। भाव तुरंत बदलता है।", gnet: "इंटरनेट", gphone: "फ़ोन", gsafe: "सुरक्षा और बैकअप", ggrow: "ऑनलाइन बढ़ें", gteam: "टीम के औज़ार",
    pendingGst: "GST चाहिए, पक्का करना है", waitFor: "अभी पक्का करना है", w_city: "आपका शहर", w_staff: "टीम का आकार", w_gst: "GST", picked: "आपकी पसंद प्लान में है।", lockedPre: "उपलब्ध नहीं: ",
    listenFree: "सुन रहा हूँ… बस बोलिए, मैं समझ लूँगा"
  }
};
const ICON = { P01: "🌐", P02: "🌐", P03: "🌐", P04: "📡", P05: "🔌", P06: "☎️", P07: "📱", P08: "📟", P09: "🔁", P10: "🔀", P11: "📞", P12: "🎥", P13: "📍", P14: "📶",
  P15: "💬", P16: "✉️", P17: "☁️", P18: "🌍", P19: "🧾", P20: "🛡️", P21: "🏭", P22: "🏠", P23: "📹", P24: "📞", P25: "📒" };
const DOC_ICON = { gst_certificate: "🧾", udyam_certificate: "🏷️", signatory_id: "🪪", address_proof: "🏠" };
const STAGE_IDX = { chat: 0, plan: 1, declined: 1, kyc: 2, order: 3 };

const LANGS = { en: ["en-IN", "English"], hi: ["hi-IN", "हिन्दी"], mr: ["mr-IN", "मराठी"], ta: ["ta-IN", "தமிழ்"], te: ["te-IN", "తెలుగు"],
  bn: ["bn-IN", "বাংলা"], gu: ["gu-IN", "ગુજરાતી"], kn: ["kn-IN", "ಕನ್ನಡ"], ml: ["ml-IN", "മലയാളം"] };
const S = { speech: "en", speechAuto: true, preview: null, prevLive: {}, liveMonthly: null, sid: null, lang: "en", quote: null, stage: "chat", order: null, busy: false, health: {}, scenarios: [], lastChips: [], trace: [], profile: {} };
const $ = (s, el = document) => el.querySelector(s);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const ui = () => UI[S.lang];
const inr = n => "₹" + Number(n).toLocaleString("en-IN");
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = s => esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br>");
const now = () => new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });

function h(tag, props = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") el.className = v;
    else if (k === "html") el.innerHTML = v;
    else if (k === "text") el.textContent = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) el.setAttribute(k, v === true ? "" : v);
  }
  kids.flat().forEach(k => k != null && el.append(k.nodeType ? k : document.createTextNode(k)));
  return el;
}

async function api(path, body, opts = {}) {
  try {
    const r = await fetch(path, body === undefined || opts.get ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok && !opts.raw) throw new Error(r.status);
    return await r.json();
  } catch (e) { toast(ui().err); throw e; }
}
let toastT;
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 2600); }

/* ------------------------------------------------------------------ chat */
const chat = $("#chat");
function scrollDown() { requestAnimationFrame(() => { chat.scrollTop = chat.scrollHeight; }); }
function addBubble(text, who) {
  const row = h("div", { class: "row " + who }, h("div", { class: "bubble" }, h("div", { html: fmt(text) }), h("time", { text: now() })));
  chat.append(row); scrollDown(); return row;
}
function addNotice(text) { chat.append(h("div", { class: "notice", text })); scrollDown(); }
function typing() { const t = h("div", { class: "row bot" }, h("div", { class: "typing" }, h("span"), h("span"), h("span"))); chat.append(t); scrollDown(); return t; }
function addCard(el) { const row = h("div", { class: "row bot" }, el); chat.append(row); scrollDown(); return el; }

const reduced = () => matchMedia("(prefers-reduced-motion:reduce)").matches;
async function streamBubble(text) {
  const body = h("div"), cur = h("span", { class: "stream-cur" });
  const row = h("div", { class: "row bot" }, h("div", { class: "bubble" }, body, h("time", { text: now() })));
  chat.append(row);
  if (document.hidden || reduced()) { body.innerHTML = fmt(text); scrollDown(); return row; }
  const parts = text.split(/(\s+)/), per = Math.max(9, Math.min(34, 1500 / Math.max(1, parts.length / 2)));
  let acc = "";
  for (let i = 0; i < parts.length; i++) {
    acc += parts[i];
    if (i % 2 === 0) {
      body.innerHTML = fmt((acc.match(/\*\*/g) || []).length % 2 ? acc + "**" : acc); body.append(cur); scrollDown(); await sleep(per);
    }
  }
  body.innerHTML = fmt(text); scrollDown();
  return row;
}

function queueBot(msgs, fast) { S.botQ = (S.botQ || Promise.resolve()).then(() => showBot(msgs, fast)); return S.botQ; }

async function showBot(msgs, fast = false) {
  setChips([]);
  for (const m of msgs) {
    if (m.text) {
      if (!fast) { const t = typing(); await sleep(220); t.remove(); }
      speak(m.text);
      if (fast) addBubble(m.text, "bot"); else await streamBubble(m.text);
    }
    for (const c of m.cards || []) {
      if (!fast && c.type !== "open_kyc") { const t = typing(); await sleep(160); t.remove(); }
      renderCard(c);
      if (c.type === "plan" && !c.smaller && !c.handoff) speakPlan(c.quote);
    }
  }
  const last = msgs[msgs.length - 1];
  setChips(last && last.chips || []);
}

function setChips(chips) {
  S.lastChips = chips;
  const box = $("#chips"); box.innerHTML = "";
  const list = chips.slice();
  if (S.stage === "kyc" && !K.open && !list.some(c => c.action === "start_kyc")) list.push({ label: ui().openKyc, hi: ui().openKyc, action: "start_kyc" });
  list.forEach((c, i) => {
    const b = h("button", { class: "chip" + (c.action === "start_kyc" ? " primary" : ""), style: `animation-delay:${i * 40}ms`, type: "button" }, S.lang === "hi" && c.hi ? c.hi : c.label);
    b.onclick = () => onChip(c);
    box.append(b);
  });
}
function onChip(c) {
  if (S.busy) return;
  const label = S.lang === "hi" && c.hi ? c.hi : c.label;
  if (c.focus) { $("#msg").focus(); return; }
  if (c.slot) return say(label, "", { slot: c.slot, value: c.value });
  if (c.action) { const { label: _l, hi: _h, ...rest } = c; return say(label, "", rest); }
  if (c.text) return say(c.text, c.text);
}

async function say(label, text, payload, voice) {
  if (S.busy) return;
  S.busy = true; $("#sendBtn").disabled = true;
  try {
    if (label) addBubble(label, "user");
    setChips([]);
    const t = typing();
    const res = await api("/api/chat", { session_id: S.sid, message: text || "", label: label || "", payload: payload || null, voice: !!voice });
    await sleep(250); t.remove();
    afterReply(res);
    await queueBot(res.messages, false);
  } catch (e) { /* toast shown */ }
  finally { S.busy = false; $("#sendBtn").disabled = false; if (V.on && !V.speaking) setTimeout(listen, 120); }
}

function afterReply(res) {
  if (res.lang && res.lang !== S.lang) applyLang(res.lang, false);
  followReplyLanguage(res);
  S.stage = res.stage; S.profile = res.profile || {}; S.preview = res.preview || null;
  syncNeeds(res.needs);
  renderStepper();
  if (res.trace && res.trace.length) { S.trace = [...res.trace.slice().reverse(), ...S.trace].slice(0, 14); }
  renderHood();
}

$("#composer").addEventListener("submit", e => {
  e.preventDefault();
  const v = $("#msg").value.trim(); if (!v) return;
  $("#msg").value = ""; say(v, v);
});

/* ------------------------------------------------------------------ stepper */
function renderStepper() {
  const idx = STAGE_IDX[S.stage] ?? 0;
  $("#stepper").innerHTML = ui().steps.map((s, i) => `<div class="step ${i < idx ? "done" : i === idx ? "on" : ""}"><i></i>${esc(s)}</div>`).join("");
}

/* ------------------------------------------------------------------ cards */
function renderCard(c) {
  if (c.type === "counts") return addCard(countsCard());
  if (c.type === "needs") return addCard(needsCard(c.tiles));
  if (c.type === "plan") return addCard(planCard(c));
  if (c.type === "handoff") return addCard(handoffCard());
  if (c.type === "tracker") { S.order = c.order; return addCard(trackerCard(c.order)); }
  if (c.type === "open_kyc") { setTimeout(openKyc, 350); }
}

function countsCard() {
  const U = ui();
  const el = h("div", { class: "card" });
  let staff = 5, sites = 1;
  const row = (title, sub, get, set, min, max) => {
    const out = h("input", { class: "num", type: "number", inputmode: "numeric", min, max, value: get(), "aria-label": title, style: "width:64px;text-align:center;font-size:22px;font-weight:800;border:0;background:transparent;color:inherit;font-family:inherit" });
    out.oninput = () => { set(Math.max(min, Math.min(max, parseInt(out.value) || min))); };
    const mk = (d, t) => h("button", { type: "button", "aria-label": t, text: d > 0 ? "+" : "−", onclick: () => { set(Math.max(min, Math.min(max, get() + d))); out.value = get(); } });
    return h("div", { class: "r" }, h("div", {}, h("b", { text: title }), h("small", { text: sub })), h("div", { class: "stepper2" }, mk(-1, "less"), out, mk(1, "more")));
  };
  const go = h("button", { class: "btn", type: "button", text: U.go + " →" });
  go.onclick = () => {
    el.classList.add("done"); go.disabled = true;
    say(U.youSaid.replace("{a}", staff).replace("{b}", sites), "", { slot: "counts", staff, sites });
  };
  el.append(h("div", { class: "counts interactive" },
    row(U.people, U.peopleSub, () => staff, v => staff = v, 1, 500),
    row(U.branches, U.branchesSub, () => sites, v => sites = v, 1, 50),
    h("div", { style: "padding-top:8px" }, go)));
  return el;
}

function handoffCard() {
  const U = ui();
  return h("div", { class: "card" }, h("div", { class: "handoff" }, h("div", { class: "ico", text: "🤝" }), h("div", {}, h("b", { text: U.handTitle }), h("p", { text: U.handSub }))));
}

/* ---- plan card ---- */
function planCard(c) {
  document.querySelectorAll(".card.plan").forEach(e => e.classList.add("stale"));
  const el = h("div", { class: "card plan" });
  el._opts = { handoff: c.handoff, smaller: c.smaller };
  S.quote = c.quote;
  paintPlan(el, c.quote);
  el.addEventListener("click", async e => {
    const b = e.target.closest("[data-act]"); if (!b || b.disabled) return;
    const q = el._quote; const items = { ...q.quantities };
    const id = b.dataset.id;
    if (b.dataset.act === "inc") items[id] = (items[id] || 0) + 1;
    if (b.dataset.act === "dec") items[id] = Math.max(0, (items[id] || 0) - 1);
    if (b.dataset.act === "cta") { onChip({ action: "start_kyc", label: ui().cont, hi: ui().cont }); return; }
    if (b.dataset.act === "inc" || b.dataset.act === "dec") requote(el, items);
  });
  el.addEventListener("change", e => {
    const sw = e.target.closest("input[data-extra]"); if (!sw) return;
    const items = { ...el._quote.quantities };
    if (sw.checked) items[sw.dataset.extra] = 1; else delete items[sw.dataset.extra];
    requote(el, items);
  });
  return el;
}
async function requote(el, items) {
  try {
    const r = await api("/api/quote", { session_id: S.sid, items });
    el._opts.handoff = r.quote.handoff;
    paintPlan(el, r.quote, true); S.quote = r.quote; S.preview = { quote: r.quote, assumed: [], final: true }; renderHood();
    if (r.quote.notes && r.quote.notes.length) toast(r.quote.notes[0].for_name + ": " + r.quote.notes[0].reason);
  } catch (e) { paintPlan(el, el._quote); }
}
function countUp(node, from, to) {
  if (from === to || matchMedia("(prefers-reduced-motion:reduce)").matches) return;
  const t0 = Date.now();
  const id = setInterval(() => {
    const p = Math.min(1, (Date.now() - t0) / 380);
    node.firstChild.textContent = inr(p >= 1 ? to : Math.round(from + (to - from) * (1 - Math.pow(1 - p, 3))));
    if (p >= 1) clearInterval(id);
  }, 30);
}
function paintPlan(el, q, animate) {
  const U = ui(), T = q.totals, o = el._opts || {};
  const prev = el.querySelector(".big"); const prevVal = prev ? parseInt(prev.dataset.now) : null;
  el._quote = q;
  let sav = "";
  if (q.savings) {
    const d = q.savings.diff;
    sav = d > 0 ? `<div class="save good">💚 ${esc(U.save.replace("{x}", inr(d)).replace("{y}", inr(q.savings.spend)))}</div>`
      : d < 0 ? `<div class="save neutral">ℹ️ ${esc(U.more.replace("{x}", inr(-d)).replace("{y}", inr(q.savings.spend)))}</div>`
        : `<div class="save neutral">${esc(U.same.replace("{y}", inr(q.savings.spend)))}</div>`;
  }
  const items = q.items.map(i => `
    <div class="item"><div class="ico" aria-hidden="true">${ICON[i.id] || "📦"}</div>
      <div class="m"><b>${esc(i.name)}</b>${i.qty > 1 && !i.editable ? `<span class="xqty">×${i.qty}</span>` : ""}${i.auto_added ? `<span class="pill">${esc(U.added)}</span>` : ""}
        <p>${esc(i.reason)}</p>
        ${i.editable && !o.smaller ? `<div class="qty interactive"><button data-act="dec" data-id="${i.id}" aria-label="Less ${esc(i.name)}" ${i.qty <= i.min_qty ? "disabled" : ""}>−</button><span>${i.qty}</span><button data-act="inc" data-id="${i.id}" aria-label="More ${esc(i.name)}">+</button></div>` : ""}
      </div>
      <div class="p">${inr(i.monthly)}<small>${i.qty > 1 ? `${inr(i.unit)} × ${i.qty}` : "/" + esc(U.month)}</small></div></div>`).join("");
  const extras = (!o.smaller && q.extras.length) ? `<div class="sec interactive"><h4>${esc(U.extras)}</h4>${q.extras.map(x => `
    <label class="extra ${x.allowed ? "" : "locked"}"><div class="ico" aria-hidden="true">${x.allowed ? ICON[x.id] || "➕" : "🔒"}</div>
      <div class="m"><b>${esc(x.name)} <span style="color:var(--ink-2);font-weight:600">+${inr(x.price)}</span></b>
        <p class="${x.allowed ? "" : "lock"}">${esc(x.allowed ? x.blurb : x.reason)}</p></div>
      <span class="sw"><input type="checkbox" data-extra="${x.id}" ${x.on ? "checked" : ""} ${x.allowed ? "" : "disabled"} aria-label="${esc(x.name)}"><i></i></span></label>`).join("")}</div>` : "";
  const refused = q.refused.length ? `<div class="sec"><h4>${esc(U.notIncluded)}</h4>${q.refused.map(r => {
    const alts = (r.alternatives || []).map(a => a.name);
    return `<div class="refused"><span class="x">⚠️</span><div><b>${esc(r.name)}</b><p>${esc(r.reason)}</p>${alts.length ? `<p class="alt">${esc(U.nearest)}: ${esc(alts.join(" / "))}</p>` : ""}</div></div>`;
  }).join("")}</div>` : "";
  const cta = o.smaller ? "" : o.handoff
    ? `<div class="cta interactive"><div class="fine">🤝 ${esc(U.handoffNote)}</div><button class="btn ghost" data-act="cta" ${q.items.length ? "" : "disabled"}>${esc(U.contAnyway)}</button></div>`
    : `<div class="cta interactive"><button class="btn" data-act="cta" ${q.items.length ? "" : "disabled"}>${esc(U.cont)}</button><div class="fine">${esc(U.ask)}</div></div>`;
  el.innerHTML = `
    <div class="card-h"><span class="tag">${esc(o.smaller ? U.smaller : U.recommended)}</span><h3>${esc(q.plan_name)}</h3><p>${esc(q.tagline)}</p></div>
    <div class="price"><div class="big" data-now="${T.monthly}">${inr(T.monthly)}<small> /${esc(U.month)}</small></div>
      <div class="sub"><span>🧾 ${inr(T.setup)} ${esc(U.setup)}</span><span>📅 ${esc(U.months.replace("{n}", T.contract_months))}</span><span>🚚 ${esc(T.expected_days > 0 ? U.live.replace("{n}", T.expected_days) : U.liveSame)}</span></div>${sav}</div>
    <div class="sec"><h4>${esc(U.included)}</h4>${items || "<p class='fine'>—</p>"}</div>${extras}${refused}${cta}`;
  if (animate && prevVal !== null) countUp(el.querySelector(".big"), prevVal, T.monthly);
}

/* ---- tracker ---- */
function trackerCard(o) {
  const el = h("div", { class: "card tracker", "data-order": o.id });
  paintTracker(el, o);
  el.addEventListener("click", async e => {
    if (!e.target.closest("[data-adv]")) return;
    const r = await api(`/api/order/${o.id}/advance`, {});
    S.order = r.order;
    document.querySelectorAll(`.tracker[data-order="${o.id}"]`).forEach(x => paintTracker(x, r.order));
    addBubble("🔔 " + r.message, "bot");
  });
  return el;
}
function paintTracker(el, o) {
  const U = ui();
  const d = new Date(o.expected_date + "T00:00");
  const ds = d.toLocaleDateString(S.lang === "hi" ? "hi-IN" : "en-IN", { weekday: "short", day: "numeric", month: "short" });
  const lis = o.stages.map((s, i) => {
    const hist = o.history.find(x => x.stage === i);
    const cls = i < o.stage || (o.done && i === o.stage) ? "done" : i === o.stage ? "now" : "todo";
    return `<li class="${cls}"><span class="c">${cls === "done" ? "✓" : ""}</span><b>${esc(s)}</b>${hist ? `<small>${esc(hist.at)}</small>` : ""}</li>`;
  }).join("");
  el.innerHTML = `<div class="orderid"><span>${esc(U.orderId)} <code>${esc(o.id)}</code></span><span class="pill">${esc(o.plan)}</span></div>
    <div class="exp"><small>${esc(U.expected)}</small><b>${esc(o.done ? "🎉 " + U.done : ds)}</b></div><ul class="tl">${lis}</ul>
    ${o.done ? "" : `<div class="cta"><button class="btn ghost sm" data-adv>${esc(U.advance)}</button></div>`}`;
}

/* ------------------------------------------------------------------ language */
async function setLang(l) {
  S.speech = l; S.speechAuto = false;                        // a manual choice is respected until "Auto" is picked again
  const sel = $("#speechLang"); if (sel) sel.value = l;
  if (l === S.lang) return;
  const r = await api("/api/lang", { session_id: S.sid, language: l });
  applyLang(r.lang, true);
  if (r.quote) {
    S.quote = r.quote;
    const cards = document.querySelectorAll(".card.plan:not(.stale)");
    const el = cards[cards.length - 1];
    if (el) { el._opts.handoff = r.quote.handoff; paintPlan(el, r.quote); }
  }
}
function applyLang(l, notice) {
  S.lang = l; document.documentElement.lang = l;
  $("#lEn").setAttribute("aria-pressed", l === "en"); $("#lHi").setAttribute("aria-pressed", l === "hi");
  $("#subtitle").textContent = ui().sub; $("#msg").placeholder = ui().ph;
  renderStepper(); renderSides(); setChips(S.lastChips);
  if (notice) addNotice(ui().lang);
  if (K.open) renderKyc();
}
$("#lEn").onclick = () => setLang("en"); $("#lHi").onclick = () => setLang("hi");

/* ------------------------------------------------------------------ KYC sheet */
let K = { open: false, consent: null, hasGst: true, gst: null, udyam: null, docs: {}, samples: [], results: null, typed: "", udyamVal: "", gstVal: "", thumbs: {}, busy: false, planNote: false };
const sheet = $("#kycSheet");

async function openKyc() {
  const st = await api(`/api/kyc/state?session_id=${S.sid}`, undefined, { get: true });
  Object.assign(K, { consent: st.consent, hasGst: st.has_gstin, samples: st.samples, open: true });
  if (st.typed_gstin && !K.gstVal) K.gstVal = st.typed_gstin;
  renderKyc(); sheet.classList.add("open");
}
$("#kycClose").onclick = () => { sheet.classList.remove("open"); K.open = false; setChips(S.lastChips); };
$("#stepper").addEventListener("click", e => { if (S.stage === "kyc" && e.target.closest(".step:nth-child(3)")) openKyc(); });

function renderKyc() {
  const U = ui(), body = $("#kycBody"), foot = $("#kycFoot");
  $("#kycTitle").textContent = U.pw;
  const keepScroll = body.scrollTop; body.innerHTML = ""; foot.innerHTML = "";
  if (!K.consent) {
    const lines = [["🗂️", U.c1], ["🎯", U.c2], ["⏳", U.c3], ["⚖️", U.c4]].map(([i, c]) => `<li><span>${i}</span><div><b>${esc(c[0])}</b><small>${esc(c[1])}</small></div></li>`).join("");
    const b = h("div", { class: "blk", html: `<h3>🔐 ${esc(U.consentT)}</h3><p>${esc(U.consentLead)}</p><ul class="lines">${lines}</ul>
      <label class="check"><input type="checkbox" id="agree"><span>${esc(U.agree)}</span></label>` });
    const btn = h("button", { class: "btn", id: "agreeBtn", disabled: true, text: U.agreeBtn });
    b.append(h("div", { style: "margin-top:10px" }, btn));
    $("#agree", b).onchange = e => btn.disabled = !e.target.checked;
    btn.onclick = async () => { await api("/api/consent", { session_id: S.sid }); K.consent = { version: "v1.0" }; renderKyc(); };
    body.append(b);
    foot.append(h("div", { class: "fine", text: "🔒 " + U.locked2 }));
    return;
  }
  // consent recorded bar
  body.append(h("div", { class: "fine", style: "display:flex;justify-content:space-between;align-items:center;padding:0 4px" },
    h("span", { text: "✓ " + U.consentOk + " (" + (K.consent.version || "v1.0") + ")" }),
    h("button", { class: "x-btn", style: "font-size:12px;width:auto;padding:4px 10px;color:var(--red)", text: U.withdraw, onclick: withdraw })));
  body.append(h("div", { id: "kRes" }));
  body.append(demoBlock());
  body.append(idsBlock());
  body.append(docsBlock());
  paintResults();
  const check = h("button", { class: "btn", id: "kCheck", text: K.results ? U.checkAgain : U.checkBtn, onclick: runVerify });
  foot.append(check);
  if (K.results && K.results.overall === "pass") {
    check.className = "btn ghost"; foot.prepend(h("button", { class: "btn", id: "kPlace", text: U.place.replace("{x}", inr(S.quote ? S.quote.totals.monthly : 0)), onclick: placeOrder }));
  }
  body.scrollTop = keepScroll;
}

async function withdraw() {
  const r = await api("/api/consent/withdraw", { session_id: S.sid });
  K = { ...K, consent: null, gst: null, udyam: null, docs: {}, results: null, gstVal: "", udyamVal: "", thumbs: {} };
  renderKyc(); toast(r.message);
}

function demoBlock() {
  const U = ui();
  const sel = h("select", { id: "sample", "aria-label": U.demoT }, K.samples.map(s => h("option", { value: s.id, text: `${s.id} · ${s.issue}` })));
  const btn = h("button", { class: "btn sm", text: U.fill, onclick: () => fillSample(sel.value, btn) });
  return h("details", { class: "demo" }, h("summary", { text: U.demoT }), h("p", { style: "margin:6px 0 0;font-size:12.5px;color:var(--ink-2)", text: U.demoSub }), sel, btn);
}

function idsBlock() {
  const U = ui();
  const b = h("div", { class: "blk", id: "kIds" });
  b.append(h("h3", { html: `<span class="n ${K.gst && K.gst.ok || K.udyam && K.udyam.ok ? "ok" : ""}">1</span>${esc(U.idsT)}` }), h("p", { text: U.idsSub }));
  const seg = h("div", { class: "seg", role: "group", "aria-label": U.haveGst },
    h("button", { type: "button", "aria-pressed": K.hasGst, text: U.yes, onclick: () => setHasGst(true) }),
    h("button", { type: "button", "aria-pressed": !K.hasGst, text: U.no, onclick: () => setHasGst(false) }));
  b.append(h("label", { style: "display:block;font-size:13px;font-weight:700;margin-top:6px", text: U.haveGst }));
  b.append(seg);
  if (K.hasGst) {
    b.append(h("div", { class: "field" }, h("label", { for: "gstin", text: U.gstin }),
      h("div", { class: "inp", id: "gstBox" }, h("input", { id: "gstin", maxlength: 15, placeholder: "22AAAAA0000A1Z5", autocomplete: "off", spellcheck: "false", value: K.gstVal, "aria-describedby": "gstMsg" }), h("span", { class: "cnt", id: "gstCnt" }), h("span", { class: "st", id: "gstSt" })),
      h("div", { class: "msg", id: "gstMsg" }), h("div", { id: "bizBox" })));
  }
  b.append(h("div", { class: "field" }, h("label", { for: "udyam", text: U.udyam }),
    h("div", { class: "inp", id: "udBox" }, h("input", { id: "udyam", maxlength: 24, placeholder: "UDYAM-MP-23-0001001", autocomplete: "off", spellcheck: "false", value: K.udyamVal }), h("span", { class: "st", id: "udSt" })),
    h("div", { class: "msg", id: "udMsg" })));
  queueMicrotask(() => {
    const g = $("#gstin"), u = $("#udyam");
    if (g) { g.oninput = () => { g.value = g.value.toUpperCase().replace(/\s/g, ""); K.gstVal = g.value; $("#gstCnt").textContent = U.chars.replace("{n}", g.value.length); if (g.value.length === 15) checkGst(); else setField("gst", "", ""); };
      g.onblur = () => { if (g.value.length && g.value.length < 15) setField("gst", "bad", "This GST number looks wrong. Please check it.".replace(/.*/, S.lang === "hi" ? "यह GST नंबर गलत लगता है। कृपया जाँचें।" : "This GST number looks wrong. Please check it.")); };
      if (K.gstVal.length === 15 && K.gst) paintGst(K.gst); else $("#gstCnt").textContent = K.gstVal ? U.chars.replace("{n}", K.gstVal.length) : ""; }
    if (u) { u.oninput = () => { u.value = u.value.toUpperCase().replace(/\s/g, ""); K.udyamVal = u.value; if (u.value.length >= 19) checkUdyam(); else setField("ud", "", ""); };
      if (K.udyam) paintUdyam(K.udyam); }
  });
  return b;
}
function setField(which, state, msg) {
  const box = $(which === "gst" ? "#gstBox" : "#udBox"), m = $(which === "gst" ? "#gstMsg" : "#udMsg"), st = $(which === "gst" ? "#gstSt" : "#udSt");
  if (!box) return;
  box.className = "inp " + state; m.className = "msg " + state; m.textContent = msg;
  st.textContent = state === "ok" ? "✅" : state === "bad" ? "❌" : state === "warn" ? "⚠️" : "";
}
async function setHasGst(v) {
  if (K.hasGst === v) return;
  K.hasGst = v; K.results = null;
  if (!v) { await api("/api/kyc/gstin", { session_id: S.sid, no_gst: true }); K.gst = null; K.gstVal = ""; delete K.docs.gst_certificate; }
  renderKyc();
}
async function checkGst() {
  const r = await api("/api/kyc/gstin", { session_id: S.sid, gstin: K.gstVal }); K.gst = r; paintGst(r);
  if (r.plan_changed) {
    S.quote = r.quote; K.planNote = true; S.preview = { quote: r.quote, assumed: [], final: true }; renderHood();
    setTimeout(async () => { await showBot([{ text: r.chat }, { cards: [{ type: "plan", quote: r.quote, handoff: !!r.quote.handoff }] }], true); }, 200);
  }
}
function paintGst(r) {
  const box = $("#bizBox"); if (!box) return;
  if (r.ok) setField("gst", "ok", "✓ " + ui().gstActive);
  else setField("gst", r.stage === "status" ? "warn" : "bad", r.message);
  box.innerHTML = r.legal_name ? `<div class="biz ${r.ok ? "" : "warn"}"><b>${esc(r.legal_name)}</b><span>${esc(r.masked)} · ${esc(r.address)}</span></div>` : "";
}
async function checkUdyam() {
  const r = await api("/api/kyc/udyam", { session_id: S.sid, udyam_number: K.udyamVal }); K.udyam = r; paintUdyam(r);
}
function paintUdyam(r) { setField("ud", r.ok ? "ok" : "bad", r.ok ? "✓ " + r.name : r.message); }

function docTypes() { return K.hasGst ? ["gst_certificate", "udyam_certificate", "signatory_id", "address_proof"] : ["udyam_certificate", "signatory_id", "address_proof"]; }
function docsBlock() {
  const U = ui();
  const b = h("div", { class: "blk", id: "kDocs" });
  b.append(h("h3", { html: `<span class="n ${Object.keys(K.docs).length >= docTypes().length ? "ok" : ""}">2</span>${esc(U.docsT)}` }), h("p", { text: U.docsSub }));
  docTypes().forEach(dt => b.append(slotEl(dt)));
  return b;
}
function slotEl(dt) {
  const U = ui(), d = K.docs[dt];
  const state = d ? (d.low ? "warn" : "ok") : "";
  const el = h("div", { class: "slot " + state, id: "slot-" + dt });
  const thumb = K.thumbs[dt];
  el.append(thumb ? h("img", { src: thumb, alt: U.docNames[dt] }) : h("div", { class: "ico", "aria-hidden": "true", text: DOC_ICON[dt] }));
  const m = h("div", { class: "m" }, h("b", { text: U.docNames[dt] }), h("small", { text: d ? (d.low ? "⚠️ " + U.hard : "✓ " + U.read) : U.docHints[dt] }));
  el.append(m);
  if (d) el.append(h("button", { class: "x-btn", "aria-label": U.remove, text: "✕", onclick: async () => { const f = new FormData(); f.append("session_id", S.sid); f.append("doc_type", dt); await fetch("/api/kyc/remove", { method: "POST", body: f }); delete K.docs[dt]; delete K.thumbs[dt]; K.results = null; renderKyc(); } }));
  else {
    const cam = h("input", { type: "file", accept: "image/*", capture: "environment", class: "sr", id: "c-" + dt, onchange: e => e.target.files[0] && uploadDoc(dt, e.target.files[0]) });
    const fil = h("input", { type: "file", accept: "image/*,application/pdf", class: "sr", id: "f-" + dt, onchange: e => e.target.files[0] && uploadDoc(dt, e.target.files[0]) });
    el.append(h("div", { class: "ups" }, h("label", { class: "up", for: "c-" + dt }, "📷 " + U.takePhoto), h("label", { class: "up", for: "f-" + dt }, "📎 " + U.uploadFile)), cam, fil);
  }
  el.append(h("div", { class: "bar" }));
  return el;
}
function loadPdfJs() {
  if (window.pdfjsLib) return Promise.resolve(window.pdfjsLib);
  return new Promise((res, rej) => {
    const sc = document.createElement("script");
    sc.src = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js";
    sc.onload = async () => {
      try {                                    // load the worker through a blob so the cross-origin script is allowed
        const code = await (await fetch("https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js")).text();
        window.pdfjsLib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(new Blob([code], { type: "text/javascript" }));
        res(window.pdfjsLib);
      } catch (e) { rej(e); }
    };
    sc.onerror = rej; document.head.append(sc);
  });
}
async function pdfToImage(file) {              // first page of the PDF becomes a PNG, which the same checks can read
  const lib = await loadPdfJs();
  const pdf = await lib.getDocument({ data: await file.arrayBuffer() }).promise;
  const page = await pdf.getPage(1), vp = page.getViewport({ scale: 2 });
  const cv = document.createElement("canvas"); cv.width = vp.width; cv.height = vp.height;
  await page.render({ canvasContext: cv.getContext("2d"), viewport: vp }).promise;
  const blob = await new Promise(r => cv.toBlob(r, "image/png"));
  return new File([blob], file.name.replace(/\.pdf$/i, "") + ".png", { type: "image/png" });
}
async function uploadDoc(dt, file, sample) {
  if (file && (file.type === "application/pdf" || /\.pdf$/i.test(file.name))) {
    try { toast("📎 …"); file = await pdfToImage(file); } catch (e) { toast(ui().pdfFail); return; }
  }
  const el = $("#slot-" + dt); const bar = el && $(".bar", el);
  if (file) K.thumbs[dt] = URL.createObjectURL(file); else if (sample) K.thumbs[dt] = "/sample-docs/" + sample;
  if (bar) bar.style.width = "70%";
  const f = new FormData(); f.append("session_id", S.sid); f.append("doc_type", dt);
  if (sample) f.append("sample", sample); else f.append("file", file);
  const r = await (await fetch("/api/kyc/upload", { method: "POST", body: f })).json();
  if (bar) bar.style.width = "100%";
  await sleep(220);
  K.docs[dt] = { low: r.low_confidence, source: r.source }; K.results = null;
  const nb = $("#slot-" + dt); if (nb) nb.replaceWith(slotEl(dt));
  const hd = $("#kDocs h3 .n"); if (hd && Object.keys(K.docs).length >= docTypes().length) hd.classList.add("ok");
}
async function fillSample(id, btn) {
  btn.disabled = true;
  const det = SAMPLE_DETAIL[id]; if (!det) { toast("sample missing"); btn.disabled = false; return; }
  K.hasGst = true; K.docs = {}; K.thumbs = {}; K.results = null; K.gst = null; K.udyam = null;
  K.gstVal = det.typed_gstin; K.udyamVal = det.udyam_number;
  renderKyc();
  await sleep(250);
  await checkGst(); await sleep(200); await checkUdyam(); await sleep(250);
  for (const [dt, path] of Object.entries(det.docs)) { await uploadDoc(dt, null, path); await sleep(180); }
  await sleep(350); runVerify();
}
let SAMPLE_DETAIL = {};

async function runVerify() {
  if (K.busy) return; K.busy = true;
  const U = ui(), btn = $("#kCheck"); if (btn) { btn.disabled = true; btn.textContent = U.checking; }
  try {
    // make sure typed numbers were looked up even if the owner never left the field
    if (K.hasGst && K.gstVal && !K.gst) await checkGst();
    if (K.udyamVal && !K.udyam) await checkUdyam();
    const r = await api("/api/kyc/verify", { session_id: S.sid });
    K.results = r; S.trace = [...(r.trace || []), ...S.trace].slice(0, 14); renderHood();
    renderKyc();
    const res = $("#kRes"); if (res) sheetScroll(res, "start");
    // colour the slots
    r.checks.forEach(c => { if (c.doc && c.passed === false) { const s = $("#slot-" + c.doc); if (s) { s.classList.remove("ok", "warn"); s.classList.add("bad"); } } });
  } finally { K.busy = false; }
}

function sheetScroll(el, where) {
  const body = $("#kycBody"); const top = el.getBoundingClientRect().top - body.getBoundingClientRect().top + body.scrollTop;
  body.scrollTo({ top: where === "center" ? top - body.clientHeight / 3 : top - 8, behavior: "smooth" });
}

function paintResults() {
  const box = $("#kRes"); if (!box) return;
  const U = ui(), r = K.results; if (!r) return;
  const warn = r.checks.some(c => c.severity === "warn");
  const kind = r.overall === "pass" ? (warn ? "warn" : "pass") : r.overall;
  const B = { pass: [U.allGood, U.allGoodSub, "🎉"], fail: [U.failT, U.failSub, "🛠️"], review: [U.reviewT, U.reviewSub, "👀"], warn: [U.warnT, U.warnSub, "⚠️"] }[kind];
  const rows = r.checks.map((c, i) => {
    const st = c.review ? "rev" : c.passed === false ? (c.severity === "warn" ? "warn" : "bad") : "ok";
    const sym = { ok: "✓", bad: "✕", warn: "!", rev: "?" }[st];
    const fix = (c.passed === false && c.severity !== "warn") || c.review ? `<button class="btn ghost sm fix" data-fix="${esc(c.doc || c.field || "")}">${esc(U.fix)}</button>` : "";
    return `<div class="res" style="animation-delay:${i * 60}ms"><span class="s ${st}">${sym}</span><div><b>${esc(c.label)}</b><p>${esc(c.message)}</p></div>${fix}</div>`;
  }).join("");
  box.innerHTML = `<div class="results"><div class="banner ${kind}"><span class="big">${B[2]}</span><div><b>${esc(B[0])}</b><span>${esc(B[1])}</span></div></div>${rows}</div>`;
  box.querySelectorAll("[data-fix]").forEach(b => b.onclick = () => {
    const t = b.dataset.fix; const target = t === "gstin" ? $("#gstin") : t === "udyam" ? $("#udyam") : $("#slot-" + t);
    if (!target) return; sheetScroll(target, "center");
    const fl = target.closest(".inp") || target; fl.classList.add("bad"); setTimeout(() => fl.classList.remove("bad"), 1800);
    if (target.tagName === "INPUT") target.focus();
  });
}

async function placeOrder() {
  const btn = $("#kPlace"); btn.disabled = true; btn.textContent = ui().placing;
  try {
    const r = await api("/api/order", { session_id: S.sid });
    S.order = r.order; S.stage = "order"; renderStepper();
    S.trace = [...(r.trace || []), ...S.trace].slice(0, 14); renderHood();
    sheet.classList.remove("open"); K.open = false;
    await sleep(420);
    addBubble(r.message, "bot");
    document.querySelectorAll(".card.plan").forEach(e => e.classList.add("stale"));
    addCard(trackerCard(r.order));
    setChips([{ label: ui().whereBtn, hi: ui().whereBtn, text: S.lang === "hi" ? "मेरा ऑर्डर कहाँ है?" : "Where is my order?" }]);
  } catch (e) { btn.disabled = false; }
}

/* ------------------------------------------------------------------ side panels + demo */
function buildDemo(into) {
  const U = ui();
  const wrap = h("div", { class: "panel" }, h("h3", { text: U.tryCase }), h("p", { text: U.tryCaseSub }));
  S.scenarios.forEach(sc => wrap.append(h("button", { class: "scn", type: "button", onclick: () => { document.getElementById("menuSheet").classList.remove("open"); playScenario(sc); } },
    h("b", { text: sc.id }), h("div", {}, h("span", { text: sc.title }), h("small", { text: sc.expect })))));
  const tools = h("div", { class: "panel" },
    h("button", { class: "btn ghost sm", style: "width:100%", text: "↺ " + U.reset, onclick: () => { document.getElementById("menuSheet").classList.remove("open"); resetChat(); } }),
    h("p", {}, h("a", { class: "link", href: "/staff", target: "_blank", text: U.staff })),
    h("p", { class: "fine", style: "text-align:left", text: "📦 " + U.sampleNote + ": data/ (drop in the real case CSVs to replace)" }));
  into.append(wrap, tools);
}
function livePanelEl() {
  const U = ui(), p = S.preview, el = h("div", { class: "panel live" });
  el.append(h("h3", { text: U.liveT }));
  if (!p || !p.quote || (!p.quote.items.length && !p.quote.refused.length)) { el.append(h("div", { class: "empty", text: U.noPlanYet })); return el; }
  const q = p.quote, T = q.totals;
  el.append(h("span", { class: "est " + (p.final ? "final" : ""), text: p.final ? U.confirmed : U.estimate }), h("h3", { class: "pn", text: q.plan_name }));
  const big = h("div", { class: "lbig" }, inr(T.monthly), h("small", { text: " /" + U.month }));
  el.append(big);
  el.append(h("div", { class: "lsub", text: `${inr(T.setup)} ${U.setup} · ${U.months.replace("{n}", T.contract_months)}` + (T.expected_days > 0 ? " · " + U.live.replace("{n}", T.expected_days) : "") }));
  const prev = S.prevLive || {}, now2 = {};
  q.items.forEach(i => {
    now2[i.id] = i.qty;
    const cls = !(i.id in prev) && Object.keys(prev).length ? "new" : (i.id in prev && prev[i.id] !== i.qty ? "chg" : "");
    el.append(h("div", { class: "li " + cls }, h("span", { text: ICON[i.id] || "📦" }), h("span", { class: "n", text: i.name + (i.qty > 1 ? " ×" + i.qty : "") }), h("span", { class: "p", text: inr(i.monthly) })));
  });
  S.prevLive = now2;
  if (S.liveMonthly !== null && S.liveMonthly !== T.monthly) { const from = S.liveMonthly; big.firstChild.textContent = inr(from); countUp(big, from, T.monthly); }
  S.liveMonthly = T.monthly;
  if (!p.final && p.pending && p.pending.length) {
    el.append(h("div", { class: "assume", text: U.waitFor + ": " + p.pending.map(k => U["w_" + k]).join(" · ") + "." }));
  }
  if (!p.final && p.assumed && p.assumed.length) {
    const v = p.values || {}, map = { staff: U.staffW.replace("{n}", v.staff), sites: U.sitesW.replace("{n}", v.sites), city: U.tierW.replace("{n}", v.tier), gst: U.noGstW };
    el.append(h("div", { class: "assume", text: U.assumeLead + ": " + p.assumed.map(k => map[k]).join(" · ") + ". " + U.assumeFoot }));
  }
  return el;
}
function renderPill() {
  const U = ui(), p = S.preview, pill = $("#livePill");
  if (!p || !p.quote || !p.quote.items.length) { pill.hidden = true; return; }
  pill.hidden = false;
  pill.innerHTML = `<span>📋 ${esc(p.quote.plan_name)}${p.final ? "" : " · " + esc(U.estimate)}</span><span>${inr(p.quote.totals.monthly)}/${esc(U.month)} ▸</span>`;
  if ($("#liveSheet").classList.contains("open")) { const lb = $("#liveBody"); lb.innerHTML = ""; lb.append(livePanelEl()); }
}
$("#livePill").onclick = () => { $("#liveTitle").textContent = ui().liveT; const lb = $("#liveBody"); lb.innerHTML = ""; lb.append(livePanelEl()); $("#liveSheet").classList.add("open"); };
$("#liveClose").onclick = () => $("#liveSheet").classList.remove("open");

function renderHood() {
  const U = ui(), R = $("#sideR"); R.innerHTML = "";
  R.append(livePanelEl()); renderPill();
  const prof = Object.entries(S.profile || {}).filter(([k, v]) => v !== false && v !== null && k !== "spend_skipped");
  const hood = h("div", { class: "panel" }, h("h3", { text: U.hood }), h("p", { text: U.hoodSub }),
    h("span", { class: "llm-badge " + (S.health.llm ? "on" : ""), text: S.health.llm ? U.llmOn : U.llmOff }));
  if (!S.trace.length) hood.append(h("p", { text: U.noTrace }));
  S.trace.forEach(t => hood.append(h("div", { class: "trace-item" }, h("code", { text: t.tool }), h("div", { text: [t.args, t.result].filter(Boolean).join("  →  ") }))));
  R.append(hood);
  if (prof.length) R.append(h("div", { class: "panel" }, h("h3", { text: U.know }), h("div", { style: "display:flex;flex-wrap:wrap;gap:6px;margin-top:6px" }, prof.map(([k, v]) => h("span", { class: "pill", style: "margin:0", text: `${k.replace("_", " ")}: ${v}` })))));
}
function renderSides() { const L = $("#sideL"); L.innerHTML = ""; buildDemo(L); const M = $("#menuBody"); M.innerHTML = ""; buildDemo(M); renderHood(); }
$("#menuBtn").onclick = () => $("#menuSheet").classList.add("open");
$("#menuClose").onclick = () => $("#menuSheet").classList.remove("open");

/* ------------------------------------------------------------------ session lifecycle */
async function resetChat(opts = {}) {
  chat.innerHTML = ""; setChips([]); S.quote = null; S.order = null; S.stage = "chat"; S.trace = []; S.profile = {}; S.preview = null; S.prevLive = {}; S.liveMonthly = null;
  stopVoice();
  K = { open: false, consent: null, hasGst: true, gst: null, udyam: null, docs: {}, samples: [], results: null, typed: "", udyamVal: "", gstVal: "", thumbs: {}, busy: false, planNote: false };
  sheet.classList.remove("open");
  const res = await api("/api/session", { language: S.lang });
  S.sid = res.session_id; S.stage = res.stage; S.preview = res.preview || null;
  try { localStorage.setItem("ud_sid", S.sid); } catch (e) { }
  renderStepper(); renderHood();
  await showBot(res.messages, !!opts.fast);
}
async function playScenario(sc) {
  if (S.busy) return;
  await resetChat({ fast: true });
  for (const m of sc.messages) { await say(m, m); await sleep(500); }
}

(async function init() {
  applyLang("en", false);
  try { S.health = await api("/api/health", undefined, { get: true }); } catch (e) { }
  try { S.scenarios = await api("/api/scenarios", undefined, { get: true }); } catch (e) { }
  try { SAMPLE_DETAIL = Object.fromEntries((await api("/api/kyc/samples-detail", undefined, { get: true })).map(s => [s.id, s])); } catch (e) { }
  renderSides(); renderStepper();
  if (await restore()) return;
  await resetChat();
})();

async function restore() {
  let sid = null; try { sid = localStorage.getItem("ud_sid"); } catch (e) { }
  if (!sid) return false;
  try {
    const r = await fetch("/api/session/" + sid); if (!r.ok) return false;
    const d = await r.json();
    if (d.history.length < 2) return false;           // nothing worth restoring
    S.sid = sid; S.stage = d.stage; S.profile = d.profile || {}; S.preview = d.preview || null;
    if (d.lang !== S.lang) applyLang(d.lang, false);
    if (S.preview && S.preview.final) S.quote = S.preview.quote;
    d.history.forEach(m => addBubble(m.text, m.role === "user" ? "user" : "bot"));
    addNotice("✨ " + ui().back);
    renderStepper(); renderHood();
    await showBot(d.resume || [], true);
    return true;
  } catch (e) { return false; }
}


/* ------------------------------------------------------------------ voice chat */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const V = { on: false, rec: null, speaking: 0, restarts: 0, warned: false, gen: 0, audio: null, audioDone: null, chain: Promise.resolve(), cache: new Map(), neural: null, silenceT: null };
const micBtn = $("#micBtn"), vbar = $("#voiceBar"), msgIn = $("#msg");
micBtn.title = ui().micTip;

function vstate(mode) {
  vbar.hidden = !mode; vbar.classList.toggle("speaking", mode === "speak");
  $("#voiceTxt").textContent = mode === "speak" ? ui().speaking : ui().listenFree;
  micBtn.setAttribute("aria-pressed", V.on ? "true" : "false");
}
function cancelSpeech() {
  V.gen++; V.speaking = 0; V.chain = Promise.resolve();
  try { speechSynthesis.cancel(); } catch (e) { }
  if (V.audio) { try { V.audio.pause(); } catch (e) { } V.audio = null; }
  if (V.audioDone) { V.audioDone(); V.audioDone = null; }
}
function stopVoice() {
  V.on = false; V.restarts = 0; clearTimeout(V.silenceT);
  try { V.rec && V.rec.abort(); } catch (e) { }
  cancelSpeech(); msgIn.classList.remove("interim"); vstate(null);
}
function startVoice() {
  if (!SR) { toast(ui().voiceNo); return; }
  V.on = true; V.restarts = 0; listen();
}
micBtn.onclick = () => (V.on ? stopVoice() : startVoice());
$("#voiceStop").onclick = stopVoice;

/* Listening: stays open through pauses and silence. It sends only after you stop talking for ~1.7 s,
   and it never gives up on its own because you were quiet. */
function listen() {
  if (!V.on || !SR || S.busy || V.speaking) return;
  const rec = new SR(); V.rec = rec;
  rec.lang = (LANGS[S.speech] || LANGS.en)[0]; rec.interimResults = true; rec.continuous = true; rec.maxAlternatives = 1;
  let said = "";
  clearTimeout(V.silenceT);
  rec.onstart = () => vstate("listen");
  rec.onresult = e => {                      // live transcription: words appear as you speak
    let txt = "";
    for (let i = 0; i < e.results.length; i++) txt += e.results[i][0].transcript;
    said = txt; msgIn.value = txt; msgIn.classList.add("interim"); $("#voiceTxt").textContent = "“" + txt + "”";
    clearTimeout(V.silenceT); V.silenceT = setTimeout(() => { try { rec.stop(); } catch (e) { } }, 1700);
  };
  rec.onerror = e => {
    if (e.error === "not-allowed" || e.error === "service-not-allowed") { stopVoice(); toast(ui().micDenied); }
    else if (e.error === "network") { stopVoice(); toast(ui().voiceNet); }
  };
  rec.onend = () => {
    clearTimeout(V.silenceT); msgIn.classList.remove("interim");
    if (!V.on || V.rec !== rec) return;
    const t = said.trim();
    if (t) { msgIn.value = ""; V.restarts = 0; say(t, t, null, true); }
    else if (++V.restarts > 60) { stopVoice(); toast(ui().voiceNet); }   // about 10 quiet minutes
    else setTimeout(listen, 150);                                      // quiet: just keep listening
  };
  try { rec.start(); } catch (e) { }
}

/* Speaking: neural voice from the server (Hindi and English), one sentence at a time so it starts fast.
   Falls back to the best voice the browser has if the server voice is not reachable. */
function speechText(text) {
  return text.replace(/\*\*/g, "").replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, "").replace(/\s*\n+\s*/g, ". ").trim();
}
function sentences(t) {
  const parts = (t.match(/[^.!?।]+[.!?।]?/g) || [t]).map(x => x.trim()).filter(Boolean), out = [];
  parts.forEach(p => { if (out.length && out[out.length - 1].length < 28) out[out.length - 1] += " " + p; else out.push(p); });
  return out;
}
const hasHindi = t => /[\u0900-\u097F]/.test(t);
function fetchChunk(text, lang) {
  if (hasHindi(text)) lang = "hi";                   // Devanagari must use the Hindi voice
  const key = lang + "|" + text;
  if (!V.cache.has(key)) {
    V.cache.set(key, fetch("/api/tts", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, lang }) })
      .then(async r => { if (!r.ok) throw new Error(r.status); return URL.createObjectURL(await r.blob()); }));
    if (V.cache.size > 80) V.cache.delete(V.cache.keys().next().value);
  }
  return V.cache.get(key);
}
function playUrl(url, gen) {
  return new Promise(res => {
    if (gen !== V.gen) return res();
    const a = new Audio(url); V.audio = a; V.audioDone = res;
    a.onended = a.onerror = () => { V.audioDone = null; res(); };
    a.play().catch(() => { V.audioDone = null; res(); });
  });
}
function bestVoice(lang) {
  const vs = speechSynthesis.getVoices().filter(v => v.lang.toLowerCase().startsWith(lang.slice(0, 2)));
  const score = v => (/natural|neural|online/i.test(v.name) ? 4 : 0) + (v.lang === lang ? 2 : 0) + (/google|microsoft/i.test(v.name) ? 1 : 0);
  return vs.sort((x, y) => score(y) - score(x))[0];
}
function speakBrowser(text, gen) {
  return new Promise(res => {
    if (!("speechSynthesis" in window) || gen !== V.gen) return res();
    const hi = hasHindi(text) || S.speech === "hi";
    const u = new SpeechSynthesisUtterance(speechText(text).replace(/₹\s?([\d,]+)/g, "$1 " + (hi ? "रुपये" : "rupees")));
    u.lang = hasHindi(text) ? (S.speech === "mr" ? "mr-IN" : "hi-IN") : (LANGS[S.speech] || LANGS.en)[0];
    const v = bestVoice(u.lang);
    if (v) u.voice = v; else if (hi && !V.warned) { V.warned = true; toast(ui().noHiVoice); }
    u.onend = u.onerror = () => res();
    speechSynthesis.speak(u);
  });
}
async function speakNow(text, gen) {
  const lang = S.lang;
  if (V.neural !== false) {
    try {
      const urls = sentences(speechText(text)).map(c => fetchChunk(c, S.speech));    // all requested at once, played in order
      for (const u of urls) { const url = await u; if (gen !== V.gen) return; await playUrl(url, gen); }
      V.neural = true; return;
    } catch (e) { if (gen !== V.gen) return; V.neural = false; }
  }
  await speakBrowser(text, gen);
}
function speak(text) {
  if (!V.on || !text) return;
  const gen = V.gen; V.speaking++; vstate("speak");
  V.chain = V.chain.then(() => speakNow(text, gen)).catch(() => { }).then(() => {
    if (gen !== V.gen) return;
    V.speaking = Math.max(0, V.speaking - 1);
    if (!V.speaking && V.on && !S.busy) listen();
  });
}
function speakPlan(q) {
  if (!V.on || !q || !q.items.length) return;
  const T = q.totals;
  speak(ui().spokenPlan.replace("{plan}", q.plan_name).replace("{price}", T.monthly.toLocaleString("en-IN")).replace("{setup}", T.setup.toLocaleString("en-IN")).replace("{months}", T.contract_months));
}
if ("speechSynthesis" in window) speechSynthesis.onvoiceschanged = () => { };

/* ------------------------------------------------------------------ "what do you need?" picker */
function needsCard(tiles) {
  if (S.needsEl) S.needsEl.classList.add("stale");
  const el = h("div", { class: "card needs" }); S.needsEl = el; paintNeeds(el, tiles);
  el.addEventListener("click", e => {
    const b = e.target.closest("[data-need]"); if (!b) return;
    const id = b.dataset.id, t = el._tiles.flatMap(g => g.tiles).find(x => x.id === id); if (!t) return;
    if (!t.allowed) { toast(ui().lockedPre + t.reason); return; }
    const a = b.dataset.need;
    const qty = a === "toggle" ? (t.qty ? 0 : (id === "P16" && S.profile.employees ? S.profile.employees : 1)) : a === "inc" ? t.qty + 1 : Math.max(0, t.qty - 1);
    tapNeed({ action: "need", id, qty });
  });
  return el;
}
function paintNeeds(el, groups) {
  const U = ui(); el._tiles = groups;
  const GN = { net: U.gnet, phone: U.gphone, safe: U.gsafe, grow: U.ggrow, team: U.gteam };
  el.innerHTML = `<div class="card-h"><span class="tag">🛠️</span><h3>${esc(U.needsT)}</h3><p>${esc(U.needsSub)}</p></div>` + groups.map(g => `
    <div class="sec interactive"><h4>${esc(GN[g.id] || g.id)}</h4><div class="tiles">${g.tiles.map(t => `
      <div class="tile ${t.qty ? "on" : ""} ${t.allowed ? "" : "locked"}">
        <button class="tmain" data-need="toggle" data-id="${t.id}" aria-pressed="${t.qty ? "true" : "false"}" aria-label="${esc(t.name)}">
          <span class="ti">${t.allowed ? ICON[t.id] || "📦" : "🔒"}</span>
          <span class="tn">${esc(t.name)}</span>
          <span class="tp">+${inr(t.price)}${t.pending ? " ⏳" : ""}</span>
          <span class="tc">${t.qty ? "✓" : ""}</span>
        </button>
        ${t.qty && t.editable ? `<div class="tq"><button data-need="dec" data-id="${t.id}" aria-label="Less">−</button><span>${t.qty}</span><button data-need="inc" data-id="${t.id}" aria-label="More">+</button></div>` : ""}
      </div>`).join("")}</div></div>`).join("");
}
function syncNeeds(tiles) {
  const el = S.needsEl; if (!el || !document.contains(el)) return;
  if (tiles) paintNeeds(el, tiles);
  else if (!el.classList.contains("done")) { el.classList.add("done"); el.innerHTML = `<div class="card-h"><span class="tag">🛠️</span><p>${esc(ui().picked)}</p></div>`; }
}
async function tapNeed(payload) {                 // instant: no typing delay, price updates at once
  try {
    const res = await api("/api/chat", { session_id: S.sid, message: "", label: "", payload });
    afterReply(res); queueBot(res.messages, true);
  } catch (e) { }
}


/* The conversation follows the language the owner is using. The advisor detects it each turn (even from a garbled
   transcript) and reports it as speech_lang; the mic, the voice and the screen follow, with no toggle needed.
   The language picker in the voice bar is a manual override ("Auto" = follow). */
function followReplyLanguage(res) {
  if (!S.speechAuto) return;
  const sp = res.speech_lang && LANGS[res.speech_lang] ? res.speech_lang : null;
  if (!sp || sp === S.speech) return;
  setSpeech(sp);
}
function setSpeech(code) {
  S.speech = code;
  const sel = $("#speechLang"); if (sel) sel.value = S.speechAuto ? "auto" : code;
  const ui2 = code === "hi" || code === "mr" ? "hi" : "en";
  if (ui2 !== S.lang) applyLang(ui2, false);
  fetch("/api/lang", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ session_id: S.sid, language: ui2, speech_lang: code }) }).catch(() => { });
  if (V.on && V.rec) { try { V.rec.abort(); } catch (e) { } setTimeout(listen, 200); }     // restart the mic in the new language
}
(function initSpeechPicker() {
  const sel = $("#speechLang"); if (!sel) return;
  sel.innerHTML = `<option value="auto">Auto</option>` + Object.entries(LANGS).map(([k, v]) => `<option value="${k}">${v[1]}</option>`).join("");
  sel.value = "auto";
  sel.onchange = () => {
    if (sel.value === "auto") { S.speechAuto = true; return; }
    S.speechAuto = false; setSpeech(sel.value);
  };
})();
