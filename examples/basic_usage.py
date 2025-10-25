"""
Basic Usage Examples for PySPL
"""

from pyspl import SPL


def example_simple_search():
    """Simple search and filtering"""
    print("=== Simple Search Example ===")

    data = [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "LA"},
        {"name": "Charlie", "age": 35, "city": "NYC"},
        {"name": "David", "age": 28, "city": "SF"},
    ]

    spl = SPL(data)

    # Find all people in NYC
    result = spl.search('city="NYC"')
    print(f"People in NYC: {result}")

    # Find people older than 28
    result = spl.search('age>28')
    print(f"People older than 28: {result}")

    # Multiple conditions
    result = spl.search('city="NYC" age>=30')
    print(f"People in NYC aged 30+: {result}")
    print()


def example_statistics():
    """Statistical aggregations"""
    print("=== Statistics Example ===")

    data = [
        {"product": "Laptop", "price": 999, "quantity": 2},
        {"product": "Mouse", "price": 25, "quantity": 5},
        {"product": "Keyboard", "price": 75, "quantity": 3},
        {"product": "Monitor", "price": 299, "quantity": 2},
    ]

    spl = SPL(data)

    # Count products
    result = spl.search('stats count')
    print(f"Total products: {result}")

    # Average price
    result = spl.search('stats avg(price)')
    print(f"Average price: {result}")

    # Multiple aggregations
    result = spl.search('stats min(price), max(price), avg(price)')
    print(f"Price statistics: {result}")
    print()


def example_grouping():
    """Group by aggregations"""
    print("=== Group By Example ===")

    data = [
        {"city": "NYC", "temperature": 72, "humidity": 65},
        {"city": "LA", "temperature": 85, "humidity": 45},
        {"city": "NYC", "temperature": 68, "humidity": 70},
        {"city": "SF", "temperature": 65, "humidity": 75},
        {"city": "LA", "temperature": 88, "humidity": 40},
    ]

    spl = SPL(data)

    # Count readings per city
    result = spl.search('stats count by city')
    print(f"Readings per city: {result}")

    # Average temperature by city
    result = spl.search('stats avg(temperature), avg(humidity) by city')
    print(f"Climate by city: {result}")
    print()


def example_field_operations():
    """Field selection and renaming"""
    print("=== Field Operations Example ===")

    data = [
        {"first": "Alice", "last": "Smith", "age": 30, "internal_id": 12345},
        {"first": "Bob", "last": "Jones", "age": 25, "internal_id": 67890},
    ]

    spl = SPL(data)

    # Select specific fields
    result = spl.search('fields first, last, age')
    print(f"Selected fields: {result}")

    # Exclude fields
    result = spl.search('fields - internal_id')
    print(f"Excluding internal_id: {result}")

    # Rename fields
    result = spl.search('rename first as first_name, last as last_name')
    print(f"Renamed fields: {result}")
    print()


def example_eval():
    """Creating computed fields"""
    print("=== Eval Example ===")

    data = [
        {"item": "Widget A", "price": 10, "quantity": 100},
        {"item": "Widget B", "price": 25, "quantity": 50},
        {"item": "Widget C", "price": 5, "quantity": 200},
    ]

    spl = SPL(data)

    # Calculate total value
    result = spl.search('eval total_value = price * quantity | fields item, total_value')
    print(f"Total values: {result}")

    # Conditional field
    result = spl.search('eval category = if(price > 15, "premium", "standard") | fields item, price, category')
    print(f"Categorized items: {result}")
    print()


def example_sorting():
    """Sorting results"""
    print("=== Sorting Example ===")

    data = [
        {"name": "Charlie", "score": 78},
        {"name": "Alice", "score": 92},
        {"name": "Bob", "score": 85},
    ]

    spl = SPL(data)

    # Sort by score (ascending)
    result = spl.search('sort score')
    print(f"Sorted by score (asc): {result}")

    # Sort by score (descending)
    result = spl.search('sort -score')
    print(f"Sorted by score (desc): {result}")
    print()


def example_complex_pipeline():
    """Complex multi-command pipeline"""
    print("=== Complex Pipeline Example ===")

    data = [
        {"timestamp": "2025-01-01", "user": "alice", "action": "login", "duration": 120},
        {"timestamp": "2025-01-01", "user": "bob", "action": "login", "duration": 95},
        {"timestamp": "2025-01-01", "user": "alice", "action": "search", "duration": 45},
        {"timestamp": "2025-01-01", "user": "bob", "action": "search", "duration": 60},
        {"timestamp": "2025-01-01", "user": "charlie", "action": "login", "duration": 110},
    ]

    spl = SPL(data)

    # Find most active users
    result = spl.search('stats count, sum(duration) by user | sort -count | head 3')
    print(f"Most active users: {result}")

    # Average login time
    result = spl.search('action="login" | stats avg(duration) | eval avg_minutes = avg(duration) / 60')
    print(f"Average login duration: {result}")

    # Categorize by duration
    result = spl.search('eval speed = if(duration > 100, "slow", "fast") | stats count by speed')
    print(f"Speed distribution: {result}")
    print()


if __name__ == '__main__':
    example_simple_search()
    example_statistics()
    example_grouping()
    example_field_operations()
    example_eval()
    example_sorting()
    example_complex_pipeline()
