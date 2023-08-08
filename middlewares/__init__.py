from .throttling import ThrottlingMiddleware
from .cq_bug_fix import CQBugFix
from .watcher import WatcherMiddleware
from loader import dp


if __name__ == "middlewares":
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(CQBugFix())
    dp.middleware.setup(WatcherMiddleware())
