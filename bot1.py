#!/usr/bin/env python3
import logging
import threading
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

class TelegramBot:
    def __init__(self):
        self.TOKEN = "8250346512:AAFpEDVOny-iuMOvdkdtazAOUf-F_PiyBZs"
        self.OWNER_ID = 6309982230
        self.REQUIRED_CHANNELS = ["@WOBSN2"]
        self.WARNING_TIMEOUT = 15
        
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        channels_text = "\n".join([f"• {channel}" for channel in self.REQUIRED_CHANNELS])
        await update.message.reply_text(
            f"🤖 تم تفعيل بوت مراقبة الاشتراك\n\n"
            f"✅ القنوات المطلوبة:\n{channels_text}\n\n"
            f"📊 للإحصائيات: /stats"
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.OWNER_ID:
            return
        await update.message.reply_text("📊 البوت يعمل بنجاح على خادم Hostinger!")
    
    async def check_membership(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if user.id == self.OWNER_ID:
            return
        
        if update.message and update.message.text and update.message.text.startswith('/'):
            return
        
        not_joined = []
        for channel in self.REQUIRED_CHANNELS:
            try:
                member = await context.bot.get_chat_member(chat_id=channel.strip(), user_id=user.id)
                if member.status not in ["member", "administrator", "creator"]:
                    not_joined.append(channel)
            except Exception as e:
                error_msg = str(e).lower()
                if "user not found" in error_msg or "user_not_participant" in error_msg:
                    not_joined.append(channel)
        
        if not_joined:
            try:
                await update.message.delete()
                
                keyboard = []
                for channel in not_joined:
                    channel_name = channel.replace("@", "")
                    keyboard.append([InlineKeyboardButton(
                        f"قناة {channel_name}", 
                        url=f"https://t.me/{channel_name}"
                    )])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                username_mention = f"@{user.username}" if user.username else user.first_name
                
                warning_msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"عذراً {username_mention} 🏴\n\nاشترك في قناة المجموعة لتتمكن من الكلام:\nللاشتراك اضغط أسفل ⬇",
                    reply_markup=reply_markup
                )
                
                async def delete_warning():
                    await asyncio.sleep(self.WARNING_TIMEOUT)
                    try:
                        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=warning_msg.message_id)
                    except:
                        pass
                
                # استخدام asyncio.create_task بدلاً من threading
                asyncio.create_task(delete_warning())
                
                self.logger.info(f"حذف رسالة من المستخدم {user.id} - غير مشترك في: {', '.join(not_joined)}")
                
            except Exception as e:
                self.logger.error(f"خطأ في معالجة رسالة غير المشترك: {e}")
    
    def start(self):
        try:
            self.logger.info("🚀 بدء تشغيل البوت على خادم Hostinger...")
            
            self.application = Application.builder().token(self.TOKEN).build()
            
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("stats", self.stats_command))
            self.application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, self.check_membership))
            
            self.logger.info("✅ البوت يعمل بنجاح!")
            self.logger.info(f"📋 القنوات المطلوبة: {', '.join(self.REQUIRED_CHANNELS)}")
            
            self.application.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            self.logger.error(f"❌ فشل في تشغيل البوت: {e}")
    
    def stop(self):
        if self.application:
            self.application.stop()

import asyncio

def main():
    print("🚀 بدء تشغيل بوت تيليجرام - نسخة الخادم")
    print("=" * 50)
    
    bot = TelegramBot()
    
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت")
        bot.stop()
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == '__main__':
    main()
