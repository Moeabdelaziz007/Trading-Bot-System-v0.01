#!/usr/bin/env python3
# backend/test_api_stress.py
# ==============================================
# PHASE 2: Backend API Stress Test for AlphaAxiom
# Comprehensive stress testing for trading system endpoints
# ==============================================

import asyncio
import aiohttp
import websockets
import json
import time
import statistics
import psutil
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import concurrent.futures
import threading
import resource

# ==============================================
# CONFIGURATION
# ==============================================

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
TIMEOUT = 10  # seconds
MAX_CONCURRENT_REQUESTS = 50
TARGET_RESPONSE_TIME = 500  # ms (except AI chat)

@dataclass
class TestResult:
    """Test result data structure"""
    endpoint: str
    method: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    test_duration: float
    errors: List[str]

@dataclass
class SystemMetrics:
    """System resource metrics"""
    memory_before: float
    memory_after: float
    cpu_before: float
    cpu_after: float
    peak_memory: float

class StressTestFramework:
    """Comprehensive stress testing framework for AlphaAxiom API"""
    
    def __init__(self):
        self.session = None
        self.results = []
        self.system_metrics = {}
        self.start_time = None
        self.end_time = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=MAX_CONCURRENT_REQUESTS,
            limit_per_host=MAX_CONCURRENT_REQUESTS,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource usage"""
        process = psutil.Process(os.getpid())
        return {
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'system_memory_mb': psutil.virtual_memory().used / 1024 / 1024,
            'system_cpu_percent': psutil.cpu_percent()
        }
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make a single HTTP request and measure performance"""
        start_time = time.time()
        error = None
        status_code = None
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(f"{BASE_URL}{endpoint}") as response:
                    status_code = response.status
                    content = await response.json()
            elif method.upper() == 'POST':
                async with self.session.post(f"{BASE_URL}{endpoint}", json=data) as response:
                    status_code = response.status
                    content = await response.json()
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'success': 200 <= status_code < 300,
                'response_time': response_time,
                'status_code': status_code,
                'content': content,
                'error': None
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_msg = f"{type(e).__name__}: {str(e)}"
            return {
                'success': False,
                'response_time': response_time,
                'status_code': status_code,
                'content': None,
                'error': error_msg
            }
    
    async def test_concurrent_requests(self, method: str, endpoint: str, data: Dict = None, 
                                     num_requests: int = 50) -> TestResult:
        """Test endpoint with concurrent requests"""
        print(f"\n🧪 Testing {method} {endpoint} with {num_requests} concurrent requests...")
        
        # Record system metrics before test
        metrics_before = self.get_system_metrics()
        peak_memory = metrics_before['memory_mb']
        
        # Create concurrent tasks
        tasks = []
        for i in range(num_requests):
            task = asyncio.create_task(self.make_request(method, endpoint, data))
            tasks.append(task)
        
        # Execute all requests concurrently
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        test_duration = time.time() - start_time
        
        # Process results
        successful_requests = 0
        failed_requests = 0
        response_times = []
        errors = []
        
        for response in responses:
            if isinstance(response, Exception):
                failed_requests += 1
                errors.append(f"Task exception: {type(response).__name__}: {str(response)}")
            else:
                if response['success']:
                    successful_requests += 1
                else:
                    failed_requests += 1
                    if response['error']:
                        errors.append(response['error'])
                
                response_times.append(response['response_time'])
            
            # Track peak memory usage
            current_metrics = self.get_system_metrics()
            peak_memory = max(peak_memory, current_metrics['memory_mb'])
        
        # Record system metrics after test
        metrics_after = self.get_system_metrics()
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        # Calculate performance metrics
        requests_per_second = num_requests / test_duration if test_duration > 0 else 0
        error_rate = (failed_requests / num_requests) * 100 if num_requests > 0 else 0
        
        result = TestResult(
            endpoint=endpoint,
            method=method,
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            response_times=response_times,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            memory_usage_mb=metrics_after['memory_mb'] - metrics_before['memory_mb'],
            cpu_usage_percent=metrics_after['cpu_percent'],
            test_duration=test_duration,
            errors=errors[:10]  # Keep only first 10 errors
        )
        
        # Store system metrics
        self.system_metrics[endpoint] = SystemMetrics(
            memory_before=metrics_before['memory_mb'],
            memory_after=metrics_after['memory_mb'],
            cpu_before=metrics_before['cpu_percent'],
            cpu_after=metrics_after['cpu_percent'],
            peak_memory=peak_memory
        )
        
        return result
    
    async def test_websocket_endpoint(self, num_connections: int = 10) -> TestResult:
        """Test WebSocket endpoint with multiple concurrent connections"""
        print(f"\n🔌 Testing WebSocket /ws with {num_connections} concurrent connections...")
        
        metrics_before = self.get_system_metrics()
        peak_memory = metrics_before['memory_mb']
        
        async def websocket_test(connection_id: int) -> Dict[str, Any]:
            """Test individual WebSocket connection"""
            start_time = time.time()
            error = None
            messages_received = 0
            
            try:
                async with websockets.connect(WS_URL) as websocket:
                    # Wait for a few messages
                    timeout = 5  # seconds
                    end_time = time.time() + timeout
                    
                    while time.time() < end_time:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            messages_received += 1
                            # Validate message structure
                            data = json.loads(message)
                            if not all(key in data for key in ['type', 'timestamp']):
                                error = "Invalid message structure"
                                break
                        except asyncio.TimeoutError:
                            break
                        except json.JSONDecodeError:
                            error = "Invalid JSON in message"
                            break
                    
                    connection_time = (time.time() - start_time) * 1000
                    
                    return {
                        'success': error is None,
                        'connection_time': connection_time,
                        'messages_received': messages_received,
                        'error': error
                    }
                    
            except Exception as e:
                connection_time = (time.time() - start_time) * 1000
                return {
                    'success': False,
                    'connection_time': connection_time,
                    'messages_received': 0,
                    'error': f"{type(e).__name__}: {str(e)}"
                }
        
        # Create concurrent WebSocket connections
        start_time = time.time()
        tasks = [websocket_test(i) for i in range(num_connections)]
        connections = await asyncio.gather(*tasks, return_exceptions=True)
        test_duration = time.time() - start_time
        
        # Process results
        successful_connections = 0
        failed_connections = 0
        connection_times = []
        total_messages = 0
        errors = []
        
        for connection in connections:
            if isinstance(connection, Exception):
                failed_connections += 1
                errors.append(f"Connection exception: {type(connection).__name__}: {str(connection)}")
            else:
                if connection['success']:
                    successful_connections += 1
                    total_messages += connection['messages_received']
                else:
                    failed_connections += 1
                    if connection['error']:
                        errors.append(connection['error'])
                
                connection_times.append(connection['connection_time'])
            
            # Track peak memory usage
            current_metrics = self.get_system_metrics()
            peak_memory = max(peak_memory, current_metrics['memory_mb'])
        
        metrics_after = self.get_system_metrics()
        
        # Calculate statistics
        if connection_times:
            avg_connection_time = statistics.mean(connection_times)
            min_connection_time = min(connection_times)
            max_connection_time = max(connection_times)
            p95_connection_time = statistics.quantiles(connection_times, n=20)[18]
            p99_connection_time = statistics.quantiles(connection_times, n=100)[98]
        else:
            avg_connection_time = min_connection_time = max_connection_time = 0
            p95_connection_time = p99_connection_time = 0
        
        connections_per_second = num_connections / test_duration if test_duration > 0 else 0
        error_rate = (failed_connections / num_connections) * 100 if num_connections > 0 else 0
        
        result = TestResult(
            endpoint="/ws",
            method="WebSocket",
            total_requests=num_connections,
            successful_requests=successful_connections,
            failed_requests=failed_connections,
            response_times=connection_times,
            avg_response_time=avg_connection_time,
            min_response_time=min_connection_time,
            max_response_time=max_connection_time,
            p95_response_time=p95_connection_time,
            p99_response_time=p99_connection_time,
            requests_per_second=connections_per_second,
            error_rate=error_rate,
            memory_usage_mb=metrics_after['memory_mb'] - metrics_before['memory_mb'],
            cpu_usage_percent=metrics_after['cpu_percent'],
            test_duration=test_duration,
            errors=errors[:10]
        )
        
        self.system_metrics["/ws"] = SystemMetrics(
            memory_before=metrics_before['memory_mb'],
            memory_after=metrics_after['memory_mb'],
            cpu_before=metrics_before['cpu_percent'],
            cpu_after=metrics_after['cpu_percent'],
            peak_memory=peak_memory
        )
        
        return result
    
    def generate_report(self) -> str:
        """Generate comprehensive performance report"""
        report = []
        report.append("=" * 80)
        report.append("🚀 ALPHAAXIOM BACKEND API STRESS TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {datetime.now().isoformat()}")
        report.append(f"Base URL: {BASE_URL}")
        report.append(f"Target Response Time: {TARGET_RESPONSE_TIME}ms")
        report.append("")
        
        # Summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.error_rate == 0 and r.avg_response_time < TARGET_RESPONSE_TIME)
        
        report.append("📊 SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Passed Tests: {passed_tests}")
        report.append(f"Failed Tests: {total_tests - passed_tests}")
        report.append(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        report.append("")
        
        # Detailed Results
        report.append("📈 DETAILED RESULTS")
        report.append("-" * 40)
        
        for result in self.results:
            report.append(f"\n🔍 {result.method} {result.endpoint}")
            report.append(f"   Total Requests: {result.total_requests}")
            report.append(f"   Successful: {result.successful_requests}")
            report.append(f"   Failed: {result.failed_requests}")
            report.append(f"   Error Rate: {result.error_rate:.2f}%")
            report.append(f"   Response Times:")
            report.append(f"     Average: {result.avg_response_time:.2f}ms")
            report.append(f"     Min: {result.min_response_time:.2f}ms")
            report.append(f"     Max: {result.max_response_time:.2f}ms")
            report.append(f"     95th Percentile: {result.p95_response_time:.2f}ms")
            report.append(f"     99th Percentile: {result.p99_response_time:.2f}ms")
            report.append(f"   Requests/Second: {result.requests_per_second:.2f}")
            report.append(f"   Test Duration: {result.test_duration:.2f}s")
            report.append(f"   Memory Usage: {result.memory_usage_mb:.2f}MB")
            report.append(f"   CPU Usage: {result.cpu_usage_percent:.2f}%")
            
            # Performance status
            if result.avg_response_time < TARGET_RESPONSE_TIME and result.error_rate == 0:
                report.append(f"   ✅ PASSED")
            else:
                report.append(f"   ❌ FAILED")
                if result.avg_response_time >= TARGET_RESPONSE_TIME:
                    report.append(f"      ⚠️  Response time exceeds {TARGET_RESPONSE_TIME}ms target")
                if result.error_rate > 0:
                    report.append(f"      ⚠️  Error rate: {result.error_rate:.2f}%")
            
            # Show errors if any
            if result.errors:
                report.append(f"   Errors (first 3):")
                for error in result.errors[:3]:
                    report.append(f"     - {error}")
        
        # System Metrics Summary
        report.append(f"\n🖥️  SYSTEM METRICS SUMMARY")
        report.append("-" * 40)
        
        for endpoint, metrics in self.system_metrics.items():
            report.append(f"\n{endpoint}:")
            report.append(f"   Memory Before: {metrics.memory_before:.2f}MB")
            report.append(f"   Memory After: {metrics.memory_after:.2f}MB")
            report.append(f"   Peak Memory: {metrics.peak_memory:.2f}MB")
            report.append(f"   Memory Delta: {metrics.memory_after - metrics.memory_before:.2f}MB")
            report.append(f"   CPU Before: {metrics.cpu_before:.2f}%")
            report.append(f"   CPU After: {metrics.cpu_after:.2f}%")
        
        # Recommendations
        report.append(f"\n💡 RECOMMENDATIONS")
        report.append("-" * 40)
        
        slow_endpoints = [r for r in self.results if r.avg_response_time >= TARGET_RESPONSE_TIME]
        if slow_endpoints:
            report.append("⚠️  Slow Endpoints (need optimization):")
            for r in slow_endpoints:
                report.append(f"   - {r.method} {r.endpoint}: {r.avg_response_time:.2f}ms")
        
        high_error_endpoints = [r for r in self.results if r.error_rate > 5]
        if high_error_endpoints:
            report.append("⚠️  High Error Rate Endpoints:")
            for r in high_error_endpoints:
                report.append(f"   - {r.method} {r.endpoint}: {r.error_rate:.2f}%")
        
        memory_intensive_endpoints = [r for r in self.results if r.memory_usage_mb > 50]
        if memory_intensive_endpoints:
            report.append("⚠️  Memory Intensive Endpoints:")
            for r in memory_intensive_endpoints:
                report.append(f"   - {r.method} {r.endpoint}: {r.memory_usage_mb:.2f}MB")
        
        if not slow_endpoints and not high_error_endpoints and not memory_intensive_endpoints:
            report.append("✅ All endpoints are performing within acceptable limits!")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    async def run_all_tests(self):
        """Run all stress tests"""
        print("🚀 Starting AlphaAxiom Backend API Stress Tests...")
        print(f"Target URL: {BASE_URL}")
        print(f"WebSocket URL: {WS_URL}")
        print(f"Max Concurrent Requests: {MAX_CONCURRENT_REQUESTS}")
        print(f"Target Response Time: {TARGET_RESPONSE_TIME}ms")
        
        self.start_time = time.time()
        
        # Test 1: GET /api/status
        result1 = await self.test_concurrent_requests('GET', '/api/status', num_requests=50)
        self.results.append(result1)
        
        # Test 2: GET /api/brain/status
        result2 = await self.test_concurrent_requests('GET', '/api/brain/status', num_requests=50)
        self.results.append(result2)
        
        # Test 3: POST /api/chat (AI chat - expect longer response times)
        chat_data = {"message": "Analyze Gold"}
        result3 = await self.test_concurrent_requests('POST', '/api/ai/chat', data=chat_data, num_requests=10)
        self.results.append(result3)
        
        # Test 4: POST /api/trade (10 concurrent trade requests)
        trade_data = {
            "symbol": "BTC/USD",
            "side": "BUY",
            "amount": 0.01,
            "auto_risk": True
        }
        result4 = await self.test_concurrent_requests('POST', '/api/trade', data=trade_data, num_requests=10)
        self.results.append(result4)
        
        # Test 5: WebSocket /ws
        result5 = await self.test_websocket_endpoint(num_connections=10)
        self.results.append(result5)
        
        self.end_time = time.time()
        
        # Generate and print report
        report = self.generate_report()
        print("\n" + report)
        
        # Save report to file
        report_filename = f"stress_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_filename}")
        
        return self.results

# ==============================================
# MAIN EXECUTION
# ==============================================

async def main():
    """Main function to run stress tests"""
    try:
        async with StressTestFramework() as framework:
            results = await framework.run_all_tests()
            
            # Exit with appropriate code
            failed_tests = sum(1 for r in results if r.error_rate > 0 or r.avg_response_time >= TARGET_RESPONSE_TIME)
            if failed_tests > 0:
                print(f"\n❌ {failed_tests} test(s) failed!")
                sys.exit(1)
            else:
                print(f"\n✅ All tests passed!")
                sys.exit(0)
                
    except Exception as e:
        print(f"❌ Stress test failed with error: {type(e).__name__}: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if backend is running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result != 0:
        print("❌ Backend server is not running on localhost:8000")
        print("Please start the backend server first:")
        print("  cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Run stress tests
    asyncio.run(main())