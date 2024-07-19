
from typing import List

from ninja import NinjaAPI

from goldlistmethod.routers import (notebook_router, pagesection_router,
                                    sentencelabel_router,
                                    sentencetranslation_router, user_router)

api = NinjaAPI()

api.add_router('/users/', user_router.router)
api.add_router('/notebooks/', notebook_router.router)
api.add_router('/pagesections/', pagesection_router.router)
api.add_router('/sentencelabels/', sentencelabel_router.router)
api.add_router('/sentencetranslations/', sentencetranslation_router.router)
