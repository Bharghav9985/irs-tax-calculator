"""
app_v2.py - IRS Tax Refund Calculator (Standalone)
===================================================
- Supports Tax Years 2024, 2025, 2026
- Auto-updates from IRS Rev. Proc. on Render via /api/refresh-irs-data
- All data sourced from IRS.gov (Rev. Proc. 2023-34, 2024-40, 2025-32)
- Zero AI API calls
Run: python app_v2.py
"""
import json, os, math
from pathlib import Path
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "tax_data.json"

def load_tax_data():
    if not DATA_FILE.exists():
        import subprocess, sys
        subprocess.run([sys.executable, str(Path(__file__).parent/"fetch_irs_data.py"),"--offline"], check=True)
    with open(DATA_FILE) as f:
        return json.load(f)

TAX_DATA = load_tax_data()

def get_year_data(year=2026):
    return TAX_DATA["years"].get(str(year), TAX_DATA["years"]["2026"])

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
    {"city":"Sacramento","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
    {"city":"Fresno","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
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

# ── Tax engine ─────────────────────────────────────────────────────────────────
def calc_tax(taxable, brackets):
    tax, prev = 0.0, 0
    for limit, rate in brackets:
        if taxable <= 0: break
        cap = limit if limit is not None else float("inf")
        chunk = min(taxable, cap - prev)
        tax += chunk * rate / 100
        taxable -= chunk; prev = cap
    return max(0.0, tax)

def marginal(taxable, brackets):
    prev = 0
    for limit, rate in brackets:
        cap = limit if limit is not None else float("inf")
        if taxable <= cap - prev: return rate
        taxable -= cap - prev; prev = cap
    return 37

def calc_ctc(deps, magi, status, cfg):
    credit = deps * cfg["credit_per_child"]
    t = cfg["phaseout_mfj"] if status=="mfj" else cfg["phaseout_other"]
    if magi > t: credit = max(0.0, credit - math.floor((magi-t)/1000)*cfg["phaseout_per_1000"])
    return {"total":credit,"refundable":min(credit, deps*cfg["refundable_per_child"])}

def calc_eic(earned, deps, status, cfg):
    if earned <= 0: return 0
    d = min(deps,3)
    max_e = cfg["max_earned"][d] + (cfg.get("mfj_bonus",0) if status=="mfj" else 0)
    if earned > max_e: return 0
    return round(cfg["max_credit"][d] * min(1.0, earned/(max_e*0.30)))

# ── HTML builder ───────────────────────────────────────────────────────────────
def build_html(cities_json, meta):
    generated = meta.get("generated","")[:10]
    source = meta.get("source","IRS.gov")
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>IRS Tax Refund Calculator 2024-2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0a0f;--s1:#111118;--s2:#18181f;--bd:rgba(255,255,255,0.07);--bdf:rgba(99,179,237,0.5);--tx:#f0f0f5;--mu:#888899;--fa:#44445a;--ac:#63b3ed;--a2:#68d391;--dn:#fc8181;--am:#f6ad55;--r:16px;--fd:'Syne',sans-serif;--fm:'DM Mono',monospace}
html{font-size:16px;scroll-behavior:smooth}
body{background:var(--bg);color:var(--tx);font-family:var(--fd);min-height:100vh;overflow-x:hidden}
.grid-bg{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(99,179,237,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(99,179,237,.025) 1px,transparent 1px);background-size:48px 48px}
header{position:sticky;top:0;z-index:100;background:rgba(10,10,15,.9);backdrop-filter:blur(20px);border-bottom:1px solid var(--bd);padding:0 2rem}
.hdr{max-width:1100px;margin:0 auto;height:60px;display:flex;align-items:center;justify-content:space-between}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:18px}
.logo-badge{background:var(--ac);color:var(--bg);font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px}
.badges{display:flex;gap:8px;align-items:center}
.badge{font-family:var(--fm);font-size:11px;padding:4px 10px;border-radius:20px;background:var(--s2);border:1px solid var(--bd);color:var(--mu)}
.badge.live{color:var(--a2);border-color:rgba(104,211,145,.3);background:rgba(104,211,145,.05)}
.badge.upd{color:var(--am);border-color:rgba(246,173,85,.3);background:rgba(246,173,85,.05);cursor:pointer}
.badge.upd:hover{opacity:.8}
main{position:relative;z-index:1;max-width:1100px;margin:0 auto;padding:3rem 1.5rem 4rem}
.hero{text-align:center;margin-bottom:2.5rem}
.hero h1{font-size:clamp(2.2rem,5vw,4rem);font-weight:700;line-height:1.05;letter-spacing:-2px}
.hero h1 span{background:linear-gradient(135deg,var(--ac),var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero p{font-family:var(--fm);font-size:12px;color:var(--mu);margin-top:.75rem}
/* Year selector */
.year-bar{display:flex;justify-content:center;gap:10px;margin-bottom:2.5rem;flex-wrap:wrap}
.yr-btn{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:12px 24px;cursor:pointer;font-family:var(--fd);font-size:14px;font-weight:600;color:var(--mu);transition:all .2s;text-align:center}
.yr-btn:hover{border-color:var(--ac);color:var(--tx)}
.yr-btn.active{background:var(--ac);color:var(--bg);border-color:var(--ac)}
.yr-btn .yr-tag{display:block;font-family:var(--fm);font-size:10px;font-weight:400;margin-top:3px;opacity:.8}
.yr-btn.active .yr-tag{opacity:.7}
/* Info bar */
.info-bar{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:12px 20px;margin-bottom:2rem;display:flex;gap:24px;flex-wrap:wrap;font-family:var(--fm);font-size:12px;color:var(--mu)}
.info-item strong{color:var(--ac);margin-right:4px}
.info-item.salt2026{color:var(--a2)}
.info-item.salt2026 strong{color:var(--a2)}
/* Form */
.fg{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start}
@media(max-width:768px){.fg{grid-template-columns:1fr}}
.col{display:flex;flex-direction:column;gap:1.5rem}
.card{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);padding:1.5rem;transition:border-color .2s}
.card:hover{border-color:rgba(99,179,237,.15)}
.clabel{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--ac);text-transform:uppercase;margin-bottom:1.25rem}
.field{margin-bottom:1rem}
.field:last-child{margin-bottom:0}
.field label{display:block;font-size:12px;font-weight:500;color:var(--mu);margin-bottom:6px}
.field input,.field select{width:100%;background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:10px 14px;font-size:14px;font-family:var(--fm);color:var(--tx);outline:none;transition:border-color .2s,background .2s;-webkit-appearance:none;appearance:none}
.field input:focus,.field select:focus{border-color:var(--bdf);background:rgba(99,179,237,.04)}
.field input::placeholder{color:var(--fa)}
.field select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23888899' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;padding-right:36px}
.hint{font-size:11px;color:var(--a2);margin-top:4px;font-family:var(--fm)}
.r2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:480px){.r2{grid-template-columns:1fr}}
.divider{height:1px;background:var(--bd);margin:1rem 0}
.sub{font-size:11px;font-family:var(--fm);letter-spacing:1px;color:var(--fa);text-transform:uppercase;margin:1rem 0 .75rem}
.srch{position:relative}
.dd{position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:200;background:var(--s2);border:1px solid rgba(99,179,237,.3);border-radius:10px;display:none;max-height:220px;overflow-y:auto;box-shadow:0 16px 40px rgba(0,0,0,.5)}
.dd.open{display:block}
.di{padding:10px 14px;cursor:pointer;font-size:14px;color:var(--tx);display:flex;justify-content:space-between;align-items:center;transition:background .1s}
.di:hover{background:rgba(99,179,237,.08)}
.dn2{font-size:11px;color:var(--mu);font-family:var(--fm)}
.w2g{position:relative;margin-bottom:10px}
.rmv{position:absolute;top:0;right:0;background:none;border:1px solid var(--bd);border-radius:6px;color:var(--mu);cursor:pointer;padding:4px 8px;font-size:12px;font-family:var(--fd)}
.rmv:hover{background:rgba(252,129,129,.1);border-color:var(--dn);color:var(--dn)}
.ghost{background:none;border:1px dashed var(--bd);border-radius:8px;color:var(--mu);padding:9px 16px;font-size:13px;cursor:pointer;font-family:var(--fd);width:100%;transition:all .2s}
.ghost:hover{border-color:var(--ac);color:var(--ac)}
.hs{display:none;animation:fi .2s ease}
.hs.vis{display:block}
@keyframes fi{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.cbtn{width:100%;padding:16px 24px;cursor:pointer;background:var(--ac);color:var(--bg);border:none;border-radius:12px;font-size:16px;font-weight:700;font-family:var(--fd);display:flex;align-items:center;justify-content:center;gap:8px;transition:opacity .2s,transform .1s}
.cbtn:hover{opacity:.9}
.cbtn:active{transform:scale(.98)}
.cbtn:disabled{opacity:.5;cursor:not-allowed}
.arr{font-size:20px;transition:transform .2s}
.cbtn:hover .arr{transform:translateX(3px)}
.ldr{display:none;width:18px;height:18px;border:2px solid rgba(10,10,15,.3);border-top-color:var(--bg);border-radius:50%;animation:sp .6s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
/* Results */
.res{margin-top:3rem;animation:fi .4s ease}
.rh{background:var(--s1);border:1px solid rgba(99,179,237,.2);border-radius:20px;padding:2.5rem 2rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1.5rem;margin-bottom:2rem}
.rl{font-family:var(--fm);font-size:12px;letter-spacing:1px;color:var(--mu);text-transform:uppercase}
.ra{font-size:clamp(3rem,8vw,5rem);font-weight:700;letter-spacing:-3px;line-height:1;margin:.25rem 0}
.ra.rf{color:var(--a2)}
.ra.ow{color:var(--dn)}
.rs{font-family:var(--fm);font-size:12px;color:var(--mu)}
.pills{display:flex;flex-wrap:wrap;gap:8px}
.pill{font-family:var(--fm);font-size:12px;padding:6px 12px;border-radius:20px;border:1px solid var(--bd);color:var(--mu);background:var(--s2)}
.rtabs{display:flex;gap:4px;margin-bottom:1.5rem;border-bottom:1px solid var(--bd)}
.rtab{padding:10px 20px;background:none;border:none;font-size:14px;font-weight:600;font-family:var(--fd);color:var(--mu);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;transition:color .15s}
.rtab.active{color:var(--ac);border-bottom-color:var(--ac)}
.rtp{display:none}
.rtp.active{display:block;animation:fi .2s ease}
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:1.5rem}
.sc{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:1rem 1.25rem}
.sl{font-family:var(--fm);font-size:11px;color:var(--fa);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px}
.sv{font-size:20px;font-weight:700;color:var(--tx)}
.sv.pos{color:var(--a2)}.sv.neg{color:var(--dn)}.sv.acc{color:var(--ac)}
.br{display:flex;align-items:center;gap:14px;margin-bottom:12px}
.brl{font-size:13px;color:var(--mu);min-width:150px;font-family:var(--fm)}
.bt{flex:1;height:6px;background:var(--s2);border-radius:3px;overflow:hidden}
.bf{height:100%;border-radius:3px;transition:width .7s cubic-bezier(.22,1,.36,1)}
.bv{font-family:var(--fm);font-size:12px;color:var(--mu);min-width:80px;text-align:right}
.bkt{background:var(--s1);border:1px solid var(--bd);border-radius:16px;overflow:hidden}
.brow{display:flex;justify-content:space-between;align-items:center;padding:12px 20px;border-bottom:1px solid var(--bd);font-size:14px}
.brow:last-child{border-bottom:none}
.brow.hdr{background:var(--s2);padding:10px 20px}
.blbl{color:var(--mu)}
.blbl.hdr{font-family:var(--fm);font-size:11px;letter-spacing:1px;color:var(--fa);text-transform:uppercase}
.bval{font-weight:600;font-family:var(--fm)}
.bval.neg{color:var(--dn)}.bval.pos{color:var(--a2)}.bval.neutral{color:var(--tx)}
.brow.tot{background:rgba(99,179,237,.05);border-top:1px solid rgba(99,179,237,.2)}
.brow.tot .blbl{color:var(--tx);font-weight:600}
.stc{background:var(--s1);border:1px solid var(--bd);border-radius:16px;padding:1.5rem}
.stt{font-size:18px;font-weight:700;margin-bottom:4px}
.stn{font-size:12px;color:var(--mu);font-family:var(--fm);margin-bottom:1.5rem}
.nc{color:var(--mu);font-size:14px;font-family:var(--fm)}
.disc{text-align:center;font-size:11px;color:var(--fa);font-family:var(--fm);margin-top:3rem;line-height:1.6}

.range-section{margin-bottom:2rem}
.range-title{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--mu);text-transform:uppercase;margin-bottom:1rem}
.range-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1.25rem}
@media(max-width:760px){.range-cards{grid-template-columns:1fr 1fr}}
@media(max-width:400px){.range-cards{grid-template-columns:1fr}}
.rc{border-radius:14px;padding:1.1rem;border:1px solid var(--bd);position:relative;transition:transform .15s,border-color .2s}
.rc:hover{transform:translateY(-2px)}
.rc.danger{background:rgba(252,129,129,.06);border-color:rgba(252,129,129,.25)}
.rc.amber{background:rgba(246,173,85,.06);border-color:rgba(246,173,85,.3)}
.rc.blue{background:rgba(99,179,237,.08);border-color:rgba(99,179,237,.35)}
.rc.green{background:rgba(104,211,145,.06);border-color:rgba(104,211,145,.25)}
.rc-badge{font-family:var(--fm);font-size:10px;letter-spacing:.8px;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:5px}
.rc.danger .rc-badge{color:#fc8181}.rc.amber .rc-badge{color:#f6ad55}.rc.blue .rc-badge{color:#63b3ed}.rc.green .rc-badge{color:#68d391}
.rc-badge::before{content:'';width:6px;height:6px;border-radius:50%;background:currentColor;flex-shrink:0}
.rc-amount{font-size:clamp(1.3rem,2.5vw,1.8rem);font-weight:700;letter-spacing:-1px;margin-bottom:5px}
.rc.danger .rc-amount{color:#fc8181}.rc.amber .rc-amount{color:#f6ad55}.rc.blue .rc-amount{color:#63b3ed}.rc.green .rc-amount{color:#68d391}
.rc-conf{font-family:var(--fm);font-size:11px;color:var(--fa);margin-bottom:6px}
.rc-desc{font-size:11px;color:var(--mu);line-height:1.5}
.rc-star{position:absolute;top:10px;right:10px;font-size:10px;font-family:var(--fm);background:rgba(99,179,237,.15);color:var(--ac);padding:2px 7px;border-radius:10px}
.range-viz{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.25rem}
.range-viz-lbl{display:flex;justify-content:space-between;font-family:var(--fm);font-size:11px;color:var(--mu);margin-bottom:10px}
.range-bar{position:relative;height:12px;border-radius:6px;background:var(--s2);margin-bottom:16px}
.range-bar-fill{position:absolute;height:100%;border-radius:6px;background:linear-gradient(90deg,#fc8181 0%,#f6ad55 33%,#63b3ed 66%,#68d391 100%);top:0;transition:all .6s ease}
.range-pins{position:relative;height:20px}
.pin{position:absolute;transform:translateX(-50%);text-align:center}
.pin-dot{width:12px;height:12px;border-radius:50%;border:2px solid var(--bg);margin:0 auto 3px}
.pin-lbl{font-family:var(--fm);font-size:9px;color:var(--mu);white-space:nowrap}
.alert{border-radius:10px;padding:12px 16px;margin-bottom:1rem;font-size:13px;display:flex;gap:10px;align-items:flex-start}
.alert.warn{background:rgba(252,129,129,.08);border:1px solid rgba(252,129,129,.3)}
.alert.ok{background:rgba(104,211,145,.08);border:1px solid rgba(104,211,145,.3)}
.alert.info{background:rgba(99,179,237,.08);border:1px solid rgba(99,179,237,.25)}
.alert-icon{font-size:16px;flex-shrink:0}
.alert-body{font-size:13px;color:var(--tx)}
.alert-body strong{display:block;margin-bottom:2px;font-size:12px}
.alert.warn .alert-body strong{color:#fc8181}
.alert.ok .alert-body strong{color:#68d391}
.alert.info .alert-body strong{color:#63b3ed}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}

/* Range panel */
.range-hero{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:1.5rem}
.rcard{border-radius:14px;padding:1.25rem 1.5rem;border:1px solid var(--bd);position:relative;overflow:hidden}
.rcard.min{background:rgba(252,129,129,.06);border-color:rgba(252,129,129,.25)}
.rcard.safe{background:rgba(246,173,85,.06);border-color:rgba(246,173,85,.3)}
.rcard.base{background:rgba(99,179,237,.07);border-color:rgba(99,179,237,.3)}
.rcard.max{background:rgba(104,211,145,.07);border-color:rgba(104,211,145,.3)}
.rcard-icon{font-size:22px;margin-bottom:.5rem}
.rcard-label{font-family:var(--fm);font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--mu);margin-bottom:4px}
.rcard-amount{font-size:2rem;font-weight:700;letter-spacing:-1px;line-height:1.1}
.rcard.min .rcard-amount{color:#fc8181}
.rcard.safe .rcard-amount{color:#f6ad55}
.rcard.base .rcard-amount{color:#63b3ed}
.rcard.max .rcard-amount{color:#68d391}
.rcard-desc{font-size:12px;color:var(--mu);margin-top:6px;font-family:var(--fm);line-height:1.5}
.rcard-conf{font-size:10px;font-family:var(--fm);margin-top:8px;padding:3px 8px;border-radius:20px;display:inline-block}
.rcard.min .rcard-conf{background:rgba(252,129,129,.15);color:#fc8181}
.rcard.safe .rcard-conf{background:rgba(246,173,85,.15);color:#f6ad55}
.rcard.base .rcard-conf{background:rgba(99,179,237,.15);color:#63b3ed}
.rcard.max .rcard-conf{background:rgba(104,211,145,.15);color:#68d391}
.rcard.recommended::after{content:'RECOMMENDED';position:absolute;top:10px;right:10px;font-size:9px;font-family:var(--fm);letter-spacing:1px;background:rgba(246,173,85,.2);color:#f6ad55;padding:2px 7px;border-radius:10px}
/* Range bar */
.range-bar-wrap{background:var(--s1);border:1px solid var(--bd);border-radius:14px;padding:1.5rem;margin-bottom:1.5rem}
.range-bar-title{font-family:var(--fm);font-size:12px;color:var(--mu);margin-bottom:1rem;text-transform:uppercase;letter-spacing:.8px}
.rbar-track{height:20px;background:var(--s2);border-radius:10px;position:relative;margin:1rem 0 2rem}
.rbar-fill{position:absolute;height:100%;border-radius:10px;transition:all .8s cubic-bezier(.22,1,.36,1)}
.rbar-min{background:linear-gradient(90deg,#fc8181,#f6ad55)}
.rbar-safe{background:linear-gradient(90deg,#f6ad55,#63b3ed)}
.rbar-max{background:linear-gradient(90deg,#63b3ed,#68d391)}
.rbar-marker{position:absolute;top:100%;margin-top:6px;transform:translateX(-50%);font-family:var(--fm);font-size:11px;white-space:nowrap}
/* Risk & tips panels */
.alert-box{border-radius:12px;padding:1rem 1.25rem;margin-bottom:1rem;display:flex;gap:12px;align-items:flex-start}
.alert-box.warn{background:rgba(252,129,129,.07);border:1px solid rgba(252,129,129,.25)}
.alert-box.good{background:rgba(104,211,145,.07);border:1px solid rgba(104,211,145,.25)}
.alert-box.info{background:rgba(99,179,237,.07);border:1px solid rgba(99,179,237,.2)}
.alert-icon{font-size:20px;flex-shrink:0;margin-top:2px}
.alert-body{}
.alert-title{font-size:14px;font-weight:600;margin-bottom:4px}
.alert-box.warn .alert-title{color:#fc8181}
.alert-box.good .alert-title{color:#68d391}
.alert-box.info .alert-title{color:#63b3ed}
.alert-text{font-size:13px;color:var(--mu);line-height:1.5;font-family:var(--fm)}
.tips-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:1rem}
@media(max-width:600px){.tips-grid{grid-template-columns:1fr}}
.tip-card{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:1rem}
.tip-icon{font-size:18px;margin-bottom:6px}
.tip-title{font-size:13px;font-weight:600;color:var(--tx);margin-bottom:4px}
.tip-text{font-size:12px;color:var(--mu);font-family:var(--fm);line-height:1.5}
.tip-amount{font-size:16px;font-weight:700;color:var(--a2);margin-top:6px;font-family:var(--fm)}
</style>
</head>
<body>
<div class="grid-bg"></div>
<header>
  <div class="hdr">
    <div class="logo">
      <span style="font-size:22px">&#9878;</span>
      <span>TaxCalc <span class="logo-badge">2024-2026</span></span>
    </div>
    <div class="badges">
      <span class="badge live">&#9679; Live Rules</span>
      <span class="badge">IRS Rev. Proc. 2025-32</span>
      <span class="badge upd" id="updBadge" onclick="triggerRefresh()" title="Click to refresh IRS data">&#8635; Auto-Update</span>
    </div>
  </div>
</header>
<main>
  <div class="hero">
    <h1>Federal Tax <span>Refund Calculator</span></h1>
    <p>All 50 states &middot; IRS brackets 2024/2025/2026 &middot; City-level rates &middot; Auto-updates from IRS.gov</p>
    <p style="font-size:11px;color:#44445a;margin-top:4px">Data: """ + source + """ &middot; Last updated: """ + generated + """</p>
  </div>

  <!-- YEAR SELECTOR -->
  <div class="year-bar">
    <button class="yr-btn" data-year="2024" onclick="selectYear(2024)">
      Tax Year 2024
      <span class="yr-tag">Filed April 2025</span>
    </button>
    <button class="yr-btn" data-year="2025" onclick="selectYear(2025)">
      Tax Year 2025
      <span class="yr-tag">Filed April 2026 (current)</span>
    </button>
    <button class="yr-btn active" data-year="2026" onclick="selectYear(2026)">
      Tax Year 2026
      <span class="yr-tag">Filed April 2027</span>
    </button>
  </div>

  <!-- KEY FACTS BAR (updates per year) -->
  <div class="info-bar" id="infoBar"></div>

  <form id="txForm" class="fg" autocomplete="off">
    <div class="col">
      <div class="card">
        <div class="clabel">01 &mdash; Location &amp; Filing</div>
        <div class="field">
          <label>City &amp; State</label>
          <div class="srch">
            <input type="text" id="citySearch" placeholder="Search any US city..." autocomplete="off"/>
            <div class="dd" id="cityDD"></div>
          </div>
          <div class="hint" id="cityHint"></div>
        </div>
        <div class="r2">
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
        <input type="hidden" id="selYear" value="2026"/>
      </div>
      <div class="card">
        <div class="clabel">02 &mdash; Income</div>
        <div id="w2c">
          <div class="w2g">
            <div class="r2">
              <div class="field"><label>W-2 wages / salary</label><input type="text" class="w2w" placeholder="$0"/></div>
              <div class="field"><label>Federal tax withheld</label><input type="text" class="w2h" placeholder="$0"/></div>
            </div>
          </div>
        </div>
        <button type="button" class="ghost" id="addW2">+ Add another W-2 / employer</button>
        <div class="divider"></div>
        <div class="r2">
          <div class="field"><label>Self-employment income</label><input type="text" id="selfE" placeholder="$0"/></div>
          <div class="field"><label>Interest &amp; dividends</label><input type="text" id="intD" placeholder="$0"/></div>
        </div>
        <div class="r2">
          <div class="field"><label>Capital gains (net)</label><input type="text" id="capG" placeholder="$0"/></div>
          <div class="field"><label>Other income (1099-MISC)</label><input type="text" id="othI" placeholder="$0"/></div>
        </div>
        <div class="field"><label>Estimated tax payments (1040-ES)</label><input type="text" id="estP" placeholder="$0"/></div>
      </div>
    </div>
    <div class="col">
      <div class="card">
        <div class="clabel">03 &mdash; Deductions</div>
        <div class="field">
          <label>Deduction method</label>
          <select id="dedType">
            <option value="standard">Standard deduction (recommended)</option>
            <option value="itemized">Itemize my deductions</option>
          </select>
        </div>
        <div id="itemSec" class="hs">
          <div class="sub">Itemized deductions</div>
          <div class="r2">
            <div class="field"><label>Mortgage interest</label><input type="text" id="mortI" placeholder="$0"/></div>
            <div class="field"><label>SALT <span id="saltCapLabel">(capped $10k)</span></label><input type="text" id="saltI" placeholder="$0"/></div>
          </div>
          <div class="r2">
            <div class="field"><label>Charitable contributions</label><input type="text" id="charI" placeholder="$0"/></div>
            <div class="field"><label>Medical (above 7.5% AGI)</label><input type="text" id="medI" placeholder="$0"/></div>
          </div>
        </div>
        <div class="sub">Above-line deductions</div>
        <div class="r2">
          <div class="field"><label>401(k) / 403(b) / IRA</label><input type="text" id="retI" placeholder="$0"/></div>
          <div class="field"><label>HSA contributions</label><input type="text" id="hsaI" placeholder="$0"/></div>
        </div>
        <div class="field"><label>Student loan interest paid</label><input type="text" id="sloI" placeholder="$0"/></div>
      </div>
      <div class="card">
        <div class="clabel">04 &mdash; Credits &amp; Other Taxes</div>
        <div class="r2">
          <div class="field"><label>Child &amp; dependent care expenses</label><input type="text" id="ccI" placeholder="$0"/></div>
          <div class="field"><label>Education expenses (1098-T)</label><input type="text" id="eduI" placeholder="$0"/></div>
        </div>
        <div class="r2">
          <div class="field"><label>State tax withheld (W-2 box 17)</label><input type="text" id="stWH" placeholder="$0"/></div>
          <div class="field"><label>Foreign tax credit</label><input type="text" id="forT" placeholder="$0"/></div>
        </div>
        <div class="field"><label>Additional Medicare / NIIT</label><input type="text" id="niitI" placeholder="$0"/></div>
      </div>
      <button type="submit" class="cbtn" id="calcBtn">
        <span id="btnTxt">Calculate My Refund</span>
        <span class="arr">&#8594;</span>
        <div class="ldr" id="ldr"></div>
      </button>
    </div>
  </form>

  <section class="res" id="resSection" style="display:none">
    <div class="rh">
      <div>
        <p class="rl" id="resLbl">Estimated Federal Refund</p>
        <div class="ra" id="resAmt">$0</div>
        <p class="rs" id="resSub"></p>
      </div>
      <div class="pills">
        <span class="pill" id="pEff"></span>
        <span class="pill" id="pMar"></span>
        <span class="pill" id="pDed"></span>
        <span class="pill" id="pYr"></span>
      </div>
    </div>
    <div class="rtabs">
      <button class="rtab active" data-t="range" onclick="swTab('range')">Refund Range</button>
      <button class="rtab" data-t="federal" onclick="swTab('federal')">Federal Detail</button>
      <button class="rtab" data-t="state" onclick="swTab('state')">State &amp; Local</button>
      <button class="rtab" data-t="range" onclick="swTab('range')">Refund Range</button>
      <button class="rtab" data-t="breakdown" onclick="swTab('breakdown')">Full Breakdown</button>
    </div>
    <div class="rtp active" id="rtp-range">
      <div id="rangePanel"></div>
    </div>
    <div class="rtp" id="rtp-federal">
      <div class="sg" id="statsG"></div>
      <div id="barS"></div>
    </div>
    <div class="rtp" id="rtp-state">
      <div class="stc" id="stCard"></div>
    </div>
    <div class="rtp" id="rtp-range">
      <div class="range-section" id="rangeSection"></div>
    </div>
    <div class="rtp" id="rtp-breakdown">
      <div class="bkt" id="brkT"></div>
    </div>
  </section>

  <p class="disc">For estimation purposes only. Consult a CPA for filing advice. Data from IRS Rev. Proc. 2023-34 (TY2024), 2024-40 + OBBBA (TY2025), 2025-32 + OBBBA (TY2026). 2025 standard deductions updated per OBBBA enacted July 4, 2025.</p>
</main>

<script id="cities-data" type="application/json">""" + cities_json + """</script>
<script id="tax-meta" type="application/json">""" + json.dumps(meta) + """</script>
<script>
'use strict';
const $=id=>document.getElementById(id);
const fmt=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
const pct=n=>n.toFixed(1)+'%';
const CITIES=JSON.parse($('cities-data').textContent);
const META=JSON.parse($('tax-meta').textContent);

// Year info for display
const YEAR_INFO = {
  2024:{std_single:'$14,600',std_mfj:'$29,200',salt:'$10,000 cap',k401:'$23,000',note:'TCJA rates'},
  2025:{std_single:'$15,750',std_mfj:'$31,500',salt:'$10,000 cap',k401:'$23,500',note:'OBBBA updated'},
  2026:{std_single:'$16,100',std_mfj:'$32,200',salt:'$40,400 cap (OBBBA)',k401:'$24,000',note:'Rev. Proc. 2025-32'},
};

let selCity=null, curYear=2026;

function selectYear(y){
  curYear=y;
  $('selYear').value=y;
  document.querySelectorAll('.yr-btn').forEach(b=>b.classList.toggle('active',+b.dataset.year===y));
  updateInfoBar(y);
  // Update SALT cap label
  $('saltCapLabel').textContent = y===2026 ? '(cap $40,400 - OBBBA)' : '(capped $10,000)';
}

function updateInfoBar(y){
  const info=YEAR_INFO[y]||YEAR_INFO[2026];
  $('infoBar').innerHTML=`
    <div class="info-item"><strong>Standard deduction (single):</strong>${info.std_single}</div>
    <div class="info-item"><strong>Standard deduction (MFJ):</strong>${info.std_mfj}</div>
    <div class="info-item ${y===2026?'salt2026':''}"><strong>SALT:</strong>${info.salt}</div>
    <div class="info-item"><strong>401(k) limit:</strong>${info.k401}</div>
    <div class="info-item"><strong>Source:</strong>${info.note}</div>
  `;
}
updateInfoBar(2026);

// City search
$('citySearch').addEventListener('input',function(){
  const q=this.value.toLowerCase().trim(),dd=$('cityDD');
  if(!q){dd.classList.remove('open');return;}
  const m=CITIES.filter(c=>c.city.toLowerCase().startsWith(q)||(c.city+', '+c.state).toLowerCase().includes(q)).slice(0,10);
  if(!m.length){dd.classList.remove('open');return;}
  dd.innerHTML=m.map(c=>`<div class="di" data-idx="${CITIES.indexOf(c)}"><span>${c.city}, ${c.state}</span><span class="dn2">${c.note}</span></div>`).join('');
  dd.querySelectorAll('.di').forEach(el=>{
    el.addEventListener('click',()=>{
      const city=CITIES[+el.dataset.idx];selCity=city;
      $('citySearch').value=city.city+', '+city.state;
      dd.classList.remove('open');
      $('cityHint').textContent=city.state_tax===0?'No state income tax in '+city.state:city.note+' ~ '+city.state_tax+'%';
    });
  });
  dd.classList.add('open');
});
document.addEventListener('click',e=>{if(!e.target.closest('.srch'))$('cityDD').classList.remove('open');});

$('dedType').addEventListener('change',function(){$('itemSec').classList.toggle('vis',this.value==='itemized');});
$('addW2').addEventListener('click',()=>{
  const g=document.createElement('div');g.className='w2g';
  g.innerHTML='<button type="button" class="rmv" onclick="this.parentElement.remove()">x Remove</button><div class="r2"><div class="field"><label>W-2 wages / salary</label><input type="text" class="w2w" placeholder="$0"/></div><div class="field"><label>Federal tax withheld</label><input type="text" class="w2h" placeholder="$0"/></div></div>';
  $('w2c').appendChild(g);
});

function pd(id){const el=typeof id==='string'?$(id):id;return parseFloat((el?.value||'').replace(/[$,\\s]/g,''))||0;}

$('txForm').addEventListener('submit',async function(e){
  e.preventDefault();
  const btn=$('calcBtn');btn.disabled=true;$('btnTxt').textContent='Calculating...';
  $('ldr').style.display='block';btn.querySelector('.arr').style.display='none';
  const wages=Array.from(document.querySelectorAll('.w2w')).reduce((a,i)=>a+pd(i),0);
  const withheld=Array.from(document.querySelectorAll('.w2h')).reduce((a,i)=>a+pd(i),0);
  const payload={
    tax_year:curYear,filing_status:$('filingStatus').value,
    dependents:$('dependents').value,deduction_type:$('dedType').value,
    wages,withheld,self_employ:pd('selfE'),interest:pd('intD'),
    cap_gains:pd('capG'),other_income:pd('othI'),est_payments:pd('estP'),
    state_withheld:pd('stWH'),retirement:pd('retI'),hsa:pd('hsaI'),
    student_loan:pd('sloI'),child_care:pd('ccI'),education:pd('eduI'),
    niit:pd('niitI'),foreign_tax:pd('forT'),
    mortgage_int:pd('mortI'),salt:pd('saltI'),charity:pd('charI'),medical:pd('medI'),
    city_data:selCity||null
  };
  try{
    const res=await fetch('/api/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const d=await res.json();renderResults(d);
  }catch(err){alert('Calculation error - please try again.');console.error(err);}
  finally{btn.disabled=false;$('btnTxt').textContent='Recalculate';$('ldr').style.display='none';btn.querySelector('.arr').style.display='inline';}
});


function renderRange(d){
  if(!d.range) return;
  const R=d.range;
  const isNeg=v=>v<0;
  const fmtR=v=>isNeg(v)?'-'+fmt(Math.abs(v)):fmt(v);
  const cards=[
    {key:'minimum',cls:'danger',icon:'&#9660;'},
    {key:'safe',cls:'amber',icon:'&#9632;'},
    {key:'estimated',cls:'blue',icon:'&#9654;',star:'Best Estimate'},
    {key:'maximum',cls:'green',icon:'&#9650;'},
  ];
  const amounts=[R.minimum.amount,R.safe.amount,R.estimated.amount,R.maximum.amount];
  const allNeg=amounts.every(a=>a<0);
  const mn=Math.min(...amounts), mx=Math.max(...amounts);
  const span=mx-mn||1;
  // Cards
  const cardsHtml=cards.map(c=>{
    const r=R[c.key];
    const neg=isNeg(r.amount);
    return `<div class="rc ${c.cls}">
      ${c.star?'<span class="rc-star">'+c.star+'</span>':''}
      <div class="rc-badge">${c.icon} ${r.label}</div>
      <div class="rc-amount ${neg?'ow':''}">${neg?'-':'+'}${fmt(Math.abs(r.amount))}</div>
      <div class="rc-conf">Confidence: ${r.confidence}</div>
      <div class="rc-desc">${r.description}</div>
    </div>`;
  }).join('');
  // Visual bar
  const pct=v=>Math.max(2,Math.min(98,Math.round((v-mn)/span*100)));
  const vizHtml=`<div class="range-viz">
    <div class="range-viz-lbl"><span>Min: ${fmtR(R.minimum.amount)}</span><span>Max: ${fmtR(R.maximum.amount)}</span></div>
    <div class="range-bar">
      <div class="range-bar-fill" style="left:${pct(R.minimum.amount)}%;right:${100-pct(R.maximum.amount)}%"></div>
    </div>
    <div class="range-pins">
      ${[{k:'minimum',col:'#fc8181',lbl:'Min'},{k:'safe',col:'#f6ad55',lbl:'Safe'},{k:'estimated',col:'#63b3ed',lbl:'Estimate'},{k:'maximum',col:'#68d391',lbl:'Max'}]
        .map(m=>`<div class="pin" style="left:${pct(R[m.k].amount)}%">
          <div class="pin-dot" style="background:${m.col}"></div>
          <div class="pin-lbl">${m.lbl}<br>${fmtR(R[m.k].amount)}</div>
        </div>`).join('')}
    </div>
  </div>`;
  // Alerts
  let alerts='';
  if(d.underpayment_risk){
    alerts+=`<div class="alert warn"><span class="alert-icon">&#9888;</span><div class="alert-body">
      <strong>Underpayment Penalty Risk</strong>
      You may owe an IRS underpayment penalty (~${fmt(d.penalty_estimate)}). The IRS requires you to pay at least 90% of your tax due during the year. Consider adjusting your withholding.
    </div></div>`;
  } else {
    alerts+=`<div class="alert ok"><span class="alert-icon">&#10003;</span><div class="alert-body">
      <strong>Safe Harbor Met</strong>
      Your withholding covers 90%+ of your tax liability. No underpayment penalty applies.
    </div></div>`;
  }
  alerts+=`<div class="alert info"><span class="alert-icon">&#8505;</span><div class="alert-body">
    <strong>How to read this range</strong>
    Safe amount (${fmtR(R.safe.amount)}) = what you can count on with 90% confidence. Best estimate (${fmtR(R.estimated.amount)}) = most likely outcome. The difference between min and max reflects documentation risk and potential missed deductions.
  </div></div>`;
  $('rangeSection').innerHTML=`
    <div class="range-title">Refund Range &mdash; Min to Max</div>
    <div class="range-cards">${cardsHtml}</div>
    ${vizHtml}
    ${alerts}`;
}

function renderResults(d){
  const sec=$('resSection');sec.style.display='block';
  setTimeout(()=>sec.scrollIntoView({behavior:'smooth',block:'start'}),80);
  const isR=d.result>=0;
  $('resLbl').textContent=isR?'Estimated Federal Refund':'Estimated Amount Owed';
  $('resAmt').textContent=fmt(Math.abs(d.result));
  $('resAmt').className='ra '+(isR?'rf':'ow');
  $('resSub').textContent=(d.using_standard?'Standard':'Itemized')+' deduction | '+d._data_source;
  $('pEff').textContent='Effective: '+pct(d.effective_rate);
  $('pMar').textContent='Marginal: '+d.marginal_rate+'%';
  $('pDed').textContent='Deduction: '+fmt(d.deduction);
  $('pYr').textContent='Tax Year '+d._tax_year;
  $('statsG').innerHTML=[
    {l:'Gross income',v:fmt(d.gross_income),c:''},
    {l:'AGI',v:fmt(d.agi),c:'acc'},
    {l:'Taxable income',v:fmt(d.taxable_income),c:''},
    {l:'Federal tax',v:fmt(d.fed_tax),c:'neg'},
    {l:'SE tax',v:fmt(d.se_tax),c:d.se_tax>0?'neg':''},
    {l:'Total credits',v:fmt(d.total_credits),c:'pos'},
    {l:'Tax liability',v:fmt(d.total_tax),c:'neg'},
    {l:'Total payments',v:fmt(d.total_payments),c:'pos'},
  ].map(s=>`<div class="sc"><div class="sl">${s.l}</div><div class="sv ${s.c}">${s.v}</div></div>`).join('');
  const mx=Math.max(d.gross_income,1);
  $('barS').innerHTML=[
    {l:'Gross income',v:d.gross_income,col:'#63b3ed'},
    {l:'AGI',v:d.agi,col:'#76e4f7'},
    {l:'Taxable income',v:d.taxable_income,col:'#9f7aea'},
    {l:'Federal tax',v:d.fed_tax,col:'#fc8181'},
    {l:'Credits',v:d.total_credits,col:'#68d391'},
  ].map(b=>`<div class="br"><span class="brl">${b.l}</span><div class="bt"><div class="bf" style="width:${Math.round(b.v/mx*100)}%;background:${b.col}"></div></div><span class="bv">${fmt(b.v)}</span></div>`).join('');
  const rows=[
    {h:'Income'},{l:'Gross income',v:d.gross_income,c:'neutral'},
    {l:'Above-line deductions',v:d.above_line,c:'neg'},
    {l:'AGI',v:d.agi,c:'acc'},
    {h:'Deductions & Tax'},
    {l:(d.using_standard?'Standard':'Itemized')+' deduction',v:d.deduction,c:'neg'},
    {l:'Taxable income',v:d.taxable_income,c:'neutral'},
    {l:'Federal income tax',v:d.fed_tax,c:'neg'},
    {l:'Self-employment tax',v:d.se_tax,c:d.se_tax>0?'neg':'neutral'},
    {h:'Credits'},
    {l:'Child Tax Credit',v:d.ctc_total,c:'pos'},{l:'Earned Income Credit',v:d.eic,c:'pos'},
    {l:'Education credit',v:d.edu_credit,c:'pos'},{l:'Total credits',v:d.total_credits,c:'pos'},
    {h:'Payments'},
    {l:'Federal withheld',v:d.withheld,c:'pos'},{l:'Est. payments',v:d.est_payments,c:'pos'},
    {l:'Total payments',v:d.total_payments,c:'pos'},{l:'Total tax liability',v:d.total_tax,c:'neg'},
  ];
  $('brkT').innerHTML=rows.map(r=>{
    if(r.h)return`<div class="brow hdr"><span class="blbl hdr">${r.h}</span></div>`;
    return`<div class="brow"><span class="blbl">${r.l}</span><span class="bval ${r.c}">${(r.c==='neg'&&r.v>0?'-':'')}${fmt(r.v)}</span></div>`;
  }).join('')+`<div class="brow tot"><span class="blbl">${isR?'Estimated refund':'Amount owed'}</span><span class="bval ${isR?'pos':'neg'}">${fmt(Math.abs(d.result))}</span></div>`;
  if(selCity&&d.state&&Object.keys(d.state).length){
    const s=d.state,city=selCity,sr=s.state_refund>=0;
    $('stCard').innerHTML=`<div class="stt">${city.city}, ${city.state}</div><div class="stn">${city.note}</div>`+
    [['State taxable income',fmt(s.state_agi),'neutral'],
     ['State income tax rate',city.state_tax>0?city.state_tax+'%':'None (0%)','neutral'],
     ['Estimated state tax',city.state_tax>0?fmt(s.state_tax_amt):'$0','neg'],
     ['City / local tax',city.city_tax>0?city.city_tax+'% -> '+fmt(s.city_tax_amt):'None',city.city_tax>0?'neg':'neutral'],
     ['State withheld',fmt(pd('stWH')),'neutral'],
     ['State + local combined',fmt(s.combined),'neg'],
     [sr?'State refund':'State owed',fmt(Math.abs(s.state_refund)),sr?'pos':'neg'],
    ].map(([l,v,c])=>`<div class="brow"><span class="blbl">${l}</span><span class="bval ${c}">${v}</span></div>`).join('');
  }else{$('stCard').innerHTML='<p class="nc">Select a city above to see state & local tax details.</p>';}
  swTab('range');
  renderRange(d);
}
function swTab(n){
  document.querySelectorAll('.rtab').forEach(t=>t.classList.toggle('active',t.dataset.t===n));
  document.querySelectorAll('.rtp').forEach(t=>t.classList.toggle('active',t.id==='rtp-'+n));
}

function renderRange(d){
  const sc=d.scenarios||{};
  const isRef=v=>v>=0;
  const fmtAmt=v=>v>=0?'+ '+fmt(v):fmt(v).replace('$','-$');

  // Build 4 scenario cards
  const cards=[
    {k:'min',icon:'&#9660;',cls:'min'},
    {k:'safe',icon:'&#128737;',cls:'safe recommended'},
    {k:'base',icon:'&#8776;',cls:'base'},
    {k:'max',icon:'&#9650;',cls:'max'},
  ];

  let html='<div class="range-hero">';
  cards.forEach(({k,icon,cls})=>{
    const s=sc[k]||{};
    const amt=s.amount||0;
    html+=`<div class="rcard ${cls}">
      <div class="rcard-icon">${icon}</div>
      <div class="rcard-label">${s.label||k}</div>
      <div class="rcard-amount">${isRef(amt)?'+':'-'}${fmt(Math.abs(amt))}</div>
      <div class="rcard-desc">${s.description||''}</div>
      <span class="rcard-conf">${s.confidence||''}</span>
    </div>`;
  });
  html+='</div>';

  // Range bar
  const amounts=[sc.minimum?.amount||0,sc.safe?.amount||0,sc.base?.amount||0,sc.maximum?.amount||0];
  const minV=Math.min(...amounts), maxV=Math.max(...amounts);
  const span=Math.max(maxV-minV,1);
  const pct=v=>Math.round((v-minV)/span*80+10); // 10-90% range

  html+=`<div class="range-bar-wrap">
    <div class="range-bar-title">Refund range visualizer</div>
    <div class="rbar-track">
      <div class="rbar-fill" style="left:${pct(amounts[0])}%;right:${100-pct(amounts[3])}%;background:linear-gradient(90deg,#fc8181,#f6ad55,#63b3ed,#68d391)"></div>
      ${amounts.map((v,i)=>{
        const labels=['Min','Safe','Base','Max'];
        const colors=['#fc8181','#f6ad55','#63b3ed','#68d391'];
        return `<span class="rbar-marker" style="left:${pct(v)}%;color:${colors[i]}">${labels[i]}<br>${fmt(Math.abs(v)).replace("$","")</span>`;
      }).join('')}
    </div>
  </div>`;

  // Risk alerts
  if(d.underpayment_risk){
    html+=`<div class="alert-box warn">
      <div class="alert-icon">&#9888;</div>
      <div class="alert-body">
        <div class="alert-title">Underpayment Penalty Risk</div>
        <div class="alert-text">You may owe <strong>${fmt(Math.abs(d.result))}</strong> and could face an IRS underpayment penalty of ~<strong>${fmt(d.penalty_est)}</strong>. You paid less than 90% of your tax liability through withholding. Increase your W-4 withholding immediately.</div>
      </div>
    </div>`;
  } else if(d.result>0){
    html+=`<div class="alert-box good">
      <div class="alert-icon">&#10003;</div>
      <div class="alert-body">
        <div class="alert-title">No Underpayment Penalty Risk</div>
        <div class="alert-text">Your withholding covers your full tax liability. You are on track for a refund with no IRS penalties.</div>
      </div>
    </div>`;
  } else {
    html+=`<div class="alert-box info">
      <div class="alert-icon">&#8505;</div>
      <div class="alert-body">
        <div class="alert-title">You Owe — Review W-4 Withholding</div>
        <div class="alert-text">Add <strong>$${d.w4_adjustment}/paycheck</strong> extra withholding on your W-4 to avoid owing next year. Recommended annual withholding: <strong>${fmt(d.recommended_withholding*26)}</strong></div>
      </div>
    </div>`;
  }

  // Optimization tips
  const tips=[];
  if(d.extra_retirement_room>0){
    tips.push({icon:'&#128176;',title:'Boost 401(k) / IRA',text:'You have room to contribute more to your retirement account this year.',amount:'Up to $'+d.extra_retirement_room.toLocaleString()+' more tax-deferred'});
  }
  if(d.extra_hsa_room>0){
    tips.push({icon:'&#127973;',title:'Fund your HSA',text:'Health Savings Account contributions are triple tax-advantaged (deductible, grows tax-free, tax-free withdrawals for medical).',amount:'Up to $'+d.extra_hsa_room.toLocaleString()+' more deductible'});
  }
  if(d.marginal_rate>=22){
    tips.push({icon:'&#127968;',title:'Mortgage Interest Deduction',text:'At your tax bracket, mortgage interest can significantly reduce your taxable income if you own a home.',amount:'Could save '+d.marginal_rate+'% of interest paid'});
  }
  if(d.eic===0&&d.result<0){
    tips.push({icon:'&#128218;',title:'Check Earned Income Credit',text:'Verify EIC eligibility - income limits and dependent rules may have changed for '+d._tax_year+'.',amount:'Up to $8,231 refundable credit'});
  }
  if(d.marginal_rate>=24){
    tips.push({icon:'&#128200;',title:'Consider Tax-Loss Harvesting',text:'If you have investment losses, they can offset capital gains and up to $3,000 of ordinary income per year.',amount:'Reduce taxable income by up to $3,000'});
  }
  tips.push({icon:'&#128203;',title:'Safe Harbor Rule',text:'Pay at least 100% of last year's tax (110% if income >$150k) to guarantee no underpayment penalty.',amount:'Recommended: '+fmt(d.recommended_withholding)+'/paycheck'});

  if(tips.length>0){
    html+=`<div style="font-family:var(--fm);font-size:11px;color:var(--mu);text-transform:uppercase;letter-spacing:.8px;margin:1rem 0 .75rem">Tax optimization tips</div>`;
    html+='<div class="tips-grid">';
    tips.slice(0,6).forEach(t=>{
      html+=`<div class="tip-card">
        <div class="tip-icon">${t.icon}</div>
        <div class="tip-title">${t.title}</div>
        <div class="tip-text">${t.text}</div>
        <div class="tip-amount">${t.amount}</div>
      </div>`;
    });
    html+='</div>';
  }

  $('rangePanel').innerHTML=html;
}

window.swTab=swTab;

async function triggerRefresh(){
  const b=$('updBadge');
  b.textContent='Refreshing...';
  try{
    const r=await fetch('/api/refresh-irs-data',{method:'POST'});
    const d=await r.json();
    b.textContent=d.status==='ok'?'Updated!':'Up to date';
    setTimeout(()=>{b.textContent='Auto-Update';},3000);
  }catch(e){b.textContent='Auto-Update';}
}
</script>
</body>
</html>"""

# ── Flask routes ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    meta = TAX_DATA.get("_meta", {})
    return Response(build_html(json.dumps(CITIES), meta), mimetype="text/html")

@app.route("/api/cities")
def api_cities():
    q = request.args.get("q","").lower()
    if not q: return jsonify([])
    return jsonify([c for c in CITIES if q in c["city"].lower() or q in (c["city"]+", "+c["state"]).lower()][:12])

@app.route("/api/tax-data")
def api_tax_data():
    year = int(request.args.get("year",2026))
    yd = get_year_data(year)
    return jsonify({"year":year,"source":yd.get("source"),"source_url":yd.get("source_url"),
                    "standard_deductions":yd.get("standard_deductions"),"salt_cap":yd.get("salt_cap"),
                    "brackets_single":yd.get("brackets",{}).get("single"),
                    "ctc":yd.get("ctc"),"k401_limit":yd.get("k401_limit")})

@app.route("/api/refresh-irs-data", methods=["POST"])
def refresh_irs_data():
    import subprocess, sys
    try:
        result = subprocess.run([sys.executable, str(Path(__file__).parent/"fetch_irs_data.py")],
                                capture_output=True, text=True, timeout=20)
        global TAX_DATA
        TAX_DATA = load_tax_data()
        return jsonify({"status":"ok","years":list(TAX_DATA["years"].keys())})
    except Exception as e:
        return jsonify({"status":"ok","note":"Using cached data","error":str(e)})

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    def p(k):
        try: return float(str(data.get(k,0)).replace(",","").replace("$","")) or 0.0
        except: return 0.0

    year = int(data.get("tax_year",2026))
    yd = get_year_data(year)
    status = data.get("filing_status","single")
    deps = int(data.get("dependents",0))
    brackets = yd["brackets"].get(status, yd["brackets"]["single"])

    wages=p("wages"); withheld=p("withheld"); self_employ=p("self_employ")
    interest=p("interest"); cap_gains=p("cap_gains"); other_income=p("other_income")
    est_payments=p("est_payments"); state_withheld=p("state_withheld")
    retirement=p("retirement"); hsa=p("hsa"); student_loan=p("student_loan")
    child_care=p("child_care"); education=p("education"); niit=p("niit")
    foreign_tax=p("foreign_tax"); mortgage_int=p("mortgage_int")
    salt_input=p("salt"); charity=p("charity"); medical=p("medical")
    deduction_type = data.get("deduction_type","standard")

    se_net = self_employ * yd["se_net_earnings_rate"]
    se_tax = se_net * yd["se_rate"] if self_employ > 400 else 0.0
    se_deduction = se_tax * yd["se_deductible_fraction"]
    gross_income = wages + self_employ + interest + cap_gains + other_income
    above_line = retirement + hsa + student_loan + se_deduction
    agi = max(0.0, gross_income - above_line)

    std_ded = yd["standard_deductions"].get(status,16100)
    salt_cap = yd.get("salt_cap",10000)
    salt_capped = min(salt_input, salt_cap)
    itemized = mortgage_int + salt_capped + charity + medical
    if deduction_type=="itemized":
        deduction=max(itemized,std_ded); using_standard=itemized<=std_ded
    else:
        deduction=std_ded; using_standard=True

    taxable_income = max(0.0, agi - deduction)
    fed_tax = calc_tax(taxable_income, brackets)
    mrate = marginal(taxable_income, brackets)
    effective = (fed_tax/gross_income*100) if gross_income>0 else 0.0

    ctc = calc_ctc(deps, agi, status, yd["ctc"])
    eic = calc_eic(wages+self_employ, deps, status, yd["eic"])
    cdcc = yd.get("cdcc",{})
    cdcc_max = cdcc.get("max_expenses_1",3000) if deps==1 else cdcc.get("max_expenses_2plus",6000)
    child_care_credit = min(child_care,cdcc_max)*cdcc.get("rate",0.20) if deps>0 else 0.0
    edu_credit = min(education, yd.get("aoc_max",2500))
    edu_ref = edu_credit * yd.get("aoc_refundable_pct",0.40)
    non_ref = min(fed_tax+se_tax, ctc["total"]-ctc["refundable"]+child_care_credit+(edu_credit-edu_ref)+foreign_tax)
    total_tax = max(0.0, fed_tax+se_tax-non_ref) + niit
    total_payments = withheld + est_payments + ctc["refundable"] + eic + edu_ref
    total_credits = ctc["total"] + eic + child_care_credit + edu_credit + foreign_tax
    result = total_payments - total_tax

    state_result = {}
    city_data = data.get("city_data") or {}
    if city_data:
        sr=city_data.get("state_tax",0)/100; cr=city_data.get("city_tax",0)/100
        sagi=max(0.0, agi-(deduction*0.5 if sr>0 else 0))
        stax=round(sagi*sr); ctax=round(agi*cr)
        state_result={"state_agi":round(sagi),"state_tax_amt":stax,"city_tax_amt":ctax,
                      "state_refund":round(state_withheld)-stax,"combined":stax+ctax}

    # ── Refund Range Engine ────────────────────────────────────────────────────
    # MINIMUM: IRS could disallow certain deductions, audit adjustments, penalties
    # Assumptions: no misc deductions, strict interpretation, +2% audit variance
    min_deduction = std_ded  # always use standard in minimum scenario
    min_taxable = max(0.0, agi - min_deduction)
    min_fed_tax = calc_tax(min_taxable, brackets)
    # Minimum: disallow 10% of credits (documentation issues), add 2% income variance
    min_credits = total_credits * 0.90
    min_non_ref = min(min_fed_tax+se_tax, (ctc["total"]-ctc["refundable"])*0.90+child_care_credit*0.90+(edu_credit-edu_ref)*0.90+foreign_tax)
    min_total_tax = max(0.0, min_fed_tax+se_tax-min_non_ref) + niit
    # Minimum payments: assume 5% of withheld was miscalculated
    min_refundable = (ctc["refundable"] + eic + edu_ref) * 0.90
    min_payments = withheld * 0.97 + est_payments + min_refundable
    minimum_result = round(min_payments - min_total_tax)

    # MAXIMUM: Best-case — all deductions accepted, all credits maximized
    # If itemized > standard, use itemized; also add any missed deductions
    max_deduction = max(deduction, itemized)
    # Add 5% bonus for commonly missed deductions (home office, vehicle, etc.)
    if self_employ > 0:
        max_deduction += self_employ * 0.05  # commonly missed SE deductions
    max_taxable = max(0.0, agi - max_deduction)
    max_fed_tax = calc_tax(max_taxable, brackets)
    # Maximum: full credits + assume withheld could be slightly higher (rounding)
    max_non_ref = min(max_fed_tax+se_tax, ctc["total"]-ctc["refundable"]+child_care_credit+(edu_credit-edu_ref)+foreign_tax)
    max_total_tax = max(0.0, max_fed_tax+se_tax-max_non_ref) + niit
    max_payments = withheld + est_payments + ctc["refundable"] + eic + edu_ref
    maximum_result = round(max_payments - max_total_tax)

    # SAFE AMOUNT: Conservative estimate — what you can count on with high confidence
    # Uses standard deduction, verified credits only (refundable ones), no gray-area items
    safe_deduction = std_ded
    safe_taxable = max(0.0, agi - safe_deduction)
    safe_fed_tax = calc_tax(safe_taxable, brackets)
    # Only include well-documented credits
    safe_credits_nonref = min(safe_fed_tax+se_tax, ctc["total"]-ctc["refundable"]+foreign_tax)
    safe_total_tax = max(0.0, safe_fed_tax+se_tax-safe_credits_nonref) + niit
    # Safe payments: only confirmed withholding + solid refundable credits
    safe_refundable = ctc["refundable"] + eic  # exclude edu (needs docs)
    safe_payments = withheld + est_payments + safe_refundable
    safe_result = round(safe_payments - safe_total_tax)

    # Ensure logical ordering: min <= safe <= estimated <= max
    minimum_result = min(minimum_result, result)
    safe_result = max(minimum_result, min(safe_result, result))
    maximum_result = max(maximum_result, result)

    # Build range explanation for each scenario
    range_notes = {
        "minimum": {
            "amount": minimum_result,
            "label": "Minimum (Conservative)",
            "description": "Worst-case: IRS questions some deductions/credits, minor audit adjustments, or documentation gaps reduce your refund.",
            "confidence": "20%",
            "color": "danger"
        },
        "safe": {
            "amount": safe_result,
            "label": "Safe Amount",
            "description": "High-confidence estimate based only on verified withholding and well-documented credits. You can count on this.",
            "confidence": "90%",
            "color": "amber"
        },
        "estimated": {
            "amount": result,
            "label": "Best Estimate",
            "description": "Most likely refund based on all your inputs at face value — this is what you should expect if everything is filed correctly.",
            "confidence": "70%",
            "color": "accent"
        },
        "maximum": {
            "amount": maximum_result,
            "label": "Maximum Possible",
            "description": "Best-case: all deductions accepted, any missed deductions claimed, and commonly overlooked credits applied.",
            "confidence": "15%",
            "color": "success"
        }
    }

    # Underpayment penalty warning (IRS requires 90% of tax paid or 100% of prior year)
    underpayment_threshold = total_tax * 0.90
    underpayment_risk = total_payments < underpayment_threshold
    penalty_estimate = round(max(0, (underpayment_threshold - total_payments) * 0.08)) if underpayment_risk else 0

    # Safe harbor check
    safe_harbor_met = total_payments >= total_tax * 0.90

    return jsonify({"gross_income":round(gross_income),"agi":round(agi),
        "taxable_income":round(taxable_income),"deduction":round(deduction),
        "using_standard":using_standard,"above_line":round(above_line),
        "fed_tax":round(fed_tax),"se_tax":round(se_tax),"total_tax":round(total_tax),
        "marginal_rate":mrate,"effective_rate":round(effective,1),
        "ctc_total":round(ctc["total"]),"ctc_refundable":round(ctc["refundable"]),
        "eic":round(eic),"child_care_credit":round(child_care_credit),
        "edu_credit":round(edu_credit),"total_credits":round(total_credits),
        "withheld":round(withheld),"est_payments":round(est_payments),
        "total_payments":round(total_payments),"result":round(result),
        "range": range_notes,
        "underpayment_risk": underpayment_risk,
        "penalty_estimate": penalty_estimate,
        "safe_harbor_met": safe_harbor_met,
        "state":state_result,"status":status,"_tax_year":year,
        "_data_source":yd.get("source","IRS Rev. Proc.")})

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    debug = os.environ.get("FLASK_ENV","development")=="development"
    print("\n  IRS Tax Calculator -> http://127.0.0.1:%d\n" % port)
    app.run(host="0.0.0.0", port=port, debug=debug)
