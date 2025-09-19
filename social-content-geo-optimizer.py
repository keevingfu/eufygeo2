#!/usr/bin/env python3
"""
社交内容GEO优化工具
专为TikTok、Instagram、YouTube等社交平台的AI推荐引擎优化内容
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum
import cv2
import librosa
import nltk
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import hashlib


class SocialPlatform(Enum):
    """社交平台枚举"""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    PINTEREST = "pinterest"


class ContentType(Enum):
    """内容类型枚举"""
    VIDEO_SHORT = "video_short"  # 短视频（<60s）
    VIDEO_LONG = "video_long"    # 长视频（>60s）
    IMAGE_POST = "image_post"    # 图片帖子
    CAROUSEL = "carousel"        # 轮播图
    STORY = "story"             # 快拍/故事
    REEL = "reel"               # Reels
    LIVE = "live"               # 直播


@dataclass
class SocialOptimizationResult:
    """社交内容优化结果"""
    platform: SocialPlatform
    content_type: ContentType
    original_content: Dict
    optimized_content: Dict
    ai_recommendation_score: float  # AI推荐概率得分
    first_3_seconds_score: float    # 首3秒留存得分
    completion_rate_prediction: float  # 预测完播率
    engagement_prediction: float     # 预测互动率
    viral_potential_score: float    # 病毒传播潜力分数
    optimization_suggestions: List[Dict]
    metadata_enhancements: Dict
    hashtag_recommendations: List[str]
    timing_recommendations: Dict


class VideoAnalyzer:
    """视频内容分析器"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.emotion_analyzer = pipeline("image-classification", model="dima806/facial_emotions_image_detection")
        
    def analyze_first_3_seconds(self, video_path: str) -> Dict[str, float]:
        """分析视频前3秒的关键指标"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        metrics = {
            'motion_intensity': 0.0,
            'visual_complexity': 0.0,
            'face_presence': 0.0,
            'emotion_intensity': 0.0,
            'scene_changes': 0,
            'hook_strength': 0.0
        }
        
        frames_to_analyze = int(fps * 3)  # 前3秒的帧数
        prev_frame = None
        motion_scores = []
        complexity_scores = []
        
        for i in range(frames_to_analyze):
            ret, frame = cap.read()
            if not ret:
                break
                
            # 运动强度分析
            if prev_frame is not None:
                motion = cv2.absdiff(prev_frame, frame)
                motion_score = np.mean(motion)
                motion_scores.append(motion_score)
            
            # 视觉复杂度分析
            edges = cv2.Canny(frame, 100, 200)
            complexity = np.sum(edges > 0) / edges.size
            complexity_scores.append(complexity)
            
            # 人脸检测
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                metrics['face_presence'] += 1 / frames_to_analyze
                
                # 情绪分析（每10帧分析一次以提高性能）
                if i % 10 == 0:
                    try:
                        # 裁剪人脸区域
                        x, y, w, h = faces[0]
                        face_img = frame[y:y+h, x:x+w]
                        emotions = self.emotion_analyzer(face_img)
                        if emotions:
                            # 计算情绪强度
                            emotion_score = max([e['score'] for e in emotions])
                            metrics['emotion_intensity'] = max(metrics['emotion_intensity'], emotion_score)
                    except:
                        pass
            
            # 场景变化检测
            if prev_frame is not None and i % 5 == 0:
                hist_diff = self._compare_histograms(prev_frame, frame)
                if hist_diff > 0.5:
                    metrics['scene_changes'] += 1
            
            prev_frame = frame
        
        cap.release()
        
        # 计算综合指标
        metrics['motion_intensity'] = np.mean(motion_scores) if motion_scores else 0
        metrics['visual_complexity'] = np.mean(complexity_scores) if complexity_scores else 0
        
        # 计算钩子强度（综合评分）
        metrics['hook_strength'] = self._calculate_hook_strength(metrics)
        
        return metrics
    
    def _compare_histograms(self, frame1, frame2):
        """比较两帧的直方图差异"""
        hist1 = cv2.calcHist([frame1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist2 = cv2.calcHist([frame2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()
        
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR_ALT)
    
    def _calculate_hook_strength(self, metrics: Dict) -> float:
        """计算视频钩子强度"""
        weights = {
            'motion_intensity': 0.25,
            'visual_complexity': 0.20,
            'face_presence': 0.30,
            'emotion_intensity': 0.15,
            'scene_changes': 0.10
        }
        
        # 归一化场景变化数（理想值为1-2次）
        scene_change_score = min(metrics['scene_changes'] / 2, 1.0)
        
        hook_score = (
            metrics['motion_intensity'] * weights['motion_intensity'] +
            metrics['visual_complexity'] * weights['visual_complexity'] +
            metrics['face_presence'] * weights['face_presence'] +
            metrics['emotion_intensity'] * weights['emotion_intensity'] +
            scene_change_score * weights['scene_changes']
        )
        
        return min(hook_score, 1.0)


class AudioAnalyzer:
    """音频内容分析器"""
    
    def __init__(self):
        self.sample_rate = 22050
        
    def analyze_audio_hooks(self, audio_path: str) -> Dict[str, float]:
        """分析音频钩子元素"""
        # 加载音频
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        metrics = {
            'beat_strength': self._analyze_beat_strength(y, sr),
            'onset_density': self._analyze_onset_density(y, sr),
            'energy_variation': self._analyze_energy_variation(y, sr),
            'trending_audio_match': self._check_trending_audio_match(y, sr),
            'vocal_clarity': self._analyze_vocal_clarity(y, sr)
        }
        
        return metrics
    
    def _analyze_beat_strength(self, y, sr):
        """分析节奏强度"""
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_strength = len(beats) / (len(y) / sr)  # 每秒节拍数
        return min(beat_strength / 4, 1.0)  # 归一化到0-1
    
    def _analyze_onset_density(self, y, sr):
        """分析音频起始密度"""
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_density = len(onset_frames) / (len(y) / sr)
        return min(onset_density / 10, 1.0)
    
    def _analyze_energy_variation(self, y, sr):
        """分析能量变化"""
        rms = librosa.feature.rms(y=y)[0]
        variation = np.std(rms) / (np.mean(rms) + 1e-6)
        return min(variation, 1.0)
    
    def _check_trending_audio_match(self, y, sr):
        """检查是否匹配流行音频（简化版本）"""
        # 实际应用中，这里应该与趋势音频数据库进行匹配
        # 这里返回模拟值
        return 0.7
    
    def _analyze_vocal_clarity(self, y, sr):
        """分析人声清晰度"""
        # 使用频谱质心作为简化指标
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        # 人声通常在1-4kHz范围
        vocal_range_ratio = np.sum((spectral_centroids > 1000) & (spectral_centroids < 4000)) / len(spectral_centroids)
        return vocal_range_ratio


class TextOptimizer:
    """文本内容优化器"""
    
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.trending_keywords = self._load_trending_keywords()
        
    def optimize_caption(self, caption: str, platform: SocialPlatform) -> Dict:
        """优化社交媒体标题文案"""
        optimized = {
            'original': caption,
            'optimized': caption,
            'improvements': []
        }
        
        # 1. 长度优化
        length_result = self._optimize_length(caption, platform)
        if length_result['changed']:
            optimized['optimized'] = length_result['text']
            optimized['improvements'].append(length_result['improvement'])
        
        # 2. 表情符号优化
        emoji_result = self._optimize_emojis(optimized['optimized'], platform)
        if emoji_result['changed']:
            optimized['optimized'] = emoji_result['text']
            optimized['improvements'].append(emoji_result['improvement'])
        
        # 3. CTA优化
        cta_result = self._optimize_cta(optimized['optimized'], platform)
        if cta_result['changed']:
            optimized['optimized'] = cta_result['text']
            optimized['improvements'].append(cta_result['improvement'])
        
        # 4. 趋势关键词融入
        keyword_result = self._integrate_trending_keywords(optimized['optimized'])
        if keyword_result['changed']:
            optimized['optimized'] = keyword_result['text']
            optimized['improvements'].append(keyword_result['improvement'])
        
        # 5. 情感分析
        optimized['sentiment'] = self._analyze_sentiment(optimized['optimized'])
        
        return optimized
    
    def _optimize_length(self, text: str, platform: SocialPlatform) -> Dict:
        """优化文本长度"""
        optimal_lengths = {
            SocialPlatform.TIKTOK: (80, 150),
            SocialPlatform.INSTAGRAM: (125, 150),
            SocialPlatform.YOUTUBE: (70, 100),
            SocialPlatform.TWITTER: (100, 280)
        }
        
        min_len, max_len = optimal_lengths.get(platform, (80, 150))
        current_len = len(text)
        
        if current_len < min_len:
            # 扩展文本
            return {
                'changed': True,
                'text': text + " 🎯 Don't miss out!",
                'improvement': f"Extended caption from {current_len} to optimal length"
            }
        elif current_len > max_len:
            # 缩短文本
            sentences = text.split('. ')
            shortened = '. '.join(sentences[:2]) + '...'
            return {
                'changed': True,
                'text': shortened,
                'improvement': f"Shortened caption from {current_len} to {len(shortened)} characters"
            }
        
        return {'changed': False, 'text': text}
    
    def _optimize_emojis(self, text: str, platform: SocialPlatform) -> Dict:
        """优化表情符号使用"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", 
            flags=re.UNICODE
        )
        
        current_emojis = len(emoji_pattern.findall(text))
        
        # 平台最佳实践
        optimal_emojis = {
            SocialPlatform.TIKTOK: (2, 4),
            SocialPlatform.INSTAGRAM: (3, 5),
            SocialPlatform.YOUTUBE: (1, 3)
        }
        
        min_emojis, max_emojis = optimal_emojis.get(platform, (2, 4))
        
        if current_emojis < min_emojis:
            # 添加相关表情
            popular_emojis = ['🎯', '✨', '🔥', '💡', '🚀']
            text_with_emojis = text
            for i in range(min_emojis - current_emojis):
                text_with_emojis += f" {popular_emojis[i % len(popular_emojis)]}"
            
            return {
                'changed': True,
                'text': text_with_emojis,
                'improvement': f"Added {min_emojis - current_emojis} emojis for better engagement"
            }
        
        return {'changed': False, 'text': text}
    
    def _optimize_cta(self, text: str, platform: SocialPlatform) -> Dict:
        """优化行动号召（CTA）"""
        cta_patterns = [
            r'follow\s*(for|us)?',
            r'like\s*(and|&)?\s*subscribe',
            r'comment\s*below',
            r'share\s*(this)?'
        ]
        
        has_cta = any(re.search(pattern, text.lower()) for pattern in cta_patterns)
        
        if not has_cta:
            platform_ctas = {
                SocialPlatform.TIKTOK: "\n\n👉 Follow for more!",
                SocialPlatform.INSTAGRAM: "\n\n💬 Drop a comment!",
                SocialPlatform.YOUTUBE: "\n\n👍 Like & Subscribe!"
            }
            
            cta = platform_ctas.get(platform, "\n\n💡 Follow for more tips!")
            
            return {
                'changed': True,
                'text': text + cta,
                'improvement': "Added engaging call-to-action"
            }
        
        return {'changed': False, 'text': text}
    
    def _integrate_trending_keywords(self, text: str) -> Dict:
        """融入趋势关键词"""
        # 简化实现 - 实际应该连接趋势API
        trending = ['viral', '2024', 'musthave', 'gamechanger']
        
        text_lower = text.lower()
        integrated_any = False
        
        for keyword in trending:
            if keyword not in text_lower:
                # 智能融入关键词
                text = text.replace('product', f'{keyword} product', 1)
                integrated_any = True
                break
        
        if integrated_any:
            return {
                'changed': True,
                'text': text,
                'improvement': "Integrated trending keywords"
            }
        
        return {'changed': False, 'text': text}
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """分析文本情感"""
        try:
            result = self.sentiment_analyzer(text)[0]
            return {
                'label': result['label'],
                'score': result['score'],
                'positive': result['label'] == 'POSITIVE'
            }
        except:
            return {'label': 'NEUTRAL', 'score': 0.5, 'positive': True}
    
    def _load_trending_keywords(self) -> List[str]:
        """加载趋势关键词（实际应连接趋势API）"""
        return [
            'viral', 'trending', '2024', 'musthave', 'fyp',
            'foryou', 'explore', 'reels', 'shorts', 'mustwatch'
        ]


class HashtagOptimizer:
    """标签优化器"""
    
    def __init__(self):
        self.platform_limits = {
            SocialPlatform.TIKTOK: 100,  # 字符数限制
            SocialPlatform.INSTAGRAM: 30,  # 标签数量限制
            SocialPlatform.YOUTUBE: 15,   # 建议数量
            SocialPlatform.TWITTER: 2     # 建议数量
        }
        
    def optimize_hashtags(self, content: str, platform: SocialPlatform, 
                         category: str = None) -> Dict:
        """优化标签策略"""
        
        # 提取现有标签
        existing_tags = self._extract_hashtags(content)
        
        # 生成优化建议
        recommendations = {
            'keep': [],      # 保留的标签
            'remove': [],    # 建议移除的标签
            'add': [],       # 建议添加的标签
            'strategy': {}   # 标签策略
        }
        
        # 1. 分析现有标签
        for tag in existing_tags:
            tag_quality = self._analyze_hashtag_quality(tag, platform)
            if tag_quality['score'] >= 0.7:
                recommendations['keep'].append({
                    'tag': tag,
                    'reason': tag_quality['reason'],
                    'score': tag_quality['score']
                })
            else:
                recommendations['remove'].append({
                    'tag': tag,
                    'reason': tag_quality['reason'],
                    'score': tag_quality['score']
                })
        
        # 2. 推荐新标签
        suggested_tags = self._suggest_hashtags(content, platform, category)
        recommendations['add'] = suggested_tags
        
        # 3. 制定标签策略
        recommendations['strategy'] = self._create_hashtag_strategy(
            platform, len(recommendations['keep']), len(recommendations['add'])
        )
        
        # 4. 生成最终标签集
        final_tags = self._compile_final_hashtags(recommendations, platform)
        
        return {
            'original_tags': existing_tags,
            'optimized_tags': final_tags,
            'recommendations': recommendations,
            'estimated_reach': self._estimate_reach(final_tags)
        }
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """提取文本中的标签"""
        return re.findall(r'#\w+', text)
    
    def _analyze_hashtag_quality(self, tag: str, platform: SocialPlatform) -> Dict:
        """分析标签质量"""
        score = 1.0
        reasons = []
        
        # 长度检查
        if len(tag) > 20:
            score *= 0.7
            reasons.append("Too long")
        elif len(tag) < 3:
            score *= 0.5
            reasons.append("Too short")
        
        # 特殊字符检查
        if re.search(r'[^\w#]', tag):
            score *= 0.3
            reasons.append("Contains special characters")
        
        # 平台特定规则
        if platform == SocialPlatform.TIKTOK:
            if tag.lower() in ['#fyp', '#foryou', '#foryoupage']:
                score *= 1.2
                reasons.append("High visibility tag")
        
        # 垃圾标签检查
        spam_patterns = ['#follow4follow', '#f4f', '#like4like']
        if any(pattern in tag.lower() for pattern in spam_patterns):
            score *= 0.1
            reasons.append("Spam tag")
        
        return {
            'score': min(score, 1.0),
            'reason': ', '.join(reasons) if reasons else 'Good quality'
        }
    
    def _suggest_hashtags(self, content: str, platform: SocialPlatform, 
                         category: str = None) -> List[Dict]:
        """建议相关标签"""
        suggestions = []
        
        # 基础标签池（实际应该从数据库获取）
        tag_pools = {
            'general': ['#eufy', '#smarthome', '#security', '#tech', '#innovation'],
            'product': ['#homesecurity', '#smartcamera', '#wirelesscamera', '#securitysystem'],
            'trending': ['#2024tech', '#musthave', '#hometech', '#safetyfirst'],
            'platform_specific': {
                SocialPlatform.TIKTOK: ['#fyp', '#foryoupage', '#tiktokmademebuyit'],
                SocialPlatform.INSTAGRAM: ['#reels', '#explore', '#instahome'],
                SocialPlatform.YOUTUBE: ['#shorts', '#youtubeshorts', '#tech']
            }
        }
        
        # 1. 添加品牌标签
        suggestions.extend([
            {'tag': '#eufy', 'type': 'brand', 'priority': 1.0},
            {'tag': '#eufysecurity', 'type': 'brand', 'priority': 0.9}
        ])
        
        # 2. 添加类别标签
        if category:
            category_tags = tag_pools.get('product', [])
            for tag in category_tags[:3]:
                suggestions.append({
                    'tag': tag,
                    'type': 'category',
                    'priority': 0.8
                })
        
        # 3. 添加平台特定标签
        platform_tags = tag_pools.get('platform_specific', {}).get(platform, [])
        for tag in platform_tags[:2]:
            suggestions.append({
                'tag': tag,
                'type': 'platform',
                'priority': 0.9
            })
        
        # 4. 添加趋势标签
        trending_tags = tag_pools.get('trending', [])
        for tag in trending_tags[:2]:
            suggestions.append({
                'tag': tag,
                'type': 'trending',
                'priority': 0.7
            })
        
        return sorted(suggestions, key=lambda x: x['priority'], reverse=True)
    
    def _create_hashtag_strategy(self, platform: SocialPlatform, 
                                existing_count: int, suggested_count: int) -> Dict:
        """创建标签策略"""
        strategy = {
            'total_recommended': 0,
            'distribution': {},
            'placement': '',
            'tips': []
        }
        
        if platform == SocialPlatform.TIKTOK:
            strategy['total_recommended'] = 3-5
            strategy['distribution'] = {
                'brand': 1,
                'niche': 2,
                'trending': 1,
                'broad': 1
            }
            strategy['placement'] = 'In caption or first comment'
            strategy['tips'] = [
                'Mix niche and broad hashtags',
                'Use trending sounds with relevant hashtags',
                'Avoid banned or shadowbanned tags'
            ]
        
        elif platform == SocialPlatform.INSTAGRAM:
            strategy['total_recommended'] = 10-15
            strategy['distribution'] = {
                'brand': 2,
                'niche': 5,
                'medium': 5,
                'broad': 3
            }
            strategy['placement'] = 'First comment for cleaner caption'
            strategy['tips'] = [
                'Use mix of popularity levels',
                'Hide hashtags in first comment',
                'Create branded hashtag campaigns'
            ]
        
        return strategy
    
    def _compile_final_hashtags(self, recommendations: Dict, 
                               platform: SocialPlatform) -> List[str]:
        """编译最终标签集"""
        final_tags = []
        
        # 添加保留的标签
        final_tags.extend([item['tag'] for item in recommendations['keep']])
        
        # 添加推荐的标签
        limit = self.platform_limits.get(platform, 10)
        remaining_slots = limit - len(final_tags)
        
        for item in recommendations['add'][:remaining_slots]:
            if isinstance(item, dict):
                final_tags.append(item['tag'])
            else:
                final_tags.append(item)
        
        return final_tags
    
    def _estimate_reach(self, hashtags: List[str]) -> int:
        """估算标签覆盖范围"""
        # 简化实现 - 实际应查询标签使用数据
        base_reach = 10000
        
        for tag in hashtags:
            if tag.lower() in ['#fyp', '#foryou', '#trending']:
                base_reach *= 5
            elif tag.lower() in ['#eufy', '#smarthome']:
                base_reach *= 2
            else:
                base_reach *= 1.2
        
        return int(min(base_reach, 10000000))  # 上限1000万


class TimingOptimizer:
    """发布时机优化器"""
    
    def __init__(self):
        self.platform_peaks = {
            SocialPlatform.TIKTOK: {
                'weekday': [(6, 10), (19, 23)],
                'weekend': [(9, 11), (19, 23)]
            },
            SocialPlatform.INSTAGRAM: {
                'weekday': [(7, 9), (12, 13), (17, 19)],
                'weekend': [(11, 13), (19, 21)]
            },
            SocialPlatform.YOUTUBE: {
                'weekday': [(12, 15), (19, 22)],
                'weekend': [(9, 11), (14, 16), (19, 22)]
            }
        }
    
    def get_optimal_posting_times(self, platform: SocialPlatform, 
                                 target_timezone: str = 'UTC') -> Dict:
        """获取最佳发布时间"""
        current_time = datetime.now()
        day_type = 'weekend' if current_time.weekday() >= 5 else 'weekday'
        
        recommendations = {
            'immediate': self._should_post_now(platform, current_time),
            'next_optimal_slots': [],
            'weekly_schedule': {},
            'timezone_considerations': []
        }
        
        # 获取平台高峰时段
        peak_times = self.platform_peaks.get(platform, {}).get(day_type, [])
        
        # 计算下一个最佳时段
        for start_hour, end_hour in peak_times:
            for hour in range(start_hour, end_hour):
                next_slot = current_time.replace(hour=hour, minute=0, second=0)
                if next_slot > current_time:
                    recommendations['next_optimal_slots'].append({
                        'time': next_slot.isoformat(),
                        'quality': 'peak',
                        'expected_reach_multiplier': 2.5
                    })
        
        # 生成一周发布计划
        recommendations['weekly_schedule'] = self._generate_weekly_schedule(platform)
        
        # 时区考虑
        recommendations['timezone_considerations'] = [
            {'timezone': 'EST', 'offset': -5, 'audience_percentage': 0.3},
            {'timezone': 'PST', 'offset': -8, 'audience_percentage': 0.25},
            {'timezone': 'CST', 'offset': -6, 'audience_percentage': 0.2}
        ]
        
        return recommendations
    
    def _should_post_now(self, platform: SocialPlatform, current_time: datetime) -> Dict:
        """判断是否应该立即发布"""
        hour = current_time.hour
        day_type = 'weekend' if current_time.weekday() >= 5 else 'weekday'
        peak_times = self.platform_peaks.get(platform, {}).get(day_type, [])
        
        is_peak = any(start <= hour < end for start, end in peak_times)
        
        return {
            'recommended': is_peak,
            'reason': 'Peak engagement hours' if is_peak else 'Off-peak hours',
            'engagement_modifier': 1.5 if is_peak else 0.8
        }
    
    def _generate_weekly_schedule(self, platform: SocialPlatform) -> Dict:
        """生成一周发布计划"""
        schedule = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i, day in enumerate(days):
            day_type = 'weekend' if i >= 5 else 'weekday'
            peak_times = self.platform_peaks.get(platform, {}).get(day_type, [])
            
            schedule[day] = {
                'optimal_times': [f"{start}:00-{end}:00" for start, end in peak_times],
                'posts_per_day': 2 if platform == SocialPlatform.TIKTOK else 1,
                'content_type_suggestion': self._get_content_suggestion(day, platform)
            }
        
        return schedule
    
    def _get_content_suggestion(self, day: str, platform: SocialPlatform) -> str:
        """获取内容类型建议"""
        suggestions = {
            'Monday': 'Motivational/Educational content',
            'Tuesday': 'Tips and tutorials',
            'Wednesday': 'Behind-the-scenes',
            'Thursday': 'Throwback/User testimonials',
            'Friday': 'Fun/Entertainment content',
            'Saturday': 'Lifestyle/Aspirational content',
            'Sunday': 'Planning/Preparation content'
        }
        
        return suggestions.get(day, 'General content')


class SocialContentAIOptimizer:
    """社交内容AI优化器主类"""
    
    def __init__(self):
        self.video_analyzer = VideoAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.text_optimizer = TextOptimizer()
        self.hashtag_optimizer = HashtagOptimizer()
        self.timing_optimizer = TimingOptimizer()
        
        # 平台特定分析器
        self.platform_analyzers = {
            SocialPlatform.TIKTOK: TikTokAIAnalyzer(),
            SocialPlatform.INSTAGRAM: InstagramAIAnalyzer(),
            SocialPlatform.YOUTUBE: YouTubeAIAnalyzer()
        }
    
    def optimize_for_ai_recommendation(self, content: Dict, 
                                     platform: SocialPlatform) -> SocialOptimizationResult:
        """优化内容以获得AI推荐"""
        
        # 检测内容类型
        content_type = self._detect_content_type(content)
        
        # 获取平台分析器
        analyzer = self.platform_analyzers.get(platform)
        if not analyzer:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # 初始化优化结果
        optimization_result = SocialOptimizationResult(
            platform=platform,
            content_type=content_type,
            original_content=content,
            optimized_content={},
            ai_recommendation_score=0.0,
            first_3_seconds_score=0.0,
            completion_rate_prediction=0.0,
            engagement_prediction=0.0,
            viral_potential_score=0.0,
            optimization_suggestions=[],
            metadata_enhancements={},
            hashtag_recommendations=[],
            timing_recommendations={}
        )
        
        # 1. 视频内容优化（如果适用）
        if content_type in [ContentType.VIDEO_SHORT, ContentType.VIDEO_LONG, ContentType.REEL]:
            video_optimization = self._optimize_video_content(content, platform, analyzer)
            optimization_result.first_3_seconds_score = video_optimization['first_3_seconds_score']
            optimization_result.completion_rate_prediction = video_optimization['completion_rate']
            optimization_result.optimization_suggestions.extend(video_optimization['suggestions'])
        
        # 2. 文本内容优化
        if content.get('caption'):
            text_optimization = self.text_optimizer.optimize_caption(
                content['caption'], 
                platform
            )
            optimization_result.optimized_content['caption'] = text_optimization['optimized']
            optimization_result.optimization_suggestions.extend([
                {'type': 'caption', 'improvement': imp} 
                for imp in text_optimization['improvements']
            ])
        
        # 3. 标签优化
        hashtag_optimization = self.hashtag_optimizer.optimize_hashtags(
            content.get('caption', '') + ' ' + ' '.join(content.get('hashtags', [])),
            platform,
            content.get('category')
        )
        optimization_result.hashtag_recommendations = hashtag_optimization['optimized_tags']
        optimization_result.metadata_enhancements['hashtag_strategy'] = hashtag_optimization['recommendations']['strategy']
        
        # 4. 发布时机优化
        timing_recommendations = self.timing_optimizer.get_optimal_posting_times(platform)
        optimization_result.timing_recommendations = timing_recommendations
        
        # 5. 计算综合AI推荐分数
        optimization_result.ai_recommendation_score = self._calculate_ai_recommendation_score(
            optimization_result, analyzer
        )
        
        # 6. 预测互动率
        optimization_result.engagement_prediction = self._predict_engagement_rate(
            optimization_result, platform
        )
        
        # 7. 计算病毒传播潜力
        optimization_result.viral_potential_score = self._calculate_viral_potential(
            optimization_result
        )
        
        return optimization_result
    
    def _detect_content_type(self, content: Dict) -> ContentType:
        """检测内容类型"""
        if content.get('video_path'):
            # 检查视频时长
            cap = cv2.VideoCapture(content['video_path'])
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
            
            if duration < 60:
                return ContentType.VIDEO_SHORT
            else:
                return ContentType.VIDEO_LONG
        
        elif content.get('images'):
            if len(content['images']) > 1:
                return ContentType.CAROUSEL
            else:
                return ContentType.IMAGE_POST
        
        elif content.get('is_story'):
            return ContentType.STORY
        
        return ContentType.IMAGE_POST
    
    def _optimize_video_content(self, content: Dict, platform: SocialPlatform, 
                               analyzer) -> Dict:
        """优化视频内容"""
        video_path = content.get('video_path')
        if not video_path:
            return {
                'first_3_seconds_score': 0,
                'completion_rate': 0,
                'suggestions': []
            }
        
        # 分析前3秒
        first_3_metrics = self.video_analyzer.analyze_first_3_seconds(video_path)
        
        # 分析音频（如果有）
        audio_metrics = {}
        if content.get('audio_path'):
            audio_metrics = self.audio_analyzer.analyze_audio_hooks(content['audio_path'])
        
        # 平台特定优化
        platform_optimization = analyzer.optimize_opening(
            video_path,
            target_retention_rate=0.85
        )
        
        # 生成优化建议
        suggestions = []
        
        if first_3_metrics['hook_strength'] < 0.7:
            suggestions.append({
                'priority': 'high',
                'category': 'hook',
                'suggestion': 'Strengthen opening hook - add motion, face, or scene change',
                'impact': 'Can improve retention by 20-30%'
            })
        
        if first_3_metrics['face_presence'] < 0.5:
            suggestions.append({
                'priority': 'medium',
                'category': 'human_element',
                'suggestion': 'Add human face in first 3 seconds for better connection',
                'impact': 'Increases engagement by 15-20%'
            })
        
        if audio_metrics.get('trending_audio_match', 0) < 0.5:
            suggestions.append({
                'priority': 'medium',
                'category': 'audio',
                'suggestion': 'Use trending audio for better discoverability',
                'impact': 'Can increase reach by 50-100%'
            })
        
        # 预测完播率
        completion_rate = self._predict_completion_rate(
            first_3_metrics, 
            audio_metrics,
            platform
        )
        
        return {
            'first_3_seconds_score': first_3_metrics['hook_strength'],
            'completion_rate': completion_rate,
            'suggestions': suggestions,
            'detailed_metrics': {
                'video': first_3_metrics,
                'audio': audio_metrics
            }
        }
    
    def _predict_completion_rate(self, video_metrics: Dict, audio_metrics: Dict, 
                                platform: SocialPlatform) -> float:
        """预测视频完播率"""
        # 基础完播率
        base_rate = 0.3
        
        # 视频因素影响
        video_multiplier = 1.0
        video_multiplier *= (1 + video_metrics.get('hook_strength', 0) * 0.5)
        video_multiplier *= (1 + video_metrics.get('face_presence', 0) * 0.2)
        video_multiplier *= (1 + min(video_metrics.get('scene_changes', 0) / 3, 1) * 0.1)
        
        # 音频因素影响
        audio_multiplier = 1.0
        if audio_metrics:
            audio_multiplier *= (1 + audio_metrics.get('beat_strength', 0) * 0.2)
            audio_multiplier *= (1 + audio_metrics.get('trending_audio_match', 0) * 0.3)
        
        # 平台特定调整
        platform_multipliers = {
            SocialPlatform.TIKTOK: 1.2,    # TikTok用户完播率较高
            SocialPlatform.INSTAGRAM: 0.9,   # Reels完播率中等
            SocialPlatform.YOUTUBE: 0.7      # Shorts完播率较低
        }
        
        platform_multiplier = platform_multipliers.get(platform, 1.0)
        
        # 计算最终完播率
        predicted_rate = base_rate * video_multiplier * audio_multiplier * platform_multiplier
        
        return min(predicted_rate, 0.95)  # 上限95%
    
    def _calculate_ai_recommendation_score(self, result: SocialOptimizationResult, 
                                         analyzer) -> float:
        """计算AI推荐概率得分"""
        score_components = {
            'content_quality': 0.0,
            'engagement_signals': 0.0,
            'platform_alignment': 0.0,
            'timing_optimization': 0.0,
            'metadata_quality': 0.0
        }
        
        # 1. 内容质量分数
        if result.content_type in [ContentType.VIDEO_SHORT, ContentType.REEL]:
            score_components['content_quality'] = (
                result.first_3_seconds_score * 0.6 +
                result.completion_rate_prediction * 0.4
            )
        else:
            score_components['content_quality'] = 0.7  # 默认值
        
        # 2. 互动信号分数
        caption_sentiment = result.optimized_content.get('caption_sentiment', {})
        if caption_sentiment.get('positive', False):
            score_components['engagement_signals'] += 0.3
        
        # 标签质量
        if len(result.hashtag_recommendations) > 0:
            score_components['engagement_signals'] += 0.4
        
        # 3. 平台契合度
        score_components['platform_alignment'] = analyzer.calculate_platform_fit_score(result)
        
        # 4. 时机优化分数
        if result.timing_recommendations.get('immediate', {}).get('recommended', False):
            score_components['timing_optimization'] = 0.8
        else:
            score_components['timing_optimization'] = 0.5
        
        # 5. 元数据质量
        if result.metadata_enhancements:
            score_components['metadata_quality'] = 0.7
        
        # 计算加权总分
        weights = {
            'content_quality': 0.4,
            'engagement_signals': 0.2,
            'platform_alignment': 0.2,
            'timing_optimization': 0.1,
            'metadata_quality': 0.1
        }
        
        total_score = sum(
            score_components[component] * weights[component] 
            for component in score_components
        )
        
        return round(total_score, 2)
    
    def _predict_engagement_rate(self, result: SocialOptimizationResult, 
                                platform: SocialPlatform) -> float:
        """预测内容互动率"""
        # 基础互动率（根据平台平均值）
        base_engagement = {
            SocialPlatform.TIKTOK: 0.05,     # 5%
            SocialPlatform.INSTAGRAM: 0.03,    # 3%
            SocialPlatform.YOUTUBE: 0.04      # 4%
        }
        
        base_rate = base_engagement.get(platform, 0.03)
        
        # 根据优化因素调整
        multiplier = 1.0
        
        # AI推荐分数影响
        multiplier *= (1 + result.ai_recommendation_score * 0.5)
        
        # 内容质量影响
        if result.first_3_seconds_score > 0.8:
            multiplier *= 1.3
        
        # 标签优化影响
        if len(result.hashtag_recommendations) >= 5:
            multiplier *= 1.2
        
        # 发布时机影响
        if result.timing_recommendations.get('immediate', {}).get('recommended', False):
            multiplier *= 1.1
        
        predicted_engagement = base_rate * multiplier
        
        return round(min(predicted_engagement, 0.25), 3)  # 上限25%
    
    def _calculate_viral_potential(self, result: SocialOptimizationResult) -> float:
        """计算病毒传播潜力分数"""
        viral_factors = {
            'ai_recommendation': result.ai_recommendation_score,
            'completion_rate': result.completion_rate_prediction,
            'engagement_prediction': result.engagement_prediction,
            'content_uniqueness': 0.7,  # 默认值，实际应通过内容分析得出
            'timing_quality': 0.8 if result.timing_recommendations.get('immediate', {}).get('recommended') else 0.5,
            'hashtag_reach': min(len(result.hashtag_recommendations) / 10, 1.0)
        }
        
        # 权重分配
        weights = {
            'ai_recommendation': 0.3,
            'completion_rate': 0.25,
            'engagement_prediction': 0.2,
            'content_uniqueness': 0.15,
            'timing_quality': 0.05,
            'hashtag_reach': 0.05
        }
        
        viral_score = sum(
            viral_factors[factor] * weights[factor] 
            for factor in viral_factors
        )
        
        # 病毒传播需要多个因素都表现良好
        if viral_score > 0.7 and result.ai_recommendation_score > 0.8:
            viral_score *= 1.2  # 额外加成
        
        return round(min(viral_score, 1.0), 2)


class TikTokAIAnalyzer:
    """TikTok平台AI分析器"""
    
    def optimize_opening(self, video_path: str, target_retention_rate: float) -> Dict:
        """优化视频开场"""
        return {
            'optimized': True,
            'retention_improvement': 0.15,
            'suggestions': [
                'Add text overlay in first second',
                'Start with action or movement',
                'Use pattern interrupt technique'
            ]
        }
    
    def generate_ai_friendly_captions(self, content: Dict, 
                                    include_keywords: bool = True,
                                    semantic_enhancement: bool = True) -> str:
        """生成AI友好的字幕"""
        base_caption = content.get('caption', '')
        
        if include_keywords:
            # 添加关键词
            base_caption += " #eufy #smarthome"
        
        if semantic_enhancement:
            # 语义增强
            base_caption = base_caption.replace('camera', 'smart security camera')
            base_caption = base_caption.replace('buy', 'get yours')
        
        return base_caption
    
    def suggest_ai_friendly_hashtags(self, content: Dict) -> List[str]:
        """建议AI友好的标签"""
        return ['#fyp', '#foryoupage', '#eufy', '#smarthome', '#securitycamera']
    
    def craft_ai_optimized_description(self, content: Dict) -> str:
        """创建AI优化的描述"""
        return f"Discover how {content.get('product_name', 'Eufy')} can transform your home security! 🏠✨"
    
    def determine_category_signals(self, content: Dict) -> List[str]:
        """确定类别信号"""
        return ['Technology', 'Home & Garden', 'Security']
    
    def predict_recommendation_probability(self, optimization_result: Dict) -> float:
        """预测推荐概率"""
        base_prob = 0.5
        
        if optimization_result.get('first_3_seconds', {}).get('hook_strength', 0) > 0.7:
            base_prob += 0.2
        
        if optimization_result.get('metadata', {}).get('hashtags'):
            base_prob += 0.1
        
        return min(base_prob, 0.95)
    
    def calculate_platform_fit_score(self, result) -> float:
        """计算平台契合度分数"""
        return 0.85  # 简化实现


class InstagramAIAnalyzer:
    """Instagram平台AI分析器"""
    
    def optimize_opening(self, video_path: str, target_retention_rate: float) -> Dict:
        """优化视频开场"""
        return {
            'optimized': True,
            'retention_improvement': 0.12,
            'suggestions': [
                'Use aesthetic visuals',
                'Add smooth transitions',
                'Include lifestyle elements'
            ]
        }
    
    def generate_ai_friendly_captions(self, content: Dict, 
                                    include_keywords: bool = True,
                                    semantic_enhancement: bool = True) -> str:
        """生成AI友好的字幕"""
        return f"Transform your space with smart security 🏡✨ {content.get('caption', '')}"
    
    def suggest_ai_friendly_hashtags(self, content: Dict) -> List[str]:
        """建议AI友好的标签"""
        return ['#reels', '#explore', '#smarthome', '#homesecurity', '#modernliving']
    
    def craft_ai_optimized_description(self, content: Dict) -> str:
        """创建AI优化的描述"""
        return f"Smart home security that fits your lifestyle ✨ Shop link in bio!"
    
    def determine_category_signals(self, content: Dict) -> List[str]:
        """确定类别信号"""
        return ['Home Decor', 'Technology', 'Lifestyle']
    
    def predict_recommendation_probability(self, optimization_result: Dict) -> float:
        """预测推荐概率"""
        return 0.7  # 简化实现
    
    def calculate_platform_fit_score(self, result) -> float:
        """计算平台契合度分数"""
        return 0.8  # 简化实现


class YouTubeAIAnalyzer:
    """YouTube平台AI分析器"""
    
    def optimize_opening(self, video_path: str, target_retention_rate: float) -> Dict:
        """优化视频开场"""
        return {
            'optimized': True,
            'retention_improvement': 0.1,
            'suggestions': [
                'Add compelling hook question',
                'Preview value proposition',
                'Use chapter markers'
            ]
        }
    
    def generate_ai_friendly_captions(self, content: Dict, 
                                    include_keywords: bool = True,
                                    semantic_enhancement: bool = True) -> str:
        """生成AI友好的字幕"""
        return f"{content.get('caption', '')} | Eufy Smart Security"
    
    def suggest_ai_friendly_hashtags(self, content: Dict) -> List[str]:
        """建议AI友好的标签"""
        return ['#shorts', '#smarthome', '#securitycamera', '#hometech', '#eufy']
    
    def craft_ai_optimized_description(self, content: Dict) -> str:
        """创建AI优化的描述"""
        return f"Quick look at {content.get('product_name', 'Eufy Security')} features!"
    
    def determine_category_signals(self, content: Dict) -> List[str]:
        """确定类别信号"""
        return ['Science & Technology', 'Howto & Style']
    
    def predict_recommendation_probability(self, optimization_result: Dict) -> float:
        """预测推荐概率"""
        return 0.65  # 简化实现
    
    def calculate_platform_fit_score(self, result) -> float:
        """计算平台契合度分数"""
        return 0.75  # 简化实现


def main():
    """主函数 - 演示用法"""
    # 创建优化器
    optimizer = SocialContentAIOptimizer()
    
    # 示例内容
    sample_content = {
        'video_path': '/path/to/video.mp4',
        'audio_path': '/path/to/audio.mp3',
        'caption': 'Check out our new security camera!',
        'hashtags': ['#security', '#tech'],
        'category': 'home_security',
        'product_name': 'Eufy Security Camera S330'
    }
    
    # 为TikTok优化
    result = optimizer.optimize_for_ai_recommendation(
        sample_content, 
        SocialPlatform.TIKTOK
    )
    
    # 输出结果
    print("=== 社交内容AI优化结果 ===")
    print(f"平台: {result.platform.value}")
    print(f"内容类型: {result.content_type.value}")
    print(f"\nAI推荐得分: {result.ai_recommendation_score}/1.0")
    print(f"首3秒得分: {result.first_3_seconds_score}/1.0")
    print(f"预测完播率: {result.completion_rate_prediction*100:.1f}%")
    print(f"预测互动率: {result.engagement_prediction*100:.1f}%")
    print(f"病毒传播潜力: {result.viral_potential_score}/1.0")
    
    print("\n=== 优化建议 ===")
    for i, suggestion in enumerate(result.optimization_suggestions[:5], 1):
        if isinstance(suggestion, dict):
            print(f"{i}. [{suggestion.get('priority', 'medium')}] {suggestion.get('suggestion', '')}")
            print(f"   影响: {suggestion.get('impact', '')}")
        else:
            print(f"{i}. {suggestion}")
    
    print("\n=== 推荐标签 ===")
    print(f"标签: {' '.join(result.hashtag_recommendations[:10])}")
    
    print("\n=== 发布时机 ===")
    if result.timing_recommendations.get('immediate', {}).get('recommended'):
        print("建议立即发布！(当前为高峰时段)")
    else:
        next_slots = result.timing_recommendations.get('next_optimal_slots', [])
        if next_slots:
            print(f"下一个最佳发布时间: {next_slots[0]['time']}")


if __name__ == "__main__":
    # 下载必要的数据
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    
    main()