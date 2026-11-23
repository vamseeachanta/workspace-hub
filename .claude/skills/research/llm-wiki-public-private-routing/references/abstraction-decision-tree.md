# Abstraction decision tree — compatibility reference

This retained path supports existing handoffs. Use [the routing skill](../SKILL.md)
and `docs/architecture/agent-data-handling-contract.md` in the explicit
workspace-hub checkout as the current authority. Earlier examples at this path
must not be treated as permission to publish anonymized client data. Codes and
standards follow the owner's ruling of 28 Oct 2026
(`.claude/rules/codes-standards-data-routing.md`).

## Decision sequence

1. Establish source ownership, proposed operation, destination and audience.
2. For client and other third-party material, verify the source-specific rights and
   applicable action authorization. Codes and standards need no rights check.
3. Check every material claim, including contributions from private sources.
4. Apply abstraction requirements only after public use is permitted.
5. Record provenance, limitations and unresolved decisions; do not publish on a gap.

## Conditional examples

| Scenario | Disposition |
|---|---|
| Standards methodology with no client name | No rights check for codes and standards (owner ruling 28 Oct 2026). Originals may sit in private Git or the ACE data store; public pages quote with citations and reconstruct charts, never the original PDF or whole sections. |
| Public project name, private numerical result | Public naming does not authorize release of the result. Preserve the private owner and obtain source-specific permission before any public derivative. |
| Public case study with cited public facts | Verify rights for each source, destination and audience; actual naming may be permitted by the governing contract. Public availability alone is not a license. |
| Mixed standards and client illustration | Each component retains its restrictions. Removing names or substituting a range does not by itself permit publication. |
| Synthetic example influenced by restricted work | The label synthetic does not establish independence or rights. Preserve uncertainty and withhold public copying until the basis is established. |

Table 1. Examples explain conditions; none supplies source-specific permission.

Authorized private retention, approved public release, local saving and Git tracking
are distinct dispositions. Verify only the disposition actually performed.
