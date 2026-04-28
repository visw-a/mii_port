const CONFIG = {
  dataUrl: "./portfolio-data.json",
  refreshMs: 30_000,
};

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percent = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 2,
  signDisplay: "always",
});

const fixed2 = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
});

const elements = {
  headlineStats: document.getElementById("headlineStats"),
  holdingsTable: document.getElementById("holdingsTable"),
  sectorBreakdown: document.getElementById("sectorBreakdown"),
  riskMetrics: document.getElementById("riskMetrics"),
  updateFeed: document.getElementById("updateFeed"),
  lastUpdatedLabel: document.getElementById("lastUpdatedLabel"),
  refreshButton: document.getElementById("refreshButton"),
  statCardTemplate: document.getElementById("statCardTemplate"),
};

function numberClass(value) {
  return value >= 0 ? "positive" : "negative";
}

function calculateMetrics(holdings) {
  const rows = holdings.map((holding) => {
    const marketValue = holding.shares * holding.price;
    const costValue = holding.shares * holding.costBasis;
    const pnl = marketValue - costValue;
    const dayDollarMove = marketValue * holding.dayChangePct;

    return {
      ...holding,
      marketValue,
      costValue,
      pnl,
      dayDollarMove,
    };
  });

  const totalMarketValue = rows.reduce((sum, row) => sum + row.marketValue, 0);
  const totalCost = rows.reduce((sum, row) => sum + row.costValue, 0);
  const totalPnl = totalMarketValue - totalCost;
  const totalDayMove = rows.reduce((sum, row) => sum + row.dayDollarMove, 0);
  const weightedBeta = rows.reduce(
    (sum, row) => sum + (row.marketValue / totalMarketValue) * row.beta,
    0,
  );
  const weightedDayPct = totalDayMove / totalMarketValue;

  return {
    rows: rows.map((row) => ({
      ...row,
      weight: row.marketValue / totalMarketValue,
    })),
    totals: {
      totalMarketValue,
      totalCost,
      totalPnl,
      totalPnlPct: totalPnl / totalCost,
      totalDayMove,
      weightedDayPct,
      weightedBeta,
    },
  };
}

function groupedBySector(rows) {
  const sectors = new Map();
  rows.forEach((row) => {
    const current = sectors.get(row.sector) ?? 0;
    sectors.set(row.sector, current + row.marketValue);
  });
  return sectors;
}

function renderStats(totals) {
  elements.headlineStats.innerHTML = "";
  const cards = [
    ["Total Market Value", currency.format(totals.totalMarketValue), totals.totalDayMove],
    ["Total P/L", currency.format(totals.totalPnl), totals.totalPnl],
    ["P/L %", percent.format(totals.totalPnlPct), totals.totalPnlPct],
    ["Today", `${currency.format(totals.totalDayMove)} (${percent.format(totals.weightedDayPct)})`, totals.totalDayMove],
  ];

  cards.forEach(([label, value, sign]) => {
    const card = elements.statCardTemplate.content.cloneNode(true);
    card.querySelector(".stat-label").textContent = label;
    const statValue = card.querySelector(".stat-value");
    statValue.textContent = value;
    statValue.classList.add(numberClass(Number(sign)));
    elements.headlineStats.append(card);
  });
}

function renderHoldings(rows) {
  elements.holdingsTable.innerHTML = rows
    .sort((a, b) => b.marketValue - a.marketValue)
    .map(
      (row) => `
      <tr>
        <td>${row.ticker}</td>
        <td>${row.name}</td>
        <td>${fixed2.format(row.shares)}</td>
        <td>${currency.format(row.price)}</td>
        <td>${currency.format(row.marketValue)}</td>
        <td class="${numberClass(row.dayChangePct)}">${percent.format(row.dayChangePct)}</td>
        <td>${percent.format(row.weight)}</td>
      </tr>
    `,
    )
    .join("");
}

function renderSectorBreakdown(rows) {
  const sectors = groupedBySector(rows);
  const grandTotal = rows.reduce((sum, row) => sum + row.marketValue, 0);
  elements.sectorBreakdown.innerHTML = [...sectors.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(
      ([sector, value]) => `
      <li>
        <span>${sector}</span>
        <span>${currency.format(value)} (${percent.format(value / grandTotal)})</span>
      </li>
    `,
    )
    .join("");
}

function renderRiskMetrics(totals, rows) {
  const topWinner = [...rows].sort((a, b) => b.dayChangePct - a.dayChangePct)[0];
  const topLoser = [...rows].sort((a, b) => a.dayChangePct - b.dayChangePct)[0];

  const items = [
    ["Portfolio Beta", fixed2.format(totals.weightedBeta)],
    ["Daily Dollar Move", currency.format(totals.totalDayMove)],
    ["Best Position", `${topWinner.ticker} (${percent.format(topWinner.dayChangePct)})`],
    ["Worst Position", `${topLoser.ticker} (${percent.format(topLoser.dayChangePct)})`],
  ];

  elements.riskMetrics.innerHTML = items
    .map(
      ([label, value]) => `
      <li>
        <span>${label}</span>
        <strong>${value}</strong>
      </li>
    `,
    )
    .join("");
}

function renderUpdateFeed(feed) {
  elements.updateFeed.innerHTML = feed
    .map(
      (entry) => `
      <li>
        <span>${entry.date}</span>
        <span>${entry.note}</span>
      </li>
    `,
    )
    .join("");
}

async function loadDashboard() {
  const response = await fetch(CONFIG.dataUrl, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch portfolio data: ${response.status}`);
  }

  const payload = await response.json();
  const { rows, totals } = calculateMetrics(payload.holdings);

  renderStats(totals);
  renderHoldings(rows);
  renderSectorBreakdown(rows);
  renderRiskMetrics(totals, rows);
  renderUpdateFeed(payload.updates);

  const now = new Date();
  elements.lastUpdatedLabel.textContent = `Last update: ${now.toLocaleString()}`;
}

async function safeRefresh() {
  try {
    await loadDashboard();
  } catch (error) {
    elements.lastUpdatedLabel.textContent = `Last update failed: ${error.message}`;
  }
}

elements.refreshButton.addEventListener("click", safeRefresh);
safeRefresh();
setInterval(safeRefresh, CONFIG.refreshMs);
