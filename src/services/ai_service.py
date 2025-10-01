import os
import openai
import anthropic
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class AIService:
    def __init__(self):
        # إعداد مفاتيح API
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        
        # إعداد عناوين URL الأساسية
        self.openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.claude_base_url = os.getenv('CLAUDE_BASE_URL', 'https://api.anthropic.com/v1')
        self.deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        
        # إعداد عملاء API
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
        
        # إعدادات النماذج
        self.model_configs = {
            'deepseek': {
                'model': 'deepseek-reasoner',
                'max_tokens': 5000,
                'temperature': 0.7
            },
            'gpt5': {
                'model': 'gpt-5',
                'max_tokens': 5000,
                'temperature': 0.7
            },
            'claude': {
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 5000,
                'temperature': 1.0
            }
        }

    def analyze_request_type(self, message: str) -> str:
        """
        تحليل نوع الطلب وتحديد النموذج الأنسب
        """
        message_lower = message.lower()
        
        # كلمات مفتاحية للتفكير والتحليل (DeepSeek)
        thinking_keywords = [
            'تحليل', 'حلل', 'فكر', 'استنتج', 'خطة', 'استراتيجية', 'مشكلة', 'حل',
            'منطق', 'تفكير', 'دراسة', 'بحث', 'تقييم', 'مقارنة', 'analyze', 'think',
            'strategy', 'plan', 'problem', 'solve', 'logic', 'reasoning'
        ]
        
        # كلمات مفتاحية لتوليد الصور والمواقع (GPT-5)
        visual_keywords = [
            'صورة', 'رسم', 'تصميم', 'موقع', 'واجهة', 'html', 'css', 'javascript',
            'كود', 'برمجة', 'تطبيق', 'image', 'draw', 'design', 'website', 'code',
            'programming', 'ui', 'interface'
        ]
        
        # كلمات مفتاحية للإبداع النصي (Claude)
        creative_keywords = [
            'قصة', 'اكتب', 'أنشئ', 'إبداعي', 'شعر', 'مقال', 'محتوى', 'تسويق',
            'رسالة', 'نص', 'story', 'write', 'creative', 'content', 'article',
            'marketing', 'text', 'poetry'
        ]
        
        # فحص الكلمات المفتاحية
        if any(keyword in message_lower for keyword in thinking_keywords):
            return 'deepseek'
        elif any(keyword in message_lower for keyword in visual_keywords):
            return 'gpt5'
        elif any(keyword in message_lower for keyword in creative_keywords):
            return 'claude'
        
        # افتراضي: استخدام DeepSeek للتفكير العام
        return 'deepseek'

    async def call_deepseek(self, message: str) -> Dict[str, Any]:
        """
        استدعاء نموذج DeepSeek للتفكير والتحليل
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.deepseek_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model_configs['deepseek']['model'],
                'messages': [
                    {'role': 'user', 'content': message}
                ],
                'max_tokens': self.model_configs['deepseek']['max_tokens'],
                'temperature': self.model_configs['deepseek']['temperature']
            }
            
            response = requests.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'model': 'DeepSeek',
                    'content': result['choices'][0]['message']['content'],
                    'usage': result.get('usage', {})
                }
            else:
                return {
                    'success': False,
                    'error': f'DeepSeek API Error: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'DeepSeek Error: {str(e)}'
            }

    async def call_gpt5(self, message: str) -> Dict[str, Any]:
        """
        استدعاء نموذج GPT-5 لتوليد الصور والمواقع
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_configs['gpt5']['model'],
                messages=[
                    {'role': 'user', 'content': message}
                ],
                max_tokens=self.model_configs['gpt5']['max_tokens'],
                temperature=self.model_configs['gpt5']['temperature']
            )
            
            return {
                'success': True,
                'model': 'GPT-5',
                'content': response.choices[0].message.content,
                'usage': response.usage.model_dump() if response.usage else {}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'GPT-5 Error: {str(e)}'
            }

    async def call_claude(self, message: str) -> Dict[str, Any]:
        """
        استدعاء نموذج Claude للإخراج الإبداعي
        """
        try:
            response = self.claude_client.messages.create(
                model=self.model_configs['claude']['model'],
                max_tokens=self.model_configs['claude']['max_tokens'],
                temperature=self.model_configs['claude']['temperature'],
                messages=[
                    {'role': 'user', 'content': message}
                ]
            )
            
            return {
                'success': True,
                'model': 'Claude',
                'content': response.content[0].text,
                'usage': response.usage.model_dump() if response.usage else {}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Claude Error: {str(e)}'
            }

    async def process_request(self, message: str, model_preference: Optional[str] = None) -> Dict[str, Any]:
        """
        معالجة الطلب وتوجيهه إلى النموذج المناسب
        """
        # تحديد النموذج المناسب
        if model_preference and model_preference in self.model_configs:
            selected_model = model_preference
        else:
            selected_model = self.analyze_request_type(message)
        
        # استدعاء النموذج المحدد
        if selected_model == 'deepseek':
            return await self.call_deepseek(message)
        elif selected_model == 'gpt5':
            return await self.call_gpt5(message)
        elif selected_model == 'claude':
            return await self.call_claude(message)
        else:
            return {
                'success': False,
                'error': f'Unknown model: {selected_model}'
            }

    def get_available_models(self) -> Dict[str, Any]:
        """
        الحصول على قائمة النماذج المتاحة
        """
        return {
            'models': [
                {
                    'id': 'gentle-ai',
                    'name': 'Gentle AI',
                    'description': 'النموذج الذكي الموحد الذي يجمع قدرات DeepSeek وGPT-5 وClaude',
                    'auto_routing': True
                },
                {
                    'id': 'gentle-r1',
                    'name': 'Gentle R1',
                    'description': 'نموذج التفكير والتحليل المنطقي (DeepSeek)',
                    'model_type': 'deepseek'
                },
                {
                    'id': 'gentle-vip',
                    'name': 'Gentle VIP',
                    'description': 'نموذج الإخراج الإبداعي عالي الجودة (Claude)',
                    'model_type': 'claude'
                }
            ]
        }
