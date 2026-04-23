---
title: "FSRU Marine Terminal Interface"
tags: [fsru, lng, terminal, interface, regasification, mooring, port-operations]
sources:
  - lng2026-tp04-shipping-marine-port-operations
  - sigtto-lng-operations-port-areas
  - mooring-failures-lng-terminals
added: 2026-04-23
last_updated: 2026-04-23
---

# FSRU Marine Terminal Interface

The FSRU marine terminal interface is the combined ship/shore, berth, and marine-operations boundary created when a floating storage and regasification unit is used as part of an LNG receiving terminal. It is best treated as a distinct LNG terminal archetype because the floating unit changes how mooring, transfer, utility tie-ins, and marine operability interact.

## Why It Deserves Its Own Page

The main LNG terminal concept page already identifies FSRU-based receiving terminals as a separate terminal type. That distinction is useful because an FSRU terminal does not behave exactly like:
- a conventional fixed export jetty
- a simple import berth for intermittent carrier unloading
- a generic offshore mooring system

Instead, the marine interface must reconcile a permanently or semi-permanently stationed floating asset with visiting LNG carriers, port operations, and shore-side regasification export needs.

## Main Interface Elements

### 1. Stationed floating unit
The FSRU itself becomes part of the terminal, so marine engineering must consider:
- how the FSRU is moored or berthed
- how environmental loads affect its motions and availability
- whether the unit remains connected to shore utilities or gas export systems under all operating states

### 2. Visiting LNG carrier interface
A receiving FSRU still depends on carrier arrivals for LNG delivery. That adds operational coupling between:
- carrier approach and berthing
- side-by-side or berth transfer arrangement, depending on terminal configuration
- transfer connection and disconnection procedures
- combined motions of the delivery vessel and the FSRU or berth

### 3. Shore-side integration
Unlike a pure ship-call berth, the FSRU terminal interface also includes continuous terminal functions such as:
- regasification export continuity
- utility and control interfaces
- shutdown consequences that affect both marine and gas-sendout operations

## Engineering Themes Supported by Current Sources

The current sources support several high-level but actionable points:
- LNG marine and port operations are active engineering topics in the LNG value chain
- terminal engineering should explicitly distinguish FSRU terminals from conventional jetties
- mooring integrity remains central because line failures and low-frequency motions can disable availability even before structural failure occurs
- port-area LNG operations require integrated operational controls rather than isolated design checks

## Where FSRU Interfaces Commonly Become Limiting

### Mooring and stationkeeping
An FSRU arrangement may face prolonged exposure to berth or stationkeeping loads rather than the shorter occupation profile of a standard carrier call. That makes motion control, line integrity, and operability especially important.

### Transfer envelope
If LNG is transferred between a visiting carrier and the FSRU, the interface becomes sensitive to relative motions between floating bodies or between a floating body and the berth.

### Operations and sequencing
FSRU terminals often require tighter coordination of:
- arrival windows
- offloading sequence
- tug and pilot support
- sendout continuity
- abnormal-condition response

## What the Current Sources Do Not Yet Support

The existing wiki sources do not justify detailed claims about:
- a preferred universal mooring arrangement for all FSRUs
- numerical operability criteria for side-by-side transfer
- regas module design details
- detailed standards hierarchy specific to FSRU classification

Those subjects need additional dedicated FSRU guidance and project references.

## Practical Framing for Wiki Use

Within this wiki, the FSRU marine terminal interface can be used as the bridge topic between LNG berth engineering and floating asset operations. It helps separate three questions that are easy to mix together:
1. Can the FSRU remain safely on station or at berth?
2. Can a visiting LNG carrier transfer cargo to it within motion limits?
3. Can the overall receiving terminal continue gas sendout and marine operations reliably?

## Related Topics

- [[lng-marine-terminal-engineering]] gives the terminal-level systems view
- [[lng-berth-operability]] covers weather-window and uptime logic at berth
- [[lng-transfer-system-envelope]] covers motion compatibility for cargo transfer
- [[lng-carrier-mooring]] covers line behavior and terminal mooring context
- [[mooring-line-failure]] and [[long-period-swell-resonance]] explain why low-frequency response is a serious availability and safety issue

## Cross-References

- [[lng-marine-terminal-engineering]]
- [[lng-berth-operability]]
- [[lng-transfer-system-envelope]]
- [[lng-carrier-mooring]]
- [[mooring-line-failure]]
- [[long-period-swell-resonance]]
- [LNG2026 TP04: Shipping, Marine and Port Operations](../sources/lng2026-tp04-shipping-marine-port-operations.md)
- [SIGTTO LNG Operations in Port Areas](../sources/sigtto-lng-operations-port-areas.md)
- [Mooring Failures at LNG Terminals](../sources/mooring-failures-lng-terminals.md)
