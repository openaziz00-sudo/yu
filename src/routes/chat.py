from flask import Blueprint, request, jsonify
from src.models.chat import db, Chat, Message
from src.services.ai_service import AIService
import asyncio
import json

chat_bp = Blueprint('chat', __name__)
ai_service = AIService()

@chat_bp.route('/chats', methods=['GET'])
def get_chats():
    """الحصول على قائمة المحادثات"""
    try:
        chats = Chat.query.order_by(Chat.updated_at.desc()).all()
        return jsonify({
            'success': True,
            'chats': [chat.to_dict() for chat in chats]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chats', methods=['POST'])
def create_chat():
    """إنشاء محادثة جديدة"""
    try:
        data = request.get_json()
        title = data.get('title', 'محادثة جديدة')
        
        chat = Chat(title=title)
        db.session.add(chat)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'chat': chat.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chats/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    """الحصول على محادثة محددة مع رسائلها"""
    try:
        chat = Chat.query.get_or_404(chat_id)
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).all()
        
        return jsonify({
            'success': True,
            'chat': chat.to_dict(),
            'messages': [message.to_dict() for message in messages]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chats/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """حذف محادثة"""
    try:
        chat = Chat.query.get_or_404(chat_id)
        db.session.delete(chat)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف المحادثة بنجاح'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chats/<int:chat_id>/messages', methods=['POST'])
def send_message(chat_id):
    """إرسال رسالة والحصول على رد من الذكاء الاصطناعي"""
    try:
        data = request.get_json()
        message_content = data.get('message', '').strip()
        model_preference = data.get('model')  # اختياري
        
        if not message_content:
            return jsonify({
                'success': False,
                'error': 'محتوى الرسالة مطلوب'
            }), 400
        
        # التحقق من وجود المحادثة
        chat = Chat.query.get_or_404(chat_id)
        
        # حفظ رسالة المستخدم
        user_message = Message(
            chat_id=chat_id,
            role='user',
            content=message_content
        )
        db.session.add(user_message)
        
        # معالجة الطلب باستخدام الذكاء الاصطناعي
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_response = loop.run_until_complete(
            ai_service.process_request(message_content, model_preference)
        )
        loop.close()
        
        if ai_response['success']:
            # حفظ رد الذكاء الاصطناعي
            assistant_message = Message(
                chat_id=chat_id,
                role='assistant',
                content=ai_response['content'],
                model_used=ai_response['model']
            )
            
            # إضافة معلومات الاستخدام كبيانات وصفية
            if 'usage' in ai_response:
                assistant_message.set_metadata({
                    'usage': ai_response['usage'],
                    'model_details': ai_response.get('model', 'Unknown')
                })
            
            db.session.add(assistant_message)
            
            # تحديث عنوان المحادثة إذا كانت الرسالة الأولى
            if len(chat.messages) == 0:
                # استخدام أول 50 حرف من الرسالة كعنوان
                chat.title = message_content[:50] + ('...' if len(message_content) > 50 else '')
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user_message': user_message.to_dict(),
                'assistant_message': assistant_message.to_dict()
            })
        else:
            # في حالة فشل الذكاء الاصطناعي، احفظ رسالة المستخدم فقط
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': ai_response.get('error', 'خطأ في معالجة الطلب'),
                'user_message': user_message.to_dict()
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/models', methods=['GET'])
def get_models():
    """الحصول على قائمة النماذج المتاحة"""
    try:
        models = ai_service.get_available_models()
        return jsonify({
            'success': True,
            **models
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/health', methods=['GET'])
def health_check():
    """فحص حالة الخدمة"""
    return jsonify({
        'success': True,
        'message': 'Gentle AI Backend is running',
        'version': '1.0.0'
    })
