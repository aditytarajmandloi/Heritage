"""
Knowledge Graph Service — Phase 2

Builds and manages a NetworkX directed graph from master_data.json.
Provides traversal methods used by the RAG pipeline (Phase 3) and
a few demo-ready API endpoints.
"""

import json
from pathlib import Path
from typing import Optional

import networkx as nx


class KnowledgeGraphService:
    """Manages the heritage knowledge graph using NetworkX."""

    def __init__(self, data_path: str):
        """Load master_data.json and build the graph."""
        self.data_path = Path(data_path)
        self.raw_data = self._load_data()
        self.graph = self._build_graph()

    # ──────────────────────────── Private ────────────────────────────

    def _load_data(self) -> dict:
        """Read the master_data.json file."""
        data_file = self.data_path / "master_data.json"
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_graph(self) -> nx.DiGraph:
        """Construct the directed graph with all nodes and edges."""
        G = nx.DiGraph()

        # --- Add Landmark nodes ---
        for lm in self.raw_data.get("landmarks", []):
            G.add_node(
                lm["id"],
                node_type="landmark",
                name=lm["name"],
                style=lm["style"],
                era=lm["era"],
                year_built=lm.get("year_built"),
                location=lm.get("location", ""),
                neighborhood=lm.get("neighborhood", ""),
                architect=lm.get("architect", ""),
                image_file=lm.get("image_file", ""),
                images=lm.get("images", []),
                coordinates=lm.get("coordinates", {}),
                short_description=lm.get("short_description", ""),
            )

        # --- Add Style nodes ---
        for style in self.raw_data.get("styles", []):
            G.add_node(
                style["id"],
                node_type="style",
                name=style["name"],
                description=style.get("description", ""),
            )

        # --- Add Era nodes ---
        for era in self.raw_data.get("eras", []):
            G.add_node(
                era["id"],
                node_type="era",
                name=era["name"],
                period=era.get("period", ""),
                description=era.get("description", ""),
            )

        # --- Build lookup maps (name -> id) for linking ---
        style_name_to_id = {s["name"]: s["id"] for s in self.raw_data.get("styles", [])}
        era_name_to_id = {e["name"]: e["id"] for e in self.raw_data.get("eras", [])}

        # --- Add Edges ---
        for lm in self.raw_data.get("landmarks", []):
            lm_id = lm["id"]

            # HAS_STYLE edge: landmark -> style
            style_id = style_name_to_id.get(lm["style"])
            if style_id:
                G.add_edge(lm_id, style_id, relation="HAS_STYLE")

            # BUILT_IN_ERA edge: landmark -> era
            era_id = era_name_to_id.get(lm["era"])
            if era_id:
                G.add_edge(lm_id, era_id, relation="BUILT_IN_ERA")

            # LOCATED_IN edge: landmark -> location (as a simple node)
            if lm.get("location"):
                loc_id = lm["location"].lower().replace(" ", "_")
                if not G.has_node(loc_id):
                    G.add_node(loc_id, node_type="location", name=lm["location"])
                G.add_edge(lm_id, loc_id, relation="LOCATED_IN")

            # NEARBY edges: landmark <-> landmark (bidirectional)
            for nearby_id in lm.get("nearby", []):
                # If the nearby landmark isn't in our dataset, create a stub node
                if not G.has_node(nearby_id):
                    readable_name = nearby_id.replace("_", " ").title()
                    G.add_node(
                        nearby_id,
                        node_type="landmark",
                        name=readable_name,
                        style="",
                        era="",
                        short_description="",
                        image_file="",
                    )
                G.add_edge(lm_id, nearby_id, relation="NEARBY")
                G.add_edge(nearby_id, lm_id, relation="NEARBY")

        return G

    def _get_node_data(self, node_id: str) -> Optional[dict]:
        """Get all attributes of a node, or None if not found."""
        if not self.graph.has_node(node_id):
            return None
        data = dict(self.graph.nodes[node_id])
        data["id"] = node_id
        return data

    def _get_landmarks_list(self) -> list[dict]:
        """Get all landmark nodes as a list of dicts."""
        landmarks = []
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("node_type") == "landmark":
                entry = dict(attrs)
                entry["id"] = node_id
                landmarks.append(entry)
        return landmarks

    # ──────────────────────────── Public API ────────────────────────────

    def get_landmark(self, landmark_id: str) -> Optional[dict]:
        """Get full details of a specific landmark by ID."""
        data = self._get_node_data(landmark_id)
        if data and data.get("node_type") == "landmark":
            return data
        return None

    def get_connections(self, landmark_id: str) -> dict:
        """
        Get all connections for a landmark, grouped by relationship type.
        Returns: { styles: [...], eras: [...], locations: [...], nearby: [...] }
        """
        result = {
            "styles": [],
            "eras": [],
            "locations": [],
            "nearby": [],
        }

        if not self.graph.has_node(landmark_id):
            return result

        # Check outgoing edges from this landmark
        for _, target, edge_data in self.graph.out_edges(landmark_id, data=True):
            relation = edge_data.get("relation", "")
            target_data = self._get_node_data(target)

            if not target_data:
                continue

            if relation == "HAS_STYLE":
                result["styles"].append(target_data)
            elif relation == "BUILT_IN_ERA":
                result["eras"].append(target_data)
            elif relation == "LOCATED_IN":
                result["locations"].append(target_data)
            elif relation == "NEARBY":
                result["nearby"].append(target_data)

        return result

    def find_by_style(self, style_name: str) -> list[dict]:
        """Find all landmarks with a given architectural style name."""
        # Find the style node ID by name
        style_id = None
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("node_type") == "style" and attrs.get("name") == style_name:
                style_id = node_id
                break

        if not style_id:
            return []

        # Find all landmarks that point to this style via HAS_STYLE
        landmarks = []
        for source, _, edge_data in self.graph.in_edges(style_id, data=True):
            if edge_data.get("relation") == "HAS_STYLE":
                lm = self._get_node_data(source)
                if lm:
                    landmarks.append(lm)

        return landmarks

    def find_by_era(self, era_name: str) -> list[dict]:
        """Find all landmarks from a given historical era name."""
        era_id = None
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("node_type") == "era" and attrs.get("name") == era_name:
                era_id = node_id
                break

        if not era_id:
            return []

        landmarks = []
        for source, _, edge_data in self.graph.in_edges(era_id, data=True):
            if edge_data.get("relation") == "BUILT_IN_ERA":
                lm = self._get_node_data(source)
                if lm:
                    landmarks.append(lm)

        return landmarks

    def find_nearby(self, landmark_id: str) -> list[dict]:
        """Find landmarks connected via NEARBY edges."""
        nearby = []
        if not self.graph.has_node(landmark_id):
            return nearby

        for _, target, edge_data in self.graph.out_edges(landmark_id, data=True):
            if edge_data.get("relation") == "NEARBY":
                target_data = self._get_node_data(target)
                if target_data and target_data.get("node_type") == "landmark":
                    nearby.append(target_data)

        return nearby

    def get_related_landmarks(self, landmark_id: str) -> list[dict]:
        """
        2-hop traversal: find landmarks sharing the same style or era.
        landmark -> style/era -> other landmarks
        """
        related = {}

        if not self.graph.has_node(landmark_id):
            return []

        # Get style and era nodes this landmark connects to
        for _, mid_node, edge_data in self.graph.out_edges(landmark_id, data=True):
            relation = edge_data.get("relation", "")
            if relation not in ("HAS_STYLE", "BUILT_IN_ERA"):
                continue

            # Now find other landmarks also connected to this mid_node
            for source, _, in_edge_data in self.graph.in_edges(mid_node, data=True):
                if source == landmark_id:
                    continue  # Skip self
                if in_edge_data.get("relation") == relation:
                    lm = self._get_node_data(source)
                    if lm and lm.get("node_type") == "landmark":
                        # Track why they're related
                        mid_data = self._get_node_data(mid_node)
                        reason = f"shares {relation.replace('_', ' ').lower()}: {mid_data.get('name', mid_node)}"
                        if source not in related:
                            related[source] = {**lm, "related_via": []}
                        related[source]["related_via"].append(reason)

        return list(related.values())

    def get_graph_summary(self) -> dict:
        """Get overall graph statistics for the demo."""
        node_types = {}
        for _, attrs in self.graph.nodes(data=True):
            nt = attrs.get("node_type", "unknown")
            node_types[nt] = node_types.get(nt, 0) + 1

        edge_types = {}
        for _, _, attrs in self.graph.edges(data=True):
            rel = attrs.get("relation", "unknown")
            edge_types[rel] = edge_types.get(rel, 0) + 1

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": node_types,
            "edge_types": edge_types,
        }

    def get_all_landmarks(self) -> list[dict]:
        """Get all landmarks with basic info for the API."""
        return self._get_landmarks_list()

    def find_landmark_by_name(self, name: str) -> Optional[dict]:
        """Find a landmark by partial name match (case-insensitive)."""
        name_lower = name.lower()
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("node_type") == "landmark":
                if name_lower in attrs.get("name", "").lower():
                    data = dict(attrs)
                    data["id"] = node_id
                    return data
        return None
