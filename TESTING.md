# ROAMFIT Testing Guide

This document provides instructions for running the ROAMFIT test suite.

## Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

Test dependencies are included in `requirements.txt`:
- `pytest>=7.4.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-mock>=3.11.0` - Mocking utilities
- `ruff>=0.1.0` - Linting
- `mypy>=1.7.0` - Type checking
- `pre-commit>=3.5.0` - Pre-commit hooks

## Pre-commit Hooks

Pre-commit hooks automatically run linting before each commit.

### Setup
```bash
pre-commit install
```

### Manual Run
```bash
# Run all hooks (linting + tests)
pre-commit run --all-files

# Run only linting
pre-commit run ruff --all-files

# Run only tests (manual stage)
pre-commit run pytest --all-files
```

Hooks configured:
- **ruff** - Code linting and formatting (runs on every commit)
- **mypy** - Type checking (runs on every commit)
- **pytest** - Run test suite (manual only - run before pushing)

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_database.py
pytest tests/test_llm.py
pytest tests/test_orchestrator.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_database.py::test_save_workout
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_llm.py          # LLM utility tests (mocked OpenAI)
├── test_database.py     # Database CRUD tests (temporary SQLite)
└── test_orchestrator.py # Orchestrator workflow tests (mocked MCP)
```

## Test Categories

### 1. LLM Utilities (`test_llm.py`)
- Tests `call_llm()` with mocked OpenAI API
- Tests `call_vision()` with mocked OpenAI Vision API
- Tests error handling and logging
- **No real API calls** - all mocked

### 2. Database Operations (`test_database.py`)
- Tests CRUD operations using temporary SQLite database
- Tests `save_workout()`, `get_workout_history()`, `update_workout()`, `delete_workout()`
- Tests `save_equipment_detection()`, `save_llm_log()`
- **Uses temporary database** - no impact on production data

### 3. Orchestrator Workflow (`test_orchestrator.py`)
- Tests orchestrator decision logic
- Tests agent coordination (mocked MCP clients)
- Tests error handling in workflows
- **Mocks all MCP clients** - no real agent calls

## Writing New Tests

### Example: Testing a Function
```python
def test_my_function():
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result["status"] == "success"
```

### Example: Testing with Mocks
```python
def test_llm_call(mocker):
    # Mock OpenAI API
    mock_response = mocker.Mock()
    mock_response.choices[0].message.content = "Test response"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    
    mocker.patch("openai.OpenAI.chat.completions.create", return_value=mock_response)
    
    # Test
    result = call_llm("test prompt")
    assert result == "Test response"
```

### Example: Testing Database Operations
```python
def test_save_workout(temp_db):
    # temp_db is a fixture that provides a temporary database
    workout_id = save_workout(
        equipment=["dumbbells"],
        workout_plan={"format": "AMRAP"},
        location="Test Gym"
    )
    assert workout_id > 0
```

## Continuous Integration

Tests run automatically on GitHub Actions for:
- Every push to any branch
- Every pull request
- Linting with ruff
- All test suites

See `.github/workflows/ci.yml` for CI configuration.

## Troubleshooting

### Tests Fail with Import Errors
- Ensure you're in the project root directory
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Database Tests Fail
- Tests use temporary databases - no cleanup needed
- If issues persist, check file permissions in `tests/` directory

### Mock Tests Fail
- Ensure `pytest-mock` is installed
- Check that mocks are properly configured
- Verify OpenAI API is not actually being called (check logs)

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Fixtures**: Share setup code via `conftest.py`
3. **Mock External Services**: Never call real APIs in tests
4. **Test Edge Cases**: Include error conditions and boundary cases
5. **Keep Tests Fast**: Use mocks and temporary databases
6. **Clear Assertions**: Use descriptive assert messages

