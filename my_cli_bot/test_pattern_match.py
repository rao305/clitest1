#!/usr/bin/env python3
import re

query = "can you find me a recent purdue grad who majored in computer science who landed a role at NVIDIA"
query_lower = query.lower()

patterns = [
    r"alumni", r"professionals", r"mentor", r"mentorship", r"network", r"networking",
    r"purdue.*graduates", r"cs.*alumni", r"people.*working", r"find.*professionals",
    r"connect.*with", r"working.*at.*", r"career.*connections", r"industry.*contacts",
    r"professionals.*in", r"people.*in.*field", r"alumni.*network"
]

print(f"Query: {query}")
print(f"Query lower: {query_lower}")
print()

for pattern in patterns:
    match = re.search(pattern, query_lower)
    print(f"Pattern '{pattern}': {'✅ MATCH' if match else '❌ NO MATCH'}")
    
print()
print("Should match patterns:")
print("- 'purdue.*graduates' should match 'purdue grad'")
print("- 'find.*professionals' should match 'find me a recent...'")
print("- 'working.*at.*' should match 'working at nvidia'")