---
name: calendly-api-6-scheduling-links-and-routing
description: 'Sub-skill of calendly-api: 6. Scheduling Links and Routing.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 6. Scheduling Links and Routing

## 6. Scheduling Links and Routing


```python
# scheduling.py
# ABOUTME: Scheduling links and routing forms
# ABOUTME: Single-use links, routing, and booking customization

from client import client
from typing import Optional


def create_single_use_link(event_type_uri: str, max_event_count: int = 1) -> dict:
    """Create a single-use scheduling link

    These links can only be used for a limited number of bookings
    """
    response = client.post(
        "/scheduling_links",
        json={
            "max_event_count": max_event_count,
            "owner": event_type_uri,
            "owner_type": "EventType",
        },
    )
    return response.get("resource", {})


def get_scheduling_link(link_uri: str) -> dict:
    """Get scheduling link details"""
    uuid = link_uri.split("/")[-1]
    response = client.get(f"/scheduling_links/{uuid}")
    return response.get("resource", {})


def list_routing_forms(organization_uri: str = None) -> list:
    """List routing forms"""
    org = organization_uri or client.organization_uri
    params = {"organization": org}
    return client.paginate("/routing_forms", params=params)


def get_routing_form(form_uri: str) -> dict:
    """Get routing form details"""
    uuid = form_uri.split("/")[-1]
    response = client.get(f"/routing_forms/{uuid}")
    return response.get("resource", {})


def list_routing_form_submissions(
    form_uri: str,
    sort: str = "created_at:desc",
) -> list:
    """List routing form submissions"""
    params = {
        "routing_form": form_uri,
        "sort": sort,
    }
    return client.paginate("/routing_form_submissions", params=params)


def get_routing_form_submission(submission_uri: str) -> dict:
    """Get routing form submission details"""
    uuid = submission_uri.split("/")[-1]
    response = client.get(f"/routing_form_submissions/{uuid}")
    return response.get("resource", {})


def build_scheduling_url(
    base_url: str,
    name: str = None,
    email: str = None,
    utm_source: str = None,
    utm_medium: str = None,
    utm_campaign: str = None,
    custom_answers: dict = None,
) -> str:
    """Build a pre-filled scheduling URL

    custom_answers: {"a1": "answer1", "a2": "answer2"} for custom questions
    """
    from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

    params = {}

    if name:
        params["name"] = name
    if email:
        params["email"] = email
    if utm_source:
        params["utm_source"] = utm_source
    if utm_medium:
        params["utm_medium"] = utm_medium
    if utm_campaign:
        params["utm_campaign"] = utm_campaign
    if custom_answers:
        params.update(custom_answers)

    if not params:
        return base_url

    parsed = urlparse(base_url)
    query = urlencode(params)

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query,
        parsed.fragment,
    ))


def generate_interview_links(
    event_type_uri: str,
    candidates: list,
) -> list:
    """Generate single-use interview links for candidates

    candidates: [{"name": "John", "email": "john@example.com"}, ...]
    """
    event_type = get_event_type(event_type_uri)
    base_url = event_type["scheduling_url"]

    links = []
    for candidate in candidates:
        # Create single-use link
        link = create_single_use_link(event_type_uri, max_event_count=1)

        # Build pre-filled URL
        scheduling_url = build_scheduling_url(
            base_url=link["booking_url"],
            name=candidate.get("name"),
            email=candidate.get("email"),
            utm_source="interview",
            utm_campaign=candidate.get("campaign", "hiring"),
        )

        links.append({
            "candidate": candidate,
            "link_uri": link["uri"],
            "scheduling_url": scheduling_url,
        })

    return links


from event_types import get_event_type


if __name__ == "__main__":
    from event_types import list_event_types

    # Get an event type
    event_types = list_event_types()
    if event_types:
        et = event_types[0]

        # Build pre-filled URL
        url = build_scheduling_url(
            base_url=et["scheduling_url"],
            name="Jane Doe",
            email="jane@example.com",
            utm_source="email",
            utm_campaign="q1-outreach",
        )
        print(f"Pre-filled URL: {url}")

        # Create single-use link
        single_use = create_single_use_link(et["uri"])
        print(f"Single-use booking URL: {single_use['booking_url']}")
```
