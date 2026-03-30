---
name: docusaurus-custom-homepage
description: 'Sub-skill of docusaurus: Custom Homepage (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Custom Homepage (+1)

## Custom Homepage


```jsx
// src/pages/index.js
import React from 'react';
import Layout from '@theme/Layout';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (

*See sub-skills for full details.*

## Plugin Development


```javascript
// plugins/my-plugin/index.js
module.exports = function myPlugin(context, options) {
  return {
    name: 'my-plugin',

    async loadContent() {
      return { data: 'example' };
    },


*See sub-skills for full details.*
