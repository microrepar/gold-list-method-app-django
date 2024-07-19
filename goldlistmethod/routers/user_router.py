from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.orm import create_schema

from goldlistmethod.models.customuser import CustomUser

router = Router()

CustomUserSchema = create_schema(CustomUser)


class CustomUserIn(Schema):
    id: Optional[int] = None
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@router.get('/', response=List[CustomUserSchema])
def list_users(request):
    qs = CustomUser.objects.all()
    return qs


@router.put('/{user_id}', response=CustomUserSchema)
def update_user(request, user_id: int, payload: CustomUserIn):
    user = get_object_or_404(CustomUser, id=user_id)
    for attr, value in payload.dict().items():
        if value:
            setattr(user, attr, value)
    user.save()
    return user


@router.post('/find_by_field/', response=List[CustomUserSchema])
def find_by_field(request, payload: CustomUserIn):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        return CustomUser.objects.filter(**filters)
    return CustomUser.objects.filter(id=None)



