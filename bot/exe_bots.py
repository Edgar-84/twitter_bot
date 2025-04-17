import logging
from bot.main import bot_dp, bot, user_router
from bot.handlers.user_handlers import register_user_handlers


async def exe_bot():
    """Function to start a bot"""
    print('BOT started')
    logging.info(msg="BOT started")

    await register_user_handlers(router=user_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot_dp.start_polling(bot)
