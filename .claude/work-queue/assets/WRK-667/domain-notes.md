# Domain Notes — WRK-667

WRK-667 is a quality-hardening WRK. WRK-655 created the RI skill infrastructure.
WRK-667 must now demonstrate that RI _increases_ execution strength by adding:

1. **Metrics schema** — define what "quality lift" means (plan rework, artifact gaps,
   cross-review blocker rate)
2. **HTML section** — surface RI confidence and findings in lifecycle HTML
3. **Validator checks** — extend validate-resource-pack.sh to enforce RI refs in WRK frontmatter
4. **Comparison examples** — 3 real WRKs: before RI → after RI to demonstrate impact

The implementation should be additive (extend existing skill/scripts) not replacement.
