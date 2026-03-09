#admin routes for adding /modifying/deleting users ,adding /modifying/deleting and verifying midwives, managing articles, viewing analytics,  Only accessible to admin users+ his settings
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, text
from app.database import get_db
from app.models.user import Notification, User
from app.models.content import Article
from app.dependencies import get_current_user_with_db,require_admin
from app.schemas import UserUpdate , MidWifeUpdate, ArticleUpdate

router = APIRouter(tags=["admin"])

#dashboard for admin to view analytics  
@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    #total users 
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    #total midwives
    total_midwives_result = await db.execute(select(func.count(User.id)).where(User.role == 'midwife'))
    total_midwives = total_midwives_result.scalar()
    
    #total articles
    total_articles_result = await db.execute(select(func.count(Article.id)))
    total_articles = total_articles_result.scalar()
    
    #new users this week
    new_users_this_week_result = await db.execute(
        select(func.count(User.id)).where(User.registration_date >= func.now() - text("INTERVAL '7 days'"))
    )
    new_users_this_week = new_users_this_week_result.scalar()
    
    #user growth (this is a simplified example, you may want to calculate growth based on specific time periods)
    user_growth_result = await db.execute(
        select(func.count(User.id)).where(User.registration_date >= func.now() - text("INTERVAL '30 days'"))
    )
    user_growth = user_growth_result.scalar()
    
    #article activity (published vs draft articles)
    published_articles_result = await db.execute(select(func.count(Article.id)).where(Article.status == 'published'))
    published_articles = published_articles_result.scalar()
    
    draft_articles_result = await db.execute(select(func.count(Article.id)).where(Article.status == 'draft'))
    draft_articles = draft_articles_result.scalar()
    
    article_activity = {
        "published": published_articles,
        "draft": draft_articles
    }
    
    #recent activities (recently registered users, recently published articles)
    recent_users_result = await db.execute(
        select(User).order_by(User.registration_date.desc()).limit(5)
    )
    recent_users = recent_users_result.scalars().all()
    
    recent_articles_result = await db.execute(
        select(Article).order_by(Article.publication_date.desc()).limit(5)
    )
    recent_articles = recent_articles_result.scalars().all()
    
    recent_activities = {
        "recent_users": recent_users,
        "recent_articles": recent_articles
    }

    return {
        "total_users": total_users,
        "total_midwives": total_midwives,
        "total_articles": total_articles,
        "new_users_this_week": new_users_this_week,
        "user_growth": user_growth,
        "article_activity": article_activity,
        "recent_activities": recent_activities
    }

#admin route to view all users with pagination and search functionality
@router.get("/users")
async def view_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 10,
    search: str = None
):
    query = select(User)
    
    if search:
        query = query.where(User.username.ilike(f"%{search}%"))
    
    total_users_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total_users = total_users_result.scalar()
    
    users_result = await db.execute(
        query.order_by(User.registration_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    users = users_result.scalars().all()
    
    return {
        "total_users": total_users,
        "page": page,
        "page_size": page_size,
        "users": users
    }

#admin route to manage users (add/modify/delete)
@router.post("/users")
async def create_user(
    user_data: UserUpdate,  # Pydantic schema for user creation
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role,
        is_active=user_data.is_active
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,  # Pydantic schema with optional fields
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # update only provided fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.add(user)
    await db.commit()
    return {"message": "User deactivated successfully"}


#midwife verification routes
@router.get("/midwives/pending")
async def view_pending_midwives(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.role == 'midwife', User.is_verified == False))
    pending_midwives = result.scalars().all()
    return pending_midwives

@router.post("/midwives/{midwife_id}/verify")
async def verify_midwife(
    midwife_id: int,
    verification_data: MidWifeUpdate,  # Pydantic schema with verification details
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == midwife_id, User.role == 'midwife'))
    midwife = result.scalar_one_or_none()
    if not midwife:
        raise HTTPException(status_code=404, detail="Midwife not found")

    midwife.is_verified = True
    db.add(midwife)
    await db.commit()
    await db.refresh(midwife)
    return midwife


async def reject_midwife(
    midwife_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == midwife_id, User.role == 'midwife'))
    midwife = result.scalar_one_or_none()
    if not midwife:
        raise HTTPException(status_code=404, detail="Midwife not found")

    midwife.is_verified = False
    db.add(midwife)
    await db.commit()
    return {"message": "Midwife application rejected successfully"}


#managing midwives 
@router.get("/midwives")
async def view_midwives(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 10,
    search: str = None
):
    query = select(User).where(User.role == 'midwife')
    
    if search:
        query = query.where(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    
    total_midwives_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total_midwives = total_midwives_result.scalar()
    
    midwives_result = await db.execute(
        query.order_by(User.registration_date.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    midwives = midwives_result.scalars().all()
    
    return {
        "total_midwives": total_midwives,
        "page": page,
        "page_size": page_size,
        "midwives": midwives
    }

@router.patch("/midwives/{midwife_id}")
async def update_midwife(
    midwife_id: int,
    midwife_data: MidWifeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == midwife_id, User.role == 'midwife'))
    midwife = result.scalar_one_or_none()
    if not midwife:
        raise HTTPException(status_code=404, detail="Midwife not found")

    
    for field, value in midwife_data.dict(exclude_unset=True).items():
        setattr(midwife, field, value)

    db.add(midwife)
    await db.commit()
    await db.refresh(midwife)
    return midwife

@router.delete("/midwives/{midwife_id}")
async def delete_midwife(
    midwife_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == midwife_id, User.role == 'midwife'))
    midwife = result.scalar_one_or_none()
    if not midwife:
        raise HTTPException(status_code=404, detail="Midwife not found")

    midwife.is_active = False
    db.add(midwife)
    await db.commit()
    return {"message": "Midwife deactivated successfully"}

#managing articles
@router.get("/articles")
async def view_articles(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 10,
    search: str = None
):
    query = select(Article)
    
    if search:
        query = query.where(Article.title.ilike(f"%{search}%") | Article.content.ilike(f"%{search}%")) | Article.category.ilike(f"%{search}%") | Article.author_id.in_(select(User.id).where(User.name.ilike(f"%{search}%")))
    
    total_articles_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total_articles = total_articles_result.scalar()
    
    articles_result = await db.execute(
        query.order_by(Article.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    articles = articles_result.scalars().all()
    
    return {
        "total_articles": total_articles,
        "page": page,
        "page_size": page_size,
        "articles": articles
    }

@router.patch("/articles/{article_id}")
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,  # Pydantic schema with optional fields for article update
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    
    for field, value in article_data.dict(exclude_unset=True).items():
        setattr(article, field, value)

    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article

@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.delete(article)
    await db.commit()
    return {"message": "Article deleted successfully"}

#the settings for the admin
@router.patch("/settings")
async def update_admin_profile(
    profile_data: UserUpdate,  # Pydantic schema with optional fields for admin profile update
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

#notifications for admin (new midwife applications, reported content, etc)
@router.get("/notifications")
async def view_notifications(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()))
    notifications = result.scalars().all()
    return notifications