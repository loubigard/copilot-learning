# Tests for Mergington High School Activities API

This directory contains comprehensive tests for the FastAPI application.

## Test Structure

- `test_activities.py` - Tests for the GET /activities endpoint
- `test_signup.py` - Tests for the POST /activities/{activity_name}/signup endpoint  
- `test_unregister.py` - Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint
- `test_main.py` - Tests for main application endpoints (root redirect, documentation, error handling)
- `test_integration.py` - Integration tests covering complete user workflows
- `conftest.py` - Test configuration and shared fixtures

## Running Tests

### Run all tests:
```bash
python -m pytest tests/ -v
```

### Run tests with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing -v
```

### Run specific test file:
```bash
python -m pytest tests/test_activities.py -v
```

### Run specific test:
```bash
python -m pytest tests/test_activities.py::TestActivitiesEndpoints::test_get_activities_success -v
```

## Test Coverage

The test suite achieves **100% code coverage** of the FastAPI application, testing:

- ✅ All API endpoints (GET, POST, DELETE)
- ✅ Success and error scenarios  
- ✅ URL encoding and special characters
- ✅ Data validation and constraints
- ✅ Complete user workflows
- ✅ Application configuration and documentation
- ✅ Error handling and edge cases

## Test Features

- **Fixtures**: `reset_activities` fixture ensures clean state between tests
- **Comprehensive Coverage**: Tests cover happy path, error cases, and edge cases
- **Integration Tests**: End-to-end workflows testing complete user journeys
- **URL Encoding**: Tests handle special characters and URL encoding properly
- **Error Scenarios**: Tests validate proper HTTP status codes and error messages