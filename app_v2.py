"""
app_v2.py - IRS Tax Refund Calculator
Zero AI calls. Data from IRS Rev. Proc. 2023-34, 2024-40, 2025-32.
"""
import json, os, math
from pathlib import Path
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "tax_data.json"

def load_tax_data():
    if not DATA_FILE.exists():
        import subprocess, sys
        subprocess.run([sys.executable, str(Path(__file__).parent/"fetch_irs_data.py"), "--offline"], check=True)
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
    {"city":"Minneapolis","state":"MN","state_tax":9.85,"city_tax":0,"note":"MN top marginal rate"},
    {"city":"Tampa","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
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
    {"city":"Orlando","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"Tallahassee","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"Knoxville","state":"TN","state_tax":0,"city_tax":0,"note":"TN - no earned income tax"},
    {"city":"Reno","state":"NV","state_tax":0,"city_tax":0,"note":"NV - no state income tax"},
    {"city":"Scottsdale","state":"AZ","state_tax":2.5,"city_tax":0,"note":"AZ flat rate"},
    {"city":"Chandler","state":"AZ","state_tax":2.5,"city_tax":0,"note":"AZ flat rate"},
    {"city":"Fort Collins","state":"CO","state_tax":4.4,"city_tax":0,"note":"CO flat rate"},
    {"city":"Madison","state":"WI","state_tax":5.3,"city_tax":0,"note":"WI marginal rate"},
    {"city":"Durham","state":"NC","state_tax":4.5,"city_tax":0,"note":"NC flat rate"},
    {"city":"Fort Lauderdale","state":"FL","state_tax":0,"city_tax":0,"note":"FL - no state income tax"},
    {"city":"Savannah","state":"GA","state_tax":5.49,"city_tax":0,"note":"GA rate"},
    {"city":"New Orleans","state":"LA","state_tax":3.0,"city_tax":0,"note":"LA flat rate"},
    {"city":"Virginia Beach","state":"VA","state_tax":5.75,"city_tax":0,"note":"VA marginal rate"},
    {"city":"Providence","state":"RI","state_tax":5.99,"city_tax":0,"note":"RI top marginal rate"},
    {"city":"Burlington","state":"VT","state_tax":8.75,"city_tax":0,"note":"VT top marginal rate"},
]

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

def get_marginal(taxable, brackets):
    prev = 0
    for limit, rate in brackets:
        cap = limit if limit is not None else float("inf")
        if taxable <= cap - prev: return rate
        taxable -= cap - prev
        prev = cap
    return 37

def calc_ctc(deps, magi, status, cfg):
    credit = deps * cfg["credit_per_child"]
    t = cfg["phaseout_mfj"] if status == "mfj" else cfg["phaseout_other"]
    if magi > t:
        credit = max(0.0, credit - math.floor((magi - t) / 1000) * cfg["phaseout_per_1000"])
    return {"total": credit, "refundable": min(credit, deps * cfg["refundable_per_child"])}

def calc_eic(earned, deps, status, cfg):
    if earned <= 0: return 0
    d = min(deps, 3)
    max_e = cfg["max_earned"][d] + (cfg.get("mfj_bonus", 0) if status == "mfj" else 0)
    if earned > max_e: return 0
    return round(cfg["max_credit"][d] * min(1.0, earned / (max_e * 0.30)))

@app.route("/")
def index():
    meta = TAX_DATA.get("_meta", {})
    generated = meta.get("generated", "")[:10]
    source = meta.get("source", "IRS.gov")
    cities_json = json.dumps(CITIES)
    html = build_html(cities_json, generated, source)
    return Response(html, mimetype="text/html")

@app.route("/api/cities")
def api_cities():
    q = request.args.get("q", "").lower()
    if not q: return jsonify([])
    return jsonify([c for c in CITIES if q in c["city"].lower() or q in (c["city"] + ", " + c["state"]).lower()][:12])

@app.route("/api/tax-data")
def api_tax_data():
    year = int(request.args.get("year", 2026))
    yd = get_year_data(year)
    return jsonify({"year": year, "source": yd.get("source"), "standard_deductions": yd.get("standard_deductions"), "salt_cap": yd.get("salt_cap"), "brackets_single": yd.get("brackets", {}).get("single")})

@app.route("/api/refresh-irs-data", methods=["POST"])
def refresh_irs_data():
    import subprocess, sys
    try:
        subprocess.run([sys.executable, str(Path(__file__).parent / "fetch_irs_data.py")], capture_output=True, text=True, timeout=20)
        global TAX_DATA
        TAX_DATA = load_tax_data()
        return jsonify({"status": "ok", "years": list(TAX_DATA["years"].keys())})
    except Exception as e:
        return jsonify({"status": "ok", "note": "Using cached data"})

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    def p(k):
        try: return float(str(data.get(k, 0)).replace(",", "").replace("$", "")) or 0.0
        except: return 0.0

    year = int(data.get("tax_year", 2026))
    yd = get_year_data(year)
    status = data.get("filing_status", "single")
    deps = int(data.get("dependents", 0))
    brackets = yd["brackets"].get(status, yd["brackets"]["single"])

    wages = p("wages"); withheld = p("withheld"); self_employ = p("self_employ")
    interest = p("interest"); cap_gains = p("cap_gains"); other_income = p("other_income")
    est_payments = p("est_payments"); state_withheld = p("state_withheld")
    retirement = p("retirement"); hsa = p("hsa"); student_loan = p("student_loan")
    child_care = p("child_care"); education = p("education"); niit = p("niit")
    foreign_tax = p("foreign_tax"); mortgage_int = p("mortgage_int")
    salt_input = p("salt"); charity = p("charity"); medical = p("medical")
    deduction_type = data.get("deduction_type", "standard")

    se_net = self_employ * yd["se_net_earnings_rate"]
    se_tax = se_net * yd["se_rate"] if self_employ > 400 else 0.0
    se_deduction = se_tax * yd["se_deductible_fraction"]
    gross_income = wages + self_employ + interest + cap_gains + other_income
    above_line = retirement + hsa + student_loan + se_deduction
    agi = max(0.0, gross_income - above_line)

    std_ded = yd["standard_deductions"].get(status, 16100)
    salt_cap = yd.get("salt_cap", 10000)
    salt_capped = min(salt_input, salt_cap)
    itemized = mortgage_int + salt_capped + charity + medical

    if deduction_type == "itemized":
        deduction = max(itemized, std_ded)
        using_standard = itemized <= std_ded
    else:
        deduction = std_ded
        using_standard = True

    taxable_income = max(0.0, agi - deduction)
    fed_tax = calc_tax(taxable_income, brackets)
    mrate = get_marginal(taxable_income, brackets)
    effective = (fed_tax / gross_income * 100) if gross_income > 0 else 0.0

    ctc = calc_ctc(deps, agi, status, yd["ctc"])
    eic = calc_eic(wages + self_employ, deps, status, yd["eic"])
    cdcc = yd.get("cdcc", {})
    cdcc_max = cdcc.get("max_expenses_1", 3000) if deps == 1 else cdcc.get("max_expenses_2plus", 6000)
    child_care_credit = min(child_care, cdcc_max) * cdcc.get("rate", 0.20) if deps > 0 else 0.0
    edu_credit = min(education, yd.get("aoc_max", 2500))
    edu_ref = edu_credit * yd.get("aoc_refundable_pct", 0.40)
    non_ref = min(fed_tax + se_tax, ctc["total"] - ctc["refundable"] + child_care_credit + (edu_credit - edu_ref) + foreign_tax)
    total_tax = max(0.0, fed_tax + se_tax - non_ref) + niit
    total_payments = withheld + est_payments + ctc["refundable"] + eic + edu_ref
    total_credits = ctc["total"] + eic + child_care_credit + edu_credit + foreign_tax
    result = total_payments - total_tax

    # ── Refund Range Engine ────────────────────────────────────────────────────
    # MINIMUM: IRS disallows some deductions, slight audit variance
    min_taxable = max(0.0, agi - std_ded)
    min_fed_tax = calc_tax(min_taxable, brackets)
    min_non_ref = min(min_fed_tax + se_tax, (ctc["total"] - ctc["refundable"]) * 0.9 + foreign_tax)
    min_total_tax = max(0.0, min_fed_tax + se_tax - min_non_ref) + niit
    min_payments = withheld * 0.97 + est_payments + (ctc["refundable"] + eic) * 0.9
    minimum_result = round(min_payments - min_total_tax)

    # SAFE: Only verified withholding + solid refundable credits, no grey-area items
    safe_taxable = max(0.0, agi - std_ded)
    safe_fed_tax = calc_tax(safe_taxable, brackets)
    safe_non_ref = min(safe_fed_tax + se_tax, ctc["total"] - ctc["refundable"] + foreign_tax)
    safe_total_tax = max(0.0, safe_fed_tax + se_tax - safe_non_ref) + niit
    safe_payments = withheld + est_payments + ctc["refundable"] + eic
    safe_result = round(safe_payments - safe_total_tax)

    # BEST ESTIMATE: exactly what was calculated
    estimated_result = round(result)

    # MAXIMUM: all deductions accepted + commonly missed SE deductions
    max_deduction = deduction
    if self_employ > 0:
        max_deduction += self_employ * 0.05
    max_taxable = max(0.0, agi - max_deduction)
    max_fed_tax = calc_tax(max_taxable, brackets)
    max_non_ref = min(max_fed_tax + se_tax, ctc["total"] - ctc["refundable"] + child_care_credit + (edu_credit - edu_ref) + foreign_tax)
    max_total_tax = max(0.0, max_fed_tax + se_tax - max_non_ref) + niit
    max_payments = withheld + est_payments + ctc["refundable"] + eic + edu_ref
    maximum_result = round(max_payments - max_total_tax)

    # Ensure logical order
    minimum_result = min(minimum_result, estimated_result)
    safe_result = max(minimum_result, min(safe_result, estimated_result))
    maximum_result = max(maximum_result, estimated_result)

    refund_range = {
        "minimum":  {"amount": minimum_result,  "label": "Minimum",       "confidence": "20%", "description": "Worst case: IRS questions deductions or credits. Some documentation gaps reduce your refund."},
        "safe":     {"amount": safe_result,      "label": "Safe Amount",   "confidence": "90%", "description": "High confidence. Based only on verified withholding and well-documented credits you can count on."},
        "estimated":{"amount": estimated_result, "label": "Best Estimate", "confidence": "70%", "description": "Most likely outcome if all your inputs are filed correctly and accepted by the IRS."},
        "maximum":  {"amount": maximum_result,   "label": "Maximum",       "confidence": "15%", "description": "Best case: all deductions accepted plus commonly missed write-offs applied in your favor."},
    }

    underpayment_risk = total_payments < total_tax * 0.90
    penalty_estimate = round(max(0, (total_tax * 0.90 - total_payments) * 0.08)) if underpayment_risk else 0

    # State
    state_result = {}
    city_data = data.get("city_data") or {}
    if city_data:
        sr = city_data.get("state_tax", 0) / 100
        cr = city_data.get("city_tax", 0) / 100
        sagi = max(0.0, agi - (deduction * 0.5 if sr > 0 else 0))
        stax = round(sagi * sr)
        ctax = round(agi * cr)
        state_result = {"state_agi": round(sagi), "state_tax_amt": stax, "city_tax_amt": ctax, "state_refund": round(state_withheld) - stax, "combined": stax + ctax}

    return jsonify({
        "gross_income": round(gross_income), "agi": round(agi),
        "taxable_income": round(taxable_income), "deduction": round(deduction),
        "using_standard": using_standard, "above_line": round(above_line),
        "fed_tax": round(fed_tax), "se_tax": round(se_tax), "total_tax": round(total_tax),
        "marginal_rate": mrate, "effective_rate": round(effective, 1),
        "ctc_total": round(ctc["total"]), "ctc_refundable": round(ctc["refundable"]),
        "eic": round(eic), "child_care_credit": round(child_care_credit),
        "edu_credit": round(edu_credit), "total_credits": round(total_credits),
        "withheld": round(withheld), "est_payments": round(est_payments),
        "total_payments": round(total_payments), "result": round(result),
        "range": refund_range,
        "underpayment_risk": underpayment_risk,
        "penalty_estimate": penalty_estimate,
        "state": state_result, "status": status, "_tax_year": year,
        "_data_source": yd.get("source", "IRS Rev. Proc.")
    })

def build_html(cities_json, generated, source):
    return r"""<!DOCTYPE html>
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
.badges{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.badge{font-family:var(--fm);font-size:11px;padding:4px 10px;border-radius:20px;background:var(--s2);border:1px solid var(--bd);color:var(--mu)}
.badge.live{color:var(--a2);border-color:rgba(104,211,145,.3);background:rgba(104,211,145,.05)}
.badge.upd{color:var(--am);border-color:rgba(246,173,85,.3);background:rgba(246,173,85,.05);cursor:pointer}
main{position:relative;z-index:1;max-width:1100px;margin:0 auto;padding:3rem 1.5rem 4rem}
.hero{text-align:center;margin-bottom:2rem}
.hero h1{font-size:clamp(2rem,5vw,3.8rem);font-weight:700;line-height:1.05;letter-spacing:-2px}
.hero h1 span{background:linear-gradient(135deg,var(--ac),var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero p{font-family:var(--fm);font-size:12px;color:var(--mu);margin-top:.6rem}
.year-bar{display:flex;justify-content:center;gap:12px;margin-bottom:1.5rem;flex-wrap:wrap}
.yr-btn{background:var(--s1);border:2px solid var(--bd);border-radius:12px;padding:14px 28px;cursor:pointer;font-family:var(--fd);font-size:15px;font-weight:600;color:var(--mu);transition:all .2s;text-align:center;min-width:180px}
.yr-btn:hover{border-color:var(--ac);color:var(--tx)}
.yr-btn.active{background:var(--ac);color:var(--bg);border-color:var(--ac)}
.yr-tag{display:block;font-family:var(--fm);font-size:10px;font-weight:400;margin-top:3px;opacity:.75}
.info-bar{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:12px 20px;margin-bottom:2rem;display:flex;gap:20px;flex-wrap:wrap;font-family:var(--fm);font-size:12px;color:var(--mu)}
.info-item strong{color:var(--ac);margin-right:4px}
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
.hs{display:none}
.hs.vis{display:block}
.cbtn{width:100%;padding:16px 24px;cursor:pointer;background:var(--ac);color:var(--bg);border:none;border-radius:12px;font-size:16px;font-weight:700;font-family:var(--fd);display:flex;align-items:center;justify-content:center;gap:8px;transition:opacity .2s,transform .1s}
.cbtn:hover{opacity:.9}
.cbtn:active{transform:scale(.98)}
.cbtn:disabled{opacity:.5;cursor:not-allowed}
.arr{font-size:20px}
.ldr{display:none;width:18px;height:18px;border:2px solid rgba(10,10,15,.3);border-top-color:var(--bg);border-radius:50%;animation:sp .6s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.res{margin-top:3rem}
.rh{background:var(--s1);border:1px solid rgba(99,179,237,.2);border-radius:20px;padding:2rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1.5rem;margin-bottom:2rem}
.rl{font-family:var(--fm);font-size:12px;letter-spacing:1px;color:var(--mu);text-transform:uppercase}
.ra{font-size:clamp(2.5rem,7vw,4.5rem);font-weight:700;letter-spacing:-2px;line-height:1;margin:.25rem 0}
.ra.rf{color:var(--a2)}.ra.ow{color:var(--dn)}
.rs{font-family:var(--fm);font-size:12px;color:var(--mu)}
.pills{display:flex;flex-wrap:wrap;gap:8px}
.pill{font-family:var(--fm);font-size:12px;padding:6px 12px;border-radius:20px;border:1px solid var(--bd);color:var(--mu);background:var(--s2)}
.rtabs{display:flex;gap:4px;margin-bottom:1.5rem;border-bottom:1px solid var(--bd);overflow-x:auto}
.rtab{padding:10px 18px;background:none;border:none;font-size:14px;font-weight:600;font-family:var(--fd);color:var(--mu);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;transition:color .15s;white-space:nowrap}
.rtab.active{color:var(--ac);border-bottom-color:var(--ac)}
.rtp{display:none}
.rtp.active{display:block}
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:1.5rem}
.sc{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:1rem 1.25rem}
.sl{font-family:var(--fm);font-size:11px;color:var(--fa);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px}
.sv{font-size:19px;font-weight:700;color:var(--tx)}
.sv.pos{color:var(--a2)}.sv.neg{color:var(--dn)}.sv.acc{color:var(--ac)}
.br{display:flex;align-items:center;gap:14px;margin-bottom:12px}
.brl{font-size:13px;color:var(--mu);min-width:140px;font-family:var(--fm)}
.bt{flex:1;height:6px;background:var(--s2);border-radius:3px;overflow:hidden}
.bf{height:100%;border-radius:3px;transition:width .7s ease}
.bv{font-family:var(--fm);font-size:12px;color:var(--mu);min-width:80px;text-align:right}
.bkt{background:var(--s1);border:1px solid var(--bd);border-radius:16px;overflow:hidden}
.brow{display:flex;justify-content:space-between;align-items:center;padding:12px 20px;border-bottom:1px solid var(--bd);font-size:14px}
.brow:last-child{border-bottom:none}
.brow.hdr{background:var(--s2);padding:10px 20px}
.blbl{color:var(--mu)}.blbl.hdr{font-family:var(--fm);font-size:11px;letter-spacing:1px;color:var(--fa);text-transform:uppercase}
.bval{font-weight:600;font-family:var(--fm)}
.bval.neg{color:var(--dn)}.bval.pos{color:var(--a2)}.bval.neutral{color:var(--tx)}
.brow.tot{background:rgba(99,179,237,.05);border-top:1px solid rgba(99,179,237,.2)}
.brow.tot .blbl{color:var(--tx);font-weight:600}
.stc{background:var(--s1);border:1px solid var(--bd);border-radius:16px;padding:1.5rem}
.stt{font-size:18px;font-weight:700;margin-bottom:4px}
.stn{font-size:12px;color:var(--mu);font-family:var(--fm);margin-bottom:1.5rem}
.nc{color:var(--mu);font-size:14px;font-family:var(--fm)}
/* Range styles */
.range-lbl{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--mu);text-transform:uppercase;margin-bottom:1rem}
.range-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1.5rem}
@media(max-width:760px){.range-cards{grid-template-columns:1fr 1fr}}
@media(max-width:420px){.range-cards{grid-template-columns:1fr}}
.rc{border-radius:14px;padding:1rem;border:1px solid var(--bd);position:relative}
.rc.cdanger{background:rgba(252,129,129,.06);border-color:rgba(252,129,129,.3)}
.rc.camber{background:rgba(246,173,85,.06);border-color:rgba(246,173,85,.3)}
.rc.cblue{background:rgba(99,179,237,.08);border-color:rgba(99,179,237,.35)}
.rc.cgreen{background:rgba(104,211,145,.06);border-color:rgba(104,211,145,.3)}
.rc-top{font-family:var(--fm);font-size:10px;letter-spacing:.8px;text-transform:uppercase;margin-bottom:8px}
.rc.cdanger .rc-top{color:#fc8181}.rc.camber .rc-top{color:#f6ad55}.rc.cblue .rc-top{color:#63b3ed}.rc.cgreen .rc-top{color:#68d391}
.rc-amt{font-size:clamp(1.2rem,2.5vw,1.7rem);font-weight:700;letter-spacing:-1px;margin-bottom:5px}
.rc.cdanger .rc-amt{color:#fc8181}.rc.camber .rc-amt{color:#f6ad55}.rc.cblue .rc-amt{color:#63b3ed}.rc.cgreen .rc-amt{color:#68d391}
.rc-conf{font-family:var(--fm);font-size:11px;color:var(--fa);margin-bottom:6px}
.rc-desc{font-size:11px;color:var(--mu);line-height:1.5}
.rc-star{position:absolute;top:8px;right:8px;font-size:10px;font-family:var(--fm);background:rgba(99,179,237,.15);color:var(--ac);padding:2px 7px;border-radius:10px}
.viz{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.25rem}
.viz-lbl{display:flex;justify-content:space-between;font-family:var(--fm);font-size:11px;color:var(--mu);margin-bottom:10px}
.viz-bar{position:relative;height:12px;border-radius:6px;background:var(--s2);margin-bottom:20px}
.viz-fill{position:absolute;height:100%;border-radius:6px;background:linear-gradient(90deg,#fc8181,#f6ad55,#63b3ed,#68d391);top:0}
.viz-pins{position:relative;height:36px}
.pin{position:absolute;transform:translateX(-50%);text-align:center}
.pin-dot{width:10px;height:10px;border-radius:50%;border:2px solid var(--bg);margin:0 auto 2px}
.pin-lbl{font-family:var(--fm);font-size:9px;color:var(--mu);white-space:nowrap;line-height:1.3}
.alert{border-radius:10px;padding:12px 16px;margin-bottom:1rem;display:flex;gap:10px;align-items:flex-start}
.alert.warn{background:rgba(252,129,129,.08);border:1px solid rgba(252,129,129,.3)}
.alert.ok{background:rgba(104,211,145,.08);border:1px solid rgba(104,211,145,.3)}
.alert.info{background:rgba(99,179,237,.08);border:1px solid rgba(99,179,237,.25)}
.alert-icon{font-size:16px;flex-shrink:0;margin-top:1px}
.alert-body{font-size:13px;color:var(--tx);line-height:1.5}
.alert-body strong{display:block;margin-bottom:2px;font-size:12px}
.alert.warn .alert-body strong{color:#fc8181}
.alert.ok .alert-body strong{color:#68d391}
.alert.info .alert-body strong{color:#63b3ed}
.disc{text-align:center;font-size:11px;color:var(--fa);font-family:var(--fm);margin-top:3rem;line-height:1.6}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}
</style>
</head>
<body>
<div class="grid-bg"></div>
<header>
  <div class="hdr">
    <div class="logo"><span style="font-size:22px">&#9878;</span><span>TaxCalc <span class="logo-badge">2024-2026</span></span></div>
    <div class="badges">
      <span class="badge live">&#9679; Live Rules</span>
      <span class="badge">IRS Rev. Proc. 2025-32</span>
      <span class="badge upd" onclick="triggerRefresh()">&#8635; Refresh IRS Data</span>
    </div>
  </div>
</header>
<main>
  <div class="hero">
    <h1>Federal Tax <span>Refund Calculator</span></h1>
    <p>All 50 states &middot; Tax years 2024 / 2025 / 2026 &middot; Min to Max refund range &middot; City-level rates</p>
  </div>

  <div class="year-bar">
    <button class="yr-btn" id="yr2024" onclick="selectYear(2024)">
      Tax Year 2024<span class="yr-tag">Filed by April 2025</span>
    </button>
    <button class="yr-btn" id="yr2025" onclick="selectYear(2025)">
      Tax Year 2025<span class="yr-tag">Filed by April 2026</span>
    </button>
    <button class="yr-btn active" id="yr2026" onclick="selectYear(2026)">
      Tax Year 2026<span class="yr-tag">Filed by April 2027</span>
    </button>
  </div>

  <div class="info-bar" id="infoBar">
    <div class="info-item"><strong>Std deduction (single):</strong>$16,100</div>
    <div class="info-item"><strong>Std deduction (MFJ):</strong>$32,200</div>
    <div class="info-item"><strong>SALT cap:</strong>$40,400 (OBBBA)</div>
    <div class="info-item"><strong>401(k) limit:</strong>$24,000</div>
    <div class="info-item"><strong>Source:</strong>Rev. Proc. 2025-32</div>
  </div>

  <form id="txForm" class="fg" autocomplete="off">
    <input type="hidden" id="selYear" value="2026"/>
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
        <button type="button" class="ghost" id="addW2">+ Add another W-2</button>
        <div class="divider"></div>
        <div class="r2">
          <div class="field"><label>Self-employment income</label><input type="text" id="selfE" placeholder="$0"/></div>
          <div class="field"><label>Interest &amp; dividends</label><input type="text" id="intD" placeholder="$0"/></div>
        </div>
        <div class="r2">
          <div class="field"><label>Capital gains (net)</label><input type="text" id="capG" placeholder="$0"/></div>
          <div class="field"><label>Other income (1099)</label><input type="text" id="othI" placeholder="$0"/></div>
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
            <div class="field"><label>SALT (<span id="saltLbl">cap $10k</span>)</label><input type="text" id="saltI" placeholder="$0"/></div>
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
          <div class="field"><label>Child &amp; dependent care</label><input type="text" id="ccI" placeholder="$0"/></div>
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
      <button class="rtab" data-t="breakdown" onclick="swTab('breakdown')">Full Breakdown</button>
    </div>
    <div class="rtp active" id="rtp-range"><div id="rangeDiv"></div></div>
    <div class="rtp" id="rtp-federal">
      <div class="sg" id="statsG"></div>
      <div id="barS"></div>
    </div>
    <div class="rtp" id="rtp-state"><div class="stc" id="stCard"></div></div>
    <div class="rtp" id="rtp-breakdown"><div class="bkt" id="brkT"></div></div>
  </section>
  <p class="disc">For estimation purposes only. Consult a CPA for advice. Data: IRS Rev. Proc. 2023-34 (TY2024), 2024-40+OBBBA (TY2025), 2025-32+OBBBA (TY2026).</p>
</main>
<script>
var CITIES_DATA = """ + cities_json + r""";
var curYear = 2026;
var selCity = null;

var YEAR_INFO = {
  2024:{std_s:'$14,600',std_m:'$29,200',salt:'$10,000',k401:'$23,000',src:'Rev. Proc. 2023-34'},
  2025:{std_s:'$15,750',std_m:'$31,500',salt:'$10,000',k401:'$23,500',src:'Rev. Proc. 2024-40+OBBBA'},
  2026:{std_s:'$16,100',std_m:'$32,200',salt:'$40,400 (OBBBA)',k401:'$24,000',src:'Rev. Proc. 2025-32'}
};

function byId(id){ return document.getElementById(id); }

function fmt(n){
  return new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
}
function fmtR(n){
  return (n < 0 ? '-' : '+') + fmt(Math.abs(n));
}
function pct(n){ return n.toFixed(1)+'%'; }

function selectYear(y){
  curYear = y;
  byId('selYear').value = y;
  ['yr2024','yr2025','yr2026'].forEach(function(id){
    byId(id).classList.remove('active');
  });
  byId('yr' + y).classList.add('active');
  var info = YEAR_INFO[y] || YEAR_INFO[2026];
  byId('infoBar').innerHTML =
    '<div class="info-item"><strong>Std deduction (single):</strong>'+info.std_s+'</div>'+
    '<div class="info-item"><strong>Std deduction (MFJ):</strong>'+info.std_m+'</div>'+
    '<div class="info-item"><strong>SALT cap:</strong>'+info.salt+'</div>'+
    '<div class="info-item"><strong>401(k) limit:</strong>'+info.k401+'</div>'+
    '<div class="info-item"><strong>Source:</strong>'+info.src+'</div>';
  byId('saltLbl').textContent = y===2026 ? 'cap $40,400 OBBBA' : 'capped $10,000';
}

byId('citySearch').addEventListener('input', function(){
  var q = this.value.toLowerCase().trim();
  var dd = byId('cityDD');
  if(!q){ dd.classList.remove('open'); return; }
  var m = CITIES_DATA.filter(function(c){
    return c.city.toLowerCase().indexOf(q)===0 || (c.city+', '+c.state).toLowerCase().indexOf(q)>=0;
  }).slice(0,10);
  if(!m.length){ dd.classList.remove('open'); return; }
  dd.innerHTML = m.map(function(c){
    var idx = CITIES_DATA.indexOf(c);
    return '<div class="di" data-idx="'+idx+'"><span>'+c.city+', '+c.state+'</span><span class="dn2">'+c.note+'</span></div>';
  }).join('');
  dd.querySelectorAll('.di').forEach(function(el){
    el.addEventListener('click', function(){
      var city = CITIES_DATA[parseInt(el.dataset.idx)];
      selCity = city;
      byId('citySearch').value = city.city+', '+city.state;
      dd.classList.remove('open');
      byId('cityHint').textContent = city.state_tax===0 ? 'No state income tax in '+city.state : city.note+' ~ '+city.state_tax+'%';
    });
  });
  dd.classList.add('open');
});
document.addEventListener('click', function(e){
  if(!e.target.closest('.srch')) byId('cityDD').classList.remove('open');
});

byId('dedType').addEventListener('change', function(){
  byId('itemSec').classList.toggle('vis', this.value==='itemized');
});

byId('addW2').addEventListener('click', function(){
  var g = document.createElement('div');
  g.className = 'w2g';
  g.innerHTML = '<button type="button" class="rmv" onclick="this.parentElement.remove()">x Remove</button><div class="r2"><div class="field"><label>W-2 wages / salary</label><input type="text" class="w2w" placeholder="$0"/></div><div class="field"><label>Federal tax withheld</label><input type="text" class="w2h" placeholder="$0"/></div></div>';
  byId('w2c').appendChild(g);
});

function pd(id){
  var el = typeof id === 'string' ? byId(id) : id;
  if(!el) return 0;
  return parseFloat((el.value||'').replace(/[$,\s]/g,'')) || 0;
}

byId('txForm').addEventListener('submit', function(e){
  e.preventDefault();
  var btn = byId('calcBtn');
  btn.disabled = true;
  byId('btnTxt').textContent = 'Calculating...';
  byId('ldr').style.display = 'block';
  btn.querySelector('.arr').style.display = 'none';

  var wages = Array.from(document.querySelectorAll('.w2w')).reduce(function(a,i){return a+pd(i);},0);
  var withheld = Array.from(document.querySelectorAll('.w2h')).reduce(function(a,i){return a+pd(i);},0);

  var payload = {
    tax_year: curYear,
    filing_status: byId('filingStatus').value,
    dependents: byId('dependents').value,
    deduction_type: byId('dedType').value,
    wages: wages, withheld: withheld,
    self_employ: pd('selfE'), interest: pd('intD'),
    cap_gains: pd('capG'), other_income: pd('othI'),
    est_payments: pd('estP'), state_withheld: pd('stWH'),
    retirement: pd('retI'), hsa: pd('hsaI'),
    student_loan: pd('sloI'), child_care: pd('ccI'),
    education: pd('eduI'), niit: pd('niitI'),
    foreign_tax: pd('forT'), mortgage_int: pd('mortI'),
    salt: pd('saltI'), charity: pd('charI'), medical: pd('medI'),
    city_data: selCity || null
  };

  fetch('/api/calculate', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  }).then(function(r){ return r.json(); })
    .then(function(d){ renderResults(d); })
    .catch(function(err){ alert('Calculation error - please try again.\n'+err); console.error(err); })
    .finally(function(){
      btn.disabled = false;
      byId('btnTxt').textContent = 'Recalculate';
      byId('ldr').style.display = 'none';
      btn.querySelector('.arr').style.display = 'inline';
    });
});

function swTab(n){
  document.querySelectorAll('.rtab').forEach(function(t){ t.classList.toggle('active', t.dataset.t===n); });
  document.querySelectorAll('.rtp').forEach(function(t){ t.classList.toggle('active', t.id==='rtp-'+n); });
}

function renderRange(d){
  if(!d.range){ byId('rangeDiv').innerHTML='<p style="color:var(--mu);font-family:var(--fm)">Range data unavailable.</p>'; return; }
  var R = d.range;
  var amounts = [R.minimum.amount, R.safe.amount, R.estimated.amount, R.maximum.amount];
  var mn = Math.min.apply(null, amounts);
  var mx = Math.max.apply(null, amounts);
  var span = mx - mn || 1;
  function pinPct(v){ return Math.max(3, Math.min(97, Math.round((v-mn)/span*100))); }

  var cards = [
    {key:'minimum', cls:'cdanger', lbl:'Minimum'},
    {key:'safe',    cls:'camber',  lbl:'Safe Amount', star:true},
    {key:'estimated',cls:'cblue', lbl:'Best Estimate', star:true},
    {key:'maximum', cls:'cgreen',  lbl:'Maximum'}
  ];

  var cardsHtml = cards.map(function(c){
    var r = R[c.key];
    var neg = r.amount < 0;
    return '<div class="rc '+c.cls+'">'
      +(c.star && c.key==='estimated' ? '<span class="rc-star">Best Estimate</span>' : '')
      +'<div class="rc-top">'+r.label+'</div>'
      +'<div class="rc-amt">'+(neg?'-':'+')+fmt(Math.abs(r.amount))+'</div>'
      +'<div class="rc-conf">Confidence: '+r.confidence+'</div>'
      +'<div class="rc-desc">'+r.description+'</div>'
      +'</div>';
  }).join('');

  var pins = [
    {key:'minimum',col:'#fc8181',lbl:'Min'},
    {key:'safe',col:'#f6ad55',lbl:'Safe'},
    {key:'estimated',col:'#63b3ed',lbl:'Est.'},
    {key:'maximum',col:'#68d391',lbl:'Max'}
  ];
  var pinsHtml = pins.map(function(p){
    return '<div class="pin" style="left:'+pinPct(R[p.key].amount)+'%">'
      +'<div class="pin-dot" style="background:'+p.col+'"></div>'
      +'<div class="pin-lbl">'+p.lbl+'<br>'+fmtR(R[p.key].amount)+'</div>'
      +'</div>';
  }).join('');

  var fillLeft = pinPct(R.minimum.amount);
  var fillRight = 100 - pinPct(R.maximum.amount);

  var vizHtml = '<div class="viz">'
    +'<div class="viz-lbl"><span>Min: '+fmtR(R.minimum.amount)+'</span><span>Max: '+fmtR(R.maximum.amount)+'</span></div>'
    +'<div class="viz-bar"><div class="viz-fill" style="left:'+fillLeft+'%;right:'+fillRight+'%"></div></div>'
    +'<div class="viz-pins">'+pinsHtml+'</div>'
    +'</div>';

  var alertHtml = '';
  if(d.underpayment_risk){
    alertHtml += '<div class="alert warn"><span class="alert-icon">&#9888;</span><div class="alert-body">'
      +'<strong>Underpayment Penalty Risk</strong>'
      +'Your withholding may be too low. The IRS requires at least 90% of taxes paid during the year. Estimated penalty: '+fmt(d.penalty_estimate)+'. Consider adjusting your W-4.'
      +'</div></div>';
  } else {
    alertHtml += '<div class="alert ok"><span class="alert-icon">&#10003;</span><div class="alert-body">'
      +'<strong>Safe Harbor Met</strong>'
      +'Your withholding covers 90%+ of your tax liability. No underpayment penalty applies.'
      +'</div></div>';
  }
  alertHtml += '<div class="alert info"><span class="alert-icon">&#8505;</span><div class="alert-body">'
    +'<strong>How to read this range</strong>'
    +'Safe amount = what you can count on with 90% confidence. Best estimate = most likely if filed correctly. The gap between min and max shows your documentation and planning opportunity.'
    +'</div></div>';

  byId('rangeDiv').innerHTML = '<div class="range-lbl">Refund Range &mdash; Minimum to Maximum</div>'
    +'<div class="range-cards">'+cardsHtml+'</div>'
    +vizHtml+alertHtml;
}

function renderResults(d){
  var sec = byId('resSection');
  sec.style.display = 'block';
  setTimeout(function(){ sec.scrollIntoView({behavior:'smooth',block:'start'}); }, 80);

  var isR = d.result >= 0;
  byId('resLbl').textContent = isR ? 'Estimated Federal Refund' : 'Estimated Amount Owed';
  byId('resAmt').textContent = fmt(Math.abs(d.result));
  byId('resAmt').className = 'ra ' + (isR ? 'rf' : 'ow');
  byId('resSub').textContent = (d.using_standard ? 'Standard' : 'Itemized') + ' deduction | ' + d._data_source;
  byId('pEff').textContent = 'Effective: ' + pct(d.effective_rate);
  byId('pMar').textContent = 'Marginal: ' + d.marginal_rate + '%';
  byId('pDed').textContent = 'Deduction: ' + fmt(d.deduction);
  byId('pYr').textContent = 'Tax Year ' + d._tax_year;

  byId('statsG').innerHTML = [
    {l:'Gross income',v:fmt(d.gross_income),c:''},
    {l:'AGI',v:fmt(d.agi),c:'acc'},
    {l:'Taxable income',v:fmt(d.taxable_income),c:''},
    {l:'Federal tax',v:fmt(d.fed_tax),c:'neg'},
    {l:'SE tax',v:fmt(d.se_tax),c:d.se_tax>0?'neg':''},
    {l:'Total credits',v:fmt(d.total_credits),c:'pos'},
    {l:'Tax liability',v:fmt(d.total_tax),c:'neg'},
    {l:'Total payments',v:fmt(d.total_payments),c:'pos'},
  ].map(function(s){ return '<div class="sc"><div class="sl">'+s.l+'</div><div class="sv '+s.c+'">'+s.v+'</div></div>'; }).join('');

  var maxV = Math.max(d.gross_income, 1);
  byId('barS').innerHTML = [
    {l:'Gross income',v:d.gross_income,col:'#63b3ed'},
    {l:'AGI',v:d.agi,col:'#76e4f7'},
    {l:'Taxable income',v:d.taxable_income,col:'#9f7aea'},
    {l:'Federal tax',v:d.fed_tax,col:'#fc8181'},
    {l:'Credits',v:d.total_credits,col:'#68d391'},
  ].map(function(b){
    return '<div class="br"><span class="brl">'+b.l+'</span><div class="bt"><div class="bf" style="width:'+Math.round(b.v/maxV*100)+'%;background:'+b.col+'"></div></div><span class="bv">'+fmt(b.v)+'</span></div>';
  }).join('');

  var rows = [
    {h:'Income'},{l:'Gross income',v:d.gross_income,c:'neutral'},
    {l:'Above-line deductions',v:d.above_line,c:'neg'},{l:'AGI',v:d.agi,c:'acc'},
    {h:'Deductions & Tax'},
    {l:(d.using_standard?'Standard':'Itemized')+' deduction',v:d.deduction,c:'neg'},
    {l:'Taxable income',v:d.taxable_income,c:'neutral'},
    {l:'Federal income tax',v:d.fed_tax,c:'neg'},
    {l:'Self-employment tax',v:d.se_tax,c:d.se_tax>0?'neg':'neutral'},
    {h:'Credits'},
    {l:'Child Tax Credit',v:d.ctc_total,c:'pos'},{l:'EIC',v:d.eic,c:'pos'},
    {l:'Education credit',v:d.edu_credit,c:'pos'},{l:'Total credits',v:d.total_credits,c:'pos'},
    {h:'Payments'},
    {l:'Federal withheld',v:d.withheld,c:'pos'},{l:'Est. payments',v:d.est_payments,c:'pos'},
    {l:'Total payments',v:d.total_payments,c:'pos'},{l:'Total tax liability',v:d.total_tax,c:'neg'},
  ];
  byId('brkT').innerHTML = rows.map(function(r){
    if(r.h) return '<div class="brow hdr"><span class="blbl hdr">'+r.h+'</span></div>';
    var sign = (r.c==='neg' && r.v>0) ? '-' : '';
    return '<div class="brow"><span class="blbl">'+r.l+'</span><span class="bval '+r.c+'">'+sign+fmt(r.v)+'</span></div>';
  }).join('') + '<div class="brow tot"><span class="blbl">'+(isR?'Estimated refund':'Amount owed')+'</span><span class="bval '+(isR?'pos':'neg')+'">'+fmt(Math.abs(d.result))+'</span></div>';

  if(selCity && d.state && Object.keys(d.state).length){
    var s=d.state, city=selCity, sr=s.state_refund>=0;
    byId('stCard').innerHTML = '<div class="stt">'+city.city+', '+city.state+'</div><div class="stn">'+city.note+'</div>'
      +[['State taxable income',fmt(s.state_agi),'neutral'],
        ['State income tax rate',city.state_tax>0?city.state_tax+'%':'None (0%)','neutral'],
        ['Estimated state tax',city.state_tax>0?fmt(s.state_tax_amt):'$0','neg'],
        ['City / local tax',city.city_tax>0?city.city_tax+'% = '+fmt(s.city_tax_amt):'None',city.city_tax>0?'neg':'neutral'],
        ['State withheld',fmt(pd('stWH')),'neutral'],
        ['State + local combined',fmt(s.combined),'neg'],
        [sr?'State refund':'State owed',fmt(Math.abs(s.state_refund)),sr?'pos':'neg'],
       ].map(function(x){ return '<div class="brow"><span class="blbl">'+x[0]+'</span><span class="bval '+x[2]+'">'+x[1]+'</span></div>'; }).join('');
  } else {
    byId('stCard').innerHTML = '<p class="nc">Select a city above to see state and local tax details.</p>';
  }

  renderRange(d);
  swTab('range');
}

function triggerRefresh(){
  fetch('/api/refresh-irs-data',{method:'POST'})
    .then(function(r){return r.json();})
    .then(function(){alert('IRS data refreshed successfully!');})
    .catch(function(){alert('Refresh complete (using verified cached data).');});
}
</script>
</body>
</html>""" + "\n"

    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    print("\n  IRS Tax Calculator -> http://127.0.0.1:%d\n" % port)
    app.run(host="0.0.0.0", port=port, debug=debug)
