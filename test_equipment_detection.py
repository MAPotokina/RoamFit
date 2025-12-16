"""Test script for Equipment Detection Agent."""
import json
from pathlib import Path

from agents.equipment_detection import detect_equipment
from database import get_db_connection

print("Testing Equipment Detection Agent...")
print("-" * 50)

# Check for test image
test_images = [
    "test_image.jpg",
    "test_image.png",
    "test.jpg",
    "test.png",
    "gym.jpg",
    "equipment.jpg",
]
image_path = None

for img in test_images:
    if Path(img).exists():
        image_path = img
        break

if image_path:
    print(f"\n1. Testing detect_equipment() with: {image_path}")
    try:
        result = detect_equipment(image_path, location="Test Location")
        print("✓ Equipment detection successful:")
        print(f"  Detection ID: {result['detection_id']}")
        print(f"  Equipment found: {result['equipment']}")
        print(f"  Image path: {result['image_path']}")
        if "error" in result:
            print(f"  Warning: {result['error']}")

        # Verify database entry
        print("\n2. Verifying database entry:")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM equipment_detections WHERE id = ?", (result["detection_id"],)
            )
            row = cursor.fetchone()
            if row:
                print("✓ Database entry found:")
                print(f"  ID: {row['id']}")
                print(f"  Timestamp: {row['timestamp']}")
                print(f"  Image path: {row['image_path']}")
                print(f"  Equipment: {json.loads(row['detected_equipment'])}")
                print(f"  Location: {row['location']}")
            else:
                print("✗ Database entry not found")

    except FileNotFoundError as e:
        print(f"✗ {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  (This is expected if OPENAI_API_KEY is not set)")
else:
    print("\n⚠️  No test image found.")
    print("   Place a test image (jpg/png) in the project root")
    print("   and run this script again.")

# Test error handling
print("\n3. Testing error handling (non-existent file):")
try:
    result = detect_equipment("nonexistent.jpg")
except FileNotFoundError as e:
    print(f"✓ Correctly raised FileNotFoundError: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

print("\n" + "-" * 50)
print("Test complete!")
