/**
 * Tech Pulse Dashboard — News Dashboard JavaScript
 * Handles filtering, searching, and theme toggling
 */

document.addEventListener('DOMContentLoaded', () => {
  // Theme toggle
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
    
    themeToggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeButton(newTheme);
    });
  }
  
  function updateThemeButton(theme) {
    if (themeToggle) {
      themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
  }
  
  // News search
  const newsSearch = document.getElementById('news-search');
  if (newsSearch) {
    newsSearch.addEventListener('input', (e) => {
      filterNews(e.target.value.toLowerCase());
    });
  }
  
  function filterNews(query) {
    const newsItems = document.querySelectorAll('.news-item');
    newsItems.forEach(item => {
      const title = item.querySelector('.news-item-title')?.textContent.toLowerCase() || '';
      const meta = item.querySelector('.news-item-meta')?.textContent.toLowerCase() || '';
      const matches = title.includes(query) || meta.includes(query);
      item.style.display = matches ? '' : 'none';
    });
  }
  
  // Video search
  const videoSearch = document.getElementById('video-search');
  if (videoSearch) {
    videoSearch.addEventListener('input', (e) => {
      filterVideos(e.target.value.toLowerCase());
    });
  }
  
  function filterVideos(query) {
    const videoCards = document.querySelectorAll('.video-card');
    videoCards.forEach(card => {
      const title = card.querySelector('.video-card-title')?.textContent.toLowerCase() || '';
      const meta = card.querySelector('.video-card-meta')?.textContent.toLowerCase() || '';
      const matches = title.includes(query) || meta.includes(query);
      card.style.display = matches ? '' : 'none';
    });
  }
  
  // Channel filters (chips)
  const chipContainers = document.querySelectorAll('.chip-container');
  chipContainers.forEach(container => {
    const chips = container.querySelectorAll('.chip');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chip.classList.toggle('active');
        applyFilters();
      });
    });
  });
  
  function applyFilters() {
    // Get active news channel filters
    const newsChannelFilters = document.querySelectorAll('#news-channel-filters .chip.active');
    const activeNewsChannels = Array.from(newsChannelFilters).map(chip => chip.dataset.channel);
    
    // Get active video channel filters
    const videoChannelFilters = document.querySelectorAll('#video-channel-filters .chip.active');
    const activeVideoChannels = Array.from(videoChannelFilters).map(chip => chip.dataset.channel);
    
    // Filter news items
    const newsItems = document.querySelectorAll('.news-item');
    newsItems.forEach(item => {
      if (activeNewsChannels.length === 0) {
        item.style.display = '';
      } else {
        const channel = item.dataset.channel;
        item.style.display = activeNewsChannels.includes(channel) ? '' : 'none';
      }
    });
    
    // Filter video cards
    const videoCards = document.querySelectorAll('.video-card');
    videoCards.forEach(card => {
      if (activeVideoChannels.length === 0) {
        card.style.display = '';
      } else {
        const channel = card.dataset.channel;
        card.style.display = activeVideoChannels.includes(channel) ? '' : 'none';
      }
    });
  }
  
  // GitHub filter
  const githubFilter = document.getElementById('github-filter');
  if (githubFilter) {
    githubFilter.addEventListener('input', (e) => {
      filterGithub(e.target.value.toLowerCase());
    });
  }
  
  function filterGithub(query) {
    const githubItems = document.querySelectorAll('.github-item');
    githubItems.forEach(item => {
      const name = item.querySelector('.github-name')?.textContent.toLowerCase() || '';
      const desc = item.querySelector('.github-desc')?.textContent.toLowerCase() || '';
      const lang = item.dataset.lang?.toLowerCase() || '';
      const matches = name.includes(query) || desc.includes(query) || lang.includes(query);
      item.style.display = matches ? '' : 'none';
    });
  }
  
  // Multimedia tabs
  const multimediaTabs = document.querySelectorAll('#multimedia-tabs .chip');
  multimediaTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      multimediaTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      const tabType = tab.dataset.tab;
      const videoCards = document.querySelectorAll('.video-card');
      
      videoCards.forEach(card => {
        if (tabType === 'all') {
          card.style.display = '';
        } else {
          const type = card.dataset.type;
          card.style.display = type === tabType ? '' : 'none';
        }
      });
    });
  });
  
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
  
  // Lazy loading for images
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          imageObserver.unobserve(img);
        }
      });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }
});
