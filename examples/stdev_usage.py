"""
Examples of using stdev (standard deviation) function
"""

from pyspl import SPL


def example_basic_stdev():
    """Basic stdev usage"""
    print("=== Basic Standard Deviation Example ===")

    data = [
        {"product": "A", "response_time": 100},
        {"product": "A", "response_time": 150},
        {"product": "A", "response_time": 200},
        {"product": "B", "response_time": 90},
        {"product": "B", "response_time": 95},
        {"product": "B", "response_time": 100},
    ]

    spl = SPL(data)

    # Calculate stdev by product
    result = spl.search('stats avg(response_time) as mean stdev(response_time) as std by product')
    print("Response time statistics by product:")
    for r in result:
        print(f"  Product {r['product']}: mean={r['mean']:.1f}ms, stdev={r['std']:.2f}ms")
    print()


def example_quality_control():
    """Using stdev for quality control"""
    print("=== Quality Control Example ===")

    # Manufacturing measurements
    data = [
        {"batch": "Morning", "measurement": 10.1},
        {"batch": "Morning", "measurement": 10.0},
        {"batch": "Morning", "measurement": 10.2},
        {"batch": "Morning", "measurement": 9.9},
        {"batch": "Afternoon", "measurement": 10.5},
        {"batch": "Afternoon", "measurement": 9.5},
        {"batch": "Afternoon", "measurement": 11.0},
        {"batch": "Afternoon", "measurement": 9.0},
    ]

    spl = SPL(data)

    # Check consistency of measurements
    result = spl.search('stats avg(measurement) as mean stdev(measurement) as std by batch')
    print("Batch quality metrics:")
    for r in result:
        consistency = "Consistent" if r['std'] < 0.2 else "Variable"
        print(f"  {r['batch']}: mean={r['mean']:.2f}, stdev={r['std']:.3f} ({consistency})")
    print()


def example_coefficient_of_variation():
    """Calculate coefficient of variation (CV)"""
    print("=== Coefficient of Variation Example ===")

    data = [
        {"stock": "TECH", "price": 150},
        {"stock": "TECH", "price": 160},
        {"stock": "TECH", "price": 140},
        {"stock": "UTIL", "price": 50},
        {"stock": "UTIL", "price": 52},
        {"stock": "UTIL", "price": 48},
    ]

    spl = SPL(data)

    # Calculate CV to compare volatility
    result = spl.search('stats avg(price) as mean stdev(price) as std by stock | eval cv = std / mean * 100')
    print("Stock volatility (Coefficient of Variation):")
    for r in result:
        print(f"  {r['stock']}: mean=${r['mean']:.2f}, stdev=${r['std']:.2f}, CV={r['cv']:.2f}%")
    print()


def example_outlier_detection():
    """Using stdev for outlier detection"""
    print("=== Outlier Detection Example ===")

    data = [
        {"sensor": "temp1", "reading": 20.1},
        {"sensor": "temp1", "reading": 20.3},
        {"sensor": "temp1", "reading": 20.0},
        {"sensor": "temp1", "reading": 25.5},  # Outlier!
        {"sensor": "temp1", "reading": 20.2},
        {"sensor": "temp1", "reading": 19.9},
    ]

    spl = SPL(data)

    # Add mean and stdev to each event, then filter outliers
    result = spl.search('eventstats avg(reading) as mean stdev(reading) as std by sensor')

    print("Detecting outliers (>2 standard deviations from mean):")
    for r in result:
        z_score = abs(r['reading'] - r['mean']) / r['std'] if r['std'] > 0 else 0
        if z_score > 2:
            print(f"  OUTLIER: reading={r['reading']}, z-score={z_score:.2f}")
    print()


def example_performance_comparison():
    """Compare performance consistency across teams"""
    print("=== Performance Consistency Example ===")

    data = [
        {"team": "Alpha", "score": 85},
        {"team": "Alpha", "score": 88},
        {"team": "Alpha", "score": 87},
        {"team": "Beta", "score": 95},
        {"team": "Beta", "score": 70},
        {"team": "Beta", "score": 90},
    ]

    spl = SPL(data)

    # Compare teams
    result = spl.search('stats avg(score) as avg_score stdev(score) as consistency by team | sort -avg_score')
    print("Team performance (lower stdev = more consistent):")
    for r in result:
        print(f"  {r['team']}: avg={r['avg_score']:.1f}, stdev={r['consistency']:.2f}")
    print()


def example_sample_vs_population():
    """Compare sample vs population stdev"""
    print("=== Sample vs Population Stdev ===")

    data = [
        {"value": 10},
        {"value": 20},
        {"value": 30},
    ]

    spl = SPL(data)

    # Compare population and sample stdev
    result = spl.search('stats stdev(value) as pop_stdev stdevs(value) as sample_stdev')
    print("Standard deviation comparison:")
    print(f"  Population stdev: {result[0]['pop_stdev']:.4f}")
    print(f"  Sample stdev: {result[0]['sample_stdev']:.4f}")
    print(f"  (Sample stdev is larger when estimating from a sample)")
    print()


def example_real_world_analytics():
    """Real-world web analytics example"""
    print("=== Web Analytics Example ===")

    data = [
        {"page": "/home", "load_time": 1.2},
        {"page": "/home", "load_time": 1.3},
        {"page": "/home", "load_time": 1.1},
        {"page": "/products", "load_time": 2.5},
        {"page": "/products", "load_time": 3.2},
        {"page": "/products", "load_time": 2.8},
        {"page": "/checkout", "load_time": 5.1},
        {"page": "/checkout", "load_time": 4.9},
        {"page": "/checkout", "load_time": 5.3},
    ]

    spl = SPL(data)

    # Analyze page load time consistency
    result = spl.search('stats count avg(load_time) as avg_time stdev(load_time) as std_time by page | sort -avg_time')
    print("Page load time analysis:")
    for r in result:
        reliability = "Reliable" if r['std_time'] < 0.5 else "Variable"
        print(f"  {r['page']}: avg={r['avg_time']:.2f}s, stdev={r['std_time']:.3f}s ({reliability})")
    print()


if __name__ == '__main__':
    example_basic_stdev()
    example_quality_control()
    example_coefficient_of_variation()
    example_outlier_detection()
    example_performance_comparison()
    example_sample_vs_population()
    example_real_world_analytics()
