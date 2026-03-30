---
name: streamlit-8-advanced-features
description: 'Sub-skill of streamlit: 8. Advanced Features.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 8. Advanced Features

## 8. Advanced Features


**Status and Progress:**
```python
import streamlit as st
import time

# Progress bar
progress = st.progress(0, text="Processing...")
for i in range(100):
    time.sleep(0.01)
    progress.progress(i + 1, text=f"Processing... {i+1}%")

# Spinner
with st.spinner("Loading data..."):
    time.sleep(2)
st.success("Done!")

# Status messages
st.success("Operation successful!")
st.info("This is informational")
st.warning("Warning: Check your inputs")
st.error("An error occurred")
st.exception(ValueError("Example exception"))

# Toast notifications
st.toast("Data saved!", icon="✅")

# Balloons and snow
st.balloons()
st.snow()
```

**Chat Interface:**
```python
import streamlit as st
import time

st.title("Chat Demo")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        response = f"You said: {prompt}"
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

**Data Editor:**
```python
import streamlit as st
import pandas as pd

# Editable dataframe
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Active": [True, False, True]
})

edited_df = st.data_editor(
    df,
    num_rows="dynamic",  # Allow adding/deleting rows
    column_config={
        "Name": st.column_config.TextColumn("Name", required=True),
        "Age": st.column_config.NumberColumn("Age", min_value=0, max_value=120),
        "Active": st.column_config.CheckboxColumn("Active")
    }
)

if st.button("Save changes"):
    st.write("Saved:", edited_df)
```
