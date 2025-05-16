from .user_controller import (
    RegisterResource,
    LoginResource,
    LogoutResource,
    UserByIdResource,
    UserByUsernameResource,
    UserByEmailResource,
    AllUsersResource,
)

from .conference_controller import (
    ConferenceDetailResource,
    ConferenceListCreateResource,
    ConferenceUserRolesResource, # We will add this next
)

from .paper_controller import (
    PaperListCreateResource,
    PaperDetailResource,
)
