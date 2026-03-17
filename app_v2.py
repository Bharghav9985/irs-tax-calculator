"""
app_v2.py - IRS Tax Refund Calculator (STANDALONE - no templates/static folders needed)
Run: python app_v2.py
Requires: pip install flask
Also needs fetch_irs_data.py in the same folder (auto-runs on first start).
"""

import json, os, math
from pathlib import Path
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "data" / "tax_data.json"

def load_tax_data():
    if not DATA_FILE.exists():
        print("data/tax_data.json not found - generating from IRS data...")
        import subprocess, sys
        subprocess.run([sys.executable, str(Path(__file__).parent / "fetch_irs_data.py"), "--offline"], check=True)
    with open(DATA_FILE) as f:
        return json.load(f)

TAX_DATA = load_tax_data()

def get_year_data(year=2024):
    return TAX_DATA["years"].get(str(year), TAX_DATA["years"]["2024"])

CITIES = [
    {"city":"New York","state":"NY","state_tax":6.85,"city_tax":3.876,"note":"NY + NYC city income tax"},
    {"city":"Los Angeles","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
    {"city":"Chicago","state":"IL","state_tax":4.95,"city_tax":0,"note":"IL flat rate"},
    {"city":"Houston","state":"TX","state_tax":0,"city_tax":0,"note":"TX - no state income tax"},
    {"city":"Phoenix","state":"AZ","state_tax":2.5,"city_tax":0,"note":"AZ flat rate"},
    {"city":"Philadelphia","state":"PA","state_tax":3.07,"city_tax":3.75,"note":"PA + Philly wage tax"},
    {"city":"San Antonio","state":"TX","state_tax":0,"city_tax":0,"note":"TX - no state income tax"},
    {"city":"San Diego","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
    {"city":"Dallas","state":"TX","state_tax":0,"city_tax":0,"note":"TX - no state income tax"},
    {"city":"San Jose","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
    {"city":"Austin","state":"TX","state_tax":0,"city_tax":0,"note":"TX - no state income tax"},
    {"city":"Jacksonville","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"Fort Worth","state":"TX","state_tax":0,"city_tax":0,"note":"TX - no state income tax"},
    {"city":"Columbus","state":"OH","state_tax":3.99,"city_tax":2.5,"note":"OH + Columbus city income tax"},
    {"city":"Charlotte","state":"NC","state_tax":4.5,"city_tax":0,"note":"NC flat rate"},
    {"city":"Indianapolis","state":"IN","state_tax":3.05,"city_tax":0,"note":"IN flat rate"},
    {"city":"San Francisco","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
    {"city":"Seattle","state":"WA","state_tax":0,"city_tax":0,"note":"WA - no state income tax"},
    {"city":"Denver","state":"CO","state_tax":4.4,"city_tax":0,"note":"CO flat rate"},
    {"city":"Nashville","state":"TN","state_tax":0,"city_tax":0,"note":"TN - no earned income tax"},
    {"city":"Oklahoma City","state":"OK","state_tax":4.75,"city_tax":0,"note":"OK marginal rate"},
    {"city":"Washington","state":"DC","state_tax":8.5,"city_tax":0,"note":"DC income tax"},
    {"city":"Las Vegas","state":"NV","state_tax":0,"city_tax":0,"note":"NV - no state income tax"},
    {"city":"Louisville","state":"KY","state_tax":4.5,"city_tax":2.2,"note":"KY flat + Louisville occupational tax"},
    {"city":"Memphis","state":"TN","state_tax":0,"city_tax":0,"note":"TN - no earned income tax"},
    {"city":"Portland","state":"OR","state_tax":9.9,"city_tax":0,"note":"OR top marginal rate"},
    {"city":"Baltimore","state":"MD","state_tax":5.75,"city_tax":3.2,"note":"MD + Baltimore city piggyback"},
    {"city":"Milwaukee","state":"WI","state_tax":5.3,"city_tax":0,"note":"WI marginal rate"},
    {"city":"Albuquerque","state":"NM","state_tax":4.9,"city_tax":0,"note":"NM marginal rate"},
    {"city":"Tucson","state":"AZ","state_tax":2.5,"city_tax":0,"note":"AZ flat rate"},
    {"city":"Fresno","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
    {"city":"Sacramento","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
    {"city":"Kansas City","state":"MO","state_tax":4.95,"city_tax":1.0,"note":"MO + KCMO earnings tax"},
    {"city":"Atlanta","state":"GA","state_tax":5.49,"city_tax":0,"note":"GA rate"},
    {"city":"Omaha","state":"NE","state_tax":5.84,"city_tax":0,"note":"NE marginal rate"},
    {"city":"Colorado Springs","state":"CO","state_tax":4.4,"city_tax":0,"note":"CO flat rate"},
    {"city":"Raleigh","state":"NC","state_tax":4.5,"city_tax":0,"note":"NC flat rate"},
    {"city":"Virginia Beach","state":"VA","state_tax":5.75,"city_tax":0,"note":"VA marginal rate"},
    {"city":"Minneapolis","state":"MN","state_tax":9.85,"city_tax":0,"note":"MN top marginal rate"},
    {"city":"Tampa","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"New Orleans","state":"LA","state_tax":3.0,"city_tax":0,"note":"LA flat rate"},
    {"city":"Boston","state":"MA","state_tax":5.0,"city_tax":0,"note":"MA flat rate"},
    {"city":"Detroit","state":"MI","state_tax":4.05,"city_tax":2.4,"note":"MI + Detroit city income tax"},
    {"city":"Miami","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"Pittsburgh","state":"PA","state_tax":3.07,"city_tax":3.0,"note":"PA + Pittsburgh local tax"},
    {"city":"Cincinnati","state":"OH","state_tax":3.99,"city_tax":1.8,"note":"OH + Cincinnati city income tax"},
    {"city":"St. Louis","state":"MO","state_tax":4.95,"city_tax":1.0,"note":"MO + St. Louis earnings tax"},
    {"city":"Salt Lake City","state":"UT","state_tax":4.65,"city_tax":0,"note":"UT flat rate"},
    {"city":"Honolulu","state":"HI","state_tax":11.0,"city_tax":0,"note":"HI top marginal rate"},
    {"city":"Anchorage","state":"AK","state_tax":0,"city_tax":0,"note":"AK - no state income tax"},
    {"city":"Boise","state":"ID","state_tax":5.8,"city_tax":0,"note":"ID flat rate"},
    {"city":"Des Moines","state":"IA","state_tax":6.0,"city_tax":0,"note":"IA marginal rate"},
    {"city":"Richmond","state":"VA","state_tax":5.75,"city_tax":1.5,"note":"VA + Richmond city tax"},
    {"city":"Sioux Falls","state":"SD","state_tax":0,"city_tax":0,"note":"SD - no state income tax"},
    {"city":"Fargo","state":"ND","state_tax":2.5,"city_tax":0,"note":"ND marginal rate"},
    {"city":"Manchester","state":"NH","state_tax":0,"city_tax":0,"note":"NH - no earned income tax"},
    {"city":"Cheyenne","state":"WY","state_tax":0,"city_tax":0,"note":"WY - no state income tax"},
    {"city":"Billings","state":"MT","state_tax":6.75,"city_tax":0,"note":"MT top marginal rate"},
    {"city":"Charleston","state":"WV","state_tax":6.5,"city_tax":0,"note":"WV marginal rate"},
    {"city":"Columbia","state":"SC","state_tax":6.5,"city_tax":0,"note":"SC marginal rate"},
    {"city":"Little Rock","state":"AR","state_tax":4.4,"city_tax":0,"note":"AR marginal rate"},
    {"city":"Jackson","state":"MS","state_tax":4.7,"city_tax":0,"note":"MS marginal rate"},
    {"city":"Birmingham","state":"AL","state_tax":5.0,"city_tax":1.0,"note":"AL + Birmingham occupational tax"},
    {"city":"Spokane","state":"WA","state_tax":0,"city_tax":0,"note":"WA - no state income tax"},
    {"city":"Eugene","state":"OR","state_tax":9.9,"city_tax":0,"note":"OR top marginal rate"},
    {"city":"Newark","state":"NJ","state_tax":10.75,"city_tax":1.0,"note":"NJ top rate + Newark payroll tax"},
    {"city":"Buffalo","state":"NY","state_tax":6.85,"city_tax":0,"note":"NY state rate"},
    {"city":"Grand Rapids","state":"MI","state_tax":4.05,"city_tax":1.5,"note":"MI + Grand Rapids city income tax"},
    {"city":"Toledo","state":"OH","state_tax":3.99,"city_tax":2.5,"note":"OH + Toledo city income tax"},
    {"city":"Akron","state":"OH","state_tax":3.99,"city_tax":2.5,"note":"OH + Akron city income tax"},
    {"city":"Orlando","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"Tallahassee","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"Knoxville","state":"TN","state_tax":0,"city_tax":0,"note":"TN - no earned income tax"},
    {"city":"Chattanooga","state":"TN","state_tax":0,"city_tax":0,"note":"TN - no earned income tax"},
    {"city":"Reno","state":"NV","state_tax":0,"city_tax":0,"note":"NV - no state income tax"},
    {"city":"Scottsdale","state":"AZ","state_tax":2.5,"city_tax":0,"note":"AZ flat rate"},
    {"city":"Chandler","state":"AZ","state_tax":2.5,"city_tax":0,"note":"AZ flat rate"},
    {"city":"Mesa","state":"AZ","state_tax":2.5,"city_tax":0,"note":"AZ flat rate"},
    {"city":"Fort Collins","state":"CO","state_tax":4.4,"city_tax":0,"note":"CO flat rate"},
    {"city":"Aurora","state":"CO","state_tax":4.4,"city_tax":0,"note":"CO flat rate"},
    {"city":"Greensboro","state":"NC","state_tax":4.5,"city_tax":0,"note":"NC flat rate"},
    {"city":"Durham","state":"NC","state_tax":4.5,"city_tax":0,"note":"NC flat rate"},
    {"city":"Madison","state":"WI","state_tax":5.3,"city_tax":0,"note":"WI marginal rate"},
    {"city":"Fort Lauderdale","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"Savannah","state":"GA","state_tax":5.49,"city_tax":0,"note":"GA rate"},
    {"city":"Providence","state":"RI","state_tax":5.99,"city_tax":0,"note":"RI top marginal rate"},
    {"city":"Burlington","state":"VT","state_tax":8.75,"city_tax":0,"note":"VT top marginal rate"},
]

# ── Calculation engine (from IRS Rev. Proc.) ──────────────────────────────────
def calc_tax(taxable, brackets):
    tax, prev = 0.0, 0
    for limit, rate in brackets:
        if taxable <= 0: break
        cap = limit if limit is not None else float("inf")
        chunk = min(taxable, cap - prev)
        tax += chunk * rate / 100
        taxable -= chunk
        prev = cap
    return max(0.0, tax)

def marginal_rate(taxable, brackets):
    prev = 0
    for limit, rate in brackets:
        cap = limit if limit is not None else float("inf")
        if taxable <= cap - prev: return rate
        taxable -= cap - prev; prev = cap
    return 37

def calc_ctc(deps, magi, status, cfg):
    credit = deps * cfg["credit_per_child"]
    threshold = cfg["phaseout_mfj"] if status == "mfj" else cfg["phaseout_other"]
    if magi > threshold:
        credit = max(0.0, credit - math.floor((magi - threshold) / 1000) * cfg["phaseout_per_1000"])
    return {"total": credit, "refundable": min(credit, deps * cfg["refundable_per_child"])}

def calc_eic(earned, deps, status, cfg):
    if earned <= 0: return 0
    d = min(deps, 3)
    max_e = cfg["max_earned"][d] + (cfg.get("mfj_bonus", 0) if status == "mfj" else 0)
    if earned > max_e: return 0
    return round(cfg["max_credit"][d] * min(1.0, earned / (max_e * 0.30)))

# ── HTML (all in one string) ───────────────────────────────────────────────────
def build_html(cities_json):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>IRS Tax Refund Calculator 2024</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0a0f;--surface:#111118;--surface2:#18181f;--border:rgba(255,255,255,0.07);--bfocus:rgba(99,179,237,0.5);--text:#f0f0f5;--muted:#888899;--faint:#44445a;--accent:#63b3ed;--accent2:#68d391;--danger:#fc8181;--r:16px;--fd:'Syne',sans-serif;--fm:'DM Mono',monospace}
html{font-size:16px;scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--fd);min-height:100vh;overflow-x:hidden}
.bg-grid{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(99,179,237,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(99,179,237,.03) 1px,transparent 1px);background-size:48px 48px}
.site-header{position:sticky;top:0;z-index:100;background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:0 2rem}
.header-inner{max-width:1100px;margin:0 auto;height:60px;display:flex;align-items:center;justify-content:space-between}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:18px}
.logo-year{background:var(--accent);color:var(--bg);font-size:11px;font-weight:700;padding:2px 7px;border-radius:4px;letter-spacing:.5px}
.header-nav{display:flex;gap:10px}
.nav-badge{font-family:var(--fm);font-size:11px;letter-spacing:.5px;padding:4px 10px;border-radius:20px;background:var(--surface2);border:1px solid var(--border);color:var(--muted)}
.nav-badge.live{color:var(--accent2);border-color:rgba(104,211,145,.3);background:rgba(104,211,145,.05)}
.main{position:relative;z-index:1;max-width:1100px;margin:0 auto;padding:3rem 1.5rem 4rem}
.hero{text-align:center;margin-bottom:3rem}
.hero-title{font-size:clamp(2.5rem,6vw,4.5rem);font-weight:700;line-height:1.0;letter-spacing:-2px}
.hero-title .accent{background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-sub{font-family:var(--fm);font-size:13px;color:var(--muted);margin-top:1rem}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start}
@media(max-width:768px){.form-grid{grid-template-columns:1fr}}
.col{display:flex;flex-direction:column;gap:1.5rem}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:1.5rem;transition:border-color .2s}
.card:hover{border-color:rgba(99,179,237,.15)}
.card-label{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--accent);text-transform:uppercase;margin-bottom:1.25rem}
.field{margin-bottom:1rem}
.field:last-child{margin-bottom:0}
.field label{display:block;font-size:12px;font-weight:500;color:var(--muted);margin-bottom:6px;letter-spacing:.3px}
.field input,.field select{width:100%;background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:10px 14px;font-size:14px;font-family:var(--fm);color:var(--text);outline:none;transition:border-color .2s,background .2s;appearance:none;-webkit-appearance:none}
.field input:focus,.field select:focus{border-color:var(--bfocus);background:rgba(99,179,237,.04)}
.field input::placeholder{color:var(--faint)}
.field select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23888899' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;padding-right:36px}
.field-hint{font-size:11px;color:var(--accent2);margin-top:5px;font-family:var(--fm)}
.row-2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:500px){.row-2{grid-template-columns:1fr}}
.divider{height:1px;background:var(--border);margin:1rem 0}
.section-sub{font-size:11px;font-family:var(--fm);letter-spacing:1px;color:var(--faint);text-transform:uppercase;margin:1rem 0 .75rem}
.search-wrap{position:relative}
.dropdown{position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:200;background:var(--surface2);border:1px solid rgba(99,179,237,.3);border-radius:10px;overflow:hidden;display:none;box-shadow:0 16px 40px rgba(0,0,0,.5);max-height:240px;overflow-y:auto}
.dropdown.open{display:block}
.drop-item{padding:10px 14px;cursor:pointer;font-size:14px;color:var(--text);transition:background .1s;display:flex;justify-content:space-between;align-items:center}
.drop-item:hover{background:rgba(99,179,237,.08)}
.drop-note{font-size:11px;color:var(--muted);font-family:var(--fm)}
.w2-group{position:relative;margin-bottom:10px}
.w2-remove{position:absolute;top:0;right:0;background:none;border:1px solid var(--border);border-radius:6px;color:var(--muted);cursor:pointer;padding:4px 8px;font-size:12px;font-family:var(--fd)}
.w2-remove:hover{background:rgba(252,129,129,.1);border-color:var(--danger);color:var(--danger)}
.ghost-btn{background:none;border:1px dashed var(--border);border-radius:8px;color:var(--muted);padding:9px 16px;font-size:13px;cursor:pointer;font-family:var(--fd);width:100%;transition:all .2s}
.ghost-btn:hover{border-color:var(--accent);color:var(--accent)}
.hidden-section{display:none;animation:fadeIn .25s ease}
.hidden-section.visible{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.calc-btn{width:100%;padding:16px 24px;cursor:pointer;background:var(--accent);color:var(--bg);border:none;border-radius:12px;font-size:16px;font-weight:700;font-family:var(--fd);letter-spacing:-.3px;display:flex;align-items:center;justify-content:center;gap:8px;transition:opacity .2s,transform .1s;position:relative}
.calc-btn:hover{opacity:.9}
.calc-btn:active{transform:scale(.98)}
.calc-btn:disabled{opacity:.5;cursor:not-allowed}
.btn-arrow{font-size:20px;transition:transform .2s}
.calc-btn:hover .btn-arrow{transform:translateX(3px)}
.btn-loader{display:none;width:18px;height:18px;border:2px solid rgba(10,10,15,.3);border-top-color:var(--bg);border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.results-section{margin-top:3rem;animation:fadeIn .4s ease}
.results-hero{background:var(--surface);border:1px solid rgba(99,179,237,.2);border-radius:20px;padding:2.5rem 2rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1.5rem;margin-bottom:2rem}
.results-label{font-family:var(--fm);font-size:12px;letter-spacing:1px;color:var(--muted);text-transform:uppercase}
.results-amount{font-size:clamp(3rem,8vw,5rem);font-weight:700;letter-spacing:-3px;line-height:1;margin:.25rem 0}
.results-amount.refund{color:var(--accent2)}
.results-amount.owe{color:var(--danger)}
.results-sub{font-family:var(--fm);font-size:12px;color:var(--muted)}
.results-pills{display:flex;flex-wrap:wrap;gap:8px}
.pill{font-family:var(--fm);font-size:12px;padding:6px 12px;border-radius:20px;border:1px solid var(--border);color:var(--muted);background:var(--surface2)}
.results-tabs{display:flex;gap:4px;margin-bottom:1.5rem;border-bottom:1px solid var(--border)}
.rtab{padding:10px 20px;background:none;border:none;font-size:14px;font-weight:600;font-family:var(--fd);color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;transition:color .15s}
.rtab.active{color:var(--accent);border-bottom-color:var(--accent)}
.rtab-content{display:none}
.rtab-content.active{display:block;animation:fadeIn .2s ease}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:1.5rem}
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem 1.25rem}
.slabel{font-family:var(--fm);font-size:11px;color:var(--faint);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px}
.svalue{font-size:20px;font-weight:700;color:var(--text)}
.svalue.pos{color:var(--accent2)}
.svalue.neg{color:var(--danger)}
.svalue.accent{color:var(--accent)}
.bar-row{display:flex;align-items:center;gap:14px;margin-bottom:12px}
.bar-row-label{font-size:13px;color:var(--muted);min-width:160px;font-family:var(--fm)}
.bar-track{flex:1;height:6px;background:var(--surface2);border-radius:3px;overflow:hidden}
.bar-fill{height:100%;border-radius:3px;transition:width .7s cubic-bezier(.22,1,.36,1)}
.bar-val{font-family:var(--fm);font-size:12px;color:var(--muted);min-width:80px;text-align:right}
.breakdown-table{background:var(--surface);border:1px solid var(--border);border-radius:16px;overflow:hidden}
.bt-row{display:flex;justify-content:space-between;align-items:center;padding:12px 20px;border-bottom:1px solid var(--border);font-size:14px}
.bt-row:last-child{border-bottom:none}
.bt-row.hdr{background:var(--surface2);padding:10px 20px}
.bt-lbl{color:var(--muted)}
.bt-lbl.hdr{font-family:var(--fm);font-size:11px;letter-spacing:1px;color:var(--faint);text-transform:uppercase}
.bt-val{font-weight:600;font-family:var(--fm)}
.bt-val.neg{color:var(--danger)}
.bt-val.pos{color:var(--accent2)}
.bt-val.neutral{color:var(--text)}
.bt-row.total{background:rgba(99,179,237,.05);border-top:1px solid rgba(99,179,237,.2)}
.bt-row.total .bt-lbl{color:var(--text);font-weight:600}
.state-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem}
.state-title{font-size:18px;font-weight:700;margin-bottom:4px}
.state-note{font-size:12px;color:var(--muted);font-family:var(--fm);margin-bottom:1.5rem}
.no-city{color:var(--muted);font-size:14px;font-family:var(--fm)}
.disclaimer{text-align:center;font-size:11px;color:var(--faint);font-family:var(--fm);margin-top:3rem;line-height:1.6}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
</style>
</head>
<body>
<div class="bg-grid"></div>
<header class="site-header">
  <div class="header-inner">
    <div class="logo"><span style="font-size:22px">&#9878;</span><span>TaxCalc <span class="logo-year">2024</span></span></div>
    <nav class="header-nav">
      <span class="nav-badge">IRS Updated</span>
      <span class="nav-badge live">&#9679; Live Rules</span>
    </nav>
  </div>
</header>
<main class="main">
  <div class="hero">
    <h1 class="hero-title">Federal Tax<br><span class="accent">Refund Calculator</span></h1>
    <p class="hero-sub">All 50 states &middot; 2024 IRS brackets &middot; City-level tax rates</p>
  </div>
  <form id="taxForm" class="form-grid" autocomplete="off">
    <div class="col">
      <div class="card">
        <div class="card-label">01 &mdash; Location &amp; Filing</div>
        <div class="field">
          <label>City &amp; State</label>
          <div class="search-wrap">
            <input type="text" id="citySearch" placeholder="Search any US city..." autocomplete="off"/>
            <div class="dropdown" id="cityDropdown"></div>
          </div>
          <div class="field-hint" id="cityHint"></div>
        </div>
        <div class="row-2">
          <div class="field">
            <label>Filing status</label>
            <select id="filingStatus">
              <option value="single">Single</option>
              <option value="mfj">Married filing jointly</option>
              <option value="mfs">Married filing separately</option>
              <option value="hoh">Head of household</option>
              <option value="qss">Qualifying surviving spouse</option>
            </select>
          </div>
          <div class="field">
            <label>Dependents</label>
            <input type="number" id="dependents" value="0" min="0" max="20"/>
          </div>
        </div>
        <div class="field">
          <label>Tax year</label>
          <select id="taxYear">
            <option value="2024">2024 &mdash; file by April 15, 2025</option>
            <option value="2025">2025 &mdash; file by April 15, 2026</option>
          </select>
        </div>
      </div>
      <div class="card">
        <div class="card-label">02 &mdash; Income</div>
        <div id="w2Container">
          <div class="w2-group">
            <div class="row-2">
              <div class="field"><label>W-2 wages / salary</label><input type="text" class="w2wages" placeholder="$0"/></div>
              <div class="field"><label>Federal tax withheld</label><input type="text" class="w2withheld" placeholder="$0"/></div>
            </div>
          </div>
        </div>
        <button type="button" class="ghost-btn" id="addW2Btn">+ Add another W-2 / employer</button>
        <div class="divider"></div>
        <div class="row-2">
          <div class="field"><label>Self-employment income</label><input type="text" id="selfEmploy" placeholder="$0"/></div>
          <div class="field"><label>Interest &amp; dividends</label><input type="text" id="interest" placeholder="$0"/></div>
        </div>
        <div class="row-2">
          <div class="field"><label>Capital gains (net)</label><input type="text" id="capGains" placeholder="$0"/></div>
          <div class="field"><label>Other income (1099-MISC)</label><input type="text" id="otherIncome" placeholder="$0"/></div>
        </div>
        <div class="field"><label>Estimated tax payments (1040-ES)</label><input type="text" id="estPayments" placeholder="$0"/></div>
      </div>
    </div>
    <div class="col">
      <div class="card">
        <div class="card-label">03 &mdash; Deductions &amp; Above-Line</div>
        <div class="field">
          <label>Deduction method</label>
          <select id="deductionType">
            <option value="standard">Standard deduction (recommended)</option>
            <option value="itemized">Itemize my deductions</option>
          </select>
        </div>
        <div id="itemizedSection" class="hidden-section">
          <div class="section-sub">Itemized deductions</div>
          <div class="row-2">
            <div class="field"><label>Mortgage interest</label><input type="text" id="mortgageInt" placeholder="$0"/></div>
            <div class="field"><label>SALT (capped at $10k)</label><input type="text" id="salt" placeholder="$0"/></div>
          </div>
          <div class="row-2">
            <div class="field"><label>Charitable contributions</label><input type="text" id="charity" placeholder="$0"/></div>
            <div class="field"><label>Medical (above 7.5% AGI)</label><input type="text" id="medical" placeholder="$0"/></div>
          </div>
        </div>
        <div class="section-sub">Above-line deductions</div>
        <div class="row-2">
          <div class="field"><label>401(k) / 403(b) / IRA</label><input type="text" id="retirement" placeholder="$0"/></div>
          <div class="field"><label>HSA contributions</label><input type="text" id="hsa" placeholder="$0"/></div>
        </div>
        <div class="field"><label>Student loan interest paid</label><input type="text" id="studentLoan" placeholder="$0"/></div>
      </div>
      <div class="card">
        <div class="card-label">04 &mdash; Credits &amp; Other Taxes</div>
        <div class="row-2">
          <div class="field"><label>Child &amp; dependent care expenses</label><input type="text" id="childCare" placeholder="$0"/></div>
          <div class="field"><label>Education expenses (1098-T)</label><input type="text" id="education" placeholder="$0"/></div>
        </div>
        <div class="row-2">
          <div class="field"><label>State tax withheld (W-2 box 17)</label><input type="text" id="stateWithheld" placeholder="$0"/></div>
          <div class="field"><label>Foreign tax credit</label><input type="text" id="foreignTax" placeholder="$0"/></div>
        </div>
        <div class="field"><label>Additional Medicare / NIIT</label><input type="text" id="niit" placeholder="$0"/></div>
      </div>
      <button type="submit" class="calc-btn" id="calcBtn">
        <span id="btnLabel">Calculate My Refund</span>
        <span class="btn-arrow">&#8594;</span>
        <div class="btn-loader" id="btnLoader"></div>
      </button>
    </div>
  </form>
  <section class="results-section" id="resultsSection" style="display:none">
    <div class="results-hero">
      <div>
        <p class="results-label" id="resultsLabel">Estimated Federal Refund</p>
        <div class="results-amount" id="resultsAmount">$0</div>
        <p class="results-sub" id="resultsSub"></p>
      </div>
      <div class="results-pills">
        <span class="pill" id="pill-effective"></span>
        <span class="pill" id="pill-marginal"></span>
        <span class="pill" id="pill-deduction"></span>
      </div>
    </div>
    <div class="results-tabs">
      <button class="rtab active" data-tab="federal" onclick="switchTab('federal')">Federal</button>
      <button class="rtab" data-tab="state" onclick="switchTab('state')">State &amp; Local</button>
      <button class="rtab" data-tab="breakdown" onclick="switchTab('breakdown')">Full Breakdown</button>
    </div>
    <div class="rtab-content active" id="rtab-federal">
      <div class="stats-grid" id="statsGrid"></div>
      <div id="barSection"></div>
    </div>
    <div class="rtab-content" id="rtab-state">
      <div class="state-card" id="stateCard"></div>
    </div>
    <div class="rtab-content" id="rtab-breakdown">
      <div class="breakdown-table" id="breakdownTable"></div>
    </div>
  </section>
  <p class="disclaimer">For estimation purposes only. Tax laws change annually. Consult a CPA or enrolled agent. Data sourced from IRS Rev. Proc. 2023-34 and 2024-40.</p>
</main>
<script id="cities-data" type="application/json">""" + cities_json + """</script>
<script>
'use strict';
const $=id=>document.getElementById(id);
const fmt=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
const pct=n=>n.toFixed(1)+'%';
let selCity=null;
const CITIES=JSON.parse($('cities-data').textContent);

$('citySearch').addEventListener('input',function(){
  const q=this.value.toLowerCase().trim(),dd=$('cityDropdown');
  if(!q){dd.classList.remove('open');return;}
  const m=CITIES.filter(c=>c.city.toLowerCase().startsWith(q)||(c.city+', '+c.state).toLowerCase().includes(q)).slice(0,10);
  if(!m.length){dd.classList.remove('open');return;}
  dd.innerHTML=m.map(c=>`<div class="drop-item" data-idx="${CITIES.indexOf(c)}"><span>${c.city}, ${c.state}</span><span class="drop-note">${c.note}</span></div>`).join('');
  dd.querySelectorAll('.drop-item').forEach(el=>{
    el.addEventListener('click',()=>{
      const city=CITIES[+el.dataset.idx];selCity=city;
      $('citySearch').value=city.city+', '+city.state;
      dd.classList.remove('open');
      $('cityHint').textContent=city.state_tax===0?'No state income tax in '+city.state:city.note+' ~ '+city.state_tax+'% state rate';
    });
  });
  dd.classList.add('open');
});
document.addEventListener('click',e=>{if(!e.target.closest('.search-wrap'))$('cityDropdown').classList.remove('open');});

$('deductionType').addEventListener('change',function(){
  $('itemizedSection').classList.toggle('visible',this.value==='itemized');
});

$('addW2Btn').addEventListener('click',()=>{
  const g=document.createElement('div');g.className='w2-group';
  g.innerHTML='<button type="button" class="w2-remove" onclick="this.parentElement.remove()">x Remove</button><div class="row-2"><div class="field"><label>W-2 wages / salary</label><input type="text" class="w2wages" placeholder="$0"/></div><div class="field"><label>Federal tax withheld</label><input type="text" class="w2withheld" placeholder="$0"/></div></div>';
  $('w2Container').appendChild(g);
});

function pd(id){const el=typeof id==='string'?$(id):id;return parseFloat((el?.value||'').replace(/[$,\\s]/g,''))||0;}

$('taxForm').addEventListener('submit',async function(e){
  e.preventDefault();
  const btn=$('calcBtn');btn.disabled=true;$('btnLabel').textContent='Calculating...';
  $('btnLoader').style.display='block';btn.querySelector('.btn-arrow').style.display='none';
  const wages=Array.from(document.querySelectorAll('.w2wages')).reduce((a,i)=>a+pd(i),0);
  const withheld=Array.from(document.querySelectorAll('.w2withheld')).reduce((a,i)=>a+pd(i),0);
  const payload={
    filing_status:$('filingStatus').value,dependents:$('dependents').value,
    deduction_type:$('deductionType').value,tax_year:$('taxYear').value,
    wages,withheld,self_employ:pd('selfEmploy'),interest:pd('interest'),
    cap_gains:pd('capGains'),other_income:pd('otherIncome'),est_payments:pd('estPayments'),
    state_withheld:pd('stateWithheld'),retirement:pd('retirement'),hsa:pd('hsa'),
    student_loan:pd('studentLoan'),child_care:pd('childCare'),education:pd('education'),
    niit:pd('niit'),foreign_tax:pd('foreignTax'),mortgage_int:pd('mortgageInt'),
    salt:pd('salt'),charity:pd('charity'),medical:pd('medical'),city_data:selCity||null
  };
  try{
    const res=await fetch('/api/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const d=await res.json();renderResults(d);
  }catch(err){alert('Calculation error - please try again.');console.error(err);}
  finally{btn.disabled=false;$('btnLabel').textContent='Recalculate';$('btnLoader').style.display='none';btn.querySelector('.btn-arrow').style.display='inline';}
});

function renderResults(d){
  const sec=$('resultsSection');sec.style.display='block';
  setTimeout(()=>sec.scrollIntoView({behavior:'smooth',block:'start'}),80);
  const isR=d.result>=0;
  $('resultsLabel').textContent=isR?'Estimated Federal Refund':'Estimated Amount Owed';
  $('resultsAmount').textContent=fmt(Math.abs(d.result));
  $('resultsAmount').className='results-amount '+(isR?'refund':'owe');
  $('resultsSub').textContent='Tax Year '+d._tax_year+' | '+(d.using_standard?'Standard':'Itemized')+' deduction';
  $('pill-effective').textContent='Effective: '+pct(d.effective_rate);
  $('pill-marginal').textContent='Marginal: '+d.marginal_rate+'%';
  $('pill-deduction').textContent='Deduction: '+fmt(d.deduction);
  $('statsGrid').innerHTML=[
    {l:'Gross income',v:fmt(d.gross_income),c:''},
    {l:'Adjusted Gross Income',v:fmt(d.agi),c:'accent'},
    {l:'Taxable income',v:fmt(d.taxable_income),c:''},
    {l:'Fed. income tax',v:fmt(d.fed_tax),c:'neg'},
    {l:'SE tax',v:fmt(d.se_tax),c:d.se_tax>0?'neg':''},
    {l:'Total credits',v:fmt(d.total_credits),c:'pos'},
    {l:'Total liability',v:fmt(d.total_tax),c:'neg'},
    {l:'Total payments',v:fmt(d.total_payments),c:'pos'},
  ].map(s=>`<div class="stat-card"><div class="slabel">${s.l}</div><div class="svalue ${s.c}">${s.v}</div></div>`).join('');
  const mx=Math.max(d.gross_income,1);
  $('barSection').innerHTML=[
    {l:'Gross income',v:d.gross_income,col:'#63b3ed'},
    {l:'AGI',v:d.agi,col:'#76e4f7'},
    {l:'Taxable income',v:d.taxable_income,col:'#9f7aea'},
    {l:'Federal tax',v:d.fed_tax,col:'#fc8181'},
    {l:'Credits',v:d.total_credits,col:'#68d391'},
  ].map(b=>`<div class="bar-row"><span class="bar-row-label">${b.l}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.round(b.v/mx*100)}%;background:${b.col}"></div></div><span class="bar-val">${fmt(b.v)}</span></div>`).join('');
  const rows=[
    {hdr:'Income'},{l:'Gross income',v:d.gross_income,c:'neutral'},
    {l:'Above-line deductions',v:d.above_line,c:'neg'},
    {l:'Adjusted Gross Income (AGI)',v:d.agi,c:'accent'},
    {hdr:'Deductions & Tax'},
    {l:(d.using_standard?'Standard':'Itemized')+' deduction',v:d.deduction,c:'neg'},
    {l:'Taxable income',v:d.taxable_income,c:'neutral'},
    {l:'Federal income tax',v:d.fed_tax,c:'neg'},
    {l:'Self-employment tax',v:d.se_tax,c:d.se_tax>0?'neg':'neutral'},
    {hdr:'Credits'},
    {l:'Child Tax Credit',v:d.ctc_total,c:'pos'},{l:'Earned Income Credit',v:d.eic,c:'pos'},
    {l:'Education credit',v:d.edu_credit,c:'pos'},{l:'Total credits',v:d.total_credits,c:'pos'},
    {hdr:'Payments'},
    {l:'Federal withheld',v:d.withheld,c:'pos'},{l:'Estimated payments',v:d.est_payments,c:'pos'},
    {l:'Total payments',v:d.total_payments,c:'pos'},{l:'Total tax liability',v:d.total_tax,c:'neg'},
  ];
  $('breakdownTable').innerHTML=rows.map(r=>{
    if(r.hdr)return`<div class="bt-row hdr"><span class="bt-lbl hdr">${r.hdr}</span></div>`;
    return`<div class="bt-row"><span class="bt-lbl">${r.l}</span><span class="bt-val ${r.c}">${(r.c==='neg'&&r.v>0?'-':'')}${fmt(r.v)}</span></div>`;
  }).join('')+`<div class="bt-row total"><span class="bt-lbl">${isR?'Estimated refund':'Amount owed'}</span><span class="bt-val ${isR?'pos':'neg'}">${fmt(Math.abs(d.result))}</span></div>`;
  if(selCity&&d.state&&Object.keys(d.state).length){
    const s=d.state,city=selCity,sr=s.state_refund>=0;
    $('stateCard').innerHTML=`<div class="state-title">${city.city}, ${city.state}</div><div class="state-note">${city.note}</div>`+
    [['State taxable income',fmt(s.state_agi),'neutral'],
     ['State income tax rate',city.state_tax>0?city.state_tax+'%':'None (0%)','neutral'],
     ['Estimated state tax',city.state_tax>0?fmt(s.state_tax_amt):'$0','neg'],
     ['City / local tax',city.city_tax>0?city.city_tax+'% -> '+fmt(s.city_tax_amt):'None',city.city_tax>0?'neg':'neutral'],
     ['State withheld',fmt(pd('stateWithheld')),'neutral'],
     ['State + local combined',fmt(s.combined),'neg'],
     [sr?'State refund':'State amount owed',fmt(Math.abs(s.state_refund)),sr?'pos':'neg'],
    ].map(([l,v,c])=>`<div class="bt-row"><span class="bt-lbl">${l}</span><span class="bt-val ${c}">${v}</span></div>`).join('');
  }else{$('stateCard').innerHTML='<p class="no-city">Select a city above to see state &amp; local tax details.</p>';}
  switchTab('federal');
}
function switchTab(n){
  document.querySelectorAll('.rtab').forEach(t=>t.classList.toggle('active',t.dataset.tab===n));
  document.querySelectorAll('.rtab-content').forEach(t=>t.classList.toggle('active',t.id==='rtab-'+n));
}
window.switchTab=switchTab;
</script>
</body>
</html>"""

# ── Flask routes ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    cities_json = json.dumps(CITIES)
    return Response(build_html(cities_json), mimetype="text/html")

@app.route("/api/cities")
def api_cities():
    q = request.args.get("q", "").lower()
    if not q: return jsonify([])
    return jsonify([c for c in CITIES if q in c["city"].lower() or q in (c["city"]+", "+c["state"]).lower()][:12])

@app.route("/api/tax-data")
def api_tax_data():
    year = int(request.args.get("year", 2024))
    yd = get_year_data(year)
    return jsonify({"year": year, "source": yd.get("source"), "source_url": yd.get("source_url"),
                    "standard_deductions": yd.get("standard_deductions"), "salt_cap": yd.get("salt_cap"),
                    "brackets_single": yd.get("brackets", {}).get("single")})

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    def p(k):
        try: return float(str(data.get(k,0)).replace(",","").replace("$","")) or 0.0
        except: return 0.0

    year = int(data.get("tax_year", 2024))
    yd = get_year_data(year)
    status = data.get("filing_status", "single")
    deps = int(data.get("dependents", 0))
    brackets = yd["brackets"].get(status, yd["brackets"]["single"])

    wages=p("wages"); withheld=p("withheld"); self_employ=p("self_employ")
    interest=p("interest"); cap_gains=p("cap_gains"); other_income=p("other_income")
    est_payments=p("est_payments"); state_withheld=p("state_withheld")
    retirement=p("retirement"); hsa=p("hsa"); student_loan=p("student_loan")
    child_care=p("child_care"); education=p("education"); niit=p("niit")
    foreign_tax=p("foreign_tax"); mortgage_int=p("mortgage_int")
    salt_input=p("salt"); charity=p("charity"); medical=p("medical")
    deduction_type = data.get("deduction_type", "standard")

    se_net = self_employ * yd["se_net_earnings_rate"]
    se_tax = se_net * yd["se_rate"] if self_employ > 400 else 0.0
    se_deduction = se_tax * yd["se_deductible_fraction"]
    gross_income = wages + self_employ + interest + cap_gains + other_income
    above_line = retirement + hsa + student_loan + se_deduction
    agi = max(0.0, gross_income - above_line)
    std_ded = yd["standard_deductions"].get(status, 14600)
    salt_capped = min(salt_input, yd.get("salt_cap", 10000))
    itemized = mortgage_int + salt_capped + charity + medical
    if deduction_type == "itemized":
        deduction = max(itemized, std_ded); using_standard = itemized <= std_ded
    else:
        deduction = std_ded; using_standard = True
    taxable_income = max(0.0, agi - deduction)
    fed_tax = calc_tax(taxable_income, brackets)
    mrate = marginal_rate(taxable_income, brackets)
    effective = (fed_tax / gross_income * 100) if gross_income > 0 else 0.0
    ctc = calc_ctc(deps, agi, status, yd["ctc"])
    eic = calc_eic(wages + self_employ, deps, status, yd["eic"])
    cdcc = yd.get("cdcc", {})
    cdcc_max = cdcc.get("max_expenses_1",3000) if deps==1 else cdcc.get("max_expenses_2plus",6000)
    child_care_credit = min(child_care, cdcc_max) * cdcc.get("rate", 0.20) if deps > 0 else 0.0
    edu_credit = min(education, yd.get("aoc_max", 2500))
    edu_refundable = edu_credit * yd.get("aoc_refundable_pct", 0.40)
    non_ref = min(fed_tax+se_tax, ctc["total"]-ctc["refundable"]+child_care_credit+(edu_credit-edu_refundable)+foreign_tax)
    total_tax = max(0.0, fed_tax+se_tax-non_ref) + niit
    total_payments = withheld + est_payments + ctc["refundable"] + eic + edu_refundable
    total_credits = ctc["total"] + eic + child_care_credit + edu_credit + foreign_tax
    result = total_payments - total_tax

    state_result = {}
    city_data = data.get("city_data") or {}
    if city_data:
        sr = city_data.get("state_tax",0)/100; cr = city_data.get("city_tax",0)/100
        sagi = max(0.0, agi-(deduction*0.5 if sr>0 else 0))
        stax = round(sagi*sr); ctax = round(agi*cr)
        state_result = {"state_agi":round(sagi),"state_tax_amt":stax,"city_tax_amt":ctax,
                        "state_refund":round(state_withheld)-stax,"combined":stax+ctax}

    return jsonify({"gross_income":round(gross_income),"agi":round(agi),"taxable_income":round(taxable_income),
        "deduction":round(deduction),"using_standard":using_standard,"above_line":round(above_line),
        "fed_tax":round(fed_tax),"se_tax":round(se_tax),"total_tax":round(total_tax),
        "marginal_rate":mrate,"effective_rate":round(effective,1),
        "ctc_total":round(ctc["total"]),"ctc_refundable":round(ctc["refundable"]),
        "eic":round(eic),"child_care_credit":round(child_care_credit),"edu_credit":round(edu_credit),
        "total_credits":round(total_credits),"withheld":round(withheld),"est_payments":round(est_payments),
        "total_payments":round(total_payments),"result":round(result),
        "state":state_result,"status":status,"_tax_year":year,
        "_data_source":yd.get("source","IRS Rev. Proc."),"_data_url":yd.get("source_url","https://irs.gov")})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV","development") == "development"
    print(f"\n  IRS Tax Calculator running at http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
