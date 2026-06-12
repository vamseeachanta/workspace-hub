# Graph RAG Phase-1 Deterministic Graph — Spike Report (llm-wiki#443)

Built from existing structure only. Zero LLM calls.

## Graph size
- Standard nodes: **305**
- Resolved citation edges (standard->standard, in-corpus): **318**
- Total citation mentions resolved: **3097**
- Fuzzy cross-links.md standards edges (existing tooling): **40**

## Connectivity (citation graph, undirected)
- Connected components: **169**
- Largest component: **126** nodes (41% of nodes)
- Component size distribution (top 10): [126, 5, 3, 3, 2, 2, 2, 1, 1, 1]
- **Orphan nodes** (no resolved citation edge): **162** (53%)

## Top citation hubs (most cited by other standards)
| code_id | times cited (in-degree) | publisher | domain |
|---|---|---|---|
| api-510 | 23 | API | asset-management |
| iso-15156 | 21 | ISO | drilling-engineering |
| api-rp-579 | 15 | API | engineering-standards |
| iso-3183 | 14 | ISO | asset-management |
| api-570 | 13 | API | asset-management |
| iso-13628 | 13 | ISO | marine-engineering |
| bs-7910 | 12 | BSI | asset-management |
| iso-19901-1 | 12 | ISO | marine-engineering |
| iso-19906 | 11 | ISO | marine-engineering |
| api-rp-521 | 10 | API | engineering-standards |
| api-rp-520 | 10 | API | asset-management |
| iso-13628-1 | 10 | ISO | marine-engineering |
| iso-19901-4 | 10 | ISO | marine-engineering |
| iso-19905-1 | 10 | ISO | marine-engineering |
| iso-19901-2 | 9 | ISO | marine-engineering |

## Ingestion-gap queue — standards CITED but NOT in corpus (top 25)
Each is a standard the corpus references but does not contain. Free acquisition signal.
| referenced id | mention count |
|---|---|
| iso-10423 | 1327 |
| iso-13628-7 | 945 |
| api-rp-581-risk | 640 |
| asme-b31 | 403 |
| iso-13628-4 | 353 |
| iso-13628-5 | 347 |
| iso-13628-2 | 282 |
| dnv-oss-101 | 281 |
| iso-13679 | 279 |
| iso-11960 | 275 |
| iso-15156-3 | 237 |
| iso-10407-2 | 225 |
| iso-19902 | 207 |
| bs-5400-3 | 204 |
| bsi-05-2001 | 194 |
| iso-13628-10 | 194 |
| astm-e-709 | 186 |
| iso-13533 | 185 |
| iso-13628-6 | 183 |
| iso-15156-1 | 168 |
| iso-15156-2 | 155 |
| iso-19901 | 146 |
| iso-10424-1 | 141 |
| api-687 | 134 |
| iso-14693 | 134 |

## Publisher distribution of nodes
- API: 175
- ISO: 62
- BSI: 33
- DNV: 12
- Norsok: 7
- NACE: 4
- ABS: 4
- IEC: 4
- OnePetro: 2
- American Petroleum Institute: 1
- SNAME: 1