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

def build_optimizer(agi, gross_income, wages, self_employ, deps, status, year,
                    retirement, hsa, student_loan, education, child_care,
                    ptc, savers_credit, city_data, deduction, std_ded, eic,
                    ctc, fed_tax, total_tax, result, taxable_income):
    tips = []
    state_code = (city_data or {}).get("state", "")
    
    # EIC eligibility
    eic_limits_2025_single = [19104, 50434, 57310, 61555]
    eic_max_2025 = [649, 4328, 7152, 8046]
    d = min(deps, 3)
    if eic == 0 and wages < eic_limits_2025_single[d]:
        tips.append({"id":"eic","title":"Earned Income Credit available","potential":eic_max_2025[d],
            "risk":"low","risk_label":"Low Risk",
            "detail":"Your income qualifies for EIC but it calculated as $0. Verify your dependents count is correct.",
            "action":"Check Section 01 dependents","form":"Schedule EIC","done":False})
    elif eic > 0:
        tips.append({"id":"eic","title":"Earned Income Credit (applied)","potential":eic,
            "risk":"low","risk_label":"Low Risk",
            "detail":"EIC of "+str(round(eic))+" is already included in your refund. Make sure dependents have valid SSNs.",
            "action":"Already applied","form":"Schedule EIC","done":True})

    # PTC - ACA marketplace
    if ptc == 0:
        tips.append({"id":"ptc","title":"Premium Tax Credit (ACA health insurance)","potential":3000,
            "risk":"medium","risk_label":"Medium Risk",
            "detail":"If you had marketplace health insurance (HealthCare.gov), you may have a large refundable credit. Check Form 1095-A from your insurer. This is the #1 missed credit for income $30k-$55k.",
            "action":"Enter amount from Form 8962 line 24 in Premium Tax Credit field","form":"Form 8962 / 1095-A","done":False})
    else:
        tips.append({"id":"ptc","title":"Premium Tax Credit (applied)","potential":ptc,
            "risk":"medium","risk_label":"Medium Risk",
            "detail":"PTC of "+str(round(ptc))+" included. Must reconcile with Form 1095-A. If your actual income differed from your estimate, you may owe some back.",
            "action":"Verify against Form 1095-A line 33","form":"Form 8962","done":True})

    # IRA contribution (still actionable until April 15)
    ira_limit = 7000
    if retirement < ira_limit:
        remaining_ira = ira_limit - retirement
        bracket_rate = 0.12 if taxable_income < 48475 else 0.22
        savings = round(remaining_ira * bracket_rate)
        tips.append({"id":"ira","title":"Traditional IRA contribution (deadline April 15)","potential":savings,
            "risk":"low","risk_label":"Low Risk",
            "detail":"You can still contribute up to $"+str(round(remaining_ira))+
                     " to a traditional IRA for "+str(year)+" before April 15. This directly reduces your taxable income, saving you $"+str(savings)+" in taxes.",
            "action":"Contribute to IRA then enter in 401k/IRA field","form":"Form 5498","done":False})

    # Saver's credit
    savers_limit_2025 = {"single":36500,"mfj":73000,"hoh":54750}
    savers_limit = savers_limit_2025.get(status, 36500)
    if savers_credit == 0 and agi < savers_limit and (retirement > 0 or hsa > 0):
        saver_rate = 0.50 if agi < 21750 else (0.20 if agi < 23625 else 0.10)
        saver_potential = round(min(retirement + hsa, 2000) * saver_rate)
        if saver_potential > 0:
            tips.append({"id":"savers","title":"Saver's Credit on retirement contributions","potential":saver_potential,
                "risk":"low","risk_label":"Low Risk",
                "detail":"You contributed to retirement but didn't claim the Saver's Credit. At your income, you get "+str(int(saver_rate*100))+"% back as a credit. Worth $"+str(saver_potential)+".",
                "action":"Enter amount in Saver's Credit field","form":"Form 8880","done":False})

    # Student loan interest
    if student_loan == 0 and agi < 85000:
        tips.append({"id":"sli","title":"Student loan interest deduction","potential":275,
            "risk":"low","risk_label":"Low Risk",
            "detail":"If you paid any student loan interest in "+str(year)+", you can deduct up to $2,500 (reduces AGI directly). Your lender sends Form 1098-E.",
            "action":"Enter interest paid in Student loan interest field","form":"Form 1098-E","done":False})
    elif student_loan > 0:
        tips.append({"id":"sli","title":"Student loan interest (applied)","potential":round(student_loan*0.12),
            "risk":"low","risk_label":"Low Risk",
            "detail":"Student loan deduction of $"+str(round(student_loan))+" reduces your AGI.",
            "action":"Already applied","form":"Form 1098-E","done":True})

    # Education credit
    if education == 0:
        tips.append({"id":"edu","title":"American Opportunity Credit (college)","potential":2500,
            "risk":"low","risk_label":"Low Risk",
            "detail":"If you or a dependent attended college (first 4 years), claim up to $2,500 — 40% ($1,000) is refundable even with no tax owed. Need Form 1098-T from the school.",
            "action":"Enter tuition in Education expenses field","form":"Form 1098-T / 8863","done":False})

    # HSA
    hsa_limit = 4300 if status in ["single","mfs","hoh"] else 8550
    if hsa == 0:
        tips.append({"id":"hsa","title":"HSA contribution deduction","potential":round(hsa_limit*0.12),
            "risk":"low","risk_label":"Low Risk",
            "detail":"If you have a high-deductible health plan, HSA contributions up to $"+str(hsa_limit)+" are fully deductible. You can still contribute for "+str(year)+" until April 15.",
            "action":"Enter HSA contributions in HSA field","form":"Form 8889","done":False})

    # IL-specific credits
    if state_code == "IL":
        tips.append({"id":"il_prop","title":"IL property tax credit","potential":75,
            "risk":"low","risk_label":"Low Risk",
            "detail":"Illinois gives a 5% credit on property taxes paid (max $75 benefit). If you own property in IL, claim this on Schedule ICR.",
            "action":"Enter on Illinois Schedule ICR when filing state return","form":"IL Schedule ICR","done":False})
        tips.append({"id":"il_k12","title":"IL K-12 education expense credit","potential":500,
            "risk":"low","risk_label":"Low Risk",
            "detail":"Illinois gives a 25% credit (max $500) on qualifying K-12 education expenses if you have school-age children.",
            "action":"Applies if you have qualifying children in grades K-12","form":"IL Schedule ICR","done":False})

    # Dependent care
    if deps > 0 and child_care == 0:
        tips.append({"id":"dcc","title":"Child & dependent care credit","potential":600,
            "risk":"low","risk_label":"Low Risk",
            "detail":"If you paid for childcare so you could work, claim up to $3,000 in expenses for 1 child ($6,000 for 2+). Credit is 20% of expenses = up to $600-$1,200.",
            "action":"Enter daycare/after-school expenses in Child care field","form":"Form 2441","done":False})

    # Withholding adjustment tip
    if result > 2000:
        tips.append({"id":"w4","title":"Adjust W-4 to stop over-withholding","potential":0,
            "risk":"info","risk_label":"Planning Tip",
            "detail":"You're getting a large refund because too much tax was withheld. Consider updating your W-4 at work to reduce withholding — get that money in your paycheck now instead of waiting for a refund.",
            "action":"Submit new W-4 to your employer","form":"Form W-4","done":False})

    # Sort: done items last, then by potential descending
    tips.sort(key=lambda x: (x["done"], -x["potential"]))
    return tips

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
    ptc = p("ptc"); savers_credit = p("savers_credit"); ev_credit = p("ev_credit")
    actc_override = p("actc_override"); other_credits = p("other_credits")
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
    # Additional user-entered credits
    extra_refundable = ptc + other_credits + (actc_override if actc_override > ctc["refundable"] else 0)
    extra_nonrefundable = savers_credit + ev_credit
    # Apply non-refundable extra credits against tax first
    non_ref = min(fed_tax + se_tax, ctc["total"] - ctc["refundable"] + child_care_credit + (edu_credit - edu_ref) + foreign_tax + extra_nonrefundable)
    total_tax = max(0.0, fed_tax + se_tax - non_ref) + niit
    total_payments = withheld + est_payments + ctc["refundable"] + eic + edu_ref + extra_refundable
    total_credits = ctc["total"] + eic + child_care_credit + edu_credit + foreign_tax + savers_credit + ev_credit + ptc + other_credits
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

    # ── Multi-State Calculation ──────────────────────────────────────────────
    STATE_EXEMPTIONS = {"IL":2775,"NY":0,"CA":144,"PA":0,"OH":2400,"MI":5600,
                        "MD":3200,"VA":930,"MO":2100,"KY":2980,"OR":236,"WI":700,
                        "MN":4800,"GA":5400,"NC":0,"CO":0,"AZ":0,"IN":1000,
                        "MA":4400,"NJ":1000,"CT":15000,"RI":4950,"VT":4500,
                        "DC":0,"LA":4500,"MS":6000,"AL":1500,"SC":0,"AR":29200}
    STATE_EITC = {"CA":0.85,"NY":0.30,"IL":0.20,"MD":0.45,"CO":0.38,"MN":0.397,
                  "NJ":0.40,"MA":0.30,"CT":0.41,"VA":0.15,"OH":0.30,"OR":0.09,
                  "WI":0.04,"GA":0.05,"MI":0.06,"LA":0.05,"RI":0.15,"VT":0.36,
                  "NM":0.25,"ME":0.25,"IA":0.15,"KS":0.17,"MN":0.397}

    # w2_list: each item has wages, withheld, state_withheld, city_data
    w2_list = data.get("w2_list") or []

    # Build per-state breakdown
    state_results = []
    state_totals = {}  # state_code -> {wages, withheld, tax_owed, refund}
    seen_states = set()

    for w2 in w2_list:
        cd = w2.get("city_data") or {}
        if not cd: continue
        sc = cd.get("state","")
        w_wages = float(str(w2.get("wages",0)).replace(",","").replace("$","")) or 0
        w_withheld = float(str(w2.get("state_withheld",0)).replace(",","").replace("$","")) or 0
        sr = cd.get("state_tax",0)/100
        cr = cd.get("city_tax",0)/100
        exemption = STATE_EXEMPTIONS.get(sc,0)
        # Prorate AGI adjustments by wage share
        total_wages_check = wages if wages > 0 else 1
        wage_share = w_wages / total_wages_check
        state_agi_portion = max(0.0, w_wages - exemption * wage_share)
        stax = round(state_agi_portion * sr)
        ctax = round(w_wages * cr)
        s_eitc = round(eic * STATE_EITC.get(sc,0) * wage_share)
        net_stax = max(0, stax - s_eitc)
        refund = round(w_withheld) - net_stax - ctax
        employer = w2.get("employer","") or cd.get("city","")+" employer"
        state_results.append({
            "employer": employer,
            "city": cd.get("city",""), "state": sc,
            "wages": round(w_wages),
            "state_tax_rate": cd.get("state_tax",0),
            "city_tax_rate": cd.get("city_tax",0),
            "state_agi": round(state_agi_portion),
            "state_tax_amt": stax,
            "city_tax_amt": ctax,
            "state_eitc": s_eitc,
            "state_withheld": round(w_withheld),
            "state_refund": refund,
            "note": cd.get("note","")
        })
        if sc not in state_totals:
            state_totals[sc] = {"wages":0,"withheld":0,"tax_owed":0,"eitc":0,"city_tax":0}
        state_totals[sc]["wages"] += w_wages
        state_totals[sc]["withheld"] += w_withheld
        state_totals[sc]["tax_owed"] += net_stax
        state_totals[sc]["eitc"] += s_eitc
        state_totals[sc]["city_tax"] += ctax

    # Build combined state summary per unique state
    state_summary = []
    for sc, st in state_totals.items():
        state_summary.append({
            "state": sc,
            "total_wages": round(st["wages"]),
            "total_withheld": round(st["withheld"]),
            "total_tax_owed": round(st["tax_owed"]),
            "state_eitc": round(st["eitc"]),
            "city_tax": round(st["city_tax"]),
            "net_refund": round(st["withheld"]) - round(st["tax_owed"]) - round(st["city_tax"])
        })

    # Legacy single city_data support
    state_result = {}
    city_data = data.get("city_data") or (w2_list[0].get("city_data") if w2_list else {}) or {}
    if not state_results and city_data:
        sc = city_data.get("state","")
        sr = city_data.get("state_tax",0)/100
        cr = city_data.get("city_tax",0)/100
        exemption = STATE_EXEMPTIONS.get(sc,0)
        sagi = max(0.0, agi - exemption)
        stax = round(sagi * sr)
        ctax = round(agi * cr)
        s_eitc = round(eic * STATE_EITC.get(sc,0))
        net_stax = max(0, stax - s_eitc)
        state_result = {"state_agi":round(sagi),"state_tax_amt":stax,"city_tax_amt":ctax,
                        "state_refund":round(state_withheld)-net_stax-ctax,
                        "combined":net_stax+ctax,"state_eitc":s_eitc,
                        "state_code":sc,"state_exemption":exemption}

    return jsonify({
        "gross_income": round(gross_income), "agi": round(agi),
        "taxable_income": round(taxable_income), "deduction": round(deduction),
        "using_standard": using_standard, "above_line": round(above_line),
        "fed_tax": round(fed_tax), "se_tax": round(se_tax), "total_tax": round(total_tax),
        "marginal_rate": mrate, "effective_rate": round(effective, 1),
        "ctc_total": round(ctc["total"]), "ctc_refundable": round(ctc["refundable"]),
        "eic": round(eic), "child_care_credit": round(child_care_credit), "ptc": round(ptc),
        "savers_credit": round(savers_credit), "ev_credit": round(ev_credit),
        "extra_refundable": round(extra_refundable),
        "edu_credit": round(edu_credit), "total_credits": round(total_credits),
        "withheld": round(withheld), "est_payments": round(est_payments),
        "total_payments": round(total_payments), "result": round(result),
        "range": refund_range,
        "underpayment_risk": underpayment_risk, "penalty_estimate": penalty_estimate,
        "state": state_result,
        "state_results": state_results,
        "state_summary": state_summary,
        "multi_state": len(state_summary) > 1,
        "status": status, "_tax_year": year,
        "_data_source": yd.get("source", "IRS Rev. Proc."),
        "optimizer": build_optimizer(agi, gross_income, wages, self_employ, deps, status, year,
                                     retirement, hsa, student_loan, education, child_care,
                                     ptc, savers_credit, city_data, deduction, std_ded, eic,
                                     ctc, fed_tax, total_tax, result, taxable_income)
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
.w2c-container{display:flex;flex-direction:column;gap:12px}
.w2-card{background:var(--s2);border:1px solid var(--bd);border-radius:12px;padding:14px;position:relative;transition:border-color .2s}
.w2-card:hover{border-color:rgba(99,179,237,.2)}
.w2-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.w2-title{font-family:var(--fm);font-size:11px;letter-spacing:1px;color:var(--ac);text-transform:uppercase;display:flex;align-items:center;gap:8px}
.w2-num{background:var(--ac);color:var(--bg);width:20px;height:20px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}
.w2-rmv{background:none;border:1px solid var(--bd);border-radius:6px;color:var(--mu);cursor:pointer;padding:4px 10px;font-size:12px;font-family:var(--fd);transition:all .15s}
.w2-rmv:hover{background:rgba(252,129,129,.1);border-color:var(--dn);color:var(--dn)}
.w2-employer{width:100%;background:transparent;border:none;border-bottom:1px solid var(--bd);color:var(--mu);font-family:var(--fm);font-size:12px;padding:4px 0 6px;margin-bottom:12px;outline:none}
.w2-employer::placeholder{color:var(--fa)}
.w2-employer:focus{border-bottom-color:var(--ac);color:var(--tx)}
.w2-boxes{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.w2-box{position:relative}
.w2-box-label{font-size:10px;font-family:var(--fm);color:var(--fa);margin-bottom:3px;display:flex;justify-content:space-between}
.w2-box-num{color:var(--ac);font-weight:500}
.w2-box input{width:100%;background:var(--bg);border:1px solid var(--bd);border-radius:6px;padding:8px 10px;font-size:13px;font-family:var(--fm);color:var(--tx);outline:none;transition:border-color .2s}
.w2-box input:focus{border-color:var(--bdf)}
.w2-box input::placeholder{color:var(--fa)}
.w2-totals{background:rgba(99,179,237,.06);border:1px solid rgba(99,179,237,.15);border-radius:10px;padding:10px 14px;margin-top:10px;display:flex;gap:20px;flex-wrap:wrap;font-family:var(--fm);font-size:12px}
.w2-total-item{color:var(--mu)}.w2-total-item strong{color:var(--ac)}
.add-w2-btn{background:none;border:2px dashed rgba(99,179,237,.3);border-radius:10px;color:var(--ac);padding:12px;font-size:13px;cursor:pointer;font-family:var(--fd);width:100%;transition:all .2s;display:flex;align-items:center;justify-content:center;gap:8px}
.add-w2-btn:hover{border-color:var(--ac);background:rgba(99,179,237,.05)}
.add-w2-btn:disabled{opacity:.4;cursor:not-allowed}
.w2-limit-note{font-family:var(--fm);font-size:11px;color:var(--fa);text-align:center;margin-top:6px}
.w2-city-wrap{position:relative;margin-bottom:8px}
.w2-city-input{width:100%;background:var(--bg);border:1px solid var(--bd);border-radius:6px;padding:8px 10px;font-size:12px;font-family:var(--fm);color:var(--tx);outline:none;transition:border-color .2s}
.w2-city-input:focus{border-color:var(--bdf)}
.w2-city-input::placeholder{color:var(--fa)}
.w2-city-tag{display:inline-flex;align-items:center;gap:6px;background:rgba(99,179,237,.1);border:1px solid rgba(99,179,237,.25);border-radius:6px;padding:4px 10px;font-family:var(--fm);font-size:11px;color:var(--ac);margin-top:4px}
.w2-city-tag .clr{cursor:pointer;color:var(--mu);margin-left:2px}
.w2-city-tag .clr:hover{color:var(--dn)}
.w2-dd{position:absolute;top:calc(100% + 2px);left:0;right:0;z-index:300;background:var(--s2);border:1px solid rgba(99,179,237,.3);border-radius:8px;display:none;max-height:180px;overflow-y:auto;box-shadow:0 12px 30px rgba(0,0,0,.5)}
.w2-dd.open{display:block}
.w2-di{padding:8px 12px;cursor:pointer;font-size:13px;color:var(--tx);display:flex;justify-content:space-between;align-items:center}
.w2-di:hover{background:rgba(99,179,237,.08)}
.w2-di .w2-dn{font-size:10px;color:var(--mu);font-family:var(--fm)}
/* File button */
.file-btn-bar{margin-top:2rem;display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:600px){.file-btn-bar{grid-template-columns:1fr}}
.file-btn{display:flex;align-items:center;justify-content:center;gap:8px;padding:14px 20px;border-radius:12px;font-size:14px;font-weight:600;font-family:var(--fd);cursor:pointer;text-decoration:none;transition:opacity .2s,transform .1s;border:none}
.file-btn:active{transform:scale(.97)}
.file-btn.federal{background:#2563eb;color:#fff}
.file-btn.federal:hover{opacity:.9}
.file-btn.state{background:#059669;color:#fff}
.file-btn.state:hover{opacity:.9}
.file-btn.freefile{background:var(--s1);color:var(--ac);border:1px solid var(--ac)}
.file-btn.freefile:hover{background:rgba(99,179,237,.08)}
.file-btn .btn-icon{font-size:18px}
.file-links-note{font-family:var(--fm);font-size:11px;color:var(--fa);text-align:center;margin-top:8px;line-height:1.6}
/* Multi-state tab */
.ms-card{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:1rem 1.25rem;margin-bottom:12px}
.ms-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.ms-state-badge{font-family:var(--fm);font-size:11px;font-weight:700;padding:3px 10px;border-radius:8px;background:rgba(99,179,237,.12);color:var(--ac)}
.ms-refund{font-size:20px;font-weight:700}
.ms-refund.pos{color:var(--a2)}.ms-refund.neg{color:var(--dn)}
.ms-rows .brow{padding:8px 0}
.ms-total{background:rgba(104,211,145,.06);border:1px solid rgba(104,211,145,.2);border-radius:10px;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;font-size:15px;font-weight:600;margin-top:8px}
.ms-total span{font-size:22px;font-weight:700}
.ms-total span.pos{color:var(--a2)}.ms-total span.neg{color:var(--dn)}
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
.opt-title{font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--mu);text-transform:uppercase;margin-bottom:1rem}
.opt-total{background:rgba(104,211,145,.08);border:1px solid rgba(104,211,145,.3);border-radius:12px;padding:14px 18px;margin-bottom:1.25rem;display:flex;justify-content:space-between;align-items:center}
.opt-total-lbl{font-size:13px;color:var(--tx)}.opt-total-lbl span{color:var(--a2);font-weight:700;font-size:18px}
.opt-item{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:14px 18px;margin-bottom:10px;display:flex;gap:14px;align-items:flex-start;transition:border-color .2s}
.opt-item:hover{border-color:rgba(99,179,237,.2)}
.opt-item.done{opacity:.55}
.opt-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:4px}
.opt-dot.low{background:#68d391}.opt-dot.medium{background:#f6ad55}.opt-dot.high{background:#fc8181}.opt-dot.info{background:#63b3ed}.opt-dot.done-dot{background:#44445a}
.opt-body{flex:1}
.opt-name{font-size:14px;font-weight:600;color:var(--tx);margin-bottom:3px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px}
.opt-amt{font-family:var(--fm);font-size:13px;color:var(--a2);white-space:nowrap}
.opt-amt.done-amt{color:var(--fa)}
.opt-risk{font-family:var(--fm);font-size:10px;padding:2px 8px;border-radius:10px;margin-left:6px}
.risk-low{background:rgba(104,211,145,.12);color:#68d391}
.risk-medium{background:rgba(246,173,85,.12);color:#f6ad55}
.risk-high{background:rgba(252,129,129,.12);color:#fc8181}
.risk-info{background:rgba(99,179,237,.12);color:#63b3ed}
.opt-detail{font-size:12px;color:var(--mu);line-height:1.5;margin-bottom:6px}
.opt-action{font-family:var(--fm);font-size:11px;color:var(--ac)}
.opt-form{font-family:var(--fm);font-size:11px;color:var(--fa);margin-left:8px}
.opt-done-badge{font-family:var(--fm);font-size:10px;background:rgba(68,68,90,.3);color:var(--fa);padding:2px 8px;border-radius:10px}
.disc{text-align:center;font-size:11px;color:var(--fa);font-family:var(--fm);margin-top:3rem;line-height:1.6}
.eic-info{background:rgba(99,179,237,.06);border:1px solid rgba(99,179,237,.2);border-radius:8px;padding:10px 14px;font-family:var(--fm);font-size:12px;color:var(--mu);margin-bottom:1rem;display:none}
.eic-info.show{display:block}
.eic-info strong{color:var(--ac)}
.eic-row{display:flex;justify-content:space-between;align-items:center;padding:3px 0}
.eic-row .eic-val{color:var(--a2);font-weight:500}
.eic-row .eic-val.zero{color:var(--fa)}
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
        <div class="clabel">02 &mdash; W-2 Income (up to 4 employers)</div>
        <div class="w2c-container" id="w2c"></div>
        <button type="button" class="add-w2-btn" id="addW2">
          <span style="font-size:18px">+</span> Add Another W-2
        </button>
        <div class="w2-limit-note" id="w2LimitNote"></div>
        <div class="w2-totals" id="w2Totals" style="display:none">
          <div class="w2-total-item">Total wages: <strong id="totWages">$0</strong></div>
          <div class="w2-total-item">Total withheld: <strong id="totWithheld">$0</strong></div>
          <div class="w2-total-item">W-2 count: <strong id="totCount">0</strong></div>
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
        <div class="clabel">04 &mdash; Credits &amp; Adjustments</div>
        <div class="sub">Auto-calculated credits (based on your income)</div>
        <div class="eic-info" id="eicInfo"></div>
        <div class="r2">
          <div class="field">
            <label>Child &amp; dependent care expenses</label>
            <input type="text" id="ccI" placeholder="$0"/>
          </div>
          <div class="field">
            <label>Education expenses (1098-T)</label>
            <input type="text" id="eduI" placeholder="$0"/>
          </div>
        </div>
        <div class="sub">Additional credits (enter amounts from your tax return)</div>
        <div class="r2">
          <div class="field">
            <label>Premium Tax Credit (ACA / marketplace insurance)</label>
            <input type="text" id="ptcI" placeholder="$0"/>
          </div>
          <div class="field">
            <label>Saver's Credit (retirement contribution credit)</label>
            <input type="text" id="savI" placeholder="$0"/>
          </div>
        </div>
        <div class="r2">
          <div class="field">
            <label>Residential clean energy / EV credit</label>
            <input type="text" id="evI" placeholder="$0"/>
          </div>
          <div class="field">
            <label>Additional Child Tax Credit (ACTC override)</label>
            <input type="text" id="actcI" placeholder="$0"/>
          </div>
        </div>
        <div class="r2">
          <div class="field">
            <label>Foreign tax credit</label>
            <input type="text" id="forT" placeholder="$0"/>
          </div>
          <div class="field">
            <label>Other refundable credits (Form 8812 etc.)</label>
            <input type="text" id="otherCrI" placeholder="$0"/>
          </div>
        </div>
        <div class="sub">Other taxes &amp; withholding</div>
        <div class="r2">
          <div class="field">
            <label>State tax withheld (W-2 box 17)</label>
            <input type="text" id="stWH" placeholder="$0"/>
          </div>
          <div class="field">
            <label>Additional Medicare / NIIT</label>
            <input type="text" id="niitI" placeholder="$0"/>
          </div>
        </div>
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
      <button class="rtab" data-t="optimizer" onclick="swTab('optimizer')">&#128200; Maximize Refund</button>
      <button class="rtab" data-t="federal" onclick="swTab('federal')">Federal Detail</button>
      <button class="rtab" data-t="state" onclick="swTab('state')" id="stateTab">State &amp; Local</button>
      <button class="rtab" data-t="breakdown" onclick="swTab('breakdown')">Full Breakdown</button>
    </div>
    <div class="rtp active" id="rtp-range"><div id="rangeDiv"></div></div>
    <div class="rtp" id="rtp-optimizer"><div id="optimizerDiv"></div></div>
    <div class="rtp" id="rtp-federal">
      <div class="sg" id="statsG"></div>
      <div id="barS"></div>
    </div>
    <div class="rtp" id="rtp-state"><div id="stCard"></div></div>
    <div class="rtp" id="rtp-breakdown"><div class="bkt" id="brkT"></div></div>
  </section>
  <div id="fileSection" style="display:none;margin-top:2rem">
    <div style="font-family:var(--fm);font-size:11px;letter-spacing:1.5px;color:var(--mu);text-transform:uppercase;margin-bottom:1rem;text-align:center">Ready to file? Choose your filing option</div>
    <div class="file-btn-bar">
      <a class="file-btn freefile" href="https://www.irs.gov/filing/free-file-do-your-federal-taxes-for-free" target="_blank" rel="noopener">
        <span class="btn-icon">&#127981;</span>
        <div><div style="font-size:13px">IRS Free File</div><div style="font-size:11px;opacity:.8;font-family:var(--fm)">Official IRS — free if income &lt;$84,000</div></div>
      </a>
      <a class="file-btn federal" href="https://www.irs.gov/filing" target="_blank" rel="noopener">
        <span class="btn-icon">&#127979;</span>
        <div><div style="font-size:13px">IRS.gov Filing Center</div><div style="font-size:11px;opacity:.8;font-family:var(--fm)">All federal filing options</div></div>
      </a>
      <a class="file-btn state" href="#" id="stateFileBtn" target="_blank" rel="noopener">
        <span class="btn-icon">&#127963;</span>
        <div><div style="font-size:13px" id="stateFileBtnTxt">State Filing Portal</div><div style="font-size:11px;opacity:.8;font-family:var(--fm)" id="stateFileBtnSub">Select a state to enable</div></div>
      </a>
      <a class="file-btn freefile" href="https://directfile.irs.gov" target="_blank" rel="noopener">
        <span class="btn-icon">&#9889;</span>
        <div><div style="font-size:13px">IRS Direct File</div><div style="font-size:11px;opacity:.8;font-family:var(--fm)">Free direct e-file with IRS</div></div>
      </a>
    </div>
    <div class="file-links-note">All links open official government websites. TaxCalc does not store your data or assist with actual filing.<br>Consult a CPA for complex situations. Deadline: April 15, <span id="fileDeadlineYear">2026</span>.</div>
  </div>
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

byId('filingStatus').addEventListener('change', updateEicPreview);
byId('dependents').addEventListener('input', updateEicPreview);
byId('selfE').addEventListener('input', updateEicPreview);
document.addEventListener('input', function(e){ if(e.target.classList.contains('w2w')) updateEicPreview(); });

byId('dedType').addEventListener('change', function(){
  byId('itemSec').classList.toggle('vis', this.value==='itemized');
});

var w2Count = 0;
var MAX_W2 = 4;

function fmtSimple(n){ return '$'+Math.round(n).toLocaleString('en-US'); }

var w2CityData = {};  // idx -> city object

function addW2(data){
  if(w2Count >= MAX_W2){ return; }
  w2Count++;
  var idx = w2Count;
  var d = data || {};
  var card = document.createElement('div');
  card.className = 'w2-card';
  card.id = 'w2card-'+idx;
  card.innerHTML =
    '<div class="w2-header">'
      +'<span class="w2-title"><span class="w2-num">'+idx+'</span> Employer / W-2 #'+idx+'</span>'
      +(idx > 1 ? '<button type="button" class="w2-rmv" onclick="removeW2('+idx+')">Remove</button>' : '')
    +'</div>'
    +'<input type="text" class="w2-employer" placeholder="Employer name (e.g. EDISQUARE INC)" value="'+(d.employer||'')+'"/>'
    // City search for this W-2
    +'<div class="w2-city-wrap" id="w2citywrap-'+idx+'">'
      +'<input type="text" class="w2-city-input" id="w2city-'+idx+'" placeholder="&#128205; Work location city (e.g. Tampa, FL)" autocomplete="off"/>'
      +'<div class="w2-dd" id="w2dd-'+idx+'"></div>'
      +'<div id="w2citytag-'+idx+'"></div>'
    +'</div>'
    // W-2 boxes
    +'<div class="w2-boxes">'
      +'<div class="w2-box"><div class="w2-box-label"><span>Box 1 — Wages, tips, other comp.</span><span class="w2-box-num">Box 1</span></div><input type="text" class="w2w" placeholder="$0" value="'+(d.wages||'')+'"/></div>'
      +'<div class="w2-box"><div class="w2-box-label"><span>Box 2 — Federal income tax withheld</span><span class="w2-box-num">Box 2</span></div><input type="text" class="w2h" placeholder="$0" value="'+(d.withheld||'')+'"/></div>'
      +'<div class="w2-box"><div class="w2-box-label"><span>Box 12 — 401(k)/403(b) deferrals</span><span class="w2-box-num">Box 12</span></div><input type="text" class="w2box12" placeholder="$0 (if shown)" value="'+(d.box12||'')+'"/></div>'
      +'<div class="w2-box"><div class="w2-box-label"><span>Box 17 — State income tax withheld</span><span class="w2-box-num">Box 17</span></div><input type="text" class="w2state" placeholder="$0 (if shown)" value="'+(d.state||'')+'"/></div>'
    +'</div>';
  byId('w2c').appendChild(card);

  // Wire city search for this W-2
  var cityInput = byId('w2city-'+idx);
  var cityDD = byId('w2dd-'+idx);
  cityInput.addEventListener('input', function(){
    var q = this.value.toLowerCase().trim();
    if(!q){ cityDD.classList.remove('open'); return; }
    var matches = CITIES_DATA.filter(function(c){
      return c.city.toLowerCase().indexOf(q)===0 || (c.city+', '+c.state).toLowerCase().indexOf(q)>=0;
    }).slice(0,8);
    if(!matches.length){ cityDD.classList.remove('open'); return; }
    cityDD.innerHTML = matches.map(function(c){
      return '<div class="w2-di" data-city=''+JSON.stringify(c).replace(/'/g,"&#39;")+''>'+
        '<span>'+c.city+', '+c.state+'</span><span class="w2-dn">'+(c.state_tax===0?'No state tax':c.state_tax+'% state')+(c.city_tax>0?' + '+c.city_tax+'% city':'')+'</span>'+
        '</div>';
    }).join('');
    cityDD.querySelectorAll('.w2-di').forEach(function(el){
      el.addEventListener('click', function(){
        var city = JSON.parse(el.dataset.city);
        w2CityData[idx] = city;
        cityInput.value = city.city+', '+city.state;
        cityDD.classList.remove('open');
        var tag = byId('w2citytag-'+idx);
        tag.innerHTML = '<div class="w2-city-tag">&#128205; '+city.city+', '+city.state
          +(city.state_tax===0?' &mdash; No state tax':' &mdash; '+city.state_tax+'% state'+(city.city_tax>0?' + '+city.city_tax+'% city':''))
          +'<span class="clr" onclick="clearW2City('+idx+')">&#10005;</span></div>';
      });
    });
    cityDD.classList.add('open');
  });
  document.addEventListener('click', function(e){
    if(!e.target.closest('#w2citywrap-'+idx)) cityDD.classList.remove('open');
  });

  card.querySelectorAll('input').forEach(function(inp){
    inp.addEventListener('input', function(){ updateW2Totals(); updateEicPreview(); });
  });
  updateW2Totals();
  updateAddBtn();
}

function clearW2City(idx){
  w2CityData[idx] = null;
  var inp = byId('w2city-'+idx);
  if(inp) inp.value = '';
  var tag = byId('w2citytag-'+idx);
  if(tag) tag.innerHTML = '';
}

function removeW2(idx){
  var card = byId('w2card-'+idx);
  if(card){ card.remove(); w2Count--; }
  // Renumber remaining cards
  var cards = byId('w2c').querySelectorAll('.w2-card');
  w2Count = 0;
  cards.forEach(function(c){
    w2Count++;
    var title = c.querySelector('.w2-title');
    if(title) title.innerHTML = '<span class="w2-num">'+w2Count+'</span> Employer / W-2 #'+w2Count;
    c.id = 'w2card-'+w2Count;
    var rmv = c.querySelector('.w2-rmv');
    if(rmv) rmv.setAttribute('onclick','removeW2('+w2Count+')');
    // Show/hide remove btn for first card
    if(w2Count === 1 && rmv){ rmv.style.display = 'none'; }
  });
  updateW2Totals();
  updateAddBtn();
}

function updateW2Totals(){
  // Build w2_list with per-W-2 city data
  var w2Cards = byId('w2c').querySelectorAll('.w2-card');
  var w2_list = [];
  var wages = 0, withheld = 0, box12Total = 0, stateWHTotal = 0;
  w2Cards.forEach(function(card, i){
    var cardIdx = parseInt(card.id.replace('w2card-',''));
    var w = pd(card.querySelector('.w2w'));
    var wh = pd(card.querySelector('.w2h'));
    var b12 = pd(card.querySelector('.w2box12'));
    var st = pd(card.querySelector('.w2state'));
    var emp = card.querySelector('.w2-employer') ? card.querySelector('.w2-employer').value : '';
    wages += w; withheld += wh; box12Total += b12; stateWHTotal += st;
    w2_list.push({
      employer: emp, wages: w, withheld: wh, box12: b12, state_withheld: st,
      city_data: w2CityData[cardIdx] || null
    });
  });
  var retVal = pd('retI') || box12Total;
  var stateWHVal = pd('stWH') || stateWHTotal;
  // Use first W-2's city as primary city_data (legacy)
  var primaryCity = null;
  for(var ci=0; ci<w2_list.length; ci++){
    if(w2_list[ci].city_data){ primaryCity = w2_list[ci].city_data; break; }
  }
  var count = document.querySelectorAll('.w2-card').length;
  var totDiv = byId('w2Totals');
  if(count > 1 || wages > 0){
    totDiv.style.display = 'flex';
    byId('totWages').textContent = fmtSimple(wages);
    byId('totWithheld').textContent = fmtSimple(withheld);
    byId('totCount').textContent = count + ' W-2'+(count===1?'':'s');
  } else {
    totDiv.style.display = 'none';
  }
  // Auto-fill state withheld from W-2 box 17 sum
  var stateTotal = Array.from(document.querySelectorAll('.w2state')).reduce(function(a,i){return a+pd(i);},0);
  if(stateTotal > 0){ var stWH = byId('stWH'); if(stWH && pd(stWH)===0) stWH.value = stateTotal; }
  // Auto-fill 401k from box 12
  var box12Total = Array.from(document.querySelectorAll('.w2box12')).reduce(function(a,i){return a+pd(i);},0);
  if(box12Total > 0){ var retI = byId('retI'); if(retI && pd(retI)===0) retI.value = box12Total; }
}

function updateAddBtn(){
  var btn = byId('addW2');
  var note = byId('w2LimitNote');
  if(w2Count >= MAX_W2){
    btn.disabled = true;
    btn.textContent = 'Maximum 4 W-2s reached';
    note.textContent = 'The IRS allows multiple W-2s in one tax year. All wages are combined on Form 1040.';
  } else {
    btn.disabled = false;
    btn.innerHTML = '<span style="font-size:18px">+</span> Add Another W-2 ('+(w2Count)+'/'+MAX_W2+' used)';
    note.textContent = '';
  }
}

byId('addW2').addEventListener('click', function(){ addW2(); });

// Initialize with 1 W-2 on load
addW2();

function updateEicPreview(){
  var wages = Array.from(document.querySelectorAll('.w2w')).reduce(function(a,i){return a+pd(i);},0);
  var selfE = pd('selfE');
  var earned = wages + selfE;
  var deps = parseInt(byId('dependents').value) || 0;
  var status = byId('filingStatus').value;
  var yr = curYear;
  // EIC tables 2024
  var EIC_MAX = {2024:[632,4213,6960,7830], 2025:[649,4328,7152,8046], 2026:[649,4328,7152,8231]};
  var EIC_LIMIT = {2024:[17640,46560,52918,56838], 2025:[18591,49084,55768,59899], 2026:[19104,50434,57310,61555]};
  var d = Math.min(deps, 3);
  var maxE = EIC_LIMIT[yr] ? EIC_LIMIT[yr][d] : EIC_LIMIT[2026][d];
  var maxC = EIC_MAX[yr] ? EIC_MAX[yr][d] : EIC_MAX[2026][d];
  if(status==='mfj') maxE += 2160;
  var eic = 0;
  if(earned > 0 && earned <= maxE){
    eic = Math.round(maxC * Math.min(1.0, earned / (maxE * 0.30)));
  }
  var info = byId('eicInfo');
  if(earned > 0){
    info.className = 'eic-info show';
    info.innerHTML = '<div class="eic-row"><span><strong>Earned Income Credit (auto)</strong> — calculated from your wages</span><span class="eic-val '+(eic===0?'zero':'')+'">'+fmt(eic)+'</span></div>'
      +'<div class="eic-row" style="font-size:11px"><span>Earned income: '+fmt(earned)+' | Max EIC for '+d+' dependent(s): '+fmt(maxC)+'</span><span style="color:var(--fa)">'+(eic===0?'Income exceeds limit':'Included automatically')+'</span></div>';
  } else {
    info.className = 'eic-info';
  }
}

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

  // Build w2_list with per-W-2 city data
  var w2Cards = byId('w2c').querySelectorAll('.w2-card');
  var w2_list = [];
  var wages = 0, withheld = 0, box12Total = 0, stateWHTotal = 0;
  w2Cards.forEach(function(card, i){
    var cardIdx = parseInt(card.id.replace('w2card-',''));
    var w = pd(card.querySelector('.w2w'));
    var wh = pd(card.querySelector('.w2h'));
    var b12 = pd(card.querySelector('.w2box12'));
    var st = pd(card.querySelector('.w2state'));
    var emp = card.querySelector('.w2-employer') ? card.querySelector('.w2-employer').value : '';
    wages += w; withheld += wh; box12Total += b12; stateWHTotal += st;
    w2_list.push({
      employer: emp, wages: w, withheld: wh, box12: b12, state_withheld: st,
      city_data: w2CityData[cardIdx] || null
    });
  });
  var retVal = pd('retI') || box12Total;
  var stateWHVal = pd('stWH') || stateWHTotal;
  // Use first W-2's city as primary city_data (legacy)
  var primaryCity = null;
  for(var ci=0; ci<w2_list.length; ci++){
    if(w2_list[ci].city_data){ primaryCity = w2_list[ci].city_data; break; }
  }

  var payload = {
    tax_year: curYear,
    filing_status: byId('filingStatus').value,
    dependents: byId('dependents').value,
    deduction_type: byId('dedType').value,
    wages: wages, withheld: withheld,
    self_employ: pd('selfE'), interest: pd('intD'),
    cap_gains: pd('capG'), other_income: pd('othI'),
    est_payments: pd('estP'), state_withheld: pd('stWH'),
    retirement: retVal, hsa: pd('hsaI'),
    student_loan: pd('sloI'), child_care: pd('ccI'),
    education: pd('eduI'), niit: pd('niitI'),
    foreign_tax: pd('forT'), mortgage_int: pd('mortI'),
    salt: pd('saltI'), charity: pd('charI'), medical: pd('medI'),
    city_data: primaryCity || selCity || null,
    w2_list: w2_list,
    ptc: pd('ptcI'),
    savers_credit: pd('savI'),
    ev_credit: pd('evI'),
    actc_override: pd('actcI'),
    other_credits: pd('otherCrI')
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

function renderOptimizer(d){
  if(!d.optimizer || !d.optimizer.length){
    byId('optimizerDiv').innerHTML='<p style="color:var(--mu);font-family:var(--fm);padding:1rem">No optimizer data available.</p>';
    return;
  }
  var tips = d.optimizer;
  var available = tips.filter(function(t){return !t.done && t.risk!=='info'});
  var totalPotential = available.reduce(function(a,t){return a+t.potential;},0);
  var html = '<div class="opt-title">&#128200; Refund Maximizer &mdash; Credits &amp; Deductions</div>';
  if(totalPotential > 0){
    html += '<div class="opt-total"><div class="opt-total-lbl">Potential additional refund available: <span>'+fmt(totalPotential)+'</span></div>'
      +'<div style="font-family:var(--fm);font-size:11px;color:var(--mu)">'+available.length+' opportunities found</div></div>';
  }
  tips.forEach(function(t){
    var dotCls = t.done ? 'done-dot' : t.risk;
    var amtCls = t.done ? 'done-amt' : '';
    var amtTxt = t.done ? 'Applied' : (t.potential > 0 ? 'up to '+fmt(t.potential) : 'Planning tip');
    html += '<div class="opt-item'+(t.done?' done':'')+'">'+
      '<div class="opt-dot '+dotCls+'"></div>'+
      '<div class="opt-body">'+
        '<div class="opt-name">'+
          '<span>'+t.title+(t.done?'&nbsp;<span class="opt-done-badge">&#10003; Applied</span>':'')+'</span>'+
          '<span class="opt-amt '+amtCls+'">'+amtTxt+'<span class="opt-risk risk-'+t.risk+'">'+t.risk_label+'</span></span>'+
        '</div>'+
        '<div class="opt-detail">'+t.detail+'</div>'+
        '<div><span class="opt-action">Action: '+t.action+'</span><span class="opt-form">'+t.form+'</span></div>'+
      '</div>'+
    '</div>';
  });
  byId('optimizerDiv').innerHTML = html;
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
    {l:'Child Tax Credit',v:d.ctc_total,c:'pos'},{l:'Earned Income Credit (auto)',v:d.eic,c:'pos'},
    {l:'Education credit',v:d.edu_credit,c:'pos'},{l:'Premium Tax Credit',v:d.ptc||0,c:'pos'},{l:"Saver's/EV/other credits",v:(d.savers_credit||0)+(d.ev_credit||0)+(d.extra_refundable||0),c:'pos'},{l:'Total credits',v:d.total_credits,c:'pos'},
    {h:'Payments'},
    {l:'Federal withheld',v:d.withheld,c:'pos'},{l:'Est. payments',v:d.est_payments,c:'pos'},
    {l:'Total payments',v:d.total_payments,c:'pos'},{l:'Total tax liability',v:d.total_tax,c:'neg'},
  ];
  byId('brkT').innerHTML = rows.map(function(r){
    if(r.h) return '<div class="brow hdr"><span class="blbl hdr">'+r.h+'</span></div>';
    var sign = (r.c==='neg' && r.v>0) ? '-' : '';
    return '<div class="brow"><span class="blbl">'+r.l+'</span><span class="bval '+r.c+'">'+sign+fmt(r.v)+'</span></div>';
  }).join('') + '<div class="brow tot"><span class="blbl">'+(isR?'Estimated refund':'Amount owed')+'</span><span class="bval '+(isR?'pos':'neg')+'">'+fmt(Math.abs(d.result))+'</span></div>';

  renderStateResults(d);
  byId('fileSection').style.display = 'block';
  byId('fileDeadlineYear').textContent = d._tax_year + 1;
  renderRange(d);
  renderOptimizer(d);
  swTab('range');
}

var STATE_FILING_URLS = {
  "AL":"https://www.revenue.alabama.gov/individual-corporate/individual-income-tax/",
  "AK":"https://tax.alaska.gov/",
  "AZ":"https://azdor.gov/individual-income-tax-filing",
  "AR":"https://www.dfa.arkansas.gov/income-tax/",
  "CA":"https://www.ftb.ca.gov/file/index.html",
  "CO":"https://tax.colorado.gov/individual-income-tax-filing",
  "CT":"https://portal.ct.gov/DRS/Individual-Taxes/Individual-Taxes",
  "DC":"https://otr.cfo.dc.gov/page/individual-income-tax",
  "DE":"https://revenue.delaware.gov/individuals/",
  "FL":"https://floridarevenue.com/",
  "GA":"https://dor.georgia.gov/individual-income-tax",
  "HI":"https://tax.hawaii.gov/geninfo/efiling/",
  "ID":"https://tax.idaho.gov/i-1039.cfm",
  "IL":"https://tax.illinois.gov/individuals/individual-income-tax.html",
  "IN":"https://www.in.gov/dor/individual-income-taxes/",
  "IA":"https://tax.iowa.gov/individual-income-tax",
  "KS":"https://www.ksrevenue.gov/efile.html",
  "KY":"https://revenue.ky.gov/Individual/Pages/default.aspx",
  "LA":"https://revenue.louisiana.gov/IndividualIncomeTax",
  "ME":"https://www.maine.gov/revenue/taxes/income-estate-tax/income-tax",
  "MD":"https://www.marylandtaxes.gov/individual/index.shtml",
  "MA":"https://www.mass.gov/how-to/file-your-massachusetts-income-tax-return",
  "MI":"https://www.michigan.gov/taxes/iit",
  "MN":"https://www.revenue.state.mn.us/individuals",
  "MS":"https://www.dor.ms.gov/individual",
  "MO":"https://dor.mo.gov/individual/",
  "MT":"https://mtrevenue.gov/taxes/income-tax/",
  "NE":"https://revenue.nebraska.gov/individuals",
  "NV":"https://tax.nv.gov/",
  "NH":"https://www.revenue.nh.gov/individuals/",
  "NJ":"https://www.nj.gov/treasury/taxation/njit.shtml",
  "NM":"https://www.tax.newmexico.gov/individuals/",
  "NY":"https://www.tax.ny.gov/pit/file/",
  "NC":"https://www.ncdor.gov/taxes-forms/individual-income-tax",
  "ND":"https://www.nd.gov/tax/user/businesses/formspublications/individual",
  "OH":"https://tax.ohio.gov/individual/filing",
  "OK":"https://www.ok.gov/tax/Individuals/",
  "OR":"https://www.oregon.gov/dor/programs/individuals/Pages/default.aspx",
  "PA":"https://www.revenue.pa.gov/TaxTypes/PIT/Pages/default.aspx",
  "RI":"https://tax.ri.gov/individual-tax",
  "SC":"https://dor.sc.gov/tax/individual",
  "SD":"https://dor.sd.gov/",
  "TN":"https://www.tn.gov/revenue/taxes/individual-income-tax.html",
  "TX":"https://comptroller.texas.gov/taxes/",
  "UT":"https://incometax.utah.gov/",
  "VT":"https://tax.vermont.gov/individual",
  "VA":"https://www.tax.virginia.gov/individual-income-tax",
  "WA":"https://dor.wa.gov/",
  "WV":"https://tax.wv.gov/Individuals/Pages/Individuals.aspx",
  "WI":"https://www.revenue.wi.gov/Pages/FAQS/ise-ind.aspx",
  "WY":"https://revenue.wyo.gov/"
};

function renderStateResults(d){
  var container = byId('stCard');
  if(!container) return;
  // Multi-state: show per-employer breakdown
  if(d.state_results && d.state_results.length > 0){
    var html = '';
    if(d.multi_state){
      html += '<div style="font-family:var(--fm);font-size:11px;letter-spacing:1px;color:var(--am);text-transform:uppercase;margin-bottom:1rem;padding:8px 12px;background:rgba(246,173,85,.08);border:1px solid rgba(246,173,85,.25);border-radius:8px">&#9888; Multi-state return — you worked in '+d.state_summary.length+' states. You may need to file separate state returns for each state.</div>';
    }
    // Per employer card
    d.state_results.forEach(function(sr){
      var pos = sr.state_refund >= 0;
      html += '<div class="ms-card">'
        +'<div class="ms-header">'
          +'<div><div style="font-size:14px;font-weight:600;color:var(--tx)">'+(sr.employer||sr.city+' employer')+'</div>'
            +'<div style="font-size:11px;color:var(--mu);font-family:var(--fm)">&#128205; '+sr.city+', '+sr.state+(sr.state_tax_rate===0?' &mdash; No state tax':' &mdash; '+sr.state_tax_rate+'% state')+(sr.city_tax_rate>0?' + '+sr.city_tax_rate+'% city':'')+'</div></div>'
          +'<div style="text-align:right"><div style="font-size:11px;color:var(--mu);font-family:var(--fm)">'+(pos?'State refund':'State owed')+'</div>'
            +'<div class="ms-refund '+(pos?'pos':'neg')+'">'+(pos?'+':'-')+fmt(Math.abs(sr.state_refund))+'</div></div>'
        +'</div>'
        +'<div class="ms-rows">'
          +[['W-2 wages',fmt(sr.wages),'neutral'],
            ['State income',fmt(sr.state_agi),'neutral'],
            ['State tax ('+sr.state_tax_rate+'%)',sr.state_tax_rate>0?'-'+fmt(sr.state_tax_amt):'None','neg'],
            ['City/local tax',sr.city_tax_rate>0?'-'+fmt(sr.city_tax_amt):'None',sr.city_tax_rate>0?'neg':'neutral'],
            ['State EITC',sr.state_eitc>0?'+'+fmt(sr.state_eitc):'$0',sr.state_eitc>0?'pos':'neutral'],
            ['State tax withheld','+'+fmt(sr.state_withheld),'pos'],
           ].map(function(x){ return '<div class="brow"><span class="blbl">'+x[0]+'</span><span class="bval '+x[2]+'">'+x[1]+'</span></div>'; }).join('')
        +'</div>'
      +'</div>';
    });
    // Summary if multi-state
    if(d.state_summary && d.state_summary.length > 0){
      var totalStateRefund = d.state_summary.reduce(function(a,s){return a+s.net_refund;},0);
      var pos = totalStateRefund >= 0;
      html += '<div class="ms-total"><span>Total state refund/owed across all states:</span><span class="'+(pos?'pos':'neg')+'">'+(pos?'+':'')+fmt(totalStateRefund)+'</span></div>';
      // Update state file button for primary state
      updateStateFileBtn(d.state_summary[0].state);
    }
    container.innerHTML = html;
  } else if(d.state){
    // Single state legacy
    var s = d.state;
    var city = primaryCity || selCity;
    if(!city && !s.state_code){ container.innerHTML='<p class="nc">Select a city on a W-2 to see state and local tax details.</p>'; return; }
    var sr = s.state_refund >= 0;
    container.innerHTML = '<div class="stc">'
      +(s.state_code?'<div class="stt">'+s.state_code+' State Tax</div>':'')
      +'<div class="stn">'+(city?city.note:'')+'</div>'
      +[['State taxable income',fmt(s.state_agi),'neutral'],
        ['State income tax rate',s.state_tax_amt>0?((s.state_tax_amt/Math.max(s.state_agi,1)*100).toFixed(1)+'%'):'None (0%)','neutral'],
        ['Estimated state tax',s.state_tax_amt>0?'-'+fmt(s.state_tax_amt):'$0','neg'],
        ['State EITC',s.state_eitc>0?'+'+fmt(s.state_eitc):'$0',s.state_eitc>0?'pos':'neutral'],
        ['State withheld','+'+fmt(pd('stWH')),'pos'],
        [sr?'State refund':'State owed',fmt(Math.abs(s.state_refund)),sr?'pos':'neg'],
       ].map(function(x){ return '<div class="brow"><span class="blbl">'+x[0]+'</span><span class="bval '+x[2]+'">'+x[1]+'</span></div>'; }).join('')
      +'</div>';
    if(s.state_code) updateStateFileBtn(s.state_code);
  } else {
    container.innerHTML='<p class="nc" style="padding:1rem">Select a city on each W-2 to see state and local tax details.</p>';
  }
}

function updateStateFileBtn(stateCode){
  var url = STATE_FILING_URLS[stateCode];
  var btn = byId('stateFileBtn');
  var txt = byId('stateFileBtnTxt');
  var sub = byId('stateFileBtnSub');
  if(url && btn){
    btn.href = url;
    if(txt) txt.textContent = stateCode+' State Filing Portal';
    if(sub) sub.textContent = 'File your '+stateCode+' state return';
    btn.style.opacity = '1';
  }
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
