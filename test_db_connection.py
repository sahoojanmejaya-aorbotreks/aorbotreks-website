import psycopg2
from psycopg2 import OperationalError

try:
    # Connection parameters from settings.py
    conn_params = {
        'dbname': 'postgres',
        'user': 'postgres.xsconhhzyaiowokwsqne',
        'password': 'P.sunny@2005',
        'host': 'aws-0-ap-south-1.pooler.supabase.com',
        'port': '6543',
        'sslmode': 'require'
    }
    
    print("Attempting to connect to the database...")
    conn = psycopg2.connect(**conn_params)
    print("Successfully connected to the database!")
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    print(f"Database version: {db_version[0]}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
except OperationalError as e:
    print(f"Error connecting to the database: {e}")
    print("\nTroubleshooting steps:")
    print("1. Check if your IP is whitelisted in Supabase dashboard")
    print("2. Verify the database credentials in settings.py")
    print("3. Ensure the database is running in Supabase")
    print("4. Check your internet connection")
    print("5. Try disabling any VPN or firewall temporarily")
