#!/usr/bin/env python3
"""
私域AI客服优化系统
为WhatsApp Business、AI聊天机器人、智能邮件营销等私域渠道优化客服体验
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum
import nltk
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import random


class PrivateDomainChannel(Enum):
    """私域渠道枚举"""
    WHATSAPP_BUSINESS = "whatsapp_business"
    WECHAT = "wechat"
    TELEGRAM = "telegram"
    EMAIL_MARKETING = "email_marketing"
    CHATBOT = "chatbot"
    LIVE_CHAT = "live_chat"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"


class MessageType(Enum):
    """消息类型枚举"""
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    TECHNICAL_SUPPORT = "technical_support"
    ORDER_STATUS = "order_status"
    COMPLAINT = "complaint"
    UPSELL = "upsell"
    RETENTION = "retention"
    ONBOARDING = "onboarding"
    FOLLOW_UP = "follow_up"


class CustomerSegment(Enum):
    """客户分群枚举"""
    NEW_CUSTOMER = "new_customer"
    REPEAT_CUSTOMER = "repeat_customer"
    VIP_CUSTOMER = "vip_customer"
    AT_RISK_CUSTOMER = "at_risk_customer"
    POTENTIAL_CUSTOMER = "potential_customer"


@dataclass
class AICustomerServiceResult:
    """AI客服优化结果"""
    channel: PrivateDomainChannel
    message_type: MessageType
    customer_segment: CustomerSegment
    original_message: str
    optimized_messages: List[Dict]
    predicted_open_rate: float
    predicted_response_rate: float
    predicted_conversion_rate: float
    sentiment_score: float
    personalization_level: float
    automation_confidence: float
    escalation_triggers: List[str]
    follow_up_sequence: List[Dict]
    performance_metrics: Dict


class ConversationFlowOptimizer:
    """对话流程优化器"""
    
    def __init__(self):
        self.conversation_patterns = self._load_conversation_patterns()
        self.escalation_rules = self._load_escalation_rules()
        
    def design_flows(self, entry_points: List[str], optimization_goals: List[str],
                    ai_handoff_points: List[str]) -> Dict[str, List]:
        """设计优化的对话流程"""
        flows = {}
        
        for entry_point in entry_points:
            flow = self._create_flow_for_entry_point(
                entry_point, 
                optimization_goals, 
                ai_handoff_points
            )
            flows[entry_point] = flow
            
        return flows
    
    def _load_conversation_patterns(self) -> Dict:
        """加载对话模式"""
        return {
            'product_inquiry': {
                'greeting': "Hi! Thanks for your interest in {product_name}! 👋",
                'qualification': "To help you find the perfect solution, what's your main security concern?",
                'presentation': "Based on what you've shared, here's how {product_name} can help:",
                'objection_handling': "I understand your concern about {objection}. Here's what makes us different:",
                'close': "Would you like me to send you a special discount code to try it risk-free?"
            },
            'technical_support': {
                'greeting': "Hi! I'm here to help resolve any technical issues quickly! 🔧",
                'diagnosis': "Let me gather some details to provide the best solution:",
                'solution': "Here's the step-by-step solution for your {issue}:",
                'verification': "Did this solve your issue? If not, I'll escalate to our tech team.",
                'follow_up': "I'll check back in 24 hours to make sure everything is working perfectly!"
            },
            'order_status': {
                'greeting': "Hi! Let me check your order status right away! 📦",
                'lookup': "I found your order #{order_number}:",
                'update': "Current status: {status}. Expected delivery: {date}",
                'proactive': "I'll send you tracking updates automatically. Anything else I can help with?",
                'upsell': "While we're chatting, have you seen our latest {related_product}?"
            }
        }
    
    def _load_escalation_rules(self) -> Dict:
        """加载升级规则"""
        return {
            'sentiment_threshold': -0.3,  # 负面情绪阈值
            'complexity_keywords': [
                'warranty claim', 'refund', 'defective', 'broken',
                'not working', 'disappointed', 'angry', 'frustrated'
            ],
            'vip_customers': ['immediate_escalation'],
            'technical_keywords': [
                'firmware update', 'connectivity issue', 'reset',
                'configuration', 'troubleshooting'
            ],
            'escalation_delay': {
                'low_priority': 120,  # 2分钟
                'medium_priority': 60,  # 1分钟
                'high_priority': 30,   # 30秒
                'urgent': 0            # 立即
            }
        }
    
    def _create_flow_for_entry_point(self, entry_point: str, goals: List[str], 
                                    handoff_points: List[str]) -> List[Dict]:
        """为入口点创建流程"""
        flow = []
        
        if entry_point == 'product_inquiry':
            flow = [
                {
                    'step': 1,
                    'type': 'greeting',
                    'message_template': self.conversation_patterns['product_inquiry']['greeting'],
                    'variables': ['product_name'],
                    'next_actions': ['qualification', 'direct_question'],
                    'ai_confidence': 0.9
                },
                {
                    'step': 2,
                    'type': 'qualification',
                    'message_template': self.conversation_patterns['product_inquiry']['qualification'],
                    'variables': [],
                    'next_actions': ['presentation', 'clarification'],
                    'ai_confidence': 0.8
                },
                {
                    'step': 3,
                    'type': 'presentation',
                    'message_template': self.conversation_patterns['product_inquiry']['presentation'],
                    'variables': ['product_name', 'benefits'],
                    'next_actions': ['close', 'objection_handling'],
                    'ai_confidence': 0.7
                },
                {
                    'step': 4,
                    'type': 'close',
                    'message_template': self.conversation_patterns['product_inquiry']['close'],
                    'variables': ['discount_code'],
                    'next_actions': ['follow_up', 'escalation'],
                    'ai_confidence': 0.6
                }
            ]
        elif entry_point == 'technical_support':
            flow = [
                {
                    'step': 1,
                    'type': 'greeting',
                    'message_template': self.conversation_patterns['technical_support']['greeting'],
                    'variables': [],
                    'next_actions': ['diagnosis'],
                    'ai_confidence': 0.9
                },
                {
                    'step': 2,
                    'type': 'diagnosis',
                    'message_template': self.conversation_patterns['technical_support']['diagnosis'],
                    'variables': [],
                    'next_actions': ['solution', 'escalation'],
                    'ai_confidence': 0.7
                },
                {
                    'step': 3,
                    'type': 'solution',
                    'message_template': self.conversation_patterns['technical_support']['solution'],
                    'variables': ['issue', 'solution_steps'],
                    'next_actions': ['verification', 'escalation'],
                    'ai_confidence': 0.6
                }
            ]
        
        # 添加优化目标到流程
        if 'quick_resolution' in goals:
            for step in flow:
                step['timeout'] = 30  # 30秒内响应
        
        if 'high_satisfaction' in goals:
            for step in flow:
                step['satisfaction_check'] = True
        
        return flow


class AnswerCardGenerator:
    """Answer Card生成器"""
    
    def __init__(self):
        self.product_database = self._load_product_database()
        self.template_library = self._load_template_library()
        
    def generate(self, question: str, context: Dict) -> Dict:
        """生成Answer Card"""
        answer_card = {
            "@context": "https://schema.org",
            "@type": "Answer",
            "question": question,
            "text": self._generate_concise_answer(question, context),
            "detailedAnswer": self._generate_detailed_answer(question, context),
            "dateCreated": datetime.now().isoformat(),
            "author": {
                "@type": "Organization",
                "name": "Eufy Customer Service",
                "url": "https://www.eufy.com/support"
            },
            "channel_optimized": True,
            "automation_ready": True
        }
        
        # 添加渠道特定优化
        if context.get('channel'):
            answer_card["channel_specific"] = self._optimize_for_channel(
                answer_card, context['channel']
            )
        
        # 添加个性化元素
        if context.get('customer_segment'):
            answer_card["personalization"] = self._add_personalization(
                answer_card, context['customer_segment']
            )
        
        return answer_card
    
    def _load_product_database(self) -> Dict:
        """加载产品数据库"""
        return {
            'eufycam_3': {
                'name': 'eufyCam 3',
                'battery_life': '365 days',
                'resolution': '4K',
                'storage': 'Local 16GB',
                'subscription': 'No monthly fee',
                'setup_time': '10 minutes',
                'app': 'eufy Security',
                'compatibility': ['iOS', 'Android', 'Alexa', 'Google Assistant']
            },
            'video_doorbell': {
                'name': 'eufy Video Doorbell',
                'battery_life': '180 days',
                'resolution': '2K',
                'features': ['Two-way audio', 'Motion detection', 'Night vision'],
                'subscription': 'No monthly fee'
            }
        }
    
    def _load_template_library(self) -> Dict:
        """加载模板库"""
        return {
            'setup_help': {
                'concise': "Setting up {product_name} takes about {setup_time}. Download the {app} app and follow the guided setup.",
                'detailed': "Here's the complete setup process:\n1. Download {app} app\n2. Create account\n3. Add device\n4. Connect to WiFi\n5. Mount camera\n\nThe app will guide you through each step with clear instructions and videos."
            },
            'battery_life': {
                'concise': "{product_name} battery lasts up to {battery_life} under normal usage.",
                'detailed': "{product_name} features industry-leading {battery_life} battery life. Actual duration depends on usage patterns:\n- Light usage: Up to {battery_life}\n- Normal usage: 6-12 months\n- Heavy usage: 3-6 months\n\nYou'll get low battery alerts through the app with plenty of time to recharge."
            },
            'subscription': {
                'concise': "No subscription required! {product_name} includes {storage} free local storage.",
                'detailed': "Unlike competitors, {product_name} works completely without monthly fees:\n✅ Free local storage ({storage})\n✅ Live viewing\n✅ Motion alerts\n✅ Two-way audio\n✅ App control\n\nOptional cloud storage available if desired, but not required."
            }
        }
    
    def _generate_concise_answer(self, question: str, context: Dict) -> str:
        """生成简洁答案"""
        question_lower = question.lower()
        product = context.get('product', 'eufycam_3')
        product_data = self.product_database.get(product, {})
        
        # 问题分类和答案生成
        if any(word in question_lower for word in ['setup', 'install', 'connect']):
            template = self.template_library['setup_help']['concise']
            return template.format(
                product_name=product_data.get('name', 'the product'),
                setup_time=product_data.get('setup_time', '10 minutes'),
                app=product_data.get('app', 'eufy Security')
            )
        
        elif any(word in question_lower for word in ['battery', 'charge', 'power']):
            template = self.template_library['battery_life']['concise']
            return template.format(
                product_name=product_data.get('name', 'the product'),
                battery_life=product_data.get('battery_life', '365 days')
            )
        
        elif any(word in question_lower for word in ['subscription', 'monthly', 'fee', 'cost']):
            template = self.template_library['subscription']['concise']
            return template.format(
                product_name=product_data.get('name', 'the product'),
                storage=product_data.get('storage', 'local storage')
            )
        
        elif any(word in question_lower for word in ['compatible', 'work with', 'support']):
            compatibility = product_data.get('compatibility', [])
            return f"{product_data.get('name', 'The product')} works with {', '.join(compatibility)}."
        
        else:
            # 通用回答
            return f"Great question about {product_data.get('name', 'our product')}! Let me help you with that."
    
    def _generate_detailed_answer(self, question: str, context: Dict) -> str:
        """生成详细答案"""
        question_lower = question.lower()
        product = context.get('product', 'eufycam_3')
        product_data = self.product_database.get(product, {})
        
        if any(word in question_lower for word in ['setup', 'install', 'connect']):
            template = self.template_library['setup_help']['detailed']
            return template.format(
                app=product_data.get('app', 'eufy Security')
            )
        
        elif any(word in question_lower for word in ['battery', 'charge', 'power']):
            template = self.template_library['battery_life']['detailed']
            return template.format(
                product_name=product_data.get('name', 'the product'),
                battery_life=product_data.get('battery_life', '365 days')
            )
        
        elif any(word in question_lower for word in ['subscription', 'monthly', 'fee', 'cost']):
            template = self.template_library['subscription']['detailed']
            return template.format(
                product_name=product_data.get('name', 'the product'),
                storage=product_data.get('storage', 'local storage')
            )
        
        else:
            # 生成通用详细回答
            concise = self._generate_concise_answer(question, context)
            return f"{concise}\n\nFor more specific help, please let me know your exact situation and I'll provide personalized guidance."
    
    def _optimize_for_channel(self, answer_card: Dict, channel: PrivateDomainChannel) -> Dict:
        """为特定渠道优化"""
        optimizations = {}
        
        if channel == PrivateDomainChannel.WHATSAPP_BUSINESS:
            optimizations = {
                'max_length': 600,  # WhatsApp建议长度
                'emoji_usage': 'encouraged',
                'formatting': 'simple_markdown',
                'media_support': ['image', 'video', 'document'],
                'quick_replies': self._generate_quick_replies(answer_card['question'])
            }
        
        elif channel == PrivateDomainChannel.EMAIL_MARKETING:
            optimizations = {
                'subject_line': self._generate_email_subject(answer_card['question']),
                'html_formatting': True,
                'cta_placement': 'bottom',
                'personalization_tokens': ['first_name', 'product_name'],
                'unsubscribe_required': True
            }
        
        elif channel == PrivateDomainChannel.CHATBOT:
            optimizations = {
                'max_length': 300,
                'conversation_flow': True,
                'follow_up_questions': self._generate_follow_up_questions(answer_card['question']),
                'escalation_triggers': ['human_requested', 'negative_sentiment', 'complex_issue']
            }
        
        return optimizations
    
    def _add_personalization(self, answer_card: Dict, segment: CustomerSegment) -> Dict:
        """添加个性化元素"""
        personalization = {}
        
        if segment == CustomerSegment.NEW_CUSTOMER:
            personalization = {
                'tone': 'welcoming_educational',
                'additional_info': 'setup_tips',
                'offer': 'welcome_discount',
                'follow_up': 'onboarding_sequence'
            }
        
        elif segment == CustomerSegment.VIP_CUSTOMER:
            personalization = {
                'tone': 'premium_service',
                'priority': 'high',
                'escalation_path': 'direct_to_specialist',
                'additional_benefits': 'vip_perks'
            }
        
        elif segment == CustomerSegment.AT_RISK_CUSTOMER:
            personalization = {
                'tone': 'retention_focused',
                'urgency': 'high',
                'offer': 'retention_incentive',
                'follow_up': 'satisfaction_survey'
            }
        
        return personalization
    
    def _generate_quick_replies(self, question: str) -> List[str]:
        """生成快速回复选项"""
        question_lower = question.lower()
        
        if 'setup' in question_lower:
            return [
                "📱 Download app",
                "📹 Watch setup video", 
                "🔧 Troubleshoot setup",
                "💬 Talk to human"
            ]
        elif 'battery' in question_lower:
            return [
                "🔋 Check battery status",
                "⚡ Charging tips",
                "🔧 Battery issues",
                "💬 Talk to human"
            ]
        else:
            return [
                "✅ Helpful",
                "❓ Need more info",
                "🔧 Technical help",
                "💬 Talk to human"
            ]
    
    def _generate_email_subject(self, question: str) -> str:
        """生成邮件主题"""
        if 'setup' in question.lower():
            return "Quick Setup Guide for Your Eufy Camera 📹"
        elif 'battery' in question.lower():
            return "Battery Tips to Maximize Your Camera's Life 🔋"
        elif 'subscription' in question.lower():
            return "Why Eufy Costs Less (No Monthly Fees!) 💰"
        else:
            return "Your Eufy Question Answered ✅"
    
    def _generate_follow_up_questions(self, question: str) -> List[str]:
        """生成后续问题"""
        question_lower = question.lower()
        
        if 'setup' in question_lower:
            return [
                "What step are you currently on?",
                "Are you seeing any error messages?",
                "Is your phone connected to WiFi?"
            ]
        elif 'battery' in question_lower:
            return [
                "How often do you get motion alerts?",
                "When did you last charge it?",
                "Are you getting low battery notifications?"
            ]
        else:
            return [
                "What specific issue are you experiencing?",
                "When did this problem start?",
                "Have you tried restarting the device?"
            ]


class MessageOptimizer:
    """消息优化器"""
    
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.optimization_patterns = self._load_optimization_patterns()
        
    def optimize_message_for_engagement(self, message_template: str, 
                                      channel: PrivateDomainChannel,
                                      customer_segment: CustomerSegment,
                                      message_type: MessageType) -> Dict:
        """优化消息以提高互动率"""
        
        # 生成A/B测试变体
        variants = self._generate_variants(
            message_template, 
            channel, 
            customer_segment, 
            message_type
        )
        
        optimized_message = {
            'original': message_template,
            'optimized_versions': []
        }
        
        for variant in variants:
            optimization = {
                'content': variant['content'],
                'optimization_type': variant['type'],
                'predicted_open_rate': self._predict_open_rate(variant, channel),
                'predicted_response_rate': self._predict_response_rate(variant, channel),
                'predicted_conversion_rate': self._predict_conversion_rate(variant, message_type),
                'personalization_score': self._calculate_personalization_score(variant, customer_segment),
                'urgency_score': self._calculate_urgency_score(variant),
                'emotional_appeal': self._analyze_emotional_appeal(variant)
            }
            optimized_message['optimized_versions'].append(optimization)
        
        # 排序变体
        optimized_message['optimized_versions'].sort(
            key=lambda x: (x['predicted_response_rate'] * 0.4 + 
                          x['predicted_conversion_rate'] * 0.6),
            reverse=True
        )
        
        return optimized_message
    
    def _load_optimization_patterns(self) -> Dict:
        """加载优化模式"""
        return {
            'urgency_triggers': [
                'limited time', 'today only', 'expires soon', 'last chance',
                'while supplies last', 'don\'t miss out'
            ],
            'personalization_tokens': [
                '{first_name}', '{product_name}', '{location}', '{last_purchase}',
                '{interest}', '{usage_pattern}'
            ],
            'emotional_triggers': {
                'curiosity': ['discover', 'secret', 'revealed', 'insider'],
                'fear': ['missing out', 'limited', 'exclusive', 'deadline'],
                'desire': ['want', 'need', 'must-have', 'essential'],
                'trust': ['proven', 'trusted', 'verified', 'guaranteed']
            },
            'channel_best_practices': {
                PrivateDomainChannel.WHATSAPP_BUSINESS: {
                    'max_length': 600,
                    'emoji_recommended': True,
                    'personal_tone': True,
                    'quick_replies': True
                },
                PrivateDomainChannel.EMAIL_MARKETING: {
                    'subject_line_critical': True,
                    'preview_text_important': True,
                    'cta_placement': 'multiple',
                    'mobile_optimization': True
                },
                PrivateDomainChannel.SMS: {
                    'max_length': 160,
                    'clear_cta': True,
                    'link_placement': 'end',
                    'opt_out_required': True
                }
            }
        }
    
    def _generate_variants(self, message: str, channel: PrivateDomainChannel,
                          segment: CustomerSegment, msg_type: MessageType) -> List[Dict]:
        """生成消息变体"""
        variants = []
        
        # 1. 好奇心驱动版本
        curiosity_variant = self._optimize_for_curiosity(message)
        variants.append({
            'content': curiosity_variant,
            'type': 'curiosity',
            'primary_emotion': 'curiosity'
        })
        
        # 2. 紧迫性版本
        urgency_variant = self._optimize_for_urgency(message)
        variants.append({
            'content': urgency_variant,
            'type': 'urgency',
            'primary_emotion': 'fear_of_missing_out'
        })
        
        # 3. 个性化版本
        personal_variant = self._optimize_for_personalization(message, segment)
        variants.append({
            'content': personal_variant,
            'type': 'personalization',
            'primary_emotion': 'connection'
        })
        
        # 4. 价值主张版本
        value_variant = self._optimize_for_value_proposition(message, msg_type)
        variants.append({
            'content': value_variant,
            'type': 'value_proposition',
            'primary_emotion': 'desire'
        })
        
        # 5. 渠道优化版本
        channel_variant = self._optimize_for_channel_specific(message, channel)
        variants.append({
            'content': channel_variant,
            'type': 'channel_optimized',
            'primary_emotion': 'platform_native'
        })
        
        return variants
    
    def _optimize_for_curiosity(self, message: str) -> str:
        """优化好奇心"""
        curiosity_hooks = [
            "You won't believe what happened...",
            "This might surprise you...",
            "Here's something most people don't know...",
            "The secret that changed everything...",
            "What we discovered will amaze you..."
        ]
        
        # 选择随机钩子
        hook = random.choice(curiosity_hooks)
        
        # 重写消息开头
        if message.startswith("Hi") or message.startswith("Hello"):
            # 替换普通问候
            optimized = message.replace(message.split('.')[0], hook.rstrip('.'), 1)
        else:
            # 在开头添加钩子
            optimized = f"{hook} {message}"
        
        # 添加神秘元素
        if '?' not in optimized:
            optimized += " Want to know more?"
        
        return optimized
    
    def _optimize_for_urgency(self, message: str) -> str:
        """优化紧迫性"""
        urgency_phrases = [
            "⏰ Limited time:",
            "🔥 Today only:",
            "⚡ Last chance:",
            "⏱️ Expires in 24 hours:",
            "🚨 While supplies last:"
        ]
        
        # 添加紧迫性前缀
        urgency_prefix = random.choice(urgency_phrases)
        optimized = f"{urgency_prefix} {message}"
        
        # 添加行动催促
        if not any(word in message.lower() for word in ['now', 'today', 'immediately']):
            optimized += " Act now!"
        
        return optimized
    
    def _optimize_for_personalization(self, message: str, segment: CustomerSegment) -> str:
        """优化个性化"""
        # 根据客户分群添加个性化元素
        if segment == CustomerSegment.NEW_CUSTOMER:
            personal_touch = "As a new Eufy family member, "
        elif segment == CustomerSegment.VIP_CUSTOMER:
            personal_touch = "As one of our valued VIP customers, "
        elif segment == CustomerSegment.REPEAT_CUSTOMER:
            personal_touch = "Thanks for being a loyal Eufy customer! "
        else:
            personal_touch = "Hi {first_name}, "
        
        # 在开头添加个性化
        optimized = f"{personal_touch}{message.lower()}"
        
        # 添加个性化结尾
        if segment == CustomerSegment.VIP_CUSTOMER:
            optimized += " Your VIP support team is standing by!"
        else:
            optimized += " We're here to help anytime!"
        
        return optimized
    
    def _optimize_for_value_proposition(self, message: str, msg_type: MessageType) -> str:
        """优化价值主张"""
        value_propositions = {
            MessageType.PRODUCT_INQUIRY: "Save hundreds with no monthly fees",
            MessageType.TECHNICAL_SUPPORT: "Get expert help in under 2 minutes",
            MessageType.UPSELL: "Protect your investment with premium features",
            MessageType.RETENTION: "Continue enjoying hassle-free security"
        }
        
        value_prop = value_propositions.get(msg_type, "Experience the Eufy difference")
        
        # 在消息中强调价值
        optimized = f"💡 {value_prop}! {message}"
        
        # 添加价值强化
        if msg_type == MessageType.PRODUCT_INQUIRY:
            optimized += " Join 2M+ happy customers who chose smart savings!"
        
        return optimized
    
    def _optimize_for_channel_specific(self, message: str, channel: PrivateDomainChannel) -> str:
        """渠道特定优化"""
        if channel == PrivateDomainChannel.WHATSAPP_BUSINESS:
            # WhatsApp风格：更个人化，使用表情符号
            optimized = message.replace("Hello", "Hey! 👋")
            if "!" not in optimized:
                optimized += " 😊"
            
        elif channel == PrivateDomainChannel.EMAIL_MARKETING:
            # 邮件风格：正式但友好
            if not message.startswith("Dear") and not message.startswith("Hi"):
                optimized = f"Hi there,\n\n{message}\n\nBest regards,\nThe Eufy Team"
            else:
                optimized = message
                
        elif channel == PrivateDomainChannel.SMS:
            # SMS：简短明了
            optimized = message[:140]  # 限制长度
            if len(message) > 140:
                optimized = optimized.rsplit(' ', 1)[0] + "... Reply for more info"
                
        else:
            optimized = message
        
        return optimized
    
    def _predict_open_rate(self, variant: Dict, channel: PrivateDomainChannel) -> float:
        """预测打开率"""
        base_rates = {
            PrivateDomainChannel.WHATSAPP_BUSINESS: 0.98,
            PrivateDomainChannel.EMAIL_MARKETING: 0.25,
            PrivateDomainChannel.SMS: 0.90,
            PrivateDomainChannel.PUSH_NOTIFICATION: 0.45
        }
        
        base_rate = base_rates.get(channel, 0.5)
        
        # 根据优化类型调整
        if variant['type'] == 'curiosity':
            base_rate *= 1.15
        elif variant['type'] == 'urgency':
            base_rate *= 1.10
        elif variant['type'] == 'personalization':
            base_rate *= 1.08
        
        # 添加随机变化
        variation = random.uniform(-0.05, 0.05)
        
        return min(max(base_rate + variation, 0.1), 0.99)
    
    def _predict_response_rate(self, variant: Dict, channel: PrivateDomainChannel) -> float:
        """预测响应率"""
        base_rates = {
            PrivateDomainChannel.WHATSAPP_BUSINESS: 0.35,
            PrivateDomainChannel.EMAIL_MARKETING: 0.08,
            PrivateDomainChannel.SMS: 0.25,
            PrivateDomainChannel.CHATBOT: 0.60
        }
        
        base_rate = base_rates.get(channel, 0.15)
        
        # 情感影响
        if variant['primary_emotion'] == 'curiosity':
            base_rate *= 1.20
        elif variant['primary_emotion'] == 'fear_of_missing_out':
            base_rate *= 1.15
        
        variation = random.uniform(-0.03, 0.03)
        return min(max(base_rate + variation, 0.05), 0.8)
    
    def _predict_conversion_rate(self, variant: Dict, msg_type: MessageType) -> float:
        """预测转化率"""
        base_rates = {
            MessageType.PRODUCT_INQUIRY: 0.12,
            MessageType.UPSELL: 0.08,
            MessageType.RETENTION: 0.15,
            MessageType.TECHNICAL_SUPPORT: 0.05
        }
        
        base_rate = base_rates.get(msg_type, 0.06)
        
        # 优化类型影响
        if variant['type'] == 'value_proposition':
            base_rate *= 1.25
        elif variant['type'] == 'urgency':
            base_rate *= 1.20
        
        variation = random.uniform(-0.02, 0.02)
        return min(max(base_rate + variation, 0.01), 0.3)
    
    def _calculate_personalization_score(self, variant: Dict, segment: CustomerSegment) -> float:
        """计算个性化得分"""
        content = variant['content'].lower()
        score = 0.0
        
        # 检查个性化元素
        if '{first_name}' in content or 'you' in content:
            score += 0.3
        
        if segment.value in content or 'vip' in content or 'loyal' in content:
            score += 0.4
        
        if 'your' in content:
            score += 0.2
        
        if variant['type'] == 'personalization':
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_urgency_score(self, variant: Dict) -> float:
        """计算紧迫性得分"""
        content = variant['content'].lower()
        urgency_words = [
            'limited', 'expires', 'today', 'now', 'hurry', 'last', 'deadline',
            'urgent', 'immediate', 'while supplies last'
        ]
        
        score = sum(0.1 for word in urgency_words if word in content)
        
        # 表情符号加成
        urgency_emojis = ['⏰', '🔥', '⚡', '⏱️', '🚨']
        if any(emoji in variant['content'] for emoji in urgency_emojis):
            score += 0.1
        
        return min(score, 1.0)
    
    def _analyze_emotional_appeal(self, variant: Dict) -> Dict:
        """分析情感吸引力"""
        content = variant['content']
        
        try:
            sentiment = self.sentiment_analyzer(content)[0]
            
            return {
                'sentiment_label': sentiment['label'],
                'sentiment_score': sentiment['score'],
                'primary_emotion': variant.get('primary_emotion', 'neutral'),
                'emotional_intensity': self._calculate_emotional_intensity(content)
            }
        except:
            return {
                'sentiment_label': 'POSITIVE',
                'sentiment_score': 0.7,
                'primary_emotion': variant.get('primary_emotion', 'neutral'),
                'emotional_intensity': 0.5
            }
    
    def _calculate_emotional_intensity(self, content: str) -> float:
        """计算情感强度"""
        high_intensity_words = [
            'amazing', 'incredible', 'fantastic', 'revolutionary', 'game-changer',
            'urgent', 'critical', 'essential', 'must-have', 'breakthrough'
        ]
        
        content_lower = content.lower()
        intensity = sum(0.1 for word in high_intensity_words if word in content_lower)
        
        # 感叹号加成
        intensity += content.count('!') * 0.05
        
        return min(intensity, 1.0)


class CustomerServicePerformanceTracker:
    """客服性能追踪器"""
    
    def __init__(self):
        self.metrics_database = {}
        self.performance_thresholds = self._load_performance_thresholds()
        
    def track_conversation_metrics(self, conversation_id: str, 
                                 channel: PrivateDomainChannel,
                                 metrics: Dict) -> Dict:
        """追踪对话指标"""
        tracked_metrics = {
            'conversation_id': conversation_id,
            'channel': channel.value,
            'timestamp': datetime.now().isoformat(),
            'response_time': metrics.get('response_time', 0),
            'resolution_time': metrics.get('resolution_time', 0),
            'customer_satisfaction': metrics.get('satisfaction_score', 0),
            'escalation_required': metrics.get('escalated', False),
            'automation_success': metrics.get('auto_resolved', False),
            'follow_up_needed': metrics.get('follow_up', False)
        }
        
        # 存储指标
        self.metrics_database[conversation_id] = tracked_metrics
        
        # 计算性能分数
        performance_score = self._calculate_performance_score(tracked_metrics)
        tracked_metrics['performance_score'] = performance_score
        
        # 生成改进建议
        tracked_metrics['improvement_suggestions'] = self._generate_performance_improvements(
            tracked_metrics
        )
        
        return tracked_metrics
    
    def _load_performance_thresholds(self) -> Dict:
        """加载性能阈值"""
        return {
            'response_time': {
                'excellent': 30,   # 30秒
                'good': 120,       # 2分钟
                'acceptable': 300   # 5分钟
            },
            'resolution_time': {
                'excellent': 300,   # 5分钟
                'good': 900,        # 15分钟
                'acceptable': 1800  # 30分钟
            },
            'satisfaction_score': {
                'excellent': 4.5,
                'good': 4.0,
                'acceptable': 3.5
            },
            'automation_rate': {
                'target': 0.70,    # 70% 自动化解决
                'minimum': 0.50    # 50% 最低要求
            }
        }
    
    def _calculate_performance_score(self, metrics: Dict) -> float:
        """计算性能得分"""
        score_components = {}
        
        # 响应时间得分
        response_time = metrics['response_time']
        if response_time <= self.performance_thresholds['response_time']['excellent']:
            score_components['response_time'] = 1.0
        elif response_time <= self.performance_thresholds['response_time']['good']:
            score_components['response_time'] = 0.8
        elif response_time <= self.performance_thresholds['response_time']['acceptable']:
            score_components['response_time'] = 0.6
        else:
            score_components['response_time'] = 0.4
        
        # 解决时间得分
        resolution_time = metrics['resolution_time']
        if resolution_time <= self.performance_thresholds['resolution_time']['excellent']:
            score_components['resolution_time'] = 1.0
        elif resolution_time <= self.performance_thresholds['resolution_time']['good']:
            score_components['resolution_time'] = 0.8
        elif resolution_time <= self.performance_thresholds['resolution_time']['acceptable']:
            score_components['resolution_time'] = 0.6
        else:
            score_components['resolution_time'] = 0.4
        
        # 满意度得分
        satisfaction = metrics['customer_satisfaction']
        if satisfaction >= self.performance_thresholds['satisfaction_score']['excellent']:
            score_components['satisfaction'] = 1.0
        elif satisfaction >= self.performance_thresholds['satisfaction_score']['good']:
            score_components['satisfaction'] = 0.8
        elif satisfaction >= self.performance_thresholds['satisfaction_score']['acceptable']:
            score_components['satisfaction'] = 0.6
        else:
            score_components['satisfaction'] = 0.4
        
        # 自动化成功加分
        if metrics['automation_success']:
            score_components['automation_bonus'] = 0.1
        else:
            score_components['automation_bonus'] = 0.0
        
        # 升级惩罚
        if metrics['escalation_required']:
            score_components['escalation_penalty'] = -0.1
        else:
            score_components['escalation_penalty'] = 0.0
        
        # 计算加权总分
        weights = {
            'response_time': 0.3,
            'resolution_time': 0.3,
            'satisfaction': 0.4,
            'automation_bonus': 1.0,
            'escalation_penalty': 1.0
        }
        
        total_score = sum(
            score_components[component] * weights[component] 
            for component in score_components
        )
        
        return max(0.0, min(1.0, total_score))
    
    def _generate_performance_improvements(self, metrics: Dict) -> List[str]:
        """生成性能改进建议"""
        improvements = []
        
        # 响应时间改进
        if metrics['response_time'] > self.performance_thresholds['response_time']['good']:
            improvements.append(
                f"Improve response time: Currently {metrics['response_time']}s, "
                f"target <{self.performance_thresholds['response_time']['good']}s"
            )
        
        # 解决时间改进
        if metrics['resolution_time'] > self.performance_thresholds['resolution_time']['good']:
            improvements.append(
                f"Reduce resolution time: Currently {metrics['resolution_time']}s, "
                f"target <{self.performance_thresholds['resolution_time']['good']}s"
            )
        
        # 满意度改进
        if metrics['customer_satisfaction'] < self.performance_thresholds['satisfaction_score']['good']:
            improvements.append(
                f"Increase customer satisfaction: Currently {metrics['customer_satisfaction']}/5, "
                f"target >{self.performance_thresholds['satisfaction_score']['good']}/5"
            )
        
        # 自动化改进
        if not metrics['automation_success'] and not metrics['escalation_required']:
            improvements.append(
                "Consider adding this interaction pattern to automation knowledge base"
            )
        
        # 升级预防
        if metrics['escalation_required']:
            improvements.append(
                "Analyze escalation reason to improve AI handling of similar cases"
            )
        
        return improvements


class PrivateDomainAICustomerServiceOptimizer:
    """私域AI客服优化系统主类"""
    
    def __init__(self):
        self.conversation_optimizer = ConversationFlowOptimizer()
        self.answer_card_generator = AnswerCardGenerator()
        self.message_optimizer = MessageOptimizer()
        self.performance_tracker = CustomerServicePerformanceTracker()
        
    def create_ai_optimized_answer_library(self, faq_data: List[Dict], 
                                         product_catalog: Dict) -> Dict:
        """创建AI优化的标准答案库"""
        
        answer_library = {
            'answer_cards': [],
            'conversation_flows': {},
            'quick_responses': {},
            'escalation_triggers': [],
            'performance_benchmarks': {},
            'automation_coverage': 0.0
        }
        
        # 1. 生成标准化Answer Cards
        for faq in faq_data:
            for question in faq.get('questions', []):
                context = {
                    'product': faq.get('product', 'general'),
                    'category': faq.get('category', 'general'),
                    'channel': PrivateDomainChannel.CHATBOT,
                    'customer_segment': CustomerSegment.NEW_CUSTOMER
                }
                
                answer_card = self.answer_card_generator.generate(question, context)
                answer_library['answer_cards'].append(answer_card)
        
        # 2. 优化对话流程
        entry_points = ['product_inquiry', 'technical_support', 'order_status']
        optimization_goals = ['quick_resolution', 'high_satisfaction', 'upsell_opportunity']
        ai_handoff_points = self._identify_ai_handoff_scenarios()
        
        conversation_flows = self.conversation_optimizer.design_flows(
            entry_points, 
            optimization_goals, 
            ai_handoff_points
        )
        answer_library['conversation_flows'] = conversation_flows
        
        # 3. 创建快速响应模板
        quick_responses = self._generate_quick_response_templates(
            common_scenarios=self._analyze_common_scenarios(faq_data),
            brand_voice=self._get_brand_voice_guidelines()
        )
        answer_library['quick_responses'] = quick_responses
        
        # 4. 设定升级触发器
        answer_library['escalation_triggers'] = self._define_escalation_triggers()
        
        # 5. 建立性能基准
        answer_library['performance_benchmarks'] = self._establish_performance_benchmarks()
        
        # 6. 计算自动化覆盖率
        answer_library['automation_coverage'] = self._calculate_automation_coverage(
            answer_library
        )
        
        return answer_library
    
    def optimize_message_for_engagement(self, message_template: str, 
                                      channel: PrivateDomainChannel,
                                      customer_segment: CustomerSegment = CustomerSegment.NEW_CUSTOMER,
                                      message_type: MessageType = MessageType.PRODUCT_INQUIRY) -> AICustomerServiceResult:
        """优化消息以提高打开率和参与度"""
        
        # 消息优化
        optimized_messages = self.message_optimizer.optimize_message_for_engagement(
            message_template, 
            channel, 
            customer_segment, 
            message_type
        )
        
        # 选择最佳变体
        best_variant = optimized_messages['optimized_versions'][0]
        
        # 生成后续序列
        follow_up_sequence = self._generate_follow_up_sequence(
            best_variant, 
            channel, 
            customer_segment, 
            message_type
        )
        
        # 设定升级触发器
        escalation_triggers = self._get_escalation_triggers_for_message(
            message_type, 
            customer_segment
        )
        
        # 计算性能指标
        performance_metrics = self._calculate_message_performance_metrics(
            best_variant, 
            channel, 
            message_type
        )
        
        # 创建结果
        result = AICustomerServiceResult(
            channel=channel,
            message_type=message_type,
            customer_segment=customer_segment,
            original_message=message_template,
            optimized_messages=optimized_messages['optimized_versions'],
            predicted_open_rate=best_variant['predicted_open_rate'],
            predicted_response_rate=best_variant['predicted_response_rate'],
            predicted_conversion_rate=best_variant['predicted_conversion_rate'],
            sentiment_score=best_variant['emotional_appeal']['sentiment_score'],
            personalization_level=best_variant['personalization_score'],
            automation_confidence=self._calculate_automation_confidence(best_variant),
            escalation_triggers=escalation_triggers,
            follow_up_sequence=follow_up_sequence,
            performance_metrics=performance_metrics
        )
        
        return result
    
    def _identify_ai_handoff_scenarios(self) -> List[str]:
        """识别AI交接场景"""
        return [
            'complex_technical_issue',
            'warranty_claim',
            'billing_dispute',
            'negative_sentiment_detected',
            'multiple_failed_attempts',
            'vip_customer_request',
            'product_defect_report',
            'security_concern'
        ]
    
    def _generate_quick_response_templates(self, common_scenarios: List[str], 
                                         brand_voice: Dict) -> Dict:
        """生成快速响应模板"""
        templates = {}
        
        for scenario in common_scenarios:
            if scenario == 'greeting':
                templates[scenario] = {
                    'formal': "Hello! Thank you for contacting Eufy. How can I help you today?",
                    'casual': "Hey there! 👋 What can I help you with?",
                    'vip': "Hello! As a valued VIP customer, you have priority support. How may I assist you?"
                }
            elif scenario == 'setup_help':
                templates[scenario] = {
                    'quick': "I'll help you set up your device! Which Eufy product are you setting up?",
                    'detailed': "Setting up your Eufy device is easy! Let me guide you through it step by step. First, what product are you setting up?",
                    'video': "Great choice! Here's a quick setup video: [link]. Need me to walk through it with you?"
                }
            elif scenario == 'technical_issue':
                templates[scenario] = {
                    'diagnostic': "I'm here to help resolve your technical issue quickly! Can you describe what's happening?",
                    'empathetic': "I understand how frustrating technical issues can be. Let's get this sorted out for you right away!",
                    'solution_focused': "Let's troubleshoot this together! What specific issue are you experiencing?"
                }
        
        return templates
    
    def _analyze_common_scenarios(self, faq_data: List[Dict]) -> List[str]:
        """分析常见场景"""
        scenarios = set()
        
        for faq in faq_data:
            category = faq.get('category', 'general')
            scenarios.add(category)
        
        # 添加通用场景
        common_scenarios = [
            'greeting', 'setup_help', 'technical_issue', 'order_inquiry',
            'product_question', 'complaint', 'compliment', 'goodbye'
        ]
        
        scenarios.update(common_scenarios)
        return list(scenarios)
    
    def _get_brand_voice_guidelines(self) -> Dict:
        """获取品牌语调指导"""
        return {
            'tone': 'helpful_professional',
            'personality': 'knowledgeable_friend',
            'values': ['privacy', 'simplicity', 'reliability'],
            'avoid': ['technical_jargon', 'pushy_sales', 'generic_responses'],
            'emoji_usage': 'moderate',
            'response_style': 'solution_oriented'
        }
    
    def _define_escalation_triggers(self) -> List[Dict]:
        """定义升级触发器"""
        return [
            {
                'trigger': 'negative_sentiment',
                'threshold': -0.3,
                'action': 'immediate_human_handoff',
                'priority': 'high'
            },
            {
                'trigger': 'complex_technical_issue',
                'keywords': ['firmware', 'connectivity', 'hardware failure'],
                'action': 'technical_specialist',
                'priority': 'medium'
            },
            {
                'trigger': 'vip_customer',
                'condition': 'customer_segment == VIP',
                'action': 'priority_queue',
                'priority': 'high'
            },
            {
                'trigger': 'multiple_failures',
                'threshold': 3,
                'action': 'human_takeover',
                'priority': 'medium'
            },
            {
                'trigger': 'explicit_human_request',
                'keywords': ['speak to human', 'talk to person', 'human agent'],
                'action': 'direct_transfer',
                'priority': 'immediate'
            }
        ]
    
    def _establish_performance_benchmarks(self) -> Dict:
        """建立性能基准"""
        return {
            'response_time_targets': {
                'ai_response': 2,      # 2秒
                'human_response': 30,   # 30秒
                'specialist_response': 120  # 2分钟
            },
            'satisfaction_targets': {
                'ai_resolution': 4.0,
                'human_resolution': 4.5,
                'overall_average': 4.2
            },
            'automation_targets': {
                'tier_1_resolution': 0.80,  # 80%一级问题自动解决
                'tier_2_resolution': 0.40,  # 40%二级问题自动解决
                'overall_automation': 0.70   # 70%整体自动化
            },
            'channel_performance': {
                PrivateDomainChannel.WHATSAPP_BUSINESS: {
                    'target_response_rate': 0.85,
                    'target_satisfaction': 4.3
                },
                PrivateDomainChannel.EMAIL_MARKETING: {
                    'target_open_rate': 0.35,
                    'target_click_rate': 0.12
                }
            }
        }
    
    def _calculate_automation_coverage(self, answer_library: Dict) -> float:
        """计算自动化覆盖率"""
        total_scenarios = len(answer_library.get('answer_cards', []))
        
        if total_scenarios == 0:
            return 0.0
        
        # 计算可自动化的场景数量
        automatable_scenarios = 0
        
        for card in answer_library.get('answer_cards', []):
            if card.get('automation_ready', False):
                automatable_scenarios += 1
        
        # 考虑对话流程的自动化能力
        flows = answer_library.get('conversation_flows', {})
        for flow_steps in flows.values():
            for step in flow_steps:
                if step.get('ai_confidence', 0) >= 0.7:
                    automatable_scenarios += 0.5  # 部分自动化
        
        coverage = min(automatable_scenarios / total_scenarios, 1.0)
        return round(coverage, 2)
    
    def _generate_follow_up_sequence(self, best_variant: Dict, channel: PrivateDomainChannel,
                                   segment: CustomerSegment, msg_type: MessageType) -> List[Dict]:
        """生成后续序列"""
        sequence = []
        
        if msg_type == MessageType.PRODUCT_INQUIRY:
            sequence = [
                {
                    'delay_hours': 2,
                    'message': "Hi! I noticed you were interested in our security camera. Any questions I can answer?",
                    'type': 'follow_up_inquiry'
                },
                {
                    'delay_hours': 24,
                    'message': "Still thinking it over? Here's what makes Eufy different: [link to comparison]",
                    'type': 'value_reinforcement'
                },
                {
                    'delay_hours': 72,
                    'message': "Last chance! Get 15% off your first Eufy camera - expires tonight!",
                    'type': 'urgency_close'
                }
            ]
        elif msg_type == MessageType.TECHNICAL_SUPPORT:
            sequence = [
                {
                    'delay_hours': 4,
                    'message': "How's everything working after our fix? Let me know if you need anything else!",
                    'type': 'satisfaction_check'
                },
                {
                    'delay_hours': 24,
                    'message': "Here are some pro tips to get even more from your Eufy device: [link]",
                    'type': 'value_add'
                }
            ]
        
        # 个性化调整
        if segment == CustomerSegment.VIP_CUSTOMER:
            for step in sequence:
                step['priority'] = 'high'
                step['message'] = f"[VIP] {step['message']}"
        
        return sequence
    
    def _get_escalation_triggers_for_message(self, msg_type: MessageType, 
                                           segment: CustomerSegment) -> List[str]:
        """获取消息的升级触发器"""
        triggers = [
            'negative_sentiment_detected',
            'explicit_human_request',
            'multiple_failed_responses'
        ]
        
        if msg_type == MessageType.TECHNICAL_SUPPORT:
            triggers.extend([
                'complex_technical_issue',
                'hardware_failure_suspected'
            ])
        
        if msg_type == MessageType.COMPLAINT:
            triggers.extend([
                'high_severity_complaint',
                'legal_threat_detected'
            ])
        
        if segment == CustomerSegment.VIP_CUSTOMER:
            triggers.append('vip_immediate_escalation')
        
        return triggers
    
    def _calculate_message_performance_metrics(self, variant: Dict, 
                                             channel: PrivateDomainChannel,
                                             msg_type: MessageType) -> Dict:
        """计算消息性能指标"""
        return {
            'engagement_score': (
                variant['predicted_open_rate'] * 0.3 +
                variant['predicted_response_rate'] * 0.4 +
                variant['predicted_conversion_rate'] * 0.3
            ),
            'automation_readiness': variant.get('automation_confidence', 0.7),
            'personalization_effectiveness': variant['personalization_score'],
            'emotional_resonance': variant['emotional_appeal']['sentiment_score'],
            'channel_optimization': self._calculate_channel_fit_score(variant, channel),
            'message_quality': self._calculate_message_quality_score(variant)
        }
    
    def _calculate_automation_confidence(self, variant: Dict) -> float:
        """计算自动化信心度"""
        confidence = 0.7  # 基础信心度
        
        # 情感积极性影响
        if variant['emotional_appeal']['sentiment_label'] == 'POSITIVE':
            confidence += 0.1
        
        # 个性化程度影响
        confidence += variant['personalization_score'] * 0.1
        
        # 消息清晰度影响
        content_length = len(variant['content'])
        if 50 <= content_length <= 200:  # 适中长度
            confidence += 0.1
        
        return min(confidence, 0.95)
    
    def _calculate_channel_fit_score(self, variant: Dict, channel: PrivateDomainChannel) -> float:
        """计算渠道适配度分数"""
        content = variant['content']
        score = 0.7  # 基础分数
        
        if channel == PrivateDomainChannel.WHATSAPP_BUSINESS:
            # WhatsApp偏好个人化和表情符号
            if any(emoji in content for emoji in ['👋', '😊', '🔥', '⚡']):
                score += 0.1
            if len(content) <= 600:  # 适合WhatsApp的长度
                score += 0.1
                
        elif channel == PrivateDomainChannel.EMAIL_MARKETING:
            # 邮件偏好结构化和专业性
            if 'Dear' in content or 'Best regards' in content:
                score += 0.1
            if '\n' in content:  # 有段落结构
                score += 0.1
                
        elif channel == PrivateDomainChannel.SMS:
            # SMS要求简洁
            if len(content) <= 160:
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_message_quality_score(self, variant: Dict) -> float:
        """计算消息质量分数"""
        quality_factors = {
            'clarity': self._assess_clarity(variant['content']),
            'relevance': self._assess_relevance(variant),
            'actionability': self._assess_actionability(variant['content']),
            'emotional_balance': self._assess_emotional_balance(variant)
        }
        
        weights = {
            'clarity': 0.3,
            'relevance': 0.3,
            'actionability': 0.2,
            'emotional_balance': 0.2
        }
        
        quality_score = sum(
            quality_factors[factor] * weights[factor]
            for factor in quality_factors
        )
        
        return round(quality_score, 2)
    
    def _assess_clarity(self, content: str) -> float:
        """评估清晰度"""
        # 简化实现：基于句子长度和复杂度
        sentences = content.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # 理想句子长度：10-20词
        if 10 <= avg_length <= 20:
            return 1.0
        elif avg_length < 10:
            return 0.8
        else:
            return max(0.4, 1.0 - (avg_length - 20) / 20)
    
    def _assess_relevance(self, variant: Dict) -> float:
        """评估相关性"""
        # 基于优化类型和内容匹配度
        relevance_scores = {
            'personalization': 0.9,
            'value_proposition': 0.85,
            'channel_optimized': 0.8,
            'urgency': 0.75,
            'curiosity': 0.7
        }
        
        return relevance_scores.get(variant['type'], 0.7)
    
    def _assess_actionability(self, content: str) -> float:
        """评估可操作性"""
        action_words = [
            'click', 'download', 'call', 'visit', 'buy', 'order',
            'try', 'get', 'start', 'join', 'reply', 'contact'
        ]
        
        content_lower = content.lower()
        action_count = sum(1 for word in action_words if word in content_lower)
        
        # 有明确行动号召得分更高
        if action_count >= 2:
            return 1.0
        elif action_count == 1:
            return 0.8
        else:
            return 0.5
    
    def _assess_emotional_balance(self, variant: Dict) -> float:
        """评估情感平衡"""
        emotional_appeal = variant.get('emotional_appeal', {})
        
        # 积极情感但不过度
        sentiment_score = emotional_appeal.get('sentiment_score', 0.5)
        
        if 0.6 <= sentiment_score <= 0.8:  # 适度积极
            return 1.0
        elif 0.5 <= sentiment_score < 0.6 or 0.8 < sentiment_score <= 0.9:
            return 0.8
        else:
            return 0.6


def main():
    """主函数 - 演示用法"""
    # 创建优化器
    optimizer = PrivateDomainAICustomerServiceOptimizer()
    
    # 示例FAQ数据
    sample_faq_data = [
        {
            'category': 'setup',
            'product': 'eufycam_3',
            'questions': [
                'How do I set up my Eufy camera?',
                'What app do I need to download?',
                'How long does setup take?'
            ]
        },
        {
            'category': 'technical',
            'product': 'eufycam_3',
            'questions': [
                'Why is my camera not connecting to WiFi?',
                'How do I reset my camera?',
                'Battery life seems shorter than expected'
            ]
        }
    ]
    
    # 示例产品目录
    sample_product_catalog = {
        'eufycam_3': {
            'name': 'eufyCam 3',
            'features': ['4K resolution', '365-day battery', 'Local storage'],
            'price': 219.99
        }
    }
    
    # 创建AI优化答案库
    answer_library = optimizer.create_ai_optimized_answer_library(
        sample_faq_data,
        sample_product_catalog
    )
    
    print("=== 私域AI客服答案库创建完成 ===")
    print(f"Answer Cards数量: {len(answer_library['answer_cards'])}")
    print(f"对话流程数量: {len(answer_library['conversation_flows'])}")
    print(f"自动化覆盖率: {answer_library['automation_coverage']*100:.1f}%")
    
    # 示例消息优化
    sample_message = "Hi! Thanks for your interest in our security camera. How can I help you today?"
    
    result = optimizer.optimize_message_for_engagement(
        sample_message,
        PrivateDomainChannel.WHATSAPP_BUSINESS,
        CustomerSegment.NEW_CUSTOMER,
        MessageType.PRODUCT_INQUIRY
    )
    
    print("\n=== 消息优化结果 ===")
    print(f"渠道: {result.channel.value}")
    print(f"客户分群: {result.customer_segment.value}")
    print(f"预测打开率: {result.predicted_open_rate*100:.1f}%")
    print(f"预测响应率: {result.predicted_response_rate*100:.1f}%")
    print(f"预测转化率: {result.predicted_conversion_rate*100:.1f}%")
    print(f"个性化程度: {result.personalization_level:.2f}/1.0")
    print(f"自动化信心度: {result.automation_confidence:.2f}/1.0")
    
    print("\n=== 优化版本 (前3个) ===")
    for i, version in enumerate(result.optimized_messages[:3], 1):
        print(f"\n{i}. 类型: {version['optimization_type']}")
        print(f"   内容: {version['content'][:100]}...")
        print(f"   响应率: {version['predicted_response_rate']*100:.1f}%")
    
    print(f"\n=== 后续序列 ===")
    for i, follow_up in enumerate(result.follow_up_sequence, 1):
        print(f"{i}. {follow_up['delay_hours']}小时后: {follow_up['message'][:80]}...")
    
    print(f"\n=== 升级触发器 ===")
    for trigger in result.escalation_triggers[:3]:
        print(f"- {trigger}")


if __name__ == "__main__":
    # 下载必要的数据
    import nltk
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except:
        pass
    
    main()