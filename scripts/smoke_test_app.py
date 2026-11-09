"""Automated smoke test for the WellSense Streamlit application.

Tests:
1. Each file in app/pages/ and app/main.py loads without raising an exception via AppTest.from_file().
2. Invalid input testing:
   - Missing consent
   - Blank gender
   - Age outside allowed range (e.g. 5, 75)
3. Full end-to-end flow:
   - Assessment submission with valid inputs
   - Prediction results and explanations verification
   - Recommendation generation and display
   - Feedback submission
   - Re-ranking using feedback
   - Feedback & History viewing, feedback reset, and full session data deletion.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest
from app.state import get_db


def test_individual_pages_load():
    """Verify that each page and main.py can load directly without exception."""
    print("--> Testing standalone page loads...")
    files = [ROOT / "app" / "main.py"] + sorted((ROOT / "app" / "pages").glob("*.py"))
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        at = AppTest.from_file(str(f))
        at.run(timeout=10)
        assert len(at.exception) == 0, f"Exception in {rel}: {[e.value for e in at.exception]}"
        print(f"  [OK] {rel} loaded with 0 exceptions")


def test_invalid_inputs():
    """Verify error handling on invalid inputs: consent, gender, age."""
    print("--> Testing invalid input handling...")

    # Case 1: Missing consent
    at = AppTest.from_file(str(ROOT / "app" / "main.py"))
    at.run(timeout=10)
    at.switch_page("pages/2_Assessment.py").run(timeout=10)
    at.button[0].click().run(timeout=10)
    assert len(at.exception) == 0, f"Exception on missing consent: {[e.value for e in at.exception]}"
    err_texts = [e.value for e in at.error]
    assert any("consent" in t.lower() for t in err_texts), f"Expected consent error, got: {err_texts}"
    print("  [OK] Missing consent correctly caught:", err_texts)

    # Case 2: Blank gender
    at = AppTest.from_file(str(ROOT / "app" / "main.py"))
    at.run(timeout=10)
    at.switch_page("pages/2_Assessment.py").run(timeout=10)
    at.checkbox[0].check()
    at.selectbox[0].select("")
    at.selectbox[2].select("3.00 - 3.49")
    at.selectbox[3].select("engineering_it")
    at.button[0].click().run(timeout=10)
    assert len(at.exception) == 0
    err_texts = [e.value for e in at.error]
    assert any("gender" in t.lower() for t in err_texts), f"Expected gender error, got: {err_texts}"
    print("  [OK] Blank gender correctly caught:", err_texts)

    # Case 3: Age outside allowed range (< 16, e.g. 5)
    at = AppTest.from_file(str(ROOT / "app" / "main.py"))
    at.run(timeout=10)
    at.switch_page("pages/2_Assessment.py").run(timeout=10)
    at.checkbox[0].check()
    at.selectbox[0].select("Female")
    at.number_input[0].set_value(5)
    at.selectbox[2].select("3.00 - 3.49")
    at.selectbox[3].select("engineering_it")
    at.button[0].click().run(timeout=10)
    assert len(at.exception) == 0
    err_texts = [e.value for e in at.error]
    assert any("age" in t.lower() for t in err_texts), f"Expected age error for age=5, got: {err_texts}"
    print("  [OK] Age < 16 correctly caught:", err_texts)

    # Case 4: Age outside allowed range (> 60, e.g. 75)
    at = AppTest.from_file(str(ROOT / "app" / "main.py"))
    at.run(timeout=10)
    at.switch_page("pages/2_Assessment.py").run(timeout=10)
    at.checkbox[0].check()
    at.selectbox[0].select("Female")
    at.number_input[0].set_value(75)
    at.selectbox[2].select("3.00 - 3.49")
    at.selectbox[3].select("engineering_it")
    at.button[0].click().run(timeout=10)
    assert len(at.exception) == 0
    err_texts = [e.value for e in at.error]
    assert any("age" in t.lower() for t in err_texts), f"Expected age error for age=75, got: {err_texts}"
    print("  [OK] Age > 60 correctly caught:", err_texts)


def test_full_flow():
    """Verify the full user journey through all pages and database operations."""
    print("--> Testing full user flow...")
    at = AppTest.from_file(str(ROOT / "app" / "main.py"))
    at.run(timeout=10)
    assert len(at.exception) == 0

    # 1. Open Assessment and fill valid form
    at.switch_page("pages/2_Assessment.py").run(timeout=10)
    at.checkbox[0].check()
    at.selectbox[0].select("Female")
    at.number_input[0].set_value(20)
    at.selectbox[1].select(2)
    at.selectbox[2].select("3.00 - 3.49")
    at.selectbox[3].select("engineering_it")
    # Also set a lifestyle value (e.g. sleep_hours = 5)
    at.number_input[1].set_value(5.0)

    # 2. Submit form
    at.button[0].click().run(timeout=10)
    assert len(at.exception) == 0
    assert len(at.error) == 0, f"Unexpected form errors: {[e.value for e in at.error]}"
    assert len(at.success) > 0, "Expected success message after submission"
    print("  [OK] Step 1 & 2: Assessment filled and submitted successfully")

    # 3. Check Prediction Results
    at.switch_page("pages/3_Prediction_Results.py").run(timeout=10)
    assert len(at.exception) == 0
    assert len(at.metric) >= 1, "Expected prediction metric"
    print(f"  [OK] Step 3a: Prediction metric displayed: {at.metric[0].value}")

    # 3b. Check Recommendations
    at.switch_page("pages/4_Personalized_Recommendations.py").run(timeout=10)
    assert len(at.exception) == 0
    assert len(at.radio) >= 1, "Expected recommendation feedback radios"
    assert len(at.button) >= 2, "Expected save feedback and re-rank buttons"
    print(f"  [OK] Step 3b: {len(at.radio)} recommendation(s) displayed")

    # 4. Save feedback
    at.radio[0].set_value("helpful")
    at.button[0].click().run(timeout=10)
    assert len(at.exception) == 0
    assert len(at.success) >= 1, "Expected feedback saved success message"
    print("  [OK] Step 4: Feedback saved successfully")

    # 5. Re-rank using feedback
    rerank_btn = [b for b in at.button if "Re-rank" in b.label]
    assert len(rerank_btn) == 1, "Re-rank button not found"
    rerank_btn[0].click().run(timeout=10)
    assert len(at.exception) == 0
    new_order_texts = [m.value for m in at.markdown if "New order" in m.value]
    assert len(new_order_texts) >= 1, "Expected new order displayed after re-ranking"
    print(f"  [OK] Step 5: Re-ranking succeeded: {new_order_texts[0]}")

    # 6. Feedback & History page, reset and delete
    at.switch_page("pages/5_Feedback_and_History.py").run(timeout=10)
    assert len(at.exception) == 0
    assert len(at.dataframe) >= 1, "Expected history dataframe"

    db = get_db()
    sid = at.session_state["sid"]
    assert db.count("assessments", sid) == 1
    assert db.count("feedback", sid) == 1
    print(f"  [OK] Step 6a: History table verified; DB has 1 assessment, 1 feedback for session {sid[:8]}...")

    # Reset feedback
    reset_btn = [b for b in at.button if "Reset" in b.label]
    assert len(reset_btn) == 1
    reset_btn[0].click().run(timeout=10)
    assert len(at.exception) == 0
    assert db.count("feedback", sid) == 0
    assert db.count("assessments", sid) == 1
    print("  [OK] Step 6b: Feedback reset successfully (feedback count = 0, assessment count = 1)")

    # Delete all stored data
    del_btn = [b for b in at.button if "Delete" in b.label]
    assert len(del_btn) == 1
    del_btn[0].click().run(timeout=10)
    assert len(at.exception) == 0
    assert db.count("assessments", sid) == 0
    assert db.count("predictions", sid) == 0
    assert db.count("recommendations", sid) == 0
    assert db.count("feedback", sid) == 0
    assert "result" not in at.session_state
    print("  [OK] Step 6c: Delete all stored data successfully cleared all session records")


def main():
    test_individual_pages_load()
    test_invalid_inputs()
    test_full_flow()
    print("\n=== ALL STREAMLIT SMOKE TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    main()
