import streamlit as st
import pandas as pd
import re
import urllib.parse
import os
from datetime import datetime
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PrimeState Adjusters | NJ Claims Processing",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# 🔒 SECURITY: PASSWORD PROTECTION
# ═══════════════════════════════════════════════════════════════════════════════
# Change this password to whatever you want your dad to type:
ACCESS_CODE = "primestate2026" 

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == ACCESS_CODE:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Enter PrimeState Access Code:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input again.
        st.text_input(
            "Enter PrimeState Access Code:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("🔒 Access Denied")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()  # STOPS the app here if password is wrong.

# ═══════════════════════════════════════════════════════════════════════════════
# 2. COMPANY CONSTANTS  (single source of truth for branding)
# ═══════════════════════════════════════════════════════════════════════════════
CO = {
    "name": "PrimeState Public Adjusters, Inc.",
    "short": "PrimeState Adjusters",
    "president": "Carlos A. Jimenez",
    "title": "President",
    "nj_address": "9060 Palisade Ave Unit C-003, North Bergen, NJ 07047",
    "nj_phone": "(201) 305-1006",
    "toll_free": "1-800-211-0434",
    "email": "info@primestateadjusters.com",
    "web": "primestateadjusters.com",
    "logo_url": "https://e1w.61f.myftpupload.com/wp-content/uploads/2024/03/prime-state-logo-quality-png-.png",
    "tagline": "No Recovery, No Fee.",
    "license_nj": "Licensed by the State of New Jersey Dept. of Banking & Insurance",
}

# ═══════════════════════════════════════════════════════════════════════════════
# 3. BRAND STYLING
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
/* ---- Palette ---- */
:root {{
    --ps-navy:    #0c1a2e;
    --ps-slate:   #1e293b;
    --ps-gold:    #c9a84c;
    --ps-gold-lt: #e8d48b;
    --ps-blue:    #2563eb;
    --ps-bg:      #f1f5f9;
    --ps-card:    #ffffff;
    --ps-border:  #e2e8f0;
    --ps-text:    #1e293b;
    --ps-muted:   #64748b;
}}

/* ---- Global ---- */
.stApp {{ background-color: var(--ps-bg); font-family: 'Segoe UI', sans-serif; }}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--ps-navy) 0%, var(--ps-slate) 100%);
}}
section[data-testid="stSidebar"] * {{ color: #cbd5e1 !important; }}
section[data-testid="stSidebar"] hr {{ border-color: #334155 !important; opacity: 0.5; }}
section[data-testid="stSidebar"] .stMetric label {{
    font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 0.08em;
}}
section[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
    font-size: 1.5rem !important; font-weight: 700 !important; color: var(--ps-gold) !important;
}}

/* ---- Cards / Sections ---- */
.ps-card {{
    background: var(--ps-card);
    border: 1px solid var(--ps-border);
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.step-header {{
    font-size: 0.68rem;
    color: var(--ps-muted);
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.06em;
    margin-bottom: 0.6rem;
    padding-bottom: 0.45rem;
    border-bottom: 2px solid var(--ps-border);
    display: flex; align-items: center; gap: 7px;
}}
.step-header .badge {{
    background: var(--ps-gold);
    color: var(--ps-navy);
    font-size: 0.58rem;
    width: 17px; height: 17px;
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 800;
}}

/* ---- Buttons ---- */
div.stButton > button {{
    border-radius: 6px; font-weight: 600; font-size: 0.82rem;
    transition: all 0.15s ease;
}}
div.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}

/* ---- Tax / Link Buttons ---- */
.tax-btn {{
    display: block; width: 100%; padding: 9px 0; text-align: center;
    background: var(--ps-blue); color: #fff !important;
    border-radius: 6px; font-weight: 600; font-size: 0.8rem;
    text-decoration: none; margin: 6px 0; transition: background 0.15s;
}}
.tax-btn:hover {{ background: #1d4ed8; }}
.link-pill {{
    display: inline-block; padding: 5px 12px;
    background: #f8fafc; border: 1px solid var(--ps-border);
    border-radius: 20px; color: var(--ps-blue) !important;
    font-size: 0.76rem; font-weight: 600;
    text-decoration: none; margin: 3px 2px;
    transition: all 0.15s;
}}
.link-pill:hover {{ background: #eff6ff; border-color: #93c5fd; }}

/* ---- Inputs ---- */
.stTextInput input, .stTextArea textarea {{
    background: #fff; border: 1px solid #cbd5e1;
    border-radius: 6px; color: var(--ps-text); font-size: 0.84rem;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--ps-gold); box-shadow: 0 0 0 2px rgba(201,168,76,0.18);
}}

/* ---- Misc ---- */
.status-dot {{
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; margin-right: 5px;
}}
.dot-pending {{ background: #f59e0b; }}
.dot-done    {{ background: #16a34a; }}
.dot-empty   {{ background: #cbd5e1; }}

/* ---- Scroll fixes ---- */
section.main {{
    overflow: auto !important;
}}
section.main > div.block-container {{
    padding-bottom: 5rem;
    min-height: 100vh;
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 4. DATABASE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
DB_FILE = "Primestate_Leads_Database.xlsx"
COLUMNS = [
    "Lead ID", "Date", "County", "Address", "Case Number",
    "Type", "Homeowner", "Phone", "Email", "Status", "Notes",
]


@st.cache_data(ttl=30)
def load_database():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    return pd.DataFrame(columns=COLUMNS)


def save_to_database(record):
    load_database.clear()
    df = load_database()
    if not df.empty and record["Lead ID"] in df["Lead ID"].values:
        idx = df[df["Lead ID"] == record["Lead ID"]].index[0]
        for k, v in record.items():
            df.at[idx, k] = v
    else:
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)
    load_database.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PDF — LETTER OF REPRESENTATION (branded)
# ═══════════════════════════════════════════════════════════════════════════════
class LOR_PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 8, CO["name"].upper(), 0, 1, "C")
        self.set_font("Arial", "", 9)
        self.cell(0, 5, "Public Insurance Adjusters", 0, 1, "C")
        self.cell(0, 4, CO["nj_address"], 0, 1, "C")
        self.cell(0, 4, f'Tel: {CO["nj_phone"]}  |  Toll-Free: {CO["toll_free"]}  |  {CO["email"]}', 0, 1, "C")
        self.cell(0, 4, CO["web"], 0, 1, "C")
        # gold accent line
        self.set_draw_color(201, 168, 76)
        self.set_line_width(0.6)
        self.line(15, self.get_y() + 3, 195, self.get_y() + 3)
        self.ln(8)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(201, 168, 76)
        self.set_line_width(0.3)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)
        self.set_font("Arial", "I", 7)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, CO["license_nj"], 0, 1, "C")
        self.cell(0, 4, f'{CO["tagline"]}  |  Page {self.page_no()}', 0, 0, "C")


def create_lor_pdf(owner_name, address, case_num, loss_date):
    pdf = LOR_PDF()
    pdf.add_page()
    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Arial", size=11)

    # Date
    pdf.cell(0, 8, f"Date: {datetime.today().strftime('%B %d, %Y')}", 0, 1)
    pdf.ln(4)

    # RE block
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "RE: Letter of Representation", 0, 1)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 5, f"Insured / Claimant: {owner_name}", 0, 1)
    pdf.cell(0, 5, f"Property Address: {address}", 0, 1)
    pdf.cell(0, 5, f"Date of Loss: {loss_date}", 0, 1)
    pdf.cell(0, 5, f"Claim / Case No.: {case_num}", 0, 1)
    pdf.ln(8)

    # Salutation
    pdf.multi_cell(0, 6, "To Whom It May Concern:")
    pdf.ln(4)

    # Body
    body = (
        f"Please be advised that {owner_name} has retained {CO['name']} "
        "to represent them in the adjustment of their insurance claim for "
        f"loss and damage sustained at the above-referenced property on {loss_date}.\n\n"
        "We respectfully request that all future correspondence, telephone calls, "
        "and communications regarding this claim be directed to our office at the "
        "address listed above. We ask that you refrain from contacting the insured "
        "directly regarding any matters pertaining to this claim.\n\n"
        "Please acknowledge receipt of this letter at your earliest convenience "
        "and provide the claim number assigned to this matter.\n\n"
        "We look forward to working toward a fair and prompt resolution. "
        "Thank you for your anticipated cooperation."
    )
    pdf.multi_cell(0, 6, body)
    pdf.ln(12)

    # Signature block
    pdf.cell(0, 6, "Respectfully,", 0, 1)
    pdf.ln(16)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 5, CO["name"], 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f'{CO["president"]}, {CO["title"]}', 0, 1)
    pdf.cell(0, 5, f'Tel: {CO["nj_phone"]}  |  {CO["email"]}', 0, 1)
    pdf.ln(18)

    # Client signature line
    pdf.set_draw_color(30, 41, 59)
    pdf.set_line_width(0.4)
    pdf.cell(85, 0, "", "T")
    pdf.ln(3)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Authorized Signature - {owner_name}", 0, 1)

    return pdf.output(dest="S").encode("latin-1")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. LOGIC HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
COUNTY_TAX_URLS = {
    "essex":    "https://www.taxdatahub.com/6229fbf0ce4aef911f9de7bc/Essex%20County",
    "camden":   "https://www.taxdatahub.com/60d088c3d3501df3b0e45ddb/camden-county",
    "mercer":   "https://pip.mercercounty.org/mapsearch",
    "ocean":    "https://tax.co.ocean.nj.us/frmTaxBoardTaxListSearch",
    "monmouth":"https://tax1.co.monmouth.nj.us/cgi-bin/prc6.cgi?menu=index&ms_user=monm&passwd=data&mode=11",
    "morris":   "https://mcweb1.co.morris.nj.us/MCTaxBoard/SearchTaxRecords.aspx",
}
DEFAULT_TAX = "https://taxrecords-nj.com/pub/cgi/prc6.cgi?menu=index&ms_user=ctb00"


def get_county_tax_url(county):
    c = str(county).strip().lower()
    return next((url for key, url in COUNTY_TAX_URLS.items() if key in c), DEFAULT_TAX)


def clean_name(raw):
    if "," in raw:
        parts = raw.split(",", 1)
        name = f"{parts[1].strip()} {parts[0].strip()}"
    else:
        name = raw.strip()
    # Tax records often return ALL CAPS — convert to proper title case
    return name.title()


def get_search_links(name, address, city, state, is_commercial):
    clean = clean_name(name)
    s_name, s_city, s_state = (urllib.parse.quote(x) for x in (clean, city, state))
    if is_commercial:
        return {
            "Google Business": f"https://www.google.com/search?q={s_name}+{urllib.parse.quote(address)}+phone",
            "NJ Entity Search": "https://www.njportal.com/DOR/BusinessNameSearch/Search/BusinessName",
        }
    h_name = clean.replace(" ", "-")
    return {
        "TruePeopleSearch": f"https://www.truepeoplesearch.com/results?name={s_name}&citystatezip={s_city},+{s_state}",
        "FastPeopleSearch": f"https://www.fastpeoplesearch.com/name/{s_name}_{s_city}-{s_state}",
        "ThatsThem": f"https://thatsthem.com/name/{h_name}/{s_state}",
    }


def parse_bulk_text(text):
    leads, current = [], {}
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "|" in line and "NJ" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                current = {
                    "state": parts[0], "county": parts[1], "city": parts[2],
                    "address_part": parts[3],
                    "full_address": f"{parts[3]}, {parts[2]}, {parts[0]}",
                    "type": parts[4] if len(parts) > 4 else "Unknown",
                    "desc": parts[5] if len(parts) > 5 else "",
                    "case": parts[-1].replace("#", "") if "#" in parts[-1] else "Pending",
                }
        elif re.match(r"\d{2}/\d{2}/\d{4}", line) and current:
            date_str = line.split(" ")[0]
            current["date"] = date_str
            lid = f"{date_str} — {current['full_address']} — {current['case']}"
            leads.append({"id": lid, "data": current})
            current = {}
    return leads


# ═══════════════════════════════════════════════════════════════════════════════
# 7. SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "queue" not in st.session_state:
    st.session_state.queue = {}
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ═══════════════════════════════════════════════════════════════════════════════
# 8. SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image(CO["logo_url"], width=200)
    st.caption(f"**NJ Claims Operations**")
    st.markdown("---")

    db = load_database()
    m1, m2 = st.columns(2)
    m1.metric("Saved", len(db))
    m2.metric("Queue", len(st.session_state.queue))

    st.markdown("---")
    st.caption("OFFICE")
    st.markdown(f"📍 {CO['nj_address']}")
    st.markdown(f"📞 {CO['nj_phone']}")
    st.markdown(f"🌐 {CO['web']}")
    st.markdown("---")

    # Database viewer
    with st.expander("📂 View Database"):
        if not db.empty:
            st.dataframe(db[["Homeowner", "Address", "Status", "Date"]].tail(15), hide_index=True, use_container_width=True)
        else:
            st.info("No records yet.")

    st.markdown("---")
    if st.button("🔄 Reset Queue", type="primary", use_container_width=True):
        st.session_state.queue = {}
        st.session_state.input_key += 1
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 9. MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("#### Claims Processing Dashboard")
st.caption("Import → Research → Generate → Save")

# ── STEP 1: IMPORT ──────────────────────────────────────────────────────────
with st.expander("📥  Step 1 — Import Leads", expanded=not st.session_state.queue):
    raw_text = st.text_area(
        "Paste pipe-delimited lead data:",
        height=70,
        key=f"raw_{st.session_state.input_key}",
        placeholder="NJ | Essex | Newark | 123 Main St | Fire | Desc | #12345\n01/15/2026 ...",
    )
    if st.button("⚡ Process Import", use_container_width=False):
        if raw_text:
            new = parse_bulk_text(raw_text)
            added = 0
            for l in new:
                if l["id"] not in st.session_state.queue:
                    st.session_state.queue[l["id"]] = l["data"]
                    added += 1
            if added:
                st.rerun()
            else:
                st.warning("No new leads found — check format.")

# ── STEP 2: WORKSPACE ───────────────────────────────────────────────────────
options = list(st.session_state.queue.keys())
if options:
    selected_id = st.selectbox("**Active Lead**", ["Select..."] + options)
else:
    st.info("⏳ Import leads above to begin processing.")
    selected_id = "Select..."

if selected_id != "Select...":
    lead = st.session_state.queue[selected_id]

    # Progress dots
    owner_name = ""  # will be set in col1
    phone = email = ""

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="medium")

    # ── COL 1: TAX LOOKUP ──
    with c1:
        st.markdown(
            '<div class="step-header"><span class="badge">1</span>Find Owner (Tax Record)</div>',
            unsafe_allow_html=True,
        )
        st.caption("Copy this address →")
        st.code(lead["address_part"])

        tax_url = get_county_tax_url(lead["county"])
        st.markdown(
            f'<a class="tax-btn" href="{tax_url}" target="_blank">'
            f'🔍 Open {lead["county"].title()} County Tax Site</a>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        owner_name = st.text_input("📝 Owner Name", placeholder="Doe, John")

    # ── COL 2: CONTACT SEARCH ──
    with c2:
        st.markdown(
            '<div class="step-header"><span class="badge">2</span>Find Contact Info</div>',
            unsafe_allow_html=True,
        )
        if owner_name:
            clean = clean_name(owner_name)
            if clean != owner_name:
                st.caption(f"✅ Formatted: **{clean}**")

            is_comm = st.checkbox("Commercial property?")
            links = get_search_links(owner_name, lead["address_part"], lead["city"], lead["state"], is_comm)

            pills_html = " ".join(
                f'<a class="link-pill" href="{url}" target="_blank">{label}</a>'
                for label, url in links.items()
            )
            st.markdown(pills_html, unsafe_allow_html=True)
            st.markdown("")

            phone = st.text_input("📞 Phone")
            email = st.text_input("📧 Email")
        else:
            st.info("← Enter owner name first")

    # ── COL 3: GENERATE & SAVE ──
    with c3:
        st.markdown(
            '<div class="step-header"><span class="badge">3</span>Generate & Save</div>',
            unsafe_allow_html=True,
        )
        if owner_name and (phone or email):
            clean_owner = clean_name(owner_name)

            # Pre-built templates
            sms = (
                f"Hello {clean_owner}, this is {CO['short']} reaching out regarding the "
                f"{lead['type']} loss at {lead['address_part']}. Please call us at "
                f"{CO['nj_phone']} — Case #{lead['case']}."
            )
            email_subj = (
                f"Letter of Representation — {lead['type']} at "
                f"{lead['address_part']} (Case #{lead['case']})"
            )
            email_body = (
                f"Dear {clean_owner},\n\n"
                f"Please find attached our Letter of Representation regarding "
                f"the loss at your property on {lead['date']}.\n\n"
                f"Should you have any questions, please do not hesitate to contact "
                f"our office at {CO['nj_phone']} or reply to this email.\n\n"
                f"Respectfully,\n"
                f"{CO['president']}\n"
                f"{CO['name']}\n"
                f"{CO['nj_phone']} | {CO['email']}"
            )

            pdf_bytes = create_lor_pdf(
                clean_owner, lead["full_address"], lead["case"], lead["date"]
            )

            tabs = st.tabs(["✉️ Email", "💬 SMS", "📄 LOR PDF"])
            with tabs[0]:
                st.text_input("Subject", email_subj, disabled=True)
                st.text_area("Body", email_body, height=140)
            with tabs[1]:
                st.text_area("Message", sms, height=80)
            with tabs[2]:
                st.download_button(
                    label="⬇ Download Letter of Representation",
                    data=pdf_bytes,
                    file_name=f"LOR_{lead['case']}_{clean_owner.replace(' ','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            st.markdown("")
            if st.button("💾 SAVE TO DATABASE", type="primary", use_container_width=True):
                record = {
                    "Lead ID": selected_id,
                    "Date": lead["date"],
                    "County": lead["county"],
                    "Address": lead["full_address"],
                    "Case Number": lead["case"],
                    "Type": lead["type"],
                    "Homeowner": clean_owner,
                    "Phone": phone,
                    "Email": email,
                    "Status": "Processed",
                    "Notes": lead["desc"],
                }
                save_to_database(record)
                del st.session_state.queue[selected_id]
                st.success(f"✅ {clean_owner} saved — lead removed from queue.")
                st.rerun()
        else:
            st.info("Complete Steps 1 & 2 to unlock outputs.")