"""Tests for the Catalog API client."""

import pytest
import requests_mock
from vmware_vra_cli.api.catalog import CatalogClient, CatalogItem, WorkflowRun


class TestCatalogClient:
    """Test cases for CatalogClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test catalog client."""
        return CatalogClient(
            base_url="https://vra.example.com",
            token="test-token",
            verify_ssl=True
        )
    
    def test_init(self):
        """Test client initialization."""
        client = CatalogClient(
            base_url="https://vra.example.com",
            token="test-token",
            verify_ssl=False
        )
        
        assert client.base_url == "https://vra.example.com"
        assert client.session.verify is False
        assert client.session.headers['Authorization'] == "Bearer test-token"
    
    def test_list_catalog_items(self, requests_mock, client):
        """Test listing catalog items."""
        mock_data = {
            "content": [
                {
                    "id": "item-1",
                    "name": "Test Item 1",
                    "type": "Cloud.vSphere.Machine",
                    "status": "RELEASED"
                },
                {
                    "id": "item-2", 
                    "name": "Test Item 2",
                    "type": "Cloud.AWS.EC2.Instance",
                    "status": "RELEASED"
                }
            ]
        }
        
        requests_mock.get(
            "https://vra.example.com/catalog/api/items",
            json=mock_data
        )
        
        items = client.list_catalog_items()
        
        assert len(items) == 2
        assert items[0].id == "item-1"
        assert items[0].name == "Test Item 1"
        assert items[1].id == "item-2"
        assert items[1].name == "Test Item 2"
    
    def test_list_catalog_items_with_project(self, requests_mock, client):
        """Test listing catalog items filtered by project."""
        requests_mock.get(
            "https://vra.example.com/catalog/api/items",
            json={"content": []}
        )
        
        client.list_catalog_items(project_id="project-123")
        
        assert requests_mock.last_request.qs == {'projectid': ['project-123']}
    
    def test_get_catalog_item(self, requests_mock, client):
        """Test getting a specific catalog item."""
        mock_data = {
            "id": "item-1",
            "name": "Test Item",
            "description": "A test catalog item",
            "type": "Cloud.vSphere.Machine",
            "status": "RELEASED",
            "version": "1.0"
        }
        
        requests_mock.get(
            "https://vra.example.com/catalog/api/items/item-1",
            json=mock_data
        )
        
        item = client.get_catalog_item("item-1")
        
        assert isinstance(item, CatalogItem)
        assert item.id == "item-1"
        assert item.name == "Test Item"
        assert item.description == "A test catalog item"
        assert item.version == "1.0"
    
    def test_get_catalog_item_schema(self, requests_mock, client):
        """Test getting catalog item schema."""
        mock_schema = {
            "type": "object",
            "properties": {
                "cpu": {"type": "integer", "default": 1},
                "memory": {"type": "integer", "default": 1024}
            }
        }
        
        requests_mock.get(
            "https://vra.example.com/catalog/api/items/item-1/schema",
            json=mock_schema
        )
        
        schema = client.get_catalog_item_schema("item-1")
        
        assert schema["type"] == "object"
        assert "cpu" in schema["properties"]
        assert "memory" in schema["properties"]
    
    def test_request_catalog_item(self, requests_mock, client):
        """Test requesting a catalog item."""
        mock_response = {
            "deploymentId": "deployment-123",
            "requestId": "request-456"
        }
        
        requests_mock.post(
            "https://vra.example.com/catalog/api/items/item-1/request",
            json=mock_response
        )
        
        result = client.request_catalog_item(
            "item-1",
            {"cpu": 2, "memory": 2048},
            "project-123",
            "Testing catalog request"
        )
        
        assert result["deploymentId"] == "deployment-123"
        assert result["requestId"] == "request-456"
        
        # Verify request payload
        request_json = requests_mock.last_request.json()
        assert request_json["projectId"] == "project-123"
        assert request_json["reason"] == "Testing catalog request"
        assert request_json["inputs"]["cpu"] == 2
        assert request_json["inputs"]["memory"] == 2048
    
    def test_list_deployments(self, requests_mock, client):
        """Test listing deployments."""
        mock_data = {
            "content": [
                {
                    "id": "deployment-1",
                    "name": "Test Deployment",
                    "status": "CREATE_SUCCESSFUL",
                    "projectId": "project-123",
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
        
        requests_mock.get(
            "https://vra.example.com/deployment/api/deployments",
            json=mock_data
        )
        
        deployments = client.list_deployments()
        
        assert len(deployments) == 1
        assert deployments[0]["id"] == "deployment-1"
        assert deployments[0]["status"] == "CREATE_SUCCESSFUL"
    
    def test_run_workflow(self, requests_mock, client):
        """Test running a workflow."""
        mock_response = {
            "id": "execution-123",
            "name": "Test Workflow Execution",
            "state": "running",
            "start-date": "2024-01-01T00:00:00Z"
        }
        
        requests_mock.post(
            "https://vra.example.com/vco/api/workflows/workflow-123/executions",
            json=mock_response
        )
        
        workflow_run = client.run_workflow(
            "workflow-123",
            {"param1": "value1", "param2": "value2"}
        )
        
        assert isinstance(workflow_run, WorkflowRun)
        assert workflow_run.id == "execution-123"
        assert workflow_run.state == "running"
        assert workflow_run.input_parameters["param1"] == "value1"
        
        # Verify request payload structure
        request_json = requests_mock.last_request.json()
        assert "parameters" in request_json
        assert len(request_json["parameters"]) == 2
    
    def test_cancel_workflow_run(self, requests_mock, client):
        """Test canceling a workflow run."""
        requests_mock.put(
            "https://vra.example.com/vco/api/workflows/workflow-123/executions/execution-456/state",
            status_code=200
        )
        
        result = client.cancel_workflow_run("workflow-123", "execution-456")
        
        assert result is True
        
        # Verify request payload
        request_json = requests_mock.last_request.json()
        assert request_json["value"] == "canceled"


class TestModels:
    """Test cases for data models."""
    
    def test_catalog_item_model(self):
        """Test CatalogItem model."""
        item_data = {
            "id": "item-1",
            "name": "Test Item",
            "description": "A test item",
            "type": "Cloud.vSphere.Machine",
            "status": "RELEASED",
            "version": "1.0"
        }
        
        item = CatalogItem(**item_data)
        
        assert item.id == "item-1"
        assert item.name == "Test Item"
        assert item.description == "A test item"
        assert item.type == "Cloud.vSphere.Machine"
        assert item.status == "RELEASED"
        assert item.version == "1.0"
    
    def test_catalog_item_optional_fields(self):
        """Test CatalogItem model with optional fields."""
        item_data = {
            "id": "item-1",
            "name": "Test Item",
            "type": "Cloud.vSphere.Machine", 
            "status": "RELEASED"
        }
        
        item = CatalogItem(**item_data)
        
        assert item.id == "item-1"
        assert item.name == "Test Item"
        assert item.description is None
        assert item.version is None
    
    def test_workflow_run_model(self):
        """Test WorkflowRun model."""
        run_data = {
            "id": "execution-1",
            "name": "Test Execution",
            "state": "completed",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-01T01:00:00Z",
            "input_parameters": {"param1": "value1"},
            "output_parameters": {"result": "success"}
        }
        
        run = WorkflowRun(**run_data)
        
        assert run.id == "execution-1"
        assert run.name == "Test Execution"
        assert run.state == "completed"
        assert run.start_date == "2024-01-01T00:00:00Z"
        assert run.end_date == "2024-01-01T01:00:00Z"
        assert run.input_parameters["param1"] == "value1"
        assert run.output_parameters["result"] == "success"
