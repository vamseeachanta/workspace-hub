---
name: trello-api-6-member-management
description: 'Sub-skill of trello-api: 6. Member Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 6. Member Management

## 6. Member Management


**REST API - Members:**
```bash
# Get board members
curl -s "https://api.trello.com/1/boards/BOARD_ID/members?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Get member info
curl -s "https://api.trello.com/1/members/MEMBER_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Add member to board
curl -s -X PUT "https://api.trello.com/1/boards/BOARD_ID/members/MEMBER_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "type=normal" | jq  # "admin", "normal", "observer"

# Remove member from board
curl -s -X DELETE "https://api.trello.com/1/boards/BOARD_ID/members/MEMBER_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"

# Assign member to card
curl -s -X POST "https://api.trello.com/1/cards/CARD_ID/idMembers" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "value=MEMBER_ID" | jq

# Remove member from card
curl -s -X DELETE "https://api.trello.com/1/cards/CARD_ID/idMembers/MEMBER_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"

# Get cards assigned to member
curl -s "https://api.trello.com/1/members/MEMBER_ID/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq
```

**Python SDK - Members:**
```python
# Get current user
me = client.get_member("me")
print(f"Name: {me.full_name}")
print(f"Username: {me.username}")
print(f"Email: {me.email}")

# Get board members
members = board.get_members()
for member in members:
    print(f"Member: {member.full_name} (@{member.username})")

# Assign member to card
card.add_member(member)

# Remove member from card
card.remove_member(member)

# Get all cards for a member
member_cards = client.get_member("me").fetch_cards()
for card in member_cards:
    print(f"Assigned card: {card.name}")

# Get boards for member
member_boards = client.get_member("me").fetch_boards()
for board in member_boards:
    print(f"Board: {board.name}")
```
