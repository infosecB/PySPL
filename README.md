# PySPL - Splunk SPL for Python Dictionaries

A lightweight Python library that allows you to run Splunk SPL (Search Processing Language) queries against Python dictionaries and lists. No Splunk installation required!

## Features

- **Search & Filter**: Use SPL search syntax to filter data
- **Statistics**: Compute aggregations like count, sum, avg, min, max
- **Eventstats**: Add aggregated values to events while preserving all records
- **Field Operations**: Select, rename, and transform fields
- **Sorting**: Sort results by any field
- **Pipe Chains**: Combine multiple SPL commands using pipes
- **Pure Python**: No external dependencies, works with standard Python dicts

## Installation

```bash
pip install pyspl
```

Or install from source:

```bash
git clone https://github.com/yourusername/pyspl.git
cd pyspl
pip install -e .
```

## Quick Start

```python
from pyspl import SPL

# Your data as a list of dictionaries
data = [
    {"name": "Alice", "age": 30, "city": "NYC", "score": 85},
    {"name": "Bob", "age": 25, "city": "LA", "score": 90},
    {"name": "Charlie", "age": 35, "city": "NYC", "score": 78},
    {"name": "David", "age": 28, "city": "SF", "score": 92},
]

# Create SPL instance
spl = SPL(data)

# Run queries
result = spl.search('city="NYC" | stats avg(score)')
print(result)
# Output: [{'avg(score)': 81.5}]
```

## Supported SPL Commands

### Search / Where
Filter data using conditions:

```python
# Exact match
spl.search('city="NYC"')

# Comparison operators
spl.search('age>30')
spl.search('score>=85')
spl.search('age<=28')

# Not equal
spl.search('city!="LA"')

# Multiple conditions (AND logic)
spl.search('city="NYC" age>25')

# Field exists
spl.search('city=*')
```

### Stats
Compute aggregations:

```python
# Count all records
spl.search('stats count')

# Count by group
spl.search('stats count by city')

# Multiple aggregations (space-separated)
spl.search('stats count avg(age) sum(score) by city')

# With aliases using 'as'
spl.search('stats count as total avg(age) as average by city')

# Mix of aliased and non-aliased
spl.search('stats dc(category) as categories count by user')

# Backward compatible: comma-separated also works
spl.search('stats count, avg(age), sum(score) by city')

# Available functions:
# - count, count(field)
# - sum(field), avg(field), min(field), max(field)
# - stdev(field) - standard deviation (population)
# - stdevp(field) - standard deviation (population, same as stdev)
# - stdevs(field) - standard deviation (sample)
# - values(field) - distinct values
# - list(field) - all values including duplicates
# - dc(field) - distinct count
```

### Eventstats
Add aggregated values to each event (like stats, but preserves all original events):

```python
# Add total count to each event
spl.search('eventstats count')

# Add city-specific count to each event
spl.search('eventstats count by city')

# Add multiple aggregations per group (space-separated)
spl.search('eventstats avg(score) max(score) by city')

# With aliases
spl.search('eventstats avg(score) as city_avg by city')

# Compare individual values to group averages
data = [
    {"name": "Alice", "city": "NYC", "score": 85},
    {"name": "Bob", "city": "NYC", "score": 78},
    {"name": "Charlie", "city": "LA", "score": 92}
]
spl = SPL(data)
result = spl.search('eventstats avg(score) as city_avg by city')
# Result: Each event now has city_avg for their city
# Alice: {"name": "Alice", "city": "NYC", "score": 85, "city_avg": 81.5}
# Bob: {"name": "Bob", "city": "NYC", "score": 78, "city_avg": 81.5}
# Charlie: {"name": "Charlie", "city": "LA", "score": 92, "city_avg": 92.0}
```

### Fields
Select or exclude fields:

```python
# Include only specific fields
spl.search('fields name, age')

# Exclude fields
spl.search('fields - score')
```

### Rename
Rename fields:

```python
spl.search('rename name as full_name, city as location')
```

### Eval
Create or modify fields:

```python
# Arithmetic
spl.search('eval total = price * quantity')

# Conditional
spl.search('eval category = if(price > 100, "expensive", "cheap")')

# Constants
spl.search('eval status = "active"')
```

### Sort
Sort results:

```python
# Ascending
spl.search('sort age')

# Descending
spl.search('sort -score')

# Multiple fields
spl.search('sort city, -age')
```

### Head / Tail
Limit results:

```python
# First 10 records (default)
spl.search('head')

# First 5 records
spl.search('head 5')

# Last 3 records
spl.search('tail 3')
```

## Complex Examples

### Web Server Log Analysis

```python
from pyspl import SPL

logs = [
    {"timestamp": "2025-01-01 10:00", "status": 200, "method": "GET", "response_time": 45},
    {"timestamp": "2025-01-01 10:01", "status": 404, "method": "GET", "response_time": 12},
    {"timestamp": "2025-01-01 10:02", "status": 200, "method": "POST", "response_time": 123},
    {"timestamp": "2025-01-01 10:03", "status": 500, "method": "POST", "response_time": 567},
    {"timestamp": "2025-01-01 10:04", "status": 200, "method": "GET", "response_time": 34},
]

spl = SPL(logs)

# Average response time by status code
result = spl.search('stats avg(response_time) by status | sort -avg(response_time)')
print(result)

# Count errors
result = spl.search('status>=400 | stats count by status')
print(result)

# Slow requests
result = spl.search('response_time>100 | fields timestamp, method, response_time')
print(result)
```

### E-commerce Analytics

```python
from pyspl import SPL

sales = [
    {"product": "Laptop", "category": "Electronics", "price": 999, "quantity": 2},
    {"product": "Mouse", "category": "Electronics", "price": 25, "quantity": 5},
    {"product": "Desk", "category": "Furniture", "price": 299, "quantity": 1},
    {"product": "Chair", "category": "Furniture", "price": 199, "quantity": 4},
]

spl = SPL(sales)

# Calculate total revenue per product
result = spl.search('eval revenue = price * quantity | stats sum(revenue) by category | sort -sum(revenue)')
print(result)

# Find expensive items
result = spl.search('price>200 | eval type = if(price>500, "premium", "standard") | fields product, price, type')
print(result)
```

### User Activity Tracking

```python
from pyspl import SPL

activities = [
    {"user": "alice", "action": "login", "duration": 120},
    {"user": "bob", "action": "login", "duration": 95},
    {"user": "alice", "action": "search", "duration": 45},
    {"user": "charlie", "action": "search", "duration": 60},
    {"user": "alice", "action": "logout", "duration": 10},
]

spl = SPL(activities)

# Most active users
result = spl.search('stats count by user | sort -count | head 3')
print(result)

# Average session duration per action
result = spl.search('stats avg(duration) by action')
print(result)

# Alice's activity summary
result = spl.search('user="alice" | stats count, sum(duration)')
print(result)
```

## Piping Commands

Chain multiple commands together using pipes:

```python
spl.search('status=200 | eval fast = if(response_time < 50, "yes", "no") | stats count by fast')

spl.search('city="NYC" | stats avg(age), count by status | sort -count | head 5')

spl.search('price>50 | eval category = if(price>100, "high", "medium") | stats sum(price) by category | fields category, sum(price)')
```

## API Reference

### SPL Class

```python
SPL(data: Union[List[Dict], Dict])
```

**Parameters:**
- `data`: A dictionary or list of dictionaries to query

**Methods:**
- `search(query: str) -> List[Dict]`: Execute an SPL query and return results

## Running Tests

```bash
python -m unittest discover tests -v
```

## Limitations

- This is a simplified implementation of SPL, not all Splunk features are supported
- Eval expressions use Python's `eval()` with restricted context (be cautious with untrusted input)
- Regular expressions and advanced SPL features are not yet implemented
- Time-based functions are not yet supported

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/infosecB/PySPL.git
cd PySPL
```

2. Install in development mode:
```bash
pip install -e .
```

3. Run tests:
```bash
python -m unittest discover tests -v
```

### Releasing a New Version

This project uses GitHub Actions for automated releases to PyPI. Here's how to release a new version:

1. **Update the version number** in both files:
   - `setup.py` (line 12: `version="X.Y.Z"`)
   - `pyproject.toml` (line 6: `version = "X.Y.Z"`)

2. **Commit the version changes**:
   ```bash
   git add setup.py pyproject.toml
   git commit -m "Bump version to X.Y.Z"
   git push
   ```

3. **Create a new release on GitHub**:
   - Go to https://github.com/infosecB/PySPL/releases/new
   - Create a new tag: `vX.Y.Z` (e.g., `v0.2.0`)
   - Set the release title: `vX.Y.Z`
   - Add release notes describing the changes
   - Click "Publish release"

4. **Automated publishing**:
   - The GitHub Action will automatically build and publish to PyPI
   - Monitor the progress at: https://github.com/infosecB/PySPL/actions

**Note**: Before the first release, you need to configure PyPI Trusted Publishing:
1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - PyPI Project Name: `pyspl`
   - Owner: `infosecB`
   - Repository name: `PySPL`
   - Workflow name: `publish.yml`
   - Environment name: (leave blank)

## License

MIT License - See LICENSE file for details

## Acknowledgments

Inspired by Splunk's Search Processing Language (SPL). This is an independent implementation and is not affiliated with Splunk Inc.
