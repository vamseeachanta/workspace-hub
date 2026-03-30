---
name: streamlit-common-issues
description: 'Sub-skill of streamlit: Common Issues.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: App reruns on every interaction**
```python
# Use forms to batch inputs
with st.form("my_form"):
    input1 = st.text_input("Input")
    submit = st.form_submit_button()
```

**Issue: Slow data loading**
```python
# Add caching
@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv("large_file.csv")
```

**Issue: Memory issues with large files**
```python
# Use chunking
@st.cache_data
def load_large_file(path, nrows=10000):
    return pd.read_csv(path, nrows=nrows)
```

**Issue: Widget state lost on rerun**
```python
# Persist in session state
if "value" not in st.session_state:
    st.session_state.value = default_value

# Use key parameter
st.text_input("Name", key="user_name")
```
