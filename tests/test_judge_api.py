import pytest
import json
from fastapi.testclient import TestClient
from judge_micro.api.main import get_app

client = TestClient(get_app(debug=True))


class TestJudgeAPI:
    """Judge API tests - Non-submit endpoints"""

    def test_get_examples(self):
        """Test getting examples"""
        # C example
        response = client.get("/judge/examples/c")
        assert response.status_code == 200
        result = response.json()
        assert "example" in result
        assert result["example"]["language"] == "c"
        
        # C++ example
        response = client.get("/judge/examples/cpp")
        assert response.status_code == 200
        result = response.json()
        assert "example" in result
        assert result["example"]["language"] == "cpp"
        
        # Advanced example
        response = client.get("/judge/examples/advanced")
        assert response.status_code == 200
        
        # Error example
        response = client.get("/judge/examples/error")
        assert response.status_code == 200

    def test_get_supported_languages(self):
        """Test getting supported languages"""
        response = client.get("/judge/languages")
        assert response.status_code == 200
        
        result = response.json()
        assert "supported_languages" in result
        languages = [lang["language"] for lang in result["supported_languages"]]
        assert "c" in languages
        assert "cpp" in languages

    def test_get_service_status(self):
        """Test getting service status"""
        response = client.get("/judge/status")
        assert response.status_code == 200
        
        result = response.json()
        assert "service" in result
        assert "status" in result

    def test_get_resource_limits(self):
        """Test getting resource limits"""
        response = client.get("/judge/limits")
        assert response.status_code == 200
        
        result = response.json()
        assert "default_limits" in result
        assert "maximum_limits" in result
        assert "code_limits" in result

    def test_get_optimized_batch_example(self):
        """Test getting optimized batch example"""
        response = client.get("/judge/examples/optimized-batch")
        assert response.status_code == 200
        
        result = response.json()
        assert "description" in result
        assert "example" in result
        assert "note" in result
        
        example = result["example"]
        assert example["language"] in ["c", "cpp"]
        assert "user_code" in example
        assert "configs" in example
        assert len(example["configs"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
