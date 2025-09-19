#!/usr/bin/env python3
"""
Eufy Content GEO Readiness Audit
Comprehensive audit of Eufy's existing content for Google AI Overview optimization
"""

import json
import csv
import requests
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse
from content_optimization_engine import ContentOptimizationEngine, ContentAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EufyContentAudit:
    """Eufy content audit results"""
    url: str
    page_type: str
    current_geo_score: float
    optimization_potential: float
    priority_level: str
    specific_recommendations: List[str]
    competitive_gaps: List[str]
    technical_issues: List[str]
    estimated_impact: str
    time_to_optimize: str

class EufyGEOAuditor:
    def __init__(self, serpapi_key: str = None):
        """Initialize Eufy GEO auditor"""
        self.optimization_engine = ContentOptimizationEngine(serpapi_key)
        
        # Eufy-specific optimization patterns
        self.eufy_advantages = [
            'local storage', 'privacy', 'no monthly fees', 'homebase',
            '365 day battery', 'solar panel', 'encrypted', 'offline'
        ]
        
        self.eufy_competitors = {
            'ring': ['amazon', 'echo', 'alexa', 'subscription'],
            'arlo': ['netgear', 'cloud only', 'subscription required'],
            'nest': ['google', 'nest aware', 'subscription'],
            'wyze': ['cloud', 'subscription'],
            'blink': ['amazon', 'cloud storage']
        }
        
        # High-priority Eufy keywords for audit
        self.priority_keywords = [
            "best security camera 2024",
            "wireless security camera",
            "home security camera system", 
            "battery security camera",
            "privacy security camera",
            "local storage security camera",
            "eufy vs ring",
            "eufy vs arlo", 
            "eufy vs nest",
            "security camera without subscription",
            "DIY security camera",
            "solar security camera"
        ]

    def audit_eufy_content(self, urls: List[str]) -> List[EufyContentAudit]:
        """Comprehensive audit of Eufy content pages"""
        audit_results = []
        
        for url in urls:
            logger.info(f"Auditing: {url}")
            
            # Analyze content with optimization engine
            analysis = self.optimization_engine.analyze_content(url)
            
            if not analysis:
                logger.warning(f"Could not analyze {url}")
                continue
            
            # Perform Eufy-specific analysis
            audit_result = self._analyze_eufy_content(analysis)
            audit_results.append(audit_result)
        
        # Sort by priority and optimization potential
        audit_results.sort(key=lambda x: (x.priority_level == 'high', x.optimization_potential), reverse=True)
        
        return audit_results

    def _analyze_eufy_content(self, analysis: ContentAnalysis) -> EufyContentAudit:
        """Analyze content specifically for Eufy brand optimization"""
        
        # Determine page type
        page_type = self._classify_page_type(analysis.url, analysis.title)
        
        # Calculate optimization potential
        optimization_potential = self._calculate_optimization_potential(analysis)
        
        # Determine priority level
        priority_level = self._determine_priority_level(analysis, optimization_potential)
        
        # Generate Eufy-specific recommendations
        specific_recommendations = self._generate_eufy_recommendations(analysis)
        
        # Identify competitive gaps
        competitive_gaps = self._identify_eufy_competitive_gaps(analysis)
        
        # Check for technical issues
        technical_issues = self._check_technical_issues(analysis)
        
        # Estimate impact and time
        estimated_impact = self._estimate_optimization_impact(analysis, optimization_potential)
        time_to_optimize = self._estimate_optimization_time(specific_recommendations)
        
        return EufyContentAudit(
            url=analysis.url,
            page_type=page_type,
            current_geo_score=analysis.geo_score,
            optimization_potential=optimization_potential,
            priority_level=priority_level,
            specific_recommendations=specific_recommendations,
            competitive_gaps=competitive_gaps,
            technical_issues=technical_issues,
            estimated_impact=estimated_impact,
            time_to_optimize=time_to_optimize
        )

    def _classify_page_type(self, url: str, title: str) -> str:
        """Classify the type of content page"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if any(term in url_lower for term in ['product', 'camera', 'doorbell']):
            return 'Product Page'
        elif any(term in title_lower for term in ['vs', 'comparison', 'compare']):
            return 'Comparison'
        elif any(term in title_lower for term in ['how to', 'guide', 'setup', 'install']):
            return 'Tutorial/Guide'
        elif any(term in title_lower for term in ['review', 'test', 'best']):
            return 'Review/Roundup'
        elif any(term in url_lower for term in ['blog', 'article', 'news']):
            return 'Blog/Article'
        elif any(term in url_lower for term in ['support', 'help', 'faq']):
            return 'Support/FAQ'
        else:
            return 'Other'

    def _calculate_optimization_potential(self, analysis: ContentAnalysis) -> float:
        """Calculate potential for GEO optimization improvement"""
        current_score = analysis.geo_score
        max_possible = 100
        
        # Base potential is inverse of current score
        base_potential = max_possible - current_score
        
        # Adjust based on content characteristics
        potential_multiplier = 1.0
        
        # High word count content has more optimization potential
        if analysis.word_count > 1500:
            potential_multiplier += 0.2
        elif analysis.word_count < 500:
            potential_multiplier -= 0.3
        
        # Content with existing structure is easier to optimize
        if len(analysis.missing_elements) < 3:
            potential_multiplier += 0.1
        
        # Content with many gaps has higher potential but requires more work
        if len(analysis.missing_elements) > 5:
            potential_multiplier += 0.3
        
        final_potential = min(100, base_potential * potential_multiplier)
        return round(final_potential, 1)

    def _determine_priority_level(self, analysis: ContentAnalysis, optimization_potential: float) -> str:
        """Determine optimization priority level"""
        
        # High priority criteria
        if (optimization_potential > 40 and analysis.geo_score < 60) or \
           any(keyword in analysis.title.lower() for keyword in ['best', 'vs', 'comparison', 'review']):
            return 'high'
        
        # Medium priority criteria  
        elif optimization_potential > 25 and analysis.word_count > 800:
            return 'medium'
        
        # Low priority
        else:
            return 'low'

    def _generate_eufy_recommendations(self, analysis: ContentAnalysis) -> List[str]:
        """Generate Eufy-specific optimization recommendations"""
        recommendations = []
        
        # Get base recommendations from optimization engine
        base_recommendations = [rec['suggestion'] for rec in analysis.optimization_suggestions]
        
        # Add Eufy-specific recommendations
        content_text = ""  # Would need actual content text for full analysis
        
        # Privacy and local storage emphasis
        if not any('privacy' in rec.lower() for rec in base_recommendations):
            recommendations.append("Emphasize privacy advantages and local storage benefits")
        
        # Battery life differentiation  
        recommendations.append("Highlight 365-day battery life and solar panel integration")
        
        # No subscription model
        recommendations.append("Emphasize no monthly fees vs. competitor subscription models")
        
        # HomeBase ecosystem
        recommendations.append("Feature HomeBase hub benefits and ecosystem integration")
        
        # DIY installation
        recommendations.append("Add DIY installation guides and ease-of-setup content")
        
        # Competitive comparison
        if analysis.page_type != 'Comparison':
            recommendations.append("Add comparison elements with Ring, Arlo, and Nest")
        
        # Technical specifications
        recommendations.append("Include specific technical specs (resolution, field of view, etc.)")
        
        # User scenarios
        recommendations.append("Add real-world use case scenarios and customer testimonials")
        
        return recommendations[:6]  # Return top 6 recommendations

    def _identify_eufy_competitive_gaps(self, analysis: ContentAnalysis) -> List[str]:
        """Identify competitive gaps specific to Eufy"""
        gaps = []
        
        # Based on competitive analysis, common gaps for Eufy content:
        gaps.extend([
            "Missing direct comparison with Ring (market leader)",
            "Not emphasizing privacy advantage over Amazon Ring",
            "Insufficient battery life advantage positioning", 
            "Missing 'no subscription' value proposition",
            "Lack of local storage security benefits explanation",
            "No HomeBase ecosystem differentiation",
            "Missing solar panel integration benefits",
            "Insufficient DIY/ease of installation emphasis"
        ])
        
        # Return most relevant gaps based on content type
        if analysis.page_type == 'Product Page':
            return gaps[:4]
        elif analysis.page_type == 'Comparison':
            return gaps[1:5]
        else:
            return gaps[:3]

    def _check_technical_issues(self, analysis: ContentAnalysis) -> List[str]:
        """Check for technical SEO issues affecting GEO performance"""
        issues = []
        
        # Schema markup issues
        if len(analysis.schema_recommendations) > 0:
            issues.append("Missing or incomplete schema markup")
        
        # Content structure issues
        if analysis.word_count < 300:
            issues.append("Content too short for comprehensive GEO optimization")
        
        if analysis.readability_score < 30:
            issues.append("Poor readability score may hurt AI Overview selection")
        
        # Missing critical elements
        if len(analysis.missing_elements) > 5:
            issues.append("Multiple critical GEO elements missing")
        
        # URL and title optimization
        if not any(keyword in analysis.title.lower() for keyword in self.priority_keywords):
            issues.append("Title not optimized for target keywords")
        
        return issues

    def _estimate_optimization_impact(self, analysis: ContentAnalysis, potential: float) -> str:
        """Estimate the impact of optimization efforts"""
        
        if potential > 50 and analysis.geo_score < 40:
            return "High - Could achieve 60%+ GEO score with optimization"
        elif potential > 30 and analysis.geo_score < 60:
            return "Medium - Could improve GEO score by 20-30 points"
        elif potential > 15:
            return "Low-Medium - Modest improvements possible"
        else:
            return "Low - Limited optimization potential"

    def _estimate_optimization_time(self, recommendations: List[str]) -> str:
        """Estimate time required for optimization"""
        
        num_recommendations = len(recommendations)
        
        if num_recommendations >= 6:
            return "4-6 hours"
        elif num_recommendations >= 4:
            return "2-4 hours"
        elif num_recommendations >= 2:
            return "1-2 hours"
        else:
            return "30-60 minutes"

    def generate_audit_report(self, audit_results: List[EufyContentAudit], output_file: str = None) -> Dict:
        """Generate comprehensive audit report"""
        
        # Calculate summary statistics
        total_pages = len(audit_results)
        high_priority = len([r for r in audit_results if r.priority_level == 'high'])
        medium_priority = len([r for r in audit_results if r.priority_level == 'medium'])
        low_priority = len([r for r in audit_results if r.priority_level == 'low'])
        
        avg_geo_score = sum(r.current_geo_score for r in audit_results) / total_pages if total_pages > 0 else 0
        avg_potential = sum(r.optimization_potential for r in audit_results) / total_pages if total_pages > 0 else 0
        
        # Identify most common gaps
        all_gaps = []
        for result in audit_results:
            all_gaps.extend(result.competitive_gaps)
        
        gap_frequency = {}
        for gap in all_gaps:
            gap_frequency[gap] = gap_frequency.get(gap, 0) + 1
        
        common_gaps = sorted(gap_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Generate recommendations by priority
        high_priority_pages = [r for r in audit_results if r.priority_level == 'high']
        medium_priority_pages = [r for r in audit_results if r.priority_level == 'medium']
        
        report = {
            'summary': {
                'total_pages_audited': total_pages,
                'average_geo_score': round(avg_geo_score, 1),
                'average_optimization_potential': round(avg_potential, 1),
                'priority_breakdown': {
                    'high': high_priority,
                    'medium': medium_priority,
                    'low': low_priority
                }
            },
            'key_findings': {
                'most_common_gaps': [gap[0] for gap in common_gaps],
                'pages_needing_immediate_attention': len(high_priority_pages),
                'estimated_total_optimization_time': self._calculate_total_time(audit_results)
            },
            'action_plan': {
                'phase_1_high_priority': [
                    {
                        'url': r.url,
                        'page_type': r.page_type,
                        'current_score': r.current_geo_score,
                        'potential_improvement': r.optimization_potential,
                        'top_recommendations': r.specific_recommendations[:3],
                        'estimated_time': r.time_to_optimize
                    }
                    for r in high_priority_pages[:5]
                ],
                'phase_2_medium_priority': [
                    {
                        'url': r.url,
                        'page_type': r.page_type,
                        'potential_improvement': r.optimization_potential
                    }
                    for r in medium_priority_pages[:10]
                ]
            },
            'detailed_results': [asdict(result) for result in audit_results]
        }
        
        # Save report if output file specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Audit report saved to {output_file}")
        
        return report

    def _calculate_total_time(self, audit_results: List[EufyContentAudit]) -> str:
        """Calculate total estimated optimization time"""
        
        time_mapping = {
            "30-60 minutes": 45,
            "1-2 hours": 90,
            "2-4 hours": 180,
            "4-6 hours": 300
        }
        
        total_minutes = 0
        for result in audit_results:
            total_minutes += time_mapping.get(result.time_to_optimize, 90)
        
        total_hours = total_minutes / 60
        
        if total_hours < 8:
            return f"{total_hours:.1f} hours"
        elif total_hours < 40:
            return f"{total_hours/8:.1f} working days"
        else:
            return f"{total_hours/40:.1f} working weeks"

    def export_to_csv(self, audit_results: List[EufyContentAudit], filename: str):
        """Export audit results to CSV for easy analysis"""
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'url', 'page_type', 'current_geo_score', 'optimization_potential',
                'priority_level', 'estimated_impact', 'time_to_optimize',
                'top_recommendation_1', 'top_recommendation_2', 'top_recommendation_3',
                'main_competitive_gap', 'technical_issues'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in audit_results:
                row = {
                    'url': result.url,
                    'page_type': result.page_type,
                    'current_geo_score': result.current_geo_score,
                    'optimization_potential': result.optimization_potential,
                    'priority_level': result.priority_level,
                    'estimated_impact': result.estimated_impact,
                    'time_to_optimize': result.time_to_optimize,
                    'top_recommendation_1': result.specific_recommendations[0] if len(result.specific_recommendations) > 0 else '',
                    'top_recommendation_2': result.specific_recommendations[1] if len(result.specific_recommendations) > 1 else '',
                    'top_recommendation_3': result.specific_recommendations[2] if len(result.specific_recommendations) > 2 else '',
                    'main_competitive_gap': result.competitive_gaps[0] if result.competitive_gaps else '',
                    'technical_issues': '; '.join(result.technical_issues)
                }
                writer.writerow(row)
        
        logger.info(f"Audit results exported to {filename}")

def main():
    """Example usage of Eufy Content Auditor"""
    
    # Initialize auditor
    auditor = EufyGEOAuditor()
    
    # Example Eufy URLs to audit (would be actual URLs in real usage)
    eufy_urls = [
        "https://www.eufy.com/products/security-cameras",
        "https://www.eufy.com/blog/best-security-camera-features",
        "https://www.eufy.com/support/security-camera-setup",
        "https://www.eufy.com/products/eufy-cam-2c",
        "https://www.eufy.com/blog/eufy-vs-ring-comparison"
    ]
    
    print("Starting Eufy Content GEO Audit...")
    print(f"Auditing {len(eufy_urls)} pages...")
    
    # Perform audit
    audit_results = auditor.audit_eufy_content(eufy_urls)
    
    # Generate report
    report = auditor.generate_audit_report(audit_results, "eufy_geo_audit_report.json")
    
    # Export to CSV
    auditor.export_to_csv(audit_results, "eufy_geo_audit_results.csv")
    
    # Print summary
    print("\n" + "="*60)
    print("EUFY CONTENT GEO AUDIT SUMMARY")
    print("="*60)
    print(f"Total Pages Audited: {report['summary']['total_pages_audited']}")
    print(f"Average GEO Score: {report['summary']['average_geo_score']}/100")
    print(f"Average Optimization Potential: {report['summary']['average_optimization_potential']}/100")
    print(f"\nPriority Breakdown:")
    print(f"  High Priority: {report['summary']['priority_breakdown']['high']} pages")
    print(f"  Medium Priority: {report['summary']['priority_breakdown']['medium']} pages")
    print(f"  Low Priority: {report['summary']['priority_breakdown']['low']} pages")
    print(f"\nEstimated Total Optimization Time: {report['key_findings']['estimated_total_optimization_time']}")
    
    print(f"\nMost Common Content Gaps:")
    for i, gap in enumerate(report['key_findings']['most_common_gaps'][:3], 1):
        print(f"  {i}. {gap}")
    
    print(f"\nTop Priority Pages for Immediate Optimization:")
    for page in report['action_plan']['phase_1_high_priority'][:3]:
        print(f"  • {page['page_type']}: {page['current_score']}/100 → +{page['potential_improvement']} potential")
        print(f"    Time: {page['estimated_time']}")
        print(f"    Top rec: {page['top_recommendations'][0] if page['top_recommendations'] else 'N/A'}")
        print()

if __name__ == "__main__":
    main()