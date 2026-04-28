from dnf.vision_fallback import VisionFallbackAdvisor


def test_extract_text_collects_output_text_blocks():
    response_json = {
        "output": [
            {
                "content": [
                    {"type": "output_text", "text": '{"direction":"RIGHT","confidence":0.82,"reason":"door on right"}'}
                ]
            }
        ]
    }

    assert '"direction":"RIGHT"' in VisionFallbackAdvisor._extract_text(response_json)


def test_extract_json_block_ignores_wrapping_text():
    raw_text = '```json {"direction":"UP","confidence":0.6,"reason":"stairs above"} ```'
    parsed = VisionFallbackAdvisor._extract_json_block(raw_text)

    assert parsed["direction"] == "UP"
    assert parsed["confidence"] == 0.6


def test_should_consult_after_threshold_and_cooldown():
    advisor = VisionFallbackAdvisor(api_key="test-key", trigger_misses=2, cooldown_seconds=0)

    advisor.record_target_missing()
    assert advisor.should_consult() is False

    advisor.record_target_missing()
    assert advisor.should_consult() is True


def test_normalize_direction_rejects_unknown_values():
    assert VisionFallbackAdvisor._normalize_direction("right_up") == "RIGHT_UP"
    assert VisionFallbackAdvisor._normalize_direction("teleport") == ""
