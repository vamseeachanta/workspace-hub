---
name: streamlit-6-session-state
description: 'Sub-skill of streamlit: 6. Session State (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 6. Session State (+1)

## 6. Session State


**Managing State:**
```python
import streamlit as st

# Initialize state
if "counter" not in st.session_state:
    st.session_state.counter = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display current state
st.write(f"Counter: {st.session_state.counter}")

# Update state with buttons
col1, col2, col3 = st.columns(3)

if col1.button("Increment"):
    st.session_state.counter += 1
    st.rerun()

if col2.button("Decrement"):
    st.session_state.counter -= 1
    st.rerun()

if col3.button("Reset"):
    st.session_state.counter = 0
    st.rerun()

# State with widgets
st.text_input("Name", key="user_name")
st.write(f"Hello, {st.session_state.user_name}!")

# State callback
def on_change():
    st.session_state.processed = st.session_state.raw_input.upper()

st.text_input("Raw input", key="raw_input", on_change=on_change)
if "processed" in st.session_state:
    st.write(f"Processed: {st.session_state.processed}")
```

**Form State:**
```python
import streamlit as st

# Forms prevent rerunning on every widget change
with st.form("my_form"):
    st.write("Submit all at once:")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    color = st.selectbox("Favorite color", ["Red", "Green", "Blue"])

    # Every form needs a submit button
    submitted = st.form_submit_button("Submit")

    if submitted:
        st.success(f"Thanks {name}! You're {age} and like {color}.")
```


## 7. Multi-Page Applications


**Directory Structure:**
```
my_app/
├── app.py              # Main entry point (optional)
├── pages/
│   ├── 1_📊_Dashboard.py
│   ├── 2_📈_Analytics.py
│   └── 3_⚙️_Settings.py
└── utils/
    └── helpers.py
```

**Main App (app.py):**
```python
import streamlit as st

st.set_page_config(
    page_title="Multi-Page App",
    page_icon="🏠",
    layout="wide"
)

st.title("Welcome to My App")
st.write("Use the sidebar to navigate between pages.")

# Shared state initialization
if "user" not in st.session_state:
    st.session_state.user = None
```

**Page 1 (pages/1_Dashboard.py):**
```python
import streamlit as st

st.set_page_config(page_title="Dashboard", page_icon="📊")

st.title("📊 Dashboard")
st.write("This is the dashboard page")

# Access shared state
if st.session_state.get("user"):
    st.write(f"Welcome back, {st.session_state.user}!")
```

**Page 2 (pages/2_Analytics.py):**
```python
import streamlit as st

st.set_page_config(page_title="Analytics", page_icon="📈")

st.title("📈 Analytics")
st.write("This is the analytics page")

# Add analytics content
```
