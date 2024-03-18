from datetime import date, timedelta

from sqlalchemy import (
    select,
    text,
    and_,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Post


async def post_create(
    text: str,
    user: User,
    db: AsyncSession,
) -> Post:
    post = Post(
        text=text,
        user_id=user.id,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def post_delete(post_id: int, user: User, db: AsyncSession) -> Post | None:
    sq = select(Post).filter(and_(Post.id == post_id, Post.user_id == user.id))
    result = await db.execute(sq)
    post = result.scalar_one_or_none()

    if post:
        await db.execute(sq)
        # Delete suitable post
        await db.delete(post)
        await db.commit()
    return post


async def post_read(id: int, db: AsyncSession) -> Post:
    sq = select(Post).filter(Post.id == id)
    result = await db.execute(sq)
    post = result.scalar_one_or_none()
    return post


async def post_search(
    username: str,
    from_date: date | None,
    days: int | None,
    db: AsyncSession,
) -> list:
    sq_username_join = ""
    sq_username_where = ""
    sq_between_date = ""
    if username:
        sq_username_join = "INNER JOIN users us ON us.id = im.user_id"
        sq_username_where = "us.username ILIKE :username AND "
    to_date = None
    if isinstance(days, int) and from_date is None:
        from_date = date.today()
    if from_date:
        sq_between_date = (
            ":from_date <= im.created_at " "AND im.created_at < :to_date AND "
        )
        if isinstance(days, int):
            if days < 0:
                to_date = date.today() + timedelta(days=days)
                if from_date > to_date:
                    from_date, to_date = to_date, from_date
            else:
                to_date = from_date + timedelta(days=days)
        else:
            to_date = from_date + timedelta(days=1)

    ## list of searched fields ##
    only_fields = "po.id, po.text"
    ##

    if sq_username_join or sq_between_date:
        sq = text(
            f"""
            SELECT {only_fields}
            FROM posts im
            {sq_username_join}
            WHERE {sq_username_where}{sq_between_date}True
        """
        )
    else:
        sq = text(
            f"""
            SELECT {only_fields}
            FROM posts im
        """
        )
    # print(sq, str(from_date), str(days), str(to_date))

    # Execute the select query asynchronously and fetch the results
    result = await db.execute(
        sq,
        {
            "username": username,
            "from_date": from_date,
            "to_date": to_date,
        },
    )
    posts = result.fetchall()

    # for im in posts:
    #     print(po)

    return posts
