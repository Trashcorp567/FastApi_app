import asyncio

from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.models import db_helper, User, Profile, Post, Order, Product, OrderProductAssociation


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(Username=username)
    session.add(user)
    await session.commit()
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.Username == username)
    user: User | None = await session.scalar(stmt)
    return user


async def create_user_profile(
        session: AsyncSession,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        bio: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        bio=bio,
    )
    session.add(profile)
    await session.commit()
    return profile


async def show_users_with_profiles(session: AsyncSession) -> list[User]:
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    users = await session.scalars(stmt)
    for user in users:
        print(user.Username)
        print(user.profile.bio)


async def get_posts_by_author(session: AsyncSession):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)
    for post in posts:
        print(post)
        print(post.user)


async def show_users_with_posts(session: AsyncSession):
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars()
    for user in users:
        print(user)
        for post in user.posts:
            print("-", post)


async def get_profile_with_post_users(session: AsyncSession):
    stmt = (
        select(Profile)
        .order_by(Profile.id)
        .options(
            joinedload(Profile.user).selectinload(User.posts),
        )
    )
    profiles = await session.scalars(stmt)

    for profile in profiles:
        print(profile.first_name, profile.user, profile.user.posts)


async def get_users_posts_profiles(session: AsyncSession):
    stmt = (
        select(User)
        .options(
        joinedload(User.profile),
            selectinload(User.posts),
        )
        .order_by(User.id)
    )
    users = await session.scalars(stmt)

    for user in users:
        print(user, user.profile and user.profile.first_name)
        for post in user.posts:
            print(post)


async def create_posts(*posts_titles: str, session: AsyncSession, user_id: int,) -> list[Post]:
    posts = [
        Post(title=title, user_id=user_id)
        for title in posts_titles
    ]
    session.add_all(posts)
    await session.commit()
    print(posts)
    return posts


async def main_relations(session: AsyncSession):
    pass


async def create_order(session: AsyncSession, promocode: str | None = None, ) -> Order:
    order = Order(promocode=promocode)
    session.add(order)
    await session.commit()
    return order


async def create_product(
        session: AsyncSession,
        name: str,
        description: str,
        price: int,
) -> Product:
    product = Product(name=name,
                      description=description,
                      price=price,)
    session.add(product)
    await session.commit()
    return product


async def orders_with_products(session: AsyncSession) -> list[Order]:
    stmt = select(Order).options(selectinload(Order.products))
    order = await session.scalars(stmt)
    return list(order)


async def create_orders_and_products(session: AsyncSession):
    order1 = await create_order(session)
    promo = await create_order(session, promocode="promo")

    mouse = await create_product(session, "Mouse", "Great gaming mouse", 190)
    keyboard = await create_product(session, "keyboard", "Great gaming keyboard", 290)
    display = await create_product(session, "display", "Office display", 390)

    order1 = await session.scalar(
        select(Order).where(Order.id == order1.id).options(selectinload(Order.products)),
    )

    promo = await session.scalar(
        select(Order).where(Order.id == promo.id).options(selectinload(Order.products)),
    )

    order1.products.append(mouse)
    order1.products.append(keyboard)
    promo.products.append(keyboard)
    promo.products.append(display)

    await session.commit()


async def demo_get_orders_with_product_through_secondary(session: AsyncSession):
    orders = await orders_with_products(session)
    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")
        for product in order.products:#type: Product
            print("-", product.id, product.name, product.price)


async def create_orders_with_product_through_secondary_with_assoc(session: AsyncSession):
    stmt = (
        select(Order).
        options(selectinload(Order.products_details).joinedload(OrderProductAssociation.product),
                ).order_by(Order.id)
    )
    orders = await session.scalars(stmt)

    return list(orders)


async def demo_get_orders_with_product_with_assoc(session: AsyncSession):
    orders = await create_orders_with_product_through_secondary_with_assoc(session)

    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")
        for order_product_details in order.products_details:#type: OrderProductAssociation
            print("-", order_product_details.product.name, order_product_details.product.price, "qty:", order_product_details.count)


async def create_gift_product_for_exist_orders(session: AsyncSession):
    orders = await create_orders_with_product_through_secondary_with_assoc(session)
    gift_product = await create_product(
        session,
        name='Gift',
        description="Подарок",
        price=0,
    )
    for order in orders:
        order.products_details.append(OrderProductAssociation(
            count=1,
            unit_price=0,
            product=gift_product,
        )
        )


async def demo_m2m(session: AsyncSession):
    await demo_get_orders_with_product_with_assoc(session)


async def main():
    async with db_helper.session_factory() as sess:
        await demo_m2m(sess)

if __name__ == "__main__":
    asyncio.run(main())
