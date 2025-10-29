"""System-wide metrics collection for estimated load calculation."""

from typing import Tuple, List, Dict, Any
import json
import subprocess
import pyone


def run_command(cmd: list[str]) -> dict:
    """Execute OpenNebula CLI command and parse JSON output."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def get_oneflow_services() -> List[Dict[str, Any]]:
    """Get all OneFlow services using CLI (pyone doesn't support services)."""
    try:
        return run_command(["oneflow", "list", "--json"])
    except Exception as e:
        print(f"Error fetching OneFlow services: {e}")
        return []


def get_vm_details(vm_id: str) -> Dict[str, Any]:
    """Get VM details using CLI."""
    try:
        return run_command(["onevm", "show", vm_id, "--json"])
    except Exception as e:
        print(f"Error fetching VM {vm_id}: {e}")
        return {}


def extract_queue_total_from_frontend(service: Dict) -> int:
    """Extract QUEUE_TOTAL from frontend VM of a service.

    Returns:
        - Queue total (int) if service has Frontend role
        - -1 if service has no Frontend role
        - 0 if Frontend role exists but no queue/monitoring data
    """
    try:
        body = service.get("TEMPLATE", {}).get("BODY", {})
        roles = body.get("roles", [])

        frontend_role = next((r for r in roles if r.get("name") == "Frontend"), None)
        if not frontend_role:
            return -1  # No Frontend role

        nodes = frontend_role.get("nodes", [])
        if not nodes:
            return 0  # Frontend role exists but no nodes

        vm_id = str(nodes[0].get("deploy_id"))
        if not vm_id:
            return 0  # Frontend role exists but no VM

        vm_data = get_vm_details(vm_id)
        vm = vm_data.get("VM", {})
        monitoring = vm.get("MONITORING", {})

        queue_total_str = monitoring.get("QUEUE_TOTAL")
        return int(queue_total_str) if queue_total_str else 0

    except Exception as e:
        print(f"Error extracting queue total from service {service.get('ID')}: {e}")
        return 0


def collect_system_metrics() -> Tuple[int, float, int]:
    """
    Collect system-wide metrics for estimated load calculation.
    Only considers services that have Frontend roles (COGNIT services).

    Returns:
        Tuple of (total_backlog, total_cpu_usage, frontend_service_count)
    """
    all_services = get_oneflow_services()

    # Filter to only services with Frontend roles
    frontend_services = []
    for service in all_services:
        if has_frontend_role(service):
            frontend_services.append(service)

    total_backlog = 0
    frontend_service_count = len(frontend_services)

    # Collect queue totals from all services with Frontend roles
    for service in frontend_services:
        backlog = extract_queue_total_from_frontend(service)
        total_backlog += backlog  # Will be >= 0 since we already filtered

    # For now, return CPU as 0 since we don't have the full one-aiops integration yet
    total_cpu = 0.0

    return total_backlog, total_cpu, frontend_service_count


def has_frontend_role(service: Dict) -> bool:
    """Check if a service has a Frontend role."""
    try:
        body = service.get("TEMPLATE", {}).get("BODY", {})
        roles = body.get("roles", [])
        return any(role.get("name") == "Frontend" for role in roles)
    except Exception:
        return False
