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
            {newsArticles.map((article, index) => (
              <article key={index} className="news-modal-article">
                <h3 className="news-modal-article-title">{article.title}</h3>
                <div className="news-modal-article-content">
                  {article.paragraphs.map((paragraph, pIndex) => (
                    <p key={pIndex} className="news-modal-paragraph">
                      {paragraph}
                    </p>
                  ))}
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
