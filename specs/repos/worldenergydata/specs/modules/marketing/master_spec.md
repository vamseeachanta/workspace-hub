# Master Specification: Marketing Materials (Generic Template)

## Overview
Generate professional marketing brochures for repository modules targeting specified audiences with appropriate technical detail levels. This specification is designed to be repository-agnostic and configured via YAML.

## Configuration System

### YAML Configuration File
All repository-specific details are configured in `marketing_config.yaml`:
- Repository name and branding
- Target audiences and technical levels
- Module list and tiers
- Statistics and metrics
- Contact information
- Industry focus and standards emphasis

### Template Variables
The following variables are replaced during brochure generation:
- `{{REPO_NAME}}` - Repository name
- `{{REPO_DESCRIPTION}}` - Short repository description
- `{{TARGET_AUDIENCE}}` - Primary audience description
- `{{TECHNICAL_LEVEL}}` - Technical detail level
- `{{MODULE_COUNT}}` - Number of modules
- `{{TEST_COUNT}}` - Number of tests
- `{{YEARS_EXPERIENCE}}` - Years of development/expertise
- `{{CONTACT_EMAIL}}` - Contact email address
- `{{GITHUB_LINK}}` - GitHub repository URL
- `{{INDUSTRY_FOCUS}}` - Industry/domain focus
- `{{STANDARDS_EMPHASIS}}` - What to emphasize (standards, data sources, etc.)

## Target Audience Configuration

Audiences are configured in YAML with the following attributes:
- **Name**: Audience segment identifier
- **Technical Level**: Detail level (Executive, Manager, Engineer, Analyst, Researcher)
- **Use Cases**: Primary use cases for this audience
- **Key Concerns**: What they care about most

## Module Organization

### Tier Structure
Modules are organized into tiers based on priority and complexity:

**Tier 1**: Core/Foundation Modules
- Essential capabilities
- Most commonly used features
- Highest priority for brochure creation

**Tier 2**: Advanced/Specialized Modules
- Sector-specific capabilities
- Advanced analysis features
- Secondary priority

**Tier 3**: Integration & Tools
- Integration with external systems
- Automation and tooling
- Supporting capabilities

**Tier 4**: Optional/Emerging Modules
- Experimental features
- Niche capabilities
- Future development areas

## Brochure Structure (1-2 Pages)

### Page 1: Overview & Capabilities

```markdown
# {{MODULE_NAME}}
## {{MODULE_TAGLINE}}

### Overview
[2-3 sentence value proposition tailored to {{TARGET_AUDIENCE}}]

### Key Capabilities
- [Capability 1] - [Brief description with {{TECHNICAL_LEVEL}} detail]
- [Capability 2] - [Brief description]
- [Capability 3] - [Brief description]
- [Capability 4] - [Brief description]
- [Capability 5] - [Brief description]

### {{STANDARDS_EMPHASIS}}
[Configured based on industry_focus: compliance standards, data sources, methodologies, etc.]
- [Item 1]
- [Item 2]
- [Item 3]

### Technical Features
#### [Feature Category 1]
- [Technical detail at {{TECHNICAL_LEVEL}}]
- [Technical detail]

#### [Feature Category 2]
- [Technical detail]
- [Technical detail]
```

### Page 2: Benefits & Outputs

```markdown
### Key Benefits
1. **[Benefit Category relevant to {{TARGET_AUDIENCE}}]**
   - [Specific benefit]
   - [Quantifiable improvement]

2. **[Benefit Category]**
   - [Specific benefit]
   - [Quantifiable improvement]

3. **[Benefit Category]**
   - [Specific benefit]
   - [Quantifiable improvement]

### Output Examples
[Screenshot or description of typical outputs]
- Interactive plots and visualizations
- Comprehensive analysis reports
- Data export capabilities

### Integration
- Compatible with: [Software/systems list from config]
- Input formats: [Format list from config]
- Output formats: [Format list from config]

### About {{REPO_NAME}}
{{REPO_DESCRIPTION}}

**Repository Highlights:**
- {{YEARS_EXPERIENCE}} years of development and expertise
- {{MODULE_COUNT}} comprehensive modules
- {{TEST_COUNT}} rigorous tests ensuring quality
- Production-ready for enterprise deployment
- [Additional stats from config]

### Contact Information
- Email: {{CONTACT_EMAIL}}
- GitHub: {{GITHUB_LINK}}
- Documentation: [Module-specific docs from config]
```

## Design Requirements

### Visual Style
- **Professional** {{INDUSTRY_FOCUS}} aesthetic
- **Clean** layout with clear hierarchy
- **Technical** but accessible language for {{TARGET_AUDIENCE}}
- **Branded** with {{REPO_NAME}} identity

### Content Guidelines
- Use **active voice** and **present tense**
- Include **quantifiable** benefits where possible
- Reference **{{STANDARDS_EMPHASIS}}** explicitly
- Show **real capabilities** (no marketing fluff)
- Include **code examples** or **technical specifications** appropriate to {{TECHNICAL_LEVEL}}
- Tailor language complexity to {{TARGET_AUDIENCE}}

### PDF Generation
- Use `pandoc` with professional template
- Include header/footer with {{REPO_NAME}} branding
- Ensure proper page breaks
- Professional fonts (Arial, Helvetica, or similar)
- Optional: Company logo from config

## File Naming Convention
- Markdown: `marketing_brochure_<module_name>.md`
- PDF: `marketing_brochure_<module_name>.pdf`
- Location: `reports/modules/marketing/` (configurable)

## Data Sources for Content

Content is automatically extracted from:
1. **Module `__init__.py` files** - Feature lists and capabilities
2. **Module `README.md` files** - Technical details and documentation
3. **Test files** - Capability validation and coverage
4. **Example reports** - Output demonstrations
5. **Main README.md** - Overall repository context
6. **Configuration YAML** - Repository-specific metadata

## Automation Workflow

### 1. Configuration Loading
```python
# Load repository-specific configuration
config = load_yaml("marketing_config.yaml")

# Extract repository metadata
repo_name = config['repository']['name']
target_audiences = config['audiences']
modules = config['modules']
```

### 2. Module Analysis
```python
# For each module in configuration
for module in modules:
    # Extract capabilities from code
    capabilities = analyze_module(module['path'])

    # Generate content with appropriate technical level
    content = generate_content(
        module=module,
        audience=config['audiences'][module['tier']],
        template=load_template("brochure_template.md")
    )
```

### 3. Template Rendering
```python
# Replace template variables
rendered = template.replace("{{REPO_NAME}}", config['repository']['name'])
rendered = rendered.replace("{{MODULE_COUNT}}", str(config['statistics']['module_count']))
# ... etc for all variables
```

### 4. PDF Generation
```bash
# Generate PDF with repository branding
pandoc marketing_brochure_<module>.md \
    -o marketing_brochure_<module>.pdf \
    --template={{REPO_NAME}}_template.tex \
    --metadata title="{{MODULE_NAME}}" \
    --metadata author="{{REPO_NAME}} Team"
```

## Approval Process
1. Load configuration YAML
2. Generate markdown brochure with template variables
3. Review technical accuracy against module code
4. Generate PDF with repository branding
5. Final validation against configuration requirements

## Configuration File Structure

See `marketing_config_schema.yaml` for complete schema definition and `<repo_name>_marketing_config.yaml` for repository-specific implementation.

### Required Sections
- `repository` - Name, description, links, branding
- `audiences` - Target audience definitions with technical levels
- `modules` - Organized by tier with metadata
- `statistics` - Repository metrics and highlights
- `contact` - Contact information and links
- `industry` - Industry focus and standards emphasis
- `branding` - Visual identity and styling preferences

## Timeline
- Research & specification: ✅ Complete
- Template creation: In progress
- Configuration creation: Per repository
- Content generation: 1 module per iteration (automated)
- PDF generation: Batch processing (automated)
- Review: Final step

## Success Criteria
- Generic template works across multiple repositories
- YAML configuration enables easy customization
- All configured modules have professional brochures
- PDFs are presentation-ready
- Content is technically accurate
- Benefits are clearly articulated for target audiences
- Output examples are included
- Automation reduces manual effort by 80%+

## Multi-Repository Support

This template is designed to support multiple repositories:
- **worldenergydata** - Energy data analysis and lifecycle management
- **digitalmodel** - Engineering asset lifecycle management
- **[Future repositories]** - Add new configurations as needed

Each repository maintains its own `<repo_name>_marketing_config.yaml` file with repository-specific metadata while using the same master specification and template system.
