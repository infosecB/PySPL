"""
E-commerce Sales Analytics Example
"""

from pyspl import SPL


def analyze_sales():
    """Analyze e-commerce sales data"""

    # Sample sales data
    sales = [
        {"order_id": "ORD001", "product": "Laptop", "category": "Electronics", "price": 999, "quantity": 2, "customer": "Alice"},
        {"order_id": "ORD002", "product": "Mouse", "category": "Electronics", "price": 25, "quantity": 5, "customer": "Bob"},
        {"order_id": "ORD003", "product": "Desk", "category": "Furniture", "price": 299, "quantity": 1, "customer": "Charlie"},
        {"order_id": "ORD004", "product": "Chair", "category": "Furniture", "price": 199, "quantity": 4, "customer": "Alice"},
        {"order_id": "ORD005", "product": "Monitor", "category": "Electronics", "price": 349, "quantity": 2, "customer": "David"},
        {"order_id": "ORD006", "product": "Keyboard", "category": "Electronics", "price": 75, "quantity": 3, "customer": "Bob"},
        {"order_id": "ORD007", "product": "Bookshelf", "category": "Furniture", "price": 149, "quantity": 2, "customer": "Eve"},
        {"order_id": "ORD008", "product": "Webcam", "category": "Electronics", "price": 89, "quantity": 1, "customer": "Charlie"},
        {"order_id": "ORD009", "product": "Lamp", "category": "Furniture", "price": 45, "quantity": 3, "customer": "Alice"},
        {"order_id": "ORD010", "product": "Headphones", "category": "Electronics", "price": 129, "quantity": 2, "customer": "David"},
    ]

    spl = SPL(sales)

    print("=== E-commerce Sales Analytics ===\n")

    # 1. Total revenue by category
    print("1. Revenue by Category:")
    result = spl.search('eval revenue = price * quantity | stats sum(revenue) by category | sort -sum(revenue)')
    for row in result:
        print(f"   {row['category']}: ${row['sum(revenue)']:,.2f}")
    print()

    # 2. Top selling products
    print("2. Top Selling Products (by quantity):")
    result = spl.search('stats sum(quantity) by product | sort -sum(quantity) | head 5')
    for row in result:
        print(f"   {row['product']}: {row['sum(quantity)']} units")
    print()

    # 3. Best customers by total spend
    print("3. Top Customers by Total Spend:")
    result = spl.search('eval total = price * quantity | stats sum(total) by customer | sort -sum(total) | head 5')
    for row in result:
        print(f"   {row['customer']}: ${row['sum(total)']:,.2f}")
    print()

    # 4. Average order value
    print("4. Average Order Value:")
    result = spl.search('eval order_value = price * quantity | stats avg(order_value)')
    print(f"   Average: ${result[0]['avg(order_value)']:,.2f}")
    print()

    # 5. Price tiers
    print("5. Product Price Distribution:")
    result = spl.search('eval tier = if(price < 100, "Budget", if(price < 300, "Mid-Range", "Premium")) | stats count by tier')
    for row in result:
        print(f"   {row['tier']}: {row['count']} products")
    print()

    # 6. High-value orders (>$500)
    print("6. High-Value Orders (>$500):")
    result = spl.search('eval order_total = price * quantity | where order_total>500 | fields order_id, product, order_total | sort -order_total')
    for row in result:
        print(f"   {row['order_id']}: {row['product']} - ${row['order_total']:,.2f}")
    print()

    # 7. Category performance metrics
    print("7. Category Performance Metrics:")
    result = spl.search('eval revenue = price * quantity | stats count, sum(revenue), avg(revenue) by category')
    for row in result:
        print(f"   {row['category']}:")
        print(f"      Orders: {row['count']}")
        print(f"      Total Revenue: ${row['sum(revenue)']:,.2f}")
        print(f"      Avg Order Value: ${row['avg(revenue)']:,.2f}")
    print()

    # 8. Customer purchase frequency
    print("8. Customer Purchase Frequency:")
    result = spl.search('stats count by customer | sort -count')
    for row in result:
        print(f"   {row['customer']}: {row['count']} orders")
    print()

    # 9. Product revenue ranking
    print("9. Product Revenue Ranking:")
    result = spl.search('eval revenue = price * quantity | stats sum(revenue) by product | sort -sum(revenue) | head 5')
    for row in result:
        print(f"   {row['product']}: ${row['sum(revenue)']:,.2f}")
    print()

    # 10. Electronics vs Furniture comparison
    print("10. Category Comparison:")
    result = spl.search('eval revenue = price * quantity | stats count, sum(revenue), avg(price), sum(quantity) by category')
    for row in result:
        print(f"   {row['category']}:")
        print(f"      Orders: {row['count']}")
        print(f"      Revenue: ${row['sum(revenue)']:,.2f}")
        print(f"      Avg Price: ${row['avg(price)']:,.2f}")
        print(f"      Total Units: {row['sum(quantity)']}")
    print()


if __name__ == '__main__':
    analyze_sales()
