import pytest
import os
from pricing_calculator import PricingCalculator


def test_instance_pricing():
    instance_type = "g5.12xlarge"
    instance_price = PricingCalculator._instance_pricing(instance_type)
    assert isinstance(instance_price, float)
    # Add more assertions to verify the returned instance price

def test_retrieve_cost_structure():
    model_id = "anthropic.claude-v2:1"
    cost_structure = PricingCalculator.retrieve_cost_structure(model_id)
    assert cost_structure is not None
    assert "model_id" in cost_structure
    assert "input_cost_per_1000_tokens" in cost_structure
    assert "output_cost_per_1000_tokens" in cost_structure

    # Test with a model_id that doesn't have a cost structure
    invalid_model_id = "invalid_model_id"
    cost_structure = PricingCalculator.retrieve_cost_structure(invalid_model_id)
    assert cost_structure is None

def retrieve_cost_structure_variants():
    cost_structure = PricingCalculator.retrieve_cost_structure('anthropic.claude-instant-v1:2:100k')
    assert cost_structure is not None
    assert "model_name" in cost_structure
    assert "input_cost_per_1000_tokens" in cost_structure
    assert "output_cost_per_1000_tokens" in cost_structure
    assert cost_structure['input_cost_per_1000_tokens'] == 0.008
    cost_structure = PricingCalculator.retrieve_cost_structure('anthropic.claude-instant-v1:2')
    assert cost_structure is not None
    assert "model_name" in cost_structure
    assert "input_cost_per_1000_tokens" in cost_structure
    assert "output_cost_per_1000_tokens" in cost_structure
    assert cost_structure['input_cost_per_1000_tokens'] == 0.008
    cost_structure = PricingCalculator.retrieve_cost_structure('anthropic.claude-instant-v1')
    assert cost_structure is not None
    assert "model_name" in cost_structure
    assert "input_cost_per_1000_tokens" in cost_structure
    assert "output_cost_per_1000_tokens" in cost_structure
    assert cost_structure['input_cost_per_1000_tokens'] == 0.008
        


def test_read_model_score_aggregate(tmpdir):
    folder = str(tmpdir)
    PricingCalculator.cleanup_previous_runs(folder)
    model_name = "anthropic.claude-v2"
    usage_file = f"{folder}/{model_name}_usage.jsonl"

    # Create a temporary usage file with sample data
    with open(usage_file, "w") as f:
        f.write('{"model_id": "anthropic.claude-v2", "input_tokens": 10, "output_tokens": 20, "processing_time": 1.5}\n')
        f.write('{"model_id": "anthropic.claude-v2", "input_tokens": 15, "output_tokens": 25, "processing_time": 2.0}\n')

    result = PricingCalculator.read_model_score_aggregate(model_name, folder)
    assert result is not None
    assert result["input_tokens"] == 25
    assert result["output_tokens"] == 45
    assert result["processing_time"] == 3.5
    assert result["cost"] > 0

def test_read_model_score_aggregate_from_api(tmpdir):
    folder = str(tmpdir)
    PricingCalculator.cleanup_previous_runs(folder)
    model_name = "amazon.titan-text-lite-v1"
    usage_file = f"{folder}/{model_name}_usage.jsonl"

    # Create a temporary usage file with sample data
    with open(usage_file, "w") as f:
        f.write('{"model_id": "amazon.titan-text-lite-v1", "input_tokens": 10, "output_tokens": 20, "processing_time": 1.5}\n')
        f.write('{"model_id": "amazon.titan-text-lite-v1", "input_tokens": 15, "output_tokens": 25, "processing_time": 2.0}\n')

    result = PricingCalculator.read_model_score_aggregate(model_name, folder)
    assert result is not None
    assert result["input_tokens"] == 25
    assert result["output_tokens"] == 45
    assert result["processing_time"] == 3.5
    assert result["cost"] > 0


def test_read_timed_score_aggregate(tmpdir):
    folder = str(tmpdir)
    PricingCalculator.cleanup_previous_runs(folder)
    model_name = "self_hosted_test"
    usage_file = f"{folder}/{model_name}_usage.jsonl"

    # Create a temporary usage file with sample data
    with open(usage_file, "w") as f:
        f.write('{"model_id": "self_hosted_test", "input_tokens": 10, "output_tokens": 20, "instance_type":"g5.12xlarge", "processing_time": 1.5}\n')
        f.write('{"model_id": "self_hosted_test", "input_tokens": 15, "output_tokens": 25, "instance_type":"g5.12xlarge", "processing_time": 2.0}\n')

    result = PricingCalculator.read_model_score_aggregate(model_name, folder)
    assert result is not None
    assert result["input_tokens"] == 25
    assert result["output_tokens"] == 45
    assert result["processing_time"] == 3.5
    assert result["cost"] > 0

def test_cleanup_previous_runs(tmpdir):
    folder = str(tmpdir)
    open(f"{folder}/test_model_usage.jsonl", "w").close()

    PricingCalculator.cleanup_previous_runs(folder)
    assert not any(fname.endswith("_usage.jsonl") for fname in os.listdir(folder))