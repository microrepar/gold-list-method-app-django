from django.db import models


class GroupChoices(models.TextChoices):
    HEADLIST = 'A', 'HEADLIST'
    B        = 'B', 'B'
    C        = 'C', 'C'
    D        = 'D', 'D'
    NEW_PAGE = 'NP', 'NP'
    REMOVED  = 'RM', 'RM'


class ProfileChoices(models.TextChoices):
    A = 'A', 'Student'
    P = 'P', 'Professor'
    G = 'G', 'Admin'
    R = 'R', 'Root'


class StatusChoices(models.TextChoices):
    ACTIVE    = 'Active', 'Active'
    INACTIVE  = 'Inactive', 'Inactive'
    PENDING   = 'Pending', 'Pending'
    SUSPENDED = 'Suspended', 'Suspended'
    ARCHIVED  = 'Archived', 'Archived'
    APPROVED  = 'Approved', 'Approved'
    