from aiogram import Dispatcher

from handlers.start import router as start_router
from handlers.review import router as review_router
from handlers.my_reviews import router as my_reviews_router
from handlers.admin import router as admin_router

from core.middlewares.message_cleanup import MessageCleanupMiddleware
from database.session import init_models


dp = Dispatcher()

# =========================================================
# 🚀 STARTUP
# =========================================================

dp.startup.register(init_models)

# =========================================================
# 🧼 MIDDLEWARES
# =========================================================

dp.message.middleware(MessageCleanupMiddleware())
dp.callback_query.middleware(MessageCleanupMiddleware())

# =========================================================
# 📦 ROUTERS
# =========================================================

dp.include_router(start_router)
dp.include_router(review_router)
dp.include_router(my_reviews_router)
dp.include_router(admin_router)