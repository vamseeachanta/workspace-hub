import ee

def test_ee_import():
    print("Testing Google Earth Engine import...")
    try:
        # Check version
        print(f"EE version: {ee.__version__}")
        # Initialization will fail without auth, but we can catch it
        print("Attempting initialization (expected to fail if not authenticated)...")
        try:
            ee.Initialize()
            print("EE initialized successfully!")
        except Exception as e:
            print(f"EE initialization failed (expected): {e}")
        
        print("EE library check: OK")
    except Exception as e:
        print(f"EE check failed: {e}")
        exit(1)

if __name__ == "__main__":
    test_ee_import()
