// Gold Digger Web Application JavaScript

class GoldDiggerApp {
  constructor() {
    this.currentTab = "dashboard";
    this.refreshInterval = null;
    this.chartInterval = "15m";
    this.priceChart = null;

    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadInitialData();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    // Tab switching
    document.querySelectorAll(".tab-button").forEach((button) => {
      button.addEventListener("click", (e) => {
        const tabName = e.target.dataset.tab;
        this.switchTab(tabName);
      });
    });

    // Header actions
    document.getElementById("refresh-all")?.addEventListener("click", () => {
      this.refreshAll();
    });

    // Chart interval selector
    document
      .getElementById("chart-interval")
      ?.addEventListener("change", (e) => {
        this.chartInterval = e.target.value;
        this.loadPriceChart();
      });

    // Price controls
    document.getElementById("fetch-prices")?.addEventListener("click", () => {
      this.loadPriceTable();
    });

    document
      .getElementById("price-interval")
      ?.addEventListener("change", () => {
        this.loadPriceTable();
      });

    // News controls
    document.getElementById("fetch-news")?.addEventListener("click", () => {
      this.fetchFreshNews();
    });

    document.getElementById("load-news")?.addEventListener("click", () => {
      this.loadNews();
    });

    // Analysis controls
    document
      .getElementById("run-complete-analysis")
      ?.addEventListener("click", () => {
        this.runCompleteAnalysis();
      });

    document
      .getElementById("analyze-sentiment")
      ?.addEventListener("click", () => {
        this.analyzeSentiment();
      });

    document
      .getElementById("trading-analysis")
      ?.addEventListener("click", () => {
        this.runTradingAnalysis();
      });

    document.getElementById("refresh-ai")?.addEventListener("click", () => {
      this.loadAISummary();
    });

    document
      .getElementById("refresh-sentiment")
      ?.addEventListener("click", () => {
        this.loadSentiment();
      });
  }

  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll(".tab-button").forEach((button) => {
      button.classList.remove("active");
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add("active");

    // Update tab content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active");
    });
    document.getElementById(`${tabName}-tab`).classList.add("active");

    this.currentTab = tabName;

    // Load tab-specific data
    switch (tabName) {
      case "prices":
        this.loadPriceTable();
        break;
      case "news":
        this.loadNews();
        break;
      case "analysis":
        // Analysis tab loads on demand
        break;
    }
  }

  async loadInitialData() {
    this.showLoading();

    try {
      await Promise.all([
        this.loadSystemStatus(),
        this.loadCurrentPrice(),
        this.loadPriceChart(),
        this.loadRecentHeadlines(),
      ]);
    } catch (error) {
      this.showToast("Error loading initial data", "error");
      console.error("Error loading initial data:", error);
    } finally {
      this.hideLoading();
    }

    // Initialize AI summary placeholder
    this.initializeAISummary();

    // Initialize sentiment placeholder
    this.initializeSentimentDisplay();
  }

  async loadSystemStatus() {
    try {
      console.log("Loading system status...");
      const response = await fetch("/api/status");
      const data = await response.json();

      const statusElement = document.getElementById("system-status");
      const statusText =
        data.status.charAt(0).toUpperCase() + data.status.slice(1);

      statusElement.innerHTML = `<i class="fas fa-circle"></i> ${statusText}`;
      statusElement.className = `stat-value status-indicator ${data.status}`;
    } catch (error) {
      console.error("Error loading system status:", error);
      const statusElement = document.getElementById("system-status");
      statusElement.innerHTML = '<i class="fas fa-circle"></i> Error';
      statusElement.className = "stat-value status-indicator error";
    }
  }

  async loadCurrentPrice() {
    try {
      console.log("Loading current price (fast endpoint)...");
      const response = await fetch("/api/current-price");
      const data = await response.json();

      if (data.current_price) {
        document.getElementById("current-price").textContent =
          `$${data.current_price.toFixed(2)}`;

        const changeElement = document.getElementById("price-change");
        const change = data.price_change || 0;
        const changePct = data.price_change_percent || 0;

        changeElement.textContent = `${change >= 0 ? "+" : ""}${change.toFixed(2)} (${changePct.toFixed(2)}%)`;
        changeElement.className = `stat-value ${change >= 0 ? "text-success" : "text-danger"}`;
      }
    } catch (error) {
      console.error("Error loading current price:", error);
      document.getElementById("current-price").textContent = "Error";
      document.getElementById("price-change").textContent = "Error";
    }
  }

  async loadPriceChart() {
    const chartContainer = document.getElementById("price-chart");
    if (!chartContainer) return;

    try {
      console.log(`Loading price chart (${this.chartInterval})...`);
      chartContainer.innerHTML = '<div class="loading">Loading chart...</div>';

      const response = await fetch(`/api/prices/chart/${this.chartInterval}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const chartData = await response.json();

      // Clear loading message
      chartContainer.innerHTML = "";

      // Plot the chart
      Plotly.newPlot("price-chart", chartData.data, chartData.layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ["pan2d", "lasso2d", "select2d"],
        displaylogo: false,
      });
    } catch (error) {
      console.error("Error loading price chart:", error);
      chartContainer.innerHTML =
        '<div class="placeholder-text">Error loading chart</div>';
    }
  }

  async loadPriceTable() {
    const interval = document.getElementById("price-interval")?.value || "15m";
    const tableBody = document.querySelector("#price-table tbody");

    if (!tableBody) return;

    try {
      tableBody.innerHTML =
        '<tr><td colspan="6" class="loading-cell">Loading price data...</td></tr>';

      const response = await fetch(`/api/prices/${interval}`);
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Clear table
      tableBody.innerHTML = "";

      // Populate table
      const maxRows = 50; // Limit to recent 50 entries
      const rowCount = Math.min(data.dates.length, maxRows);

      for (let i = rowCount - 1; i >= 0; i--) {
        const row = document.createElement("tr");
        row.innerHTML = `
                    <td>${new Date(data.dates[i]).toLocaleString()}</td>
                    <td>$${data.open[i].toFixed(2)}</td>
                    <td>$${data.high[i].toFixed(2)}</td>
                    <td>$${data.low[i].toFixed(2)}</td>
                    <td>$${data.close[i].toFixed(2)}</td>
                    <td>${data.volume[i].toLocaleString()}</td>
                `;
        tableBody.appendChild(row);
      }
    } catch (error) {
      console.error("Error loading price table:", error);
      tableBody.innerHTML =
        '<tr><td colspan="6" class="loading-cell">Error loading price data</td></tr>';
    }
  }

  async loadNews() {
    const limit = document.getElementById("news-limit")?.value || 20;
    const category = document.getElementById("news-category")?.value || "";
    const container = document.getElementById("news-articles");

    if (!container) return;

    try {
      container.innerHTML =
        '<div class="loading">Loading news articles...</div>';

      let url = `/api/news?limit=${limit}`;
      if (category) {
        url += `&category=${encodeURIComponent(category)}`;
      }

      const response = await fetch(url);
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      container.innerHTML = "";

      if (data.articles.length === 0) {
        container.innerHTML =
          '<div class="placeholder-text">No news articles found</div>';
        return;
      }

      data.articles.forEach((article) => {
        const articleElement = document.createElement("div");
        articleElement.className = "news-article";

        const sentimentClass = this.getSentimentClass(article.sentiment_score);
        const publishedDate = new Date(article.published_date).toLocaleString();

        articleElement.innerHTML = `
                    <div class="news-meta">
                        <span class="news-publisher">${article.publisher || "Unknown"}</span>
                        <span class="news-date">${publishedDate}</span>
                        ${
                          article.sentiment_score !== null
                            ? `<span class="news-sentiment ${sentimentClass}">${sentimentClass}</span>`
                            : ""
                        }
                    </div>
                    <div class="news-title">${article.title}</div>
                    ${article.summary ? `<div class="news-summary">${article.summary}</div>` : ""}
                    ${article.link ? `<a href="${article.link}" target="_blank" class="btn btn-sm mt-2">Read More</a>` : ""}
                `;

        container.appendChild(articleElement);
      });
    } catch (error) {
      console.error("Error loading news:", error);
      container.innerHTML =
        '<div class="placeholder-text">Error loading news articles</div>';
    }
  }

  async loadRecentHeadlines() {
    const container = document.getElementById("recent-headlines");
    if (!container) return;

    try {
      console.log("Loading recent headlines...");
      const response = await fetch("/api/news?limit=5");
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      container.innerHTML = "";

      if (data.articles.length === 0) {
        container.innerHTML =
          '<div class="placeholder-text">No recent headlines</div>';
        return;
      }

      data.articles.forEach((article) => {
        const item = document.createElement("div");
        item.className = "news-item";

        const sentimentClass = this.getSentimentClass(article.sentiment_score);

        item.innerHTML = `
                    <div class="news-title">${article.title}</div>
                    <div class="news-meta">
                        <span>${article.publisher || "Unknown"}</span>
                        ${
                          article.sentiment_score !== null
                            ? `<span class="news-sentiment ${sentimentClass}">${sentimentClass}</span>`
                            : ""
                        }
                    </div>
                `;

        container.appendChild(item);
      });
    } catch (error) {
      console.error("Error loading recent headlines:", error);
      container.innerHTML =
        '<div class="placeholder-text">Error loading headlines</div>';
    }
  }

  async loadSentiment() {
    try {
      console.log("Loading sentiment analysis (AI endpoint)...");
      const response = await fetch("/api/news/analyze");
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Update sentiment label
      const labelElement = document.getElementById("sentiment-label");
      if (labelElement) {
        labelElement.textContent = data.sentiment_label || "Unknown";
        labelElement.className = `sentiment-label text-${this.getSentimentClass(data.overall_sentiment)}`;
      }

      // Update sentiment meter
      const needleElement = document.querySelector(".sentiment-needle");
      if (needleElement) {
        // Convert sentiment score (-1 to 1) to rotation angle (-90 to 90 degrees)
        const angle = (data.overall_sentiment || 0) * 90;
        needleElement.style.transform = `rotate(${angle}deg)`;
      }

      // Update sentiment stats
      if (data.sentiment_distribution) {
        const dist = data.sentiment_distribution;
        document.getElementById("positive-count").textContent =
          dist.positive || 0;
        document.getElementById("neutral-count").textContent =
          dist.neutral || 0;
        document.getElementById("negative-count").textContent =
          dist.negative || 0;
      }
    } catch (error) {
      console.error("Error loading sentiment:", error);
      document.getElementById("sentiment-label").textContent = "Error";
    }
  }

  async loadAISummary() {
    const container = document.getElementById("ai-summary");
    if (!container) return;

    try {
      console.log("Loading AI summary (AI endpoint)...");
      container.innerHTML =
        '<div class="loading">Generating AI summary...</div>';

      const response = await fetch("/api/complete-analysis");
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      const analysisDate = new Date(data.timestamp).toLocaleString();
      container.innerHTML = `
                <div class="ai-summary-content">
                    ${data.ai_summary || "AI summary not available"}
                </div>
                <div class="ai-summary-meta">
                    <small class="text-muted">
                      <i class="fas fa-clock"></i> Generated: ${analysisDate}
                      <br>
                      <i class="fas fa-sync-alt"></i> Fresh analysis completed
                    </small>
                </div>
            `;
    } catch (error) {
      console.error("Error loading AI summary:", error);
      container.innerHTML =
        '<div class="placeholder-text">Error generating AI summary</div>';
    }
  }

  async initializeAISummary() {
    const container = document.getElementById("ai-summary");
    if (!container) return;

    // Check if there's a cached AI analysis first
    try {
      const response = await fetch("/api/latest-ai-analysis");
      const data = await response.json();

      if (data.has_cached_analysis) {
        // Show cached analysis
        const analysisDate = new Date(data.timestamp).toLocaleString();
        container.innerHTML = `
          <div class="ai-summary-cached">
            <div class="ai-summary-content">
              ${data.recommendation || "No recommendation available"}
            </div>
            <div class="ai-summary-meta">
              <small class="text-muted">
                <i class="fas fa-clock"></i> Cached analysis from: ${analysisDate}
                <br>
                <i class="fas fa-info-circle"></i> Price at analysis: $${data.current_price?.toFixed(2) || "N/A"}
              </small>
            </div>
          </div>
        `;
      } else {
        // Show placeholder for new analysis
        this.showAISummaryPlaceholder(container);
      }
    } catch (error) {
      console.error("Error loading cached AI analysis:", error);
      this.showAISummaryPlaceholder(container);
    }
  }

  showAISummaryPlaceholder(container) {
    container.innerHTML = `
            <div class="ai-summary-placeholder">
                <div class="placeholder-text">
                    <i class="fas fa-robot"></i>
                    <p>No cached AI analysis available</p>
                    <button id="load-ai-summary" class="btn btn-primary">
                        <i class="fas fa-brain"></i> Generate New AI Summary
                    </button>
                </div>
            </div>
        `;

    // Add click handler for the button
    document
      .getElementById("load-ai-summary")
      ?.addEventListener("click", () => {
        this.loadAISummary();
      });
  }

  initializeSentimentDisplay() {
    const labelElement = document.getElementById("sentiment-label");
    if (labelElement) {
      labelElement.innerHTML = `
        <span style="cursor: pointer; color: var(--primary-color);" onclick="window.goldDiggerApp.loadSentiment()">
          <i class="fas fa-play-circle"></i> Click to analyze sentiment
        </span>
      `;
    }

    const positiveElement = document.getElementById("positive-count");
    const neutralElement = document.getElementById("neutral-count");
    const negativeElement = document.getElementById("negative-count");

    if (positiveElement) positiveElement.textContent = "-";
    if (neutralElement) neutralElement.textContent = "-";
    if (negativeElement) negativeElement.textContent = "-";
  }

  async fetchFreshNews() {
    try {
      this.showToast("Fetching fresh news...", "info");

      const response = await fetch("/api/news/fetch");
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      this.showToast(
        `Fetched ${data.articles_fetched || 0} new articles`,
        "success",
      );

      // Refresh news displays
      if (this.currentTab === "news") {
        this.loadNews();
      }
      this.loadRecentHeadlines();
    } catch (error) {
      console.error("Error fetching fresh news:", error);
      this.showToast("Error fetching news", "error");
    }
  }

  async runCompleteAnalysis() {
    const resultsContainer = document.getElementById("analysis-results");
    if (!resultsContainer) return;

    try {
      this.showLoading("Running complete analysis...");

      const response = await fetch("/api/complete-analysis");
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Display results
      resultsContainer.innerHTML = `
                <div class="analysis-section">
                    <h4><i class="fas fa-coins"></i> Price Analysis</h4>
                    <p><strong>Current Price:</strong> $${data.current_price?.toFixed(2) || "N/A"}</p>
                    ${data.trading_analysis ? this.formatTradingAnalysis(data.trading_analysis) : ""}
                </div>

                <div class="analysis-section">
                    <h4><i class="fas fa-heart-pulse"></i> Sentiment Analysis</h4>
                    <p><strong>Overall Sentiment:</strong> ${data.sentiment?.score?.toFixed(3) || "N/A"}</p>
                    <p><strong>Articles Analyzed:</strong> ${data.sentiment?.articles_analyzed || 0}</p>
                </div>

                <div class="analysis-section">
                    <h4><i class="fas fa-robot"></i> AI Summary</h4>
                    <div class="ai-summary-content">
                        ${data.ai_summary || "No summary available"}
                    </div>
                </div>

                <div class="analysis-section">
                    <h4><i class="fas fa-newspaper"></i> Recent News</h4>
                    <div class="recent-news-list">
                        ${
                          data.recent_news
                            ?.map(
                              (article) => `
                            <div class="news-item">
                                <div class="news-title">${article.title}</div>
                                <div class="news-meta">
                                    <span>${article.publisher || "Unknown"}</span>
                                    <span>${new Date(article.published_date).toLocaleDateString()}</span>
                                </div>
                            </div>
                        `,
                            )
                            .join("") || "No recent news"
                        }
                    </div>
                </div>

                <div class="analysis-section">
                    <h4><i class="fas fa-clock"></i> Analysis Details</h4>
                    <p><strong>Generated:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                </div>
            `;
    } catch (error) {
      console.error("Error running complete analysis:", error);
      resultsContainer.innerHTML =
        '<div class="placeholder-text">Error running analysis</div>';
    } finally {
      this.hideLoading();
    }
  }

  async analyzeSentiment() {
    const resultsContainer = document.getElementById("analysis-results");
    if (!resultsContainer) return;

    try {
      this.showLoading("Analyzing sentiment...");

      const response = await fetch("/api/news/analyze");
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      resultsContainer.innerHTML = `
                <div class="analysis-section">
                    <h4><i class="fas fa-heart-pulse"></i> Sentiment Analysis Results</h4>
                    <p><strong>Overall Sentiment:</strong> ${data.sentiment_label} (${data.overall_sentiment?.toFixed(3)})</p>
                    <p><strong>Articles Analyzed:</strong> ${data.articles_analyzed}</p>

                    <div class="sentiment-breakdown">
                        <h5>Sentiment Distribution:</h5>
                        <ul>
                            <li class="text-success">Positive: ${data.sentiment_distribution?.positive || 0} articles</li>
                            <li class="text-muted">Neutral: ${data.sentiment_distribution?.neutral || 0} articles</li>
                            <li class="text-danger">Negative: ${data.sentiment_distribution?.negative || 0} articles</li>
                        </ul>
                    </div>

                    <div class="keywords-section">
                        <h5>Top Keywords:</h5>
                        <div class="keywords-list">
                            ${
                              data.top_keywords
                                ?.map(
                                  (kw) => `
                                <span class="keyword-tag">${kw.keyword} (${kw.count})</span>
                            `,
                                )
                                .join("") || "No keywords available"
                            }
                        </div>
                    </div>
                </div>
            `;
    } catch (error) {
      console.error("Error analyzing sentiment:", error);
      resultsContainer.innerHTML =
        '<div class="placeholder-text">Error analyzing sentiment</div>';
    } finally {
      this.hideLoading();
    }
  }

  async runTradingAnalysis() {
    const resultsContainer = document.getElementById("analysis-results");
    if (!resultsContainer) return;

    try {
      this.showLoading("Running trading analysis...");

      const response = await fetch("/api/trading/analyze");
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      resultsContainer.innerHTML = `
                <div class="analysis-section">
                    <h4><i class="fas fa-chart-line"></i> Trading Analysis Results</h4>
                    <p><strong>Current Price:</strong> $${data.current_price?.toFixed(2) || "N/A"}</p>
                    <p><strong>Price Change:</strong>
                        <span class="${data.price_change >= 0 ? "text-success" : "text-danger"}">
                            ${data.price_change >= 0 ? "+" : ""}${data.price_change?.toFixed(2) || "N/A"}
                            (${data.price_change_percent?.toFixed(2) || "N/A"}%)
                        </span>
                    </p>

                    ${data.analysis ? this.formatTradingAnalysis(data.analysis) : ""}

                    <div class="timestamp">
                        <p><strong>Analysis Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                    </div>
                </div>
            `;
    } catch (error) {
      console.error("Error running trading analysis:", error);
      resultsContainer.innerHTML =
        '<div class="placeholder-text">Error running trading analysis</div>';
    } finally {
      this.hideLoading();
    }
  }

  formatTradingAnalysis(analysis) {
    if (!analysis || typeof analysis !== "object") {
      return "<p>No detailed analysis available</p>";
    }

    let html = '<div class="trading-analysis-details">';

    // Handle different analysis formats
    for (const [key, value] of Object.entries(analysis)) {
      if (value !== null && value !== undefined) {
        const formattedKey = key
          .replace(/_/g, " ")
          .replace(/\b\w/g, (l) => l.toUpperCase());
        html += `<p><strong>${formattedKey}:</strong> ${value}</p>`;
      }
    }

    html += "</div>";
    return html;
  }

  refreshAll() {
    this.showToast("Refreshing all data...", "info");
    this.loadInitialData();
  }

  startAutoRefresh() {
    // Refresh data every 5 minutes
    this.refreshInterval = setInterval(
      () => {
        this.loadSystemStatus();
        this.loadCurrentPrice();
        if (this.currentTab === "dashboard") {
          this.loadRecentHeadlines();
        }
        // Note: Sentiment analysis is NOT auto-refreshed - only on user request
      },
      5 * 60 * 1000,
    );
  }

  getSentimentClass(score) {
    if (score === null || score === undefined) return "neutral";
    if (score > 0.1) return "positive";
    if (score < -0.1) return "negative";
    return "neutral";
  }

  showLoading(message = "Loading...") {
    const overlay = document.getElementById("loading-overlay");
    const text = overlay.querySelector(".loading-text");
    if (text) text.textContent = message;
    overlay.classList.remove("hidden");
  }

  hideLoading() {
    document.getElementById("loading-overlay").classList.add("hidden");
  }

  showToast(message, type = "info", duration = 5000) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    const toastId = Date.now().toString();
    toast.innerHTML = `
            <div class="toast-header">
                <span class="toast-title">${this.getToastTitle(type)}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="toast-body">${message}</div>
        `;

    container.appendChild(toast);

    // Trigger show animation
    setTimeout(() => toast.classList.add("show"), 100);

    // Auto remove
    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  getToastTitle(type) {
    const titles = {
      success: "Success",
      error: "Error",
      warning: "Warning",
      info: "Info",
    };
    return titles[type] || "Notification";
  }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.goldDiggerApp = new GoldDiggerApp();
});

// Handle page visibility change to pause/resume updates
document.addEventListener("visibilitychange", () => {
  if (document.hidden && window.goldDiggerApp) {
    // Page is hidden, could pause updates
    console.log("Page hidden, continuing background updates");
  } else if (window.goldDiggerApp) {
    // Page is visible, refresh data
    console.log("Page visible, refreshing data");
    window.goldDiggerApp.loadSystemStatus();
    window.goldDiggerApp.loadCurrentPrice();
  }
});

// Add some additional CSS for the keyword tags
const additionalStyles = `
<style>
.keywords-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.keyword-tag {
    background: var(--bg-secondary);
    color: var(--text-primary);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    border: 1px solid var(--border-color);
}

.sentiment-breakdown ul {
    list-style: none;
    padding: 0;
}

.sentiment-breakdown li {
    padding: 0.25rem 0;
    font-weight: 500;
}

.trading-analysis-details p {
    margin-bottom: 0.5rem;
}

.recent-news-list {
    max-height: 300px;
    overflow-y: auto;
}
</style>
`;

// Inject additional styles
document.head.insertAdjacentHTML("beforeend", additionalStyles);
