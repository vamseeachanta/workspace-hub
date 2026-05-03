# Disagreement report — plan #2589 (2026-05-02)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### gemini

- Plan §Evidence (embedded verification) claims `ls knowledge/wikis/naval-architecture/wiki/entities/ 2>&1` returns `(empty)`. This is fabricated. The `entities/` directory does not exist at HEAD; the command returns `No such file or directory`.
- Plan §Files to Change proposes creating `knowledge/wikis/naval-architecture/wiki/entities/classification-societies.md`, but because the `entities/` directory does not exist, this will fail unless directory creation is explicitly added to the plan's pseudocode.
- Plan §Risks and Open Questions correctly notes that `index.md` is auto-generated and proposes the mitigation to "log the additions in log.md AND in knowledge/seeds/naval-architecture-resources.yaml". However, §Files to Change and §Pseudocode fail to include any updates to `knowledge/seeds/naval-architecture-resources.yaml`. `index.md` line 8 confirms `*Auto-generated from knowledge/seeds/naval-architecture-resources.yaml*`. Manual edits to `index.md` will be overwritten.
- Plan §Resource Intelligence Summary claims sibling wikis `knowledge/wikis/marine-engineering/wiki/` and `knowledge/wikis/maritime-law/wiki/` are "referenced via cross-links". While referenced in existing files, the `wiki/` subdirectories for these sibling domains do not actually exist at HEAD. Propagating these as `see_also` targets will result in broken links.
- Plan §TDD Test List includes `test_index_links_resolve` for `index.md` links, but relies only on `test_frontmatter_see_also_min_two` for the new concept pages. The latter only checks `len(see_also) >= 2` (parsing YAML) and fails to actually validate that the newly authored `see_also` links resolve.

