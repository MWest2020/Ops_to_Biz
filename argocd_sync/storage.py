#!/usr/bin/env python3
"""Fetch Nextcloud PVC usage per namespace via kubectl.

Strategy mirrors `mcc check-storage`:
- For non-NFS PVCs (CSI / Gardener pv-shoot-*): kubelet /stats/summary per node.
- For NFS-backed PVCs (storageClass nfs / nfs-v4): `du -sh pvc-*` inside the
  nfs-server-provisioner-0 pod in the default namespace.

Returns one used-bytes total per namespace, summing all PVCs whose name
contains 'nextcloud' and excludes sidecar datastores.
"""

import json
import os
import subprocess
import sys

NFS_POD = "nfs-server-provisioner-0"
NFS_NAMESPACE = "default"
NFS_STORAGE_CLASSES = ("nfs", "nfs-v4")

_NC_PVC_EXCLUDE = (
    "mariadb", "redis", "postgres", "postgresql", "pgbouncer",
    "imaginary", "collabora", "onlyoffice", "elasticsearch",
)


def _kubectl(args, timeout=30):
    result = subprocess.run(
        ["kubectl", *args],
        capture_output=True, text=True, timeout=timeout,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def _format_bytes(n):
    if n >= 1024**4:
        return f"{n / 1024**4:.1f}T"
    if n >= 1024**3:
        return f"{n / 1024**3:.1f}G"
    if n >= 1024**2:
        return f"{n / 1024**2:.1f}M"
    if n > 0:
        return f"{n / 1024:.0f}K"
    return "0"


def _parse_size_to_bytes(size_str):
    """Parse `du -sh` style strings ('4.2G', '512M', '12K', '1.5T')."""
    s = size_str.strip()
    if not s:
        return 0
    mult = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    suf = s[-1].upper()
    if suf in mult:
        try:
            return int(float(s[:-1]) * mult[suf])
        except ValueError:
            return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def _is_nextcloud_pvc(name):
    n = name.lower()
    if "nextcloud" not in n:
        return False
    return not any(x in n for x in _NC_PVC_EXCLUDE)


def _all_pvcs():
    raw = _kubectl(["get", "pvc", "--all-namespaces", "-o", "json"], timeout=60)
    if not raw:
        return []
    try:
        return json.loads(raw).get("items", [])
    except json.JSONDecodeError:
        return []


def _kubelet_stats():
    """Return {(namespace, pvc_name): used_bytes} from kubelet /stats/summary.

    Only valid for non-NFS PVCs; for NFS-backed claims kubelet reports the
    full filesystem size, not per-PVC usage.
    """
    raw = _kubectl(
        ["get", "nodes", "-o", "jsonpath={.items[*].metadata.name}"], timeout=10
    )
    if not raw:
        return {}
    nodes = raw.strip().split()
    stats = {}
    for node in nodes:
        node_raw = _kubectl(
            ["get", "--raw", f"/api/v1/nodes/{node}/proxy/stats/summary"],
            timeout=30,
        )
        if not node_raw:
            continue
        try:
            data = json.loads(node_raw)
        except json.JSONDecodeError:
            continue
        for pod in data.get("pods", []):
            for vol in pod.get("volume", []):
                ref = vol.get("pvcRef")
                if not ref:
                    continue
                key = (ref.get("namespace", ""), ref.get("name", ""))
                stats[key] = vol.get("usedBytes", 0)
    return stats


def _nfs_usage():
    """Return {volume_name: used_bytes} via `du -sh pvc-*` inside NFS pod."""
    raw = _kubectl(
        [
            "exec", NFS_POD, "-n", NFS_NAMESPACE, "--",
            "sh", "-c",
            "cd /export 2>/dev/null || cd /data 2>/dev/null || cd /; "
            "du -sh pvc-* 2>/dev/null || true",
        ],
        timeout=600,
    )
    usage = {}
    if not raw:
        return usage
    for line in raw.strip().split("\n"):
        parts = line.split(None, 1)
        if len(parts) == 2:
            size_str, dirname = parts
            usage[dirname.strip().rstrip("/")] = _parse_size_to_bytes(size_str)
    return usage


def nextcloud_used_per_namespace():
    """Return {namespace: 'used_string'} for namespaces with a Nextcloud PVC.

    Sums all Nextcloud PVCs in the namespace (excluding sidecars). NFS-backed
    claims use NFS-pod `du`; CSI-backed claims use kubelet stats.
    """
    pvcs = _all_pvcs()
    if not pvcs:
        print("[storage] ERROR: kubectl returned no PVCs (auth/cluster issue?)",
              file=sys.stderr)
        return None

    print(f"[storage] Found {len(pvcs)} PVCs; fetching usage data...",
          file=sys.stderr)
    print("[storage] Querying kubelet stats per node...", file=sys.stderr)
    kubelet = _kubelet_stats()
    print(f"[storage] Got kubelet stats for {len(kubelet)} mounted volume(s)",
          file=sys.stderr)
    print("[storage] Querying NFS pod for du -sh (this can take a few minutes)...",
          file=sys.stderr)
    nfs = _nfs_usage()
    print(f"[storage] Got NFS sizes for {len(nfs)} pvc-* directories",
          file=sys.stderr)

    by_ns = {}
    nc_count = 0
    for pvc in pvcs:
        meta = pvc.get("metadata", {})
        name = meta.get("name", "")
        if not _is_nextcloud_pvc(name):
            continue
        nc_count += 1
        ns = meta.get("namespace", "")
        spec = pvc.get("spec", {})
        vol = spec.get("volumeName", "")
        sc = spec.get("storageClassName", "")
        is_nfs = sc in NFS_STORAGE_CLASSES

        if is_nfs:
            used = nfs.get(vol, 0)
        else:
            used = kubelet.get((ns, name), 0)
        by_ns[ns] = by_ns.get(ns, 0) + used

    print(f"[storage] Aggregated {nc_count} Nextcloud PVC(s) over "
          f"{len(by_ns)} namespace(s)", file=sys.stderr)
    return {ns: _format_bytes(b) for ns, b in by_ns.items() if b > 0}


def main():
    result = nextcloud_used_per_namespace()
    if result is None:
        sys.exit(1)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
