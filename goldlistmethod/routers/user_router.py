from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.orm import create_schema

from usermanager.models import StudentUser

router = Router()

UserSchema = create_schema(StudentUser)


class UserIn(Schema):
    id: Optional[int] = None
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@router.get('/', response=List[UserSchema])
def list_users(request):
    qs = StudentUser.objects.all()
    return qs


@router.put('/{user_id}', response=UserSchema)
def update_user(request, user_id: int, payload: UserIn):
    user = get_object_or_404(StudentUser, id=user_id)
    for attr, value in payload.dict().items():
        if value:
            setattr(user, attr, value)
    user.save()
    return user


@router.post('/find_by_field/', response=List[UserSchema])
def find_by_field(request, payload: UserIn):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        return StudentUser.objects.filter(**filters)
    return StudentUser.objects.filter(id=None)



