"""
Web Server Log Analysis Example
"""

from pyspl import SPL


def analyze_web_logs():
    """Analyze web server access logs"""

    # Sample web server logs
    logs = [
        {"timestamp": "2025-01-01 10:00:00", "ip": "192.168.1.1", "method": "GET", "path": "/api/users", "status": 200, "response_time": 45, "user_agent": "Chrome"},
        {"timestamp": "2025-01-01 10:00:05", "ip": "192.168.1.2", "method": "GET", "path": "/api/products", "status": 200, "response_time": 32, "user_agent": "Firefox"},
        {"timestamp": "2025-01-01 10:00:10", "ip": "192.168.1.1", "method": "POST", "path": "/api/login", "status": 200, "response_time": 123, "user_agent": "Chrome"},
        {"timestamp": "2025-01-01 10:00:15", "ip": "192.168.1.3", "method": "GET", "path": "/api/invalid", "status": 404, "response_time": 12, "user_agent": "Safari"},
        {"timestamp": "2025-01-01 10:00:20", "ip": "192.168.1.2", "method": "POST", "path": "/api/data", "status": 500, "response_time": 567, "user_agent": "Firefox"},
        {"timestamp": "2025-01-01 10:00:25", "ip": "192.168.1.4", "method": "GET", "path": "/api/users", "status": 200, "response_time": 34, "user_agent": "Chrome"},
        {"timestamp": "2025-01-01 10:00:30", "ip": "192.168.1.1", "method": "GET", "path": "/api/products", "status": 200, "response_time": 28, "user_agent": "Chrome"},
        {"timestamp": "2025-01-01 10:00:35", "ip": "192.168.1.5", "method": "POST", "path": "/api/login", "status": 401, "response_time": 15, "user_agent": "Mobile"},
        {"timestamp": "2025-01-01 10:00:40", "ip": "192.168.1.3", "method": "GET", "path": "/api/users", "status": 200, "response_time": 41, "user_agent": "Safari"},
        {"timestamp": "2025-01-01 10:00:45", "ip": "192.168.1.2", "method": "DELETE", "path": "/api/data/123", "status": 204, "response_time": 89, "user_agent": "Firefox"},
    ]

    spl = SPL(logs)

    print("=== Web Server Log Analysis ===\n")

    # 1. Status code distribution
    print("1. Status Code Distribution:")
    result = spl.search('stats count by status | sort -count')
    for row in result:
        print(f"   Status {row['status']}: {row['count']} requests")
    print()

    # 2. Average response time by endpoint
    print("2. Average Response Time by Endpoint:")
    result = spl.search('stats avg(response_time) by path | sort -avg(response_time)')
    for row in result:
        print(f"   {row['path']}: {row['avg(response_time)']:.2f}ms")
    print()

    # 3. Error rate
    print("3. Error Analysis:")
    total = spl.search('stats count')
    errors = spl.search('status>=400 | stats count')
    print(f"   Total requests: {total[0]['count']}")
    print(f"   Errors (4xx/5xx): {errors[0]['count']}")
    print()

    # 4. Slow requests (>100ms)
    print("4. Slow Requests (>100ms):")
    result = spl.search('response_time>100 | fields timestamp, method, path, response_time | sort -response_time')
    for row in result:
        print(f"   {row['timestamp']} - {row['method']} {row['path']} - {row['response_time']}ms")
    print()

    # 5. Top IPs by request count
    print("5. Top IP Addresses:")
    result = spl.search('stats count by ip | sort -count | head 5')
    for row in result:
        print(f"   {row['ip']}: {row['count']} requests")
    print()

    # 6. Request method distribution
    print("6. HTTP Method Distribution:")
    result = spl.search('stats count by method | sort -count')
    for row in result:
        print(f"   {row['method']}: {row['count']} requests")
    print()

    # 7. User agent analysis
    print("7. User Agent Distribution:")
    result = spl.search('stats count by user_agent | sort -count')
    for row in result:
        print(f"   {row['user_agent']}: {row['count']} requests")
    print()

    # 8. Performance categorization
    print("8. Performance Categories:")
    result = spl.search('eval performance = if(response_time < 50, "fast", if(response_time < 150, "medium", "slow")) | stats count by performance')
    for row in result:
        print(f"   {row['performance']}: {row['count']} requests")
    print()

    # 9. API endpoint popularity
    print("9. Most Popular Endpoints:")
    result = spl.search('status=200 | stats count by path | sort -count | head 3')
    for row in result:
        print(f"   {row['path']}: {row['count']} successful requests")
    print()

    # 10. Failed authentication attempts
    print("10. Authentication Issues:")
    result = spl.search('path="/api/login" status!=200 | fields timestamp, ip, status')
    if result:
        for row in result:
            print(f"   {row['timestamp']} - IP {row['ip']} - Status {row['status']}")
    else:
        print("   No failed login attempts")
    print()


if __name__ == '__main__':
    analyze_web_logs()
