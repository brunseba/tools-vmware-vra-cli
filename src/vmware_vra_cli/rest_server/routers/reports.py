"""Reports endpoints for MCP server."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from vmware_vra_cli.rest_server.models import (
    ActivityTimelineRequest,
    ActivityTimelineResponse,
    CatalogUsageRequest,
    CatalogUsageResponse,
    UnsyncReportRequest,
    UnsyncReportResponse,
    ResourcesUsageResponse,
    DependenciesReportResponse,
    BaseResponse,
)
from vmware_vra_cli.rest_server.utils import get_catalog_client, handle_client_error
from vmware_vra_cli.rest_server.cache import cache_response, get_cache_stats, invalidate_cache

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/cache/stats")
async def get_cache_statistics():
    """Get Redis cache statistics for monitoring performance."""
    return get_cache_stats()


@router.post("/cache/invalidate")
async def invalidate_report_cache(pattern: str = "reports:*"):
    """Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Redis key pattern (default: 'reports:*' clears all report caches)
    """
    deleted = invalidate_cache(pattern)
    return {
        "success": True,
        "message": f"Invalidated {deleted} cache entries",
        "pattern": pattern,
        "deleted_count": deleted
    }


@router.get("/activity-timeline", response_model=ActivityTimelineResponse)
async def get_activity_timeline_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    days_back: int = Query(30, ge=1, le=365, description="Days back for activity timeline"),
    group_by: str = Query("day", pattern="^(day|week|month|year)$", description="Group results by time period"),
    statuses: str = Query(
        "CREATE_SUCCESSFUL,UPDATE_SUCCESSFUL,SUCCESSFUL,CREATE_FAILED,UPDATE_FAILED,FAILED,CREATE_INPROGRESS,UPDATE_INPROGRESS,INPROGRESS",
        description="Comma-separated list of statuses to include"
    ),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate an activity timeline for service catalog items.
    
    This timeline provides a historical view of deployment activities over a specified period,
    allowing you to see patterns, peak activity periods, and trends.
    
    Group options:
    - day: Daily activity (default)
    - week: Weekly activity (shows week number and year)
    - month: Monthly activity (shows month and year)
    - year: Yearly activity (shows annual totals)
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        # Convert status string to list
        include_statuses = [status.strip().upper() for status in statuses.split(',')]
        
        timeline_data = client.get_activity_timeline(
            project_id=project_id,
            days_back=days_back,
            include_statuses=include_statuses,
            group_by=group_by
        )
        
        return ActivityTimelineResponse(
            success=True,
            message=f"Activity timeline generated for {days_back} days",
            timeline_data=timeline_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate activity timeline", e)


@router.get("/catalog-usage", response_model=CatalogUsageResponse)
async def get_catalog_usage_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    include_zero: bool = Query(False, description="Include catalog items with zero deployments"),
    sort_by: str = Query("deployments", pattern="^(deployments|resources|name)$", description="Sort results by field"),
    detailed_resources: bool = Query(False, description="Fetch exact resource counts (slower but more accurate)"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate a usage report for service catalog items.
    
    This report shows:
    - All catalog items in the specified project (or all projects)
    - Number of deployments created from each catalog item
    - Total number of resources created from each catalog item
    - Success rate and other deployment statistics
    
    By default, only catalog items with at least one deployment are shown.
    Use include_zero=true to show all catalog items.
    Use detailed_resources=true to fetch exact resource counts (slower).
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        usage_stats = client.get_catalog_usage_stats(
            project_id=project_id,
            fetch_resource_counts=detailed_resources
        )
        
        # Filter out zero deployments unless requested
        if not include_zero:
            usage_stats = [stats for stats in usage_stats if stats['deployment_count'] > 0]
        
        # Sort results
        if sort_by == 'deployments':
            usage_stats.sort(key=lambda x: x['deployment_count'], reverse=True)
        elif sort_by == 'resources':
            usage_stats.sort(key=lambda x: x['resource_count'], reverse=True)
        elif sort_by == 'name':
            usage_stats.sort(key=lambda x: x['catalog_item'].name.lower())
        
        # Get all deployments for summary statistics
        all_deployments = client.list_deployments(project_id=project_id)
        
        # Convert to JSON-serializable format
        catalog_items_data = []
        for stat in usage_stats:
            catalog_items_data.append({
                'id': stat['catalog_item'].id,
                'name': stat['catalog_item'].name,
                'type': stat['catalog_item'].type.name,
                'deployment_count': stat['deployment_count'],
                'resource_count': stat['resource_count'],
                'success_count': stat['success_count'],
                'failed_count': stat['failed_count'],
                'in_progress_count': stat['in_progress_count'],
                'success_rate': stat['success_rate'],
                'status_breakdown': stat['status_counts']
            })
        
        # Calculate summary statistics
        total_catalog_deployments = sum(stat['deployment_count'] for stat in usage_stats)
        total_catalog_resources = sum(stat['resource_count'] for stat in usage_stats)
        active_items = len([s for s in usage_stats if s['deployment_count'] > 0])
        
        summary = {
            'total_catalog_items': len(usage_stats),
            'active_items': active_items,
            'total_deployments_system_wide': len(all_deployments),
            'catalog_linked_deployments': total_catalog_deployments,
            'unlinked_deployments': len(all_deployments) - total_catalog_deployments,
            'total_resources': total_catalog_resources,
            'average_deployments_per_active_item': (
                total_catalog_deployments / active_items if active_items > 0 else 0
            )
        }
        
        return CatalogUsageResponse(
            success=True,
            message=f"Catalog usage report generated for {len(usage_stats)} items",
            usage_stats=catalog_items_data,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate catalog usage report", e)


@router.get("/resources-usage", response_model=ResourcesUsageResponse)
async def get_resources_usage_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    detailed_resources: bool = Query(True, description="Fetch detailed resource information"),
    sort_by: str = Query("catalog-item", pattern="^(deployment-name|catalog-item|resource-count|status)$", description="Sort deployments by field"),
    group_by: str = Query("catalog-item", pattern="^(catalog-item|resource-type|deployment-status)$", description="Group results by field"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate a consolidated resources usage report across all deployments.
    
    This report provides a comprehensive view of all resources existing in each deployment,
    showing resource types, counts, states, and their relationship to catalog items.
    
    The report includes:
    - Total resource counts by type and status
    - Resource breakdown per deployment
    - Catalog item resource utilization
    - Unlinked deployments and their resources
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        report_data = client.get_resources_usage_report(
            project_id=project_id,
            include_detailed_resources=detailed_resources
        )
        
        return ResourcesUsageResponse(
            success=True,
            message=f"Resources usage report generated for {report_data['summary']['total_deployments']} deployments",
            report_data=report_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate resources usage report", e)


@router.get("/unsync", response_model=UnsyncReportResponse)
async def get_unsync_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    detailed_resources: bool = Query(False, description="Fetch exact resource counts (slower but more accurate)"),
    reason_filter: Optional[str] = Query(None, description="Filter by specific reason (e.g., missing_catalog_references, catalog_item_deleted)"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate a report of deployments that don't match to catalog items.
    
    This report identifies "unsynced" deployments that cannot be linked back to any
    catalog item in the system. These deployments may indicate:
    - Deployments created outside the service catalog
    - Catalog items that were deleted after deployment
    - Issues with deployment tracking or naming
    - Failed deployments that lost their catalog associations
    
    The report provides detailed analysis of why each deployment is unsynced
    and suggests potential remediation actions.
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        unsync_data = client.get_unsynced_deployments(
            project_id=project_id,
            fetch_resource_counts=detailed_resources
        )
        
        # Apply reason filter if specified
        if reason_filter:
            filtered_deployments = []
            for unsync in unsync_data['unsynced_deployments']:
                if unsync['analysis']['primary_reason'] == reason_filter:
                    filtered_deployments.append(unsync)
            
            unsync_data['unsynced_deployments'] = filtered_deployments
            # Recalculate summary for filtered data
            unsync_data['summary']['unsynced_deployments'] = len(filtered_deployments)
            unsync_data['summary']['unsynced_percentage'] = (
                len(filtered_deployments) / max(unsync_data['summary']['total_deployments'], 1) * 100
            )
        
        return UnsyncReportResponse(
            success=True,
            message=f"Unsync report generated - found {unsync_data['summary']['unsynced_deployments']} unsynced deployments",
            unsync_data=unsync_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate unsync report", e)


@router.get("/dependencies", response_model=DependenciesReportResponse)
async def get_dependencies_report(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    deployment_id: Optional[str] = Query(None, description="Filter by specific deployment ID"),
    verbose: bool = Query(False, description="Enable verbose HTTP logging")
):
    """Generate a dependencies report showing relationships between resources.
    
    This report analyzes resource dependencies within deployments, showing how
    resources relate to each other (e.g., VMs depend on networks, disks, security groups).
    
    The report includes:
    - Resource dependency graph
    - Types of dependencies (network, storage, security)
    - Dependency chains and potential issues
    - Resources without dependencies (standalone)
    
    This endpoint is cached for 5 minutes to improve performance.
    """
    try:
        client = get_catalog_client(verbose=verbose)
        
        # Get deployments
        if deployment_id:
            deployments = [client.get_deployment(deployment_id)]
        else:
            deployments = client.list_deployments(project_id=project_id)
        
        # Analyze dependencies
        dependencies_data = analyze_resource_dependencies(deployments)
        
        return DependenciesReportResponse(
            success=True,
            message=f"Dependencies report generated for {len(deployments)} deployment(s)",
            dependencies_data=dependencies_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_client_error("generate dependencies report", e)


def extract_dependencies_from_properties(properties, resource_id_map, current_deployment_id=''):
    """Extract detailed dependencies from resource properties.
    
    Args:
        properties: Resource properties dict
        resource_id_map: Map of resource IDs to resource info for cross-referencing
        current_deployment_id: Current resource's deployment ID for cross-deployment detection
    
    Returns:
        List of dependency objects with type, target, and details
    """
    dependencies = []
    
    if not properties or not isinstance(properties, dict):
        return dependencies
    
    # Network dependencies - detailed analysis
    for key in ['networks', 'network', 'networkInterfaces', 'nics']:
        if key in properties:
            network_data = properties[key]
            if isinstance(network_data, list):
                for idx, net in enumerate(network_data):
                    if isinstance(net, dict):
                        dep = {
                            'type': 'network',
                            'description': f"Network interface {idx + 1}",
                            'details': {}
                        }
                        # Extract network details
                        if 'id' in net:
                            dep['target_id'] = net['id']
                            dep['details']['network_id'] = net['id']
                        if 'name' in net:
                            dep['target_name'] = net['name']
                            dep['details']['network_name'] = net['name']
                        if 'address' in net:
                            dep['details']['ip_address'] = net['address']
                        if 'assignment' in net:
                            dep['details']['assignment_type'] = net['assignment']
                        dependencies.append(dep)
            elif isinstance(network_data, dict):
                dep = {'type': 'network', 'description': 'Network connectivity', 'details': {}}
                if 'id' in network_data:
                    dep['target_id'] = network_data['id']
                if 'name' in network_data:
                    dep['target_name'] = network_data['name']
                dependencies.append(dep)
    
    # Storage dependencies - disks and volumes
    for key in ['disks', 'disk', 'storage', 'volumes', 'attachedDisks']:
        if key in properties:
            storage_data = properties[key]
            if isinstance(storage_data, list):
                for idx, disk in enumerate(storage_data):
                    if isinstance(disk, dict):
                        dep = {
                            'type': 'storage',
                            'description': f"Disk {idx + 1}",
                            'details': {}
                        }
                        if 'id' in disk:
                            dep['target_id'] = disk['id']
                            dep['details']['disk_id'] = disk['id']
                        if 'name' in disk:
                            dep['target_name'] = disk['name']
                            dep['details']['disk_name'] = disk['name']
                        if 'capacityInGB' in disk or 'capacity' in disk:
                            dep['details']['capacity'] = disk.get('capacityInGB', disk.get('capacity'))
                        if 'type' in disk:
                            dep['details']['disk_type'] = disk['type']
                        dependencies.append(dep)
            elif isinstance(storage_data, dict):
                dep = {'type': 'storage', 'description': 'Storage', 'details': {}}
                if 'id' in storage_data:
                    dep['target_id'] = storage_data['id']
                dependencies.append(dep)
    
    # Security group dependencies
    for key in ['securityGroups', 'securityGroup', 'security_groups', 'firewallRules']:
        if key in properties:
            sg_data = properties[key]
            if isinstance(sg_data, list):
                for idx, sg in enumerate(sg_data):
                    if isinstance(sg, dict):
                        dep = {
                            'type': 'security',
                            'description': f"Security group {idx + 1}",
                            'details': {}
                        }
                        if 'id' in sg:
                            dep['target_id'] = sg['id']
                            dep['details']['sg_id'] = sg['id']
                        if 'name' in sg:
                            dep['target_name'] = sg['name']
                            dep['details']['sg_name'] = sg['name']
                        dependencies.append(dep)
            elif isinstance(sg_data, dict):
                dep = {'type': 'security', 'description': 'Security group', 'details': {}}
                if 'id' in sg_data:
                    dep['target_id'] = sg_data['id']
                if 'name' in sg_data:
                    dep['target_name'] = sg_data['name']
                dependencies.append(dep)
    
    # Load balancer dependencies
    for key in ['loadBalancers', 'loadBalancer', 'lb']:
        if key in properties:
            lb_data = properties[key]
            if isinstance(lb_data, list):
                for idx, lb in enumerate(lb_data):
                    if isinstance(lb, dict):
                        dep = {
                            'type': 'load_balancer',
                            'description': f"Load balancer {idx + 1}",
                            'details': {}
                        }
                        if 'id' in lb:
                            dep['target_id'] = lb['id']
                        if 'name' in lb:
                            dep['target_name'] = lb['name']
                        dependencies.append(dep)
    
    # Cross-resource dependencies - look for resource IDs in properties
    def find_resource_refs(obj, path='', current_deployment_id=''):
        """Recursively find resource references in properties.
        
        Identifies both same-deployment and cross-deployment references.
        """
        refs = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                current_path = f"{path}.{k}" if path else k
                # Check if this looks like a resource reference
                if k in ['resourceId', 'resource_id', 'dependsOn', 'depends_on', 'sourceResourceId', 
                         'targetId', 'target_id', 'parentId', 'parent_id']:
                    if isinstance(v, str) and v in resource_id_map:
                        target_deployment_id = resource_id_map[v].get('deployment_id', '')
                        is_cross_deployment = (target_deployment_id != current_deployment_id)
                        
                        refs.append({
                            'type': 'cross_deployment' if is_cross_deployment else 'same_deployment',
                            'description': f"{'Cross-deployment' if is_cross_deployment else 'Same-deployment'} reference at {current_path}",
                            'target_id': v,
                            'target_name': resource_id_map[v].get('name', 'Unknown'),
                            'target_type': resource_id_map[v].get('type', 'Unknown'),
                            'target_deployment_id': target_deployment_id,
                            'target_deployment_name': resource_id_map[v].get('deployment_name', 'Unknown'),
                            'details': {
                                'reference_path': current_path,
                                'cross_deployment': is_cross_deployment
                            }
                        })
                    # Also check for resource IDs in value strings (e.g., ARNs, URIs)
                    elif isinstance(v, str):
                        for res_id, res_info in resource_id_map.items():
                            if res_id in v and res_id != v:  # Partial match
                                target_deployment_id = res_info.get('deployment_id', '')
                                is_cross_deployment = (target_deployment_id != current_deployment_id)
                                refs.append({
                                    'type': 'cross_deployment' if is_cross_deployment else 'same_deployment',
                                    'description': f"Resource ID found in {current_path}",
                                    'target_id': res_id,
                                    'target_name': res_info.get('name', 'Unknown'),
                                    'target_type': res_info.get('type', 'Unknown'),
                                    'target_deployment_id': target_deployment_id,
                                    'target_deployment_name': res_info.get('deployment_name', 'Unknown'),
                                    'details': {
                                        'reference_path': current_path,
                                        'reference_value': v[:100],  # Truncate long values
                                        'cross_deployment': is_cross_deployment
                                    }
                                })
                                break  # Only match once per value
                elif isinstance(v, (dict, list)):
                    refs.extend(find_resource_refs(v, current_path, current_deployment_id))
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                refs.extend(find_resource_refs(item, f"{path}[{idx}]", current_deployment_id))
        return refs
    
    cross_refs = find_resource_refs(properties, '', current_deployment_id)
    dependencies.extend(cross_refs)
    
    return dependencies


def find_resource_refs_in_inputs(inputs, current_deployment_id, resource_map):
    """Scan deployment inputs for references to resources in other deployments.
    
    Args:
        inputs: Dictionary of deployment input parameters
        current_deployment_id: Current deployment ID
        resource_map: Global map of all resources
    
    Returns:
        List of dependency references found in inputs
    """
    refs = []
    
    if not inputs or not isinstance(inputs, dict):
        return refs
    
    for input_name, input_value in inputs.items():
        # Skip null/None values
        if input_value is None:
            continue
        
        # Check if input value is a string that might contain resource references
        if isinstance(input_value, str):
            # Direct resource ID match
            if input_value in resource_map:
                target_deployment_id = resource_map[input_value].get('deployment_id', '')
                is_cross_deployment = (target_deployment_id != current_deployment_id)
                
                refs.append({
                    'type': 'cross_deployment' if is_cross_deployment else 'same_deployment',
                    'description': f"Input '{input_name}' references resource",
                    'input_name': input_name,
                    'target_id': input_value,
                    'target_name': resource_map[input_value].get('name', 'Unknown'),
                    'target_type': resource_map[input_value].get('type', 'Unknown'),
                    'target_deployment_id': target_deployment_id,
                    'target_deployment_name': resource_map[input_value].get('deployment_name', 'Unknown'),
                    'details': {
                        'input_name': input_name,
                        'cross_deployment': is_cross_deployment
                    }
                })
            # Partial match - resource ID embedded in string (e.g., ARN, URI)
            else:
                for res_id, res_info in resource_map.items():
                    if len(res_id) > 10 and res_id in input_value:  # Only match substantial IDs
                        target_deployment_id = res_info.get('deployment_id', '')
                        is_cross_deployment = (target_deployment_id != current_deployment_id)
                        
                        refs.append({
                            'type': 'cross_deployment' if is_cross_deployment else 'same_deployment',
                            'description': f"Input '{input_name}' contains resource ID",
                            'input_name': input_name,
                            'target_id': res_id,
                            'target_name': res_info.get('name', 'Unknown'),
                            'target_type': res_info.get('type', 'Unknown'),
                            'target_deployment_id': target_deployment_id,
                            'target_deployment_name': res_info.get('deployment_name', 'Unknown'),
                            'details': {
                                'input_name': input_name,
                                'input_value': input_value[:100],
                                'cross_deployment': is_cross_deployment
                            }
                        })
                        break  # Only match once per input
        
        # Recursively check nested structures
        elif isinstance(input_value, dict):
            # Recursively scan nested dict
            nested_refs = find_resource_refs_in_inputs(input_value, current_deployment_id, resource_map)
            for ref in nested_refs:
                ref['input_name'] = f"{input_name}.{ref.get('input_name', '')}"
                refs.append(ref)
        
        elif isinstance(input_value, list):
            # Scan list items
            for idx, item in enumerate(input_value):
                if isinstance(item, (dict, str)):
                    if isinstance(item, dict):
                        nested_refs = find_resource_refs_in_inputs(item, current_deployment_id, resource_map)
                        for ref in nested_refs:
                            ref['input_name'] = f"{input_name}[{idx}].{ref.get('input_name', '')}"
                            refs.append(ref)
                    elif isinstance(item, str) and item in resource_map:
                        target_deployment_id = resource_map[item].get('deployment_id', '')
                        is_cross_deployment = (target_deployment_id != current_deployment_id)
                        
                        refs.append({
                            'type': 'cross_deployment' if is_cross_deployment else 'same_deployment',
                            'description': f"Input '{input_name}[{idx}]' references resource",
                            'input_name': f"{input_name}[{idx}]",
                            'target_id': item,
                            'target_name': resource_map[item].get('name', 'Unknown'),
                            'target_type': resource_map[item].get('type', 'Unknown'),
                            'target_deployment_id': target_deployment_id,
                            'target_deployment_name': resource_map[item].get('deployment_name', 'Unknown'),
                            'details': {
                                'input_name': f"{input_name}[{idx}]",
                                'cross_deployment': is_cross_deployment
                            }
                        })
    
    return refs


def analyze_resource_dependencies(deployments):
    """Analyze resource dependencies across deployments with deep property inspection.
    
    Focuses on identifying cross-deployment dependencies where resources in one
    deployment depend on resources in another deployment.
    
    Also analyzes deployment inputs to find references to resources from other deployments.
    """
    all_resources = []
    resource_types_count = {}
    deployment_dependencies = []
    global_resource_map = {}  # Global map of all resources across all deployments
    
    # First pass: build global resource map across ALL deployments
    for deployment in deployments:
        if isinstance(deployment, dict):
            deployment_id = deployment.get('id', '')
            deployment_name = deployment.get('name', 'Unknown')
            resources = deployment.get('resources', [])
        else:
            deployment_id = getattr(deployment, 'id', '')
            deployment_name = getattr(deployment, 'name', 'Unknown')
            resources = getattr(deployment, 'resources', [])
        
        for resource in resources:
            if isinstance(resource, dict):
                resource_id = resource.get('id', None)
                resource_name = resource.get('name', 'Unknown')
                resource_type = resource.get('type', 'Unknown')
            else:
                resource_id = getattr(resource, 'id', None)
                resource_name = getattr(resource, 'name', 'Unknown')
                resource_type = getattr(resource, 'type', 'Unknown')
            
            if resource_id:
                global_resource_map[resource_id] = {
                    'id': resource_id,
                    'name': resource_name,
                    'type': resource_type,
                    'deployment_id': deployment_id,
                    'deployment_name': deployment_name
                }
    
    # Second pass: analyze dependencies
    for deployment in deployments:
        deployment_resources = []
        deployment_deps = []
        
        # Handle both dict and object deployments
        if isinstance(deployment, dict):
            deployment_id = deployment.get('id', '')
            deployment_name = deployment.get('name', 'Unknown')
            resources = deployment.get('resources', [])
        else:
            deployment_id = getattr(deployment, 'id', '')
            deployment_name = getattr(deployment, 'name', 'Unknown')
            resources = getattr(deployment, 'resources', [])
        
        # Build temp resources list for this deployment
        temp_resources = []
        for resource in resources:
            if isinstance(resource, dict):
                resource_id = resource.get('id', None)
                resource_name = resource.get('name', 'Unknown')
                resource_type = resource.get('type', 'Unknown')
                properties = resource.get('properties', {})
            else:
                resource_id = getattr(resource, 'id', None)
                resource_name = getattr(resource, 'name', 'Unknown')
                resource_type = getattr(resource, 'type', 'Unknown')
                properties = getattr(resource, 'properties', {})
            
            temp_resources.append({
                'id': resource_id,
                'name': resource_name,
                'type': resource_type,
                'properties': properties,
                'deployment_id': deployment_id
            })
        
        # Analyze dependencies with global cross-deployment context
        for res_data in temp_resources:
            resource_id = res_data['id']
            resource_name = res_data['name']
            resource_type = res_data['type']
            properties = res_data['properties']
            res_deployment_id = res_data['deployment_id']
            
            # Count resource types
            resource_types_count[resource_type] = resource_types_count.get(resource_type, 0) + 1
            
            resource_info = {
                'id': resource_id,
                'name': resource_name,
                'type': resource_type,
                'deployment_id': deployment_id,
                'deployment_name': deployment_name,
            }
            
            # Extract detailed dependencies using global resource map for cross-deployment detection
            resource_dependencies = extract_dependencies_from_properties(properties, global_resource_map, res_deployment_id)
            
            if resource_dependencies:
                resource_info['dependencies'] = resource_dependencies
                deployment_deps.append({
                    'resource_id': resource_id,
                    'resource_name': resource_name,
                    'resource_type': resource_type,
                    'depends_on': resource_dependencies
                })
            
            deployment_resources.append(resource_info)
            all_resources.append(resource_info)
        
        # Also analyze deployment inputs for cross-deployment dependencies
        deployment_input_deps = []
        if isinstance(deployment, dict):
            inputs = deployment.get('inputs', {})
        else:
            inputs = getattr(deployment, 'inputs', {})
        
        if inputs:
            # Scan deployment inputs for resource references
            input_refs = find_resource_refs_in_inputs(inputs, deployment_id, global_resource_map)
            for ref in input_refs:
                deployment_input_deps.append({
                    'source_type': 'deployment_input',
                    'source_name': deployment_name,
                    'input_name': ref.get('input_name'),
                    'depends_on': [ref]
                })
                deployment_deps.append({
                    'resource_id': deployment_id,
                    'resource_name': f"{deployment_name} (input: {ref.get('input_name')})",
                    'resource_type': 'deployment',
                    'depends_on': [ref]
                })
        
        deployment_dependencies.append({
            'deployment_id': deployment_id,
            'deployment_name': deployment_name,
            'resource_count': len(deployment_resources),
            'resources': deployment_resources,
            'dependency_count': len(deployment_deps),
            'dependencies': deployment_deps,
            'input_dependencies': deployment_input_deps
        })
    
    # Calculate summary
    total_resources = len(all_resources)
    resources_with_deps = len([r for r in all_resources if 'dependencies' in r])
    standalone_resources = total_resources - resources_with_deps
    
    # Count dependency types and analyze cross-resource links
    dependency_types_count = {}
    cross_resource_links = []
    
    for dep_info in deployment_dependencies:
        for dep in dep_info['dependencies']:
            for depends_on in dep['depends_on']:
                dep_type = depends_on['type']
                dependency_types_count[dep_type] = dependency_types_count.get(dep_type, 0) + 1
                
                # Track cross-resource dependencies (focus on cross-deployment ones)
                if dep_type in ['cross_deployment', 'same_deployment']:
                    link = {
                        'source_id': dep['resource_id'],
                        'source_name': dep['resource_name'],
                        'source_type': dep['resource_type'],
                        'source_deployment_id': dep_info['deployment_id'],
                        'source_deployment_name': dep_info['deployment_name'],
                        'target_id': depends_on.get('target_id'),
                        'target_name': depends_on.get('target_name'),
                        'target_type': depends_on.get('target_type'),
                        'target_deployment_id': depends_on.get('target_deployment_id'),
                        'target_deployment_name': depends_on.get('target_deployment_name'),
                        'is_cross_deployment': (dep_type == 'cross_deployment')
                    }
                    cross_resource_links.append(link)
    
    # Separate cross-deployment links from same-deployment links
    cross_deployment_links = [link for link in cross_resource_links if link.get('is_cross_deployment', False)]
    same_deployment_links = [link for link in cross_resource_links if not link.get('is_cross_deployment', False)]
    
    # Count deployments with input dependencies
    deployments_with_input_deps = len([d for d in deployment_dependencies if d.get('input_dependencies', [])])
    total_input_deps = sum(len(d.get('input_dependencies', [])) for d in deployment_dependencies)
    
    return {
        'summary': {
            'total_deployments': len(deployments),
            'total_resources': total_resources,
            'resources_with_dependencies': resources_with_deps,
            'standalone_resources': standalone_resources,
            'unique_resource_types': len(resource_types_count),
            'dependency_types': dependency_types_count,
            'resource_types': resource_types_count,
            'cross_resource_links_count': len(cross_resource_links),
            'cross_deployment_links_count': len(cross_deployment_links),
            'same_deployment_links_count': len(same_deployment_links),
            'deployments_with_input_dependencies': deployments_with_input_deps,
            'total_input_dependencies': total_input_deps
        },
        'deployments': deployment_dependencies,
        'all_resources': all_resources,
        'cross_resource_links': cross_resource_links,
        'cross_deployment_links': cross_deployment_links,
        'same_deployment_links': same_deployment_links
    }
