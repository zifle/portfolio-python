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
    album_toggle_publish,
)
from .location import LocationsIndex
from .category import (
    CategoryIndex,
    CategoryDetail,
)
from .text import (
    TextIndex,
)
from .upload import (
    ImageUpload,
)
from .image import post_image_description