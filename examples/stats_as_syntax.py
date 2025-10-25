"""
Examples of using the 'as' syntax in stats and eventstats commands
"""

from pyspl import SPL


def example_basic_as_syntax():
    """Basic usage of 'as' syntax"""
    print("=== Basic 'as' Syntax Example ===")

    data = [
        {"user": "alice", "category": "electronics", "price": 100},
        {"user": "alice", "category": "books", "price": 50},
        {"user": "bob", "category": "electronics", "price": 200},
        {"user": "charlie", "category": "books", "price": 30},
    ]

    spl = SPL(data)

    # Simple alias
    result = spl.search('stats count as total by user')
    print("count as total:")
    for r in result:
        print(f"  {r}")
    print()


def example_multiple_aliases():
    """Multiple aggregations with aliases"""
    print("=== Multiple Aliases Example ===")

    data = [
        {"user": "alice", "category": "electronics", "price": 100},
        {"user": "alice", "category": "books", "price": 50},
        {"user": "bob", "category": "electronics", "price": 200},
        {"user": "bob", "category": "sports", "price": 75},
    ]

    spl = SPL(data)

    # Multiple aliases
    result = spl.search('stats count as purchases sum(price) as revenue avg(price) as avg_price by user')
    print("Multiple aggregations with aliases:")
    for r in result:
        print(f"  User {r['user']}: {r['purchases']} purchases, ${r['revenue']} revenue, ${r['avg_price']:.2f} avg")
    print()


def example_user_query():
    """The user's exact query style"""
    print("=== User Query Style: dc(category) as category count by user ===")

    data = [
        {"user": "alice", "category": "electronics"},
        {"user": "alice", "category": "books"},
        {"user": "alice", "category": "electronics"},
        {"user": "bob", "category": "electronics"},
        {"user": "bob", "category": "sports"},
        {"user": "charlie", "category": "books"},
    ]

    spl = SPL(data)

    # User's exact syntax
    result = spl.search('stats dc(category) as category count by user')
    print("Results:")
    for r in result:
        print(f"  User {r['user']}: {r['category']} unique categories, {r['count']} total events")
    print()


def example_space_separated():
    """Space-separated aggregations (no commas needed)"""
    print("=== Space-Separated Aggregations (No Commas) ===")

    data = [
        {"team": "A", "score": 85},
        {"team": "A", "score": 90},
        {"team": "B", "score": 78},
        {"team": "B", "score": 82},
    ]

    spl = SPL(data)

    # No commas - just spaces
    result = spl.search('stats count avg(score) min(score) max(score) by team')
    print("Space-separated aggregations:")
    for r in result:
        print(f"  Team {r['team']}: count={r['count']}, avg={r['avg(score)']}, min={r['min(score)']}, max={r['max(score)']}")
    print()


def example_eventstats_with_alias():
    """Eventstats with aliases"""
    print("=== Eventstats with Aliases ===")

    data = [
        {"employee": "Alice", "dept": "Sales", "sales": 50000},
        {"employee": "Bob", "dept": "Sales", "sales": 45000},
        {"employee": "Charlie", "dept": "Engineering", "sales": 30000},
        {"employee": "David", "dept": "Engineering", "sales": 35000},
    ]

    spl = SPL(data)

    # Add department average with alias
    result = spl.search('eventstats avg(sales) as dept_avg by dept')
    print("Employee performance vs department average:")
    for r in result:
        diff = r['sales'] - r['dept_avg']
        status = "above" if diff > 0 else "below" if diff < 0 else "at"
        print(f"  {r['employee']}: ${r['sales']:,} ({status} dept avg of ${r['dept_avg']:,.0f})")
    print()


def example_mixed_syntax():
    """Mix of aliased and non-aliased aggregations"""
    print("=== Mixed Aliased and Non-Aliased ===")

    data = [
        {"product": "Laptop", "category": "Electronics", "price": 999, "quantity": 5},
        {"product": "Mouse", "category": "Electronics", "price": 25, "quantity": 50},
        {"product": "Desk", "category": "Furniture", "price": 299, "quantity": 10},
    ]

    spl = SPL(data)

    # Mix: some with aliases, some without
    result = spl.search('stats count as products sum(quantity) avg(price) as avg_price by category')
    print("Mixed syntax results:")
    for r in result:
        print(f"  {r['category']}: {r['products']} products, {r['sum(quantity)']} units, ${r['avg_price']:.2f} avg price")
    print()


def example_complex_pipeline():
    """Complex pipeline with aliases"""
    print("=== Complex Pipeline with Aliases ===")

    data = [
        {"timestamp": "10:00", "user": "alice", "action": "login", "duration": 120},
        {"timestamp": "10:01", "user": "alice", "action": "search", "duration": 45},
        {"timestamp": "10:02", "user": "bob", "action": "login", "duration": 95},
        {"timestamp": "10:03", "user": "bob", "action": "search", "duration": 60},
        {"timestamp": "10:04", "user": "charlie", "action": "login", "duration": 110},
    ]

    spl = SPL(data)

    # Complex query with filtering, stats with aliases, and sorting
    result = spl.search('action="login" | stats count as logins avg(duration) as avg_time by user | sort -avg_time')
    print("User login statistics (sorted by average time):")
    for r in result:
        print(f"  {r['user']}: {r['logins']} logins, {r['avg_time']:.1f}s avg time")
    print()


if __name__ == '__main__':
    example_basic_as_syntax()
    example_multiple_aliases()
    example_user_query()
    example_space_separated()
    example_eventstats_with_alias()
    example_mixed_syntax()
    example_complex_pipeline()
