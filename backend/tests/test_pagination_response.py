import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from unittest.mock import Mock

from app.core.pagination import PaginationParams, PaginatedResponse
from app.core.response import envelope, paginated_envelope

def test_pagination_params():
    params = PaginationParams(page=1, limit=20)
    assert params.page == 1
    assert params.limit == 20
    assert params.offset == 0

def test_pagination_params_page2():
    params = PaginationParams(page=2, limit=20)
    assert params.offset == 20

def test_paginated_response():
    resp = PaginatedResponse[int](items=[1,2,3], total=100, page=1, limit=20, pages=5)
    assert resp.items == [1,2,3]
    assert resp.total == 100
    assert resp.pages == 5

def test_envelope():
    request = Mock(spec=Request)
    request.state = Mock()
    request.state.request_id = "req-123"
    request.headers.get.return_value = "req-123"
    
    resp = envelope(success=True, data={"id": 1}, message="OK", request=request)
    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 200

def test_envelope_with_code():
    request = Mock(spec=Request)
    request.state = Mock()
    request.state.request_id = "req-123"
    request.headers.get.return_value = "req-123"
    
    resp = envelope(success=False, data=None, message="Not Found", request=request, code="NOT_FOUND", details={"field": "id"}, status_code=404)
    assert resp.status_code == 404

def test_paginated_envelope():
    request = Mock(spec=Request)
    request.state = Mock()
    request.state.request_id = "req-123"
    
    result = paginated_envelope(items=[1,2,3], total=25, page=1, limit=10, request=request)
    assert result["success"] is True
    assert result["data"]["items"] == [1,2,3]
    assert result["data"]["total"] == 25
    assert result["data"]["page"] == 1
    assert result["data"]["limit"] == 10
    assert result["data"]["pages"] == 3
    assert result["message"] == "OK"
    assert "request_id" in result