---
name: windmill-3-go-scripts
description: 'Sub-skill of windmill: 3. Go Scripts.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Go Scripts

## 3. Go Scripts


```go
// scripts/performance/batch_processor.go
// High-performance batch processing using Go.

package inner

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	wmill "github.com/windmill-labs/windmill-go-client"
)

type BatchConfig struct {
	BatchSize     int    `json:"batch_size"`
	Concurrency   int    `json:"concurrency"`
	RetryAttempts int    `json:"retry_attempts"`
	TimeoutSecs   int    `json:"timeout_secs"`
}

type ProcessResult struct {
	TotalItems     int            `json:"total_items"`
	Successful     int            `json:"successful"`
	Failed         int            `json:"failed"`
	ProcessingTime float64        `json:"processing_time_seconds"`
	Errors         []ProcessError `json:"errors,omitempty"`
}

type ProcessError struct {
	ItemID string `json:"item_id"`
	Error  string `json:"error"`
}

func Main(
	items []map[string]interface{},
	config BatchConfig,
) (*ProcessResult, error) {
	startTime := time.Now()

	// Set defaults
	if config.BatchSize == 0 {
		config.BatchSize = 100
	}
	if config.Concurrency == 0 {
		config.Concurrency = 4
	}
	if config.RetryAttempts == 0 {
		config.RetryAttempts = 3
	}
	if config.TimeoutSecs == 0 {
		config.TimeoutSecs = 30
	}

	// Get API credentials
	ctx := context.Background()
	resource, err := wmill.GetResource("u/admin/processing_api")
	if err != nil {
		return nil, fmt.Errorf("failed to get resource: %w", err)
	}

	apiKey := resource["api_key"].(string)

	result := &ProcessResult{
		TotalItems: len(items),
	}

	var mu sync.Mutex
	var wg sync.WaitGroup

	// Create worker pool
	itemChan := make(chan map[string]interface{}, config.BatchSize)
	errorChan := make(chan ProcessError, len(items))

	// Start workers
	for i := 0; i < config.Concurrency; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for item := range itemChan {
				err := processItem(ctx, item, apiKey, config)
				mu.Lock()
				if err != nil {
					result.Failed++
					errorChan <- ProcessError{
						ItemID: fmt.Sprintf("%v", item["id"]),
						Error:  err.Error(),
					}
				} else {
					result.Successful++
				}
				mu.Unlock()
			}
		}()
	}

	// Send items to workers
	for _, item := range items {
		itemChan <- item
	}
	close(itemChan)

	// Wait for all workers to complete
	wg.Wait()
	close(errorChan)

	// Collect errors
	for err := range errorChan {
		result.Errors = append(result.Errors, err)
	}

	result.ProcessingTime = time.Since(startTime).Seconds()

	return result, nil
}

func processItem(
	ctx context.Context,
	item map[string]interface{},
	apiKey string,
	config BatchConfig,
) error {
	var lastErr error

	for attempt := 1; attempt <= config.RetryAttempts; attempt++ {
		ctx, cancel := context.WithTimeout(ctx, time.Duration(config.TimeoutSecs)*time.Second)
		defer cancel()

		// Process item (simplified - real implementation would make API calls)
		select {
		case <-ctx.Done():
			lastErr = ctx.Err()
		default:
			// Simulate processing
			time.Sleep(10 * time.Millisecond)

			// Validate item
			if _, ok := item["id"]; !ok {
				return fmt.Errorf("missing required field: id")
			}

			return nil
		}

		// Exponential backoff before retry
		if attempt < config.RetryAttempts {
			time.Sleep(time.Duration(1<<attempt) * time.Second)
		}
	}

	return fmt.Errorf("failed after %d attempts: %w", config.RetryAttempts, lastErr)
}
```
