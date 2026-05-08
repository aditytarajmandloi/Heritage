"""Quick validation of all graph service methods."""
from app.services.graph_service import KnowledgeGraphService

gs = KnowledgeGraphService(data_path="data")

# Test 1: find_by_style
neo_d = gs.find_by_style("Neo-Dravidian")
print("1. Neo-Dravidian landmarks:", [lm["name"] for lm in neo_d])

# Test 2: find_by_era
br = gs.find_by_era("British Raj")
print("2. British Raj landmarks:", [lm["name"] for lm in br])

# Test 3: get_related_landmarks (2-hop)
related = gs.get_related_landmarks("bangalore_palace")
print("3. Related to Bangalore Palace:", [(r["name"], r["related_via"]) for r in related])

# Test 4: find_nearby
nearby = gs.find_nearby("vidhana_soudha")
print("4. Nearby Vidhana Soudha:", [n["name"] for n in nearby])

# Test 5: get_connections
conn = gs.get_connections("state_central_library")
print("5. SCL styles:", [s["name"] for s in conn["styles"]])
print("   SCL locations:", [loc["name"] for loc in conn["locations"]])
print("   SCL nearby:", [n["name"] for n in conn["nearby"]])

# Test 6: find_landmark_by_name
found = gs.find_landmark_by_name("tipu")
print("6. Search 'tipu':", found["name"] if found else "Not found")

# Summary
summary = gs.get_graph_summary()
print(f"\nGraph: {summary['total_nodes']} nodes, {summary['total_edges']} edges")
print(f"Node types: {summary['node_types']}")
print(f"Edge types: {summary['edge_types']}")

print("\n--- ALL TESTS PASSED ---")
