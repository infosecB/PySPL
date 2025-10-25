"""
Eventstats Command Examples
"""

from pyspl import SPL


def example_eventstats_basic():
    """Basic eventstats usage"""
    print("=== Basic Eventstats Example ===")

    data = [
        {"name": "Alice", "city": "NYC", "score": 85},
        {"name": "Bob", "city": "LA", "score": 90},
        {"name": "Charlie", "city": "NYC", "score": 78},
        {"name": "David", "city": "SF", "score": 92},
        {"name": "Eve", "city": "LA", "score": 88},
    ]

    spl = SPL(data)

    # Add total count to each event
    result = spl.search('eventstats count')
    print(f"With total count added to each event:")
    for r in result[:2]:  # Show first 2
        print(f"  {r['name']}: count={r['count']}")
    print()

    # Add count by city to each event
    result = spl.search('eventstats count by city')
    print(f"With city count added to each event:")
    for r in result:
        print(f"  {r['name']} ({r['city']}): city_count={r['count']}")
    print()


def example_eventstats_vs_stats():
    """Compare eventstats and stats behavior"""
    print("=== Eventstats vs Stats Comparison ===")

    data = [
        {"name": "Alice", "city": "NYC", "score": 85},
        {"name": "Bob", "city": "NYC", "score": 78},
        {"name": "Charlie", "city": "LA", "score": 92},
    ]

    spl = SPL(data)

    # Stats: Reduces to aggregated groups
    print("Stats (aggregates and groups):")
    result = spl.search('stats avg(score) by city')
    for r in result:
        print(f"  {r}")
    print()

    # Eventstats: Preserves all events, adds aggregated values
    print("Eventstats (preserves all events, adds aggregation):")
    result = spl.search('eventstats avg(score) by city')
    for r in result:
        print(f"  {r['name']} ({r['city']}): score={r['score']}, city_avg={r['avg(score)']}")
    print()


def example_performance_comparison():
    """Compare individual performance to group average"""
    print("=== Performance Comparison Example ===")

    data = [
        {"employee": "Alice", "department": "Sales", "sales": 150000},
        {"employee": "Bob", "department": "Sales", "sales": 120000},
        {"employee": "Charlie", "department": "Engineering", "sales": 80000},
        {"employee": "David", "department": "Engineering", "sales": 90000},
        {"employee": "Eve", "department": "Sales", "sales": 180000},
    ]

    spl = SPL(data)

    # Add department average to each employee
    result = spl.search('eventstats avg(sales) by department | fields employee, department, sales, avg(sales)')

    print("Employee performance vs department average:")
    for r in result:
        performance = "above" if r['sales'] > r['avg(sales)'] else "below"
        diff = abs(r['sales'] - r['avg(sales)'])
        print(f"  {r['employee']} ({r['department']}): ${r['sales']:,} ({performance} avg by ${diff:,.0f})")
    print()


def example_anomaly_detection():
    """Use eventstats for anomaly detection"""
    print("=== Anomaly Detection Example ===")

    data = [
        {"timestamp": "10:00", "server": "web-1", "response_time": 45},
        {"timestamp": "10:01", "server": "web-1", "response_time": 52},
        {"timestamp": "10:02", "server": "web-1", "response_time": 350},  # Anomaly!
        {"timestamp": "10:03", "server": "web-1", "response_time": 48},
        {"timestamp": "10:00", "server": "web-2", "response_time": 38},
        {"timestamp": "10:01", "server": "web-2", "response_time": 41},
        {"timestamp": "10:02", "server": "web-2", "response_time": 39},
    ]

    spl = SPL(data)

    # Add average response time per server to each event
    result = spl.search('eventstats avg(response_time) by server')

    print("Detecting anomalies (>2x average):")
    for r in result:
        if r['response_time'] > 2 * r['avg(response_time)']:
            print(f"  ANOMALY: {r['server']} at {r['timestamp']}: {r['response_time']}ms (avg: {r['avg(response_time)']:.1f}ms)")
    print()


def example_enrichment():
    """Use eventstats to enrich data with group statistics"""
    print("=== Data Enrichment Example ===")

    data = [
        {"product": "Laptop", "category": "Electronics", "price": 999, "units": 10},
        {"product": "Mouse", "category": "Electronics", "price": 25, "units": 50},
        {"product": "Desk", "category": "Furniture", "price": 299, "units": 15},
        {"product": "Chair", "category": "Furniture", "price": 199, "units": 20},
        {"product": "Monitor", "category": "Electronics", "price": 349, "units": 12},
    ]

    spl = SPL(data)

    # Add category statistics to each product
    result = spl.search('eventstats count, avg(price), sum(units) by category | fields product, category, price, avg(price), sum(units)')

    print("Products enriched with category statistics:")
    for r in result:
        print(f"  {r['product']}:")
        print(f"    Category: {r['category']}")
        print(f"    Price: ${r['price']} (category avg: ${r['avg(price)']:.2f})")
        print(f"    Total units in category: {r['sum(units)']}")
    print()


def example_ranking():
    """Use eventstats to calculate rankings"""
    print("=== Ranking Example ===")

    data = [
        {"student": "Alice", "class": "Math", "score": 92},
        {"student": "Bob", "class": "Math", "score": 78},
        {"student": "Charlie", "class": "Math", "score": 85},
        {"student": "David", "class": "Science", "score": 88},
        {"student": "Eve", "class": "Science", "score": 95},
    ]

    spl = SPL(data)

    # Add max score per class to show how far from top
    result = spl.search('eventstats max(score) by class')

    print("Student scores with class maximum:")
    for r in result:
        points_from_top = r['max(score)'] - r['score']
        status = "TOP SCORE!" if points_from_top == 0 else f"{points_from_top} points from top"
        print(f"  {r['student']} ({r['class']}): {r['score']} ({status})")
    print()


if __name__ == '__main__':
    example_eventstats_basic()
    example_eventstats_vs_stats()
    example_performance_comparison()
    example_anomaly_detection()
    example_enrichment()
    example_ranking()
