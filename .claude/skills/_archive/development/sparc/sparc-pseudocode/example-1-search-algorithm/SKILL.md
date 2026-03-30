---
name: sparc-pseudocode-example-1-search-algorithm
description: 'Sub-skill of sparc-pseudocode: Example 1: Search Algorithm (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Search Algorithm (+2)

## Example 1: Search Algorithm


```
ALGORITHM: OptimizedSearch
INPUT: query (string), filters (object), limit (integer)
OUTPUT: results (array of items)

SUBROUTINES:
    BuildSearchIndex()
    ScoreResult(item, query)
    ApplyFilters(items, filters)

BEGIN
    // Phase 1: Query preprocessing
    normalizedQuery <- NormalizeText(query)
    queryTokens <- Tokenize(normalizedQuery)

    // Phase 2: Index lookup
    candidates <- SET()
    FOR EACH token IN queryTokens DO
        matches <- SearchIndex.get(token)
        candidates <- candidates UNION matches
    END FOR

    // Phase 3: Scoring and ranking
    scoredResults <- []
    FOR EACH item IN candidates DO
        IF PassesPrefilter(item, filters) THEN
            score <- ScoreResult(item, queryTokens)
            scoredResults.append({item: item, score: score})
        END IF
    END FOR

    // Phase 4: Sort and filter
    scoredResults.sortByDescending(score)
    finalResults <- ApplyFilters(scoredResults, filters)

    // Phase 5: Pagination
    RETURN finalResults.slice(0, limit)
END

SUBROUTINE: ScoreResult
INPUT: item, queryTokens
OUTPUT: score (float)

BEGIN
    score <- 0

    // Title match (highest weight)
    titleMatches <- CountTokenMatches(item.title, queryTokens)
    score <- score + (titleMatches * 10)

    // Description match (medium weight)
    descMatches <- CountTokenMatches(item.description, queryTokens)
    score <- score + (descMatches * 5)

    // Tag match (lower weight)
    tagMatches <- CountTokenMatches(item.tags, queryTokens)
    score <- score + (tagMatches * 2)

    // Boost by recency
    daysSinceUpdate <- (CurrentDate - item.updatedAt).days
    recencyBoost <- 1 / (1 + daysSinceUpdate * 0.1)
    score <- score * recencyBoost

    RETURN score
END
```


## Example 2: Design Patterns


```
PATTERN: Strategy Pattern

INTERFACE: AuthenticationStrategy
    authenticate(credentials): User or Error

CLASS: EmailPasswordStrategy IMPLEMENTS AuthenticationStrategy
    authenticate(credentials):
        // Email/password logic

CLASS: OAuthStrategy IMPLEMENTS AuthenticationStrategy
    authenticate(credentials):
        // OAuth logic

CLASS: AuthenticationContext
    strategy: AuthenticationStrategy

    executeAuthentication(credentials):
        RETURN strategy.authenticate(credentials)

---

PATTERN: Observer Pattern

CLASS: EventEmitter
    listeners: Map<eventName, List<callback>>

    on(eventName, callback):
        IF NOT listeners.has(eventName) THEN
            listeners.set(eventName, [])
        END IF
        listeners.get(eventName).append(callback)

    emit(eventName, data):
        IF listeners.has(eventName) THEN
            FOR EACH callback IN listeners.get(eventName) DO
                callback(data)
            END FOR
        END IF
```


## Example 3: Complexity Analysis


```
ANALYSIS: User Authentication Flow

Time Complexity:
    - Email validation: O(1)
    - Database lookup: O(log n) with index
    - Password verification: O(1) - fixed bcrypt rounds
    - Session creation: O(1)
    - Total: O(log n)

Space Complexity:
    - Input storage: O(1)
    - User object: O(1)
    - Session data: O(1)
    - Total: O(1)

ANALYSIS: Search Algorithm

Time Complexity:
    - Query preprocessing: O(m) where m = query length
    - Index lookup: O(k * log n) where k = token count
    - Scoring: O(p) where p = candidate count
    - Sorting: O(p log p)
    - Filtering: O(p)
    - Total: O(p log p) dominated by sorting

Space Complexity:
    - Token storage: O(k)
    - Candidate set: O(p)
    - Scored results: O(p)
    - Total: O(p)

Optimization Notes:
    - Use inverted index for O(1) token lookup
    - Implement early termination for large result sets
    - Consider approximate algorithms for >10k results
```
