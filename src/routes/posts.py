from datetime import date
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi import Path
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.database.connect import get_db
from src.database.models import User, Post
from src.repository import posts as repository_posts
from src.schemas import PostDb, PostReadResponseSchema, PostsReadResponseSchema, ReturnMessageResponseSchema

from src.services.auth import auth_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostDb)
async def image_create(
    text: str,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        image = await repository_posts.post_create(
            text, current_user, db
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Post already exists")
    return image


@router.delete("/{image_id}", response_model=ReturnMessageResponseSchema)
async def image_delete(
    image_id: int = Path(description="The ID of image to delete", ge=1),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image: Post = await repository_posts.post_delete(image_id, current_user, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image is absent.",
        )
    return {"message": f"Image with ID {image_id} is successfully deleted."}


def shortent(about: str) -> str:
    if len(about) > 48:
        about = about[:48] + "…"
    return about


@router.get(
    "/{id}",
    response_model=PostReadResponseSchema,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def image_read(
    id: int,
    db: AsyncSession = Depends(get_db)):
    post: Post = await repository_posts.post_read(id, db)

    if post:
        return {"image_id": post.id}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Image {id} is absent.",
    )


@router.get(
    "/find/{search:path}",
    response_model=List[PostsReadResponseSchema],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def images_search(
    search: str,
    db: AsyncSession = Depends(get_db)):
    '''

    Retrieves a list of posts which are corresponded to search filter. Call of this
    function is rate limited.

    :param db: The database session.
    :type db: Session
    :return: List of posts
    :rtype: List[PostsReadResponseSchema]

    Searches posts into database which is identified by AsyncSession db.

    For example:

    Get images with case insensitive username 'moroz' which are created
    from 2023-08-24 (-5 days) up to 2023-08-29 and each post:
    |.../api/images/find/roy bebru/2023-08-29/-5/
    search="Moroz/2023-08-29/-5"

    Get all images:

    |.../api/posts/find/
    '''

    username = None
    from_date = None
    days = None
    ind = 0

    search_args = search.split("/")

    if search_args[0] == "":
        ind += 1
    if len(search_args) > ind:
        if len(search_args[ind]):
            if search_args[ind].startswith("@"):
                username = search_args[ind][1:]
                ind += 1
            elif not search_args[ind][0].isdigit() and not search_args[ind][
                0
            ].startswith("-"):
                username = search_args[ind]
                ind += 1
        else:
            ind += 1  # skip empty

    if len(search_args) > ind:
        try:
            from_date = date.fromisoformat(search_args[ind])
            ind += 1
        except ValueError:
            pass

    if len(search_args) > ind:
        try:
            days = int(search_args[ind])
            ind += 1
        except ValueError:
            pass

    if from_date is None and days is None and username:
        username = None

    records = await repository_posts.post_search(
        username, from_date, days,
        db)
    return [
        {
            'post_id': id, 'post_text': text,
        }
        for id, text in records]
