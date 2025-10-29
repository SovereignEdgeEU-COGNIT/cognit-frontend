"""System-wide metrics collection for estimated load calculation."""

from typing import Tuple, List, Dict, Any
import json
import math
import subprocess
from datetime import datetime, timedelta
from pyoneai.core import Entity, EntityType, EntityUID, MonitoringConfig
from pyoneai.core import Float, MetricAttributes, MetricType
from pyoneai.core.time import Period
import cognit_conf as conf


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


def collect_system_metrics() -> List[Dict[str, Any]]:
    """
    Collect per-service metrics for estimated load calculation.
    For each OneFlow service with Frontend role, collects:
    - queue_total from the Frontend VM (automatically summed by SDK)
    - average CPU usage across all FaaS VMs (automatically averaged by SDK)

    Returns:
        List of dicts with service metrics:
        [{"service_id": int, "service_name": str, "queue_total": int, "avg_cpu": float}]
    """
    all_services = get_oneflow_services()

    # Filter to only services with Frontend roles
    frontend_services = []
    for service in all_services:
        if has_frontend_role(service):
            frontend_services.append(service)

    service_metrics = []

    if not frontend_services:
        return service_metrics

    try:
        # Build service topology for monitoring
        services_data = []
        for service in frontend_services:
            service_id = service.get("ID")
            service_name = service.get("NAME", f"service_{service_id}")

            # Extract VM IDs for Frontend and FaaS roles
            frontend_vms = []
            faas_vms = []

            try:
                body = service.get("TEMPLATE", {}).get("BODY", {})
                roles = body.get("roles", [])

                for role in roles:
                    role_name = role.get("name")
                    nodes = role.get("nodes", [])

                    for node in nodes:
                        vm_id = node.get("deploy_id")
                        if vm_id:
                            vm_info = {"id": vm_id}
                            if role_name == "Frontend":
                                frontend_vms.append(vm_info)
                            elif role_name == "FaaS":
                                faas_vms.append(vm_info)
            except Exception as e:
                print(f"Warning: Could not extract VM info from service {service_id}: {e}")

            services_data.append({
                "service_id": service_id,
                "service_name": service_name,
                "frontend_vms": frontend_vms,
                "faas_vms": faas_vms,
            })

        # Build service topology and create monitoring config
        service_topology = build_service_topology(services_data)
        monitoring_config = create_service_monitoring_config(service_topology)

        # Collect metrics for each service using SDK service aggregation
        for service_data in services_data:
            service_id = service_data["service_id"]
            service_name = service_data["service_name"]

            # Get metrics using SDK service aggregation
            metrics = get_service_metrics(service_id, service_name, monitoring_config)

            service_metrics.append({
                "service_id": service_id,
                "service_name": service_name,
                "queue_total": metrics["queue_total"],
                "avg_cpu": metrics["avg_cpu"],
            })

    except Exception as e:
        print(f"Error collecting system metrics: {e}")

    return service_metrics


def has_frontend_role(service: Dict) -> bool:
    """Check if a service has a Frontend role."""
    try:
        body = service.get("TEMPLATE", {}).get("BODY", {})
        roles = body.get("roles", [])
        return any(role.get("name") == "Frontend" for role in roles)
    except Exception:
        return False


def build_service_topology(services_data: list[dict]) -> dict:
    """Build service topology mapping for SDK from processed service data.

    Args:
        services_data: List of processed service dictionaries
    Returns:
        Dict mapping service_id -> {role_name: [vm_ids]}
    """
    topology = {}

    for service_data in services_data:
        if not service_data:
            continue

        service_id = service_data.get("service_id")

        if not service_id:
            continue

        roles = {}

        if service_data["frontend_vms"]:
            frontend_ids = [int(vm["id"]) for vm in service_data["frontend_vms"]]
            roles["Frontend"] = frontend_ids

        if service_data["faas_vms"]:
            faas_ids = [int(vm["id"]) for vm in service_data["faas_vms"]]
            roles["FaaS"] = faas_ids

        if roles:
            topology[int(service_id)] = roles  # Ensure service_id is integer

    return topology


def create_service_monitoring_config(service_topology: dict) -> MonitoringConfig:
    """Create monitoring configuration for service aggregation.

    Args:
        service_topology: Service topology mapping
    Returns:
        MonitoringConfig with service_aggregating backend
    """
    vm_monitoring = MonitoringConfig.opennebula_db_mysql(
        **conf.DB_CONFIG,
        metric_xpath_mapping={
            "queue_total": "QUEUE_TOTAL",
            "cpu": "CPU",
        }
    )

    return MonitoringConfig(
        backend="service_aggregating",
        connection={"vm_monitoring_config": vm_monitoring},
        schema={"service_topology": service_topology},
        behavior={"monitor_interval": 60}
    )


def get_service_metrics(
    service_id: int,
    service_name: str,
    monitoring_config: MonitoringConfig,
    lookback_minutes: int = conf.METRICS_LOOKBACK_MINUTES
) -> dict[str, Any]:
    """Fetch metrics for a specific service using SDK service aggregation.

    Args:
        service_id: OneFlow service ID
        service_name: Service name for logging
        monitoring_config: Service monitoring configuration
        lookback_minutes: Time window in minutes
    Returns:
        Dict with queue_total and avg_cpu metrics
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=lookback_minutes)
    period = Period(slice(start_time, end_time, timedelta(minutes=1)))

    results = {"queue_total": 0, "avg_cpu": None}

    try:
        # Get Frontend role metrics (queue_total is automatically summed)
        frontend_role = Entity(
            uid=EntityUID(type=EntityType.SERVICE_ROLE, id=f"{service_id}_Frontend"),
            metrics={
                "queue_total": MetricAttributes(
                    name="queue_total",
                    type=MetricType.GAUGE,
                    dtype=Float(),
                    aggregation_fn="sum"
                )
            },
            monitoring=monitoring_config
        )

        queue_data = frontend_role["queue_total"][period]
        if queue_data is not None and queue_data.values.size > 0:
            queue_sum = queue_data.values.flatten().sum()
            if not math.isnan(queue_sum):
                results["queue_total"] = int(queue_sum)
                print(f"Service {service_id} ({service_name}): queue_total={results['queue_total']}")
            else:
                print(f"Service {service_id} ({service_name}): queue_total=NaN (no data)")

    except Exception as e:
        print(f"Warning: Could not fetch queue_total for service {service_id}: {e}")

    try:
        # Get FaaS role metrics (CPU is automatically averaged)
        faas_role = Entity(
            uid=EntityUID(type=EntityType.SERVICE_ROLE, id=f"{service_id}_FaaS"),
            metrics={
                "cpu": MetricAttributes(
                    name="cpu",
                    type=MetricType.GAUGE,
                    dtype=Float(),
                    aggregation_fn="avg"
                )
            },
            monitoring=monitoring_config
        )

        cpu_data = faas_role["cpu"][period]
        if cpu_data is not None and cpu_data.values.size > 0:
            cpu_avg = cpu_data.values.flatten().mean()
            if not math.isnan(cpu_avg):
                results["avg_cpu"] = float(cpu_avg)
                print(f"Service {service_id} ({service_name}): avg_cpu={results['avg_cpu']:.2f}%")
            else:
                print(f"Service {service_id} ({service_name}): avg_cpu=NaN (no data)")

    except Exception as e:
        print(f"Warning: Could not fetch avg_cpu for service {service_id}: {e}")

    return results
