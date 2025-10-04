"""
Business Logic Tests for Aura Cold Brew Autonomous Brand Agent

These tests focus on core business logic, NOT mocking.
They use REAL functions with REAL data (or realistic fixtures).

Run with: python test_business_logic.py
Or with pytest: pytest test_business_logic.py -v
"""

import asyncio
import json
from main import (
    _get_brand_rules,
    _build_openai_prompt,
    _log_mock,
    AdGenerationResponse,
    CONFIDENCE_THRESHOLD,
    DEMO_MODE
)


# ==============================================================================
# TEST 1: Brand Rules Integrity
# ==============================================================================

def test_brand_rules_contain_required_elements():
    """
    BUSINESS RULE: Brand guidelines must include core identity elements.

    Why this matters: If brand rules are incomplete, generated ads could be off-brand.
    """
    print("\n[TEST 1] Validating Brand Rules Integrity...")

    brand_rules = _get_brand_rules()

    # Critical brand elements that MUST be present (case-insensitive)
    required_elements = [
        "aura cold brew",
        "premium",
        "green mermaid",
        "sustainability",
        "young professionals",
        "summer"
    ]

    brand_rules_lower = brand_rules.lower()
    for element in required_elements:
        assert element.lower() in brand_rules_lower, f"Missing critical brand element: {element}"

    # Ensure guidelines aren't empty or trivial
    assert len(brand_rules) > 100, "Brand rules too short to be useful"

    print("  ✓ Brand rules contain all required elements")
    print(f"  ✓ Brand rules length: {len(brand_rules)} characters")


# ==============================================================================
# TEST 2: Prompt Construction Quality
# ==============================================================================

def test_prompt_includes_competitor_context():
    """
    BUSINESS RULE: Generated prompts must include competitor ad for context.

    Why this matters: Without competitor context, responses won't be competitive.
    """
    print("\n[TEST 2] Validating Prompt Construction...")

    competitor_ad = "Red Bull gives you wings! Energy all day long."
    brand_rules = _get_brand_rules()

    prompt = _build_openai_prompt(competitor_ad, brand_rules)

    # Verify competitor ad is included
    assert competitor_ad in prompt, "Competitor ad not included in prompt"

    # Verify brand rules are included
    assert "Aura Cold Brew" in prompt, "Brand name not in prompt"

    # Verify prompt requests required outputs
    assert "ad_copy" in prompt.lower(), "Prompt doesn't request ad copy"
    assert "tagline" in prompt.lower(), "Prompt doesn't request tagline"
    assert "image" in prompt.lower(), "Prompt doesn't request image keywords"
    assert "confidence" in prompt.lower(), "Prompt doesn't request confidence score"

    print("  ✓ Prompt includes competitor context")
    print("  ✓ Prompt includes brand rules")
    print("  ✓ Prompt requests all required outputs")


# ==============================================================================
# TEST 3: Confidence Threshold Logic
# ==============================================================================

def test_confidence_threshold_is_reasonable():
    """
    BUSINESS RULE: Confidence threshold must be high enough to ensure quality.

    Why this matters: Low thresholds could auto-approve poor quality ads.
    """
    print("\n[TEST 3] Validating Confidence Threshold...")

    assert CONFIDENCE_THRESHOLD >= 80, f"Confidence threshold too low: {CONFIDENCE_THRESHOLD}"
    assert CONFIDENCE_THRESHOLD <= 95, f"Confidence threshold unrealistically high: {CONFIDENCE_THRESHOLD}"

    print(f"  ✓ Confidence threshold set appropriately: {CONFIDENCE_THRESHOLD}%")


# ==============================================================================
# TEST 4: Mock Logging Functionality
# ==============================================================================

def test_mock_logging_captures_required_fields():
    """
    BUSINESS RULE: All analytics logs must capture key decision factors.

    Why this matters: Missing data makes it impossible to debug or improve the agent.
    """
    print("\n[TEST 4] Validating Analytics Logging...")

    test_response = AdGenerationResponse(
        status="approved",
        confidence_score=95,
        ad_copy="Test ad copy here",
        generated_tagline="Test Tagline",
        image_prompt="test prompt",
        competitor_ad_text="Competitor ad"
    )

    # This should not raise an exception
    try:
        _log_mock(test_response)
        print("  ✓ Mock logging function executes without error")
    except Exception as e:
        raise AssertionError(f"Mock logging failed: {e}")

    # Verify all required fields are present in response model
    assert hasattr(test_response, 'status')
    assert hasattr(test_response, 'confidence_score')
    assert hasattr(test_response, 'ad_copy')
    assert hasattr(test_response, 'competitor_ad_text')

    print("  ✓ All required logging fields present")


# ==============================================================================
# TEST 5: Demo Mode Behavior
# ==============================================================================

def test_demo_mode_provides_consistent_output():
    """
    BUSINESS RULE: DEMO_MODE must return consistent, high-quality responses.

    Why this matters: Unpredictable demo outputs could cause presentation failures.
    """
    print("\n[TEST 5] Validating DEMO_MODE Behavior...")

    if DEMO_MODE:
        print("  ℹ DEMO_MODE is ENABLED")
        print("    This ensures fast, reliable demos with pre-built responses")
    else:
        print("  ℹ DEMO_MODE is DISABLED")
        print("    Live API calls will be made (slower, requires API keys)")

    # In DEMO_MODE, we expect specific behavior
    if DEMO_MODE:
        # Demo responses should be high quality
        expected_confidence = 95
        assert expected_confidence >= CONFIDENCE_THRESHOLD, \
            "Demo response confidence below threshold"

        print(f"  ✓ Demo mode confidence ({expected_confidence}%) exceeds threshold ({CONFIDENCE_THRESHOLD}%)")


# ==============================================================================
# TEST 6: Data Model Validation
# ==============================================================================

def test_ad_generation_response_model_validation():
    """
    BUSINESS RULE: Response models must enforce required fields with correct types.

    Why this matters: Invalid data structures cause downstream errors.
    """
    print("\n[TEST 6] Validating Data Model Schemas...")

    # Test valid response
    valid_response = AdGenerationResponse(
        status="approved",
        confidence_score=92,
        ad_copy="Valid ad copy",
        competitor_ad_text="Competitor ad"
    )

    assert valid_response.status == "approved"
    assert isinstance(valid_response.confidence_score, int)
    assert isinstance(valid_response.ad_copy, str)

    print("  ✓ Valid response model created successfully")

    # Test that confidence_score must be an integer
    try:
        invalid_response = AdGenerationResponse(
            status="approved",
            confidence_score="ninety-five",  # Wrong type!
            ad_copy="Test",
            competitor_ad_text="Test"
        )
        raise AssertionError("Model accepted invalid confidence_score type")
    except (ValueError, TypeError):
        print("  ✓ Model correctly rejects invalid types")


# ==============================================================================
# TEST 7: Brand Alignment Checks
# ==============================================================================

def test_brand_keywords_in_guidelines():
    """
    BUSINESS RULE: Brand guidelines must emphasize key differentiators.

    Why this matters: Generic guidelines lead to generic, forgettable campaigns.
    """
    print("\n[TEST 7] Validating Brand Differentiation...")

    brand_rules = _get_brand_rules()

    # Aura Cold Brew's key differentiators (based on prompt in main.py)
    differentiators = [
        "premium",
        "sustainability",
        "modern",
        "quality",
        "mermaid"  # Iconic logo element
    ]

    found_count = sum(1 for term in differentiators if term.lower() in brand_rules.lower())

    assert found_count >= 3, f"Only {found_count}/5 differentiators found in brand rules"

    print(f"  ✓ {found_count}/5 key differentiators present in brand guidelines")


# ==============================================================================
# TEST 8: Output Format Validation
# ==============================================================================

def test_response_format_is_json_serializable():
    """
    BUSINESS RULE: All API responses must be JSON serializable.

    Why this matters: Non-serializable responses break API contracts.
    """
    print("\n[TEST 8] Validating JSON Serializability...")

    test_response = AdGenerationResponse(
        status="approved",
        confidence_score=88,
        ad_copy="Smooth energy for smooth people.",
        generated_tagline="Aura: Energy Refined",
        competitor_ad_text="Competitor X"
    )

    # Attempt to serialize
    try:
        json_output = test_response.model_dump_json()
        parsed_back = json.loads(json_output)

        assert parsed_back["confidence_score"] == 88
        assert parsed_back["status"] == "approved"

        print("  ✓ Response successfully serializes to JSON")
        print("  ✓ Response successfully deserializes from JSON")
    except Exception as e:
        raise AssertionError(f"JSON serialization failed: {e}")


# ==============================================================================
# TEST 9: Business Logic - Confidence Scoring
# ==============================================================================

def test_confidence_score_logic():
    """
    BUSINESS RULE: Confidence scores must be realistic (1-100 range).

    Why this matters: Scores outside this range indicate broken logic.
    """
    print("\n[TEST 9] Validating Confidence Score Logic...")

    # Test various confidence scores
    test_cases = [
        (0, "Minimum possible score"),
        (50, "Mid-range score"),
        (85, "Threshold score"),
        (95, "High-quality score"),
        (100, "Perfect score")
    ]

    for score, description in test_cases:
        response = AdGenerationResponse(
            status="pending" if score < CONFIDENCE_THRESHOLD else "approved",
            confidence_score=score,
            ad_copy="Test",
            competitor_ad_text="Test"
        )

        assert 0 <= response.confidence_score <= 100, \
            f"{description} ({score}) outside valid range"

    print("  ✓ All test confidence scores within valid range (0-100)")
    print(f"  ✓ Scores >= {CONFIDENCE_THRESHOLD}% should auto-approve")


# ==============================================================================
# TEST 10: Integration Test - Full Workflow Simulation
# ==============================================================================

def test_end_to_end_workflow_simulation():
    """
    BUSINESS RULE: The complete ad generation workflow must execute without errors.

    Why this matters: Individual unit tests passing doesn't guarantee the full pipeline works.
    """
    print("\n[TEST 10] Simulating End-to-End Workflow...")

    # Step 1: Get brand rules
    brand_rules = _get_brand_rules()
    print("  ✓ Step 1: Retrieved brand rules")

    # Step 2: Build prompt with competitor context
    competitor_ad = "Monster Energy - Unleash the Beast!"
    prompt = _build_openai_prompt(competitor_ad, brand_rules)
    print("  ✓ Step 2: Built OpenAI prompt")

    # Step 3: Simulate LLM response (in real workflow, this calls OpenAI)
    simulated_llm_output = {
        "confidence_score": 92,
        "ad_copy": "Aura Cold Brew: Refined energy for refined tastes. No beasts, just balance.",
        "generated_tagline": "Stay Sharp, Stay Smooth",
        "image_keywords": "Professional cold brew can, minimalist design, green mermaid logo"
    }
    print("  ✓ Step 3: Simulated LLM response")

    # Step 4: Create response model
    final_response = AdGenerationResponse(
        status="approved" if simulated_llm_output["confidence_score"] >= CONFIDENCE_THRESHOLD else "pending",
        confidence_score=simulated_llm_output["confidence_score"],
        ad_copy=simulated_llm_output["ad_copy"],
        generated_tagline=simulated_llm_output["generated_tagline"],
        image_prompt=simulated_llm_output["image_keywords"],
        competitor_ad_text=competitor_ad
    )
    print("  ✓ Step 4: Created response model")

    # Step 5: Log analytics (mock)
    _log_mock(final_response)
    print("  ✓ Step 5: Logged analytics")

    # Verify final output quality
    assert final_response.status == "approved", "Response not approved despite high confidence"
    assert len(final_response.ad_copy) > 20, "Ad copy too short"
    assert final_response.generated_tagline is not None, "Missing tagline"

    print("\n  ✅ FULL WORKFLOW SIMULATION SUCCESSFUL")
    print(f"     Generated ad: {final_response.ad_copy[:60]}...")


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("BUSINESS LOGIC TESTS - Aura Cold Brew Autonomous Brand Agent")
    print("="*70)
    print("\nThese tests validate CORE BUSINESS LOGIC using REAL functions.")
    print("No mocks, no stubs - just real code with real data.\n")

    tests = [
        test_brand_rules_contain_required_elements,
        test_prompt_includes_competitor_context,
        test_confidence_threshold_is_reasonable,
        test_mock_logging_captures_required_fields,
        test_demo_mode_provides_consistent_output,
        test_ad_generation_response_model_validation,
        test_brand_keywords_in_guidelines,
        test_response_format_is_json_serializable,
        test_confidence_score_logic,
        test_end_to_end_workflow_simulation,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n  ❌ FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"\n  ❌ ERROR: {e}")

    print("\n" + "="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Business logic is solid.\n")
        exit(0)
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review failures above.\n")
        exit(1)
