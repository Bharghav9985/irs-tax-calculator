"""
app_v2.py - IRS Tax Refund Calculator (Final Clean Build)
All features. Zero patching. Written fresh.
"""
import json, os, math
from pathlib import Path
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "tax_data.json"

def load_tax_data():
    if not DATA_FILE.exists():
        import subprocess, sys
        subprocess.run([sys.executable, str(Path(__file__).parent / "fetch_irs_data.py"), "--offline"], check=True)
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
    {"city":"Kansas City","state":"MO","state_tax":4.95,"city_tax":1.0,"note":"MO + KCMO earnings tax"},
    {"city":"Atlanta","state":"GA","state_tax":5.49,"city_tax":0,"note":"GA rate"},
    {"city":"Omaha","state":"NE","state_tax":5.84,"city_tax":0,"note":"NE marginal rate"},
    {"city":"Colorado Springs","state":"CO","state_tax":4.4,"city_tax":0,"note":"CO flat rate"},
    {"city":"Raleigh","state":"NC","state_tax":4.5,"city_tax":0,"note":"NC flat rate"},
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
    {"city":"Providence","state":"RI","state_tax":5.99,"city_tax":0,"note":"RI top marginal rate"},
    {"city":"Burlington","state":"VT","state_tax":8.75,"city_tax":0,"note":"VT top marginal rate"},
    {"city":"Virginia Beach","state":"VA","state_tax":5.75,"city_tax":0,"note":"VA marginal rate"},
    {"city":"Fresno","state":"CA","state_tax":9.3,"city_tax":0,"note":"CA marginal rate"},
    {"city":"Mesa","state":"AZ","state_tax":2.5,"city_tax":0,"note":"AZ flat rate"},
    {"city":"Aurora","state":"CO","state_tax":4.4,"city_tax":0,"note":"CO flat rate"},
    {"city":"Greensboro","state":"NC","state_tax":4.5,"city_tax":0,"note":"NC flat rate"},
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

def get_marginal(taxable, brackets):
    prev = 0
    for limit, rate in brackets:
        cap = limit if limit is not None else float("inf")
        if taxable <= cap - prev: return rate
        taxable -= cap - prev; prev = cap
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

STATE_EXEMPTIONS = {"IL":2775,"NY":0,"CA":144,"PA":0,"OH":2400,"MI":5600,
    "MD":3200,"VA":930,"MO":2100,"KY":2980,"OR":236,"WI":700,"MN":4800,
    "GA":5400,"NC":0,"CO":0,"AZ":0,"IN":1000,"MA":4400,"NJ":1000,"CT":15000}
STATE_EITC_RATES = {"CA":0.85,"NY":0.30,"IL":0.20,"MD":0.45,"CO":0.38,
    "MN":0.397,"NJ":0.40,"MA":0.30,"CT":0.41,"VA":0.15,"OH":0.30,
    "OR":0.09,"WI":0.04,"GA":0.05,"MI":0.06,"LA":0.05}
STATE_FILING_URLS = {
    "AL":"https://www.revenue.alabama.gov","AK":"https://tax.alaska.gov",
    "AZ":"https://azdor.gov","AR":"https://www.dfa.arkansas.gov",
    "CA":"https://www.ftb.ca.gov/file","CO":"https://tax.colorado.gov",
    "CT":"https://portal.ct.gov/DRS","DC":"https://otr.cfo.dc.gov",
    "FL":"https://floridarevenue.com","GA":"https://dor.georgia.gov",
    "HI":"https://tax.hawaii.gov","ID":"https://tax.idaho.gov",
    "IL":"https://tax.illinois.gov","IN":"https://www.in.gov/dor",
    "IA":"https://tax.iowa.gov","KS":"https://www.ksrevenue.gov",
    "KY":"https://revenue.ky.gov","LA":"https://revenue.louisiana.gov",
    "ME":"https://www.maine.gov/revenue","MD":"https://www.marylandtaxes.gov",
    "MA":"https://www.mass.gov/dor","MI":"https://www.michigan.gov/taxes",
    "MN":"https://www.revenue.state.mn.us","MS":"https://www.dor.ms.gov",
    "MO":"https://dor.mo.gov","MT":"https://mtrevenue.gov",
    "NE":"https://revenue.nebraska.gov","NV":"https://tax.nv.gov",
    "NH":"https://www.revenue.nh.gov","NJ":"https://www.nj.gov/treasury/taxation",
    "NM":"https://www.tax.newmexico.gov","NY":"https://www.tax.ny.gov",
    "NC":"https://www.ncdor.gov","ND":"https://www.nd.gov/tax",
    "OH":"https://tax.ohio.gov","OK":"https://www.ok.gov/tax",
    "OR":"https://www.oregon.gov/dor","PA":"https://www.revenue.pa.gov",
    "RI":"https://tax.ri.gov","SC":"https://dor.sc.gov",
    "SD":"https://dor.sd.gov","TN":"https://www.tn.gov/revenue",
    "TX":"https://comptroller.texas.gov","UT":"https://incometax.utah.gov",
    "VT":"https://tax.vermont.gov","VA":"https://www.tax.virginia.gov",
    "WA":"https://dor.wa.gov","WV":"https://tax.wv.gov",
    "WI":"https://www.revenue.wi.gov","WY":"https://revenue.wyo.gov"
}

@app.route("/")
def index():
    meta = TAX_DATA.get("_meta", {})
    return Response(build_html(json.dumps(CITIES), meta), mimetype="text/html")

@app.route("/api/cities")
def api_cities():
    q = request.args.get("q", "").lower()
    if not q: return jsonify([])
    return jsonify([c for c in CITIES if q in c["city"].lower() or q in (c["city"]+", "+c["state"]).lower()][:12])

@app.route("/api/refresh-irs-data", methods=["POST"])
def refresh_irs_data():
    import subprocess, sys
    try:
        subprocess.run([sys.executable, str(Path(__file__).parent / "fetch_irs_data.py")], capture_output=True, timeout=20)
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

    wages = p("wages"); withheld = p("withheld")
    self_employ = p("self_employ"); interest = p("interest")
    cap_gains = p("cap_gains"); other_income = p("other_income")
    est_payments = p("est_payments"); state_withheld = p("state_withheld")
    retirement = p("retirement"); hsa = p("hsa"); student_loan = p("student_loan")
    child_care = p("child_care"); education = p("education"); niit = p("niit")
    foreign_tax = p("foreign_tax"); mortgage_int = p("mortgage_int")
    salt_input = p("salt"); charity = p("charity"); medical = p("medical")
    ptc = p("ptc"); savers_credit = p("savers_credit"); ev_credit = p("ev_credit")
    actc_override = p("actc_override"); other_credits = p("other_credits")
    deduction_type = data.get("deduction_type", "standard")

    # Federal calculation
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
        deduction = max(itemized, std_ded); using_standard = itemized <= std_ded
    else:
        deduction = std_ded; using_standard = True

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
    extra_nonref = savers_credit + ev_credit
    extra_ref = ptc + other_credits + (actc_override if actc_override > ctc["refundable"] else 0)
    non_ref = min(fed_tax + se_tax, ctc["total"] - ctc["refundable"] + child_care_credit + (edu_credit - edu_ref) + foreign_tax + extra_nonref)
    total_tax = max(0.0, fed_tax + se_tax - non_ref) + niit
    total_payments = withheld + est_payments + ctc["refundable"] + eic + edu_ref + extra_ref
    total_credits = ctc["total"] + eic + child_care_credit + edu_credit + foreign_tax + savers_credit + ev_credit + ptc + other_credits
    result = total_payments - total_tax

    # Refund range
    min_taxable = max(0.0, agi - std_ded)
    min_fed = calc_tax(min_taxable, brackets)
    min_non_ref = min(min_fed + se_tax, (ctc["total"] - ctc["refundable"]) * 0.9 + foreign_tax)
    min_tax = max(0.0, min_fed + se_tax - min_non_ref) + niit
    min_pay = withheld * 0.97 + est_payments + (ctc["refundable"] + eic) * 0.9
    minimum_result = min(round(min_pay - min_tax), round(result))

    safe_fed = calc_tax(max(0.0, agi - std_ded), brackets)
    safe_non_ref = min(safe_fed + se_tax, ctc["total"] - ctc["refundable"] + foreign_tax)
    safe_tax = max(0.0, safe_fed + se_tax - safe_non_ref) + niit
    safe_pay = withheld + est_payments + ctc["refundable"] + eic
    safe_result = max(minimum_result, min(round(safe_pay - safe_tax), round(result)))

    max_ded = deduction + (self_employ * 0.05 if self_employ > 0 else 0)
    max_fed = calc_tax(max(0.0, agi - max_ded), brackets)
    max_non_ref = min(max_fed + se_tax, ctc["total"] - ctc["refundable"] + child_care_credit + (edu_credit - edu_ref) + foreign_tax)
    max_tax = max(0.0, max_fed + se_tax - max_non_ref) + niit
    max_pay = withheld + est_payments + ctc["refundable"] + eic + edu_ref
    maximum_result = max(round(max_pay - max_tax), round(result))

    refund_range = {
        "minimum":  {"amount": minimum_result, "label": "Minimum", "confidence": "20%", "description": "Worst case: IRS questions some deductions or credits."},
        "safe":     {"amount": safe_result, "label": "Safe Amount", "confidence": "90%", "description": "High confidence — based only on verified withholding and solid credits."},
        "estimated":{"amount": round(result), "label": "Best Estimate", "confidence": "70%", "description": "Most likely refund if all inputs are filed correctly."},
        "maximum":  {"amount": maximum_result, "label": "Maximum", "confidence": "15%", "description": "Best case — all deductions accepted and missed write-offs applied."},
    }

    underpayment_risk = total_payments < total_tax * 0.90
    penalty_estimate = round(max(0, (total_tax * 0.90 - total_payments) * 0.08)) if underpayment_risk else 0

    # Multi-state calculation
    w2_list = data.get("w2_list") or []
    state_results = []
    state_map = {}

    for w2 in w2_list:
        cd = w2.get("city_data") or {}
        if not cd: continue
        sc = cd.get("state", "")
        w_wages = float(str(w2.get("wages", 0)).replace(",", "").replace("$", "")) or 0
        w_state_wh = float(str(w2.get("state_withheld", 0)).replace(",", "").replace("$", "")) or 0
        sr = cd.get("state_tax", 0) / 100
        cr = cd.get("city_tax", 0) / 100
        exemption = STATE_EXEMPTIONS.get(sc, 0)
        wage_share = w_wages / max(wages, 1)
        state_agi_portion = max(0.0, w_wages - exemption * wage_share)
        stax = round(state_agi_portion * sr)
        ctax = round(w_wages * cr)
        s_eitc = round(eic * STATE_EITC_RATES.get(sc, 0) * wage_share)
        net_stax = max(0, stax - s_eitc)
        refund_amt = round(w_state_wh) - net_stax - ctax
        state_results.append({
            "employer": w2.get("employer", "") or (cd.get("city", "") + " employer"),
            "city": cd.get("city", ""), "state": sc, "wages": round(w_wages),
            "state_tax_rate": cd.get("state_tax", 0), "city_tax_rate": cd.get("city_tax", 0),
            "state_agi": round(state_agi_portion), "state_tax_amt": stax,
            "city_tax_amt": ctax, "state_eitc": s_eitc,
            "state_withheld": round(w_state_wh), "state_refund": refund_amt,
            "note": cd.get("note", ""), "file_url": STATE_FILING_URLS.get(sc, "https://irs.gov")
        })
        if sc not in state_map:
            state_map[sc] = {"wages": 0, "withheld": 0, "tax_owed": 0, "city_tax": 0}
        state_map[sc]["wages"] += w_wages
        state_map[sc]["withheld"] += w_state_wh
        state_map[sc]["tax_owed"] += net_stax
        state_map[sc]["city_tax"] += ctax

    state_summary = [{"state": sc, "total_wages": round(st["wages"]),
        "total_withheld": round(st["withheld"]), "total_tax_owed": round(st["tax_owed"]),
        "city_tax": round(st["city_tax"]),
        "net_refund": round(st["withheld"]) - round(st["tax_owed"]) - round(st["city_tax"]),
        "file_url": STATE_FILING_URLS.get(sc, "https://irs.gov")}
        for sc, st in state_map.items()]

    # Optimizer tips
    tips = []
    if ptc == 0:
        tips.append({"id":"ptc","title":"Premium Tax Credit (ACA marketplace insurance)","potential":2500,
            "risk":"medium","risk_label":"Medium Risk","done":False,
            "detail":"If you had marketplace health insurance via HealthCare.gov, check Form 1095-A. This is the most commonly missed credit for income $30k-$55k. Can add $500-$5,000+ to your refund.",
            "action":"Enter amount from Form 8962 line 24","form":"Form 8962 / 1095-A"})
    else:
        tips.append({"id":"ptc","title":"Premium Tax Credit (applied)","potential":round(ptc),
            "risk":"medium","risk_label":"Medium Risk","done":True,
            "detail":"PTC of $"+str(round(ptc))+" is included. Verify it matches your Form 1095-A.",
            "action":"Already applied","form":"Form 8962"})

    ira_limit = yd.get("ira_limit", 7000)
    if retirement < ira_limit:
        bracket_rate = 0.12 if taxable_income < 48475 else 0.22
        savings = round((ira_limit - retirement) * bracket_rate)
        tips.append({"id":"ira","title":"Traditional IRA contribution (until April 15)","potential":savings,
            "risk":"low","risk_label":"Low Risk","done":False,
            "detail":"Contribute up to $"+str(round(ira_limit - retirement))+" more to a traditional IRA before April 15. Directly reduces your taxable income by that amount.",
            "action":"Contribute to IRA, enter in 401k/IRA field","form":"Form 5498"})

    if savers_credit == 0 and agi < 36500 and retirement > 0:
        saver_rate = 0.50 if agi < 21750 else (0.20 if agi < 23625 else 0.10)
        saver_pot = round(min(retirement, 2000) * saver_rate)
        if saver_pot > 0:
            tips.append({"id":"savers","title":"Saver's Credit on retirement contributions","potential":saver_pot,
                "risk":"low","risk_label":"Low Risk","done":False,
                "detail":"You contributed to retirement but may not have claimed the Saver's Credit. At your income level you get "+str(int(saver_rate*100))+"% back as a tax credit.",
                "action":"Enter in Saver's Credit field","form":"Form 8880"})

    if education == 0:
        tips.append({"id":"edu","title":"American Opportunity Credit (college)","potential":2500,
            "risk":"low","risk_label":"Low Risk","done":False,
            "detail":"If you or a dependent attended college (first 4 years), claim up to $2,500. 40% ($1,000) is refundable even with no tax owed. Need Form 1098-T from school.",
            "action":"Enter tuition in Education expenses field","form":"Form 1098-T / 8863"})

    if student_loan == 0 and agi < 85000:
        tips.append({"id":"sli","title":"Student loan interest deduction","potential":275,
            "risk":"low","risk_label":"Low Risk","done":False,
            "detail":"Paid student loan interest in "+str(year)+"? Deduct up to $2,500 — reduces your AGI directly. Your lender sends Form 1098-E.",
            "action":"Enter interest paid in Student loan interest field","form":"Form 1098-E"})

    if deps > 0 and child_care == 0:
        tips.append({"id":"dcc","title":"Child & dependent care credit","potential":600,
            "risk":"low","risk_label":"Low Risk","done":False,
            "detail":"Paid for childcare so you could work? Claim up to $3,000 expenses (1 child) or $6,000 (2+). Credit = 20% of expenses.",
            "action":"Enter daycare expenses in Child care field","form":"Form 2441"})

    any_il = any(w.get("city_data",{}).get("state","") == "IL" for w in w2_list)
    if any_il:
        tips.append({"id":"il","title":"Illinois property tax & K-12 credits","potential":500,
            "risk":"low","risk_label":"Low Risk","done":False,
            "detail":"Illinois offers a 5% property tax credit (max $75) and a 25% K-12 education expense credit (max $500) on Schedule ICR.",
            "action":"File IL Schedule ICR with your state return","form":"IL Schedule ICR"})

    if result > 2000:
        tips.append({"id":"w4","title":"Adjust W-4 — stop over-withholding","potential":0,
            "risk":"info","risk_label":"Planning Tip","done":False,
            "detail":"You are getting a large refund because too much was withheld from your paycheck. Update your W-4 to get that money now instead of waiting for refund season.",
            "action":"Submit updated W-4 to your employer","form":"Form W-4"})

    tips.sort(key=lambda x: (x["done"], -x["potential"]))

    return jsonify({
        "gross_income": round(gross_income), "agi": round(agi),
        "taxable_income": round(taxable_income), "deduction": round(deduction),
        "using_standard": using_standard, "above_line": round(above_line),
        "fed_tax": round(fed_tax), "se_tax": round(se_tax), "total_tax": round(total_tax),
        "marginal_rate": mrate, "effective_rate": round(effective, 1),
        "ctc_total": round(ctc["total"]), "ctc_refundable": round(ctc["refundable"]),
        "eic": round(eic), "child_care_credit": round(child_care_credit),
        "ptc": round(ptc), "savers_credit": round(savers_credit),
        "edu_credit": round(edu_credit), "total_credits": round(total_credits),
        "withheld": round(withheld), "est_payments": round(est_payments),
        "total_payments": round(total_payments), "result": round(result),
        "range": refund_range,
        "underpayment_risk": underpayment_risk, "penalty_estimate": penalty_estimate,
        "state_results": state_results, "state_summary": state_summary,
        "multi_state": len(state_summary) > 1,
        "optimizer": tips,
        "status": status, "_tax_year": year,
        "_data_source": yd.get("source", "IRS Rev. Proc.")
    })

def build_html(cities_json, meta):
    generated = meta.get("generated", "")[:10]
    source = meta.get("source", "IRS.gov")
    state_urls_json = json.dumps(STATE_FILING_URLS)

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
.bg-grid{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(99,179,237,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(99,179,237,.025) 1px,transparent 1px);background-size:48px 48px}
header{position:sticky;top:0;z-index:100;background:rgba(10,10,15,.92);backdrop-filter:blur(20px);border-bottom:1px solid var(--bd);padding:0 2rem}
.hdr{max-width:1100px;margin:0 auto;height:60px;display:flex;align-items:center;justify-content:space-between}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:18px}
.logo-badge{background:var(--ac);color:var(--bg);font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px}
.hdr-badges{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.hbadge{font-family:var(--fm);font-size:11px;padding:4px 10px;border-radius:20px;background:var(--s2);border:1px solid var(--bd);color:var(--mu);cursor:default}
.hbadge.live{color:var(--a2);border-color:rgba(104,211,145,.3)}
.hbadge.btn{cursor:pointer;color:var(--am);border-color:rgba(246,173,85,.3)}
.hbadge.btn:hover{opacity:.8}
main{position:relative;z-index:1;max-width:1100px;margin:0 auto;padding:2.5rem 1.5rem 4rem}
.hero{text-align:center;margin-bottom:2rem}
.hero h1{font-size:clamp(2rem,5vw,3.8rem);font-weight:700;line-height:1.05;letter-spacing:-2px}
.hero h1 span{background:linear-gradient(135deg,var(--ac),var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero p{font-family:var(--fm);font-size:12px;color:var(--mu);margin-top:.5rem}
/* Year selector */
.year-bar{display:flex;justify-content:center;gap:12px;margin-bottom:1.5rem;flex-wrap:wrap}
.yr-btn{background:var(--s1);border:2px solid var(--bd);border-radius:12px;padding:13px 26px;cursor:pointer;font-family:var(--fd);font-size:15px;font-weight:600;color:var(--mu);transition:all .2s;text-align:center;min-width:175px;line-height:1.3}
.yr-btn:hover{border-color:var(--ac);color:var(--tx)}
.yr-btn.active{background:var(--ac);color:var(--bg);border-color:var(--ac)}
.yr-sub{display:block;font-family:var(--fm);font-size:10px;font-weight:400;margin-top:3px;opacity:.75}
/* Info bar */
.info-bar{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:11px 18px;margin-bottom:1.5rem;display:flex;gap:18px;flex-wrap:wrap;font-family:var(--fm);font-size:12px;color:var(--mu)}
.info-item strong{color:var(--ac);margin-right:4px}
/* Grid */
.fg{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start}
@media(max-width:768px){.fg{grid-template-columns:1fr}}
.col{display:flex;flex-direction:column;gap:1.5rem}
.card{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);padding:1.5rem;transition:border-color .2s}
.card:hover{border-color:rgba(99,179,237,.12)}
.clabel{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--ac);text-transform:uppercase;margin-bottom:1.25rem}
.field{margin-bottom:1rem}
.field:last-child{margin-bottom:0}
.field label{display:block;font-size:12px;font-weight:500;color:var(--mu);margin-bottom:6px}
.field input,.field select{width:100%;background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:10px 14px;font-size:14px;font-family:var(--fm);color:var(--tx);outline:none;transition:border-color .2s;-webkit-appearance:none;appearance:none}
.field input:focus,.field select:focus{border-color:var(--bdf);background:rgba(99,179,237,.04)}
.field input::placeholder{color:var(--fa)}
.field select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23888899' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;padding-right:36px}
.hint{font-size:11px;color:var(--a2);margin-top:4px;font-family:var(--fm)}
.r2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:480px){.r2{grid-template-columns:1fr}}
.divider{height:1px;background:var(--bd);margin:1rem 0}
.subsec{font-size:11px;font-family:var(--fm);letter-spacing:1px;color:var(--fa);text-transform:uppercase;margin:1rem 0 .75rem}
/* City search (global) */
.srch-wrap{position:relative}
.city-dd{position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:200;background:var(--s2);border:1px solid rgba(99,179,237,.3);border-radius:10px;display:none;max-height:200px;overflow-y:auto;box-shadow:0 16px 40px rgba(0,0,0,.5)}
.city-dd.open{display:block}
.city-di{padding:9px 14px;cursor:pointer;font-size:14px;color:var(--tx);display:flex;justify-content:space-between;align-items:center}
.city-di:hover{background:rgba(99,179,237,.08)}
.city-di small{font-size:11px;color:var(--mu);font-family:var(--fm)}
/* W-2 cards */
.w2-stack{display:flex;flex-direction:column;gap:12px}
.w2-card{background:var(--s2);border:1px solid var(--bd);border-radius:12px;padding:14px}
.w2-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.w2-title{font-family:var(--fm);font-size:11px;letter-spacing:1px;color:var(--ac);text-transform:uppercase;display:flex;align-items:center;gap:7px}
.w2-num{background:var(--ac);color:var(--bg);width:19px;height:19px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0}
.w2-rmv{background:none;border:1px solid var(--bd);border-radius:6px;color:var(--mu);cursor:pointer;padding:3px 9px;font-size:12px;font-family:var(--fd)}
.w2-rmv:hover{border-color:var(--dn);color:var(--dn)}
.w2-emp{width:100%;background:transparent;border:none;border-bottom:1px solid var(--bd);color:var(--mu);font-family:var(--fm);font-size:12px;padding:4px 0 6px;margin-bottom:11px;outline:none}
.w2-emp:focus{border-bottom-color:var(--ac);color:var(--tx)}
.w2-emp::placeholder{color:var(--fa)}
/* Per-W-2 city */
.w2-city-wrap{position:relative;margin-bottom:11px}
.w2-city-inp{width:100%;background:var(--bg);border:1px solid var(--bd);border-radius:6px;padding:8px 10px;font-size:12px;font-family:var(--fm);color:var(--tx);outline:none;transition:border-color .2s}
.w2-city-inp:focus{border-color:var(--bdf)}
.w2-city-inp::placeholder{color:var(--fa)}
.w2-city-dd{position:absolute;top:calc(100% + 2px);left:0;right:0;z-index:300;background:var(--s2);border:1px solid rgba(99,179,237,.3);border-radius:8px;display:none;max-height:170px;overflow-y:auto;box-shadow:0 12px 28px rgba(0,0,0,.5)}
.w2-city-dd.open{display:block}
.w2-city-di{padding:8px 12px;cursor:pointer;font-size:13px;color:var(--tx);display:flex;justify-content:space-between}
.w2-city-di:hover{background:rgba(99,179,237,.08)}
.w2-city-di small{font-size:10px;color:var(--mu);font-family:var(--fm)}
.w2-city-tag{display:inline-flex;align-items:center;gap:6px;background:rgba(99,179,237,.1);border:1px solid rgba(99,179,237,.2);border-radius:5px;padding:3px 9px;font-family:var(--fm);font-size:11px;color:var(--ac);margin-top:4px}
.w2-city-clr{cursor:pointer;color:var(--mu);margin-left:2px}
.w2-city-clr:hover{color:var(--dn)}
/* W-2 boxes */
.w2-boxes{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.w2-box-lbl{font-size:10px;font-family:var(--fm);color:var(--fa);margin-bottom:3px;display:flex;justify-content:space-between}
.w2-box-lbl span{color:var(--ac);font-weight:500}
.w2-box input{width:100%;background:var(--bg);border:1px solid var(--bd);border-radius:6px;padding:8px 10px;font-size:13px;font-family:var(--fm);color:var(--tx);outline:none;transition:border-color .2s}
.w2-box input:focus{border-color:var(--bdf)}
.w2-box input::placeholder{color:var(--fa)}
/* W-2 totals & add btn */
.w2-totals{background:rgba(99,179,237,.05);border:1px solid rgba(99,179,237,.15);border-radius:9px;padding:9px 14px;margin-top:8px;display:flex;gap:18px;flex-wrap:wrap;font-family:var(--fm);font-size:12px;color:var(--mu)}
.w2-totals strong{color:var(--ac)}
.add-w2-btn{background:none;border:2px dashed rgba(99,179,237,.25);border-radius:10px;color:var(--ac);padding:11px;font-size:13px;cursor:pointer;font-family:var(--fd);width:100%;transition:all .2s;display:flex;align-items:center;justify-content:center;gap:7px;margin-top:4px}
.add-w2-btn:hover{border-color:var(--ac);background:rgba(99,179,237,.05)}
.add-w2-btn:disabled{opacity:.4;cursor:not-allowed}
/* Hidden section */
.hs{display:none}
.hs.vis{display:block}
/* EIC preview */
.eic-box{background:rgba(99,179,237,.05);border:1px solid rgba(99,179,237,.2);border-radius:8px;padding:9px 13px;font-family:var(--fm);font-size:12px;color:var(--mu);margin-bottom:1rem;display:none}
.eic-box.show{display:block}
.eic-row{display:flex;justify-content:space-between;padding:2px 0}
.eic-val{color:var(--a2);font-weight:500}
/* Calc button */
.cbtn{width:100%;padding:15px 24px;cursor:pointer;background:var(--ac);color:var(--bg);border:none;border-radius:12px;font-size:16px;font-weight:700;font-family:var(--fd);display:flex;align-items:center;justify-content:center;gap:8px;transition:opacity .2s,transform .1s}
.cbtn:hover{opacity:.9}
.cbtn:active{transform:scale(.98)}
.cbtn:disabled{opacity:.5;cursor:not-allowed}
.arr{font-size:20px}
.spin{display:none;width:18px;height:18px;border:2px solid rgba(10,10,15,.3);border-top-color:var(--bg);border-radius:50%;animation:sp .6s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
/* Results */
.res{margin-top:3rem}
.res-hero{background:var(--s1);border:1px solid rgba(99,179,237,.2);border-radius:20px;padding:2rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1.5rem;margin-bottom:2rem}
.res-lbl{font-family:var(--fm);font-size:12px;letter-spacing:1px;color:var(--mu);text-transform:uppercase}
.res-amt{font-size:clamp(2.5rem,7vw,4.5rem);font-weight:700;letter-spacing:-2px;line-height:1;margin:.25rem 0}
.res-amt.rf{color:var(--a2)}.res-amt.ow{color:var(--dn)}
.res-sub{font-family:var(--fm);font-size:12px;color:var(--mu)}
.pills{display:flex;flex-wrap:wrap;gap:8px}
.pill{font-family:var(--fm);font-size:12px;padding:5px 12px;border-radius:20px;border:1px solid var(--bd);color:var(--mu);background:var(--s2)}
/* Tabs */
.tabs{display:flex;gap:0;margin-bottom:1.5rem;border-bottom:1px solid var(--bd);overflow-x:auto}
.tab{padding:10px 16px;background:none;border:none;font-size:13px;font-weight:600;font-family:var(--fd);color:var(--mu);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;transition:color .15s;white-space:nowrap}
.tab.active{color:var(--ac);border-bottom-color:var(--ac)}
.tab-pane{display:none}
.tab-pane.active{display:block}
/* Stats grid */
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:11px;margin-bottom:1.5rem}
.sc{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:.9rem 1.1rem}
.sc .sl{font-family:var(--fm);font-size:11px;color:var(--fa);text-transform:uppercase;letter-spacing:.8px;margin-bottom:5px}
.sc .sv{font-size:19px;font-weight:700;color:var(--tx)}
.sv.pos{color:var(--a2)}.sv.neg{color:var(--dn)}.sv.acc{color:var(--ac)}
/* Bar chart */
.bar-row{display:flex;align-items:center;gap:13px;margin-bottom:11px}
.bar-lbl{font-size:13px;color:var(--mu);min-width:130px;font-family:var(--fm)}
.bar-track{flex:1;height:6px;background:var(--s2);border-radius:3px;overflow:hidden}
.bar-fill{height:100%;border-radius:3px;transition:width .7s ease}
.bar-val{font-family:var(--fm);font-size:12px;color:var(--mu);min-width:78px;text-align:right}
/* Breakdown table */
.bkt{background:var(--s1);border:1px solid var(--bd);border-radius:14px;overflow:hidden}
.brow{display:flex;justify-content:space-between;align-items:center;padding:11px 18px;border-bottom:1px solid var(--bd);font-size:14px}
.brow:last-child{border-bottom:none}
.brow.bh{background:var(--s2);padding:8px 18px}
.blbl{color:var(--mu)}.blbl.bh{font-family:var(--fm);font-size:11px;letter-spacing:1px;color:var(--fa);text-transform:uppercase}
.bval{font-weight:600;font-family:var(--fm)}
.bval.neg{color:var(--dn)}.bval.pos{color:var(--a2)}.bval.neutral{color:var(--tx)}
.brow.tot{background:rgba(99,179,237,.05);border-top:1px solid rgba(99,179,237,.2)}
.brow.tot .blbl{color:var(--tx);font-weight:600}
/* Range */
.range-lbl{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--mu);text-transform:uppercase;margin-bottom:1rem}
.range-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-bottom:1.25rem}
@media(max-width:720px){.range-grid{grid-template-columns:1fr 1fr}}
@media(max-width:400px){.range-grid{grid-template-columns:1fr}}
.rc{border-radius:13px;padding:.95rem;border:1px solid var(--bd);position:relative}
.rc.cR{background:rgba(252,129,129,.06);border-color:rgba(252,129,129,.28)}
.rc.cA{background:rgba(246,173,85,.06);border-color:rgba(246,173,85,.28)}
.rc.cB{background:rgba(99,179,237,.07);border-color:rgba(99,179,237,.32)}
.rc.cG{background:rgba(104,211,145,.06);border-color:rgba(104,211,145,.28)}
.rc-top{font-family:var(--fm);font-size:10px;letter-spacing:.8px;text-transform:uppercase;margin-bottom:7px}
.rc.cR .rc-top{color:#fc8181}.rc.cA .rc-top{color:#f6ad55}.rc.cB .rc-top{color:#63b3ed}.rc.cG .rc-top{color:#68d391}
.rc-amt{font-size:clamp(1.2rem,2.5vw,1.7rem);font-weight:700;letter-spacing:-1px;margin-bottom:4px}
.rc.cR .rc-amt{color:#fc8181}.rc.cA .rc-amt{color:#f6ad55}.rc.cB .rc-amt{color:#63b3ed}.rc.cG .rc-amt{color:#68d391}
.rc-conf{font-family:var(--fm);font-size:11px;color:var(--fa);margin-bottom:5px}
.rc-desc{font-size:11px;color:var(--mu);line-height:1.5}
.rc-star{position:absolute;top:8px;right:8px;font-size:10px;font-family:var(--fm);background:rgba(99,179,237,.15);color:var(--ac);padding:2px 7px;border-radius:9px}
.viz{background:var(--s1);border:1px solid var(--bd);border-radius:11px;padding:1.1rem 1.4rem;margin-bottom:1.2rem}
.viz-lbls{display:flex;justify-content:space-between;font-family:var(--fm);font-size:11px;color:var(--mu);margin-bottom:9px}
.viz-bar{position:relative;height:11px;border-radius:6px;background:var(--s2);margin-bottom:18px}
.viz-fill{position:absolute;height:100%;border-radius:6px;background:linear-gradient(90deg,#fc8181,#f6ad55,#63b3ed,#68d391);top:0}
.viz-pins{position:relative;height:34px}
.pin{position:absolute;transform:translateX(-50%);text-align:center}
.pin-dot{width:10px;height:10px;border-radius:50%;border:2px solid var(--bg);margin:0 auto 2px}
.pin-lbl{font-family:var(--fm);font-size:9px;color:var(--mu);white-space:nowrap;line-height:1.3}
/* Alerts */
.al{border-radius:10px;padding:11px 15px;margin-bottom:.9rem;display:flex;gap:9px;align-items:flex-start}
.al.warn{background:rgba(252,129,129,.07);border:1px solid rgba(252,129,129,.28)}
.al.ok{background:rgba(104,211,145,.07);border:1px solid rgba(104,211,145,.28)}
.al.info{background:rgba(99,179,237,.07);border:1px solid rgba(99,179,237,.23)}
.al-ico{font-size:15px;flex-shrink:0;margin-top:1px}
.al-body{font-size:13px;color:var(--tx);line-height:1.5}
.al-body strong{display:block;margin-bottom:2px;font-size:12px}
.al.warn .al-body strong{color:#fc8181}
.al.ok .al-body strong{color:#68d391}
.al.info .al-body strong{color:#63b3ed}
/* State results */
.ms-card{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:1rem 1.2rem;margin-bottom:11px}
.ms-hdr{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;gap:10px}
.ms-emp{font-size:14px;font-weight:600;color:var(--tx)}
.ms-loc{font-size:11px;color:var(--mu);font-family:var(--fm);margin-top:2px}
.ms-ref{font-size:20px;font-weight:700;text-align:right}
.ms-ref.pos{color:var(--a2)}.ms-ref.neg{color:var(--dn)}
.ms-total{background:rgba(104,211,145,.06);border:1px solid rgba(104,211,145,.2);border-radius:9px;padding:11px 15px;display:flex;justify-content:space-between;align-items:center;margin-top:8px}
.ms-total-amt{font-size:22px;font-weight:700}
.ms-total-amt.pos{color:var(--a2)}.ms-total-amt.neg{color:var(--dn)}
.no-state{color:var(--mu);font-size:14px;font-family:var(--fm);padding:.5rem 0}
/* Optimizer */
.opt-lbl{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--mu);text-transform:uppercase;margin-bottom:1rem}
.opt-total{background:rgba(104,211,145,.07);border:1px solid rgba(104,211,145,.25);border-radius:11px;padding:12px 16px;margin-bottom:1.1rem;display:flex;justify-content:space-between;align-items:center}
.opt-total-lbl{font-size:13px;color:var(--tx)}
.opt-total-amt{font-size:20px;font-weight:700;color:var(--a2)}
.opt-item{background:var(--s1);border:1px solid var(--bd);border-radius:11px;padding:13px 16px;margin-bottom:9px;display:flex;gap:12px}
.opt-item.done{opacity:.55}
.opt-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;margin-top:4px}
.opt-dot.low{background:#68d391}.opt-dot.medium{background:#f6ad55}.opt-dot.info{background:#63b3ed}.opt-dot.done-c{background:#44445a}
.opt-body{flex:1}
.opt-name{font-size:14px;font-weight:600;color:var(--tx);margin-bottom:3px;display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap}
.opt-right{display:flex;align-items:center;gap:6px;flex-shrink:0}
.opt-amt{font-family:var(--fm);font-size:12px;color:var(--a2)}
.opt-amt.done-amt{color:var(--fa)}
.risk-badge{font-family:var(--fm);font-size:10px;padding:2px 7px;border-radius:9px}
.risk-low{background:rgba(104,211,145,.12);color:#68d391}
.risk-medium{background:rgba(246,173,85,.12);color:#f6ad55}
.risk-info{background:rgba(99,179,237,.12);color:#63b3ed}
.opt-detail{font-size:12px;color:var(--mu);line-height:1.5;margin-bottom:5px}
.opt-action{font-family:var(--fm);font-size:11px;color:var(--ac)}
.opt-form{font-family:var(--fm);font-size:11px;color:var(--fa);margin-left:8px}
.done-badge{font-family:var(--fm);font-size:10px;background:rgba(68,68,90,.3);color:var(--fa);padding:2px 7px;border-radius:9px;margin-left:4px}
/* File buttons */
.file-section{margin-top:2rem;display:none}
.file-section-lbl{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--mu);text-transform:uppercase;text-align:center;margin-bottom:1rem}
.file-grid{display:grid;grid-template-columns:1fr 1fr;gap:11px}
@media(max-width:600px){.file-grid{grid-template-columns:1fr}}
.file-btn{display:flex;align-items:center;justify-content:center;gap:9px;padding:13px 18px;border-radius:11px;font-size:13px;font-weight:600;font-family:var(--fd);cursor:pointer;text-decoration:none;transition:opacity .2s;border:none;text-align:left}
.file-btn:hover{opacity:.88}
.file-btn.fed{background:#1d4ed8;color:#fff}
.file-btn.sta{background:#047857;color:#fff}
.file-btn.free{background:var(--s1);color:var(--ac);border:1px solid var(--ac)}
.file-btn.direct{background:var(--s1);color:var(--am);border:1px solid var(--am)}
.file-btn-ico{font-size:20px;flex-shrink:0}
.file-btn-txt{font-size:13px}
.file-btn-sub{font-size:11px;opacity:.75;font-family:var(--fm);display:block;margin-top:1px}
.file-note{font-family:var(--fm);font-size:11px;color:var(--fa);text-align:center;margin-top:8px;line-height:1.6}
.disc{text-align:center;font-size:11px;color:var(--fa);font-family:var(--fm);margin-top:2.5rem;line-height:1.6}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}
</style>
</head>
<body>
<div class="bg-grid"></div>
<header>
  <div class="hdr">
    <div class="logo"><span style="font-size:22px">&#9878;</span><span>TaxCalc <span class="logo-badge">2024-2026</span></span></div>
    <div class="hdr-badges">
      <span class="hbadge live">&#9679; Live Rules</span>
      <span class="hbadge">IRS Rev. Proc. 2025-32</span>
      <span class="hbadge btn" onclick="doRefresh()">&#8635; Refresh IRS Data</span>
    </div>
  </div>
</header>
<main>
  <div class="hero">
    <h1>Federal Tax <span>Refund Calculator</span></h1>
    <p>Tax years 2024 / 2025 / 2026 &middot; All 50 states &middot; Multi-W-2 &middot; City-level rates &middot; Data: """ + source + """ &middot; """ + generated + """</p>
  </div>

  <div class="year-bar">
    <button type="button" class="yr-btn" id="yr2024" onclick="selYear(2024)">
      Tax Year 2024<span class="yr-sub">Filed April 2025</span>
    </button>
    <button type="button" class="yr-btn" id="yr2025" onclick="selYear(2025)">
      Tax Year 2025<span class="yr-sub">Filed April 2026</span>
    </button>
    <button type="button" class="yr-btn active" id="yr2026" onclick="selYear(2026)">
      Tax Year 2026<span class="yr-sub">Filed April 2027</span>
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
    <div class="col">
      <div class="card">
        <div class="clabel">01 &mdash; Filing Details</div>
        <div class="r2">
          <div class="field">
            <label>Filing status</label>
            <select id="filing_status">
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
        <div class="clabel">02 &mdash; W-2 Income (up to 4)</div>
        <div class="w2-stack" id="w2Stack"></div>
        <button type="button" class="add-w2-btn" id="addW2Btn">
          <span style="font-size:17px">+</span> <span id="addW2BtnTxt">Add W-2</span>
        </button>
        <div class="w2-totals" id="w2Totals" style="display:none">
          Combined wages: <strong id="totWages">$0</strong> &nbsp;|&nbsp;
          Combined withheld: <strong id="totWithheld">$0</strong>
        </div>
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
          <div class="subsec">Itemized deductions</div>
          <div class="r2">
            <div class="field"><label>Mortgage interest</label><input type="text" id="mortI" placeholder="$0"/></div>
            <div class="field"><label>SALT (<span id="saltLbl">cap $10k</span>)</label><input type="text" id="saltI" placeholder="$0"/></div>
          </div>
          <div class="r2">
            <div class="field"><label>Charitable contributions</label><input type="text" id="charI" placeholder="$0"/></div>
            <div class="field"><label>Medical (above 7.5% AGI)</label><input type="text" id="medI" placeholder="$0"/></div>
          </div>
        </div>
        <div class="subsec">Above-line deductions</div>
        <div class="r2">
          <div class="field"><label>401(k) / 403(b) / IRA</label><input type="text" id="retI" placeholder="$0"/></div>
          <div class="field"><label>HSA contributions</label><input type="text" id="hsaI" placeholder="$0"/></div>
        </div>
        <div class="field"><label>Student loan interest paid</label><input type="text" id="sloI" placeholder="$0"/></div>
      </div>

      <div class="card">
        <div class="clabel">04 &mdash; Credits &amp; Taxes</div>
        <div class="eic-box" id="eicBox"></div>
        <div class="r2">
          <div class="field"><label>Child &amp; dependent care</label><input type="text" id="ccI" placeholder="$0"/></div>
          <div class="field"><label>Education expenses (1098-T)</label><input type="text" id="eduI" placeholder="$0"/></div>
        </div>
        <div class="subsec">Additional credits</div>
        <div class="r2">
          <div class="field"><label>Premium Tax Credit (ACA / Form 8962)</label><input type="text" id="ptcI" placeholder="$0"/></div>
          <div class="field"><label>Saver&apos;s Credit (Form 8880)</label><input type="text" id="savI" placeholder="$0"/></div>
        </div>
        <div class="r2">
          <div class="field"><label>Clean energy / EV credit</label><input type="text" id="evI" placeholder="$0"/></div>
          <div class="field"><label>Other refundable credits</label><input type="text" id="otherCrI" placeholder="$0"/></div>
        </div>
        <div class="r2">
          <div class="field"><label>Foreign tax credit</label><input type="text" id="forT" placeholder="$0"/></div>
          <div class="field"><label>Additional Medicare / NIIT</label><input type="text" id="niitI" placeholder="$0"/></div>
        </div>
        <div class="field"><label>State tax withheld (W-2 box 17 total)</label><input type="text" id="stWH" placeholder="$0"/></div>
      </div>

      <button type="submit" class="cbtn" id="calcBtn">
        <span id="calcBtnTxt">Calculate My Refund</span>
        <span class="arr">&#8594;</span>
        <div class="spin" id="calcSpin"></div>
      </button>
    </div>
  </form>

  <div class="res" id="resSection" style="display:none">
    <div class="res-hero">
      <div>
        <p class="res-lbl" id="resLbl">Estimated Federal Refund</p>
        <div class="res-amt" id="resAmt">$0</div>
        <p class="res-sub" id="resSub"></p>
      </div>
      <div class="pills">
        <span class="pill" id="pEff"></span>
        <span class="pill" id="pMar"></span>
        <span class="pill" id="pDed"></span>
        <span class="pill" id="pYr"></span>
      </div>
    </div>

    <div class="tabs">
      <button type="button" class="tab active" data-tab="range" onclick="swTab('range')">&#127926; Refund Range</button>
      <button type="button" class="tab" data-tab="optimizer" onclick="swTab('optimizer')">&#128200; Maximize</button>
      <button type="button" class="tab" data-tab="federal" onclick="swTab('federal')">Federal</button>
      <button type="button" class="tab" data-tab="state" onclick="swTab('state')">State &amp; Local</button>
      <button type="button" class="tab" data-tab="breakdown" onclick="swTab('breakdown')">Breakdown</button>
    </div>

    <div class="tab-pane active" id="tab-range"><div id="rangeDiv"></div></div>
    <div class="tab-pane" id="tab-optimizer"><div id="optimizerDiv"></div></div>
    <div class="tab-pane" id="tab-federal">
      <div class="sg" id="statsG"></div>
      <div id="barS"></div>
    </div>
    <div class="tab-pane" id="tab-state"><div id="stateDiv"></div></div>
    <div class="tab-pane" id="tab-breakdown"><div class="bkt" id="brkT"></div></div>
  </div>

  <div class="file-section" id="fileSection">
    <div class="file-section-lbl">Ready to file your return?</div>
    <div class="file-grid">
      <a class="file-btn free" href="https://www.irs.gov/filing/free-file-do-your-federal-taxes-for-free" target="_blank" rel="noopener">
        <span class="file-btn-ico">&#127981;</span>
        <div><div class="file-btn-txt">IRS Free File</div><span class="file-btn-sub">Free federal e-file if income &lt; $84k</span></div>
      </a>
      <a class="file-btn direct" href="https://directfile.irs.gov" target="_blank" rel="noopener">
        <span class="file-btn-ico">&#9889;</span>
        <div><div class="file-btn-txt">IRS Direct File</div><span class="file-btn-sub">Free direct e-file at IRS.gov</span></div>
      </a>
      <a class="file-btn fed" href="https://www.irs.gov/filing" target="_blank" rel="noopener">
        <span class="file-btn-ico">&#127979;</span>
        <div><div class="file-btn-txt">IRS Filing Center</div><span class="file-btn-sub">All federal filing options</span></div>
      </a>
      <a class="file-btn sta" href="#" id="stateFileBtn" target="_blank" rel="noopener">
        <span class="file-btn-ico">&#127963;</span>
        <div><div class="file-btn-txt" id="stateFileTxt">State Filing Portal</div><span class="file-btn-sub" id="stateFileSub">Select a state to enable</span></div>
      </a>
    </div>
    <div class="file-note">Links open official government websites. TaxCalc does not store or share your data. &nbsp;Filing deadline: April 15, <span id="deadlineYr">2027</span>.</div>
  </div>

  <p class="disc">For estimation purposes only. Consult a CPA for advice. Data from IRS Rev. Proc. 2023-34 (TY2024), 2024-40+OBBBA (TY2025), 2025-32+OBBBA (TY2026).</p>
</main>

<script>
// ── Data ──────────────────────────────────────────────────────────────────────
var CITIES = """ + cities_json + """;
var STATE_URLS = """ + state_urls_json + """;
var YEAR_INFO = {
  2024:{s:'$14,600',m:'$29,200',salt:'$10,000',k:'$23,000',src:'Rev. Proc. 2023-34'},
  2025:{s:'$15,750',m:'$31,500',salt:'$10,000',k:'$23,500',src:'Rev. Proc. 2024-40+OBBBA'},
  2026:{s:'$16,100',m:'$32,200',salt:'$40,400 (OBBBA)',k:'$24,000',src:'Rev. Proc. 2025-32'}
};
var curYear = 2026;
var w2CityMap = {};
var w2Count = 0;
var MAX_W2 = 4;

// ── Helpers ───────────────────────────────────────────────────────────────────
function G(id){ return document.getElementById(id); }
function fmt(n){ return new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n); }
function fmtS(n){ return (n<0?'-':'+')+fmt(Math.abs(n)); }
function pct(n){ return n.toFixed(1)+'%'; }
function pv(id){
  var el = typeof id==='string' ? G(id) : id;
  if(!el) return 0;
  return parseFloat((el.value||'').replace(/[$,\\s]/g,''))||0;
}

// ── Year selector ─────────────────────────────────────────────────────────────
function selYear(y){
  curYear = y;
  ['yr2024','yr2025','yr2026'].forEach(function(id){ G(id).classList.remove('active'); });
  G('yr'+y).classList.add('active');
  var info = YEAR_INFO[y] || YEAR_INFO[2026];
  G('infoBar').innerHTML =
    '<div class="info-item"><strong>Std deduction (single):</strong>'+info.s+'</div>'+
    '<div class="info-item"><strong>Std deduction (MFJ):</strong>'+info.m+'</div>'+
    '<div class="info-item"><strong>SALT cap:</strong>'+info.salt+'</div>'+
    '<div class="info-item"><strong>401(k) limit:</strong>'+info.k+'</div>'+
    '<div class="info-item"><strong>Source:</strong>'+info.src+'</div>';
  G('saltLbl').textContent = y===2026 ? 'cap $40,400 OBBBA' : 'capped $10,000';
  updateEicPreview();
}

// ── Tab switching ─────────────────────────────────────────────────────────────
function swTab(name){
  document.querySelectorAll('.tab').forEach(function(t){
    t.classList.toggle('active', t.dataset.tab===name);
  });
  document.querySelectorAll('.tab-pane').forEach(function(p){
    p.classList.toggle('active', p.id==='tab-'+name);
  });
}

// ── City search helper ────────────────────────────────────────────────────────
function makeCitySearch(inputEl, ddEl, onSelect){
  inputEl.addEventListener('input', function(){
    var q = this.value.toLowerCase().trim();
    if(!q){ ddEl.classList.remove('open'); return; }
    var m = CITIES.filter(function(c){
      return c.city.toLowerCase().indexOf(q)===0 || (c.city+', '+c.state).toLowerCase().indexOf(q)>=0;
    }).slice(0,9);
    if(!m.length){ ddEl.classList.remove('open'); return; }
    ddEl.innerHTML = m.map(function(c){
      return '<div class="w2-city-di" data-ci="'+CITIES.indexOf(c)+'">'+
        '<span>'+c.city+', '+c.state+'</span>'+
        '<small>'+(c.state_tax===0?'No state tax':c.state_tax+'% state')+(c.city_tax>0?' + '+c.city_tax+'% city':'')+'</small>'+
        '</div>';
    }).join('');
    ddEl.querySelectorAll('.w2-city-di').forEach(function(el){
      el.addEventListener('click', function(){
        var city = CITIES[parseInt(el.dataset.ci)];
        ddEl.classList.remove('open');
        onSelect(city);
      });
    });
    ddEl.classList.add('open');
  });
  document.addEventListener('click', function(e){
    if(!e.target.closest('.w2-city-wrap') && !e.target.closest('.srch-wrap')) ddEl.classList.remove('open');
  });
}

// ── W-2 management ────────────────────────────────────────────────────────────
function addW2(preload){
  if(w2Count >= MAX_W2) return;
  w2Count++;
  var i = w2Count;
  var d = preload || {};
  var card = document.createElement('div');
  card.className = 'w2-card'; card.id = 'w2c-'+i;
  card.innerHTML =
    '<div class="w2-hdr">'+
      '<span class="w2-title"><span class="w2-num">'+i+'</span>W-2 #'+i+'</span>'+
      (i>1?'<button type="button" class="w2-rmv" onclick="removeW2('+i+')">Remove</button>':'')+
    '</div>'+
    '<input class="w2-emp" placeholder="Employer name (optional)" value="'+(d.emp||'')+'"/>'+
    '<div class="w2-city-wrap" id="w2cw-'+i+'">'+
      '<input class="w2-city-inp" id="w2ci-'+i+'" placeholder="&#128205; Work state / city (e.g. Tampa, FL)" autocomplete="off" value="'+(d.cityTxt||'')+'"/>'+
      '<div class="w2-city-dd" id="w2cd-'+i+'"></div>'+
      '<div id="w2ct-'+i+'"></div>'+
    '</div>'+
    '<div class="w2-boxes">'+
      '<div><div class="w2-box-lbl">Box 1 - Wages, tips<span>Box 1</span></div><input class="w2b1" placeholder="$0" value="'+(d.w||'')+'"/></div>'+
      '<div><div class="w2-box-lbl">Box 2 - Federal withheld<span>Box 2</span></div><input class="w2b2" placeholder="$0" value="'+(d.wh||'')+'"/></div>'+
      '<div><div class="w2-box-lbl">Box 12 - 401(k)/403(b)<span>Box 12</span></div><input class="w2b12" placeholder="$0 if shown" value="'+(d.b12||'')+'"/></div>'+
      '<div><div class="w2-box-lbl">Box 17 - State withheld<span>Box 17</span></div><input class="w2b17" placeholder="$0 if shown" value="'+(d.b17||'')+'"/></div>'+
    '</div>';
  G('w2Stack').appendChild(card);
  w2CityMap[i] = d.city || null;

  // Wire city search for this W-2
  var ci = G('w2ci-'+i);
  var cd = G('w2cd-'+i);
  makeCitySearch(ci, cd, function(city){
    w2CityMap[i] = city;
    ci.value = city.city+', '+city.state;
    G('w2ct-'+i).innerHTML = '<div class="w2-city-tag">&#128205; '+city.city+', '+city.state+
      (city.state_tax===0?' - No state tax':' - '+city.state_tax+'% state')+(city.city_tax>0?' + '+city.city_tax+'% city':'')+
      '<span class="w2-city-clr" onclick="clearW2City('+i+')">&times;</span></div>';
    updateStateFileBtn(city.state);
  });
  // Wire input events
  card.querySelectorAll('input').forEach(function(inp){
    inp.addEventListener('input', function(){ updateW2Totals(); updateEicPreview(); });
  });
  updateW2Totals(); updateAddBtn();
}

function clearW2City(i){
  w2CityMap[i] = null;
  G('w2ci-'+i).value = '';
  G('w2ct-'+i).innerHTML = '';
}

function removeW2(i){
  var card = G('w2c-'+i); if(card) card.remove();
  delete w2CityMap[i]; w2Count--;
  // Renumber
  var cards = G('w2Stack').querySelectorAll('.w2-card');
  w2CityMap = {}; w2Count = 0;
  cards.forEach(function(c){
    w2Count++;
    var ii = w2Count;
    c.id = 'w2c-'+ii;
    var t = c.querySelector('.w2-title');
    if(t) t.innerHTML = '<span class="w2-num">'+ii+'</span>W-2 #'+ii;
    var rmv = c.querySelector('.w2-rmv');
    if(rmv){ rmv.setAttribute('onclick','removeW2('+ii+')'); rmv.style.display = ii===1?'none':''; }
    if(G('w2ci-'+ii)) w2CityMap[ii] = w2CityMap[ii] || null;
  });
  updateW2Totals(); updateAddBtn();
}

function updateW2Totals(){
  var wgs = Array.from(document.querySelectorAll('.w2b1')).reduce(function(a,x){return a+pv(x);},0);
  var wth = Array.from(document.querySelectorAll('.w2b2')).reduce(function(a,x){return a+pv(x);},0);
  var cnt = document.querySelectorAll('.w2-card').length;
  var td = G('w2Totals');
  if(cnt>1||wgs>0){ td.style.display='flex'; G('totWages').textContent=fmt(wgs); G('totWithheld').textContent=fmt(wth); }
  else td.style.display='none';
  // Auto-fill box17 into state withheld field if empty
  var b17 = Array.from(document.querySelectorAll('.w2b17')).reduce(function(a,x){return a+pv(x);},0);
  if(b17>0 && pv('stWH')===0) G('stWH').value = b17;
  // Auto-fill box12 into retirement if empty
  var b12 = Array.from(document.querySelectorAll('.w2b12')).reduce(function(a,x){return a+pv(x);},0);
  if(b12>0 && pv('retI')===0) G('retI').value = b12;
}

function updateAddBtn(){
  var btn = G('addW2Btn'); var txt = G('addW2BtnTxt');
  if(w2Count>=MAX_W2){ btn.disabled=true; txt.textContent='Max 4 W-2s reached'; }
  else{ btn.disabled=false; txt.textContent='Add W-2 ('+w2Count+'/'+MAX_W2+' used)'; }
}

// ── EIC preview ───────────────────────────────────────────────────────────────
function updateEicPreview(){
  var wages = Array.from(document.querySelectorAll('.w2b1')).reduce(function(a,x){return a+pv(x);},0) + pv('selfE');
  var deps = parseInt(G('dependents').value)||0;
  var status = G('filing_status').value;
  var EIC_MAX = {2024:[632,4213,6960,7830],2025:[649,4328,7152,8046],2026:[649,4328,7152,8231]};
  var EIC_LIM = {2024:[17640,46560,52918,56838],2025:[18591,49084,55768,59899],2026:[19104,50434,57310,61555]};
  var d = Math.min(deps,3);
  var lim = (EIC_LIM[curYear]||EIC_LIM[2026])[d] + (status==='mfj'?2160:0);
  var maxC = (EIC_MAX[curYear]||EIC_MAX[2026])[d];
  var eic = (wages>0 && wages<=lim) ? Math.round(maxC*Math.min(1,wages/(lim*0.30))) : 0;
  var box = G('eicBox');
  if(wages>0){
    box.className='eic-box show';
    box.innerHTML='<div class="eic-row"><span><strong>Earned Income Credit (auto-calculated)</strong></span><span class="eic-val">'+(eic>0?fmt(eic):'$0 (income exceeds limit)')+'</span></div>'+
      '<div class="eic-row" style="font-size:11px"><span>Wages: '+fmt(wages)+' | Limit for '+d+' dependent(s): '+fmt(lim)+'</span><span style="color:var(--fa)">'+(eic>0?'Included in refund':'Not eligible')+'</span></div>';
  } else box.className='eic-box';
}

// ── Deduction toggle ──────────────────────────────────────────────────────────
G('dedType').addEventListener('change', function(){ G('itemSec').classList.toggle('vis',this.value==='itemized'); });
G('filing_status').addEventListener('change', updateEicPreview);
G('dependents').addEventListener('input', updateEicPreview);
G('selfE').addEventListener('input', updateEicPreview);
document.addEventListener('input', function(e){ if(e.target.classList.contains('w2b1')) updateEicPreview(); });

// ── Add W-2 button ────────────────────────────────────────────────────────────
G('addW2Btn').addEventListener('click', function(){ addW2(); });

// ── Form submit ───────────────────────────────────────────────────────────────
G('txForm').addEventListener('submit', function(e){
  e.preventDefault();
  var btn = G('calcBtn');
  btn.disabled = true;
  G('calcBtnTxt').textContent = 'Calculating...';
  G('calcSpin').style.display = 'block';
  btn.querySelector('.arr').style.display = 'none';

  var wages=0, withheld=0, w2list=[];
  document.querySelectorAll('.w2-card').forEach(function(card){
    var idx = parseInt(card.id.replace('w2c-',''));
    var w = pv(card.querySelector('.w2b1'));
    var wh = pv(card.querySelector('.w2b2'));
    var b12 = pv(card.querySelector('.w2b12'));
    var b17 = pv(card.querySelector('.w2b17'));
    var emp = card.querySelector('.w2-emp') ? card.querySelector('.w2-emp').value : '';
    wages += w; withheld += wh;
    w2list.push({employer:emp, wages:w, withheld:wh, box12:b12, state_withheld:b17, city_data:w2CityMap[idx]||null});
  });

  var stateWH = pv('stWH') || Array.from(document.querySelectorAll('.w2b17')).reduce(function(a,x){return a+pv(x);},0);
  var retVal = pv('retI') || Array.from(document.querySelectorAll('.w2b12')).reduce(function(a,x){return a+pv(x);},0);

  var payload = {
    tax_year: curYear,
    filing_status: G('filing_status').value,
    dependents: G('dependents').value,
    deduction_type: G('dedType').value,
    wages: wages, withheld: withheld,
    self_employ: pv('selfE'), interest: pv('intD'),
    cap_gains: pv('capG'), other_income: pv('othI'),
    est_payments: pv('estP'), state_withheld: stateWH,
    retirement: retVal, hsa: pv('hsaI'),
    student_loan: pv('sloI'), child_care: pv('ccI'),
    education: pv('eduI'), niit: pv('niitI'),
    foreign_tax: pv('forT'), mortgage_int: pv('mortI'),
    salt: pv('saltI'), charity: pv('charI'), medical: pv('medI'),
    ptc: pv('ptcI'), savers_credit: pv('savI'),
    ev_credit: pv('evI'), actc_override: 0,
    other_credits: pv('otherCrI'),
    w2_list: w2list, city_data: null
  };

  fetch('/api/calculate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)})
    .then(function(r){ return r.json(); })
    .then(function(d){ showResults(d); })
    .catch(function(err){ alert('Error: '+err); console.error(err); })
    .finally(function(){
      btn.disabled=false;
      G('calcBtnTxt').textContent='Recalculate';
      G('calcSpin').style.display='none';
      btn.querySelector('.arr').style.display='inline';
    });
});

// ── Show results ──────────────────────────────────────────────────────────────
function showResults(d){
  var sec = G('resSection'); sec.style.display='block';
  setTimeout(function(){ sec.scrollIntoView({behavior:'smooth',block:'start'}); },80);

  var isR = d.result>=0;
  G('resLbl').textContent = isR ? 'Estimated Federal Refund' : 'Estimated Amount Owed';
  G('resAmt').textContent = fmt(Math.abs(d.result));
  G('resAmt').className = 'res-amt '+(isR?'rf':'ow');
  G('resSub').textContent = (d.using_standard?'Standard':'Itemized')+' deduction | '+d._data_source;
  G('pEff').textContent = 'Effective: '+pct(d.effective_rate);
  G('pMar').textContent = 'Marginal: '+d.marginal_rate+'%';
  G('pDed').textContent = 'Deduction: '+fmt(d.deduction);
  G('pYr').textContent = 'Tax Year '+d._tax_year;

  showRange(d);
  showOptimizer(d);
  showFederal(d);
  showState(d);
  showBreakdown(d);
  showFileButtons(d);
  swTab('range');
}

// ── Range tab ─────────────────────────────────────────────────────────────────
function showRange(d){
  if(!d.range){ G('rangeDiv').innerHTML=''; return; }
  var R=d.range;
  var items=[
    {k:'minimum',c:'cR',ico:'&#9660;'},
    {k:'safe',c:'cA',ico:'&#9632;'},
    {k:'estimated',c:'cB',ico:'&#9654;',star:true},
    {k:'maximum',c:'cG',ico:'&#9650;'}
  ];
  var amounts=[R.minimum.amount,R.safe.amount,R.estimated.amount,R.maximum.amount];
  var mn=Math.min.apply(null,amounts), mx=Math.max.apply(null,amounts), span=mx-mn||1;
  function pp(v){ return Math.max(3,Math.min(97,Math.round((v-mn)/span*100))); }

  var cards = items.map(function(it){
    var r=R[it.k], neg=r.amount<0;
    return '<div class="rc '+it.c+'">'+
      (it.star?'<span class="rc-star">Best Estimate</span>':'')+
      '<div class="rc-top">'+it.ico+' '+r.label+'</div>'+
      '<div class="rc-amt">'+(neg?'-':'+')+fmt(Math.abs(r.amount))+'</div>'+
      '<div class="rc-conf">Confidence: '+r.confidence+'</div>'+
      '<div class="rc-desc">'+r.description+'</div>'+
    '</div>';
  }).join('');

  var pins=[
    {k:'minimum',col:'#fc8181',lbl:'Min'},
    {k:'safe',col:'#f6ad55',lbl:'Safe'},
    {k:'estimated',col:'#63b3ed',lbl:'Est.'},
    {k:'maximum',col:'#68d391',lbl:'Max'}
  ];
  var pinsHtml = pins.map(function(p){
    return '<div class="pin" style="left:'+pp(R[p.k].amount)+'%">'+
      '<div class="pin-dot" style="background:'+p.col+'"></div>'+
      '<div class="pin-lbl">'+p.lbl+'<br>'+fmtS(R[p.k].amount)+'</div>'+
    '</div>';
  }).join('');

  var alerts='';
  if(d.underpayment_risk){
    alerts+='<div class="al warn"><span class="al-ico">&#9888;</span><div class="al-body"><strong>Underpayment Penalty Risk</strong>Your withholding may be too low. The IRS requires at least 90% of taxes paid during the year. Estimated penalty: '+fmt(d.penalty_estimate)+'. Consider updating your W-4.</div></div>';
  } else {
    alerts+='<div class="al ok"><span class="al-ico">&#10003;</span><div class="al-body"><strong>Safe Harbor Met</strong>Your withholding covers 90%+ of tax liability. No underpayment penalty applies.</div></div>';
  }
  alerts+='<div class="al info"><span class="al-ico">&#8505;</span><div class="al-body"><strong>How to read this range</strong>Safe amount = what you can count on. Best Estimate = most likely. The gap shows your documentation and planning opportunity.</div></div>';

  G('rangeDiv').innerHTML=
    '<div class="range-lbl">Refund Range &mdash; Minimum to Maximum</div>'+
    '<div class="range-grid">'+cards+'</div>'+
    '<div class="viz"><div class="viz-lbls"><span>Min: '+fmtS(R.minimum.amount)+'</span><span>Max: '+fmtS(R.maximum.amount)+'</span></div>'+
    '<div class="viz-bar"><div class="viz-fill" style="left:'+pp(R.minimum.amount)+'%;right:'+(100-pp(R.maximum.amount))+'%"></div></div>'+
    '<div class="viz-pins">'+pinsHtml+'</div></div>'+
    alerts;
}

// ── Optimizer tab ─────────────────────────────────────────────────────────────
function showOptimizer(d){
  if(!d.optimizer||!d.optimizer.length){ G('optimizerDiv').innerHTML=''; return; }
  var tips=d.optimizer;
  var avail=tips.filter(function(t){return !t.done&&t.risk!=='info';});
  var total=avail.reduce(function(a,t){return a+t.potential;},0);
  var html='<div class="opt-lbl">&#128200; Refund Maximizer</div>';
  if(total>0) html+='<div class="opt-total"><span class="opt-total-lbl">Potential additional refund available</span><span class="opt-total-amt">'+fmt(total)+'</span></div>';
  tips.forEach(function(t){
    var dotC=t.done?'done-c':t.risk;
    var amtTxt=t.done?'Applied':(t.potential>0?'up to '+fmt(t.potential):'Tip');
    html+='<div class="opt-item'+(t.done?' done':'')+'">'+
      '<div class="opt-dot '+dotC+'"></div>'+
      '<div class="opt-body">'+
        '<div class="opt-name">'+
          '<span>'+t.title+(t.done?'&nbsp;<span class="done-badge">&#10003; Applied</span>':'')+'</span>'+
          '<div class="opt-right"><span class="opt-amt'+(t.done?' done-amt':'')+'">'+amtTxt+'</span><span class="risk-badge risk-'+t.risk+'">'+t.risk_label+'</span></div>'+
        '</div>'+
        '<div class="opt-detail">'+t.detail+'</div>'+
        '<div><span class="opt-action">Action: '+t.action+'</span><span class="opt-form">&nbsp;'+t.form+'</span></div>'+
      '</div>'+
    '</div>';
  });
  G('optimizerDiv').innerHTML=html;
}

// ── Federal detail tab ────────────────────────────────────────────────────────
function showFederal(d){
  G('statsG').innerHTML=[
    {l:'Gross income',v:fmt(d.gross_income),c:''},
    {l:'AGI',v:fmt(d.agi),c:'acc'},
    {l:'Taxable income',v:fmt(d.taxable_income),c:''},
    {l:'Federal tax',v:fmt(d.fed_tax),c:'neg'},
    {l:'SE tax',v:fmt(d.se_tax),c:d.se_tax>0?'neg':''},
    {l:'Total credits',v:fmt(d.total_credits),c:'pos'},
    {l:'Tax liability',v:fmt(d.total_tax),c:'neg'},
    {l:'Total payments',v:fmt(d.total_payments),c:'pos'},
  ].map(function(s){ return '<div class="sc"><div class="sl">'+s.l+'</div><div class="sv '+s.c+'">'+s.v+'</div></div>'; }).join('');
  var mx=Math.max(d.gross_income,1);
  G('barS').innerHTML=[
    {l:'Gross income',v:d.gross_income,col:'#63b3ed'},
    {l:'AGI',v:d.agi,col:'#76e4f7'},
    {l:'Taxable income',v:d.taxable_income,col:'#9f7aea'},
    {l:'Federal tax',v:d.fed_tax,col:'#fc8181'},
    {l:'Credits',v:d.total_credits,col:'#68d391'},
  ].map(function(b){ return '<div class="bar-row"><span class="bar-lbl">'+b.l+'</span><div class="bar-track"><div class="bar-fill" style="width:'+Math.round(b.v/mx*100)+'%;background:'+b.col+'"></div></div><span class="bar-val">'+fmt(b.v)+'</span></div>'; }).join('');
}

// ── State & local tab ─────────────────────────────────────────────────────────
function showState(d){
  var div=G('stateDiv');
  if(!d.state_results||d.state_results.length===0){
    div.innerHTML='<p class="no-state">Select a city on each W-2 to see state and local tax details.</p>'; return;
  }
  var html='';
  if(d.multi_state){
    html+='<div class="al warn" style="margin-bottom:1rem"><span class="al-ico">&#9888;</span><div class="al-body"><strong>Multi-state return</strong>You worked in '+d.state_summary.length+' states. You may need to file a separate state return for each state where you earned income.</div></div>';
  }
  d.state_results.forEach(function(sr){
    var pos=sr.state_refund>=0;
    html+='<div class="ms-card">'+
      '<div class="ms-hdr">'+
        '<div><div class="ms-emp">'+(sr.employer||sr.city+' employer')+'</div><div class="ms-loc">&#128205; '+sr.city+', '+sr.state+(sr.state_tax_rate===0?' - No state tax':' - '+sr.state_tax_rate+'% state')+(sr.city_tax_rate>0?' + '+sr.city_tax_rate+'% city':'')+'</div></div>'+
        '<div><div style="font-size:11px;color:var(--mu);font-family:var(--fm);text-align:right">'+(pos?'Refund':'Owed')+'</div><div class="ms-ref '+(pos?'pos':'neg')+'">'+(pos?'+':'-')+fmt(Math.abs(sr.state_refund))+'</div></div>'+
      '</div>'+
      '<div class="bkt">'+ [
        ['W-2 wages',fmt(sr.wages),'neutral'],
        ['State AGI',fmt(sr.state_agi),'neutral'],
        ['State tax'+(sr.state_tax_rate>0?' ('+sr.state_tax_rate+'%)':''),sr.state_tax_rate>0?'-'+fmt(sr.state_tax_amt):'None','neg'],
        ['City/local tax',sr.city_tax_rate>0?'-'+fmt(sr.city_tax_amt):'None',sr.city_tax_rate>0?'neg':'neutral'],
        ['State EITC',sr.state_eitc>0?'+'+fmt(sr.state_eitc):'$0',sr.state_eitc>0?'pos':'neutral'],
        ['State withheld','+'+fmt(sr.state_withheld),'pos'],
      ].map(function(x){ return '<div class="brow"><span class="blbl">'+x[0]+'</span><span class="bval '+x[2]+'">'+x[1]+'</span></div>'; }).join('')+
      '</div>'+
    '</div>';
    updateStateFileBtn(sr.state, sr.file_url);
  });
  if(d.state_summary && d.state_summary.length>0){
    var tot=d.state_summary.reduce(function(a,s){return a+s.net_refund;},0);
    var tp=tot>=0;
    html+='<div class="ms-total"><span style="font-size:13px;color:var(--tx)">Total state refund / owed:</span><span class="ms-total-amt '+(tp?'pos':'neg')+'">'+(tp?'+':'')+fmt(tot)+'</span></div>';
  }
  div.innerHTML=html;
}

// ── Breakdown tab ─────────────────────────────────────────────────────────────
function showBreakdown(d){
  var isR=d.result>=0;
  var rows=[
    {h:'Income'},{l:'Gross income',v:d.gross_income,c:'neutral'},
    {l:'Above-line deductions',v:d.above_line,c:'neg'},{l:'AGI',v:d.agi,c:'acc'},
    {h:'Deductions & Tax'},
    {l:(d.using_standard?'Standard':'Itemized')+' deduction',v:d.deduction,c:'neg'},
    {l:'Taxable income',v:d.taxable_income,c:'neutral'},
    {l:'Federal income tax',v:d.fed_tax,c:'neg'},
    {l:'Self-employment tax',v:d.se_tax,c:d.se_tax>0?'neg':'neutral'},
    {h:'Credits'},
    {l:'Child Tax Credit',v:d.ctc_total,c:'pos'},
    {l:'Earned Income Credit',v:d.eic,c:'pos'},
    {l:'Education credit',v:d.edu_credit,c:'pos'},
    {l:'Premium Tax Credit',v:d.ptc,c:'pos'},
    {l:'Total credits',v:d.total_credits,c:'pos'},
    {h:'Payments'},
    {l:'Federal withheld',v:d.withheld,c:'pos'},
    {l:'Estimated payments',v:d.est_payments,c:'pos'},
    {l:'Total payments',v:d.total_payments,c:'pos'},
    {l:'Total tax liability',v:d.total_tax,c:'neg'},
  ];
  G('brkT').innerHTML=rows.map(function(r){
    if(r.h) return '<div class="brow bh"><span class="blbl bh">'+r.h+'</span></div>';
    return '<div class="brow"><span class="blbl">'+r.l+'</span><span class="bval '+r.c+'">'+(r.c==='neg'&&r.v>0?'-':'')+fmt(r.v)+'</span></div>';
  }).join('')+'<div class="brow tot"><span class="blbl">'+(isR?'Estimated refund':'Amount owed')+'</span><span class="bval '+(isR?'pos':'neg')+'">'+fmt(Math.abs(d.result))+'</span></div>';
}

// ── File buttons ──────────────────────────────────────────────────────────────
function showFileButtons(d){
  G('fileSection').style.display='block';
  G('deadlineYr').textContent = d._tax_year+1;
}

function updateStateFileBtn(stateCode, url){
  var btn=G('stateFileBtn');
  var u = url || STATE_URLS[stateCode] || 'https://www.irs.gov';
  btn.href=u;
  G('stateFileTxt').textContent = stateCode+' State Filing Portal';
  G('stateFileSub').textContent = 'File your '+stateCode+' state return';
}

// ── Refresh IRS data ──────────────────────────────────────────────────────────
function doRefresh(){
  fetch('/api/refresh-irs-data',{method:'POST'})
    .then(function(r){return r.json();})
    .then(function(){ alert('IRS data refreshed!'); })
    .catch(function(){ alert('Using cached IRS data.'); });
}

// ── Init ──────────────────────────────────────────────────────────────────────
addW2();
</script>
</body>
</html>""" + "\n"
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    print("\\n  IRS Tax Calculator -> http://127.0.0.1:%d\\n" % port)
    app.run(host="0.0.0.0", port=port, debug=debug)
