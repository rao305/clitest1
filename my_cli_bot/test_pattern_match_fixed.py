#!/usr/bin/env python3
import re

query = "can you find me a recent purdue grad who majored in computer science who landed a role at NVIDIA"
query_lower = query.lower()

patterns = [
    r"alumni", r"professionals", r"mentor", r"mentorship", r"network", r"networking",
    r"purdue.*graduates", r"purdue.*grad", r"cs.*alumni", r"people.*working", 
    r"find.*professionals", r"find.*me.*grad", r"find.*me.*alumni",
    r"connect.*with", r"working.*at.*", r"landed.*role.*at", r"role.*at.*",
    r"career.*connections", r"industry.*contacts",
    r"professionals.*in", r"people.*in.*field", r"alumni.*network"
]

print(f"Query: {query}")
print(f"Query lower: {query_lower}")
print()

matches = []
for pattern in patterns:
    match = re.search(pattern, query_lower)
    status = '✅ MATCH' if match else '❌ NO MATCH'
    print(f"Pattern '{pattern}': {status}")
    if match:
        matches.append(pattern)
        
print(f"\n🎯 Total matches: {len(matches)}")
print(f"Matching patterns: {matches}")