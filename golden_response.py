import http.server
import socketserver
import urllib.parse
import urllib.request
import json
import re
import sys
from datetime import datetime, timezone
import random

# Default Port (will auto-fallback if busy)
DEFAULT_PORT = 8080

# Mock data base prices
BASE_PRICES = {
    "AAPL": 175.50,
    "GOOGL": 140.25,
    "MSFT": 378.90,
    "AMZN": 178.35,
    "TSLA": 245.80,
    "META": 505.20,
    "NVDA": 890.15,
    "GC=F": 2350.00,
    "CL=F": 78.50
}

# Ticker regex matching the main application validation rules
TICKER_REGEX = re.compile(r"^[A-Za-z0-9=.-]{1,12}$")

def sanitize_ticker(ticker):
    return ticker.strip().upper()

def validate_date(date_str):
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        if dt_utc.date() > now_utc.date():
            raise ValueError("Future dates are not allowed")
        return dt
    except ValueError as e:
        if "Future" in str(e):
            raise e
        raise ValueError("Date must be in YYYY-MM-DD format")

def get_mock_live(ticker):
    base_price = BASE_PRICES.get(ticker, 100.0)
    current_price = base_price + (random.random() - 0.5) * (base_price * 0.02)
    change = current_price - base_price
    change_pct = (change / base_price) * 100
    
    return {
        "ticker": ticker,
        "companyName": f"{ticker} Corporation (Mock Data)",
        "currentPrice": round(current_price, 2),
        "open": round(base_price + (random.random() - 0.5) * (base_price * 0.01), 2),
        "high": round(max(current_price, base_price) + (random.random() * (base_price * 0.01)), 2),
        "low": round(min(current_price, base_price) - (random.random() * (base_price * 0.01)), 2),
        "previousClose": round(base_price, 2),
        "volume": int(1000000 + random.random() * 500000),
        "currency": "INR" if ticker.endswith(".NS") else "USD",
        "marketState": "REGULAR",
        "timestamp": int(datetime.now().timestamp())
    }

def get_mock_history(ticker, date_str, dt):
    # Saturday (5) or Sunday (6) check
    if dt.weekday() >= 5:
        return None  # Market Closed
        
    base_price = BASE_PRICES.get(ticker, 100.0)
    return {
        "ticker": ticker,
        "date": date_str,
        "open": round(base_price * 0.99, 2),
        "high": round(base_price * 1.01, 2),
        "low": round(base_price * 0.98, 2),
        "close": round(base_price, 2),
        "adjustedClose": round(base_price, 2),
        "volume": 1000000
    }

def fetch_yahoo_live(ticker):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode('utf-8'))
        results = data.get("quoteResponse", {}).get("result", [])
        if not results:
            return None
        quote = results[0]
        
        # Return mapped fields
        return {
            "ticker": quote.get("symbol", ticker),
            "companyName": quote.get("longName") or quote.get("shortName") or ticker,
            "currentPrice": quote.get("regularMarketPrice"),
            "open": quote.get("regularMarketOpen"),
            "high": quote.get("regularMarketDayHigh"),
            "low": quote.get("regularMarketDayLow"),
            "previousClose": quote.get("regularMarketPreviousClose"),
            "volume": quote.get("regularMarketVolume", 0),
            "currency": quote.get("currency", "USD"),
            "marketState": quote.get("marketState", "UNKNOWN"),
            "timestamp": quote.get("regularMarketTime", 0)
        }

def fetch_yahoo_history(ticker, dt):
    # Set window to cover the target day
    period1 = int(dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc).timestamp())
    period2 = period1 + 86400
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={period1}&period2={period2}&interval=1d"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode('utf-8'))
        chart = data.get("chart", {})
        if chart.get("error"):
            return None
        result = chart.get("result", [])
        if not result:
            return None
            
        res = result[0]
        timestamps = res.get("timestamp", [])
        if not timestamps:
            return None  # Market closed on this day (weekend / holiday)
            
        indicators = res.get("indicators", {}).get("quote", [{}])[0]
        adjclose = res.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])
        
        open_val = indicators.get("open", [None])[0]
        high_val = indicators.get("high", [None])[0]
        low_val = indicators.get("low", [None])[0]
        close_val = indicators.get("close", [None])[0]
        volume_val = indicators.get("volume", [0])[0]
        adj_close_val = adjclose[0] if len(adjclose) > 0 else close_val
        
        if open_val is None or close_val is None:
            return None
            
        return {
            "ticker": ticker,
            "date": dt.strftime("%Y-%m-%d"),
            "open": round(open_val, 2),
            "high": round(high_val, 2),
            "low": round(low_val, 2),
            "close": round(close_val, 2),
            "adjustedClose": round(adj_close_val, 2),
            "volume": int(volume_val)
        }

class StockRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Override to log cleanly to console
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        # 1. API: Live Quote
        if path.startswith("/api/stocks/live/"):
            ticker = path.replace("/api/stocks/live/", "").strip()
            if not ticker or not TICKER_REGEX.match(ticker):
                self.send_json({"success": False, "message": "Invalid ticker format"}, 400)
                return
                
            ticker = sanitize_ticker(ticker)
            try:
                # Try fetching real data first
                data = fetch_yahoo_live(ticker)
                if not data:
                    # Fallback to mock data if ticker not found in Yahoo
                    data = get_mock_live(ticker)
                self.send_json({"success": True, "data": data, "timestamp": datetime.now().isoformat()})
            except Exception as e:
                # Fallback to mock data on network errors
                sys.stderr.write(f"Yahoo live fetch failed for {ticker}: {e}. Falling back to mock data.\n")
                data = get_mock_live(ticker)
                self.send_json({"success": True, "data": data, "timestamp": datetime.now().isoformat()})
            return
            
        # 2. API: Historical Quote
        elif path == "/api/stocks/history":
            ticker_param = query.get("ticker", [""])[0].strip()
            date_param = query.get("date", [""])[0].strip()
            
            if not ticker_param or not TICKER_REGEX.match(ticker_param):
                self.send_json({"success": False, "message": "Validation failed: Ticker format invalid"}, 400)
                return
            if not date_param:
                self.send_json({"success": False, "message": "Validation failed: Date is required"}, 400)
                return
                
            ticker = sanitize_ticker(ticker_param)
            try:
                dt = validate_date(date_param)
            except ValueError as e:
                self.send_json({"success": False, "message": str(e)}, 400)
                return
                
            try:
                # Try fetching real Yahoo chart data
                data = fetch_yahoo_history(ticker, dt)
                if data is None:
                    # None returned means market closed / weekend
                    self.send_json({"message": "Market Closed"}, 200)
                    return
                self.send_json({"success": True, "data": data, "timestamp": datetime.now().isoformat()})
            except Exception as e:
                sys.stderr.write(f"Yahoo history fetch failed for {ticker}: {e}. Falling back to mock data.\n")
                # Fallback to mock history handler
                data = get_mock_history(ticker, date_param, dt)
                if data is None:
                    self.send_json({"message": "Market Closed"}, 200)
                else:
                    self.send_json({"success": True, "data": data, "timestamp": datetime.now().isoformat()})
            return
            
        # 3. Serve Frontend HTML Dashboard
        elif path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode('utf-8'))
            return
            
        # 4. Not Found
        else:
            self.send_response(404)
            self.end_headers()
            
    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        # Support CORS for local development
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

# Premium Glassmorphic Frontend HTML dashboard
HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethara.ai - Stock Market Dashboard</title>
    <!-- Google Fonts & Tailwind CDN -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;900&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: { sans: ['Outfit', 'sans-serif'] },
                }
            }
        }
    </script>
    <style>
        .glass {
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .light .glass {
            background: rgba(255, 255, 255, 0.65);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(15, 23, 42, 0.08);
        }
        .text-glow {
            text-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
        }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 light:from-slate-50 light:via-indigo-50 light:to-slate-100 min-h-screen text-slate-100 light:text-slate-900 transition-colors duration-300">
    <div class="max-w-7xl mx-auto px-4 py-6">
        
        <!-- Header -->
        <header class="glass rounded-3xl p-6 mb-8 flex justify-between items-center shadow-2xl">
            <div class="flex items-center space-x-3 animate-pulse">
                <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                    <i data-lucide="trending-up" class="text-white w-6 h-6"></i>
                </div>
                <div>
                    <h1 class="text-2xl font-black tracking-tight bg-gradient-to-r from-white to-slate-400 light:from-slate-950 light:to-slate-600 bg-clip-text text-transparent">
                        Ethara<span class="text-emerald-500 font-extrabold">.ai</span>
                    </h1>
                    <p class="text-xs text-slate-400">Stock Market Checker Replica</p>
                </div>
            </div>
            
            <div class="flex items-center space-x-4">
                <div class="hidden md:flex items-center space-x-2 text-xs bg-slate-800/40 light:bg-slate-200/50 px-3 py-1.5 rounded-full border border-slate-700/30">
                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
                    <span class="text-slate-400 font-medium">Backend: Connected</span>
                </div>
                <!-- Theme Toggle -->
                <button id="themeToggle" class="p-3 rounded-2xl bg-slate-800/50 light:bg-slate-200/60 hover:scale-105 active:scale-95 transition-all duration-200 border border-slate-700/30">
                    <i id="themeIcon" data-lucide="sun" class="w-5 h-5 text-amber-400"></i>
                </button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <!-- Left Controls Column (Forms, Watchlist, History) -->
            <div class="lg:col-span-1 space-y-6">
                
                <!-- Navigation Tabs inside Glassmorphism -->
                <div class="glass p-2 rounded-2xl flex space-x-2">
                    <button id="tabLiveBtn" class="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 bg-emerald-500 text-white shadow-md shadow-emerald-500/20">
                        Live Price
                    </button>
                    <button id="tabHistBtn" class="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 text-slate-400 hover:text-slate-200 hover:bg-slate-800/30 light:hover:bg-slate-100">
                        Historical Data
                    </button>
                </div>

                <!-- Forms Card -->
                <div class="glass p-6 rounded-3xl shadow-xl space-y-6">
                    <!-- Live Search Form -->
                    <form id="liveForm" class="space-y-4">
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-slate-400">Live Quote Ticker</label>
                            <div class="relative">
                                <i data-lucide="search" class="absolute left-3.5 top-3.5 w-5 h-5 text-slate-400"></i>
                                <input type="text" id="liveTickerInput" placeholder="e.g. AAPL, TSLA, NVDA, GC=F" required
                                    class="w-full pl-11 pr-4 py-3 bg-slate-900/50 light:bg-white border border-slate-700/40 light:border-slate-300 rounded-2xl outline-none focus:ring-2 focus:ring-emerald-500/50 text-slate-100 light:text-slate-900 font-semibold transition">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-500/10 transition duration-300 active:scale-[0.98]">
                            Get Live Price
                        </button>
                    </form>

                    <!-- Historical Search Form -->
                    <form id="histForm" class="space-y-4 hidden">
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-slate-400">Historical Ticker</label>
                            <div class="relative">
                                <i data-lucide="search" class="absolute left-3.5 top-3.5 w-5 h-5 text-slate-400"></i>
                                <input type="text" id="histTickerInput" placeholder="e.g. AAPL, GOOGL" required
                                    class="w-full pl-11 pr-4 py-3 bg-slate-900/50 light:bg-white border border-slate-700/40 light:border-slate-300 rounded-2xl outline-none focus:ring-2 focus:ring-emerald-500/50 text-slate-100 light:text-slate-900 font-semibold transition">
                            </div>
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-slate-400">Select Date</label>
                            <div class="relative">
                                <i data-lucide="calendar" class="absolute left-3.5 top-3.5 w-5 h-5 text-slate-400"></i>
                                <input type="date" id="histDateInput" required
                                    class="w-full pl-11 pr-4 py-3 bg-slate-900/50 light:bg-white border border-slate-700/40 light:border-slate-300 rounded-2xl outline-none focus:ring-2 focus:ring-emerald-500/50 text-slate-100 light:text-slate-900 font-semibold transition">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-500/10 transition duration-300 active:scale-[0.98]">
                            Get Historical Data
                        </button>
                    </form>
                    
                    <div id="validationError" class="text-rose-500 text-xs font-semibold hidden flex items-center space-x-1.5">
                        <i data-lucide="alert-circle" class="w-4 h-4 shrink-0"></i>
                        <span id="validationErrorMsg"></span>
                    </div>
                </div>

                <!-- Watchlist Card -->
                <div class="glass p-6 rounded-3xl shadow-xl">
                    <h3 class="text-sm font-semibold text-slate-400 mb-4 flex items-center justify-between">
                        <span>Watchlist</span>
                        <i data-lucide="bookmark" class="w-4 h-4 text-emerald-500"></i>
                    </h3>
                    <div id="watchlistContainer" class="flex flex-wrap gap-2">
                        <!-- Filled dynamically -->
                    </div>
                </div>

                <!-- Search History Card -->
                <div class="glass p-6 rounded-3xl shadow-xl">
                    <h3 class="text-sm font-semibold text-slate-400 mb-4 flex items-center justify-between">
                        <span>Recent Searches</span>
                        <i data-lucide="history" class="w-4 h-4 text-slate-400"></i>
                    </h3>
                    <ul id="historyContainer" class="space-y-2 text-sm max-h-40 overflow-y-auto">
                        <!-- Filled dynamically -->
                    </ul>
                </div>
            </div>

            <!-- Right Content Output Column -->
            <div class="lg:col-span-2 space-y-6">
                
                <!-- Loading Spinner -->
                <div id="loader" class="hidden glass p-12 rounded-3xl flex flex-col items-center justify-center space-y-4">
                    <div class="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin"></div>
                    <p class="text-slate-400 text-sm font-medium">Fetching secure market data...</p>
                </div>

                <!-- Placeholder Screen -->
                <div id="placeholderScreen" class="glass p-16 rounded-3xl flex flex-col items-center justify-center text-center space-y-4">
                    <div class="w-20 h-20 bg-slate-800/40 light:bg-slate-200/50 rounded-full flex items-center justify-center border border-slate-700/20 shadow-inner">
                        <i data-lucide="bar-chart-2" class="w-10 h-10 text-slate-400"></i>
                    </div>
                    <div>
                        <h4 class="text-lg font-bold">No Ticker Queried</h4>
                        <p class="text-slate-400 text-sm max-w-sm mt-1">Enter a ticker symbol on the left and fetch its live price or historical trading record.</p>
                    </div>
                </div>

                <!-- Live Response Card -->
                <div id="liveResultCard" class="hidden glass p-8 rounded-3xl space-y-6 relative overflow-hidden">
                    <div class="absolute -right-16 -top-16 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl"></div>
                    
                    <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800/30 pb-6 gap-4">
                        <div>
                            <div class="flex items-center space-x-3">
                                <h2 id="liveSymbol" class="text-3xl font-black tracking-tight text-white light:text-slate-950">AAPL</h2>
                                <button id="addWatchlistBtn" class="p-2 rounded-xl bg-slate-850 hover:bg-slate-800 hover:scale-105 active:scale-95 transition border border-slate-700/30">
                                    <i data-lucide="plus" class="w-4 h-4 text-emerald-500"></i>
                                </button>
                            </div>
                            <p id="liveCompanyName" class="text-slate-400 text-sm mt-1">Apple Inc.</p>
                        </div>
                        <div class="text-left md:text-right">
                            <div class="text-4xl font-black text-glow" id="livePrice">$175.50</div>
                            <div class="text-sm font-semibold flex items-center space-x-1.5 mt-1" id="liveChangeBadge">
                                <span id="liveChangeText">+1.25 (+0.72%)</span>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-6">
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl border border-slate-750/30">
                            <span class="text-xs text-slate-400 block mb-1">Open Price</span>
                            <span class="text-base font-bold" id="liveOpen">$174.50</span>
                        </div>
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl border border-slate-750/30">
                            <span class="text-xs text-slate-400 block mb-1">Day High</span>
                            <span class="text-base font-bold text-emerald-500" id="liveHigh">$176.20</span>
                        </div>
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl border border-slate-750/30">
                            <span class="text-xs text-slate-400 block mb-1">Day Low</span>
                            <span class="text-base font-bold text-rose-500" id="liveLow">$173.80</span>
                        </div>
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl border border-slate-750/30">
                            <span class="text-xs text-slate-400 block mb-1">Previous Close</span>
                            <span class="text-base font-bold" id="livePrevClose">$174.25</span>
                        </div>
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl border border-slate-750/30">
                            <span class="text-xs text-slate-400 block mb-1">Trading Volume</span>
                            <span class="text-base font-bold" id="liveVolume">1.2M</span>
                        </div>
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl border border-slate-750/30">
                            <span class="text-xs text-slate-400 block mb-1">Market State</span>
                            <span class="text-base font-bold uppercase tracking-wider text-emerald-500 text-xs mt-1" id="liveState">REGULAR</span>
                        </div>
                    </div>
                </div>

                <!-- Historical Response Card -->
                <div id="histResultCard" class="hidden glass p-8 rounded-3xl space-y-6">
                    <div class="flex justify-between items-center border-b border-slate-800/30 pb-6">
                        <div>
                            <h2 class="text-2xl font-black text-white light:text-slate-950">
                                <span id="histSymbol">AAPL</span> Historical Data
                            </h2>
                            <p id="histDateTitle" class="text-slate-400 text-sm mt-1">Trading Date: 2024-05-10</p>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl">
                            <span class="text-xs text-slate-400 block mb-1">Open</span>
                            <span class="text-base font-bold" id="histOpen">$100.00</span>
                        </div>
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl">
                            <span class="text-xs text-slate-400 block mb-1">High</span>
                            <span class="text-base font-bold text-emerald-500" id="histHigh">$110.00</span>
                        </div>
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl">
                            <span class="text-xs text-slate-400 block mb-1">Low</span>
                            <span class="text-base font-bold text-rose-500" id="histLow">$90.00</span>
                        </div>
                        <div class="bg-slate-800/20 light:bg-slate-200/20 p-4 rounded-2xl">
                            <span class="text-xs text-slate-400 block mb-1">Close (Adj)</span>
                            <span class="text-base font-bold" id="histClose">$105.00</span>
                        </div>
                    </div>

                    <!-- Chart Section -->
                    <div class="bg-slate-900/60 light:bg-slate-200/30 p-6 rounded-2xl border border-slate-800/30">
                        <h4 class="text-sm font-semibold text-slate-400 mb-4">OHLC Comparison</h4>
                        <div class="h-64">
                            <canvas id="ohlcChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Market Closed Alert -->
                <div id="marketClosedCard" class="hidden flex items-center p-6 rounded-3xl bg-amber-500/10 border border-amber-500/25 text-amber-500 font-semibold animate-fade-in space-x-4">
                    <i data-lucide="info" class="w-8 h-8 shrink-0"></i>
                    <div>
                        <h5 class="text-base font-bold">Market Closed</h5>
                        <p class="text-xs font-normal text-slate-400 mt-1">No transaction history exists for this date. Tickers are not traded during weekends, public holidays, or non-trading sessions.</p>
                    </div>
                </div>

                <!-- General Error Card -->
                <div id="errorCard" class="hidden flex items-center p-6 rounded-3xl bg-rose-500/10 border border-rose-500/25 text-rose-500 font-semibold animate-fade-in space-x-4">
                    <i data-lucide="alert-triangle" class="w-8 h-8 shrink-0"></i>
                    <div>
                        <h5 class="text-base font-bold">Request Failed</h5>
                        <p class="text-xs font-normal text-slate-400 mt-1" id="errorCardMsg">No data returned by server.</p>
                    </div>
                </div>

            </div>
        </main>
    </div>

    <!-- Scripting for Client UI & APIs -->
    <script>
        // Init LocalStorage structures
        let watchlist = JSON.parse(localStorage.getItem('ethara_watchlist') || '[]');
        let searchHistory = JSON.parse(localStorage.getItem('ethara_history') || '[]');
        let chartInstance = null;

        // Set max attribute on date picker to today (UTC)
        document.getElementById('histDateInput').max = new Date().toISOString().split('T')[0];

        // Theme management
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        
        // Load default theme
        if (localStorage.getItem('theme') === 'light') {
            document.documentElement.classList.remove('dark');
            document.documentElement.classList.add('light');
            themeIcon.setAttribute('data-lucide', 'moon');
        }

        themeToggle.addEventListener('click', () => {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                document.documentElement.classList.add('light');
                localStorage.setItem('theme', 'light');
                themeIcon.setAttribute('data-lucide', 'moon');
            } else {
                document.documentElement.classList.remove('light');
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
                themeIcon.setAttribute('data-lucide', 'sun');
            }
            lucide.createIcons();
        });

        // Tab selection logic
        const tabLiveBtn = document.getElementById('tabLiveBtn');
        const tabHistBtn = document.getElementById('tabHistBtn');
        const liveForm = document.getElementById('liveForm');
        const histForm = document.getElementById('histForm');

        tabLiveBtn.addEventListener('click', () => {
            tabLiveBtn.className = "flex-1 py-2.5 rounded-xl text-sm font-semibold bg-emerald-500 text-white shadow-md shadow-emerald-500/20";
            tabHistBtn.className = "flex-1 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/30 light:hover:bg-slate-100";
            liveForm.classList.remove('hidden');
            histForm.classList.add('hidden');
        });

        tabHistBtn.addEventListener('click', () => {
            tabHistBtn.className = "flex-1 py-2.5 rounded-xl text-sm font-semibold bg-emerald-500 text-white shadow-md shadow-emerald-500/20";
            tabLiveBtn.className = "flex-1 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/30 light:hover:bg-slate-100";
            histForm.classList.remove('hidden');
            liveForm.classList.add('hidden');
        });

        // Render functions
        function renderWatchlist() {
            const container = document.getElementById('watchlistContainer');
            if (watchlist.length === 0) {
                container.innerHTML = `<span class="text-xs text-slate-500 italic py-2">No bookmarks saved</span>`;
                return;
            }
            container.innerHTML = watchlist.map(ticker => `
                <div class="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-slate-800/40 light:bg-slate-200/50 text-xs border border-slate-700/20">
                    <button class="font-bold hover:text-emerald-400" onclick="searchLiveDirect('${ticker}')">${ticker}</button>
                    <button onclick="removeFromWatchlist('${ticker}')" class="text-slate-500 hover:text-rose-500 font-bold ml-1">×</button>
                </div>
            `).join('');
        }

        function renderHistory() {
            const container = document.getElementById('historyContainer');
            if (searchHistory.length === 0) {
                container.innerHTML = `<li class="text-xs text-slate-500 italic">No search history</li>`;
                return;
            }
            container.innerHTML = searchHistory.map(item => `
                <li class="flex items-center justify-between group py-1.5 border-b border-slate-800/20 last:border-0">
                    <span class="cursor-pointer hover:text-emerald-400 font-semibold" onclick="searchLiveDirect('${item}')">${item}</span>
                    <i data-lucide="arrow-right-circle" class="w-4 h-4 text-slate-500 group-hover:text-emerald-500 transition opacity-0 group-hover:opacity-100 cursor-pointer" onclick="searchLiveDirect('${item}')"></i>
                </li>
            `).join('');
            lucide.createIcons();
        }

        // Global functions
        window.searchLiveDirect = function(ticker) {
            document.getElementById('liveTickerInput').value = ticker;
            tabLiveBtn.click();
            document.getElementById('liveForm').dispatchEvent(new Event('submit'));
        }

        window.removeFromWatchlist = function(ticker) {
            watchlist = watchlist.filter(t => t !== ticker);
            localStorage.setItem('ethara_watchlist', JSON.stringify(watchlist));
            renderWatchlist();
        }

        // DOM Elements
        const loader = document.getElementById('loader');
        const placeholderScreen = document.getElementById('placeholderScreen');
        const liveResultCard = document.getElementById('liveResultCard');
        const histResultCard = document.getElementById('histResultCard');
        const marketClosedCard = document.getElementById('marketClosedCard');
        const errorCard = document.getElementById('errorCard');
        const valError = document.getElementById('validationError');
        const valErrorMsg = document.getElementById('validationErrorMsg');

        function hideAllOutputs() {
            placeholderScreen.classList.add('hidden');
            liveResultCard.classList.add('hidden');
            histResultCard.classList.add('hidden');
            marketClosedCard.classList.add('hidden');
            errorCard.classList.add('hidden');
            valError.classList.add('hidden');
        }

        function showValError(msg) {
            valErrorMsg.innerText = msg;
            valError.classList.remove('hidden');
        }

        function addHistory(ticker) {
            if (!searchHistory.includes(ticker)) {
                searchHistory.unshift(ticker);
                searchHistory = searchHistory.slice(0, 10);
                localStorage.setItem('ethara_history', JSON.stringify(searchHistory));
                renderHistory();
            }
        }

        // API Fetchers
        // 1. Live Form Submit
        document.getElementById('liveForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const ticker = document.getElementById('liveTickerInput').value.trim().toUpperCase();
            hideAllOutputs();

            if (!ticker) {
                showValError("Ticker is required.");
                return;
            }
            if (!/^[A-Za-z0-9=.-]{1,12}$/.test(ticker)) {
                showValError("Invalid ticker symbol format.");
                return;
            }

            loader.classList.remove('hidden');

            try {
                const res = await fetch(`/api/stocks/live/${ticker}`);
                const resData = await res.json();
                loader.classList.add('hidden');

                if (resData.success) {
                    const data = resData.data;
                    document.getElementById('liveSymbol').innerText = data.ticker;
                    document.getElementById('liveCompanyName').innerText = data.companyName;
                    
                    const sign = data.currentPrice >= data.previousClose ? '+' : '';
                    const diff = data.currentPrice - data.previousClose;
                    const diffPct = data.previousClose !== 0 ? (diff / data.previousClose) * 100 : 0;
                    
                    document.getElementById('livePrice').innerText = `${data.currency === 'INR' ? '₹' : '$'}${data.currentPrice.toFixed(2)}`;
                    
                    const badge = document.getElementById('liveChangeBadge');
                    const text = document.getElementById('liveChangeText');
                    
                    text.innerText = `${sign}${diff.toFixed(2)} (${sign}${diffPct.toFixed(2)}%)`;
                    if (diff >= 0) {
                        badge.className = "text-sm font-semibold flex items-center space-x-1.5 mt-1 text-emerald-500 bg-emerald-500/10 px-2.5 py-1 rounded-lg w-max";
                    } else {
                        badge.className = "text-sm font-semibold flex items-center space-x-1.5 mt-1 text-rose-500 bg-rose-500/10 px-2.5 py-1 rounded-lg w-max";
                    }
                    
                    document.getElementById('liveOpen').innerText = `${data.currency === 'INR' ? '₹' : '$'}${data.open.toFixed(2)}`;
                    document.getElementById('liveHigh').innerText = `${data.currency === 'INR' ? '₹' : '$'}${data.high.toFixed(2)}`;
                    document.getElementById('liveLow').innerText = `${data.currency === 'INR' ? '₹' : '$'}${data.low.toFixed(2)}`;
                    document.getElementById('livePrevClose').innerText = `${data.currency === 'INR' ? '₹' : '$'}${data.previousClose.toFixed(2)}`;
                    document.getElementById('liveVolume').innerText = data.volume.toLocaleString();
                    document.getElementById('liveState').innerText = data.marketState;
                    
                    // Add Watchlist Action Setup
                    const addBtn = document.getElementById('addWatchlistBtn');
                    if (watchlist.includes(data.ticker)) {
                        addBtn.innerHTML = `<i data-lucide="check" class="w-4 h-4 text-emerald-400"></i>`;
                    } else {
                        addBtn.innerHTML = `<i data-lucide="plus" class="w-4 h-4 text-slate-400"></i>`;
                    }
                    addBtn.onclick = () => {
                        if (!watchlist.includes(data.ticker)) {
                            watchlist.push(data.ticker);
                            localStorage.setItem('ethara_watchlist', JSON.stringify(watchlist));
                            addBtn.innerHTML = `<i data-lucide="check" class="w-4 h-4 text-emerald-400"></i>`;
                            renderWatchlist();
                        }
                    };
                    
                    liveResultCard.classList.remove('hidden');
                    addHistory(data.ticker);
                    lucide.createIcons();
                } else {
                    document.getElementById('errorCardMsg').innerText = resData.message || "Failed to fetch live quotes.";
                    errorCard.classList.remove('hidden');
                }
            } catch (err) {
                loader.classList.add('hidden');
                document.getElementById('errorCardMsg').innerText = "Unable to connect to the backend server.";
                errorCard.classList.remove('hidden');
            }
        });

        // 2. Historical Form Submit
        document.getElementById('histForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const ticker = document.getElementById('histTickerInput').value.trim().toUpperCase();
            const date = document.getElementById('histDateInput').value;
            hideAllOutputs();

            if (!ticker) {
                showValError("Ticker is required.");
                return;
            }
            if (!/^[A-Za-z0-9=.-]{1,12}$/.test(ticker)) {
                showValError("Invalid ticker symbol format.");
                return;
            }
            if (!date) {
                showValError("Date is required.");
                return;
            }
            if (new Date(date) > new Date()) {
                showValError("Future dates are not allowed.");
                return;
            }

            loader.classList.remove('hidden');

            try {
                const res = await fetch(`/api/stocks/history?ticker=${ticker}&date=${date}`);
                const resData = await res.json();
                loader.classList.add('hidden');

                if (resData.message === "Market Closed") {
                    marketClosedCard.classList.remove('hidden');
                    return;
                }

                if (resData.success) {
                    const data = resData.data;
                    document.getElementById('histSymbol').innerText = data.ticker;
                    document.getElementById('histDateTitle').innerText = `Trading Date: ${data.date}`;
                    
                    document.getElementById('histOpen').innerText = `$${data.open.toFixed(2)}`;
                    document.getElementById('histHigh').innerText = `$${data.high.toFixed(2)}`;
                    document.getElementById('histLow').innerText = `$${data.low.toFixed(2)}`;
                    document.getElementById('histClose').innerText = `$${data.close.toFixed(2)}`;
                    
                    histResultCard.classList.remove('hidden');
                    
                    // Render comparison Chart.js
                    if (chartInstance) {
                        chartInstance.destroy();
                    }
                    
                    const isDark = document.documentElement.classList.contains('dark');
                    const textCol = isDark ? '#94a3b8' : '#475569';
                    const gridCol = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(15,23,42,0.06)';
                    
                    const ctx = document.getElementById('ohlcChart').getContext('2d');
                    chartInstance = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: ['Open', 'High', 'Low', 'Close'],
                            datasets: [{
                                label: 'Price ($)',
                                data: [data.open, data.high, data.low, data.close],
                                backgroundColor: [
                                    'rgba(16, 185, 129, 0.45)', // open
                                    'rgba(16, 185, 129, 0.75)', // high
                                    'rgba(244, 63, 94, 0.65)',  // low
                                    'rgba(59, 130, 246, 0.65)'  // close
                                ],
                                borderColor: [
                                    '#10b981', '#10b981', '#f43f5e', '#3b82f6'
                                ],
                                borderWidth: 2,
                                borderRadius: 8
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                x: {
                                    grid: { color: gridCol },
                                    ticks: { color: textCol }
                                },
                                y: {
                                    grid: { color: gridCol },
                                    ticks: { color: textCol }
                                }
                            }
                        }
                    });
                } else {
                    document.getElementById('errorCardMsg').innerText = resData.message || "Failed to fetch historical data.";
                    errorCard.classList.remove('hidden');
                }
            } catch (err) {
                loader.classList.add('hidden');
                document.getElementById('errorCardMsg').innerText = "Unable to connect to the backend server.";
                errorCard.classList.remove('hidden');
            }
        });

        // Initial renders
        renderWatchlist();
        renderHistory();
        lucide.createIcons();
    </script>
</body>
</html>
"""

def main():
    port = DEFAULT_PORT
    server = None
    
    # Simple automatic port selection in case 8080 is busy
    while port < DEFAULT_PORT + 20:
        try:
            # Re-usable port
            socketserver.TCPServer.allow_reuse_address = True
            server = socketserver.TCPServer(("", port), StockRequestHandler)
            break
        except OSError:
            print(f"Port {port} is currently in use, trying next port...")
            port += 1
            
    if not server:
        print("Error: Could not bind server to any port in range 8080-8100.")
        sys.exit(1)
        
    print(f"\n========================================================")
    print(f" Ethara.ai Stock Tracker - Single File Python Replica")
    print(f"========================================================")
    print(f"-> Local dashboard: http://localhost:{port}/")
    print(f"-> API Endpoints:")
    print(f"   - Live quote:   http://localhost:{port}/api/stocks/live/AAPL")
    print(f"   - History:      http://localhost:{port}/api/stocks/history?ticker=AAPL&date=2024-05-10")
    print(f"--------------------------------------------------------")
    print(f"Press Ctrl+C to terminate the server.")
    print(f"========================================================\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()
        print("Server stopped.")

if __name__ == "__main__":
    main()
