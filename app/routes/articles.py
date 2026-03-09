from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.content import Article
from app.database import get_db
from app.schemas.content import ArticleCreate, ArticleResponse
from app.dependencies import get_current_user

router = APIRouter( tags=["Articles"])



@router.get("/")
async def get_articles(
    search: str = None,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Article)
    
    if search:
        query = query.where(Article.title.ilike(f"%{search}%"))
    
    if category:
        query = query.where(Article.category == category)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return articles

@router.get("/{article_id}")
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article

@router.post("/", response_model=ArticleResponse)
async def create_article(
    article: ArticleCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if user has permission to create articles
    if current_user.get("role") not in ["admin", "midwife"]:
        raise HTTPException(status_code=403, detail="Only admins and midwives can create articles")
    
    new_article = Article(
        title=article.title,
        content=article.content,
        category=article.category,
        author_id=int(current_user.get("sub"))
    )
    
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    
    return new_article

