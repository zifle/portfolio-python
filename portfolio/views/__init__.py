from .index import index_view
from .auth import (
    set_csrf_token,
    login_view,
    logout_view,
    user,
)
from .album import (
    AlbumIndex,
    AlbumDetail,
    AlbumUpload,
    albumTogglePublish,
)
from .location import LocationsIndex
from .category import (
    CategoryIndex,
    CategoryDetail,
)