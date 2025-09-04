from supabase import create_client
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xsconhhzyaiowokwsqne.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzY29uaGh6eWFpb3dva3dzcW5lIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTEwMjA2MiwiZXhwIjoyMDY0Njc4MDYyfQ.N2CNRhk4y43eq5XktZGt_z5J3Zv_DVyfHH8Zd68QxXU")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)