# app.py
# To run this app:
# 1. Save the code as 'app.py'.
# 2. Make sure you have pandas and streamlit installed:
#    pip install pandas streamlit
# 3. Open your terminal, navigate to the directory where you saved the file, and run:
#    streamlit run app.py

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import numpy as np
import os

# --- App Configuration ---
st.set_page_config(
    page_title="Local Food Wastage Management",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Database Setup ---
DB_NAME = "food_wastage.db"

@st.cache_resource
def init_database():
    """
    Initializes the SQLite database. Creates tables and populates them with
    mock data if the database file doesn't exist. This function is cached
    so it only runs once per session.
    """
    # --- Data Generation ---
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        
        # --- Providers Data ---
        providers_data = {
            'Provider_ID': range(1, 11),
            'Name': ['Green Leaf Restaurant', 'FreshMart Grocers', 'The Daily Bread Bakery', 'City Supermarket', 'The Grand Hotel', 'Quick Bites Cafe', 'HealthyHarvest Organics', 'SeaBreeze Fine Dining', 'Budget Grocers', 'Sunrise Bakery'],
            'Type': ['Restaurant', 'Grocery Store', 'Bakery', 'Supermarket', 'Restaurant', 'Cafe', 'Grocery Store', 'Restaurant', 'Supermarket', 'Bakery'],
            'Address': ['123 MG Road', '45 Commercial Street', '78 Church Street', '90 Brigade Road', '11 Palace Road', '22 Koramangala High St', '33 Indiranagar 100ft Rd', '44 Juhu Tara Road', '55 Linking Road', '66 Hill Road'],
            'City': ['Bangalore', 'Bangalore', 'Bangalore', 'Bangalore', 'Bangalore', 'Bangalore', 'Bangalore', 'Mumbai', 'Mumbai', 'Mumbai'],
            'Contact': ['9876543210', '9876543211', '9876543212', '9876543213', '9876543214', '9876543215', '9876543216', '9876543217', '9876543218', '9876543219']
        }
        providers_df = pd.DataFrame(providers_data)
        providers_df.to_sql('providers', conn, if_exists='replace', index=False)

        # --- Receivers Data ---
        receivers_data = {
            'Receiver_ID': range(101, 109),
            'Name': ['Hope Foundation', 'Community Food Bank', 'Shelter Home for All', 'Child Care Trust', 'Elderly Support Group', 'Daily Meals Initiative', 'Street Dwellers Aid', 'Urban Poor Collective'],
            'Type': ['NGO', 'Community Center', 'NGO', 'NGO', 'Community Center', 'Individual', 'NGO', 'Community Center'],
            'City': ['Bangalore', 'Bangalore', 'Mumbai', 'Mumbai', 'Bangalore', 'Mumbai', 'Bangalore', 'Mumbai'],
            'Contact': ['8765432109', '8765432108', '8765432107', '8765432106', '8765432105', '8765432104', '8765432103', '8765432102']
        }
        receivers_df = pd.DataFrame(receivers_data)
        receivers_df.to_sql('receivers', conn, if_exists='replace', index=False)

        # --- Food Listings Data ---
        food_listings_data = {
            'Food_ID': range(1001, 1021),
            'Food_Name': ['Vegetable Biryani', 'Fresh Apples', 'Sourdough Bread', 'Milk Cartons', 'Chicken Curry', 'Coffee & Sandwiches', 'Organic Spinach', 'Grilled Fish', 'Lentils', 'Assorted Pastries', 'Paneer Butter Masala', 'Brown Rice', 'Whole Wheat Bread', 'Yogurt Cups', 'Idli Sambar', 'Iced Tea', 'Quinoa', 'Prawn Masala', 'Basmati Rice', 'Muffins'],
            'Quantity': np.random.randint(5, 50, size=20),
            'Expiry_Date': [(datetime.now() + timedelta(days=int(x))).strftime('%Y-%m-%d') for x in np.random.randint(1, 10, size=20)],
            'Provider_ID': np.random.randint(1, 11, size=20),
            'Location': ['Bangalore', 'Bangalore', 'Bangalore', 'Bangalore', 'Bangalore', 'Bangalore', 'Bangalore', 'Mumbai', 'Mumbai', 'Mumbai'] * 2,
            'Food_Type': ['Vegetarian', 'Vegetarian', 'Vegetarian', 'Vegetarian', 'Non-Vegetarian', 'Vegetarian', 'Vegetarian', 'Non-Vegetarian', 'Vegetarian', 'Vegetarian'] * 2,
            'Meal_Type': ['Lunch', 'Snacks', 'Breakfast', 'Breakfast', 'Dinner', 'Breakfast', 'Lunch', 'Dinner', 'Lunch', 'Snacks'] * 2
        }
        food_listings_df = pd.DataFrame(food_listings_data)
        food_listings_df = pd.merge(food_listings_df, providers_df[['Provider_ID', 'Type']], on='Provider_ID')
        food_listings_df.rename(columns={'Type': 'Provider_Type'}, inplace=True)
        food_listings_df.to_sql('food_listings', conn, if_exists='replace', index=False)

        # --- Claims Data ---
        claims_data = {
            'Claim_ID': range(2001, 2016),
            'Food_ID': np.random.choice(range(1001, 1021), size=15, replace=False),
            'Receiver_ID': np.random.randint(101, 109, size=15),
            'Status': np.random.choice(['Completed', 'Pending', 'Cancelled'], size=15, p=[0.6, 0.2, 0.2]),
            'Timestamp': [(datetime.now() - timedelta(hours=int(x))).strftime('%Y-%m-%d %H:%M:%S') for x in np.random.randint(1, 48, size=15)]
        }
        claims_df = pd.DataFrame(claims_data)
        claims_df.to_sql('claims', conn, if_exists='replace', index=False)
        
        conn.close()
        print("Database initialized and populated.")
    return sqlite3.connect(DB_NAME, check_same_thread=False)

conn = init_database()

# --- Helper Functions ---
def execute_query(query, params=None):
    """Executes a SQL query and returns the result as a DataFrame."""
    if params:
        return pd.read_sql_query(query, conn, params=params)
    return pd.read_sql_query(query, conn)

def run_commit(query, params=None):
    """Runs a SQL command that modifies the database (INSERT, UPDATE, DELETE)."""
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    conn.commit()

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Browse & Claim Food", "Manage Listings (CRUD)", "Analytics & Insights"])

# =================================================================================================
# PAGE 1: DASHBOARD
# =================================================================================================
if page == "Dashboard":
    st.title("🍲 Local Food Wastage Management Dashboard")
    st.markdown("Welcome to the central hub for managing and understanding local food redistribution efforts.")

    # --- Key Metrics ---
    st.header("System Overview")
    
    total_providers = execute_query("SELECT COUNT(DISTINCT Provider_ID) FROM providers;").iloc[0,0]
    total_receivers = execute_query("SELECT COUNT(DISTINCT Receiver_ID) FROM receivers;").iloc[0,0]
    total_food_listings = execute_query("SELECT COUNT(DISTINCT Food_ID) FROM food_listings;").iloc[0,0]
    total_claims = execute_query("SELECT COUNT(DISTINCT Claim_ID) FROM claims;").iloc[0,0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Food Providers", f"{total_providers}")
    col2.metric("Total Receivers", f"{total_receivers}")
    col3.metric("Active Food Listings", f"{total_food_listings}")
    col4.metric("Total Claims Made", f"{total_claims}")

    st.divider()

    # --- Expiring Soon ---
    st.header("⚠️ Food Expiring Soon")
    st.markdown("These items need to be claimed urgently to prevent wastage.")
    expiring_soon_query = """
        SELECT Food_Name, Quantity, Expiry_Date, Location, Provider_Type
        FROM food_listings
        WHERE Expiry_Date BETWEEN date('now') AND date('now', '+3 days')
        ORDER BY Expiry_Date ASC;
    """
    expiring_df = execute_query(expiring_soon_query)
    st.dataframe(expiring_df, use_container_width=True)
    
    st.divider()
    
    # --- Recent Claims ---
    st.header("Recent Claims Activity")
    recent_claims_query = """
        SELECT c.Timestamp, fl.Food_Name, r.Name as ReceiverName, c.Status
        FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        ORDER BY c.Timestamp DESC
        LIMIT 10;
    """
    recent_claims_df = execute_query(recent_claims_query)
    st.dataframe(recent_claims_df, use_container_width=True)

# =================================================================================================
# PAGE 2: BROWSE & CLAIM FOOD
# =================================================================================================
elif page == "Browse & Claim Food":
    st.title("Browse Available Food Listings")
    st.markdown("Find and filter surplus food available for claim in your area.")

    # --- Filtering Options ---
    st.sidebar.header("Filter Options")
    
    cities = execute_query("SELECT DISTINCT Location FROM food_listings;")['Location'].tolist()
    provider_types = execute_query("SELECT DISTINCT Provider_Type FROM food_listings;")['Provider_Type'].tolist()
    food_types = execute_query("SELECT DISTINCT Food_Type FROM food_listings;")['Food_Type'].tolist()
    meal_types = execute_query("SELECT DISTINCT Meal_Type FROM food_listings;")['Meal_Type'].tolist()

    selected_city = st.sidebar.multiselect("City", cities, default=cities)
    selected_provider_type = st.sidebar.multiselect("Provider Type", provider_types, default=provider_types)
    selected_food_type = st.sidebar.multiselect("Food Type", food_types, default=food_types)
    selected_meal_type = st.sidebar.multiselect("Meal Type", meal_types, default=meal_types)

    # --- Dynamic Query for Filtering ---
    query = """
        SELECT 
            fl.Food_Name, fl.Quantity, fl.Expiry_Date, fl.Location, fl.Food_Type, fl.Meal_Type,
            p.Name as ProviderName, p.Type as ProviderType, p.Contact as ProviderContact
        FROM food_listings fl
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        WHERE fl.Location IN ({})
        AND fl.Provider_Type IN ({})
        AND fl.Food_Type IN ({})
        AND fl.Meal_Type IN ({})
    """.format(
        ','.join('?' for _ in selected_city),
        ','.join('?' for _ in selected_provider_type),
        ','.join('?' for _ in selected_food_type),
        ','.join('?' for _ in selected_meal_type)
    )
    
    params = selected_city + selected_provider_type + selected_food_type + selected_meal_type
    
    filtered_data = execute_query(query, params)

    st.dataframe(filtered_data, use_container_width=True)

    st.info(f"Showing {len(filtered_data)} listings based on your filters.")
    
    # --- Display Contact Info ---
    st.header("Provider Contact Information")
    st.markdown("Contact providers directly to coordinate pickup.")
    
    if not filtered_data.empty:
        contact_info = filtered_data[['ProviderName', 'ProviderType', 'ProviderContact', 'Location']].drop_duplicates().reset_index(drop=True)
        st.dataframe(contact_info, use_container_width=True)
    else:
        st.warning("No listings match the current filters.")

# =================================================================================================
# PAGE 3: MANAGE LISTINGS (CRUD)
# =================================================================================================
elif page == "Manage Listings (CRUD)":
    st.title("Manage Food Listings")
    st.markdown("This section is for food providers to add, update, or remove their listings.")

    crud_option = st.selectbox("Choose an action", ["Add New Listing", "Update Existing Listing", "Remove Listing"])

    # --- ADD NEW LISTING ---
    if crud_option == "Add New Listing":
        st.header("Add a New Food Listing")
        
        providers_list = execute_query("SELECT Provider_ID, Name FROM providers;")
        provider_map = {name: pid for pid, name in zip(providers_list['Provider_ID'], providers_list['Name'])}

        with st.form("add_listing_form"):
            provider_name = st.selectbox("Select Your Organization", options=list(provider_map.keys()))
            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            expiry_date = st.date_input("Expiry Date", min_value=datetime.today())
            food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            
            submitted = st.form_submit_button("Add Listing")

            if submitted:
                provider_id = provider_map[provider_name]
                provider_details = execute_query(f"SELECT Type, City FROM providers WHERE Provider_ID = {provider_id}")
                provider_type = provider_details['Type'][0]
                location = provider_details['City'][0]
                
                insert_query = """
                    INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type, Provider_Type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                run_commit(insert_query, (food_name, quantity, expiry_date.strftime('%Y-%m-%d'), provider_id, location, food_type, meal_type, provider_type))
                st.success(f"Successfully added listing for '{food_name}'!")
                st.balloons()

    # --- UPDATE EXISTING LISTING ---
    elif crud_option == "Update Existing Listing":
        st.header("Update an Existing Food Listing")
        
        all_listings = execute_query("SELECT Food_ID, Food_Name, Provider_ID FROM food_listings")
        listing_options = {f"{row['Food_Name']} (ID: {row['Food_ID']})": row['Food_ID'] for index, row in all_listings.iterrows()}
        
        selected_listing_str = st.selectbox("Select Listing to Update", options=list(listing_options.keys()))
        
        if selected_listing_str:
            food_id_to_update = listing_options[selected_listing_str]
            current_data = execute_query(f"SELECT * FROM food_listings WHERE Food_ID = {food_id_to_update}").iloc[0]

            with st.form("update_listing_form"):
                st.write(f"**Updating:** {current_data['Food_Name']}")
                new_quantity = st.number_input("New Quantity", min_value=1, step=1, value=int(current_data['Quantity']))
                new_expiry_date = st.date_input("New Expiry Date", min_value=datetime.today(), value=datetime.strptime(current_data['Expiry_Date'], '%Y-%m-%d').date())
                
                update_submitted = st.form_submit_button("Update Listing")

                if update_submitted:
                    update_query = """
                        UPDATE food_listings
                        SET Quantity = ?, Expiry_Date = ?
                        WHERE Food_ID = ?
                    """
                    run_commit(update_query, (new_quantity, new_expiry_date.strftime('%Y-%m-%d'), food_id_to_update))
                    st.success(f"Successfully updated listing ID {food_id_to_update}!")

    # --- REMOVE LISTING ---
    elif crud_option == "Remove Listing":
        st.header("Remove a Food Listing")
        
        all_listings = execute_query("SELECT Food_ID, Food_Name FROM food_listings")
        listing_options = {f"{row['Food_Name']} (ID: {row['Food_ID']})": row['Food_ID'] for index, row in all_listings.iterrows()}
        
        selected_listing_str = st.selectbox("Select Listing to Remove", options=list(listing_options.keys()))
        
        if st.button("Remove Listing", type="primary"):
            food_id_to_delete = listing_options[selected_listing_str]
            # First, delete associated claims to maintain integrity
            run_commit(f"DELETE FROM claims WHERE Food_ID = {food_id_to_delete}")
            # Then, delete the listing
            run_commit(f"DELETE FROM food_listings WHERE Food_ID = {food_id_to_delete}")
            st.success(f"Successfully removed listing ID {food_id_to_delete} and any associated claims.")
            st.warning("The page will refresh to reflect the changes.")
            st.experimental_rerun()

# =================================================================================================
# PAGE 4: ANALYTICS & INSIGHTS
# =================================================================================================
elif page == "Analytics & Insights":
    st.title("Analytics & Insights")
    st.markdown("Deep dive into the data to understand trends in food donation, claims, and distribution.")

    def display_query_and_result(query, title, chart_type=None, chart_params=None):
        """Helper to display a query, its result, and an optional chart."""
        st.subheader(title)
        with st.expander("View SQL Query"):
            st.code(query, language='sql')
        
        df = execute_query(query)
        st.dataframe(df, use_container_width=True)
        
        if chart_type and not df.empty:
            if chart_type == 'bar' and chart_params:
                st.bar_chart(df.set_index(chart_params['x']), y=chart_params['y'])
            elif chart_type == 'pie' and chart_params:
                st.altair_chart(alt.Chart(df).mark_arc().encode(
                    theta=alt.Theta(field=chart_params['values'], type="quantitative"),
                    color=alt.Color(field=chart_params['names'], type="nominal"),
                    tooltip=[chart_params['names'], chart_params['values']]
                ), use_container_width=True)
        st.divider()

    # --- All 15 Queries ---
    import altair as alt

    # 1
    display_query_and_result(
        """
        SELECT p.City, COUNT(DISTINCT p.Provider_ID) AS NumberOfProviders, COUNT(DISTINCT r.Receiver_ID) AS NumberOfReceivers
        FROM providers p LEFT JOIN receivers r ON p.City = r.City GROUP BY p.City;
        """,
        "1. Number of Food Providers and Receivers by City"
    )
    # 2
    display_query_and_result(
        """
        SELECT p.Type, SUM(fl.Quantity) AS TotalQuantityDonated FROM food_listings fl
        JOIN providers p ON fl.Provider_ID = p.Provider_ID GROUP BY p.Type ORDER BY TotalQuantityDonated DESC;
        """,
        "2. Top Contributing Provider Types by Food Quantity",
        chart_type='bar', chart_params={'x': 'Type', 'y': 'TotalQuantityDonated'}
    )
    # 3
    display_query_and_result(
        "SELECT Name, Type, Address, Contact FROM providers WHERE City = 'Bangalore';",
        "3. Contact Information for Providers in Bangalore"
    )
    # 4
    display_query_and_result(
        """
        SELECT r.Name, r.Type, r.City, COUNT(c.Claim_ID) AS NumberOfClaims FROM claims c
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID GROUP BY r.Receiver_ID ORDER BY NumberOfClaims DESC LIMIT 10;
        """,
        "4. Top Receivers by Number of Claims",
        chart_type='bar', chart_params={'x': 'Name', 'y': 'NumberOfClaims'}
    )
    # 5
    display_query_and_result(
        "SELECT SUM(Quantity) AS TotalAvailableQuantity FROM food_listings;",
        "5. Total Quantity of Food Available"
    )
    # 6
    display_query_and_result(
        "SELECT Location, COUNT(Food_ID) AS NumberOfListings FROM food_listings GROUP BY Location ORDER BY NumberOfListings DESC;",
        "6. Number of Food Listings by City",
        chart_type='bar', chart_params={'x': 'Location', 'y': 'NumberOfListings'}
    )
    # 7
    display_query_and_result(
        "SELECT Food_Type, COUNT(Food_ID) AS ListingCount FROM food_listings GROUP BY Food_Type ORDER BY ListingCount DESC;",
        "7. Most Common Food Types Available"
    )
    # 8
    display_query_and_result(
        """
        SELECT fl.Food_Name, COUNT(c.Claim_ID) AS NumberOfClaims FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID GROUP BY fl.Food_ID ORDER BY NumberOfClaims DESC;
        """,
        "8. Number of Claims per Food Item"
    )
    # 9
    display_query_and_result(
        """
        SELECT p.Name, p.Type, COUNT(c.Claim_ID) AS SuccessfulClaims FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID JOIN providers p ON fl.Provider_ID = p.Provider_ID
        WHERE c.Status = 'Completed' GROUP BY p.Provider_ID ORDER BY SuccessfulClaims DESC;
        """,
        "9. Providers with Most Successful Claims"
    )
    # 10
    query10 = "SELECT Status, COUNT(*) AS ClaimCount, (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims)) AS Percentage FROM claims GROUP BY Status;"
    st.subheader("10. Percentage Distribution of Claim Statuses")
    with st.expander("View SQL Query"):
        st.code(query10, language='sql')
    df10 = execute_query(query10)
    st.dataframe(df10, use_container_width=True)
    if not df10.empty:
        pie_chart = alt.Chart(df10).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Percentage", type="quantitative"),
            color=alt.Color(field="Status", type="nominal", title="Claim Status"),
            tooltip=['Status', 'ClaimCount', 'Percentage']
        ).properties(title="Claim Status Distribution")
        st.altair_chart(pie_chart, use_container_width=True)
    st.divider()
    # 11
    display_query_and_result(
        """
        SELECT r.Name, AVG(fl.Quantity) AS AverageQuantityPerClaim FROM claims c
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        WHERE c.Status = 'Completed' GROUP BY r.Receiver_ID ORDER BY AverageQuantityPerClaim DESC;
        """,
        "11. Average Quantity of Food per Claim for Each Receiver"
    )
    # 12
    display_query_and_result(
        """
        SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS NumberOfClaims FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID GROUP BY fl.Meal_Type ORDER BY NumberOfClaims DESC;
        """,
        "12. Most Claimed Meal Types",
        chart_type='bar', chart_params={'x': 'Meal_Type', 'y': 'NumberOfClaims'}
    )
    # 13
    display_query_and_result(
        """
        SELECT p.Name, p.City, SUM(fl.Quantity) AS TotalQuantityDonated FROM food_listings fl
        JOIN providers p ON fl.Provider_ID = p.Provider_ID GROUP BY p.Provider_ID ORDER BY TotalQuantityDonated DESC;
        """,
        "13. Total Food Quantity Donated by Each Provider"
    )
    # 14
    display_query_and_result(
        """
        SELECT Food_Name, Quantity, Expiry_Date, Location FROM food_listings
        WHERE Expiry_Date BETWEEN date('now') AND date('now', '+3 days') ORDER BY Expiry_Date ASC;
        """,
        "14. Food Items Expiring in the Next 3 Days"
    )
    # 15
    display_query_and_result(
        """
        SELECT p.Name, p.Type, p.City, fl.Food_Name, fl.Quantity FROM food_listings fl
        JOIN providers p ON fl.Provider_ID = p.Provider_ID LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
        WHERE c.Claim_ID IS NULL;
        """,
        "15. Providers with Unclaimed Food Listings"
    )
