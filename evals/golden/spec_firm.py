"""Golden test world, part 1: the firm, its thesis, companies, deals, passes and people.

Everything here is fictional: Quillwater Ventures, its team, founders, funds and LPs
do not exist. "Today" in this world is Thursday 22 Oct 2026, 07:00 in Bangalore.
"""

NOW = "2026-10-22T07:00:00+05:30"
TZ = "Asia/Kolkata"
FIRM = {"name": "Quillwater Ventures", "domain": "quillwater.vc", "fund": "Fund II", "fund_size_usd": 80_000_000}

MEMBERS = [
    {"key": "aditi", "name": "Aditi Rao", "email": "aditi@quillwater.vc", "title": "Partner", "level": "partner"},
    {"key": "kabir", "name": "Kabir Shah", "email": "kabir@quillwater.vc", "title": "Principal", "level": "principal"},
    {"key": "meera", "name": "Meera Iyer", "email": "meera@quillwater.vc", "title": "Associate", "level": "associate"},
    {"key": "rohan", "name": "Rohan Das", "email": "rohan@quillwater.vc", "title": "Analyst", "level": "analyst"},
    {"key": "tara", "name": "Tara Menon", "email": "tara@quillwater.vc", "title": "Head of Platform", "level": "platform"},
    {"key": "vikram", "name": "Vikram Nair", "email": "vikram@quillwater.vc", "title": "CFO", "level": "finance"},
]

THESIS = {
    "sectors": ["fintech infrastructure", "b2b software for financial services"],
    "sector_keywords": [
        "payments infrastructure", "payment orchestration", "banking infrastructure", "core banking", "lending infrastructure",
        "embedded finance", "regtech", "compliance automation", "kyc", "aml", "fraud", "treasury", "reconciliation",
        "credit infrastructure", "account aggregator", "upi", "collections software", "underwriting", "insurtech infrastructure",
        "wealthtech infrastructure", "api banking", "card issuing", "settlement", "payouts", "lending os", "b2b fintech",
    ],
    "stages": ["pre-seed", "seed", "series a"],
    "check_min_usd": 500_000,
    "check_max_usd": 3_000_000,
    "geographies": ["india", "us-india"],
    "anti_patterns": ["consumer lending", "crypto trading", "d2c"],
    "statement": "Quillwater backs India-first fintech infrastructure and B2B software for financial services, pre-seed to Series A, "
                 "with first checks of $500K to $3M, in India and US-India cross-border. We avoid consumer lending without an "
                 "in-house risk team, crypto trading platforms and D2C brands.",
}

FIRM_SITE = (
    "# Quillwater Ventures\n\nWe are an early-stage fund for the plumbing of finance. Quillwater backs India-first fintech "
    "infrastructure and B2B software for financial services: payments, lending infrastructure, core banking, treasury, "
    "reconciliation, compliance, fraud and account aggregator rails.\n\nWe lead or co-lead pre-seed, seed and Series A rounds "
    "with first checks of $500K to $3M, in India and US-India cross-border companies.\n\nWhat we avoid: consumer lending "
    "without an in-house risk team, crypto trading platforms, and D2C brands.\n"
)

# key, name, domain, sector, hq, status, entry stage (portfolio), check_usd (portfolio)
PORTFOLIO = [
    ("orbit", "Orbit Treasury", "orbittreasury.in", "treasury management for mid-market companies", "Mumbai, India", "Seed", 1_500_000),
    ("kestrel", "Kestrel Pay", "kestrelpay.in", "payment orchestration", "Bangalore, India", "Seed", 2_000_000),
    ("ferro", "Ferro Credit Cloud", "ferrocredit.com", "lending infrastructure for NBFCs", "Pune, India", "Series A", 3_000_000),
    ("tallyfin", "Tallyfin", "tallyfin.com", "accounting and reconciliation APIs", "Delhi, India", "Seed", 1_200_000),
    ("saffire", "Saffire KYC", "saffirekyc.com", "KYC and AML automation", "Hyderabad, India", "Seed", 1_000_000),
    ("nimbus", "Nimbus Collect", "nimbuscollect.in", "collections software for lenders", "Bangalore, India", "Pre-seed", 600_000),
    ("quanta", "Quanta Rails", "quantarails.com", "UPI infrastructure for banks", "Mumbai, India", "Seed", 2_500_000),
    ("brightvault", "Brightvault", "brightvault.io", "wealthtech infrastructure APIs", "Bangalore, India", "Seed", 1_500_000),
    ("ledgerline", "Ledgerline", "ledgerline.io", "core banking for cooperative banks", "Pune, India", "Seed", 2_000_000),
    ("cardinal", "Cardinal Risk", "cardinalrisk.ai", "fraud detection for issuers", "Bangalore, India", "Seed", 1_800_000),
    ("harbor", "Harbor Insure Stack", "harborstack.in", "insurtech infrastructure", "Chennai, India", "Pre-seed", 750_000),
    ("mintrail", "Mintrail", "mintrail.in", "payroll finance APIs", "Gurugram, India", "Seed", 1_000_000),
]

# key, company, domain, sector text, hq, stage key, days in stage, owner, round, raise_usd, next_step, next_step_due (days from today), crm last contact (days ago), extra
DEALS = [
    # Inbound (dwell 3)
    ("paysa", "Paysa Labs", "paysa.in", "payouts infrastructure for marketplaces", "Bangalore, India", "inbound", 1, "rohan", "Seed", 1_800_000, None, None, 1, {}),
    ("coinvault", "Coinvault Exchange", "coinvault.io", "crypto trading app for retail investors", "Bangalore, India", "inbound", 2, "rohan", "Seed", 3_000_000, None, None, 2, {}),
    ("glowkart", "Glowkart", "glowkart.in", "D2C skincare brand", "Mumbai, India", "inbound", 1, "rohan", "Seed", 2_000_000, None, None, 1, {}),
    ("ruplink", "Ruplink", "ruplink.in", "account aggregator infrastructure", "Bangalore, India", "inbound", 5, "rohan", "Pre-seed", 800_000, None, None, 5, {}),
    ("sutra", "Sutra Compliance", "sutracompliance.com", "compliance automation for NBFCs", "Mumbai, India", "inbound", 2, "rohan", "Seed", 1_500_000, None, None, 2, {}),
    # Screening (dwell 7)
    ("vaultline", "Vaultline", "vaultline.in", "treasury APIs for startups", "Bangalore, India", "screening", 4, "rohan", "Seed", 2_000_000, "Screening call with founder", 2, 3, {}),
    ("nexa", "Nexa Lend OS", "nexalend.com", "lending OS for small banks", "Pune, India", "screening", 3, "rohan", "Seed", 2_500_000, "Read data room", 3, 2, {}),
    ("clearpath", "Clearpath Recon", "clearpathrecon.com", "reconciliation for payment aggregators", "Delhi, India", "screening", 11, "rohan", "Seed", 1_500_000, "Decide on first meeting", 2, 4, {}),
    ("ankur", "Ankur Credit Stack", "ankurstack.in", "credit infrastructure for rural lenders", "Jaipur, India", "screening", 2, "rohan", "Pre-seed", 700_000, "Book intro call", 4, 2, {}),
    ("fintegrate", "Fintegrate", "fintegrate.dev", "embedded finance APIs for SaaS", "San Francisco, US and Bangalore, India", "screening", 5, "rohan", "Seed", 3_000_000, "Customer reference check", 3, 3, {}),
    ("bharatrisk", "Bharat Risk Labs", "bharatrisk.in", "fraud models for UPI apps", "Hyderabad, India", "screening", 6, "rohan", "Seed", 1_200_000, "Screening memo", 1, 2, {}),
    # First meeting (dwell 7)
    ("zeno", "Zeno Treasury", "zenotreasury.com", "treasury management for exporters", "Mumbai, India", "first_meeting", 4, "meera", "Seed", 2_000_000, "Second meeting with CTO", 3, 3, {}),
    ("pillar", "Pillar KYC", "pillarkyc.in", "KYC orchestration", "Bangalore, India", "first_meeting", 3, "meera", "Seed", 1_500_000, "Product demo", 4, 2, {}),
    ("rivulet", "Rivulet Payments", "rivuletpay.com", "cross-border payment rails for SMBs", "Bangalore, India and Delaware, US", "first_meeting", 5, "meera", "Seed", 3_000_000, "Second meeting", 2, 3, {}),
    ("deccan", "Deccan Lend Cloud", "deccanlend.cloud", "lending infrastructure for gold loan NBFCs", "Hyderabad, India", "first_meeting", 2, "meera", "Pre-seed", 900_000, "Founder reference calls", 5, 2, {}),
    ("aster", "Aster Underwrite", "asteruw.ai", "AI underwriting for MSME lenders", "Bangalore, India", "first_meeting", 6, "meera", "Seed", 2_200_000, "Model walkthrough", 2, 4, {}),
    ("copperleaf", "Copperleaf Collect", "copperleaf.in", "collections software for microfinance", "Kolkata, India", "first_meeting", 5, "meera", "Seed", 1_400_000, "Second meeting", 3, 9, {"no_recent_contact": True}),
    ("halo", "Halo Reconcile", "haloreconcile.com", "reconciliation for insurers", "Chennai, India", "first_meeting", 12, "meera", "Seed", 1_600_000, "Second meeting", 2, 3, {}),
    # Second meeting (dwell 10)
    ("trellis", "Trellis Banking API", "trellisapi.in", "API banking platform", "Mumbai, India", "second_meeting", 5, "meera", "Series A", 6_000_000, "Diligence plan", 3, 2, {}),
    ("ember", "Ember Credit", "embercredit.in", "credit infrastructure for BNPL providers", "Bangalore, India", "second_meeting", 4, "meera", "Seed", 2_000_000, "Customer calls", 4, 3, {}),
    ("northwind", "Northwind Insure Stack", "northwindstack.com", "insurtech infrastructure for brokers", "Pune, India", "second_meeting", 6, "meera", "Seed", 1_800_000, "Partner intro", 3, 3, {}),
    ("sable", "Sable Fraud AI", "sablefraud.ai", "fraud detection for card issuers", "Bangalore, India", "second_meeting", 3, "meera", "Seed", 2_500_000, "Diligence kickoff", 2, 1, {}),
    ("juniper", "Juniper Payroll Rails", "juniperrails.in", "payroll payouts infrastructure", "Gurugram, India", "second_meeting", 7, "meera", "Seed", 1_700_000, "Reference checks", 3, 2, {}),
    ("mosaic", "Mosaic Wealth Infra", "mosaicwealth.io", "wealthtech infrastructure for RIAs", "Mumbai, India", "second_meeting", 15, "meera", "Seed", 2_000_000, "Diligence decision", 3, 3, {}),
    # Diligence (dwell 21)
    ("lumen", "Lumen Ledger", "lumenledger.com", "reconciliation SaaS for NBFCs", "Bangalore, India", "diligence", 9, "kabir", "Series A", 8_000_000, "Cohort analysis review", 4, 2, {}),
    ("kite", "Kite Pay", "kitepay.in", "payment orchestration for D2C-agnostic merchants", "Bangalore, India", "diligence", 3, "kabir", "Seed", 3_000_000, "Customer references", 5, 1, {}),
    ("vertex", "Vertex Card Issuing", "vertexcards.in", "card issuing platform for fintechs", "Mumbai, India", "diligence", 30, "kabir", "Series A", 7_000_000, "Tech diligence call", 5, 12, {"no_recent_contact": True}),
    ("banyanrisk", "Banyan Risk Cloud", "banyanrisk.com", "risk infrastructure and fraud for lenders", "Bangalore, India", "diligence", 10, "kabir", "Seed", 2_000_000, None, None, 3, {}),
    ("cobalt", "Cobalt AA", "cobaltaa.in", "account aggregator infrastructure", "Pune, India", "diligence", 12, "kabir", "Seed", 1_500_000, "Send diligence questions", -7, 4, {}),
    ("prism", "Prism Lending OS", "prismlend.com", "lending OS for co-lending partnerships", "Mumbai, India", "diligence", 8, "kabir", "Series A", 5_000_000, "Model review", 3, 20, {"fresh_email_days": 2}),
    # Partner meeting (dwell 7)
    ("ironwood", "Ironwood Compliance", "ironwoodcomply.com", "compliance automation for banks", "Mumbai, India", "partner_meeting", 3, "aditi", "Series A", 6_000_000, "IC on Monday", 4, 1, {}),
    ("solace", "Solace Treasury", "solacetreasury.in", "treasury for D2C-agnostic SMB exporters", "Bangalore, India", "partner_meeting", 9, "aditi", "Seed", 2_000_000, "Partner vote", 1, 3, {}),
    ("gravity", "Gravity Payouts", "gravitypayouts.com", "payouts infrastructure for gig platforms", "Bangalore, India", "partner_meeting", 4, "aditi", "Seed", 3_000_000, "Partner meeting Monday", 4, 2, {}),
    # Term sheet (dwell 10)
    ("atlas", "Atlas Settlement", "atlassettle.com", "settlement infrastructure for brokers", "Mumbai, India", "term_sheet", 5, "aditi", "Series A", 9_000_000, "Send term sheet markup", 1, 1, {}),
    ("beacon", "Beacon Credit Rails", "beaconrails.in", "credit infrastructure APIs", "Bangalore, India", "term_sheet", 4, "aditi", "Seed", 2_800_000, "Founder call on terms", 2, 2, {}),
    # Closing (dwell 30)
    ("orchid", "Orchid Cards", "orchidcards.in", "card issuing for corporates", "Bangalore, India", "closing", 12, "aditi", "Seed", 2_000_000, "Wire after CP sign-off", 6, 2, {}),
    ("sterling", "Sterling AA", "sterlingaa.com", "account aggregator for wealth platforms", "Mumbai, India", "closing", 9, "aditi", "Seed", 1_500_000, "Legal docs review", 5, 10, {"no_recent_contact": True}),
    # Portfolio (recent)
    ("ledgerline_d", "Ledgerline", "ledgerline.io", "core banking for cooperative banks", "Pune, India", "portfolio", 40, "aditi", "Seed", 2_000_000, None, None, 5, {"portfolio_key": "ledgerline"}),
    ("cardinal_d", "Cardinal Risk", "cardinalrisk.ai", "fraud detection for issuers", "Bangalore, India", "portfolio", 60, "kabir", "Seed", 1_800_000, None, None, 6, {"portfolio_key": "cardinal"}),
    # Passed
    ("fizzbuy", "Fizzbuy", "fizzbuy.in", "D2C beverages", "Delhi, India", "passed", 40, "rohan", "Seed", 2_000_000, None, None, 40, {}),
    ("moonlend", "Moonlend", "moonlend.in", "consumer lending app", "Bangalore, India", "passed", 35, "meera", "Seed", 3_000_000, None, None, 35, {}),
    ("tokenswap", "TokenSwap", "tokenswap.xyz", "crypto trading platform", "Singapore", "passed", 60, "rohan", "Seed", 4_000_000, None, None, 60, {}),
    ("parcelpro", "Parcelpro", "parcelpro.in", "logistics marketplace", "Mumbai, India", "passed", 50, "meera", "Series A", 10_000_000, None, None, 50, {}),
    ("dhanam", "Dhanam Neo", "dhanamneo.in", "consumer neobank", "Chennai, India", "passed", 45, "kabir", "Seed", 3_000_000, None, None, 45, {}),
    ("quickcash", "Quickcash", "quickcash.in", "consumer lending for students", "Pune, India", "passed", 30, "rohan", "Pre-seed", 1_000_000, None, None, 30, {}),
]

PASSES = [
    ("Fizzbuy", "fizzbuy.in", "2026-09-12", "D2C brand, outside thesis", None, "rohan"),
    ("Moonlend", "moonlend.in", "2026-09-17", "Consumer lending with no in-house risk team", "Risk team in place and two NBFC partners live", "meera"),
    ("TokenSwap", "tokenswap.xyz", "2026-08-23", "Crypto trading platform", None, "rohan"),
    ("Parcelpro", "parcelpro.in", "2026-09-02", "Logistics marketplace, outside thesis", None, "meera"),
    ("Dhanam Neo", "dhanamneo.in", "2026-09-07", "Consumer neobank, outside thesis", None, "kabir"),
    ("Quickcash", "quickcash.in", "2026-09-22", "Consumer lending", None, "rohan"),
    ("Paysa Labs", "paysa.in", "2026-03-12", "Too early: pre-product, no design partners", "Two marketplaces live on payouts", "rohan"),
    ("Vaultline", "vaultline.in", "2026-05-20", "Founder-market fit unclear", "A CFO-background co-founder joins", "kabir"),
    ("Ruplink", "ruplink.in", "2026-06-04", "AA licence pending", "AA licence granted", "rohan"),
    ("Wagerly", "wagerly.gg", "2026-02-10", "Real-money gaming, outside thesis", None, "rohan"),
    ("Cartwheel Retail", "cartwheel.shop", "2026-01-28", "D2C brand", None, "meera"),
    ("Lendquick", "lendquick.in", "2025-12-15", "Consumer lending", None, "kabir"),
    ("Chainmint", "chainmint.io", "2026-04-02", "Crypto trading", None, "rohan"),
    ("Stackfarm", "stackfarm.in", "2026-03-30", "Agritech marketplace, outside thesis", None, "meera"),
    ("Petpal", "petpal.in", "2026-02-21", "Consumer pet care, outside thesis", None, "rohan"),
    ("Tutorly", "tutorly.app", "2026-01-09", "Edtech, outside thesis", None, "meera"),
    ("Bytebrew", "bytebrew.dev", "2026-04-18", "Devtools without a finance angle", "Moves into payments developer tooling", "kabir"),
    ("Fitflow", "fitflow.in", "2026-02-02", "Consumer fitness, outside thesis", None, "rohan"),
    ("Gharbazaar", "gharbazaar.in", "2026-05-05", "Consumer proptech, outside thesis", None, "meera"),
    ("Swiftship", "swiftship.in", "2026-06-11", "Logistics, outside thesis", None, "rohan"),
]

# Founders and company people: key -> list of (name, email, title)
FOUNDERS = {
    "orbit": [("Vikram Rao", "vikram@orbittreasury.in", "CEO"), ("Lata Krishnan", "lata@orbittreasury.in", "CFO")],
    "kestrel": [("Neel Bhatt", "neel@kestrelpay.in", "CEO")],
    "ferro": [("Anjali Sen", "anjali@ferrocredit.com", "CEO")],
    "tallyfin": [("Rahul Sharma", "rahul@tallyfin.com", "CEO")],
    "saffire": [("Imran Qureshi", "imran@saffirekyc.com", "CEO")],
    "nimbus": [("Divya Raman", "divya@nimbuscollect.in", "CEO")],
    "quanta": [("Harsh Vora", "harsh@quantarails.com", "CEO")],
    "brightvault": [("Nisha Grover", "nisha@brightvault.io", "CEO")],
    "ledgerline": [("Mohan Kulkarni", "mohan@ledgerline.io", "CEO")],
    "cardinal": [("Zara Ahmed", "zara@cardinalrisk.ai", "CEO")],
    "harbor": [("Karthik Subramanian", "karthik@harborstack.in", "CEO")],
    "mintrail": [("Pooja Malhotra", "pooja@mintrail.in", "CEO")],
    "paysa": [("Rhea Khosla", "rhea@paysa.in", "CEO")],
    "coinvault": [("Aakash Jain", "aakash@coinvault.io", "CEO")],
    "glowkart": [("Simran Gill", "simran@glowkart.in", "CEO")],
    "ruplink": [("Priya Nair", "priya@ruplink.in", "CEO")],
    "sutra": [("Manish Agarwal", "manish@sutracompliance.com", "CEO")],
    "vaultline": [("Tanvi Shah", "tanvi@vaultline.in", "CEO")],
    "nexa": [("Gaurav Mehta", "gaurav@nexalend.com", "CEO")],
    "clearpath": [("Ritu Chawla", "ritu@clearpathrecon.com", "CEO")],
    "ankur": [("Suresh Meena", "suresh@ankurstack.in", "CEO")],
    "fintegrate": [("Jordan Lee", "jordan@fintegrate.dev", "CEO"), ("Ravi Iyengar", "ravi@fintegrate.dev", "CTO")],
    "bharatrisk": [("Farah Kazi", "farah@bharatrisk.in", "CEO")],
    "zeno": [("Farhan Ali", "farhan@zenotreasury.com", "CEO")],
    "pillar": [("Kavya Reddy", "kavya@pillarkyc.in", "CEO")],
    "rivulet": [("Omkar Patil", "omkar@rivuletpay.com", "CEO")],
    "deccan": [("Lakshmi Prasad", "lakshmi@deccanlend.cloud", "CEO")],
    "aster": [("Yash Arora", "yash@asteruw.ai", "CEO")],
    "copperleaf": [("Debashish Roy", "debashish@copperleaf.in", "CEO")],
    "halo": [("Shreya Venkat", "shreya@haloreconcile.com", "CEO")],
    "trellis": [("Neha Kulkarni", "neha@trellisapi.in", "CEO")],
    "ember": [("Leena Dsouza", "leena@embercredit.in", "CEO")],
    "northwind": [("Aman Gupta", "aman@northwindstack.com", "CEO")],
    "sable": [("Abhishek Joshi", "abhishek.joshi@sablefraud.ai", "CEO")],
    "juniper": [("Tushar Bansal", "tushar@juniperrails.in", "CEO")],
    "mosaic": [("Ira Saxena", "ira@mosaicwealth.io", "CEO")],
    "lumen": [("Maya Chen", "maya@lumenledger.com", "CEO"), ("Dev Pillai", "dev@lumenledger.com", "CTO")],
    "kite": [("Siddharth Menon", "siddharth@kitepay.in", "CEO"), ("Arun Pillai", "arun@kitepay.in", "CTO")],
    "vertex": [("Rohit Saluja", "rohit@vertexcards.in", "CEO")],
    "banyanrisk": [("Meghna Rao", "meghna@banyanrisk.com", "CEO")],
    "cobalt": [("Anita Dalal", "anita@cobaltaa.in", "CEO")],
    "prism": [("Sanjay Iyer", "sanjay@prismlend.com", "CEO")],
    "ironwood": [("Katherine Fernandes", "katherine@ironwoodcomply.com", "CEO")],
    "solace": [("Varun Khanna", "varun@solacetreasury.in", "CEO")],
    "gravity": [("Arjun Khurana", "arjun@gravitypayouts.com", "CEO")],
    "atlas": [("Ishaan Verma", "ishaan@atlassettle.com", "CEO")],
    "beacon": [("Rahul Basu", "rahul@beaconrails.in", "CEO")],
    "orchid": [("Natasha Pinto", "natasha@orchidcards.in", "CEO")],
    "sterling": [("Akhil Menon", "akhil@sterlingaa.com", "CEO")],
    "fizzbuy": [("Rohan Mittal", "rohan@fizzbuy.in", "CEO")],
    "moonlend": [("Kunal Bajaj", "kunal@moonlend.in", "CEO")],
    "tokenswap": [("Leo Tan", "leo@tokenswap.xyz", "CEO")],
    "parcelpro": [("Sameer Kohli", "sameer@parcelpro.in", "CEO")],
    "dhanam": [("Geetha Raman", "geetha@dhanamneo.in", "CEO")],
    "quickcash": [("Varsha Lal", "varsha@quickcash.in", "CEO")],
}

# Other contacts: (key, name, email, title, company name, company domain, role)
OTHERS = [
    # Co-investors and funds (fictional)
    ("dev_m", "Dev Malhotra", "dev@saffronpeak.vc", "Partner", "Saffron Peak Capital", "saffronpeak.vc", "co_investor"),
    ("ana_r", "Ana Rodrigues", "ana@saffronpeak.vc", "Principal", "Saffron Peak Capital", "saffronpeak.vc", "co_investor"),
    ("hemant", "Hemant Joshi", "hemant@monsoonarc.vc", "Partner", "Monsoon Arc Ventures", "monsoonarc.vc", "co_investor"),
    ("claire", "Claire Dubois", "claire@bluepeak.partners", "Partner", "Bluepeak Partners", "bluepeak.partners", "co_investor"),
    ("sunil", "Sunil Batra", "sunil@tamarind.capital", "Managing Partner", "Tamarind Capital", "tamarind.capital", "co_investor"),
    ("ruchi", "Ruchi Anand", "ruchi@tamarind.capital", "VP", "Tamarind Capital", "tamarind.capital", "co_investor"),
    ("mike_o", "Michael Okafor", "michael@ridgeline.vc", "Partner", "Ridgeline VC", "ridgeline.vc", "co_investor"),
    ("joy", "Joy Mathew", "joy@harbourlight.fund", "Partner", "Harbourlight Fund", "harbourlight.fund", "co_investor"),
    ("prakash", "Prakash Iyer", "prakash@kalpa.vc", "Partner", "Kalpa Ventures", "kalpa.vc", "co_investor"),
    ("emma", "Emma Lindqvist", "emma@fjordfof.example", "Investment Director", "Fjord Fund of Funds", "fjordfof.example", "co_investor"),
    # Banks and corporates (intro targets)
    ("raj_m", "Raj Malhotra", "raj.malhotra@fablebank.in", "Head of Digital Partnerships", "Fable Bank", "fablebank.in", "operator"),
    ("rahul_s2", "Rahul Sharma", "rahul.sharma@fablebank.in", "VP Payments", "Fable Bank", "fablebank.in", "operator"),
    ("omar", "Omar Siddiqui", "omar@coastline.bank", "Chief Digital Officer", "Coastline Bank", "coastline.bank", "operator"),
    ("pinki", "Pinki Das", "pinki@pinnaclesfb.in", "Head of Lending", "Pinnacle Small Finance Bank", "pinnaclesfb.in", "operator"),
    ("vivek", "Vivek Chandra", "vivek@arborinsure.in", "CTO", "Arbor Insurance", "arborinsure.in", "operator"),
    ("deepa", "Deepa Rangan", "deepa@kavericoop.bank", "General Manager", "Kaveri Cooperative Bank", "kavericoop.bank", "operator"),
    ("tom", "Tom Becker", "tom@ledgerlane.fund", "Director", "Ledger & Lane Fund Services", "ledgerlane.fund", "operator"),
    ("sana", "Sana Mirza", "sana@ledgerlane.fund", "Fund Accountant", "Ledger & Lane Fund Services", "ledgerlane.fund", "operator"),
    ("arvind", "Arvind Kumar", "arvind@kumarlegal.in", "Partner", "Kumar & Associates", "kumarlegal.in", "advisor"),
    ("fatima", "Fatima Sheikh", "fatima@talentbridge.in", "Founder", "Talentbridge", "talentbridge.in", "operator"),
    ("george", "George Thomas", "george.thomas@gmail.com", "CFO candidate", None, None, "operator"),
    ("swati", "Swati Kulkarni", "swati.kulkarni@gmail.com", "CFO candidate", None, None, "operator"),
    ("nikita", "Nikita Bhosle", "nikita@upiforum.org", "Program Lead", "UPI Builders Forum", "upiforum.org", "operator"),
    ("helen_g", "Helen Gomes", "helen@greenpay.example", "COO", "Greenpay Africa", "greenpay.example", "operator"),
    ("aditya_b", "Aditya Bhat", "aditya@meshbank.in", "Head of Partnerships", "Mesh Bank", "meshbank.in", "operator"),
    ("ravi_t", "Ravi Thakur", "ravi@zylo.example", "CEO", "Zylo Systems", "zylo.example", "operator"),
    # LP contacts (fictional LPs)
    ("helen", "Helen Park", "helen.park@northgate.edu.example", "Director, Private Investments", "Northgate Endowment", "northgate.edu.example", "lp"),
    ("kunal", "Kunal Shetty", "kunal@banyanfo.in", "Principal", "Banyan Family Office", "banyanfo.in", "lp"),
    ("marcus", "Marcus Hale", "marcus@coralstone.example", "Head of PE", "Coralstone Pension", "coralstone.example", "lp"),
    ("ingrid", "Ingrid Sorensen", "ingrid@tidewater.example", "Program Officer", "Tidewater Foundation", "tidewater.example", "lp"),
    ("anand", "Anand Saraswat", "anand@saraswatifo.in", "CIO", "Saraswati Family Office", "saraswatifo.in", "lp"),
    ("lin", "Lin Wei", "lin@lotusridge.example", "Partner", "Lotus Ridge FoF", "lotusridge.example", "lp"),
    ("olivia", "Olivia Grant", "olivia@evergrove.example", "Director", "Evergrove Capital Partners", "evergrove.example", "lp"),
    ("rakesh", "Rakesh Bhandari", "rakesh@himalayaholdings.in", "Managing Director", "Himalaya Holdings", "himalayaholdings.in", "lp"),
    ("peter", "Peter Quinn", "peter@peregrinetrust.example", "Trustee", "Peregrine Trust", "peregrinetrust.example", "lp"),
    ("sofia", "Sofia Martins", "sofia@silverline.example", "Head of Alternatives", "Silverline Insurance", "silverline.example", "lp"),
    ("grant", "Grant Hollis", "grant@granitepeak.example", "Director", "Granite Peak Endowment", "granitepeak.example", "lp"),
    ("ashok", "Ashok Menon", "ashok@ashokaangels.in", "Lead", "Ashoka Angels Collective", "ashokaangels.in", "lp"),
    ("meenal", "Meenal Kapadia", "meenal@marigoldfo.in", "Principal", "Marigold Family Office", "marigoldfo.in", "lp"),
    ("david", "David Brennan", "david@riverbend.example", "PE Lead", "Riverbend Pension", "riverbend.example", "lp"),
    ("chitra", "Chitra Raghavan", "chitra@cedarpine.in", "Partner", "Cedar & Pine Family Office", "cedarpine.in", "lp"),
]

LPS = [
    # id, name, contact key, commitment, reup start, reup end, last touch days ago
    ("lp_northgate", "Northgate Endowment", "helen", 8_000_000, "2027-01-10", "2027-03-31", 50),
    ("lp_banyan", "Banyan Family Office", "kunal", 5_000_000, "2027-01-05", "2027-03-15", 80),
    ("lp_coralstone", "Coralstone Pension", "marcus", 10_000_000, "2027-01-15", "2027-04-15", 20),
    ("lp_tidewater", "Tidewater Foundation", "ingrid", 4_000_000, "2027-04-01", "2027-06-30", 120),
    ("lp_saraswati", "Saraswati Family Office", "anand", 3_000_000, "2027-01-05", "2027-03-31", 12),
    ("lp_lotus", "Lotus Ridge FoF", "lin", 7_000_000, "2027-02-01", "2027-04-30", 25),
    ("lp_evergrove", "Evergrove Capital Partners", "olivia", 6_000_000, "2027-03-01", "2027-05-31", 30),
    ("lp_himalaya", "Himalaya Holdings", "rakesh", 4_000_000, "2027-01-20", "2027-03-31", 9),
    ("lp_peregrine", "Peregrine Trust", "peter", 3_000_000, "2027-04-15", "2027-06-30", 95),
    ("lp_silverline", "Silverline Insurance", "sofia", 6_000_000, "2027-02-15", "2027-05-15", 33),
    ("lp_granite", "Granite Peak Endowment", "grant", 5_000_000, "2027-03-15", "2027-06-15", 40),
    ("lp_ashoka", "Ashoka Angels Collective", "ashok", 2_000_000, "2027-01-10", "2027-02-28", 15),
    ("lp_marigold", "Marigold Family Office", "meenal", 3_000_000, "2027-02-01", "2027-03-31", 28),
    ("lp_riverbend", "Riverbend Pension", "david", 9_000_000, "2027-03-01", "2027-06-30", 35),
    ("lp_cedar", "Cedar & Pine Family Office", "chitra", 5_000_000, "2027-01-25", "2027-04-30", 18),
]
# Who owns each LP relationship: Aditi keeps the two largest pensions, Vikram (IR) the rest. Fund II has called 45%
# of commitments so far, pro rata; Peregrine Trust has paid in 40%: the latest 5% call is still outstanding.
LP_OWNER = {"lp_coralstone": "aditi", "lp_riverbend": "aditi"}
LP_CALLED_PCT = 0.45
LP_PAID_IN_PCT = {"lp_peregrine": 0.40}
LP_LAST_CALL = "2026-10-05"

# Duplicates: the same person appears under a second address or name. All of these must merge.
DUPLICATES = [
    # (canonical email, duplicate name, duplicate email, how it appears, rule)
    ("priya@ruplink.in", "Priya Nair", "priya.nair@gmail.com", "same_event", "personal and work in one meeting"),
    ("maya@lumenledger.com", "Maya Chen", "maya.chen@lumenledger.com", "thread", "same name, same domain"),
    ("farhan@zenotreasury.com", "Farhan Ali", "farhan.ali@zenotreasury.com", "thread", "same name, same domain"),
    ("neha@trellisapi.in", "Neha Kulkarni", "neha.k@trellisapi.in", "thread", "same name, same domain"),
    ("ishaan@atlassettle.com", "Ishaan Verma", "ishaan.v@atlassettle.com", "thread", "same name, same domain"),
    ("siddharth@kitepay.in", "Sid Menon", "sid@kitepay.in", "thread", "nickname, same domain"),
    ("abhishek.joshi@sablefraud.ai", "Abhi Joshi", "abhi@sablefraud.ai", "thread", "nickname, same domain"),
    ("vikram@orbittreasury.in", "Vik Rao", "vik@orbittreasury.in", "thread", "nickname, same domain"),
    ("katherine@ironwoodcomply.com", "Kat Fernandes", "kat@ironwoodcomply.com", "thread", "nickname, same domain"),
    ("arjun@gravitypayouts.com", "Arjun Khurana", "arjun.khurana@gmail.com", "same_event", "personal and work in one meeting"),
    ("leena@embercredit.in", "Leena Dsouza", "leena.dsouza@gmail.com", "same_thread", "personal and work in one thread"),
    ("rahul@beaconrails.in", "Rahul Basu", "rahul.basu@yahoo.com", "same_event", "personal and work in one meeting"),
    ("nisha@brightvault.io", "Nisha Grover", "nisha.grover@gmail.com", "gmail_variant", "gmail dots"),
    ("tanvi@vaultline.in", "Tanvi Shah", "tanvi.shah+vc@gmail.com", "gmail_pair", "gmail plus tag"),
    ("rhea@paysa.in", "Rhea Khosla", "rhea.khosla@gmail.com", "gmail_pair", "gmail dots"),
]
# For gmail_variant/gmail_pair the person has two spellings of one personal address in addition to work.
GMAIL_SECOND = {
    "nisha.grover@gmail.com": "nishagrover@gmail.com",
    "tanvi.shah+vc@gmail.com": "tanvishah@gmail.com",
    "rhea.khosla@gmail.com": "rhea.khosla+deals@gmail.com",
}

# Must never merge.
HARD_NEGATIVES = [
    ("rahul@tallyfin.com", "rahul.sharma@fablebank.in", "same name, two companies"),
    ("priya@ruplink.in", "priya.nair@northgate-alumni.example", "same name, two companies"),
    ("anita@cobaltaa.in", "anita.dalal@gmail.com", "same name, personal address never seen together"),
]
EXTRA_PEOPLE = [
    ("Priya Nair", "priya.nair@northgate-alumni.example", "Alumni Relations", "Northgate Alumni Office", "northgate-alumni.example"),
    ("Anita Dalal", "anita.dalal@gmail.com", "Angel investor", None, None),
]
# Initial plus last name at the same domain: the right answer is a needs_review row, not a merge.
REVIEW_CASES = [("sanjay@prismlend.com", "S. Iyer", "s.iyer@prismlend.com")]
