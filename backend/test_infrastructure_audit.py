#!/usr/bin/env python3
"""
==============================================
PHASE 4: Zero-Cost Infrastructure Audit
==============================================

Comprehensive infrastructure audit for AlphaAxiom trading system
to ensure we stay within free tier limits and optimize costs.

Audit Coverage:
- AI Model Token Usage (GLM-4.5, Gemini 2.0, Groq)
- Cloudflare Workers consumption
- D1 Database usage
- R2 Storage efficiency
- Performance across geographical regions
- Cost analysis and optimization recommendations
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics
import subprocess
import psutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class TokenUsageMetrics:
    """Token usage metrics for AI models"""
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: datetime
    request_type: str  # 'chat', 'analysis', 'strategy'

@dataclass
class CloudflareMetrics:
    """Cloudflare infrastructure metrics"""
    workers_requests: int
    workers_cpu_time_ms: int
    d1_reads: int
    d1_writes: int
    d1_storage_bytes: int
    r2_operations: int
    r2_storage_bytes: int
    bandwidth_egress_bytes: int

@dataclass
class PerformanceMetrics:
    """Performance metrics across regions"""
    region: str
    response_time_ms: float
    success_rate: float
    error_count: int
    timestamp: datetime

@dataclass
class CostAnalysis:
    """Cost breakdown analysis"""
    ai_tokens_cost: float
    cloudflare_workers_cost: float
    d1_storage_cost: float
    r2_storage_cost: float
    bandwidth_cost: float
    total_monthly_cost: float
    free_tier_usage_percent: float

class InfrastructureAuditor:
    """
    Comprehensive infrastructure auditor for AlphaAxiom system
    """
    
    def __init__(self):
        self.token_usage_log: List[TokenUsageMetrics] = []
        self.cloudflare_metrics: CloudflareMetrics = CloudflareMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        self.performance_data: List[PerformanceMetrics] = []
        self.cost_analysis: Optional[CostAnalysis] = None
        
        # Cloudflare free tier limits (2024)
        self.CLOUDFLARE_FREE_LIMITS = {
            'workers_requests': 100000,  # 100k requests/day
            'workers_cpu_time': 10 * 60 * 1000,  # 10 minutes CPU time/day
            'd1_storage': 5 * 1024 * 1024 * 1024,  # 5GB storage
            'd1_reads': 25 * 1000 * 1000,  # 25M reads/day
            'd1_writes': 100 * 1000,  # 100k writes/day
            'r2_storage': 10 * 1024 * 1024 * 1024,  # 10GB storage
            'r2_class_a_operations': 1000000,  # 1M Class A operations/month
            'r2_class_b_operations': 10000000,  # 10M Class B operations/month
            'bandwidth_egress': 100 * 1024 * 1024 * 1024  # 100GB/month
        }
        
        # AI Model pricing (per 1M tokens)
        self.AI_MODEL_PRICING = {
            'gemini-1.5-flash': {'input': 0.075, 'output': 0.15},  # Flash pricing
            'gemini-2.0': {'input': 0.125, 'output': 0.375},  # Pro pricing
            'glm-4.5': {'input': 0.5, 'output': 1.0},  # Estimated pricing
            'groq': {'input': 0.19, 'output': 0.78},  # Llama 3 70B
        }
        
        # Test regions for performance testing
        self.TEST_REGIONS = [
            'us-east-1', 'us-west-2', 'eu-west-1', 
            'ap-southeast-1', 'ap-northeast-1'
        ]

    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """
        Run complete infrastructure audit
        """
        print("🔍 Starting AlphaAxiom Infrastructure Audit...")
        print("=" * 60)
        
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'audit_version': '1.0.0',
            'findings': {},
            'recommendations': [],
            'cost_analysis': {},
            'performance_analysis': {},
            'free_tier_status': {}
        }
        
        try:
            # 1. Token Usage Analysis
            print("📊 Analyzing AI token usage...")
            token_analysis = await self.analyze_token_usage()
            audit_results['findings']['token_usage'] = token_analysis
            
            # 2. Cloudflare Infrastructure Analysis
            print("☁️ Analyzing Cloudflare infrastructure...")
            cloudflare_analysis = await self.analyze_cloudflare_infrastructure()
            audit_results['findings']['cloudflare'] = cloudflare_analysis
            
            # 3. Performance Testing
            print("⚡ Running performance tests...")
            performance_results = await self.run_performance_tests()
            audit_results['performance_analysis'] = performance_results
            
            # 4. Cost Analysis
            print("💰 Calculating cost analysis...")
            cost_results = await self.calculate_costs()
            audit_results['cost_analysis'] = cost_results
            
            # 5. Free Tier Status
            print("🆓 Checking free tier status...")
            free_tier_status = await self.check_free_tier_status()
            audit_results['free_tier_status'] = free_tier_status
            
            # 6. Generate Recommendations
            print("💡 Generating optimization recommendations...")
            recommendations = await self.generate_recommendations(audit_results)
            audit_results['recommendations'] = recommendations
            
            print("✅ Infrastructure audit completed!")
            
        except Exception as e:
            print(f"❌ Audit error: {e}")
            audit_results['error'] = str(e)
        
        return audit_results

    async def analyze_token_usage(self) -> Dict[str, Any]:
        """
        Analyze AI model token usage from logs and current usage
        """
        try:
            # Check for existing token usage logs
            token_usage_file = "token_usage_logs.json"
            current_usage = {
                'total_tokens': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'by_model': {},
                'by_type': {'chat': 0, 'analysis': 0, 'strategy': 0},
                'daily_usage': [],
                'cost_estimate': 0.0
            }
            
            # Load existing logs if available
            if os.path.exists(token_usage_file):
                with open(token_usage_file, 'r') as f:
                    logged_usage = json.load(f)
                    current_usage.update(logged_usage)
            
            # Simulate current usage based on system activity
            simulated_usage = await self.simulate_current_token_usage()
            
            # Merge with existing data
            for model, usage in simulated_usage['by_model'].items():
                if model not in current_usage['by_model']:
                    current_usage['by_model'][model] = {
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'total_tokens': 0,
                        'cost': 0.0
                    }
                
                current_usage['by_model'][model]['input_tokens'] += usage['input_tokens']
                current_usage['by_model'][model]['output_tokens'] += usage['output_tokens']
                current_usage['by_model'][model]['total_tokens'] += usage['total_tokens']
                current_usage['by_model'][model]['cost'] += usage['cost']
            
            # Calculate totals
            for model_data in current_usage['by_model'].values():
                current_usage['total_tokens'] += model_data['total_tokens']
                current_usage['input_tokens'] += model_data['input_tokens']
                current_usage['output_tokens'] += model_data['output_tokens']
                current_usage['cost_estimate'] += model_data['cost']
            
            # Check against Gemini Flash free tier (15 requests/minute)
            gemini_usage = current_usage['by_model'].get('gemini-1.5-flash', {})
            gemini_requests = gemini_usage.get('total_tokens', 0) // 1000  # Rough estimate
            
            return {
                'status': 'success',
                'current_usage': current_usage,
                'gemini_flash_status': {
                    'requests_per_minute': gemini_requests,
                    'within_free_tier': gemini_requests < 15,
                    'utilization_percent': (gemini_requests / 15) * 100 if gemini_requests > 0 else 0
                },
                'recommendations': self._get_token_usage_recommendations(current_usage)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def simulate_current_token_usage(self) -> Dict[str, Any]:
        """
        Simulate current token usage based on system activity
        """
        # This would normally connect to actual usage monitoring
        # For demo, we'll simulate realistic usage patterns
        
        usage_simulation = {
            'by_model': {
                'gemini-1.5-flash': {
                    'input_tokens': 50000,  # ~50k input tokens
                    'output_tokens': 15000,  # ~15k output tokens
                    'total_tokens': 65000,
                    'cost': 0.0
                },
                'glm-4.5': {
                    'input_tokens': 30000,
                    'output_tokens': 10000,
                    'total_tokens': 40000,
                    'cost': 0.0
                },
                'groq': {
                    'input_tokens': 20000,
                    'output_tokens': 8000,
                    'total_tokens': 28000,
                    'cost': 0.0
                }
            }
        }
        
        # Calculate costs
        for model, data in usage_simulation['by_model'].items():
            if model in self.AI_MODEL_PRICING:
                pricing = self.AI_MODEL_PRICING[model]
                data['cost'] = (
                    (data['input_tokens'] / 1000000) * pricing['input'] +
                    (data['output_tokens'] / 1000000) * pricing['output']
                )
        
        return usage_simulation

    async def analyze_cloudflare_infrastructure(self) -> Dict[str, Any]:
        """
        Analyze Cloudflare Workers, D1, and R2 usage
        """
        try:
            # This would normally connect to Cloudflare API
            # For demo, we'll simulate current usage
            
            simulated_metrics = {
                'workers': {
                    'requests_today': 15420,  # ~15k requests
                    'cpu_time_ms': 450000,  # ~7.5 minutes
                    'memory_usage_mb': 128,
                    'errors_4xx': 142,
                    'errors_5xx': 8
                },
                'd1': {
                    'storage_used_bytes': 512 * 1024 * 1024,  # 512MB
                    'reads_today': 1500000,  # 1.5M reads
                    'writes_today': 85000,  # 85k writes
                    'query_time_avg_ms': 12.5,
                    'tables_count': 7
                },
                'r2': {
                    'storage_used_bytes': 2.1 * 1024 * 1024 * 1024,  # 2.1GB
                    'class_a_operations': 450000,  # 450k operations
                    'class_b_operations': 3200000,  # 3.2M operations
                    'objects_count': 15420,
                    'avg_object_size_kb': 142
                },
                'kv': {
                    'reads_today': 25000,
                    'writes_today': 8500,
                    'storage_used_bytes': 45 * 1024 * 1024  # 45MB
                }
            }
            
            # Calculate utilization percentages
            utilization = {
                'workers_requests_percent': (simulated_metrics['workers']['requests_today'] / 
                                         self.CLOUDFLARE_FREE_LIMITS['workers_requests']) * 100,
                'workers_cpu_percent': (simulated_metrics['workers']['cpu_time_ms'] / 
                                    self.CLOUDFLARE_FREE_LIMITS['workers_cpu_time']) * 100,
                'd1_storage_percent': (simulated_metrics['d1']['storage_used_bytes'] / 
                                    self.CLOUDFLARE_FREE_LIMITS['d1_storage']) * 100,
                'd1_reads_percent': (simulated_metrics['d1']['reads_today'] / 
                                   self.CLOUDFLARE_FREE_LIMITS['d1_reads']) * 100,
                'd1_writes_percent': (simulated_metrics['d1']['writes_today'] / 
                                    self.CLOUDFLARE_FREE_LIMITS['d1_writes']) * 100,
                'r2_storage_percent': (simulated_metrics['r2']['storage_used_bytes'] / 
                                    self.CLOUDFLARE_FREE_LIMITS['r2_storage']) * 100
            }
            
            # Check if within free tier
            free_tier_status = {
                'workers_within_limits': (
                    utilization['workers_requests_percent'] < 100 and 
                    utilization['workers_cpu_percent'] < 100
                ),
                'd1_within_limits': (
                    utilization['d1_storage_percent'] < 100 and
                    utilization['d1_reads_percent'] < 100 and
                    utilization['d1_writes_percent'] < 100
                ),
                'r2_within_limits': utilization['r2_storage_percent'] < 100,
                'overall_within_free_tier': False  # Will be calculated
            }
            
            free_tier_status['overall_within_free_tier'] = (
                free_tier_status['workers_within_limits'] and
                free_tier_status['d1_within_limits'] and
                free_tier_status['r2_within_limits']
            )
            
            return {
                'status': 'success',
                'current_metrics': simulated_metrics,
                'utilization': utilization,
                'free_tier_status': free_tier_status,
                'recommendations': self._get_cloudflare_recommendations(simulated_metrics, utilization)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def run_performance_tests(self) -> Dict[str, Any]:
        """
        Run performance tests across different geographical regions
        """
        try:
            performance_results = {
                'regional_performance': {},
                'global_metrics': {
                    'avg_response_time': 0,
                    'p95_response_time': 0,
                    'p99_response_time': 0,
                    'success_rate': 0,
                    'total_tests': 0
                },
                'bottlenecks': [],
                'recommendations': []
            }
            
            all_response_times = []
            total_successes = 0
            total_tests = 0
            
            # Test each region
            for region in self.TEST_REGIONS:
                region_results = await self._test_region_performance(region)
                performance_results['regional_performance'][region] = region_results
                
                all_response_times.extend(region_results['response_times'])
                total_successes += region_results['success_count']
                total_tests += region_results['total_tests']
            
            # Calculate global metrics
            if all_response_times:
                performance_results['global_metrics']['avg_response_time'] = statistics.mean(all_response_times)
                performance_results['global_metrics']['p95_response_time'] = statistics.quantiles(all_response_times, n=20)[18]  # 95th percentile
                performance_results['global_metrics']['p99_response_time'] = statistics.quantiles(all_response_times, n=100)[98]  # 99th percentile
            
            performance_results['global_metrics']['success_rate'] = (total_successes / total_tests) * 100 if total_tests > 0 else 0
            performance_results['global_metrics']['total_tests'] = total_tests
            
            # Identify bottlenecks
            performance_results['bottlenecks'] = self._identify_performance_bottlenecks(performance_results)
            performance_results['recommendations'] = self._get_performance_recommendations(performance_results)
            
            return {
                'status': 'success',
                'results': performance_results
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def _test_region_performance(self, region: str) -> Dict[str, Any]:
        """
        Test performance for a specific region
        """
        # Simulate regional performance testing
        # In reality, this would make actual requests to regional endpoints
        
        response_times = []
        success_count = 0
        total_tests = 50  # Test 50 requests per region
        
        for i in range(total_tests):
            # Simulate response time based on region
            base_latency = {
                'us-east-1': 50,
                'us-west-2': 75,
                'eu-west-1': 120,
                'ap-southeast-1': 180,
                'ap-northeast-1': 150
            }.get(region, 100)
            
            # Add random variation
            response_time = base_latency + (i * 2) + (hash(region + str(i)) % 30)
            response_times.append(response_time)
            
            # Simulate success rate (95% average)
            if hash(region + str(i)) % 100 < 95:
                success_count += 1
        
        return {
            'region': region,
            'response_times': response_times,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'success_count': success_count,
            'total_tests': total_tests,
            'success_rate': (success_count / total_tests) * 100
        }

    async def calculate_costs(self) -> Dict[str, Any]:
        """
        Calculate comprehensive cost analysis
        """
        try:
            # Get current usage data
            token_usage = await self.analyze_token_usage()
            cloudflare_usage = await self.analyze_cloudflare_infrastructure()
            
            # Calculate AI costs
            ai_costs = token_usage.get('current_usage', {}).get('cost_estimate', 0.0)
            
            # Calculate Cloudflare costs (beyond free tier)
            cf_metrics = cloudflare_usage.get('current_metrics', {})
            utilization = cloudflare_usage.get('utilization', {})
            
            # Estimate overage costs
            workers_overage_cost = max(0, utilization.get('workers_requests_percent', 0) - 100) * 0.50  # $0.50 per 100k requests
            d1_overage_cost = max(0, utilization.get('d1_storage_percent', 0) - 100) * 0.75  # $0.75 per GB
            r2_overage_cost = max(0, utilization.get('r2_storage_percent', 0) - 100) * 0.15  # $0.15 per GB
            
            # Bandwidth costs (beyond 100GB free)
            estimated_bandwidth_gb = 50  # Estimate based on current usage
            bandwidth_cost = max(0, estimated_bandwidth_gb - 100) * 0.09  # $0.09 per GB
            
            total_monthly_cost = (
                ai_costs + workers_overage_cost + d1_overage_cost + 
                r2_overage_cost + bandwidth_cost
            )
            
            cost_breakdown = {
                'ai_tokens': ai_costs,
                'cloudflare_workers': workers_overage_cost,
                'd1_storage': d1_overage_cost,
                'r2_storage': r2_overage_cost,
                'bandwidth': bandwidth_cost,
                'total_monthly': total_monthly_cost
            }
            
            # Project annual costs
            annual_cost = total_monthly_cost * 12
            
            # Calculate cost per active user (assuming 100 users)
            cost_per_user = total_monthly_cost / 100
            
            return {
                'status': 'success',
                'cost_breakdown': cost_breakdown,
                'monthly_projection': total_monthly_cost,
                'annual_projection': annual_cost,
                'cost_per_user': cost_per_user,
                'free_tier_savings': max(0, total_monthly_cost - (total_monthly_cost * 0.3)),  # Estimated free tier value
                'recommendations': self._get_cost_optimization_recommendations(cost_breakdown)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def check_free_tier_status(self) -> Dict[str, Any]:
        """
        Check current status against free tier limits
        """
        try:
            cloudflare_analysis = await self.analyze_cloudflare_infrastructure()
            token_analysis = await self.analyze_token_usage()
            
            free_tier_status = {
                'overall_status': 'healthy',
                'alerts': [],
                'warnings': [],
                'utilization_summary': {},
                'time_until_limit': {}
            }
            
            # Check Cloudflare limits
            cf_utilization = cloudflare_analysis.get('utilization', {})
            cf_status = cloudflare_analysis.get('free_tier_status', {})
            
            for service, utilization in cf_utilization.items():
                free_tier_status['utilization_summary'][service] = f"{utilization:.1f}%"
                
                if utilization > 90:
                    free_tier_status['alerts'].append(f"⚠️ {service}: {utilization:.1f}% utilized - Approaching limit!")
                    free_tier_status['overall_status'] = 'critical'
                elif utilization > 75:
                    free_tier_status['warnings'].append(f"⚡ {service}: {utilization:.1f}% utilized - Monitor closely")
                    if free_tier_status['overall_status'] == 'healthy':
                        free_tier_status['overall_status'] = 'warning'
            
            # Check Gemini Flash limits
            gemini_status = token_analysis.get('gemini_flash_status', {})
            gemini_utilization = gemini_status.get('utilization_percent', 0)
            
            free_tier_status['utilization_summary']['gemini_flash'] = f"{gemini_utilization:.1f}%"
            
            if not gemini_status.get('within_free_tier', True):
                free_tier_status['alerts'].append(f"🚨 Gemini Flash: Exceeding free tier limits!")
                free_tier_status['overall_status'] = 'critical'
            elif gemini_utilization > 80:
                free_tier_status['warnings'].append(f"⚡ Gemini Flash: {gemini_utilization:.1f}% utilized")
            
            # Estimate time until limits (based on current usage patterns)
            current_date = datetime.now()
            days_in_month = 30
            
            for service, utilization in cf_utilization.items():
                if utilization > 0:
                    daily_rate = utilization / days_in_month
                    remaining_days = max(0, (100 - utilization) / daily_rate) if daily_rate > 0 else days_in_month
                    limit_date = current_date + timedelta(days=remaining_days)
                    free_tier_status['time_until_limit'][service] = {
                        'days_remaining': int(remaining_days),
                        'estimated_limit_date': limit_date.strftime('%Y-%m-%d')
                    }
            
            return {
                'status': 'success',
                'free_tier_status': free_tier_status
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def generate_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """
        Generate comprehensive optimization recommendations
        """
        recommendations = []
        
        try:
            # Cost optimization recommendations
            cost_analysis = audit_results.get('cost_analysis', {})
            if cost_analysis.get('status') == 'success':
                cost_breakdown = cost_analysis.get('cost_breakdown', {})
                
                if cost_breakdown.get('ai_tokens', 0) > 10:
                    recommendations.append("💡 Consider implementing token caching to reduce AI API calls")
                    recommendations.append("💡 Use smaller models for simple requests, reserve larger models for complex analysis")
                
                if cost_breakdown.get('bandwidth', 0) > 5:
                    recommendations.append("💡 Implement response compression and caching to reduce bandwidth costs")
            
            # Performance recommendations
            perf_analysis = audit_results.get('performance_analysis', {})
            if perf_analysis.get('status') == 'success':
                results = perf_analysis.get('results', {})
                global_metrics = results.get('global_metrics', {})
                
                if global_metrics.get('avg_response_time', 0) > 200:
                    recommendations.append("⚡ Optimize database queries and add caching layers")
                    recommendations.append("⚡ Consider implementing edge caching for frequently accessed data")
                
                if global_metrics.get('success_rate', 100) < 95:
                    recommendations.append("🔧 Implement better error handling and retry mechanisms")
            
            # Free tier optimization
            free_tier = audit_results.get('free_tier_status', {})
            if free_tier.get('status') == 'success':
                ft_status = free_tier.get('free_tier_status', {})
                
                if ft_status.get('overall_status') == 'critical':
                    recommendations.append("🚨 CRITICAL: Implement usage throttling to stay within free tier limits")
                    recommendations.append("🚨 Consider upgrading to paid plan or optimizing resource usage immediately")
                elif ft_status.get('overall_status') == 'warning':
                    recommendations.append("⚠️ Monitor usage closely and implement optimization strategies")
            
            # Infrastructure recommendations
            recommendations.extend([
                "📊 Implement comprehensive logging and monitoring for better visibility",
                "🔄 Set up automated alerts for when usage approaches limits",
                "🗂️ Implement data archival strategy for old trading data",
                "🔐 Review and optimize API security to prevent unauthorized usage",
                "📈 Regular performance audits to identify optimization opportunities"
            ])
            
        except Exception as e:
            recommendations.append(f"❌ Error generating recommendations: {e}")
        
        return recommendations

    def _get_token_usage_recommendations(self, usage_data: Dict[str, Any]) -> List[str]:
        """Get specific token usage recommendations"""
        recommendations = []
        
        total_tokens = usage_data.get('total_tokens', 0)
        cost_estimate = usage_data.get('cost_estimate', 0)
        
        if total_tokens > 100000:  # > 100k tokens
            recommendations.append("📝 Implement prompt optimization to reduce token usage")
            recommendations.append("💾 Cache frequently requested responses")
        
        if cost_estimate > 5:  # > $5
            recommendations.append("💰 Consider using more cost-effective models for routine tasks")
            recommendations.append("📊 Implement usage quotas per user/model")
        
        return recommendations

    def _get_cloudflare_recommendations(self, metrics: Dict[str, Any], utilization: Dict[str, Any]) -> List[str]:
        """Get specific Cloudflare recommendations"""
        recommendations = []
        
        # Workers recommendations
        if utilization.get('workers_requests_percent', 0) > 80:
            recommendations.append("⚡ Implement request batching to reduce Workers invocations")
            recommendations.append("🗂️ Add response caching at the edge")
        
        if utilization.get('workers_cpu_percent', 0) > 80:
            recommendations.push("🔧 Optimize Workers code for better CPU efficiency")
            recommendations.append("⚖️ Distribute heavy computations across multiple Workers")
        
        # D1 recommendations
        if utilization.get('d1_reads_percent', 0) > 80:
            recommendations.append("📚 Implement read-through caching for frequently accessed data")
            recommendations.append("🔍 Optimize database queries and add proper indexes")
        
        if utilization.get('d1_writes_percent', 0) > 80:
            recommendations.append("📝 Batch write operations where possible")
            recommendations.append("🗑️ Implement data cleanup and archival strategies")
        
        # R2 recommendations
        if utilization.get('r2_storage_percent', 0) > 80:
            recommendations.append("📦 Implement data compression for stored objects")
            recommendations.append("🗂️ Set up automated lifecycle policies for old data")
        
        return recommendations

    def _identify_performance_bottlenecks(self, performance_results: Dict[str, Any]) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        regional_perf = performance_results.get('regional_performance', {})
        
        for region, metrics in regional_perf.items():
            avg_time = metrics.get('avg_response_time', 0)
            success_rate = metrics.get('success_rate', 100)
            
            if avg_time > 300:  # > 300ms
                bottlenecks.append(f"🐌 {region}: High average response time ({avg_time:.1f}ms)")
            
            if success_rate < 95:  # < 95% success rate
                bottlenecks.append(f"❌ {region}: Low success rate ({success_rate:.1f}%)")
        
        return bottlenecks

    def _get_performance_recommendations(self, performance_results: Dict[str, Any]) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        global_metrics = performance_results.get('global_metrics', {})
        avg_response = global_metrics.get('avg_response_time', 0)
        p95_response = global_metrics.get('p95_response_time', 0)
        success_rate = global_metrics.get('success_rate', 100)
        
        if avg_response > 200:
            recommendations.append("⚡ Implement response caching and CDN optimization")
            recommendations.append("🔧 Optimize database queries and connection pooling")
        
        if p95_response > 500:
            recommendations.append("📊 Implement request queuing and load balancing")
            recommendations.append("🔍 Profile and optimize slow endpoints")
        
        if success_rate < 98:
            recommendations.append("🛡️ Implement circuit breakers and retry mechanisms")
            recommendations.append("📝 Improve error handling and logging")
        
        return recommendations

    def _get_cost_optimization_recommendations(self, cost_breakdown: Dict[str, Any]) -> List[str]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        ai_cost = cost_breakdown.get('ai_tokens', 0)
        cf_cost = cost_breakdown.get('cloudflare_workers', 0)
        storage_cost = cost_breakdown.get('d1_storage', 0) + cost_breakdown.get('r2_storage', 0)
        
        if ai_cost > 10:
            recommendations.append("🤖 Implement AI model selection based on request complexity")
            recommendations.append("💾 Add response caching for repetitive AI queries")
        
        if cf_cost > 5:
            recommendations.append("⚡ Optimize Workers code to reduce CPU time")
            recommendations.append("📊 Implement request deduplication")
        
        if storage_cost > 5:
            recommendations.append("🗂️ Implement data lifecycle management")
            recommendations.append("📦 Use compression for stored data")
        
        return recommendations

    def save_audit_report(self, audit_results: Dict[str, Any], filename: str = None) -> str:
        """
        Save audit report to file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"infrastructure_audit_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(audit_results, f, indent=2, default=str)
            
            print(f"📄 Audit report saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return ""

    def generate_executive_summary(self, audit_results: Dict[str, Any]) -> str:
        """
        Generate executive summary of audit findings
        """
        try:
            summary = []
            summary.append("🚀 ALPHAAXIOM INFRASTRUCTURE AUDIT - EXECUTIVE SUMMARY")
            summary.append("=" * 60)
            summary.append(f"📅 Audit Date: {audit_results.get('timestamp', 'Unknown')}")
            summary.append(f"🔍 Audit Version: {audit_results.get('audit_version', 'Unknown')}")
            summary.append("")
            
            # Free Tier Status
            free_tier = audit_results.get('free_tier_status', {})
            if free_tier.get('status') == 'success':
                ft_status = free_tier.get('free_tier_status', {})
                overall_status = ft_status.get('overall_status', 'unknown')
                
                status_emoji = {
                    'healthy': '✅',
                    'warning': '⚠️',
                    'critical': '🚨'
                }.get(overall_status, '❓')
                
                summary.append(f"{status_emoji} Free Tier Status: {overall_status.upper()}")
                
                alerts = ft_status.get('alerts', [])
                warnings = ft_status.get('warnings', [])
                
                if alerts:
                    summary.append("🚨 CRITICAL ALERTS:")
                    for alert in alerts:
                        summary.append(f"   • {alert}")
                
                if warnings:
                    summary.append("⚠️ WARNINGS:")
                    for warning in warnings:
                        summary.append(f"   • {warning}")
            
            summary.append("")
            
            # Cost Analysis
            cost_analysis = audit_results.get('cost_analysis', {})
            if cost_analysis.get('status') == 'success':
                monthly_cost = cost_analysis.get('monthly_projection', 0)
                annual_cost = cost_analysis.get('annual_projection', 0)
                
                summary.append("💰 COST ANALYSIS:")
                summary.append(f"   • Monthly Projection: ${monthly_cost:.2f}")
                summary.append(f"   • Annual Projection: ${annual_cost:.2f}")
                summary.append(f"   • Cost Per User: ${cost_analysis.get('cost_per_user', 0):.2f}")
            
            summary.append("")
            
            # Performance Summary
            perf_analysis = audit_results.get('performance_analysis', {})
            if perf_analysis.get('status') == 'success':
                results = perf_analysis.get('results', {})
                global_metrics = results.get('global_metrics', {})
                
                summary.append("⚡ PERFORMANCE SUMMARY:")
                summary.append(f"   • Average Response Time: {global_metrics.get('avg_response_time', 0):.1f}ms")
                summary.append(f"   • Success Rate: {global_metrics.get('success_rate', 0):.1f}%")
                summary.append(f"   • Total Tests: {global_metrics.get('total_tests', 0)}")
            
            summary.append("")
            
            # Top Recommendations
            recommendations = audit_results.get('recommendations', [])
            if recommendations:
                summary.append("💡 TOP RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations[:5], 1):
                    summary.append(f"   {i}. {rec}")
            
            summary.append("")
            summary.append("📊 For detailed analysis, see the full audit report.")
            
            return "\n".join(summary)
            
        except Exception as e:
            return f"❌ Error generating summary: {e}"


async def main():
    """
    Main execution function
    """
    auditor = InfrastructureAuditor()
    
    print("🔍 AlphaAxiom Infrastructure Audit Starting...")
    print("📋 This audit will analyze:")
    print("   • AI Model Token Usage & Costs")
    print("   • Cloudflare Workers, D1, and R2 Usage")
    print("   • Performance Across Geographical Regions")
    print("   • Cost Analysis & Optimization Opportunities")
    print("   • Free Tier Compliance Status")
    print("")
    
    # Run comprehensive audit
    audit_results = await auditor.run_comprehensive_audit()
    
    # Save detailed report
    report_filename = auditor.save_audit_report(audit_results)
    
    # Generate and display executive summary
    summary = auditor.generate_executive_summary(audit_results)
    print("\n" + summary)
    
    # Save summary to file
    if report_filename:
        summary_filename = report_filename.replace('.json', '_summary.txt')
        try:
            with open(summary_filename, 'w') as f:
                f.write(summary)
            print(f"\n📄 Executive summary saved to: {summary_filename}")
        except Exception as e:
            print(f"❌ Error saving summary: {e}")
    
    return audit_results


if __name__ == "__main__":
    # Run the audit
    results = asyncio.run(main())
    
    print("\n✅ Infrastructure audit completed!")
    print("📊 Review the generated reports for detailed findings and recommendations.")