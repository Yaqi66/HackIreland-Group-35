import React, { useEffect, useState } from 'react';
import useStore from '../store/useStore';
import '../styles/NewsModal.css';

const NewsModal = () => {
  const { newsArticles, isNewsModalOpen, setIsNewsModalOpen } = useStore();
  const [shouldRender, setShouldRender] = useState(false);

  useEffect(() => {
    if (isNewsModalOpen) {
      setShouldRender(true);
    } else {
      const timer = setTimeout(() => setShouldRender(false), 300); // match animation duration
      return () => clearTimeout(timer);
    }
  }, [isNewsModalOpen]);

  if (!shouldRender) return null;

  return (
    <div 
      className={`modal-overlay ${isNewsModalOpen ? 'modal-show' : 'modal-hide'}`}
      onClick={() => setIsNewsModalOpen(false)}
    >
      <div 
        className={`modal-content ${isNewsModalOpen ? 'modal-show' : 'modal-hide'}`}
        onClick={(e) => e.stopPropagation()}
      >
        <button 
          className="modal-close"
          onClick={() => setIsNewsModalOpen(false)}
        >
          ×
        </button>
        <div className="news-modal-container">
          <h2 className="news-modal-title">Latest News</h2>
          <div className="news-articles-list">
            {newsArticles?.map((article, index) => (
              <article key={index} className="news-modal-article">
                <div className="news-modal-article-image">
                  {article.image ? (
                    <img 
                      src={article.image} 
                      alt={article.title || 'News article'} 
                      onError={(e) => {
                        e.target.src = 'https://placehold.co/600x400?text=News';
                      }}
                    />
                  ) : (
                    <div className="news-modal-article-image-placeholder">
                      News
                    </div>
                  )}
                </div>
                <div className="news-modal-article-content">
                  <h3 className="news-modal-article-title">
                    {article.link ? (
                      <a href={article.link} target="_blank" rel="noopener noreferrer">
                        {article.title || 'News Article'}
                      </a>
                    ) : (
                      article.title || 'News Article'
                    )}
                  </h3>
                  <p className="news-modal-article-description">
                    {article.description || 'No description available'}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsModal;
