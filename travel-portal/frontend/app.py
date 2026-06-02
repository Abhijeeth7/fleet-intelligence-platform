# frontend/app.py
import os
import streamlit as st
import requests

# App Environment Setups
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Travel Analytics Portal", layout="wide")

# Modern Styling & Custom UI Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 20px !important;
        color: #ffffff !important; /* Kept text white */
    }
    
    /* Sleek light blue gradient background */
    .stApp {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 50%, #7DD3FC 100%) !important;
    }
    
    /* Headers with gradient texts */
    h1 {
        background: linear-gradient(90deg, #1E40AF 0%, #0369A1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        margin-bottom: 25px !important;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #1E3A8A !important; /* Darker blue for visibility on light bg */
        font-weight: 600 !important;
        font-size: 1.4rem !important;
        letter-spacing: -0.2px;
        margin-top: 20px !important;
    }
    
    /* Sidebar styling - soft translucent light blue */
    [data-testid="stSidebar"] {
        background-color: rgba(240, 249, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(30, 64, 175, 0.1);
    }
    
    /* Light Glassmorphic cards for forms */
    div[data-testid="stForm"], div.stCard, .stAlert {
        background: rgba(255, 255, 255, 0.4) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(3, 105, 161, 0.15) !important;
        box-shadow: 0 10px 30px 0 rgba(30, 41, 59, 0.08) !important;
        padding: 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stForm"]:hover {
        border-color: rgba(3, 105, 161, 0.3) !important;
        box-shadow: 0 12px 40px 0 rgba(3, 105, 161, 0.15) !important;
        transform: translateY(-2px);
    }
    
    /* Input field stylings - crisp light backgrounds */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #ffffff !important;
        border: 1px solid rgba(30, 41, 59, 0.15) !important;
        border-radius: 8px !important;
        color: #1E293B !important; /* Kept input text dark so users can read what they type */
        font-size: 14px !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease-in-out;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: #0284C7 !important;
        box-shadow: 0 0 0 1px #0284C7 !important;
    }
    
    /* Premium style for custom checkbox labels */
    .stCheckbox>label>span {
        color: #1E293B !important; /* Darkened for accessibility on light bg */
        font-size: 14.5px !important;
        font-weight: 500 !important;
    }
    
    /* Primary buttons with animated hover gradients */
    button[kind="primary"], .stButton > button {
        background: linear-gradient(95deg, #0284C7 0%, #0369A1 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 15px 0 rgba(2, 132, 199, 0.2) !important;
        letter-spacing: 0.3px;
    }
    button[kind="primary"]:hover, .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 22px 0 rgba(2, 132, 199, 0.3) !important;
    }
    
    /* Animations keyframes */
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .stApp section {
        animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
</style>
""", unsafe_allow_html=True)


# Helper function to fetch companies for mapping dropdown selectors
def fetch_companies():
    try:
        response = requests.get(f"{BACKEND_URL}/company")
        if response.status_code == 200:
            return response.json()
    except Exception:
        return []
    return []

# Sidebar Navigation Control Center
st.sidebar.title("🗺️ Navigation")
page = st.sidebar.radio(
    "Go To Portal Page:",
    [
        "Company Registration",
        "Fleet Registration",
        "Driver Registration",
        "Route Registration",
        "Revenue Entry",
        "Market Share Entry"
    ]
)

# ----------------- PAGE 1: COMPANY REGISTRATION -----------------
if page == "Company Registration":
    st.header("🏢 Company Registration Profile")
    
    with st.form("company_form", clear_on_submit=True):
        name = st.text_input("Legal Fleet Company Name")
        tax_id = st.text_input("Government Tax Identification Number (EIN/VAT)")
        submitted = st.form_submit_button("Register Company Profile")
        
        if submitted:
            if name and tax_id:
                res = requests.post(f"{BACKEND_URL}/company", json={"name": name, "tax_id": tax_id})
                if res.status_code == 201:
                    st.success(f"Successfully registered operator: {name}")
                else:
                    st.error(f"Error handling entry: {res.json().get('detail')}")
            else:
                st.warning("All verification field forms required.")

    # Render Current Registered Operators Table
    st.subheader("Registered Active Operators")
    companies = fetch_companies()
    if companies:
        st.dataframe(companies, use_container_width=True)
        
        # Document Compliance Checklist Section
        st.write("---")
        st.subheader("📑 Indian Regulatory Documents Compliance Checklist")
        st.info("Mandatory documents required under Motor Vehicles Act for commercial bus operations in India.")
        
        company_options_doc = {c["name"]: c["id"] for c in companies}
        selected_doc_company = st.selectbox("Select Operator to Manage Documents Checklist:", list(company_options_doc.keys()))
        company_id = company_options_doc[selected_doc_company]
        
        # Fetch current documents checklist state
        current_docs = {"has_rc": False, "has_fitness": False, "has_permit": False, "has_insurance": False, "has_puc": False, "has_road_tax": False}
        try:
            doc_res = requests.get(f"{BACKEND_URL}/document/{company_id}")
            if doc_res.status_code == 200:
                current_docs = doc_res.json()
        except Exception:
            pass
            
        with st.form("documents_checklist_form"):
            col1, col2 = st.columns(2)
            with col1:
                has_rc = st.checkbox("📄 Registration Certificate (RC)", value=current_docs.get("has_rc", False), help="Mandatory Vehicle Registration Proof (Form 23)")
                has_fitness = st.checkbox("🛠️ Fitness Certificate (Form 38)", value=current_docs.get("has_fitness", False), help="Mandatory roadworthiness certificate for commercial transport")
                has_permit = st.checkbox("🗺️ Road/Stage Carriage Permit", value=current_docs.get("has_permit", False), help="All India Tourist Permit (AITP) or Local Stage Carriage Permit")
            with col2:
                has_insurance = st.checkbox("🛡️ Third Party / Commercial Insurance", value=current_docs.get("has_insurance", False), help="Mandatory third-party commercial vehicle liability insurance")
                has_puc = st.checkbox("💨 Pollution Under Control Certificate (PUC)", value=current_docs.get("has_puc", False), help="Mandatory emission standards compliance certificate")
                has_road_tax = st.checkbox("🪙 Road Tax Payment Receipt", value=current_docs.get("has_road_tax", False), help="Receipt for paid commercial vehicle path/road taxes")
                
            doc_submitted = st.form_submit_button("Update Compliance Documents Profile")
            if doc_submitted:
                payload = {
                    "company_id": company_id,
                    "has_rc": has_rc,
                    "has_fitness": has_fitness,
                    "has_permit": has_permit,
                    "has_insurance": has_insurance,
                    "has_puc": has_puc,
                    "has_road_tax": has_road_tax
                }
                res = requests.post(f"{BACKEND_URL}/document", json=payload)
                if res.status_code == 201:
                    st.success("Compliance documents profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update documents checklist profile.")
        
        # Display nice compliance badge status
        all_docs = [has_rc, has_fitness, has_permit, has_insurance, has_puc, has_road_tax]
        compliant_count = sum(1 for d in all_docs if d)
        total_docs = len(all_docs)
        
        if compliant_count == total_docs:
            st.success("✅ **FULLY COMPLIANT** — All mandatory Indian commercial transport document validations verified.")
        elif compliant_count > 0:
            st.warning(f"⚠️ **PARTIALLY COMPLIANT** — {compliant_count}/{total_docs} documents verified. Ensure outstanding documents are updated.")
        else:
            st.error("❌ **NON-COMPLIANT** — No mandatory transport documents registered yet for this operator.")
    else:
        st.info("No corporate fleet registration entries loaded.")

# ----------------- PAGE 2: FLEET REGISTRATION -----------------
elif page == "Fleet Registration":
    st.header("🚎 Vehicle Fleet Registration Asset Matrix")
    companies = fetch_companies()
    
    if not companies:
        st.error("⚠️ Register a parent corporate profile first before tracking asset distributions.")
    else:
        company_options = {c["name"]: c["id"] for c in companies}
        
        with st.form("vehicle_form", clear_on_submit=True):
            selected_company = st.selectbox("Assign Vehicle to Fleet Operator:", list(company_options.keys()))
            plate_number = st.text_input("License Registration Plate ID Number")
            model = st.text_input("Asset Classification Profile Name (e.g. Volvo B11R, Mercedes Sprinter)")
            submitted = st.form_submit_button("Provision Asset to Field Operations")
            
            if submitted:
                if plate_number and model:
                    payload = {
                        "company_id": company_options[selected_company],
                        "plate_number": plate_number,
                        "model": model
                    }
                    res = requests.post(f"{BACKEND_URL}/vehicle", json=payload)
                    if res.status_code == 201:
                        st.success(f"Asset registration clear for vehicle {plate_number}")
                    else:
                        st.error(f"Failed transaction handling: {res.json().get('detail')}")
                else:
                    st.warning("Input all descriptive operational tracking variables.")
        
        st.subheader("Active Tracked Service Fleet Assets")
        vehicles = []
        try:
            v_res = requests.get(f"{BACKEND_URL}/vehicle")
            if v_res.status_code == 200 and v_res.json():
                vehicles = v_res.json()
                st.dataframe(vehicles, use_container_width=True)
            else:
                st.info("No active vehicle allocations deployed.")
        except Exception:
            st.info("No active vehicle allocations deployed.")
            
        # Service Fleet Amenities Checklist Section
        if vehicles:
            st.write("---")
            st.subheader("❄️ Service Fleet Amenities Checklist")
            st.info("On-board comfort and safety amenities provided by the operator for passenger satisfaction.")
            
            # Map vehicles list to strings
            vehicle_options = {f"{v['plate_number']} ({v['model']})": v["id"] for v in vehicles}
            selected_vehicle_label = st.selectbox("Select Vehicle to Configure Amenities Checklist:", list(vehicle_options.keys()))
            vehicle_id = vehicle_options[selected_vehicle_label]
            
            # Fetch current amenities checklist state
            current_amenities = {
                "has_wifi": False, "has_ac": False, "has_charging_ports": False,
                "has_reclining_seats": False, "has_reading_light": False, "has_blanket": False,
                "has_first_aid": False, "has_gps": False, "has_cctv": False
            }
            try:
                amenity_res = requests.get(f"{BACKEND_URL}/amenity/{vehicle_id}")
                if amenity_res.status_code == 200:
                    current_amenities = amenity_res.json()
            except Exception:
                pass
                
            with st.form("amenities_checklist_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    has_wifi = st.checkbox("📶 High-Speed Wi-Fi", value=current_amenities.get("has_wifi", False))
                    has_ac = st.checkbox("❄️ Air Conditioning (AC)", value=current_amenities.get("has_ac", False))
                    has_charging_ports = st.checkbox("🔌 USB Charging Ports", value=current_amenities.get("has_charging_ports", False))
                with col2:
                    has_reclining_seats = st.checkbox("💺 Reclining Seats", value=current_amenities.get("has_reclining_seats", False))
                    has_reading_light = st.checkbox("💡 Individual Reading Light", value=current_amenities.get("has_reading_light", False))
                    has_blanket = st.checkbox("🛌 Cozy Blanket & Pillow", value=current_amenities.get("has_blanket", False))
                with col3:
                    has_first_aid = st.checkbox("🚑 First Aid Safety Kit", value=current_amenities.get("has_first_aid", False))
                    has_gps = st.checkbox("📍 Real-Time GPS Tracking", value=current_amenities.get("has_gps", False))
                    has_cctv = st.checkbox("📹 Security CCTV Camera", value=current_amenities.get("has_cctv", False))
                    
                amenity_submitted = st.form_submit_button("Update Fleet Amenities Profile")
                if amenity_submitted:
                    payload = {
                        "vehicle_id": vehicle_id,
                        "has_wifi": has_wifi,
                        "has_ac": has_ac,
                        "has_charging_ports": has_charging_ports,
                        "has_reclining_seats": has_reclining_seats,
                        "has_reading_light": has_reading_light,
                        "has_blanket": has_blanket,
                        "has_first_aid": has_first_aid,
                        "has_gps": has_gps,
                        "has_cctv": has_cctv
                    }
                    res = requests.post(f"{BACKEND_URL}/amenity", json=payload)
                    if res.status_code == 201:
                        st.success("Fleet amenities updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update fleet amenities checklist.")

# ----------------- PAGE 3: DRIVER REGISTRATION -----------------
elif page == "Driver Registration":
    st.header("🧑‍✈️ Personnel Logistics: Driver Registry")
    companies = fetch_companies()
    
    if not companies:
        st.error("⚠️ Missing Corporate entity infrastructure assignments.")
    else:
        company_options = {c["name"]: c["id"] for c in companies}
        
        with st.form("driver_form", clear_on_submit=True):
            selected_company = st.selectbox("Employer Affiliation Assignment:", list(company_options.keys()))
            full_name = st.text_input("Legal Professional Operator Name")
            license_number = st.text_input("Commercial Driver License ID Validation String (CDL)")
            submitted = st.form_submit_button("Certify Commercial Driver Profile")
            
            if submitted:
                if full_name and license_number:
                    payload = {
                        "company_id": company_options[selected_company],
                        "full_name": full_name,
                        "license_number": license_number
                    }
                    res = requests.post(f"{BACKEND_URL}/driver", json=payload)
                    if res.status_code == 201:
                        st.success(f"Staff operator file bound for employee: {full_name}")
                    else:
                        st.error(f"Verification rejected: {res.json().get('detail')}")
                else:
                    st.warning("Provide validation identifiers.")

# ----------------- PAGE 4: ROUTE REGISTRATION -----------------
elif page == "Route Registration":
    st.header("📍 Logistical Route Infrastructure Provisions")
    
    with st.form("route_form", clear_on_submit=True):
        route_name = st.text_input("Custom Route Name (Optional - auto-generates if blank)")
        origin = st.text_input("Origin Hub Hub-ID Terminal Reference")
        destination = st.text_input("Destination Terminal Terminal-ID Reference")
        duration = st.number_input("Estimated Duration (Hours)", min_value=0.0, max_value=72.0, value=1.0, step=0.1)
        submitted = st.form_submit_button("Save Route Node")
        
        if submitted:
            if origin and destination:
                payload = {
                    "route_name": route_name if route_name.strip() else None,
                    "origin": origin,
                    "destination": destination,
                    "estimated_duration_hours": duration
                }
                res = requests.post(f"{BACKEND_URL}/route", json=payload)
                if res.status_code == 201:
                    st.success(f"Route successfully logged!")
                else:
                    st.error(f"Error handling entry: {res.json().get('detail')}")
            else:
                st.warning("Origin and Destination references are required.")

    # Render Current Logged Routes
    st.subheader("Registered Active Routes")
    try:
        r_res = requests.get(f"{BACKEND_URL}/route")
        if r_res.status_code == 200 and r_res.json():
            import pandas as pd
            st.dataframe(pd.DataFrame(r_res.json()), use_container_width=True)
        else:
            st.info("No active route structures registered.")
    except Exception:
        st.info("Unable to fetch route registrations from backend.")

# ----------------- PAGE 5: REVENUE ENTRY -----------------
elif page == "Revenue Entry":
    st.header("💰 Accounting Operations Matrix Ledger")
    companies = fetch_companies()
    
    if not companies:
        st.error("⚠️ Register a parent corporate profile first before tracking financial ledgers.")
    else:
        company_options = {c["name"]: c["id"] for c in companies}
        
        with st.form("revenue_form", clear_on_submit=True):
            selected_company = st.selectbox("Assign Revenue to Operator:", list(company_options.keys()))
            amount = st.number_input("Gross Balance Revenue Valuation Reporting (USD)", min_value=0.0, value=1000.0, step=100.0)
            statement_date = st.date_input("Reporting Audit Statement Close Interval Settlement Date")
            submitted = st.form_submit_button("Submit Certified Audit Ledger Block")
            
            if submitted:
                payload = {
                    "company_id": company_options[selected_company],
                    "amount": amount,
                    "statement_date": statement_date.isoformat()
                }
                res = requests.post(f"{BACKEND_URL}/revenue", json=payload)
                if res.status_code == 201:
                    st.success(f"Audit block saved for {selected_company}.")
                else:
                    st.error(f"Transaction rejected: {res.json().get('detail')}")
        
        st.subheader("Certified Fiscal Ledger Allocations")
        try:
            rev_res = requests.get(f"{BACKEND_URL}/revenue")
            if rev_res.status_code == 200 and rev_res.json():
                import pandas as pd
                # Map company_id to name for better reading
                company_map = {c["id"]: c["name"] for c in companies}
                data = rev_res.json()
                for entry in data:
                    entry["company_name"] = company_map.get(entry["company_id"], "Unknown")
                df = pd.DataFrame(data)[["company_name", "amount", "statement_date"]]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No certified ledger entries recorded.")
        except Exception:
            st.info("Unable to fetch ledger allocations from backend.")

# ----------------- PAGE 6: MARKET SHARE ENTRY -----------------
elif page == "Market Share Entry":
    st.header("📊 Industry Performance Index Metrics")
    companies = fetch_companies()
    
    if not companies:
        st.error("⚠️ Register a corporate profile first to analyze market share allocations.")
    else:
        # Initialize session state for mock market shares if not present
        if "market_shares" not in st.session_state:
            st.session_state.market_shares = {c["name"]: 100.0 / len(companies) for c in companies}
        
        # Synchronize session state keys with current companies list
        for c in companies:
            if c["name"] not in st.session_state.market_shares:
                st.session_state.market_shares[c["name"]] = 0.0
        # Remove deleted companies
        st.session_state.market_shares = {k: v for k, v in st.session_state.market_shares.items() if any(c["name"] == k for c in companies)}
        
        with st.form("market_share_form"):
            st.subheader("Adjust Targeted Capacity allocations (%):")
            new_shares = {}
            for name in st.session_state.market_shares.keys():
                new_shares[name] = st.slider(f"Capacity Share for {name} (%)", 0.0, 100.0, float(st.session_state.market_shares[name]))
            submitted = st.form_submit_button("Commit Analytical Assessment Data Node")
            
            if submitted:
                total = sum(new_shares.values())
                if total > 100.1: # slight tolerance for float representation
                    st.error(f"Total capacity share allocation exceeds 100% (currently {total:.1f}%). Please adjust values.")
                else:
                    st.session_state.market_shares = new_shares
                    st.success("Analytical Assessment Data Node committed successfully!")
        
        # Render a clean bar chart
        import pandas as pd
        shares_df = pd.DataFrame([
            {"Company": name, "Capacity Share (%)": share}
            for name, share in st.session_state.market_shares.items()
        ])
        
        if not shares_df.empty and shares_df["Capacity Share (%)"].sum() > 0:
            st.subheader("Regional Operational Control Capacity Allocations")
            st.bar_chart(shares_df.set_index("Company"))
        else:
            st.info("No active capacity allocations committed yet.")

