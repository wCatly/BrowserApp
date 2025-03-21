from neo4j import GraphDatabase
import time
from src.config import LOCAL_NEO4J_URI, LOCAL_NEO4J_USER, LOCAL_NEO4J_PASSWORD
from src.config import AURA_NEO4J_URI, AURA_NEO4J_USER, AURA_NEO4J_PASSWORD

def test_connection(uri, auth, name):
    print(f"\nTesting {name} Neo4j connection...")
    print(f"URI: {uri}")
    try:
        # Add connection timeout and max retry time
        start_time = time.time()
        max_time = 8  # 8 seconds max wait time
        
        # Create driver with timeout settings
        driver = GraphDatabase.driver(
            uri, 
            auth=auth,
            connection_timeout=3,  # 3 second connection timeout
            max_connection_lifetime=5  # 5 second connection lifetime
        )
        
        # Try to verify connectivity with timeout
        while time.time() - start_time < max_time:
            try:
                driver.verify_connectivity()
                print(f"✅ {name} Connection successful!")
                driver.close()
                return True
            except Exception as inner_e:
                if time.time() - start_time >= max_time:
                    raise inner_e
                time.sleep(0.5)
        
        driver.close()
        return True

    except Exception as e:
        print(f"❌ {name} Connection failed with error: {e}")
        return False

# Test local Neo4j connection
local_success = test_connection(
    LOCAL_NEO4J_URI, 
    (LOCAL_NEO4J_USER, LOCAL_NEO4J_PASSWORD),
    "Local"
)

# Test Aura Neo4j connection
aura_success = test_connection(
    AURA_NEO4J_URI, 
    (AURA_NEO4J_USER, AURA_NEO4J_PASSWORD),
    "Aura"
)

print("\n=== CONNECTION TEST SUMMARY ===")
if local_success:
    print("✅ Local Neo4j connection successful")
    print("   You can use the app with your local Neo4j database")
    print("   Make sure in config.py: USE_LOCAL_NEO4J = True")
else:
    print("❌ Local Neo4j connection failed")
    print("   To use a local Neo4j database:")
    print("   1. Install Neo4j Desktop or run a Neo4j Docker container")
    print("   2. Update LOCAL_NEO4J_PASSWORD in config.py")
    print("   3. Make sure Neo4j is running and accessible")

if aura_success:
    print("\n✅ Neo4j Aura connection successful")
    print("   You can use the app with your Aura cloud instance")
    print("   Make sure in config.py: USE_LOCAL_NEO4J = False")
else:
    print("\n❌ Neo4j Aura connection failed")
    print("   Possible reasons:")
    print("   1. Your Neo4j Aura instance might be inactive or paused")
    print("   2. The credentials might be incorrect or expired")
    print("   3. There might be network connectivity issues")
    print("   4. Check your Neo4j Aura account to verify status")

if not local_success and not aura_success:
    print("\n⚠️ Neither connection method works!")
    print("   You'll need to fix one of these connections to use the application")
else:
    print("\n✅ At least one connection method works!")
    print("   You can use the app by setting the correct USE_LOCAL_NEO4J value in config.py") 