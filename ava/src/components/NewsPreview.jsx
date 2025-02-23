import React, { useMemo } from 'react';
import useStore from '../store/useStore';

const NewsPreview = () => {
  const { newsArticles, setIsNewsModalOpen } = useStore();

  const randomArticles = useMemo(() => {
    if (!newsArticles.length) return [];
    
    // Get 3 random articles
    const shuffled = [...newsArticles].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, 3);
  }, [newsArticles]);

  if (!randomArticles.length) {
    return <div className="news-preview-empty">Loading news...</div>;
  }

  return (
    <div className="news-preview" onClick={() => setIsNewsModalOpen(true)}>
      {randomArticles.map((article, index) => (
        <div key={index} className="news-article">
          <h3 className="news-title">{article.title}</h3>
          <p className="news-paragraph">
            {article.paragraphs[0]?.substring(0, 100)}
            {article.paragraphs[0]?.length > 100 ? '...' : ''}
          </p>
        </div>
      ))}
    </div>
  );
};

export default NewsPreview;
