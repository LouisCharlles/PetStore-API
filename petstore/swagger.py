from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="PetStore",
        default_version="v1",
        description="Uma API REST desenvolvida em Django feita para ser um serviço de marcar consultas em um veterinário. A aplicação permite cadastrar: usuários, pets e veterinários. Um usuário pode ter 1 ou mais pets e pode marcar consultas com veterinários e vizualizar as informações de suas consultas e seus pets. O veterinário pode vizualizar a consulta, agendar uma data e um horário para essa consulta, e definir se ela já foi realizada ou não. A aplicação também disponibilza as opções de atualizar as informações do usuário, pet, veterinário e consulta, assim como poder deleta-los se necessário.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contato@PetStore.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)