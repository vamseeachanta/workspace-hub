#!/usr/bin/env python3
"""
Reclassify miscategorized domain entries in standards-transfer-ledger.yaml.

Many entries are in domains that don't match their actual content:
- ASTM A-series steel specs in 'structural' should be 'materials'
- ASTM E-series testing/fatigue in various domains need review
- ISO drawing standards in wrong domains -> 'cad'
- Welding standards (API 1104, AWS) -> 'materials'
- API 14xx platform safety -> 'process' or 'marine' or 'installation'
- ASTM G-series corrosion -> 'cathodic-protection'
- Storage tank standards -> 'installation'
- Valve/equipment standards miscategorized
- etc.
"""
import yaml
import sys
import re
from collections import Counter

LEDGER_PATH = "data/document-index/standards-transfer-ledger.yaml"

def classify_standard(entry):
    """Return the correct domain for a standard, or None if current is fine."""
    sid = entry.get('id', '').upper()
    title = (entry.get('title', '') or '').upper()
    org = (entry.get('org', '') or '').upper()
    notes = (entry.get('notes', '') or '').upper()
    current = entry.get('domain', '')
    combined = f"{sid} {title} {notes}"

    # ========================================================================
    # ASTM A-series: Steel/metal material specifications -> materials
    # ========================================================================
    if 'ASTM' in sid or 'ASTM' in org:
        # ASTM A-series = material specifications (steel, alloy, etc.)
        if re.search(r'ASTM[- _]?A\d', sid) or re.search(r'ASTM[- _]?A\d', title):
            # A131 = structural steel for ships (could be marine or materials)
            # A36 = carbon structural steel
            # A508, A541 = forgings
            # All are fundamentally material specifications
            if current != 'materials':
                return 'materials'

        # ASTM E-series = testing methods
        if re.search(r'ASTM[- _]?E\d', sid) or re.search(r'ASTM[- _]?E\d', title):
            # Fatigue testing standards
            fatigue_kw = ['FATIGUE', 'CYCLE COUNTING', 'STRAIN-CONTROLLED', 'CRACK GROWTH',
                          'STRESS-RUPTURE', 'CREEP', 'CONSTANT AMPLITUDE']
            is_fatigue = any(kw in combined for kw in fatigue_kw)

            # Materials testing standards (hardness, tension, metallography, etc.)
            materials_kw = ['HARDNESS', 'TENSION TEST', 'METALLOG', 'GRAIN SIZE',
                           'DUCTILITY', 'BEND TEST', 'COMPRESSION TEST', 'POISSON',
                           'MICROETCH', 'INCLUSION', 'DECARBURIZ', 'INDENTATION',
                           'POLISHING', 'QUANTITATIVE ANALYSIS', 'POLE FIGURE',
                           'EXTENSOMETER', 'STRAIN RATIO', 'SUPERPLASTIC',
                           'FORMING LIMIT', 'STRAIN-HARDENING', 'SPRING',
                           'METALLIC FOIL', 'BALL PUNCH', 'SHARP-NOTCH',
                           'RESIDUAL STRAIN', 'IN-PLANE LENGTH', 'STRAIN GRADIENT',
                           'TRANSLAMINAR', 'CRACK-TIP OPENING', 'CHEVRON-NOTCH',
                           'CTOD', 'K-R CURVE', 'VOLUME FRACTION', 'CRACK-ARREST',
                           'SCANNING ELECTRON', 'CALIBRAT', 'FORCE-MEASUR',
                           'ENERGY-DISPERSI', 'ELECTROLYTIC', 'LABORATORY SAFETY',
                           'AUSTENITE', 'X-RAY DETERMINATION', 'X-RAY DIFFR',
                           'COMPUTER-GENERATED', 'ELEVATED TEMPERATURE',
                           'RESIDUAL STRESS', 'HOLE-DRILL', 'THERMOCOUPLE',
                           'RESIDUAL CIRC', 'DATA ACQUISITION', 'DATA RECORDS',
                           'PLASTICS AND POLYMERIC']

            # Structural testing standards (modulus, radiographs, structural analysis)
            structural_kw = ['YOUNG\'S MODULUS', 'SHEAR MODULUS', 'RADIOGRAPH',
                            'HEAVY-WALLED', 'RUSTING', 'PAINTED', 'SULFUR PRINT',
                            'MACROSTRUCTU', 'STRESS RELAXATION', 'STEPPED BLOCK']

            if is_fatigue:
                # Fatigue testing -> structural (fatigue analysis domain)
                if current != 'structural':
                    return 'structural'
            elif any(kw in combined for kw in structural_kw):
                if current != 'structural':
                    return 'structural'
            elif any(kw in combined for kw in materials_kw):
                if current != 'materials':
                    return 'materials'
            else:
                # Default for ASTM E: materials testing
                if current != 'materials':
                    return 'materials'

        # ASTM D-series = coatings/paints -> structural (coating assessment)
        if re.search(r'ASTM[- _]?D\d', sid) or re.search(r'ASTM[- _]?D\d', title):
            if 'RUST' in combined or 'PAINT' in combined:
                if current != 'structural':
                    return 'structural'

        # ASTM G-series = corrosion testing -> cathodic-protection
        if re.search(r'ASTM[- _]?G\d', sid) or re.search(r'ASTM[- _]?G\d', title):
            if current != 'cathodic-protection':
                return 'cathodic-protection'

    # ========================================================================
    # API standards reclassification
    # ========================================================================
    if 'API' in org or 'API' in sid:
        # API 1104 = Welding of pipelines -> materials (welding)
        if '1104' in sid:
            if current != 'materials':
                return 'materials'

        # API 5CT = Casing and Tubing -> drilling
        if '5CT' in sid:
            if current != 'drilling':
                return 'drilling'

        # API 5D = Drill Pipe -> drilling
        if re.search(r'\b5D\b', sid):
            if current != 'drilling':
                return 'drilling'

        # API 6A, 6AF = Wellhead equipment -> drilling
        if re.search(r'\b6A\b', sid) or '6AF' in sid or '6ASECTION' in sid:
            if current != 'drilling':
                return 'drilling'

        # API RP 14B = Subsurface safety valve -> drilling
        # API RP 14C = Safety analysis for surface production -> process
        # API RP 14E = Design of production platforms -> process
        # API RP 14G = Fire prevention -> regulatory
        # API RP 14H = Installation -> installation
        # API RP 14J = Hazards analysis -> regulatory
        if 'RP-14C' in sid or 'RP_14C' in sid:
            if current != 'process':
                return 'process'
        if 'RP-14J' in sid or 'RP_14J' in sid:
            if current != 'regulatory':
                return 'regulatory'

        # API 12-series (storage tanks) -> installation
        if re.search(r'API.*(12[A-Z]|12R)', sid) or re.search(r'API.*(SPEC.*12|RP.*12[A-Z])', sid):
            if 'TANK' in combined or 'STORAGE' in combined or 'SETTING' in combined or 'MAINTENANCE' in combined:
                if current != 'installation':
                    return 'installation'

        # API RP 2201 = Procedures for Welding/Hot Tapping -> pipeline
        # (already pipeline, fine)

        # API RP 2016 = petroleum storage -> installation (or regulatory)
        if '2016' in sid and 'PETROLEUM STORAGE' in combined:
            if current != 'installation':
                return 'installation'

        # API 520, 521 = Pressure relief devices -> process
        # API 526, 527 = Flanged steel pressure-relief valves -> process
        # API 530 = Fired heater tubes -> process
        # Already mostly in process, good

        # API 560 = Fired heaters -> process
        if '560' in sid and current != 'process':
            if 'HEATER' in combined or 'FIRED' in combined:
                return 'process'

        # API RP 572 = Inspection of Pressure Vessels -> structural
        if '572' in sid and 'PRESSURE VESSEL' in combined:
            if current != 'structural':
                return 'structural'

        # API RP 573 = Inspection of Fired Boilers and Heaters -> process
        if '573' in sid:
            if current != 'process':
                return 'process'

        # API RP 574 = Inspection of Piping -> pipeline
        if re.search(r'RP.574\b', sid) and 'PIPING' in combined:
            if current != 'pipeline':
                return 'pipeline'

        # API RP 575 = Atmospheric/low-pressure storage tanks -> installation
        if '575' in sid and ('TANK' in combined or 'STORAGE' in combined):
            if current != 'installation':
                return 'installation'

        # API RP 576 = Pressure-relieving devices -> process
        if '576' in sid:
            if current != 'process':
                return 'process'

        # API 578 = Material verification -> materials (already correct)
        # API 579 = Fitness for service -> structural (already correct)

        # API 580, 581 = Risk-based inspection -> regulatory (already correct)

        # API RP 582 = Welding guidelines for CPI -> materials
        # (already materials, fine)

        # API 594, 599, 600, 602, 603, 607, 608, 609 = Valves -> process
        valve_ids = ['594', '599', '600', '602', '603', '607', '608', '609']
        for vid in valve_ids:
            if vid in sid and ('VALVE' in combined or 'STD' in title or 'GATE' in combined or 'PLUG' in combined or 'CHECK' in combined or 'BUTTERFLY' in combined):
                if current != 'process':
                    return 'process'

        # API Std 610-619 = Pumps, turbines, compressors -> process (already correct)

        # API 650 = Welded tanks -> installation
        if re.search(r'STD.650\b', sid) or re.search(r'RP.650\b', sid):
            if 'TANK' in combined or 'WELDED' in combined:
                if current != 'installation':
                    return 'installation'

        # API 620 = Large welded low-pressure storage tanks -> installation
        if '620' in sid and ('TANK' in combined or 'STORAGE' in combined):
            if current != 'installation':
                return 'installation'

        # API 653 = Tank inspection -> installation
        if '653' in sid and 'TANK' in combined:
            if current != 'installation':
                return 'installation'

        # API 660-677 = Heat exchangers, fans, gears -> process
        # Already in process mostly

        # API RP 683 = Material verification for upstream -> materials (correct)

        # API RP 686 = Machinery installation -> installation
        if '686' in sid and 'INSTALL' in combined:
            pass  # keep installation

        # API RP 687 = Rotor repair -> process (actually more materials/mechanical)
        if '687' in sid:
            if current != 'process':
                return 'process'

        # API RP 1604 = Closure of underground storage tanks -> regulatory
        # API RP 1615 = Installation of underground storage systems -> installation
        if '1615' in sid:
            if current != 'installation':
                return 'installation'

        # API RP 1621 = Bulk liquid stock control -> regulatory (correct)

        # API RP 1631 = Interior lining of existing steel underground storage tanks -> materials
        # (already materials)

        # API RP 2210 = Flame arrestors -> process
        if '2210' in sid:
            if current != 'process':
                return 'process'

        # API RP 2350 = Overfill protection -> process
        if '2350' in sid:
            if current != 'process':
                return 'process'

        # API 531M = Measurement of noise -> process
        if '531M' in sid or '531' in sid:
            if current != 'process':
                return 'process'

        # API RP 536 = Post-combustion -> process
        if '536' in sid:
            if current != 'process':
                return 'process'

        # API RP 17A = Subsea production systems -> marine
        if '17A' in sid and current != 'marine':
            return 'marine'

        # API RP 2Z = Preproduction qualification for steel plates -> materials
        # (already materials, fine)

        # API 2B = Fabrication of structural steel pipe -> structural (correct)
        # API 2H = Carbon manganese steel plate -> materials (correct)

        # API Inspection standards (510, 570) - these are inspection/regulatory
        if '510' in sid and 'INSP' in sid:
            if current != 'regulatory':
                return 'regulatory'
        if '570' in sid and 'INSP' in sid:
            if current != 'regulatory':
                return 'regulatory'

        # API RP 571 = Damage mechanisms -> materials (correct)

        # API RP 80 = Security -> regulatory (correct)

        # API 12B, 12D, 12F, 12J, 12L, 12P, 12GDU = tanks/vessels -> installation
        tank_patterns = ['12B', '12D', '12F', '12J', '12L', '12P', '12GDU', '12N']
        for tp in tank_patterns:
            if tp in sid:
                if current != 'installation':
                    return 'installation'

    # ========================================================================
    # ISO standards
    # ========================================================================
    if 'ISO' in org or 'ISO' in sid:
        # ISO 128-xx, 129, 406, 1101, 2768, 2902, 5456, 5457, 6410, 7200, 7519, 7573
        # = Drawing/CAD standards
        cad_patterns = ['128-', '129', '406', '1101', '2768', '2902', '5456', '5457',
                       '6410', '7200', '7519', '7573']
        for cp in cad_patterns:
            if cp in sid:
                if current != 'cad':
                    return 'cad'
            if cp in title:
                if current != 'cad':
                    return 'cad'

        # ISO 13819 = Fixed offshore structures -> structural
        if '13819' in sid and current != 'structural':
            return 'structural'

        # ISO 15156 = Cracking-resistant materials in H2S -> cathodic-protection
        # (already cathodic-protection, fine)

        # ISO 15589 = Cathodic protection -> cathodic-protection (correct)

        # ISO thermal spray standards (14916-14922, 2063) -> materials
        # (already materials, fine)

    # ========================================================================
    # DNV standards
    # ========================================================================
    if 'DNV' in org or 'DNV' in sid:
        # DNV OS/RP F-series = pipeline
        # DNV RP B401 = cathodic protection
        # DNV OS E301 = Position mooring -> marine
        # Most seem correctly classified already
        pass

    # ========================================================================
    # AWS welding standards -> materials
    # ========================================================================
    if 'AWS' in sid or 'AWS' in org or 'AWS' in title:
        if current != 'materials':
            return 'materials'

    # ========================================================================
    # BS standards
    # ========================================================================
    if 'BS' in org:
        if 'FATIGUE' in combined:
            if current != 'structural':
                return 'structural'

    # ========================================================================
    # ABS standards -> marine
    # ========================================================================
    if 'ABS' in org or 'ABS' in sid:
        if current != 'marine':
            return 'marine'

    # ========================================================================
    # Specific reclassifications based on analysis
    # ========================================================================

    # ASTM E1544 = Stepped Block (calibration reference) -> materials
    if 'E1544' in sid:
        if current != 'materials':
            return 'materials'

    # ASTM E915 = X-Ray alignment -> materials (testing equipment)
    if 'E915' in sid:
        if current != 'materials':
            return 'materials'

    # API Std 589 = Fire test for valves -> process
    if '589' in sid and 'API' in (org + sid):
        if current != 'process':
            return 'process'

    # API 591 = Valve specs -> process
    if '591' in sid and 'API' in (org + sid):
        if current != 'process':
            return 'process'

    # API 621 = Reconditioning of metallic gate/globe/check valves -> process
    if '621' in sid and 'API' in (org + sid):
        if current != 'process':
            return 'process'

    # API 652 = Lining of aboveground storage tanks -> installation
    if '652' in sid and 'API' in (org + sid):
        if current != 'installation':
            return 'installation'

    # API Std 598 = Valve inspection and testing -> process
    if '598' in sid and 'API' in (org + sid):
        if current != 'process':
            return 'process'

    # API Std 560 = Fired heaters -> process
    if '560' in sid and 'API' in (org + sid):
        if current != 'process':
            return 'process'

    # API Std 526 = Flanged steel pressure relief valves -> process
    if '526' in sid and 'API' in (org + sid):
        if current != 'process':
            return 'process'

    # API Std 530 = Calculation of heater-tube thickness -> process
    if '530' in sid and 'API' in (org + sid):
        if current != 'process':
            return 'process'

    return None  # No change needed


def main():
    with open(LEDGER_PATH, 'r') as f:
        data = yaml.safe_load(f)

    changes = []
    before_counts = Counter()
    after_counts = Counter()

    for entry in data['standards']:
        old_domain = entry.get('domain', '')
        before_counts[old_domain] += 1

        new_domain = classify_standard(entry)
        if new_domain and new_domain != old_domain:
            changes.append({
                'id': entry.get('id', ''),
                'title': (entry.get('title', '') or '')[:80],
                'old': old_domain,
                'new': new_domain,
                'status': entry.get('status', '')
            })
            entry['domain'] = new_domain
            after_counts[new_domain] += 1
        else:
            after_counts[old_domain] += 1

    # Print summary
    print(f"\n=== RECLASSIFICATION SUMMARY ===")
    print(f"Total entries: {len(data['standards'])}")
    print(f"Entries reclassified: {len(changes)}")
    print()

    # Show changes grouped by transition
    transitions = Counter()
    for c in changes:
        transitions[(c['old'], c['new'])] += 1

    print("Domain transitions:")
    for (old, new), count in sorted(transitions.items(), key=lambda x: -x[1]):
        print(f"  {old:25s} -> {new:25s} : {count}")

    print()
    print("Before/After domain counts:")
    all_domains = sorted(set(list(before_counts.keys()) + list(after_counts.keys())))
    print(f"  {'Domain':25s} {'Before':>8s} {'After':>8s} {'Delta':>8s}")
    for d in all_domains:
        b = before_counts.get(d, 0)
        a = after_counts.get(d, 0)
        delta = a - b
        sign = '+' if delta > 0 else ''
        print(f"  {d:25s} {b:8d} {a:8d} {sign}{delta:7d}")

    print()
    print("All changes:")
    for c in changes:
        print(f"  [{c['status']:12s}] {c['id']:40s} {c['old']:20s} -> {c['new']}")

    # Write back
    with open(LEDGER_PATH, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120, sort_keys=False)

    print(f"\n=== Written {LEDGER_PATH} ===")

    return len(changes)


if __name__ == '__main__':
    n = main()
    sys.exit(0 if n > 0 else 1)
