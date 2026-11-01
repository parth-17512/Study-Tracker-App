import pytest
from app.services.subject_grouping_service import SubjectGroupingService
from unittest.mock import MagicMock

def test_subject_grouping_with_similar_topics():
    # Example from specification:
    # Python - 4h (14400s), Python Programming - 3h (10800s), Python Projects - 2h (7200s)
    # Math - 2h (7200s)
    dist = {
        "Python": 14400,
        "Python Programming": 10800,
        "Python Projects": 7200,
        "Calculus": 7200
    }
    original_dist = dist.copy()

    mock_router = MagicMock()
    # Mock LLM returning valid grouping
    mock_router.generate_text.return_value = '{"groups": [{"label": "Python", "topics": ["Python", "Python Programming", "Python Projects"]}, {"label": "Mathematics", "topics": ["Calculus"]}]}'

    service = SubjectGroupingService(provider_router=mock_router)
    result = service.group_topics(dist)

    # 1. Total seconds must exactly match
    expected_total = sum(dist.values())
    assert result["total_seconds"] == expected_total

    group_sums = sum(g["total_seconds"] for g in result["groups"])
    assert group_sums == expected_total

    # 2. Check Python group
    python_group = next(g for g in result["groups"] if g["label"] == "Python")
    assert python_group["total_seconds"] == 32400 # 9 hours
    assert python_group["total_minutes"] == 540
    assert "9h" in python_group["formatted_duration"]

    # 3. Check explainability (inspect original subjects)
    member_names = [m["name"] for m in python_group["topics"]]
    assert "Python" in member_names
    assert "Python Programming" in member_names
    assert "Python Projects" in member_names
    assert len(python_group["topics"]) == 3
    assert dist == original_dist

def test_subject_grouping_conservative_rule_fallback_when_llm_fails():
    dist = {
        "Python Basics": 3600,
        "Python Advanced": 7200,
        "History 101": 1800,
        "European History": 5400
    }

    mock_router = MagicMock()
    mock_router.generate_text.side_effect = RuntimeError("Provider offline")

    service = SubjectGroupingService(provider_router=mock_router)
    result = service.group_topics(dist)

    # Deterministic sum check
    assert sum(g["total_seconds"] for g in result["groups"]) == sum(dist.values())

    # Check that Python topics grouped together under Python rule
    python_group = next((g for g in result["groups"] if "Python" in g["label"]), None)
    assert python_group is not None
    assert python_group["total_seconds"] == 10800

def test_subject_grouping_does_not_merge_unrelated_ambiguous_topics():
    dist = {
        "Java": 3600,
        "JavaScript": 5400
    }

    mock_router = MagicMock()
    mock_router.generate_text.return_value = "ERROR: connection failed"

    service = SubjectGroupingService(provider_router=mock_router)
    result = service.group_topics(dist)

    # Conservative rule must keep Java and JavaScript separate
    labels = [g["label"] for g in result["groups"]]
    assert "Java" in labels
    assert "JavaScript" in labels
    assert len(result["groups"]) == 2

def test_invalid_llm_grouping_cannot_duplicate_or_drop_topic_totals():
    distribution = {"Python": 3600, "Physics": 7200}
    mock_router = MagicMock()
    mock_router.generate_text.return_value = (
        '{"groups": [{"label": "Python", "topics": ["Python", "Physics"]}, '
        '{"label": "Physics", "topics": ["Physics"]}]}'
    )

    result = SubjectGroupingService(provider_router=mock_router).group_topics(distribution)

    assert result["total_seconds"] == sum(distribution.values())
    assert sum(group["total_seconds"] for group in result["groups"]) == sum(distribution.values())


def test_duplicate_llm_group_labels_fall_back_without_dropping_topic_totals():
    distribution = {
        "Python": 3600,
        "Python Basics": 7200,
        "Calculus": 1800,
    }
    mock_router = MagicMock()
    mock_router.generate_text.return_value = (
        '{"groups": [{"label": "Programming", "topics": ["Python"]}, '
        '{"label": "Programming", "topics": ["Python Basics", "Calculus"]}]}'
    )

    result = SubjectGroupingService(provider_router=mock_router).group_topics(distribution)

    assert result["total_seconds"] == sum(distribution.values())
    assert sum(group["total_seconds"] for group in result["groups"]) == sum(distribution.values())
    assert sum(
        len(group["topics"]) for group in result["groups"]
    ) == len(distribution)


def test_conservative_grouping_matches_topic_stems_case_insensitively():
    distribution = {
        "Biology Basics": 3600,
        "biology advanced": 7200,
        "History": 1800,
    }
    mock_router = MagicMock()
    mock_router.generate_text.return_value = "ERROR: provider unavailable"

    result = SubjectGroupingService(provider_router=mock_router).group_topics(distribution)

    biology_group = next(
        group for group in result["groups"] if len(group["topics"]) == 2
    )
    assert biology_group["total_seconds"] == 10800
    assert result["total_seconds"] == sum(distribution.values())


def test_subject_grouping_empty_and_single_topic():
    service = SubjectGroupingService()

    # Empty
    empty_res = service.group_topics({})
    assert empty_res["total_seconds"] == 0
    assert empty_res["groups"] == []

    # Single topic
    single_res = service.group_topics({"Biology": 3600})
    assert single_res["total_seconds"] == 3600
    assert len(single_res["groups"]) == 1
    assert single_res["groups"][0]["label"] == "Biology"
    assert single_res["groups"][0]["percentage"] == 100.0
