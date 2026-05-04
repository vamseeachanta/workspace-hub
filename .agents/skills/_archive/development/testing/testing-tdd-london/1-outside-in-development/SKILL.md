---
name: testing-tdd-london-1-outside-in-development
description: 'Sub-skill of testing-tdd-london: 1. Outside-In Development (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Outside-In Development (+2)

## 1. Outside-In Development


```typescript
// Start with acceptance test (outermost layer)
describe('User Registration Feature', () => {
  it('should register new user successfully', async () => {
    // Mock all collaborators
    const mockRepository = {
      save: jest.fn().mockResolvedValue({ id: '123', email: 'test@example.com' }),
      findByEmail: jest.fn().mockResolvedValue(null)
    };


*See sub-skills for full details.*

## 2. Interaction Testing


```typescript
describe('Order Processing', () => {
  it('should follow proper workflow interactions', async () => {
    const mockPayment = { charge: jest.fn().mockResolvedValue({ success: true }) };
    const mockInventory = { reserve: jest.fn().mockResolvedValue(true) };
    const mockShipping = { schedule: jest.fn().mockResolvedValue({ trackingId: 'ABC' }) };

    const service = new OrderService(mockPayment, mockInventory, mockShipping);
    await service.processOrder(order);


*See sub-skills for full details.*

## 3. Contract Definition Through Mocks


```typescript
// Define contracts for collaborators
const userServiceContract = {
  register: {
    input: { email: 'string', password: 'string' },
    output: { success: 'boolean', id: 'string' },
    collaborators: ['UserRepository', 'NotificationService'],
    interactions: [
      { method: 'findByEmail', args: ['email'], returns: 'null|User' },
      { method: 'save', args: ['User'], returns: 'User' },

*See sub-skills for full details.*
