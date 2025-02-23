import React, { useMemo } from 'react';
import useStore from '../store/useStore';

const NewsPreview = () => {
  const { newsArticles, setIsNewsModalOpen } = useStore();

  const randomArticles = useMemo(() => {
    if (!newsArticles?.length) return [];
    
    // Get up to 3 random articles
    const shuffled = [...newsArticles].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, 3);
  }, [newsArticles]);

  if (!randomArticles.length) {
    return <div className="news-preview-empty">No news articles available</div>;
  }

  return (
    <div className="news-preview" onClick={() => setIsNewsModalOpen(true)}>
      {randomArticles.map((article, index) => (
        <div key={index} className="news-article">
          <div className="news-article-image">
            {article.image ? (
              <img 
                src={article.image} 
                alt={article.title || 'News article'} 
                onError={(e) => {
                  e.target.src = 'https://placehold.co/600x400?text=News';
                }}
              />
            ) : (
              <div className="news-article-image-placeholder">
                News
              </div>
            )}
          </div>
          <div className="news-article-content">
            <h3 className="news-title">
              {article.title || 'News Article'}
            </h3>
            <p className="news-description">
              {article.description 
                ? (article.description.length > 100 
                    ? `${article.description.substring(0, 100)}...` 
                    : article.description)
                : 'No description available'}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NewsPreview;
