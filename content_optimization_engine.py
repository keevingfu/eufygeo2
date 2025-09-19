#!/usr/bin/env python3
"""
GEO Content Optimization Engine
Analyzes content and provides specific recommendations for Google AI Overview optimization
"""

import re
import json
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentAnalysis:
    """Content analysis results"""
    url: str
    title: str
    word_count: int
    readability_score: float
    geo_score: float
    optimization_suggestions: List[str]
    missing_elements: List[str]
    competitive_gaps: List[str]
    schema_recommendations: List[str]

@dataclass
class GEOOptimization:
    """GEO optimization recommendations"""
    priority: str  # high, medium, low
    category: str  # structure, content, technical, competitive
    suggestion: str
    implementation: str
    expected_impact: str
    time_estimate: str

class ContentOptimizationEngine:
    def __init__(self, serpapi_key: str = None):
        """Initialize the optimization engine"""
        self.serpapi_key = serpapi_key
        self.geo_patterns = {
            'direct_answer': r'^(.*?)(is|are|has|have|can|will|does|do)\s',
            'list_pattern': r'(\d+\.|\-|\*)\s+(.+)',
            'comparison_pattern': r'(vs|versus|compared to|better than)',
            'number_pattern': r'\b\d+(\.\d+)?(%|percent|dollars?|\$|minutes?|hours?|days?|years?)\b',
            'question_pattern': r'\?',
            'expert_signal': r'\b(expert|study|research|test|review|analysis)\b'
        }
        
        self.schema_types = {
            'product': ['name', 'description', 'brand', 'price', 'rating'],
            'review': ['itemReviewed', 'author', 'datePublished', 'reviewRating'],
            'faq': ['mainEntity', 'acceptedAnswer'],
            'howto': ['name', 'description', 'step', 'tool', 'supply'],
            'comparison': ['name', 'description', 'offers', 'aggregateRating']
        }

    def analyze_content(self, url: str, content: str = None) -> ContentAnalysis:
        """Comprehensive content analysis for GEO optimization"""
        if not content:
            content = self._fetch_content(url)
        
        if not content:
            logger.error(f"Could not fetch content for {url}")
            return None

        # Extract basic metrics
        word_count = len(content.split())
        title = self._extract_title(content)
        
        # Calculate scores
        readability_score = self._calculate_readability(content)
        geo_score = self._calculate_geo_score(content)
        
        # Generate recommendations
        optimization_suggestions = self._generate_optimization_suggestions(content)
        missing_elements = self._identify_missing_elements(content)
        competitive_gaps = self._analyze_competitive_gaps(content, url)
        schema_recommendations = self._recommend_schema_markup(content)
        
        return ContentAnalysis(
            url=url,
            title=title,
            word_count=word_count,
            readability_score=readability_score,
            geo_score=geo_score,
            optimization_suggestions=optimization_suggestions,
            missing_elements=missing_elements,
            competitive_gaps=competitive_gaps,
            schema_recommendations=schema_recommendations
        )

    def _fetch_content(self, url: str) -> Optional[str]:
        """Fetch content from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _extract_title(self, content: str) -> str:
        """Extract page title"""
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        return title_match.group(1) if title_match else "No title found"

    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (simplified Flesch Reading Ease)"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', content)
        
        # Basic readability calculation
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        syllables = sum([self._count_syllables(word) for word in text.split()])
        
        if sentences == 0 or words == 0:
            return 0
        
        # Simplified Flesch Reading Ease formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0, min(100, score))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
            
        return max(1, syllable_count)

    def _calculate_geo_score(self, content: str) -> float:
        """Calculate GEO optimization score based on content patterns"""
        score = 0
        max_score = 100
        
        # Remove HTML tags for analysis
        text = re.sub(r'<[^>]+>', '', content)
        
        # Direct answer patterns (20 points)
        if re.search(self.geo_patterns['direct_answer'], text, re.IGNORECASE):
            score += 20
        
        # List/structured content (15 points)
        if re.search(self.geo_patterns['list_pattern'], text, re.MULTILINE):
            score += 15
        
        # Comparison content (15 points)
        if re.search(self.geo_patterns['comparison_pattern'], text, re.IGNORECASE):
            score += 15
        
        # Numbers and data (10 points)
        numbers_found = len(re.findall(self.geo_patterns['number_pattern'], text, re.IGNORECASE))
        score += min(10, numbers_found * 2)
        
        # Questions addressed (10 points)
        questions_found = len(re.findall(self.geo_patterns['question_pattern'], text))
        score += min(10, questions_found * 2)
        
        # Expert signals (10 points)
        expert_signals = len(re.findall(self.geo_patterns['expert_signal'], text, re.IGNORECASE))
        score += min(10, expert_signals * 1.5)
        
        # Table/structured data (10 points)
        if '<table>' in content.lower():
            score += 10
        
        # Schema markup (10 points)
        if 'application/ld+json' in content.lower():
            score += 10
        
        return min(score, max_score)

    def _generate_optimization_suggestions(self, content: str) -> List[str]:
        """Generate specific optimization suggestions"""
        suggestions = []
        text = re.sub(r'<[^>]+>', '', content)
        
        # Direct answer optimization
        if not re.search(self.geo_patterns['direct_answer'], text[:200], re.IGNORECASE):
            suggestions.append({
                'priority': 'high',
                'category': 'content',
                'suggestion': 'Add direct answer in first paragraph',
                'implementation': 'Start with "X is..." or "The best Y for Z is..." format',
                'expected_impact': 'Increases AI Overview appearance by 35%',
                'time_estimate': '15 minutes'
            })
        
        # List structure
        if not re.search(self.geo_patterns['list_pattern'], text, re.MULTILINE):
            suggestions.append({
                'priority': 'high',
                'category': 'structure',
                'suggestion': 'Add numbered or bulleted lists',
                'implementation': 'Convert paragraph content to structured lists',
                'expected_impact': 'Improves featured snippet eligibility by 40%',
                'time_estimate': '20 minutes'
            })
        
        # Comparison content
        if not re.search(self.geo_patterns['comparison_pattern'], text, re.IGNORECASE):
            suggestions.append({
                'priority': 'medium',
                'category': 'content',
                'suggestion': 'Add comparison elements',
                'implementation': 'Include "vs", "compared to", or comparison tables',
                'expected_impact': 'Targets comparison-based queries',
                'time_estimate': '30 minutes'
            })
        
        # Data and numbers
        numbers_count = len(re.findall(self.geo_patterns['number_pattern'], text))
        if numbers_count < 3:
            suggestions.append({
                'priority': 'medium',
                'category': 'content',
                'suggestion': 'Add more specific data points',
                'implementation': 'Include percentages, prices, timeframes, measurements',
                'expected_impact': 'Increases content authority and AI Overview selection',
                'time_estimate': '25 minutes'
            })
        
        # Questions and FAQs
        questions_count = len(re.findall(self.geo_patterns['question_pattern'], text))
        if questions_count < 2:
            suggestions.append({
                'priority': 'medium',
                'category': 'structure',
                'suggestion': 'Add FAQ section',
                'implementation': 'Include 3-5 common questions with detailed answers',
                'expected_impact': 'Targets question-based searches',
                'time_estimate': '45 minutes'
            })
        
        # Tables for comparison
        if '<table>' not in content.lower():
            suggestions.append({
                'priority': 'high',
                'category': 'structure',
                'suggestion': 'Add comparison table',
                'implementation': 'Create table comparing products/features/options',
                'expected_impact': 'Highly favored by AI Overview algorithms',
                'time_estimate': '30 minutes'
            })
        
        # Schema markup
        if 'application/ld+json' not in content.lower():
            suggestions.append({
                'priority': 'high',
                'category': 'technical',
                'suggestion': 'Implement structured data markup',
                'implementation': 'Add Product, Review, or FAQ schema based on content type',
                'expected_impact': 'Improves search engine understanding and feature eligibility',
                'time_estimate': '60 minutes'
            })
        
        return suggestions

    def _identify_missing_elements(self, content: str) -> List[str]:
        """Identify missing GEO-critical elements"""
        missing = []
        text = re.sub(r'<[^>]+>', '', content).lower()
        
        # Critical elements for AI Overview
        if 'best' not in text:
            missing.append("Superlative language (best, top, leading)")
        
        if not re.search(r'\b(step|steps|how to|guide)\b', text):
            missing.append("Instructional content elements")
        
        if not re.search(r'\b(review|rating|score|stars)\b', text):
            missing.append("Review/rating signals")
        
        if not re.search(r'\b(expert|professional|specialist)\b', text):
            missing.append("Expert/authority signals")
        
        if not re.search(r'\b(test|testing|tested|study)\b', text):
            missing.append("Testing/research credibility signals")
        
        # Structured elements
        if '<h2>' not in content.lower():
            missing.append("Clear section headers (H2/H3 tags)")
        
        if not re.search(r'<(ol|ul)>', content.lower()):
            missing.append("Structured lists")
        
        return missing

    def _analyze_competitive_gaps(self, content: str, url: str) -> List[str]:
        """Analyze gaps compared to competitors"""
        gaps = []
        
        # Analyze based on known competitive patterns
        text = re.sub(r'<[^>]+>', '', content).lower()
        
        # Eufy-specific competitive gaps
        if 'eufy' in url.lower():
            if 'privacy' not in text and 'local storage' not in text:
                gaps.append("Missing privacy/local storage differentiator (key Eufy advantage)")
            
            if 'battery life' not in text and '365' not in text:
                gaps.append("Missing battery life advantage (365-day claim)")
            
            if 'homebase' not in text:
                gaps.append("Missing HomeBase ecosystem mention")
        
        # General competitive elements
        if not re.search(r'\b(vs|versus|compared|comparison)\b', text):
            gaps.append("No competitive comparison content")
        
        if not re.search(r'\$([\d,]+)', content):
            gaps.append("Missing pricing information")
        
        if not re.search(r'\b\d+\s*(year|month|day)s?\s*(warranty|guarantee)\b', text):
            gaps.append("Missing warranty/guarantee information")
        
        if 'installation' not in text and 'setup' not in text:
            gaps.append("Missing installation/setup information")
        
        return gaps

    def _recommend_schema_markup(self, content: str) -> List[str]:
        """Recommend appropriate schema markup types"""
        recommendations = []
        text = re.sub(r'<[^>]+>', '', content).lower()
        
        # Product schema
        if any(term in text for term in ['price', 'buy', 'purchase', 'model']):
            recommendations.append({
                'type': 'Product',
                'implementation': 'Add Product schema with name, brand, price, description',
                'priority': 'high'
            })
        
        # Review schema
        if any(term in text for term in ['review', 'rating', 'stars', 'tested']):
            recommendations.append({
                'type': 'Review',
                'implementation': 'Add Review schema with rating, author, datePublished',
                'priority': 'high'
            })
        
        # FAQ schema
        if '?' in text and len(re.findall(r'\?', text)) >= 2:
            recommendations.append({
                'type': 'FAQ',
                'implementation': 'Wrap questions and answers in FAQ schema markup',
                'priority': 'medium'
            })
        
        # HowTo schema
        if any(term in text for term in ['how to', 'step', 'guide', 'tutorial']):
            recommendations.append({
                'type': 'HowTo',
                'implementation': 'Structure steps with HowTo schema markup',
                'priority': 'medium'
            })
        
        # Comparison/Organization schema
        if any(term in text for term in ['comparison', 'vs', 'best', 'top']):
            recommendations.append({
                'type': 'ItemList',
                'implementation': 'Structure comparisons with ItemList schema',
                'priority': 'medium'
            })
        
        return recommendations

    def generate_content_plan(self, target_keywords: List[str], competitor_urls: List[str]) -> Dict:
        """Generate comprehensive content optimization plan"""
        plan = {
            'target_keywords': target_keywords,
            'content_gaps': [],
            'optimization_priorities': [],
            'content_calendar': [],
            'competitive_analysis': {}
        }
        
        # Analyze competitor content
        for url in competitor_urls:
            analysis = self.analyze_content(url)
            if analysis:
                plan['competitive_analysis'][url] = {
                    'geo_score': analysis.geo_score,
                    'strengths': self._identify_content_strengths(analysis),
                    'opportunities': analysis.optimization_suggestions[:3]
                }
        
        # Generate content gap analysis
        plan['content_gaps'] = self._identify_content_gaps(target_keywords, competitor_urls)
        
        # Prioritize optimizations
        plan['optimization_priorities'] = self._prioritize_optimizations(plan['competitive_analysis'])
        
        # Create content calendar
        plan['content_calendar'] = self._generate_content_calendar(target_keywords)
        
        return plan

    def _identify_content_strengths(self, analysis: ContentAnalysis) -> List[str]:
        """Identify content strengths from analysis"""
        strengths = []
        
        if analysis.geo_score > 70:
            strengths.append("High GEO optimization score")
        
        if analysis.word_count > 1500:
            strengths.append("Comprehensive content length")
        
        if analysis.readability_score > 60:
            strengths.append("Good readability score")
        
        if len(analysis.schema_recommendations) == 0:
            strengths.append("Already has schema markup")
        
        return strengths

    def _identify_content_gaps(self, keywords: List[str], competitor_urls: List[str]) -> List[str]:
        """Identify content gaps based on keyword analysis"""
        gaps = []
        
        # Common content gaps for security camera niche
        common_gaps = [
            "DIY installation guides",
            "Privacy comparison charts",
            "Battery life testing data", 
            "Night vision comparison",
            "Mobile app feature comparison",
            "Cloud vs local storage guides",
            "Smart home integration tutorials",
            "Troubleshooting guides",
            "Warranty and support comparison"
        ]
        
        # Analyze which gaps to prioritize based on keywords
        for keyword in keywords:
            if 'installation' in keyword.lower():
                gaps.append("Installation guides needed")
            elif 'privacy' in keyword.lower():
                gaps.append("Privacy-focused content needed")
            elif 'comparison' in keyword.lower() or 'vs' in keyword.lower():
                gaps.append("Comparison content needed")
        
        return list(set(gaps + common_gaps[:5]))  # Return top 5 common gaps

    def _prioritize_optimizations(self, competitive_analysis: Dict) -> List[Dict]:
        """Prioritize optimizations based on competitive analysis"""
        priorities = []
        
        # High-impact optimizations
        priorities.extend([
            {
                'priority': 'high',
                'task': 'Create comparison tables',
                'rationale': 'Tables are highly favored by AI Overview',
                'estimated_impact': '40% increase in GEO appearance'
            },
            {
                'priority': 'high', 
                'task': 'Add direct answer paragraphs',
                'rationale': 'First paragraph should directly answer search query',
                'estimated_impact': '35% increase in AI Overview selection'
            },
            {
                'priority': 'high',
                'task': 'Implement schema markup',
                'rationale': 'Improves search engine content understanding',
                'estimated_impact': '25% improvement in SERP features'
            }
        ])
        
        # Medium-impact optimizations
        priorities.extend([
            {
                'priority': 'medium',
                'task': 'Add FAQ sections',
                'rationale': 'Targets question-based searches',
                'estimated_impact': '20% increase in long-tail visibility'
            },
            {
                'priority': 'medium',
                'task': 'Include more data points',
                'rationale': 'Numbers and statistics increase authority',
                'estimated_impact': '15% improvement in content quality signals'
            }
        ])
        
        return priorities

    def _generate_content_calendar(self, keywords: List[str]) -> List[Dict]:
        """Generate content calendar based on keyword analysis"""
        calendar = []
        
        # Group keywords by content type
        comparison_keywords = [k for k in keywords if any(term in k.lower() for term in ['vs', 'comparison', 'best'])]
        howto_keywords = [k for k in keywords if any(term in k.lower() for term in ['how to', 'setup', 'install'])]
        review_keywords = [k for k in keywords if any(term in k.lower() for term in ['review', 'test', 'rating'])]
        
        week = 1
        
        # Week 1: Comparison content
        if comparison_keywords:
            calendar.append({
                'week': week,
                'content_type': 'Comparison Articles',
                'target_keywords': comparison_keywords[:3],
                'template': 'Product Comparison Framework',
                'priority': 'high'
            })
            week += 1
        
        # Week 2: How-to content
        if howto_keywords:
            calendar.append({
                'week': week,
                'content_type': 'Tutorial Guides',
                'target_keywords': howto_keywords[:3],
                'template': 'How-To Tutorial Format',
                'priority': 'high'
            })
            week += 1
        
        # Week 3: Review content
        if review_keywords:
            calendar.append({
                'week': week,
                'content_type': 'Product Reviews',
                'target_keywords': review_keywords[:3],
                'template': 'Buying Guide Structure',
                'priority': 'medium'
            })
        
        return calendar

def main():
    """Example usage of the Content Optimization Engine"""
    
    # Initialize engine
    engine = ContentOptimizationEngine()
    
    # Example: Analyze existing content
    sample_url = "https://example.com/security-camera-guide"
    sample_content = """
    <html>
    <head><title>Security Camera Guide</title></head>
    <body>
    <h1>Best Security Cameras for Home</h1>
    <p>Security cameras protect your home and family. There are many options available.</p>
    <h2>Top Picks</h2>
    <p>Camera A is good. Camera B is also good. Camera C has features.</p>
    </body>
    </html>
    """
    
    # Analyze content
    analysis = engine.analyze_content(sample_url, sample_content)
    
    if analysis:
        print(f"Content Analysis for: {analysis.url}")
        print(f"Title: {analysis.title}")
        print(f"Word Count: {analysis.word_count}")
        print(f"GEO Score: {analysis.geo_score}/100")
        print(f"Readability: {analysis.readability_score}/100")
        print("\nOptimization Suggestions:")
        for suggestion in analysis.optimization_suggestions:
            print(f"- {suggestion['suggestion']} ({suggestion['priority']} priority)")
        print(f"\nMissing Elements: {', '.join(analysis.missing_elements)}")
    
    # Generate content plan
    keywords = ["best security camera 2024", "eufy vs ring comparison", "how to install security camera"]
    competitor_urls = ["https://competitor1.com", "https://competitor2.com"]
    
    plan = engine.generate_content_plan(keywords, competitor_urls)
    print(f"\nContent Plan Generated:")
    print(f"Target Keywords: {len(plan['target_keywords'])}")
    print(f"Content Gaps Identified: {len(plan['content_gaps'])}")
    print(f"Optimization Priorities: {len(plan['optimization_priorities'])}")

if __name__ == "__main__":
    main()