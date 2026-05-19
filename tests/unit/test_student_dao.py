"""Unit tests for Student DAO.

To run these tests:
    poetry install  # Install dependencies including pytest-asyncio
    poetry run pytest tests/unit/test_student_dao.py -v

Or run all tests:
    poetry run pytest tests/ -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, call


@pytest.mark.asyncio
async def test_student_create_uses_parameterized_query():
    """Test that Student.create uses parameterized queries to prevent SQL injection."""
    # Import here to avoid dependency issues in test discovery
    from cdk.containers.dvpwa.sqli.dao.student import Student

    # Create mock connection and cursor
    mock_cursor = AsyncMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__aexit__.return_value = AsyncMock()

    # Test with a normal name
    test_name = "John Doe"
    await Student.create(mock_conn, test_name)

    # Verify execute was called with parameterized query
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args

    # Check that the query uses %s placeholder
    query = call_args[0][0]
    assert "VALUES (%s)" in query
    assert "INSERT INTO students (name)" in query

    # Check that parameters are passed separately
    params = call_args[0][1]
    assert params == (test_name,)

    # Verify the name is NOT in the query string itself
    assert test_name not in query


@pytest.mark.asyncio
async def test_student_create_prevents_sql_injection():
    """Test that Student.create is safe against SQL injection attempts."""
    from cdk.containers.dvpwa.sqli.dao.student import Student

    # Create mock connection and cursor
    mock_cursor = AsyncMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__aexit__.return_value = AsyncMock()

    # Test with a malicious SQL injection attempt
    malicious_name = "'); DROP TABLE students; --"
    await Student.create(mock_conn, malicious_name)

    # Verify execute was called with parameterized query
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args

    # Check that the query structure is unchanged
    query = call_args[0][0]
    assert query == "INSERT INTO students (name) VALUES (%s)"

    # Check that the malicious input is passed as a parameter (safely)
    params = call_args[0][1]
    assert params == (malicious_name,)

    # Verify the malicious string is NOT in the query itself
    assert "DROP TABLE" not in query
    assert malicious_name not in query


@pytest.mark.asyncio
async def test_student_create_with_special_characters():
    """Test that Student.create handles special characters correctly."""
    from cdk.containers.dvpwa.sqli.dao.student import Student

    # Create mock connection and cursor
    mock_cursor = AsyncMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__aexit__.return_value = AsyncMock()

    # Test with special characters that could cause issues
    special_name = "O'Brien"
    await Student.create(mock_conn, special_name)

    # Verify execute was called correctly
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args

    # Check that parameters are passed separately
    params = call_args[0][1]
    assert params == (special_name,)

    # The query should still use the placeholder
    query = call_args[0][0]
    assert "VALUES (%s)" in query
