# pyrefly: ignore [missing-import]
import streamlit as st


# ─────────────────────────────────────────────────────────────
# Full landing page HTML/CSS
# Rendered directly into Streamlit DOM for true full screen
# Buttons use native a href with ?lp_action=login which forces
# Streamlit backend to catch the action and change state.
# ─────────────────────────────────────────────────────────────

_LANDING_HTML = """<style>
/* ── Smooth Scrolling ── */
html {
  scroll-behavior: smooth;
}

/* ── Keyframes ── */
@keyframes meshShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes blob1{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(40px,-30px) scale(1.08)}66%{transform:translate(-20px,20px) scale(.95)}}
@keyframes blob2{0%,100%{transform:translate(0,0) scale(1)}40%{transform:translate(-50px,30px) scale(1.1)}70%{transform:translate(30px,-20px) scale(.9)}}
@keyframes blob3{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(20px,40px) scale(1.05)}}
@keyframes particleDrift{0%{transform:translateY(110vh) rotate(0deg);opacity:0}10%{opacity:1}90%{opacity:.6}100%{transform:translateY(-60px) rotate(720deg);opacity:0}}
@keyframes glowPulse{0%,100%{opacity:.4;transform:scale(1)}50%{opacity:.85;transform:scale(1.15)}}
@keyframes gridFade{0%,100%{opacity:.04}50%{opacity:.09}}
@keyframes dnaFloat{0%,100%{transform:translateY(0) rotate(0deg);opacity:.12}50%{transform:translateY(-22px) rotate(180deg);opacity:.22}}
@keyframes scanline{0%{top:-2px}100%{top:100%}}
@keyframes fadeUp{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:translateY(0)}}
@keyframes floatCard{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes barGrow{from{width:0}to{width:var(--w,70%)}}
@keyframes gradShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

/* ── Root & Background ── */
[data-testid="stAppViewContainer"] {
  background: linear-gradient(-45deg,#050816 0%,#0b1220 25%,#07111f 50%,#050d1a 75%,#050816 100%) !important;
  background-size: 400% 400% !important;
  animation: meshShift 18s ease infinite !important;
  color: #f8fafc;
  overflow-x: hidden;
}

[data-testid="stSidebar"] { display: none !important; }

.blob{position:fixed;border-radius:50%;filter:blur(90px);pointer-events:none;z-index:0;}
.blob-1{width:620px;height:620px;top:-160px;left:-110px;background:radial-gradient(circle,rgba(37,99,235,.3) 0%,transparent 70%);animation:blob1 14s ease-in-out infinite;}
.blob-2{width:500px;height:500px;bottom:-80px;right:-80px;background:radial-gradient(circle,rgba(6,182,212,.24) 0%,transparent 70%);animation:blob2 18s ease-in-out infinite;}
.blob-3{width:400px;height:400px;top:50%;left:50%;transform:translate(-50%,-50%);background:radial-gradient(circle,rgba(16,185,129,.09) 0%,transparent 70%);animation:blob3 22s ease-in-out infinite;}

.grid{position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:60px 60px;animation:gridFade 8s ease-in-out infinite;z-index:0;pointer-events:none;}

.glow{position:fixed;border-radius:50%;pointer-events:none;z-index:0;}
.glow-1{width:320px;height:320px;top:20%;left:10%;background:radial-gradient(circle,rgba(37,99,235,.16) 0%,transparent 70%);animation:glowPulse 6s ease-in-out infinite;}
.glow-2{width:260px;height:260px;bottom:25%;right:12%;background:radial-gradient(circle,rgba(6,182,212,.14) 0%,transparent 70%);animation:glowPulse 8s ease-in-out infinite 2s;}

.particles{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.p{position:absolute;bottom:-10px;width:3px;height:3px;border-radius:50%;animation:particleDrift var(--dur,12s) linear infinite;animation-delay:var(--delay,0s);left:var(--x,50%);background:var(--col,rgba(37,99,235,.7));}

.dna{position:fixed;font-size:1.4rem;opacity:.12;pointer-events:none;z-index:0;animation:dnaFloat var(--dur,10s) ease-in-out infinite;top:var(--top,30%);left:var(--left,80%);animation-delay:var(--delay,0s);}

.scanline{position:fixed;left:0;width:100%;height:2px;background:linear-gradient(90deg,transparent,rgba(37,99,235,.12),transparent);animation:scanline 9s linear infinite;z-index:0;pointer-events:none;}

/* ── Layout ── */
/* 100% max-width makes it fully responsive and uses the full screen! */
.wrap{position:relative;z-index:5;max-width:100%;margin:0 auto;padding:0 5%;}
.section{padding:3rem 0 5rem;}

/* ── Navbar ── */
nav{position:sticky;top:0;display:flex;align-items:center;justify-content:space-between;padding:.85rem 5%;background:rgba(5,8,22,.8);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.06);z-index:100;}
.logo{display:flex;align-items:center;gap:.6rem;font-size:1.15rem;font-weight:800;color:#fff;letter-spacing:-.03em;}
.logo-dot{width:10px;height:10px;background:#06B6D4;border-radius:50%;box-shadow:0 0 12px #06B6D4,0 0 24px rgba(6,182,212,.4);animation:glowPulse 3s ease-in-out infinite;flex-shrink:0;}
.nav-links{display:flex;align-items:center;gap:2rem;list-style:none;}
.nav-links a{color:rgba(255,255,255,.5);text-decoration:none;font-size:.875rem;font-weight:500;transition:color .2s;cursor:pointer;}
.nav-links a:hover{color:#fff;}
.nav-badge{background:rgba(37,99,235,.1);border:1px solid rgba(37,99,235,.22);color:#93C5FD;font-size:.68rem;font-weight:700;padding:.22rem .7rem;border-radius:9999px;letter-spacing:.05em;text-transform:uppercase;animation:glowPulse 3s ease-in-out infinite;}

/* ── Hero ── */
.hero{text-align:center;padding:6rem 2rem 3rem;max-width:860px;margin:0 auto;display:flex;flex-direction:column;align-items:center;}
.badge{display:inline-flex;align-items:center;gap:.55rem;background:rgba(37,99,235,.08);border:1px solid rgba(37,99,235,.2);color:#93C5FD;font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:.35rem 1rem;border-radius:9999px;margin-bottom:2rem;animation:fadeUp .6s ease-out both;}
.badge-dot{width:7px;height:7px;background:#10B981;border-radius:50%;box-shadow:0 0 8px #10B981;animation:glowPulse 2s ease-in-out infinite;flex-shrink:0;}
.hero-title{font-size:clamp(2.8rem,7vw,5.2rem);font-weight:900;line-height:1.06;margin:0 0 1.5rem;letter-spacing:-.04em;animation:fadeUp .7s ease-out .1s both;text-align:center;width:100%;}
.title-white{color:#fff;display:block;}
.title-grad{background:linear-gradient(135deg,#3B82F6 0%,#06B6D4 50%,#10B981 100%);background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-size:200% 200%;animation:gradShift 6s ease infinite;display:inline-block;}
.hero-sub{font-size:1.15rem;color:rgba(255,255,255,.46);line-height:1.72;max-width:640px;margin:0 auto 2.5rem;animation:fadeUp .8s ease-out .2s both;text-align:center;}

/* ── Premium CTA Buttons ── */
.btn-row{display:flex;justify-content:center;align-items:center;gap:1.2rem;margin-top:2.5rem;animation:fadeUp .9s ease-out .3s both;flex-wrap:wrap;}
.btn-primary{display:inline-flex;align-items:center;gap:0.6rem;background:linear-gradient(135deg,#2563EB,#1D4ED8);color:#fff;border:none;border-radius:12px;font-weight:700;font-size:0.98rem;padding:0.9rem 2.2rem;text-decoration:none;box-shadow:0 4px 24px rgba(37,99,235,0.35);transition:all 0.25s ease;cursor:pointer;user-select:none;}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(37,99,235,0.55);color:#fff;}
.btn-secondary{display:inline-flex;align-items:center;gap:0.6rem;background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.85);border:1px solid rgba(255,255,255,0.1);border-radius:12px;font-weight:600;font-size:0.98rem;padding:0.9rem 2.2rem;text-decoration:none;transition:all 0.25s ease;cursor:pointer;user-select:none;}
.btn-secondary:hover{background:rgba(255,255,255,0.12);color:#fff;transform:translateY(-2px);}
.btn-admin{display:inline-flex;align-items:center;gap:0.6rem;background:rgba(245,158,11,0.08);color:#F59E0B;border:1px solid rgba(245,158,11,0.2);border-radius:12px;font-weight:700;font-size:0.82rem;padding:0.7rem 1.6rem;text-decoration:none;transition:all 0.25s ease;cursor:pointer;user-select:none;}
.btn-admin:hover{background:rgba(245,158,11,0.15);transform:translateY(-2px);box-shadow:0 6px 20px rgba(245,158,11,0.2);color:#F59E0B;}

/* ── Mockup Cards ── */
.mockup-wrap{display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;padding:1rem 5% 3.5rem;animation:fadeUp 1s ease-out .5s both;}
.mockup-card{background:rgba(11,18,32,.9);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:1.5rem;backdrop-filter:blur(24px);box-shadow:0 20px 60px rgba(0,0,0,.5),0 0 0 1px rgba(37,99,235,.07);flex-shrink:0;}
.mockup-card:nth-child(1){animation:floatCard 6s ease-in-out infinite;}
.mockup-card:nth-child(2){animation:floatCard 6s ease-in-out infinite 1s;}
.mockup-card:nth-child(3){animation:floatCard 6s ease-in-out infinite 2s;}
.mock-hdr{display:flex;align-items:center;gap:.6rem;margin-bottom:1rem;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:rgba(255,255,255,.3);}
.mdot{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
.mdot-g{background:#10B981;box-shadow:0 0 8px #10B981;}
.mdot-b{background:#2563EB;box-shadow:0 0 8px #2563EB;}
.mdot-c{background:#06B6D4;box-shadow:0 0 8px #06B6D4;}
.mock-dis{font-size:1.3rem;font-weight:800;color:#fff;margin-bottom:.25rem;}
.mock-conf{font-size:.78rem;color:#10B981;font-weight:700;margin-bottom:.9rem;}
.mock-lbl{font-size:.68rem;color:rgba(255,255,255,.28);margin-bottom:.12rem;}
.bar-t{width:100%;height:5px;background:rgba(255,255,255,.06);border-radius:9999px;overflow:hidden;margin-bottom:.45rem;}
.bar-f{height:100%;border-radius:9999px;background:linear-gradient(90deg,#2563EB,#06B6D4);animation:barGrow 1.8s ease-out both;width:var(--w,70%);}
.chat-row{display:flex;align-items:flex-start;gap:.55rem;margin-bottom:.65rem;}
.av{width:26px;height:26px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:.62rem;font-weight:800;}
.av-ai{background:#06B6D4;color:#050816;}
.av-u{background:#2563EB;color:#fff;}
.bubble{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:.42rem .65rem;font-size:.72rem;color:rgba(255,255,255,.62);line-height:1.5;max-width:195px;}
.bubble-u{background:rgba(37,99,235,.12);border-color:rgba(37,99,235,.2);}

/* ── Stats ── */
.stats{display:flex;justify-content:center;flex-wrap:wrap;background:rgba(11,18,32,.6);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.06);border-radius:20px;margin:0 5% 5rem;padding:2.5rem 1rem;animation:fadeUp 1s ease-out .6s both;}
.stat{flex:1;min-width:130px;text-align:center;padding:1rem 1.2rem;position:relative;}
.stat+.stat::before{content:'';position:absolute;left:0;top:20%;height:60%;width:1px;background:rgba(255,255,255,.07);}
.stat-val{font-size:2.5rem;font-weight:900;letter-spacing:-.04em;line-height:1;margin-bottom:.45rem;background:linear-gradient(135deg,#fff 0%,rgba(255,255,255,.55) 100%);background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stat-val-accent{background:linear-gradient(135deg,#10B981,#06B6D4)!important;background-clip:text!important;-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;}
.stat-lbl{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.3);}

/* ── Section Headers ── */
.sec-eyebrow{text-align:center;font-size:.72rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#06B6D4;margin-bottom:.75rem;}
.sec-title{text-align:center;font-size:clamp(1.7rem,4vw,2.6rem);font-weight:900;letter-spacing:-.04em;color:#fff;margin:0 0 .9rem;}
.sec-sub{text-align:center;font-size:.95rem;color:rgba(255,255,255,.36);max-width:560px;margin:0 auto 3.5rem;line-height:1.7;}

/* ── Feature Cards ── */
.grid-feat{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.2rem;}
.feat-card{background:rgba(11,18,32,.75);border:1px solid rgba(255,255,255,.06);border-radius:20px;padding:2rem;position:relative;overflow:hidden;transition:transform .3s cubic-bezier(.4,0,.2,1),border-color .3s,box-shadow .3s;backdrop-filter:blur(12px);}
.feat-card::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at top left,var(--glow,rgba(37,99,235,.06)),transparent 60%);pointer-events:none;}
.feat-card:hover{transform:translateY(-6px);border-color:rgba(37,99,235,.25);box-shadow:0 20px 50px rgba(0,0,0,.35),0 0 30px rgba(37,99,235,.08);}
.feat-icon{width:50px;height:50px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:1.4rem;margin-bottom:1.2rem;background:var(--ibg,rgba(37,99,235,.1));border:1px solid var(--ib,rgba(37,99,235,.2));}
.feat-title{font-size:1.02rem;font-weight:700;color:#fff;margin:0 0 .5rem;}
.feat-desc{font-size:.84rem;color:rgba(255,255,255,.36);line-height:1.65;margin:0;}
.feat-pill{display:inline-block;margin-top:.9rem;font-size:.68rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:.18rem .6rem;border-radius:9999px;background:var(--pb,rgba(37,99,235,.1));color:var(--pc,#60A5FA);border:1px solid var(--pbr,rgba(37,99,235,.2));}

/* ── Steps ── */
.steps{display:flex;gap:0;flex-wrap:wrap;margin-top:1rem;}
.step{flex:1;min-width:170px;text-align:center;padding:2rem 1.5rem;position:relative;}
.step+.step::before{content:'→';position:absolute;left:-.5rem;top:2.2rem;color:rgba(255,255,255,.14);font-size:1.1rem;}
.step-num{width:46px;height:46px;border-radius:50%;background:rgba(37,99,235,.1);border:1px solid rgba(37,99,235,.25);color:#60A5FA;font-size:1.05rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin:0 auto .9rem;}
.step-title{font-size:.96rem;font-weight:700;color:#fff;margin:0 0 .35rem;}
.step-desc{font-size:.8rem;color:rgba(255,255,255,.32);line-height:1.6;}

/* ── CTA Banner ── */
.cta-banner{margin:0 0 3rem;background:linear-gradient(135deg,rgba(37,99,235,.1),rgba(6,182,212,.07));border:1px solid rgba(37,99,235,.16);border-radius:24px;padding:4rem 2rem;text-align:center;position:relative;overflow:hidden;}
.cta-banner::before{content:'';position:absolute;top:-50%;left:50%;transform:translateX(-50%);width:380px;height:180px;background:radial-gradient(ellipse,rgba(37,99,235,.16),transparent 70%);pointer-events:none;}
.cta-title{font-size:clamp(1.5rem,4vw,2.2rem);font-weight:900;color:#fff;margin:0 0 .7rem;letter-spacing:-.04em;}
.cta-sub{font-size:.95rem;color:rgba(255,255,255,.4);max-width:480px;margin:0 auto 2.5rem;line-height:1.65;}

/* ── Footer ── */
footer{border-top:1px solid rgba(255,255,255,.05);padding:2.5rem 5% 3rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;}
.ft-brand{display:flex;align-items:center;gap:.5rem;font-size:.86rem;font-weight:700;color:rgba(255,255,255,.42);}
.ft-links{display:flex;gap:1.4rem;flex-wrap:wrap;}
.ft-link{font-size:.78rem;color:rgba(255,255,255,.26);text-decoration:none;transition:color .2s;cursor:pointer;}
.ft-link:hover{color:rgba(255,255,255,.6);}
.ft-copy{font-size:.73rem;color:rgba(255,255,255,.16);}

@media(max-width:768px){nav{padding:.7rem 1.2rem;}.nav-links{display:none;}.hero{padding:4rem 1.2rem 2.5rem;}.stats{margin:0 1rem 3rem;}.cta-banner{padding:3rem 1.2rem;}.step+.step::before{display:none;}footer{flex-direction:column;align-items:center;text-align:center;}.btn-row{flex-direction:column;gap:0.8rem;width:100%;max-width:300px;margin:2rem auto 0;}}
</style>

<!-- background layers -->
<div class="blob blob-1"></div>
<div class="blob blob-2"></div>
<div class="blob blob-3"></div>
<div class="grid"></div>
<div class="glow glow-1"></div>
<div class="glow glow-2"></div>
<div class="particles">
<div class="p" style="--x:8%;  --dur:14s;--delay:0s; --col:rgba(37,99,235,.8);"></div>
<div class="p" style="--x:18%; --dur:18s;--delay:2s; --col:rgba(6,182,212,.7);"></div>
<div class="p" style="--x:30%; --dur:12s;--delay:4s; --col:rgba(37,99,235,.6);"></div>
<div class="p" style="--x:45%; --dur:20s;--delay:1s; --col:rgba(16,185,129,.7);"></div>
<div class="p" style="--x:55%; --dur:16s;--delay:6s; --col:rgba(37,99,235,.9);"></div>
<div class="p" style="--x:70%; --dur:11s;--delay:3s; --col:rgba(6,182,212,.8);"></div>
<div class="p" style="--x:80%; --dur:22s;--delay:5s; --col:rgba(16,185,129,.6);"></div>
<div class="p" style="--x:92%; --dur:15s;--delay:8s; --col:rgba(37,99,235,.7);"></div>
<div class="p" style="--x:25%; --dur:19s;--delay:10s;--col:rgba(6,182,212,.5);"></div>
<div class="p" style="--x:65%; --dur:13s;--delay:7s; --col:rgba(37,99,235,.7);"></div>
</div>
<div class="dna" style="--top:14%;--left:4%;  --dur:12s;--delay:0s;">🧬</div>
<div class="dna" style="--top:60%;--left:91%;--dur:14s;--delay:3s;">🫀</div>
<div class="dna" style="--top:80%;--left:7%;  --dur:10s;--delay:5s;">🧬</div>
<div class="dna" style="--top:35%;--left:87%;--dur:16s;--delay:2s;">⚕️</div>
<div class="scanline"></div>

<!-- NAVBAR -->
<nav>
<div class="logo"><div class="logo-dot"></div>MediSense AI</div>
<ul class="nav-links">
<li><a href="#features">Features</a></li>
<li><a href="#workflow">Workflow</a></li>
<li><a href="#stats">Accuracy</a></li>
<li><a href="#footer">About</a></li>
</ul>
<div class="nav-badge">🩺 HEALTHAI V3 LIVE</div>
</nav>

<!-- HERO -->
<div class="hero">
<div class="badge"><span class="badge-dot"></span>AI-Powered Clinical Intelligence &nbsp;·&nbsp; 86.7% Accuracy</div>
<h1 class="hero-title">
<span class="title-white">Diagnose with</span><br>
<span class="title-grad">Machine Intelligence</span>
</h1>
<p class="hero-sub">The most advanced open-source medical AI platform. Combines Qwen&nbsp;2.5:3B clinical reasoning with 3 trained ML models across 754 diseases and 377 symptoms.</p>
<div class="btn-row">
<a class="btn-primary" href="?lp_action=register" target="_self">🚀 Get Started — Free</a>
<a class="btn-secondary" href="?lp_action=login" target="_self">👤 Patient Login →</a>
<a class="btn-admin" href="?lp_action=admin_login" target="_self">🔐 Admin Portal</a>
</div>
</div>

<!-- FLOATING MOCKUP CARDS -->
<div class="mockup-wrap">
<div class="mockup-card" style="width:230px;">
<div class="mock-hdr"><div class="mdot mdot-g"></div>AI Diagnosis</div>
<div class="mock-dis">Pneumonia</div>
<div class="mock-conf">✓ 91.4% Confidence</div>
<div class="mock-lbl">Logistic Regression</div>
<div class="bar-t"><div class="bar-f" style="--w:91%"></div></div>
<div class="mock-lbl">Decision Tree</div>
<div class="bar-t"><div class="bar-f" style="--w:78%"></div></div>
<div class="mock-lbl">KNN</div>
<div class="bar-t"><div class="bar-f" style="--w:85%"></div></div>
</div>
<div class="mockup-card" style="width:255px;">
<div class="mock-hdr"><div class="mdot mdot-b"></div>NLU Consultation</div>
<div class="chat-row"><div class="av av-u">U</div><div class="bubble bubble-u">I've had a fever and chest pain for 2 days...</div></div>
<div class="chat-row"><div class="av av-ai">AI</div><div class="bubble">I understand. Is the pain sharp or dull? Any difficulty breathing?</div></div>
<div class="chat-row"><div class="av av-u">U</div><div class="bubble bubble-u">Sharp, and yes — it's hard to breathe deeply.</div></div>
</div>
<div class="mockup-card" style="width:195px;">
<div class="mock-hdr"><div class="mdot mdot-c"></div>Session Analytics</div>
<div style="display:flex;flex-direction:column;gap:.9rem;margin-top:.4rem;">
<div><div style="font-size:.68rem;color:rgba(255,255,255,.28);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.18rem;">Symptoms Logged</div><div style="font-size:1.55rem;font-weight:800;color:#fff;">12</div></div>
<div><div style="font-size:.68rem;color:rgba(255,255,255,.28);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.18rem;">Predictions Run</div><div style="font-size:1.55rem;font-weight:800;color:#06B6D4;">3</div></div>
<div><div style="font-size:.68rem;color:rgba(255,255,255,.28);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.18rem;">Risk Level</div><div style="font-size:.95rem;font-weight:700;color:#F59E0B;">⚠ Moderate</div></div>
</div>
</div>
</div>

<!-- STATS -->
<div class="stats" id="stats">
<div class="stat"><div class="stat-val">247K+</div><div class="stat-lbl">Training Records</div></div>
<div class="stat"><div class="stat-val">754</div><div class="stat-lbl">Diseases Mapped</div></div>
<div class="stat"><div class="stat-val">377</div><div class="stat-lbl">Clinical Symptoms</div></div>
<div class="stat"><div class="stat-val stat-val-accent">86.7%</div><div class="stat-lbl">Baseline Accuracy</div></div>
<div class="stat"><div class="stat-val">3</div><div class="stat-lbl">ML Algorithms</div></div>
</div>

<!-- FEATURES -->
<div class="wrap section" id="features">
<div class="sec-eyebrow">Why MediSense AI</div>
<h2 class="sec-title">A complete clinical AI workflow</h2>
<p class="sec-sub">From natural language symptom capture to explainable AI reports — every step is powered by production-grade machine learning.</p>
<div class="grid-feat">

<div class="feat-card" style="--glow:rgba(37,99,235,.07);--ibg:rgba(37,99,235,.12);--ib:rgba(37,99,235,.2);">
<div class="feat-icon">💬</div>
<div class="feat-title">Natural Language Intake</div>
<p class="feat-desc">Powered by Qwen 2.5:3B via Ollama. Describe how you feel in plain English — the AI extracts and maps clinical symptoms through intelligent follow-ups.</p>
<div class="feat-pill" style="--pb:rgba(37,99,235,.1);--pc:#60A5FA;--pbr:rgba(37,99,235,.2);">LLM Powered</div>
</div>

<div class="feat-card" style="--glow:rgba(6,182,212,.07);--ibg:rgba(6,182,212,.12);--ib:rgba(6,182,212,.2);">
<div class="feat-icon">🧠</div>
<div class="feat-title">3-Model Ensemble</div>
<p class="feat-desc">Logistic Regression, Decision Tree, and KNN trained on 247K+ patient records. Switch models and compare predictions in real-time.</p>
<div class="feat-pill" style="--pb:rgba(6,182,212,.1);--pc:#06B6D4;--pbr:rgba(6,182,212,.2);">Scikit-Learn</div>
</div>

<div class="feat-card" style="--glow:rgba(16,185,129,.07);--ibg:rgba(16,185,129,.12);--ib:rgba(16,185,129,.2);">
<div class="feat-icon">📄</div>
<div class="feat-title">Explainable AI Reports</div>
<p class="feat-desc">Hospital-grade diagnostic summaries explaining exactly why the model predicted each condition, with specialist referrals and care plans.</p>
<div class="feat-pill" style="--pb:rgba(16,185,129,.1);--pc:#10B981;--pbr:rgba(16,185,129,.2);">XAI Ready</div>
</div>

<div class="feat-card" style="--glow:rgba(245,158,11,.07);--ibg:rgba(245,158,11,.12);--ib:rgba(245,158,11,.2);">
<div class="feat-icon">📊</div>
<div class="feat-title">Real-Time Analytics</div>
<p class="feat-desc">Track predictions, symptom distributions, and model performance across every session with live charts and telemetry dashboards.</p>
<div class="feat-pill" style="--pb:rgba(245,158,11,.1);--pc:#F59E0B;--pbr:rgba(245,158,11,.2);">Live Data</div>
</div>

<div class="feat-card" style="--glow:rgba(168,85,247,.07);--ibg:rgba(168,85,247,.12);--ib:rgba(168,85,247,.2);">
<div class="feat-icon">🔐</div>
<div class="feat-title">Secure Authentication</div>
<p class="feat-desc">Local SQLite database with password hashing. Your clinical data never leaves your machine — fully private by design.</p>
<div class="feat-pill" style="--pb:rgba(168,85,247,.1);--pc:#A855F7;--pbr:rgba(168,85,247,.2);">Private First</div>
</div>

<div class="feat-card" style="--glow:rgba(239,68,68,.07);--ibg:rgba(239,68,68,.12);--ib:rgba(239,68,68,.2);">
<div class="feat-icon">⚡</div>
<div class="feat-title">Emergency Detection</div>
<p class="feat-desc">Rule-based emergency classifier runs on every message. Critical symptoms trigger immediate escalation alerts before any prediction is made.</p>
<div class="feat-pill" style="--pb:rgba(239,68,68,.1);--pc:#EF4444;--pbr:rgba(239,68,68,.2);">Safety Layer</div>
</div>

</div>
</div>

<!-- HOW IT WORKS -->
<div class="wrap" style="padding-bottom:5rem;" id="workflow">
<div class="sec-eyebrow">The Workflow</div>
<h2 class="sec-title">From conversation to diagnosis</h2>
<p class="sec-sub">Four intelligent steps from first symptom to printable report.</p>
<div class="steps">
<div class="step"><div class="step-num">1</div><div class="step-title">Describe Symptoms</div><p class="step-desc">Chat naturally with the AI. No forms. No checkboxes.</p></div>
<div class="step"><div class="step-num">2</div><div class="step-title">AI Extraction</div><p class="step-desc">Qwen 2.5:3B maps your words to 377 clinical variables.</p></div>
<div class="step"><div class="step-num">3</div><div class="step-title">ML Prediction</div><p class="step-desc">3 trained models predict across 754 diseases with confidence scores.</p></div>
<div class="step"><div class="step-num">4</div><div class="step-title">XAI Report</div><p class="step-desc">Download a hospital-grade diagnostic summary with specialist referrals.</p></div>
</div>
</div>

<!-- CTA BANNER -->
<div class="wrap" style="padding-bottom:2rem;">
<div class="cta-banner">
<h2 class="cta-title">Ready to start your AI consultation?</h2>
<p class="cta-sub">Free, open-source, and 100% private. Your data stays on your machine.</p>
<div class="btn-row">
<a class="btn-primary" href="?lp_action=register" target="_self">✨ Create Free Account</a>
<a class="btn-secondary" href="?lp_action=login" target="_self">Sign In</a>
</div>
</div>
</div>

<!-- FOOTER -->
<footer id="footer">
<div class="ft-brand"><div style="width:8px;height:8px;border-radius:50%;background:#06B6D4;box-shadow:0 0 8px #06B6D4;"></div>MediSense AI</div>
<div class="ft-links">
<a class="ft-link" href="#" title="MediSense AI operates under strict local-first standards. All data processing, SQLite interactions, and clinical NLP pipelines execute natively on your machine to ensure complete data sovereignty and HIPAA-aligned isolation.">Privacy Policy</a>
<a class="ft-link" href="#" title="MediSense AI is a diagnostic simulation assistant designed to assist clinical workflows. It is intended for educational, screening, and research scenarios. For critical medical concerns, always consult a medical professional.">Terms of Use</a>
<a class="ft-link" href="#" title="The source repository for HealthAI v3 is protected under MediSense internal permissions. Please log in to your workspace and check the developer center to link your clinical license key.">GitHub</a>
<a class="ft-link" href="#" title="Comprehensive clinical API documentation, Scikit-Learn training pipelines, and LLM orchestration schemas can be viewed in the Clinical Workspace developer tab after secure authentication.">Documentation</a>
</div>
<div class="ft-copy">© 2026 MediSense AI · v3.0.0 · Streamlit + Scikit-Learn + Ollama</div>
</footer>
"""


def render_landing() -> None:
    """Render the premium landing page directly via st.markdown for full width and correct navigation."""

    # Aggressively clear Streamlit's default container padding/margins
    st.markdown("""
<style>
/* Hide header, deploy button, menu and footer elements */
header[data-testid="stHeader"], 
.stDeployButton, 
[data-testid="stToolbar"], 
#MainMenu, 
footer {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    min-height: 0px !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Zero out spacing and force 100% width for full-screen edge-to-edge visual integration */
[data-testid="stAppViewContainer"] > .main .block-container,
[data-testid="stMainBlockContainer"],
.main .block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlock"] > [data-testid="element-container"] {
    padding: 0 !important;
    margin: 0 !important;
}

/* Zero out top spacing for the main block view */
.main, .main .block-container, [data-testid="stAppViewContainer"] {
    
    margin-top: 0 !important;
    top: 0 !important;
}
</style>
""", unsafe_allow_html=True)

    # Render full landing page HTML directly to the Streamlit DOM
    st.markdown(_LANDING_HTML, unsafe_allow_html=True)
